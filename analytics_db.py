# analytics_db.py - Sistema de Analytics para Inventario Stock

import sqlite3
import os
from datetime import datetime, timedelta
import pytz
import tzlocal
from dateutil import parser

class AnalyticsDB:
    def __init__(self):
        """Inicializa la conexión a la base de datos de analytics"""
        self.db_type = 'sqlite'  # Por defecto SQLite para desarrollo
        self.db_path = 'analytics.db'
        # Usar zona horaria local del sistema
        try:
            self.local_tz = tzlocal.get_localzone()
        except:
            # Fallback a America/Lima si no se puede detectar
            self.local_tz = pytz.timezone('America/Lima')
        self.peru_tz = self.local_tz  # Mantener peru_tz para compatibilidad
        
        # Intentar con PostgreSQL si está disponible
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            try:
                import psycopg2
                self.db_type = 'postgresql'
                self.database_url = database_url
                print(f"✅ Analytics conectado a PostgreSQL (producción) - Zona horaria: {self.local_tz}")
            except ImportError:
                print("⚠️ psycopg2 no disponible, usando SQLite")
        else:
            print(f"📊 Analytics usando SQLite (desarrollo) - Zona horaria: {self.local_tz}")
        
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
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS page_visits (
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
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_visits_user ON page_visits(user_email)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_visits_timestamp ON page_visits(visit_timestamp DESC)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_visits_page ON page_visits(page_url)")
                else:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS page_visits (
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
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_visits_user ON page_visits(user_email)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_visits_timestamp ON page_visits(visit_timestamp)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_visits_page ON page_visits(page_url)")
                conn.commit()
                print("📊 Tablas de analytics creadas correctamente")
        except Exception as e:
            print(f"❌ Error creando tablas de analytics: {e}")
    
    def log_visit(self, user_email, user_name, page_url, page_title=None, 
                  ip_address=None, user_agent=None, referrer=None, method='GET'):
        """Registra una visita de usuario a una página"""
        try:
            # Usar zona horaria local del sistema
            now_peru = datetime.now(self.local_tz)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute("""
                        INSERT INTO page_visits 
                        (user_email, user_name, page_url, page_title, visit_timestamp, 
                         ip_address, user_agent, referrer, method)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_email, user_name, page_url, page_title, now_peru, 
                          ip_address, user_agent, referrer, method))
                else:
                    cursor.execute("""
                        INSERT INTO page_visits 
                        (user_email, user_name, page_url, page_title, visit_timestamp, 
                         ip_address, user_agent, referrer, method)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_email, user_name, page_url, page_title, now_peru, 
                          ip_address, user_agent, referrer, method))
                conn.commit()
        except Exception as e:
            print(f"❌ Error registrando visita: {e}")
    
    def get_total_visits(self, days=30):
        """Obtiene el número total de visitas en un período"""
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT COUNT(*) FROM page_visits 
                        WHERE visit_timestamp > %s
                    """, (cutoff_date,))
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM page_visits 
                        WHERE visit_timestamp > ?
                    """, (cutoff_date,))
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"❌ Error obteniendo total de visitas: {e}")
            return 0
    
    def get_unique_users(self, days=30):
        """Obtiene el número de usuarios únicos en un período"""
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT COUNT(DISTINCT user_email) FROM page_visits 
                        WHERE visit_timestamp > %s
                    """, (cutoff_date,))
                else:
                    cursor.execute("""
                        SELECT COUNT(DISTINCT user_email) FROM page_visits 
                        WHERE visit_timestamp > ?
                    """, (cutoff_date,))
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"❌ Error obteniendo usuarios únicos: {e}")
            return 0
    
    def get_visits_by_user(self, days=30, limit=20):
        """Obtiene estadísticas de visitas por usuario"""
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT user_email, user_name, COUNT(*) as visit_count, 
                               MAX(visit_timestamp) as last_visit
                        FROM page_visits 
                        WHERE visit_timestamp > %s
                        GROUP BY user_email, user_name
                        ORDER BY visit_count DESC
                        LIMIT %s
                    """, (cutoff_date, limit))
                else:
                    cursor.execute("""
                        SELECT user_email, user_name, COUNT(*) as visit_count, 
                               MAX(visit_timestamp) as last_visit
                        FROM page_visits 
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
            print(f"❌ Error obteniendo visitas por usuario: {e}")
            return []
    
    def get_visits_by_page(self, days=30):
        """Obtiene estadísticas de visitas por página"""
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT page_url, page_title, COUNT(*) as visit_count
                        FROM page_visits 
                        WHERE visit_timestamp > %s
                        GROUP BY page_url, page_title
                        ORDER BY visit_count DESC
                    """, (cutoff_date,))
                else:
                    cursor.execute("""
                        SELECT page_url, page_title, COUNT(*) as visit_count
                        FROM page_visits 
                        WHERE visit_timestamp > ?
                        GROUP BY page_url, page_title
                        ORDER BY visit_count DESC
                    """, (cutoff_date,))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Error obteniendo visitas por página: {e}")
            return []
    
    def get_visits_by_day(self, days=30):
        """Obtiene visitas agrupadas por día"""
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT DATE(visit_timestamp) as visit_date, 
                               COUNT(*) as visit_count,
                               COUNT(DISTINCT user_email) as unique_users
                        FROM page_visits 
                        WHERE visit_timestamp > %s
                        GROUP BY DATE(visit_timestamp)
                        ORDER BY visit_date ASC
                    """, (cutoff_date,))
                else:
                    cursor.execute("""
                        SELECT DATE(visit_timestamp) as visit_date, 
                               COUNT(*) as visit_count,
                               COUNT(DISTINCT user_email) as unique_users
                        FROM page_visits 
                        WHERE visit_timestamp > ?
                        GROUP BY DATE(visit_timestamp)
                        ORDER BY visit_date ASC
                    """, (cutoff_date,))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Error obteniendo visitas por día: {e}")
            return []
    
    def get_visits_by_hour(self, days=7):
        """Obtiene visitas agrupadas por hora del día"""
        try:
            cutoff_date = datetime.now(self.peru_tz) - timedelta(days=days)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT EXTRACT(HOUR FROM visit_timestamp) as hour, 
                               COUNT(*) as visit_count
                        FROM page_visits 
                        WHERE visit_timestamp > %s
                        GROUP BY EXTRACT(HOUR FROM visit_timestamp)
                        ORDER BY hour ASC
                    """, (cutoff_date,))
                else:
                    cursor.execute("""
                        SELECT CAST(strftime('%H', visit_timestamp) AS INTEGER) as hour, 
                               COUNT(*) as visit_count
                        FROM page_visits 
                        WHERE visit_timestamp > ?
                        GROUP BY CAST(strftime('%H', visit_timestamp) AS INTEGER)
                        ORDER BY hour ASC
                    """, (cutoff_date,))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Error obteniendo visitas por hora: {e}")
            return []
    
    def get_recent_visits(self, limit=50):
        """Obtiene las visitas más recientes del sistema"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT user_email, user_name, page_url, page_title, 
                               visit_timestamp, ip_address
                        FROM page_visits 
                        ORDER BY visit_timestamp DESC
                        LIMIT %s
                    """, (limit,))
                else:
                    cursor.execute("""
                        SELECT user_email, user_name, page_url, page_title, 
                               visit_timestamp, ip_address
                        FROM page_visits 
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
            print(f"❌ Error obteniendo visitas recientes: {e}")
            return []
