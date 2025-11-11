# src/inference/__init__.py
"""
SIGN-AI - Módulo de Inferencia
Sistema de predicción de lenguaje de señas
"""

from .sign_language_predictor import SignLanguagePredictor
from .real_time_camera import RealTimeCamera

__all__ = ['SignLanguagePredictor', 'RealTimeCamera']

