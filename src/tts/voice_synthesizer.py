"""
Voice Synthesizer - Módulo de Text-to-Speech para VOZ VISIBLE
Soporta síntesis de voz en español colombiano usando gTTS
"""

import os
import hashlib
import time
from typing import Optional, Tuple
from pathlib import Path
import logging

try:
    from gtts import gTTS
    import io
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logging.warning("gTTS no está disponible. Instala con: pip install gtts")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logging.warning("pygame no está disponible para reproducción local. Instala con: pip install pygame")


class VoiceSynthesizer:
    """
    Sintetizador de voz para convertir texto a audio
    
    Características:
    - Soporte para español colombiano
    - Cache de audio generado
    - Múltiples formatos de salida
    - Reproducción opcional
    """
    
    def __init__(self, cache_dir: str = "data/cache/tts", language: str = "es-co", slow: bool = False):
        """
        Inicializar sintetizador de voz
        
        Args:
            cache_dir: Directorio para cache de archivos de audio
            language: Código de idioma (es-co para español colombiano)
            slow: Si True, habla más lento
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.language = language
        self.slow = slow
        
        self.logger = logging.getLogger(__name__)
        
        if not GTTS_AVAILABLE:
            self.logger.error("gTTS no está disponible. La síntesis de voz no funcionará.")
        
        self.logger.info(f"✅ VoiceSynthesizer inicializado (idioma: {language}, cache: {cache_dir})")
    
    def _get_cache_path(self, text: str) -> Path:
        """
        Obtener ruta de cache para un texto
        
        Args:
            text: Texto a convertir
            
        Returns:
            Ruta del archivo de cache
        """
        # Crear hash del texto para nombre de archivo
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        cache_filename = f"{text_hash}.mp3"
        return self.cache_dir / cache_filename
    
    def text_to_speech(self, text: str, use_cache: bool = True) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Convertir texto a audio
        
        Args:
            text: Texto a convertir a voz
            use_cache: Si True, usa cache si existe
            
        Returns:
            Tupla (audio_bytes, error_message)
            - audio_bytes: Bytes del archivo MP3, None si hay error
            - error_message: Mensaje de error, None si es exitoso
        """
        if not GTTS_AVAILABLE:
            return None, "gTTS no está disponible. Instala con: pip install gtts"
        
        if not text or not text.strip():
            return None, "Texto vacío"
        
        text = text.strip()
        
        # Verificar cache
        cache_path = self._get_cache_path(text)
        if use_cache and cache_path.exists():
            self.logger.debug(f"📦 Usando cache para: {text[:50]}...")
            try:
                with open(cache_path, 'rb') as f:
                    return f.read(), None
            except Exception as e:
                self.logger.warning(f"Error leyendo cache: {e}")
        
        # Generar audio con gTTS
        try:
            self.logger.debug(f"🎤 Generando audio para: {text[:50]}...")
            
            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            
            # Guardar en buffer de memoria
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_bytes = audio_buffer.getvalue()
            
            # Guardar en cache
            if use_cache:
                try:
                    with open(cache_path, 'wb') as f:
                        f.write(audio_bytes)
                    self.logger.debug(f"💾 Audio guardado en cache: {cache_path}")
                except Exception as e:
                    self.logger.warning(f"Error guardando cache: {e}")
            
            return audio_bytes, None
            
        except Exception as e:
            error_msg = f"Error generando audio: {str(e)}"
            self.logger.error(error_msg)
            return None, error_msg
    
    def text_to_speech_file(self, text: str, output_path: Optional[str] = None, use_cache: bool = True) -> Tuple[Optional[str], Optional[str]]:
        """
        Convertir texto a archivo de audio
        
        Args:
            text: Texto a convertir
            output_path: Ruta de salida (opcional, usa cache si no se especifica)
            use_cache: Si True, usa cache si existe
            
        Returns:
            Tupla (file_path, error_message)
        """
        if not text or not text.strip():
            return None, "Texto vacío"
        
        text = text.strip()
        
        # Determinar ruta de salida
        if output_path is None:
            output_path = str(self._get_cache_path(text))
        else:
            output_path = str(Path(output_path))
        
        # Verificar cache
        cache_path = self._get_cache_path(text)
        if use_cache and cache_path.exists() and output_path == str(cache_path):
            self.logger.debug(f"📦 Usando cache para: {text[:50]}...")
            return str(cache_path), None
        
        # Generar audio
        audio_bytes, error = self.text_to_speech(text, use_cache=use_cache)
        
        if error:
            return None, error
        
        # Guardar archivo
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                f.write(audio_bytes)
            
            self.logger.debug(f"💾 Audio guardado en: {output_file}")
            return str(output_file), None
            
        except Exception as e:
            error_msg = f"Error guardando archivo: {str(e)}"
            self.logger.error(error_msg)
            return None, error_msg
    
    def play_audio(self, audio_bytes: bytes) -> bool:
        """
        Reproducir audio desde bytes (requiere pygame)
        
        Args:
            audio_bytes: Bytes del archivo de audio
            
        Returns:
            True si se reprodujo correctamente, False si hay error
        """
        if not PYGAME_AVAILABLE:
            self.logger.warning("pygame no está disponible. No se puede reproducir audio.")
            return False
        
        try:
            # Inicializar pygame mixer si no está inicializado
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            # Crear archivo temporal en memoria
            audio_file = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Esperar a que termine la reproducción
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error reproduciendo audio: {e}")
            return False
    
    def clear_cache(self, older_than_days: Optional[int] = None) -> int:
        """
        Limpiar cache de archivos de audio
        
        Args:
            older_than_days: Si se especifica, solo elimina archivos más antiguos que X días
            
        Returns:
            Número de archivos eliminados
        """
        deleted_count = 0
        current_time = time.time()
        
        try:
            for cache_file in self.cache_dir.glob("*.mp3"):
                if older_than_days is None:
                    cache_file.unlink()
                    deleted_count += 1
                else:
                    file_age = current_time - cache_file.stat().st_mtime
                    if file_age > (older_than_days * 86400):  # 86400 segundos = 1 día
                        cache_file.unlink()
                        deleted_count += 1
            
            self.logger.info(f"🗑️ Cache limpiado: {deleted_count} archivos eliminados")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error limpiando cache: {e}")
            return deleted_count
    
    def get_cache_size(self) -> int:
        """
        Obtener tamaño total del cache en bytes
        
        Returns:
            Tamaño del cache en bytes
        """
        total_size = 0
        try:
            for cache_file in self.cache_dir.glob("*.mp3"):
                total_size += cache_file.stat().st_size
        except Exception as e:
            self.logger.error(f"Error calculando tamaño de cache: {e}")
        
        return total_size

