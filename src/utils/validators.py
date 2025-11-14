"""
Utilidades para validación de datos en Voz Visible
"""

from __future__ import annotations

import base64
import re
from typing import Tuple, Optional


def validate_base64_image(image_data: str) -> Tuple[bool, Optional[str]]:
    """
    Valida que una cadena sea una imagen base64 válida
    
    Args:
        image_data: Cadena con imagen en base64
        
    Returns:
        Tupla (es_válida, mensaje_error)
    """
    if not image_data:
        return False, "La imagen no puede estar vacía"
    
    # Verificar formato data URI
    if image_data.startswith('data:image'):
        # Extraer el base64
        try:
            parts = image_data.split(',')
            if len(parts) != 2:
                return False, "Formato de data URI inválido"
            
            base64_part = parts[1]
            # Validar formato de imagen
            image_type = parts[0].split(';')[0].split(':')[1]
            if image_type not in ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']:
                return False, f"Tipo de imagen no soportado: {image_type}"
        except Exception:
            return False, "Error procesando data URI"
    else:
        # Asumir que es base64 puro
        base64_part = image_data
    
    # Validar que sea base64 válido
    try:
        # Intentar decodificar
        decoded = base64.b64decode(base64_part, validate=True)
        if len(decoded) == 0:
            return False, "La imagen está vacía"
        
        # Verificar tamaño máximo (10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(decoded) > max_size:
            return False, f"La imagen es demasiado grande (máximo {max_size // (1024*1024)}MB)"
        
        # Verificar tamaño mínimo (1KB)
        min_size = 1024  # 1KB
        if len(decoded) < min_size:
            return False, "La imagen es demasiado pequeña"
        
    except Exception as e:
        return False, f"Error validando base64: {str(e)}"
    
    return True, None


def validate_text_for_tts(text: str, max_length: int = 500) -> Tuple[bool, Optional[str]]:
    """
    Valida texto para síntesis de voz
    
    Args:
        text: Texto a validar
        max_length: Longitud máxima permitida
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not text:
        return False, "El texto no puede estar vacío"
    
    if not isinstance(text, str):
        return False, "El texto debe ser una cadena de caracteres"
    
    text = text.strip()
    
    if len(text) == 0:
        return False, "El texto no puede estar vacío"
    
    if len(text) > max_length:
        return False, f"El texto es demasiado largo (máximo {max_length} caracteres)"
    
    # Verificar caracteres válidos (básico)
    if not re.match(r'^[\w\s\.,;:!?¡¿áéíóúÁÉÍÓÚñÑüÜ\-\(\)]+$', text):
        return False, "El texto contiene caracteres no válidos"
    
    return True, None


def validate_session_id(session_id: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Valida un ID de sesión
    
    Args:
        session_id: ID de sesión a validar
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if session_id is None:
        return True, None  # Opcional
    
    if not isinstance(session_id, str):
        return False, "El session_id debe ser una cadena"
    
    if len(session_id) == 0:
        return False, "El session_id no puede estar vacío"
    
    if len(session_id) > 100:
        return False, "El session_id es demasiado largo (máximo 100 caracteres)"
    
    # Solo caracteres alfanuméricos, guiones y guiones bajos
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        return False, "El session_id contiene caracteres no válidos"
    
    return True, None


def validate_confidence(confidence: float) -> Tuple[bool, Optional[str]]:
    """
    Valida un valor de confianza
    
    Args:
        confidence: Valor de confianza (0-1)
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not isinstance(confidence, (int, float)):
        return False, "La confianza debe ser un número"
    
    if confidence < 0 or confidence > 1:
        return False, "La confianza debe estar entre 0 y 1"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo para evitar problemas de seguridad
    
    Args:
        filename: Nombre de archivo a sanitizar
        
    Returns:
        Nombre de archivo sanitizado
    """
    # Remover caracteres peligrosos
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limitar longitud
    if len(filename) > 255:
        filename = filename[:255]
    return filename


__all__ = [
    "validate_base64_image",
    "validate_text_for_tts",
    "validate_session_id",
    "validate_confidence",
    "sanitize_filename"
]

