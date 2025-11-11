
import numpy as np
import tensorflow as tf
import joblib
import json
from pathlib import Path

class SignLanguageInference:
    """Sistema de inferencia para reconocimiento de lenguaje de señas"""

    def __init__(self, model_path, scaler_path, label_encoder_path, feature_info_path):
        """Inicializar sistema de inferencia"""
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_info = None
        self.class_names = None

        # Cargar componentes
        self._load_components(model_path, scaler_path, label_encoder_path, feature_info_path)

    def _load_components(self, model_path, scaler_path, label_encoder_path, feature_info_path):
        """Cargar todos los componentes necesarios"""
        try:
            # Cargar modelo
            self.model = tf.keras.models.load_model(model_path)

            # Cargar preprocesadores
            self.scaler = joblib.load(scaler_path)
            self.label_encoder = joblib.load(label_encoder_path)

            # Cargar información de características
            with open(feature_info_path, 'r', encoding='utf-8') as f:
                self.feature_info = json.load(f)
            self.class_names = self.feature_info['class_names']

        except Exception as e:
            print(f"❌ Error cargando componentes: {str(e)}")
            raise

    def preprocess_landmarks(self, landmarks_dict):
        """Preprocesar landmarks para inferencia"""
        try:
            # Extraer características en el orden correcto
            feature_columns = self.feature_info['feature_columns']
            features = []

            for col in feature_columns:
                if col in landmarks_dict:
                    features.append(landmarks_dict[col])
                else:
                    features.append(0.0)  # Valor por defecto

            # Convertir a array numpy
            features_array = np.array(features).reshape(1, -1)

            # Normalizar características
            features_normalized = self.scaler.transform(features_array)

            return features_normalized

        except Exception as e:
            print(f"❌ Error preprocesando landmarks: {str(e)}")
            return None

    def predict(self, landmarks_dict, return_probabilities=False):
        """Realizar predicción"""
        try:
            # Preprocesar landmarks
            features = self.preprocess_landmarks(landmarks_dict)
            if features is None:
                return None

            # Hacer predicción
            predictions = self.model.predict(features, verbose=0)
            predicted_class_idx = np.argmax(predictions[0])
            predicted_class = self.class_names[predicted_class_idx]
            confidence = predictions[0][predicted_class_idx]

            if return_probabilities:
                # Crear diccionario con probabilidades de todas las clases
                probabilities = {}
                for i, class_name in enumerate(self.class_names):
                    probabilities[class_name] = float(predictions[0][i])

                return {
                    'predicted_class': predicted_class,
                    'confidence': float(confidence),
                    'probabilities': probabilities
                }
            else:
                return {
                    'predicted_class': predicted_class,
                    'confidence': float(confidence)
                }

        except Exception as e:
            print(f"❌ Error en predicción: {str(e)}")
            return None

    def get_model_info(self):
        """Obtener información del modelo"""
        return {
            'model_name': self.model.name if hasattr(self.model, 'name') else 'Unknown',
            'n_classes': len(self.class_names),
            'n_features': self.feature_info['n_features'],
            'class_names': self.class_names,
            'feature_columns': self.feature_info['feature_columns']
        }
