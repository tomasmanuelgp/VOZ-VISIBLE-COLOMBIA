from __future__ import annotations

"""Configuración centralizada para VOZ VISIBLE."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _resolve_path(value: str | None, default: str) -> Path:
    return Path(value or default).resolve()


@dataclass(slots=True)
class ModelConfig:
    primary_model_path: Path = _resolve_path(
        os.getenv("MODEL_PRIMARY_PATH"),
        "models/Dense_Simple_patient.h5",
    )
    secondary_model_path: Path = _resolve_path(
        os.getenv("MODEL_SECONDARY_PATH"),
        "models/final_correct_model.h5",
    )
    scaler_path: Path = _resolve_path(
        os.getenv("SCALER_PATH"),
        "data/processed/scaler_optimized.pkl",
    )
    label_encoder_path: Path = _resolve_path(
        os.getenv("LABEL_ENCODER_PATH"),
        "data/processed/label_encoder.pkl",
    )
    feature_info_path: Path = _resolve_path(
        os.getenv("FEATURE_INFO_PATH"),
        "data/processed/feature_info.json",
    )

    def required_files(self) -> List[Path]:
        return [
            self.primary_model_path,
            self.secondary_model_path,
            self.scaler_path,
            self.label_encoder_path,
            self.feature_info_path,
        ]


@dataclass(slots=True)
class TTSConfig:
    cache_dir: Path = _resolve_path(
        os.getenv("TTS_CACHE_PATH"),
        "data/cache/tts",
    )
    language: str = os.getenv("TTS_LANGUAGE", "es-co")
    slow: bool = os.getenv("TTS_SLOW", "false").lower() == "true"


@dataclass(slots=True)
class AppSettings:
    secret_key: str = os.getenv("APP_SECRET_KEY", "voz-visible-secret-key-2024")
    upload_folder: Path = _resolve_path(
        os.getenv("UPLOAD_FOLDER"),
        "web/uploads",
    )
    debug: bool = os.getenv("APP_DEBUG", "false").lower() == "true"

    model: ModelConfig = ModelConfig()
    tts: TTSConfig = TTSConfig()


__all__ = ["AppSettings", "ModelConfig", "TTSConfig"]
