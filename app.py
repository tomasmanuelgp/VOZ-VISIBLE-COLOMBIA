#!/usr/bin/env python3
"""
VOZ VISIBLE - Aplicación Web Flask
Sistema de Reconocimiento de Lenguaje de Señas Colombiano en Tiempo Real
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import sys
import json
import base64
import cv2
import numpy as np
from PIL import Image
import io
import time
import threading
from pathlib import Path

# Configurar paths de manera robusta
def setup_import_paths():
    """
    Configurar paths para imports
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(current_dir, 'src')
    
    # Agregar paths
    paths_to_add = [src_path, current_dir]
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return src_path, current_dir

# Configurar paths
src_path, project_root = setup_import_paths()

# Importar predictor con múltiples intentos
SignLanguagePredictor = None
import_error = None

# Intentar importar desde diferentes ubicaciones
import_attempts = [
    'inference.sign_language_predictor',
    'src.inference.sign_language_predictor',
    'inference.sign_language_predictor',
]

for import_path in import_attempts:
    try:
        if import_path.startswith('src.'):
            # Importar desde src
            module = __import__(import_path, fromlist=['SignLanguagePredictor'])
            SignLanguagePredictor = module.SignLanguagePredictor
            print(f"✅ SignLanguagePredictor importado desde: {import_path}")
            break
        else:
            # Importar directamente
            from inference.sign_language_predictor import SignLanguagePredictor
            print(f"✅ SignLanguagePredictor importado desde: {import_path}")
            break
    except ImportError as e:
        import_error = str(e)
        print(f"❌ Error importando desde {import_path}: {e}")
        continue

if SignLanguagePredictor is None:
    print(f"❌ No se pudo importar SignLanguagePredictor")
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"📁 Archivo app.py: {__file__}")
    print(f"📁 src_path: {src_path}")
    
    # Verificar estructura de archivos
    if os.path.exists(src_path):
        print(f" Contenido de src/:")
        for item in os.listdir(src_path):
            item_path = os.path.join(src_path, item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
                if item == 'inference':
                    for subitem in os.listdir(item_path):
                        print(f"    {subitem}")
            else:
                print(f"  📄 {item}")
    else:
        print(f"❌ Directorio src/ no existe")
    
    sys.exit(1)

# Configuración de la aplicación
app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.config['SECRET_KEY'] = 'voz-visible-secret-key-2024'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Variables globales
predictor = None
system_status = "initializing"
current_prediction = {"word": "Iniciando...", "confidence": 0.0}

# Configuración de rutas
UPLOAD_FOLDER = 'web/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def initialize_predictor():
    """
    Inicializar el predictor de lenguaje de señas colombiano
    """
    global predictor, system_status
    
    try:
        print("🤖 Inicializando sistema de predicción...")
        
        # Definir rutas de archivos
        model_path = "models/Dense_Simple_patient.h5"
        scaler_path = "data/processed/scaler_optimized.pkl"
        label_encoder_path = "data/processed/label_encoder.pkl"
        feature_info_path = "data/processed/feature_info.json"
        
        # Verificar archivos
        required_files = [model_path, scaler_path, label_encoder_path, feature_info_path]
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            print(f"❌ Archivos faltantes: {missing_files}")
            system_status = "missing_files"
            return False
        
        # Inicializar predictor
        predictor = SignLanguagePredictor(
            model_path=model_path,
            scaler_path=scaler_path,
            label_encoder_path=label_encoder_path,
            feature_info_path=feature_info_path
        )
        
        system_status = "ready"
        print("✅ Sistema de predicción inicializado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando predictor: {str(e)}")
        system_status = "error"
        return False

# Rutas principales
@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/camera')
def camera():
    """Página de cámara en tiempo real"""
    return render_template('camera.html')

# API Endpoints
@app.route('/api/status')
def api_status():
    """
    Obtener estado del sistema
    """
    model_info = {}
    if predictor:
        model_info = predictor.get_model_info()
    
    return jsonify({
        'status': system_status,
        'message': get_status_message(system_status),
        'model_info': model_info,
        'timestamp': time.time()
    })

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    Realizar predicción de lenguaje de señas colombiano
    """
    global current_prediction
    
    if system_status != "ready" or not predictor:
        return jsonify({
            'status': 'error',
            'message': 'Sistema no disponible',
            'error': get_status_message(system_status)
        })
    
    try:
        data = request.get_json()
        
        # Predicción desde imagen
        if 'image' in data:
            image_data = data['image']
            
            # Procesar imagen base64
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decodificar imagen
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convertir a formato OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Realizar predicción
            prediction, confidence, success = predictor.predict_realtime(cv_image)
            
            if success:
                current_prediction = {"word": prediction, "confidence": confidence}
                return jsonify({
                    'status': 'success',
                    'word': prediction,
                    'confidence': float(confidence),
                    'timestamp': time.time()
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error en la predicción',
                    'error': 'No se pudieron extraer características'
                })
        
        else:
            return jsonify({
                'status': 'error',
                'message': 'Datos inválidos',
                'error': 'Se requiere imagen'
            })
            
    except Exception as e:
        print(f"❌ Error en predicción: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor',
            'error': str(e)
        })

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """
    Subir y analizar imagen
    """
    if system_status != "ready" or not predictor:
        return jsonify({
            'status': 'error',
            'message': 'Sistema no disponible'
        })
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No se envió archivo'
            })
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No se seleccionó archivo'
            })
        
        # Guardar archivo temporalmente
        filename = f"temp_{int(time.time())}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Cargar y procesar imagen
        image = cv2.imread(filepath)
        if image is None:
            return jsonify({
                'status': 'error',
                'message': 'Imagen inválida'
            })
        
        # Realizar predicción
        prediction, confidence, success = predictor.predict_realtime(image)
        
        # Limpiar archivo temporal
        os.remove(filepath)
        
        if success:
            return jsonify({
                'status': 'success',
                'word': prediction,
                'confidence': float(confidence),
                'timestamp': time.time()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No se pudieron extraer características de la imagen'
            })
            
    except Exception as e:
        print(f"❌ Error en upload: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error procesando imagen',
            'error': str(e)
        })

@app.route('/api/model-info')
def api_model_info():
    """
    Obtener información del modelo
    """
    if predictor:
        return jsonify(predictor.get_model_info())
    else:
        return jsonify({
            'status': 'error',
            'message': 'Predictor no inicializado'
        })

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    print(f"🔌 Cliente conectado: {request.sid}")
    emit('status', {
        'status': system_status,
        'message': get_status_message(system_status),
        'current_prediction': current_prediction
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    print(f" Cliente desconectado: {request.sid}")

@socketio.on('start_camera')
def handle_start_camera():
    """Iniciar cámara en tiempo real"""
    if system_status == "ready" and predictor:
        emit('camera_status', {'status': 'started', 'message': 'Cámara iniciada'})
    else:
        emit('camera_status', {'status': 'error', 'message': 'Sistema no disponible'})

@socketio.on('stop_camera')
def handle_stop_camera():
    """Detener cámara"""
    emit('camera_status', {'status': 'stopped', 'message': 'Cámara detenida'})

@socketio.on('process_frame')
def handle_process_frame(data):
    """Procesar frame de cámara"""
    if system_status != "ready" or not predictor:
        emit('prediction', {
            'status': 'error',
            'message': 'Sistema no disponible'
        })
        return
    
    try:
        # Procesar frame (data contiene imagen en base64)
        image_data = data['frame']
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Decodificar y procesar
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Realizar predicción
        prediction, confidence, success = predictor.predict_realtime(cv_image)
        
        if success:
            emit('prediction', {
                'status': 'success',
                'word': prediction,
                'confidence': float(confidence),
                'timestamp': time.time()
            })
        else:
            emit('prediction', {
                'status': 'error',
                'message': 'No se pudieron extraer características'
            })
            
    except Exception as e:
        print(f"❌ Error procesando frame: {str(e)}")
        emit('prediction', {
            'status': 'error',
            'message': 'Error procesando frame',
            'error': str(e)
        })

# Funciones auxiliares
def get_status_message(status):
    """Obtener mensaje de estado"""
    messages = {
        'initializing': 'Inicializando sistema...',
        'ready': 'Sistema listo',
        'error': 'Error en el sistema',
        'missing_files': 'Archivos del modelo no encontrados'
    }
    return messages.get(status, 'Estado desconocido')

if __name__ == '__main__':
    print(" VOZ VISIBLE - Aplicación Web")
    print("=" * 50)
    print("🌐 Iniciando servidor web...")
    print("📡 URL: http://localhost:5000")
    print("=" * 50)
    
    # Inicializar sistema
    initialize_predictor()
    
    # Ejecutar aplicación
    socketio.run(app, 
                debug=True, 
                host='0.0.0.0', 
                port=5000,
                allow_unsafe_werkzeug=True)
