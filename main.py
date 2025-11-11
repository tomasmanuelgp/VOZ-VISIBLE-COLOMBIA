#!/usr/bin/env python3
"""
SIGN-AI - Sistema de Reconocimiento de Lenguaje de Señas en Tiempo Real
Soporte para múltiples modelos con archivos corregidos
"""

import sys
import os
from pathlib import Path

# Agregar src al path de manera más robusta
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importar predictor
try:
    from inference.real_time_camera import RealTimeCamera
    print("✅ RealTimeCamera importado correctamente")
except ImportError as e:
    print(f"❌ Error importando RealTimeCamera: {e}")
    print(" Verificando estructura de archivos...")
    
    # Verificar si el archivo existe
    camera_path = os.path.join(src_path, 'inference', 'real_time_camera.py')
    if os.path.exists(camera_path):
        print(f"✅ Archivo encontrado en: {camera_path}")
    else:
        print(f"❌ Archivo no encontrado en: {camera_path}")
    
    # Listar contenido de src/inference
    inference_dir = os.path.join(src_path, 'inference')
    if os.path.exists(inference_dir):
        print(f"📁 Contenido de {inference_dir}:")
        for file in os.listdir(inference_dir):
            print(f"  • {file}")
    
    sys.exit(1)

def main():
    """
    Función principal de SIGN-AI con soporte para múltiples modelos
    """
    print("🤟 SIGN-AI - Sistema de Reconocimiento de Lenguaje de Señas")
    print("=" * 60)
    print(" Versión: 1.0")
    print("⚡ Modo: Tiempo Real con Cámara Web")
    print("=" * 60)
    
    # Definir modelos disponibles (en orden de preferencia)
    modelos_disponibles = {
        "Dense_Simple": {
            "path": "models/Dense_Simple_patient.h5",
            "descripcion": "Modelo Dense Simple (98.75% precisión)"
        },
        "Final_Correct": {
            "path": "models/final_correct_model.h5", 
            "descripcion": "Modelo Final Optimizado"
        }
    }
    
    # Archivos comunes necesarios (con nombres corregidos)
    archivos_comunes = {
        "scaler": "data/processed/scaler_optimized.pkl",
        "label_encoder": "data/processed/label_encoder.pkl",
        "feature_info": "data/processed/feature_info.json"
    }
    
    print("🔍 Verificando archivos necesarios...")
    
    # Verificar archivos comunes
    archivos_faltantes = []
    for name, path in archivos_comunes.items():
        if os.path.exists(path):
            print(f"  ✅ {name}: {path}")
        else:
            print(f"  ❌ {name}: {path} - NO ENCONTRADO")
            archivos_faltantes.append(path)
    
    # Verificar modelos disponibles
    modelo_seleccionado = None
    modelos_encontrados = []
    
    for nombre, info in modelos_disponibles.items():
        if os.path.exists(info["path"]):
            print(f"  ✅ {nombre}: {info['path']}")
            modelos_encontrados.append(nombre)
            if modelo_seleccionado is None:  # Usar el primero disponible
                modelo_seleccionado = nombre
        else:
            print(f"  ❌ {nombre}: {info['path']} - NO ENCONTRADO")
    
    if archivos_faltantes:
        print(f"\n❌ ERROR: Faltan {len(archivos_faltantes)} archivos necesarios:")
        for file in archivos_faltantes:
            print(f"  • {file}")
        print("\n💡 Asegúrate de que todos los archivos estén en su lugar")
        print("💡 Verifica que los nombres de archivos no tengan números como (5)")
        return False
    
    if modelo_seleccionado is None:
        print(f"\n❌ ERROR: No se encontró ningún modelo disponible")
        print("💡 Asegúrate de tener al menos uno de estos modelos:")
        for nombre, info in modelos_disponibles.items():
            print(f"  • {info['path']}")
        return False
    
    print(f"\n✅ Todos los archivos encontrados correctamente")
    print(f"🎯 Modelo seleccionado: {modelo_seleccionado}")
    print(f" Descripción: {modelos_disponibles[modelo_seleccionado]['descripcion']}")
    
    if len(modelos_encontrados) > 1:
        print(f"📊 Modelos disponibles: {', '.join(modelos_encontrados)}")
        print(f" Usando {modelo_seleccionado} (primero disponible)")
    
    try:
        # Inicializar sistema de cámara
        print(f"\n Inicializando sistema de cámara...")
        
        camera_system = RealTimeCamera(
            model_path=modelos_disponibles[modelo_seleccionado]["path"],
            scaler_path=archivos_comunes["scaler"],
            label_encoder_path=archivos_comunes["label_encoder"],
            feature_info_path=archivos_comunes["feature_info"]
        )
        
        # Mostrar información del modelo
        model_info = camera_system.get_model_info()
        print(f"\n INFORMACIÓN DEL MODELO:")
        print(f"  • Modelo: {modelo_seleccionado}")
        print(f"  • Características de entrada: {model_info['num_features']}")
        print(f"  • Clases disponibles: {model_info['num_classes']}")
        print(f"  • Capas del modelo: {model_info['num_layers']}")
        print(f"  • FPS de predicción: {model_info['prediction_fps']}")
        
        # Iniciar cámara
        print(f"\n📹 Iniciando cámara...")
        if not camera_system.start_camera():
            print("❌ Error: No se pudo iniciar la cámara")
            return False
        
        # Ejecutar sistema de reconocimiento
        print(f"\n🚀 INICIANDO RECONOCIMIENTO EN TIEMPO REAL")
        print("=" * 50)
        print("📋 INSTRUCCIONES:")
        print("  1. Posiciona tu cámara para que capture tus manos")
        print("  2. Haz gestos de lenguaje de señas")
        print("  3. Observa las predicciones en pantalla")
        print("  4. Usa las teclas para controlar el sistema")
        print("=" * 50)
        
        # Ejecutar sistema
        camera_system.run()
        
        print("\n✅ Sistema finalizado correctamente")
        return True
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Sistema interrumpido por el usuario")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        print("💡 Revisa que todos los archivos estén correctos")
        print("💡 Verifica que los nombres de archivos no tengan números como (5)")
        return False

def show_help():
    """
    Mostrar ayuda del sistema
    """
    print("\n AYUDA - SIGN-AI")
    print("=" * 40)
    print(" OBJETIVO:")
    print("  Reconocimiento de lenguaje de señas en tiempo real usando IA")
    print()
    print("📁 ARCHIVOS NECESARIOS:")
    print("  • models/Dense_Simple_patient.h5 - Modelo Dense Simple")
    print("  • models/final_correct_model.h5 - Modelo Final Optimizado")
    print("  • data/processed/scaler_optimized.pkl - Preprocesador")
    print("  • data/processed/label_encoder.pkl - Codificador de etiquetas")
    print("  • data/processed/feature_info.json - Información de características")
    print()
    print("⌨️ CONTROLES DURANTE LA EJECUCIÓN:")
    print("  • Q - Salir del programa")
    print("  • R - Reiniciar sistema")
    print("  • S - Capturar pantalla")
    print("  • H - Mostrar ayuda")
    print()
    print("🚀 EJECUCIÓN:")
    print("  python main.py")
    print("=" * 40)

if __name__ == "__main__":
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
    else:
        # Ejecutar sistema principal
        success = main()
        
        if success:
            print("\n ¡SIGN-AI ejecutado exitosamente!")
        else:
            print("\n💥 SIGN-AI terminó con errores")
            print(" Usa 'python main.py --help' para ver la ayuda") 