"""
SIGN-AI - Web Predictor
Predictor optimizado para aplicación web con manejo de imágenes
"""

import cv2
import numpy as np
import base64
from PIL import Image
import io
from typing import Tuple, Optional, Dict, Any
import sys
import os

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from inference.sign_language_predictor import SignLanguagePredictor

class WebSignLanguagePredictor(SignLanguagePredictor):
    """
    Predictor de lenguaje de señas optimizado para aplicación web
    
    Características adicionales:
    - Manejo de imágenes base64
    - Procesamiento de archivos subidos
    - Optimizaciones para tiempo real web
    """
    
    def __init__(self, model_path: str, scaler_path: str, label_encoder_path: str, feature_info_path: str):
        """
        Inicializar predictor web
        """
        super().__init__(model_path, scaler_path, label_encoder_path, feature_info_path)
        print("🌐 WebSignLanguagePredictor inicializado")
    
    def predict_from_base64(self, image_base64: str) -> Tuple[str, float, bool]:
        """
        Predecir desde imagen en base64
        
        Args:
            image_base64: Imagen codificada en base64
            
        Returns:
            Tupla (clase_predicha, confianza, éxito)
        """
        try:
            # Limpiar header de data URL si existe
            if image_base64.startswith('data:image'):
                image_base64 = image_base64.split(',')[1]
            
            # Decodificar imagen
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convertir a formato OpenCV (BGR)
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Realizar predicción usando el método padre
            return self.predict_realtime(cv_image)
            
        except Exception as e:
            print(f"❌ Error en predict_from_base64: {e}")
            return "Error", 0.0, False
    
    def predict_from_file(self, file_path: str) -> Tuple[str, float, bool]:
        """
        Predecir desde archivo de imagen
        
        Args:
            file_path: Ruta al archivo de imagen
            
        Returns:
            Tupla (clase_predicha, confianza, éxito)
        """
        try:
            # Cargar imagen
            image = cv2.imread(file_path)
            if image is None:
                return "Error", 0.0, False
            
            # Realizar predicción
            return self.predict_realtime(image)
            
        except Exception as e:
            print(f"❌ Error en predict_from_file: {e}")
            return "Error", 0.0, False
    
    def predict_from_landmarks(self, landmarks_dict: Dict[str, float]) -> Tuple[str, float, bool]:
        """
        Predecir desde landmarks directos
        
        Args:
            landmarks_dict: Diccionario con landmarks extraídos
            
        Returns:
            Tupla (clase_predicha, confianza, éxito)
        """
        try:
            # Crear array de características
            features = np.zeros(258, dtype=np.float32)
            
            # Mapear landmarks al array de características
            for i, (key, value) in enumerate(landmarks_dict.items()):
                if i < 258:
                    features[i] = float(value)
            
            # Normalizar características
            features_scaled = self.scaler.transform([features])
            
            # Hacer predicción
            prediction = self.model.predict(features_scaled, verbose=0)
            
            # Obtener resultado
            class_idx = np.argmax(prediction[0])
            confidence = float(prediction[0][class_idx])
            class_name = self.label_encoder.inverse_transform([class_idx])[0]
            
            return class_name, confidence, True
            
        except Exception as e:
            print(f"❌ Error en predict_from_landmarks: {e}")
            return "Error", 0.0, False
    
    def get_web_model_info(self) -> Dict[str, Any]:
        """
        Obtener información del modelo para web
        
        Returns:
            Diccionario con información del modelo
        """
        base_info = self.get_model_info()
        
        # Agregar información específica para web
        web_info = {
            **base_info,
            'web_features': {
                'supports_base64': True,
                'supports_file_upload': True,
                'supports_landmarks': True,
                'supports_realtime': True
            },
            'supported_formats': ['jpg', 'jpeg', 'png', 'bmp'],
            'max_image_size': '10MB',
            'prediction_time': '< 100ms'
        }
        
        return web_info
