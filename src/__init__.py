# src/__init__.py
"""
SIGN-AI - Módulo principal
Sistema de Reconocimiento de Lenguaje de Señas
"""

__version__ = "1.0.0"
__author__ = "SIGN-AI Team"

# Importar clases principales
try:
    from .inference.sign_language_predictor import SignLanguagePredictor
    from .inference.real_time_camera import RealTimeCamera
    __all__ = ['SignLanguagePredictor', 'RealTimeCamera']
except ImportError:
    # Si hay problemas de importación, definir como lista vacía
    __all__ = []

