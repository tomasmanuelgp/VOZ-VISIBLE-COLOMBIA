"""
Servicio de logging para traducciones de Voz Visible
Guarda cada predicción con información detallada
"""

from __future__ import annotations

import csv
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TranslationLogger:
    """Servicio para registrar traducciones en CSV y SQLite"""

    def __init__(self, logs_dir: str = "backend/logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.csv_file = self.logs_dir / "translations.csv"
        self.db_file = self.logs_dir / "translations.db"
        
        self._init_csv()
        self._init_database()

    def _init_csv(self):
        """Inicializar archivo CSV con headers si no existe"""
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'text_translated',
                    'confidence',
                    'response_time_ms',
                    'session_id',
                    'user_id'
                ])

    def _init_database(self):
        """Inicializar base de datos SQLite"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                text_translated TEXT NOT NULL,
                confidence REAL NOT NULL,
                response_time_ms INTEGER NOT NULL,
                session_id TEXT,
                user_id TEXT
            )
        ''')
        
        # Crear índices para búsquedas rápidas
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON translations(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session 
            ON translations(session_id)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Base de datos de traducciones inicializada en %s", self.db_file)

    def log_translation(
        self,
        text_translated: str,
        confidence: float,
        response_time_ms: float,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """
        Registrar una traducción en CSV y SQLite
        
        Args:
            text_translated: Texto traducido
            confidence: Confianza del modelo (0-1)
            response_time_ms: Tiempo de respuesta en milisegundos
            session_id: ID de sesión (opcional)
            user_id: ID de usuario (opcional)
        """
        timestamp = datetime.now().isoformat()
        
        try:
            # Guardar en CSV
            self._log_to_csv(
                timestamp, text_translated, confidence,
                response_time_ms, session_id, user_id
            )
            
            # Guardar en SQLite
            self._log_to_db(
                timestamp, text_translated, confidence,
                response_time_ms, session_id, user_id
            )
            
            logger.debug(
                "Traducción registrada: %s (confianza: %.2f%%, tiempo: %.2fms)",
                text_translated,
                confidence * 100,
                response_time_ms
            )
        except Exception as exc:
            logger.exception("Error registrando traducción: %s", exc)

    def _log_to_csv(
        self,
        timestamp: str,
        text_translated: str,
        confidence: float,
        response_time_ms: float,
        session_id: Optional[str],
        user_id: Optional[str]
    ):
        """Guardar en archivo CSV"""
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                text_translated,
                confidence,
                int(response_time_ms),
                session_id or '',
                user_id or ''
            ])

    def _log_to_db(
        self,
        timestamp: str,
        text_translated: str,
        confidence: float,
        response_time_ms: float,
        session_id: Optional[str],
        user_id: Optional[str]
    ):
        """Guardar en base de datos SQLite"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO translations 
            (timestamp, text_translated, confidence, response_time_ms, session_id, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, text_translated, confidence, int(response_time_ms), session_id, user_id))
        
        conn.commit()
        conn.close()

    def get_logs(
        self,
        limit: int = 100,
        session_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtener logs de traducciones
        
        Args:
            limit: Número máximo de registros
            session_id: Filtrar por sesión
            start_date: Fecha de inicio (ISO format)
            end_date: Fecha de fin (ISO format)
            
        Returns:
            Lista de diccionarios con los logs
        """
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM translations WHERE 1=1'
        params = []
        
        if session_id:
            query += ' AND session_id = ?'
            params.append(session_id)
        
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def get_stats(self) -> Dict:
        """
        Obtener estadísticas de traducciones
        
        Returns:
            Diccionario con estadísticas
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Total de traducciones
        cursor.execute('SELECT COUNT(*) FROM translations')
        total = cursor.fetchone()[0]
        
        # Promedio de confianza
        cursor.execute('SELECT AVG(confidence) FROM translations')
        avg_confidence = cursor.fetchone()[0] or 0
        
        # Promedio de tiempo de respuesta
        cursor.execute('SELECT AVG(response_time_ms) FROM translations')
        avg_response_time = cursor.fetchone()[0] or 0
        
        # Última traducción
        cursor.execute('''
            SELECT timestamp, text_translated, confidence 
            FROM translations 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        last_translation = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_translations': total,
            'avg_confidence': round(avg_confidence, 4) if avg_confidence else 0,
            'avg_response_time_ms': round(avg_response_time, 2) if avg_response_time else 0,
            'last_translation': {
                'timestamp': last_translation[0] if last_translation else None,
                'text': last_translation[1] if last_translation else None,
                'confidence': last_translation[2] if last_translation else None,
            }
        }


__all__ = ["TranslationLogger"]

