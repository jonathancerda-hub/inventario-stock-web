# analytics_db.py - Sistema de Analytics para Inventario Stock

import sqlite3
import os
from datetime import datetime, timedelta
import pytz
from dateutil import parser
from typing import Optional, Dict, List, Any, Tuple
from logging_config import get_logger

logger = get_logger('analytics_db')

class AnalyticsDB:
    def __init__(self) -> None:
        """Inicializa la conexión a la base de datos de analytics"""
        self.db_type = 'sqlite'  # Por defecto SQLite para desarrollo
        self.db_path = 'analytics.db'
        # Validar table_prefix: solo alfanuméricos y guion bajo (B608: previene SQL injection en nombre de tabla)
        raw_prefix = os.getenv('ANALYTICS_TABLE_PREFIX', '')
        import re
        if raw_prefix and not re.match(r'^[a-zA-Z0-9_]+$', raw_prefix):
            raise ValueError(f"ANALYTICS_TABLE_PREFIX solo puede contener letras, números y guiones bajos. Valor recibido: {raw_prefix!r}")
        self.table_prefix = raw_prefix
        # Usar zona horaria de Perú (America/Lima)
        self.local_tz = pytz.timezone('America/Lima')
        self.peru_tz = self.local_tz  # Mantener peru_tz para compatibilidad
        
        # Intentar con PostgreSQL si está disponible
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            try:
                import psycopg2
                self.db_type = 'postgresql'
                self.database_url = database_url
                logger.info(f"Analytics conectado a PostgreSQL (producción) - Zona horaria: {self.local_tz}")
            except ImportError:
                logger.warning("psycopg2 no disponible, usando SQLite como alternativa")
        else:
            logger.info(f"Analytics usando SQLite (desarrollo) - Zona horaria: {self.local_tz}")
        
        self._create_tables()
    
    def _get_connection(self):
        """Obtiene una conexión a la base de datos según el tipo"""
        if self.db_type == 'postgresql':
            import psycopg2
            return psycopg2.connect(self.database_url)
        else:
            return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        """Crea las tablas necesarias si no existen"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        CREATE TABLE IF NOT EXISTS {self.table_prefix}page_visits (
                            id SERIAL PRIMARY KEY,
                            user_email VARCHAR(255) NOT NULL,
                            user_name VARCHAR(255),
                            page_url VARCHAR(500) NOT NULL,
                            page_title VARCHAR(255),
                            visit_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            session_duration INTEGER DEFAULT 0,
                            ip_address VARCHAR(50),
                            user_agent TEXT,
                            referrer VARCHAR(500),
                            method VARCHAR(10)
                        )
                    """)
                    # Crear índices
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}visits_user ON {self.table_prefix}page_visits(user_email)")
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}visits_timestamp ON {self.table_prefix}page_visits(visit_timestamp DESC)")
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}visits_page ON {self.table_prefix}page_visits(page_url)")
                else:
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        CREATE TABLE IF NOT EXISTS {self.table_prefix}page_visits (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_email TEXT NOT NULL,
                            user_name TEXT,
                            page_url TEXT NOT NULL,
                            page_title TEXT,
                            visit_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            session_duration INTEGER DEFAULT 0,
                            ip_address TEXT,
                            user_agent TEXT,
                            referrer TEXT,
                            method TEXT
                        )
                    """)
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}visits_user ON {self.table_prefix}page_visits(user_email)")
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}visits_timestamp ON {self.table_prefix}page_visits(visit_timestamp)")
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}visits_page ON {self.table_prefix}page_visits(page_url)")
                conn.commit()
                logger.info("Tablas de analytics creadas correctamente")
        except Exception as e:
            logger.error(f"Error creando tablas de analytics: {e}")
    
    def log_visit(self, user_email: str, user_name: str, page_url: str, page_title: Optional[str] = None, 
                  ip_address: Optional[str] = None, user_agent: Optional[str] = None, referrer: Optional[str] = None, method: str = 'GET') -> bool:
        """
        Registra una visita de usuario a una página en la base de datos de analytics.
        
        Args:
            user_email (str): Email del usuario que realiza la visita
            user_name (str): Nombre completo del usuario
            page_url (str): URL de la página visitada
            page_title (str, optional): Título de la página
            ip_address (str, optional): Dirección IP del cliente
            user_agent (str, optional): User-Agent del navegador
            referrer (str, optional): URL de referencia
            method (str, optional): Método HTTP (GET/POST). Default: 'GET'
        
        Returns:
            bool: True si el registro fue exitoso, False en caso de error
        
        Note:
            - Usa zona horaria America/Lima para timestamps
            - Soporta tanto SQLite (desarrollo) como PostgreSQL (producción)
            - Los errores se loggean pero no interrumpen la ejecución
        """
        try:
            # Usar zona horaria local del sistema
            now_peru = datetime.now(self.local_tz)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        INSERT INTO {self.table_prefix}page_visits 
                        (user_email, user_name, page_url, page_title, visit_timestamp, 
                         ip_address, user_agent, referrer, method)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_email, user_name, page_url, page_title, now_peru, 
                          ip_address, user_agent, referrer, method))
                else:
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        INSERT INTO {self.table_prefix}page_visits 
                        (user_email, user_name, page_url, page_title, visit_timestamp, 
                         ip_address, user_agent, referrer, method)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_email, user_name, page_url, page_title, now_peru, 
                          ip_address, user_agent, referrer, method))
                conn.commit()
        except Exception as e:
            logger.error(f"Error registrando visita en analytics: {e}")
    
    def get_total_visits(self, days: int = 30) -> Optional[int]:
        """
        Obtiene el número total de visitas en un período.
        
        Args:
            days (int, optional): Número de días hacia atrás. Default: 30
        
        Returns:
            int: Total de visitas registradas en el período
            None: Si ocurre un error
        
        Note:
            Cuenta todas las visitas sin importar el usuario.
            Ideal para KPIs generales de tráfico.
        """
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT COUNT(*) FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > %s
                    """, (cutoff_date,))
                else:
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT COUNT(*) FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > ?
                    """, (cutoff_date,))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error obteniendo total de visitas: {e}")
            return 0
    
    def get_unique_users(self, days: int = 30) -> Optional[int]:
        """
        Obtiene el número de usuarios únicos en un período.
        
        Args:
            days (int, optional): Número de días hacia atrás. Default: 30
        
        Returns:
            int: Cantidad de usuarios únicos (por email) que visitaron el sitio
            None: Si ocurre un error
        
        Note:
            Cuenta por user_email, permitiendo identificar usuarios recurrentes.
            Útil para medir engagement y penetración de usuarios.
        """
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT COUNT(DISTINCT user_email) FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > %s
                    """, (cutoff_date,))
                else:
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT COUNT(DISTINCT user_email) FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > ?
                    """, (cutoff_date,))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error obteniendo usuarios únicos: {e}")
            return 0
    
    def get_visits_by_user(self, days: int = 30, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene estadísticas de visitas agrupadas por usuario.
        
        Args:
            days (int, optional): Número de días hacia atrás. Default: 30
            limit (int, optional): Máximo de usuarios a retornar. Default: 20
        
        Returns:
            list[dict]: Lista de usuarios ordenada por cantidad de visitas:
                - user_email: Email del usuario
                - user_name: Nombre completo
                - visit_count: Total de visitas
                - last_visit: Fecha/hora de última visita
            None: Si ocurre un error
        
        Note:
            Retorna los usuarios más activos primero.
            Útil para identificar power users y patrones de uso.
        """
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT user_email, user_name, COUNT(*) as visit_count, 
                               MAX(visit_timestamp) as last_visit
                        FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > %s
                        GROUP BY user_email, user_name
                        ORDER BY visit_count DESC
                        LIMIT %s
                    """, (cutoff_date, limit))
                else:
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT user_email, user_name, COUNT(*) as visit_count, 
                               MAX(visit_timestamp) as last_visit
                        FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > ?
                        GROUP BY user_email, user_name
                        ORDER BY visit_count DESC
                        LIMIT ?
                    """, (cutoff_date, limit))
                
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    data = dict(zip(columns, row))
                    # Convertir last_visit a datetime si es string
                    if data.get('last_visit') and isinstance(data['last_visit'], str):
                        try:
                            data['last_visit'] = parser.parse(data['last_visit'])
                        except:
                            data['last_visit'] = None
                    results.append(data)
                return results
        except Exception as e:
            logger.error(f"Error obteniendo visitas por usuario: {e}")
            return []
    
    def get_visits_by_page(self, days: int = 30) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene estadísticas de visitas agrupadas por página.
        
        Args:
            days (int, optional): Número de días hacia atrás. Default: 30
        
        Returns:
            list[dict]: Lista de páginas ordenada por cantidad de visitas:
                - page_url: URL de la página
                - page_title: Título de la página
                - visit_count: Total de visitas
            None: Si ocurre un error
        
        Note:
            Identifica las páginas más populares del sistema.
            Útil para optimizar contenido y mejorar UX.
        """
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT page_url, page_title, COUNT(*) as visit_count
                        FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > %s
                        GROUP BY page_url, page_title
                        ORDER BY visit_count DESC
                    """, (cutoff_date,))
                else:
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT page_url, page_title, COUNT(*) as visit_count
                        FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > ?
                        GROUP BY page_url, page_title
                        ORDER BY visit_count DESC
                    """, (cutoff_date,))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo visitas por página: {e}")
            return []
    
    def get_visits_by_day(self, days=30):
        """
        Obtiene visitas agrupadas por día.
        
        Args:
            days (int, optional): Número de días hacia atrás. Default: 30
        
        Returns:
            list[dict]: Lista de días con estadísticas:
                - visit_date: Fecha (YYYY-MM-DD)
                - visit_count: Total de visitas en ese día
                - unique_users: Usuarios únicos en ese día
            None: Si ocurre un error
        
        Note:
            Usa zona horaria America/Lima para agrupar por fecha local.
            Ideal para gráficos de series temporales y tendencias.
        """
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT DATE(visit_timestamp AT TIME ZONE 'America/Lima') as visit_date, 
                               COUNT(*) as visit_count,
                               COUNT(DISTINCT user_email) as unique_users
                        FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > %s
                        GROUP BY DATE(visit_timestamp AT TIME ZONE 'America/Lima')
                        ORDER BY visit_date ASC
                    """, (cutoff_date,))
                else:
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT DATE(visit_timestamp) as visit_date, 
                               COUNT(*) as visit_count,
                               COUNT(DISTINCT user_email) as unique_users
                        FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > ?
                        GROUP BY DATE(visit_timestamp)
                        ORDER BY visit_date ASC
                    """, (cutoff_date,))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo visitas por día: {e}")
            return []
    
    def get_visits_by_hour(self, days=7):
        """
        Obtiene visitas agrupadas por hora del día.
        
        Args:
            days (int, optional): Número de días hacia atrás. Default: 7
        
        Returns:
            list[dict]: Lista de horas (0-23) con estadísticas:
                - hour: Hora del día (0-23)
                - visit_count: Total de visitas en esa hora
            None: Si ocurre un error
        
        Note:
            Usa zona horaria America/Lima para determinar la hora.
            Útil para identificar horarios pico de uso y optimizar recursos.
        """
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT EXTRACT(HOUR FROM visit_timestamp AT TIME ZONE 'America/Lima') as hour, 
                               COUNT(*) as visit_count
                        FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > %s
                        GROUP BY EXTRACT(HOUR FROM visit_timestamp AT TIME ZONE 'America/Lima')
                        ORDER BY hour ASC
                    """, (cutoff_date,))
                else:
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT CAST(strftime('%H', visit_timestamp) AS INTEGER) as hour, 
                               COUNT(*) as visit_count
                        FROM {self.table_prefix}page_visits 
                        WHERE visit_timestamp > ?
                        GROUP BY CAST(strftime('%H', visit_timestamp) AS INTEGER)
                        ORDER BY hour ASC
                    """, (cutoff_date,))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo visitas por hora: {e}")
            return []
    
    def get_recent_visits(self, limit=50):
        """
        Obtiene las visitas más recientes del sistema.
        
        Args:
            limit (int, optional): Máximo de visitas a retornar. Default: 50
        
        Returns:
            list[dict]: Lista de visitas recientes ordenadas por timestamp:
                - user_email: Email del usuario
                - user_name: Nombre completo
                - page_url: URL visitada
                - page_title: Título de la página
                - visit_timestamp: Fecha/hora de la visita
                - ip_address: IP del cliente
            None: Si ocurre un error
        
        Note:
            Retorna las visitas más recientes primero (DESC).
            Útil para monitoreo en tiempo real y auditoría.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT user_email, user_name, page_url, page_title, 
                               visit_timestamp, ip_address
                        FROM {self.table_prefix}page_visits 
                        ORDER BY visit_timestamp DESC
                        LIMIT %s
                    """, (limit,))
                else:
                    cursor.execute(  # nosec B608 - table_prefix validado en __init__ con regex [a-zA-Z0-9_]+
                        f"""
                        SELECT user_email, user_name, page_url, page_title, 
                               visit_timestamp, ip_address
                        FROM {self.table_prefix}page_visits 
                        ORDER BY visit_timestamp DESC
                        LIMIT ?
                    """, (limit,))
                
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    data = dict(zip(columns, row))
                    # Convertir visit_timestamp a datetime si es string
                    if data.get('visit_timestamp') and isinstance(data['visit_timestamp'], str):
                        try:
                            data['visit_timestamp'] = parser.parse(data['visit_timestamp'])
                        except:
                            data['visit_timestamp'] = None
                    results.append(data)
                return results
        except Exception as e:
            logger.error(f"Error obteniendo visitas recientes: {e}")
            return []
