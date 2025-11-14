"""Repositorio para gestionar carga de modelos de lenguaje de señas."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from config.settings import AppSettings

logger = logging.getLogger(__name__)


class SignLanguageRepository:
    """Repositorio encargado de validar y cargar recursos del predictor."""

    def __init__(self, settings: AppSettings):
        self.settings = settings

    def _import_predictor(self):
        from inference.sign_language_predictor import SignLanguagePredictor  # type: ignore

        return SignLanguagePredictor

    def validate_required_files(self) -> list[Path]:
        missing_files: list[Path] = []
        for file_path in self.settings.model.required_files():
            if not file_path.exists():
                missing_files.append(file_path)
        return missing_files

    def load_predictor(self):
        missing_files = self.validate_required_files()
        if missing_files:
            raise FileNotFoundError(
                "Faltan archivos requeridos para el predictor: "
                + ", ".join(str(path) for path in missing_files)
            )

        SignLanguagePredictor = self._import_predictor()
        logger.info("Cargando modelo de lenguaje de señas desde %s", self.settings.model.primary_model_path)

        predictor = SignLanguagePredictor(
            model_path=str(self.settings.model.primary_model_path),
            scaler_path=str(self.settings.model.scaler_path),
            label_encoder_path=str(self.settings.model.label_encoder_path),
            feature_info_path=str(self.settings.model.feature_info_path),
        )

        return predictor


__all__ = ["SignLanguageRepository"]
