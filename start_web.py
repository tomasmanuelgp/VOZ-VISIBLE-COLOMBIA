#!/usr/bin/env python3
"""
SIGN-AI - Script de inicio para aplicación web
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """
    Verificar que todos los archivos necesarios estén presentes
    """
    print("🔍 Verificando archivos necesarios...")
    
    required_files = [
        "models/Dense_Simple_patient.h5",
        "data/processed/scaler_optimized.pkl", 
        "data/processed/label_encoder.pkl",
        "data/processed/feature_info.json",
        "web/templates/index.html",
        "web/templates/camera.html",
        "web/static/css/style.css",
        "web/static/js/main.js"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Archivos faltantes:")
        for file in missing_files:
            print(f"  • {file}")
        return False
    
    print("✅ Todos los archivos necesarios están presentes")
    return True

def check_dependencies():
    """
    Verificar dependencias de Python
    """
    print("📦 Verificando dependencias...")
    
    required_packages = [
        'flask',
        'flask-cors', 
        'flask-socketio',
        'tensorflow',
        'mediapipe',
        'opencv-python',
        'numpy',
        'scikit-learn',
        'pillow'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Paquetes faltantes:")
        for package in missing_packages:
            print(f"  • {package}")
        print("\n💡 Instala las dependencias con:")
        print("pip install -r requirements_web.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def start_web_app():
    """
    Iniciar aplicación web
    """
    print("🚀 Iniciando SIGN-AI Web Application...")
    print("=" * 50)
    print("🌐 URL: http://localhost:5000")
    print("📹 Cámara: http://localhost:5000/camera") 
    print("🔧 API: http://localhost:5000/api/status")
    print("=" * 50)
    print("💡 Presiona Ctrl+C para detener el servidor")
    print()
    
    try:
        # Importar y ejecutar la aplicación
        from app import app, socketio, initialize_predictor
        
        # Inicializar sistema
        initialize_predictor()
        
        # Ejecutar aplicación
        socketio.run(app, 
                    debug=False,
                    host='0.0.0.0', 
                    port=5000,
                    allow_unsafe_werkzeug=True)
                    
    except KeyboardInterrupt:
        print("\n\n⏹️ Aplicación detenida por el usuario")
    except Exception as e:
        print(f"\n❌ Error ejecutando la aplicación: {e}")

def main():
    """
    Función principal
    """
    print("🤟 SIGN-AI - Aplicación Web")
    print("=" * 40)
    
    # Verificar archivos
    if not check_requirements():
        print("\n💡 Asegúrate de tener todos los archivos necesarios")
        return False
    
    # Verificar dependencias
    if not check_dependencies():
        return False
    
    # Iniciar aplicación
    start_web_app()
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
