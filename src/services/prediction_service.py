"""Servicios para manejar predicciones de lenguaje de señas."""

from __future__ import annotations

import base64
import io
import logging
import time
from typing import Dict, Optional

import cv2  # type: ignore
import numpy as np
from PIL import Image

from config.settings import AppSettings
from repositories.sign_language_repository import SignLanguageRepository
from services.tts_service import TTSService

logger = logging.getLogger(__name__)

# Importar logging service opcionalmente
try:
    from services.logging_service import TranslationLogger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    logger.warning("TranslationLogger no disponible")


class PredictionService:
    """Gestiona la inicialización y uso del predictor y TTS."""

    def __init__(self, settings: AppSettings, repository: SignLanguageRepository, tts_service: TTSService):
        self.settings = settings
        self.repository = repository
        self.tts_service = tts_service

        self.predictor = None
        self.system_status: str = "initializing"
        self.current_prediction: Dict[str, float | str] = {
            "word": "Iniciando...",
            "confidence": 0.0,
        }
        
        # Inicializar servicio de logging si está disponible
        self.logger_service: Optional[TranslationLogger] = None
        if LOGGING_AVAILABLE:
            try:
                logs_dir = str(settings.upload_folder.parent / "logs")
                self.logger_service = TranslationLogger(logs_dir=logs_dir)
                logger.info("Servicio de logging inicializado")
            except Exception as exc:
                logger.warning("No se pudo inicializar el servicio de logging: %s", exc)

    def initialize(self) -> bool:
        try:
            logger.info("Inicializando predictor de lenguaje de señas")
            self.predictor = self.repository.load_predictor()
            self.tts_service.initialize()
            self.settings.upload_folder.mkdir(parents=True, exist_ok=True)
            self.system_status = "ready"
            logger.info("Sistema inicializado correctamente")
            return True
        except FileNotFoundError as exc:
            self.system_status = "missing_files"
            logger.error("Archivos faltantes: %s", exc)
            return False
        except Exception as exc:  # pylint: disable=broad-except
            self.system_status = "error"
            logger.exception("Error inicializando predictor: %s", exc)
            return False

    def is_ready(self) -> bool:
        return self.system_status == "ready" and self.predictor is not None

    def get_status_payload(self) -> Dict[str, object]:
        model_info = {}
        if self.predictor:
            model_info = self.predictor.get_model_info()
        return {
            "status": self.system_status,
            "message": self._get_status_message(),
            "model_info": model_info,
            "timestamp": time.time(),
        }

    def predict_from_frame(self, cv_image, include_landmarks: bool = False, session_id: Optional[str] = None):
        if not self.is_ready():
            raise RuntimeError("Sistema no disponible")
        
        start_time = time.time()
        word, confidence, success, landmarks = self.predictor.predict_realtime(cv_image, include_landmarks=include_landmarks)  # type: ignore[arg-type]
        response_time_ms = (time.time() - start_time) * 1000
        
        if not success:
            return None
        
        self.current_prediction = {"word": word, "confidence": float(confidence)}
        
        # Registrar en logs si está disponible
        if self.logger_service:
            try:
                self.logger_service.log_translation(
                    text_translated=word,
                    confidence=float(confidence),
                    response_time_ms=response_time_ms,
                    session_id=session_id
                )
            except Exception as exc:
                logger.warning("Error registrando traducción en logs: %s", exc)
        
        audio_data = self.tts_service.generate_audio_base64(word)
        response = {
            "status": "success",
            "word": word,
            "confidence": float(confidence),
            "timestamp": time.time(),
            "response_time_ms": round(response_time_ms, 2),
        }
        if audio_data:
            response["audio"] = audio_data
        if landmarks:
            response["landmarks"] = landmarks
        return response

    def predict_from_base64(self, image_data: str, include_landmarks: bool = False, session_id: Optional[str] = None):
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return self.predict_from_frame(cv_image, include_landmarks=include_landmarks, session_id=session_id)

    def _get_status_message(self) -> str:
        messages = {
            "initializing": "Inicializando sistema...",
            "ready": "Sistema listo",
            "error": "Error en el sistema",
            "missing_files": "Archivos del modelo no encontrados",
        }
        return messages.get(self.system_status, "Estado desconocido")


__all__ = ["PredictionService"]
