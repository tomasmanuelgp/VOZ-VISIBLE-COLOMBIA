import tensorflow as tf
import mediapipe as mp
import cv2
import numpy as np
import pickle
import json
from typing import Tuple, Optional
import time

class SignLanguagePredictor:
    """
    Predictor de lenguaje de señas optimizado para SIGN-AI
    
    Características:
    - Extrae exactamente 258 características (compatible con modelo entrenado)
    - Pose: 33 landmarks × 4 valores = 132 características
    - Mano derecha: 21 landmarks × 3 valores = 63 características  
    - Mano izquierda: 21 landmarks × 3 valores = 63 características
    - Total: 258 características
    """
    
    def __init__(self, model_path: str, scaler_path: str, label_encoder_path: str, feature_info_path: str):
        """
        Inicializar predictor de lenguaje de señas
        
        Args:
            model_path: Ruta al modelo .h5 entrenado
            scaler_path: Ruta al scaler .pkl
            label_encoder_path: Ruta al label encoder .pkl
            feature_info_path: Ruta al archivo feature_info.json
        """
        print("🤖 Inicializando SignLanguagePredictor...")
        
        # Cargar modelo entrenado
        self.model = tf.keras.models.load_model(model_path)
        print(f"✅ Modelo cargado: {model_path}")
        
        # Cargar preprocesadores
        self.scaler = pickle.load(open(scaler_path, 'rb'))
        self.label_encoder = pickle.load(open(label_encoder_path, 'rb'))
        print(f"✅ Scaler y Label Encoder cargados")
        
        # Cargar información de características
        with open(feature_info_path, 'r', encoding='utf-8') as f:
            self.feature_info = json.load(f)
        
        # Obtener número de características (258)
        self.num_features = 258  # Valor fijo basado en el modelo
        print(f"✅ Feature info cargado: {self.num_features} características")
        
        # Inicializar MediaPipe Holistic
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            model_complexity=1,
            static_image_mode=False
        )
        
        # Configurar dibujo de landmarks
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Variables para tiempo real
        self.last_prediction_time = 0
        self.prediction_interval = 0.1  # Predecir cada 100ms (10 FPS)
        
        print("🎯 Predictor inicializado correctamente")
        print(f"📊 Características esperadas: {self.num_features}")
        print(f"📊 Clases disponibles: {len(self.label_encoder.classes_)}")
        print(f"⚡ Frecuencia de predicción: {1/self.prediction_interval} FPS")
    
    def extract_landmarks(self, frame: np.ndarray) -> Tuple[np.ndarray, any]:
        """
        Extraer landmarks de un frame de cámara (optimizado para tiempo real)
        
        Args:
            frame: Frame de cámara (BGR)
            
        Returns:
            Tupla (características, resultados_mediapipe)
        """
        # Convertir BGR a RGB para MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Procesar con MediaPipe Holistic
        results = self.holistic.process(rgb_frame)
        
        # Inicializar array de características (258 características)
        features = np.zeros(258, dtype=np.float32)
        
        # Extraer características de POSE (33 landmarks × 4 valores = 132 características)
        if results.pose_landmarks:
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                if i < 33:  # Solo 33 landmarks de pose
                    idx = i * 4
                    features[idx] = landmark.x      # Coordenada X
                    features[idx + 1] = landmark.y  # Coordenada Y
                    features[idx + 2] = landmark.z  # Coordenada Z
                    features[idx + 3] = landmark.visibility  # Visibilidad
        
        # Extraer características de MANO DERECHA (21 landmarks × 3 valores = 63 características)
        if results.right_hand_landmarks:
            for i, landmark in enumerate(results.right_hand_landmarks.landmark):
                if i < 21:  # Solo 21 landmarks por mano
                    idx = 132 + (i * 3)  # Empezar después de pose (132)
                    features[idx] = landmark.x      # Coordenada X
                    features[idx + 1] = landmark.y  # Coordenada Y
                    features[idx + 2] = landmark.z  # Coordenada Z
        
        # Extraer características de MANO IZQUIERDA (21 landmarks × 3 valores = 63 características)
        if results.left_hand_landmarks:
            for i, landmark in enumerate(results.left_hand_landmarks.landmark):
                if i < 21:  # Solo 21 landmarks por mano
                    idx = 195 + (i * 3)  # Empezar después de pose + mano derecha (195)
                    features[idx] = landmark.x      # Coordenada X
                    features[idx + 1] = landmark.y  # Coordenada Y
                    features[idx + 2] = landmark.z  # Coordenada Z
        
        return features, results
    
    def predict_realtime(self, frame: np.ndarray) -> Tuple[str, float, bool]:
        """
        Predecir lenguaje de señas en tiempo real (con control de frecuencia)
        
        Args:
            frame: Frame de cámara (BGR)
            
        Returns:
            Tupla (clase_predicha, confianza, prediccion_realizada)
        """
        current_time = time.time()
        
        # Controlar frecuencia de predicción para optimizar rendimiento
        if current_time - self.last_prediction_time < self.prediction_interval:
            return "Esperando...", 0.0, False
        
        try:
            # Extraer características del frame
            features, results = self.extract_landmarks(frame)
            
            # Normalizar características usando el scaler entrenado
            features_scaled = self.scaler.transform([features])
            
            # Hacer predicción con el modelo
            prediction = self.model.predict(features_scaled, verbose=0)
            
            # Obtener clase con mayor probabilidad
            class_idx = np.argmax(prediction[0])
            confidence = float(prediction[0][class_idx])
            
            # Decodificar índice a nombre de clase
            class_name = self.label_encoder.inverse_transform([class_idx])[0]
            
            # Actualizar tiempo de última predicción
            self.last_prediction_time = current_time
            
            return class_name, confidence, True
            
        except Exception as e:
            print(f"❌ Error en predicción: {e}")
            return "Error", 0.0, False
    
    def draw_landmarks_realtime(self, frame: np.ndarray, results) -> np.ndarray:
        """
        Dibujar landmarks detectados en el frame (optimizado para tiempo real)
        
        Args:
            frame: Frame de cámara (BGR)
            results: Resultados de MediaPipe Holistic
            
        Returns:
            Frame con landmarks dibujados
        """
        # Dibujar landmarks de pose (verde)
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                self.mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
            )
        
        # Dibujar landmarks de mano derecha (rojo)
        if results.right_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, 
                results.right_hand_landmarks, 
                self.mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
        
        # Dibujar landmarks de mano izquierda (azul)
        if results.left_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, 
                results.left_hand_landmarks, 
                self.mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
        
        return frame
    
    def get_model_info(self) -> dict:
        """
        Obtener información del modelo
        
        Returns:
            Diccionario con información del modelo
        """
        return {
            "input_shape": self.model.input_shape,
            "output_shape": self.model.output_shape,
            "num_layers": len(self.model.layers),
            "num_classes": len(self.label_encoder.classes_),
            "classes": list(self.label_encoder.classes_),
            "num_features": self.num_features,
            "prediction_fps": 1/self.prediction_interval
        }
