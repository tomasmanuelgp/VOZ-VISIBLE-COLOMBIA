#!/usr/bin/env python3
"""
VOZ VISIBLE - Aplicación Web Flask
Sistema de Reconocimiento de Lenguaje de Señas Colombiano en Tiempo Real
"""

from flask import Flask, render_template, request, jsonify, Response, current_app
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import sys
import base64
import cv2
import numpy as np
from PIL import Image
import io
import time
import logging

# Configurar paths de manera robusta ANTES de los imports
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

# Configurar paths PRIMERO
src_path, project_root = setup_import_paths()

# Ahora importar los módulos (después de configurar paths)
from config.settings import AppSettings
from repositories.sign_language_repository import SignLanguageRepository
from services.prediction_service import PredictionService
from services.tts_service import TTSService

# Importar validadores
try:
    from utils.validators import (
        validate_base64_image,
        validate_text_for_tts,
        validate_session_id
    )
    VALIDATORS_AVAILABLE = True
except ImportError:
    VALIDATORS_AVAILABLE = False
    logging.warning("Validadores no disponibles")

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

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

# Configuración de la aplicación
app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar servicios
settings = AppSettings()
app.config['SECRET_KEY'] = settings.secret_key
settings.upload_folder.mkdir(parents=True, exist_ok=True)
repository = SignLanguageRepository(settings)
tts_service = TTSService(settings)
prediction_service = PredictionService(settings, repository, tts_service)
app.config['PREDICTION_SERVICE'] = prediction_service
app.config['SETTINGS'] = settings

def get_prediction_service() -> PredictionService:
    return current_app.config['PREDICTION_SERVICE']


def get_tts_service() -> TTSService:
    return current_app.config['PREDICTION_SERVICE'].tts_service


def initialize_predictor():
    """
    Inicializar el predictor de lenguaje de señas colombiano y TTS
    """
    return prediction_service.initialize()

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
    service = get_prediction_service()
    return jsonify(service.get_status_payload())

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    Realizar predicción de lenguaje de señas colombiano
    
    Body JSON:
    {
        "image": "data:image/jpeg;base64,...",
        "include_landmarks": true/false (opcional, default: false)
    }
    """
    service = get_prediction_service()
    
    if not service.is_ready():
        return jsonify({
            'status': 'error',
            'message': 'Sistema no disponible',
            'error': 'Inicializa el predictor antes de realizar predicciones'
        }), 503
    
    try:
        data = request.get_json() or {}
        
        if 'image' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Datos inválidos',
                'error': 'Se requiere imagen'
            }), 400
        
        # Validar imagen
        if VALIDATORS_AVAILABLE:
            is_valid, error_msg = validate_base64_image(data['image'])
            if not is_valid:
                return jsonify({
                    'status': 'error',
                    'message': 'Imagen inválida',
                    'error': error_msg
                }), 400
        
        include_landmarks = data.get('include_landmarks', False)
        session_id = data.get('session_id') or request.remote_addr
        
        # Validar session_id
        if VALIDATORS_AVAILABLE and session_id:
            is_valid, error_msg = validate_session_id(session_id)
            if not is_valid:
                session_id = request.remote_addr  # Usar IP como fallback
        
        response_data = service.predict_from_base64(data['image'], include_landmarks=include_landmarks, session_id=session_id)
        if response_data:
            return jsonify(response_data)
        return jsonify({
            'status': 'error',
            'message': 'No se pudieron extraer características'
        }), 422
            
    except Exception as e:
        logging.exception("❌ Error en predicción")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """
    Subir y analizar imagen
    """
    service = get_prediction_service()
    if not service.is_ready():
        return jsonify({
            'status': 'error',
            'message': 'Sistema no disponible'
        }), 503
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No se envió archivo'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No se seleccionó archivo'
            }), 400
        
        filename = f"temp_{int(time.time())}.jpg"
        upload_folder = current_app.config['SETTINGS'].upload_folder
        filepath = upload_folder / filename
        file.save(filepath)
        
        image = cv2.imread(str(filepath))
        filepath.unlink(missing_ok=True)
        if image is None:
            return jsonify({
                'status': 'error',
                'message': 'Imagen inválida'
            }), 400
        
        response_data = service.predict_from_frame(image)
        if response_data:
            return jsonify(response_data)
        return jsonify({
            'status': 'error',
            'message': 'No se pudieron extraer características de la imagen'
        }), 422
            
    except Exception as e:
        logging.exception("❌ Error en upload")
        return jsonify({
            'status': 'error',
            'message': 'Error procesando imagen',
            'error': str(e)
        }), 500

@app.route('/api/model-info')
def api_model_info():
    """
    Obtener información del modelo
    """
    service = get_prediction_service()
    if service.predictor:
        return jsonify(service.predictor.get_model_info())
    return jsonify({
        'status': 'error',
        'message': 'Predictor no inicializado'
    }), 503

@app.route('/api/tts', methods=['POST'])
def api_tts():
    """
    Generar audio de texto a voz (TTS)
    
    Body JSON:
    {
        "text": "Texto a convertir a voz",
        "format": "base64" | "url" (opcional, default: "base64")
    }
    """
    tts_service = get_tts_service()
    if not tts_service.is_available():
        return jsonify({
            'status': 'error',
            'message': 'Sistema TTS no disponible'
        }), 503
    
    try:
        data = request.get_json() or {}
        
        if 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Se requiere el campo "text"'
            }), 400
        
        text = data['text'].strip()
        
        # Validar texto
        if VALIDATORS_AVAILABLE:
            is_valid, error_msg = validate_text_for_tts(text)
            if not is_valid:
                return jsonify({
                    'status': 'error',
                    'message': 'Texto inválido',
                    'error': error_msg
                }), 400
        elif not text:
            return jsonify({
                'status': 'error',
                'message': 'El texto no puede estar vacío'
            }), 400
        
        format_type = data.get('format', 'base64')
        if format_type == 'base64':
            audio_data = tts_service.generate_audio_base64(text)
            if not audio_data:
                return jsonify({
                    'status': 'error',
                    'message': 'No se pudo generar audio'
                }), 500
            return jsonify({
                'status': 'success',
                'audio': audio_data,
                'text': text,
                'timestamp': time.time()
            })
        
        file_path = tts_service.save_audio_file(text)
        if not file_path:
            return jsonify({
                'status': 'error',
                'message': 'No se pudo generar archivo de audio'
            }), 500
        audio_url = f'/api/tts/file/{os.path.basename(file_path)}'
        return jsonify({
            'status': 'success',
            'audio_url': audio_url,
            'text': text,
            'timestamp': time.time()
        })
            
    except Exception as e:
        logging.exception("❌ Error en TTS")
        return jsonify({
            'status': 'error',
            'message': 'Error generando audio',
            'error': str(e)
        }), 500

@app.route('/api/tts/file/<filename>')
def api_tts_file(filename):
    """
    Servir archivo de audio desde cache
    """
    tts_service = get_tts_service()
    if not tts_service.is_available():
        return jsonify({
            'status': 'error',
            'message': 'Sistema TTS no disponible'
        }), 503
    
    try:
        cache_path = current_app.config['SETTINGS'].tts.cache_dir / filename
        if not cache_path.exists():
            return jsonify({
                'status': 'error',
                'message': 'Archivo no encontrado'
            }), 404
        
        with open(cache_path, 'rb') as f:
            audio_data = f.read()
        
        return Response(
            audio_data,
            mimetype='audio/mpeg',
            headers={
                'Content-Disposition': f'inline; filename="{filename}"',
                'Cache-Control': 'public, max-age=31536000'  # Cache por 1 año
            }
        )
        
    except Exception as e:
        logging.exception("❌ Error sirviendo archivo TTS")
        return jsonify({
            'status': 'error',
            'message': 'Error sirviendo archivo',
            'error': str(e)
        }), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    print(f"🔌 Cliente conectado: {request.sid}")
    service = get_prediction_service()
    payload = service.get_status_payload()
    payload['current_prediction'] = service.current_prediction
    emit('status', payload)

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    print(f" Cliente desconectado: {request.sid}")

@socketio.on('start_camera')
def handle_start_camera():
    """Iniciar cámara en tiempo real"""
    service = get_prediction_service()
    if service.is_ready():
        emit('camera_status', {'status': 'started', 'message': 'Cámara iniciada'})
    else:
        emit('camera_status', {'status': 'error', 'message': 'Sistema no disponible'})

@socketio.on('stop_camera')
def handle_stop_camera():
    """Detener cámara"""
    emit('camera_status', {'status': 'stopped', 'message': 'Cámara detenida'})

@socketio.on('process_frame')
def handle_process_frame(data):
    """
    Procesar frame de cámara
    
    data puede contener:
    - 'frame': imagen en base64
    - 'include_landmarks': boolean (opcional, default: false)
    """
    service = get_prediction_service()
    if not service.is_ready():
        emit('prediction', {
            'status': 'error',
            'message': 'Sistema no disponible'
        })
        return
    
    try:
        # Procesar frame (data contiene imagen en base64)
        image_data = data.get('frame', '')
        if not image_data:
            emit('prediction', {
                'status': 'error',
                'message': 'No se proporcionó frame'
            })
            return
            
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Decodificar y procesar
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Verificar si se solicitan landmarks
        include_landmarks = data.get('include_landmarks', False)
        session_id = data.get('session_id') or request.remote_addr
        
        prediction_data = service.predict_from_frame(cv_image, include_landmarks=include_landmarks, session_id=session_id)
        if prediction_data:
            emit('prediction', prediction_data)
        else:
            emit('prediction', {
                'status': 'error',
                'message': 'No se pudieron extraer características'
            })
            
    except Exception as e:
        logging.exception("❌ Error procesando frame")
        emit('prediction', {
            'status': 'error',
            'message': 'Error procesando frame',
            'error': str(e)
        })

@app.route('/api/logs', methods=['GET'])
def api_get_logs():
    """
    Obtener logs de traducciones (solo para admin)
    
    Query parameters:
    - limit: Número máximo de registros (default: 100)
    - session_id: Filtrar por sesión (opcional)
    - start_date: Fecha de inicio ISO (opcional)
    - end_date: Fecha de fin ISO (opcional)
    """
    service = get_prediction_service()
    
    if not hasattr(service, 'logger_service') or not service.logger_service:
        return jsonify({
            'status': 'error',
            'message': 'Servicio de logging no disponible'
        }), 503
    
    try:
        limit = int(request.args.get('limit', 100))
        session_id = request.args.get('session_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        logs = service.logger_service.get_logs(
            limit=limit,
            session_id=session_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'status': 'success',
            'logs': logs,
            'count': len(logs)
        })
    except Exception as e:
        logging.exception("Error obteniendo logs")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo logs',
            'error': str(e)
        }), 500

@app.route('/api/logs/stats', methods=['GET'])
def api_get_logs_stats():
    """
    Obtener estadísticas de traducciones
    """
    service = get_prediction_service()
    
    if not hasattr(service, 'logger_service') or not service.logger_service:
        return jsonify({
            'status': 'error',
            'message': 'Servicio de logging no disponible'
        }), 503
    
    try:
        stats = service.logger_service.get_stats()
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    except Exception as e:
        logging.exception("Error obteniendo estadísticas")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo estadísticas',
            'error': str(e)
        }), 500

@app.route('/api/healthcheck', methods=['GET'])
def api_healthcheck():
    """
    Healthcheck endpoint para verificar estado del sistema
    """
    service = get_prediction_service()
    status_payload = service.get_status_payload()
    
    return jsonify({
        'status': 'ok' if service.is_ready() else 'degraded',
        'system': status_payload,
        'timestamp': time.time()
    })

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
