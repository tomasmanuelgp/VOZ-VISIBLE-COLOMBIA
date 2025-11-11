import cv2
import numpy as np
import sys
import os
from typing import Optional

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from inference.sign_language_predictor import SignLanguagePredictor

class RealTimeCamera:
    """
    Sistema de cámara en tiempo real para SIGN-AI
    
    Funcionalidades:
    - Captura de video en tiempo real
    - Reconocimiento de lenguaje de señas
    - Visualización de resultados
    - Controles de usuario
    """
    
    def __init__(self, model_path: str, scaler_path: str, label_encoder_path: str, feature_info_path: str):
        """
        Inicializar sistema de cámara en tiempo real
        
        Args:
            model_path: Ruta al modelo .h5
            scaler_path: Ruta al scaler .pkl
            label_encoder_path: Ruta al label encoder .pkl
            feature_info_path: Ruta al feature_info.json
        """
        print("📹 Inicializando sistema de cámara en tiempo real...")
        
        # Inicializar predictor
        self.predictor = SignLanguagePredictor(
            model_path, scaler_path, label_encoder_path, feature_info_path
        )
        
        # Configurar cámara
        self.cap = None
        self.is_running = False
        
        # Variables para visualización
        self.current_prediction = "Iniciando..."
        self.current_confidence = 0.0
        self.prediction_history = []
        
        print("✅ Sistema de cámara inicializado")
    
    def start_camera(self, camera_index: int = 0) -> bool:
        """
        Iniciar cámara
        
        Args:
            camera_index: Índice de la cámara (0 = cámara por defecto)
            
        Returns:
            True si se inició correctamente, False si hay error
        """
        try:
            # Inicializar cámara
            self.cap = cv2.VideoCapture(camera_index)
            
            if not self.cap.isOpened():
                print(f"❌ Error: No se pudo abrir la cámara {camera_index}")
                return False
            
            # Configurar resolución
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"✅ Cámara {camera_index} iniciada correctamente")
            print(f"📊 Resolución: 640x480")
            print(f"�� FPS: 30")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al iniciar cámara: {e}")
            return False
    
    def run(self):
        """
        Ejecutar sistema de reconocimiento en tiempo real
        """
        if not self.cap or not self.cap.isOpened():
            print("❌ Error: Cámara no inicializada")
            return
        
        print("�� Iniciando reconocimiento en tiempo real...")
        print("📋 Controles:")
        print("  • 'q' - Salir")
        print("  • 'r' - Reiniciar")
        print("  • 's' - Capturar pantalla")
        print("  • 'h' - Mostrar ayuda")
        print("=" * 50)
        
        self.is_running = True
        
        while self.is_running:
            # Leer frame de la cámara
            ret, frame = self.cap.read()
            
            if not ret:
                print("❌ Error: No se pudo leer frame de la cámara")
                break
            
            # Voltear frame horizontalmente (efecto espejo)
            frame = cv2.flip(frame, 1)
            
            # Hacer predicción en tiempo real
            prediction, confidence, prediction_made = self.predictor.predict_realtime(frame)
            
            if prediction_made:
                self.current_prediction = prediction
                self.current_confidence = confidence
                
                # Agregar a historial
                self.prediction_history.append((prediction, confidence))
                if len(self.prediction_history) > 10:  # Mantener solo últimas 10
                    self.prediction_history.pop(0)
            
            # Dibujar información en el frame
            frame = self._draw_info(frame)
            
            # Mostrar frame
            cv2.imshow('SIGN-AI - Reconocimiento en Tiempo Real', frame)
            
            # Manejar teclas
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self._reset()
            elif key == ord('s'):
                self._save_screenshot(frame)
            elif key == ord('h'):
                self._show_help()
        
        self._cleanup()
    
    def _draw_info(self, frame: np.ndarray) -> np.ndarray:
        """
        Dibujar información en el frame
        
        Args:
            frame: Frame de video
            
        Returns:
            Frame con información dibujada
        """
        # Configurar colores
        color_white = (255, 255, 255)
        color_black = (0, 0, 0)
        color_green = (0, 255, 0)
        color_red = (0, 0, 255)
        
        # Dibujar fondo para texto
        cv2.rectangle(frame, (10, 10), (400, 120), color_black, -1)
        cv2.rectangle(frame, (10, 10), (400, 120), color_white, 2)
        
        # Dibujar predicción actual
        cv2.putText(frame, f"Prediccion: {self.current_prediction}", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_white, 2)
        
        # Dibujar confianza
        confidence_color = color_green if self.current_confidence > 0.7 else color_red
        cv2.putText(frame, f"Confianza: {self.current_confidence:.2f}", 
                   (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, confidence_color, 2)
        
        # Dibujar historial
        if self.prediction_history:
            recent_pred = self.prediction_history[-1][0]
            cv2.putText(frame, f"Ultimo: {recent_pred}", 
                       (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_white, 1)
        
        # Dibujar controles
        cv2.putText(frame, "Controles: Q=Salir, R=Reiniciar, S=Captura, H=Ayuda", 
                   (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_white, 1)
        
        return frame
    
    def _reset(self):
        """Reiniciar sistema"""
        self.current_prediction = "Reiniciando..."
        self.current_confidence = 0.0
        self.prediction_history.clear()
        print("🔄 Sistema reiniciado")
    
    def _save_screenshot(self, frame: np.ndarray):
        """Guardar captura de pantalla"""
        filename = f"screenshot_{len(self.prediction_history)}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Captura guardada: {filename}")
    
    def _show_help(self):
        """Mostrar ayuda"""
        print("\n📋 AYUDA - SIGN-AI")
        print("=" * 30)
        print("🎯 Objetivo: Reconocer lenguaje de señas en tiempo real")
        print("📹 Cámara: Usa tu cámara web")
        print("🤟 Gestos: Haz señas con las manos")
        print("📊 Resultado: Aparece en pantalla")
        print("\n⌨️ Controles:")
        print("  • Q - Salir del programa")
        print("  • R - Reiniciar sistema")
        print("  • S - Capturar pantalla")
        print("  • H - Mostrar esta ayuda")
        print("=" * 30)
    
    def _cleanup(self):
        """Limpiar recursos"""
        print("🧹 Limpiando recursos...")
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        self.is_running = False
        
        print("✅ Recursos liberados")
    
    def get_model_info(self) -> dict:
        """Obtener información del modelo"""
        return self.predictor.get_model_info()