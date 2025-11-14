"""Servicio para manejar Text-to-Speech."""

from __future__ import annotations

import base64
import logging
from typing import Optional

from config.settings import AppSettings
from tts.voice_synthesizer import VoiceSynthesizer

logger = logging.getLogger(__name__)


class TTSService:
    """Encapsula la lógica de síntesis de voz."""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.synthesizer: Optional[VoiceSynthesizer] = None

    def initialize(self) -> None:
        try:
            self.synthesizer = VoiceSynthesizer(
                cache_dir=str(self.settings.tts.cache_dir),
                language=self.settings.tts.language,
                slow=self.settings.tts.slow,
            )
            logger.info("Servicio TTS inicializado")
        except Exception as exc:
            self.synthesizer = None
            logger.exception("No se pudo inicializar el servicio TTS: %s", exc)

    def generate_audio_base64(self, text: str) -> Optional[str]:
        if not self.synthesizer:
            return None
        audio_bytes, error = self.synthesizer.text_to_speech(text)
        if error or not audio_bytes:
            logger.warning("Error generando audio TTS: %s", error)
            return None
        return f"data:audio/mpeg;base64,{base64.b64encode(audio_bytes).decode('utf-8')}"

    def save_audio_file(self, text: str) -> Optional[str]:
        if not self.synthesizer:
            return None
        file_path, error = self.synthesizer.text_to_speech_file(text)
        if error:
            logger.warning("Error guardando archivo TTS: %s", error)
            return None
        return file_path

    def is_available(self) -> bool:
        return self.synthesizer is not None


__all__ = ["TTSService"]
