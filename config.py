"""
Configuración centralizada de la aplicación Inventario Stock Web.

Este módulo contiene todas las constantes y configuraciones de la aplicación,
evitando valores hardcodeados (magic numbers) en el código principal.
"""

from datetime import timedelta
from typing import Final


class SessionConfig:
    """Configuración de sesiones de usuario."""
    
    # Tiempo de expiración de sesión por inactividad
    TIMEOUT_MINUTES: Final[int] = 15
    LIFETIME: Final[timedelta] = timedelta(minutes=TIMEOUT_MINUTES)
    
    # Flags de seguridad de cookies
    COOKIE_SECURE: Final[bool] = True  # Solo HTTPS en producción
    COOKIE_HTTPONLY: Final[bool] = True  # Prevenir acceso desde JavaScript
    COOKIE_SAMESITE: Final[str] = 'Lax'  # Protección contra CSRF


class ExportConfig:
    """Configuración de exportaciones de datos."""
    
    # Límite máximo de filas en exportaciones
    MAX_ROWS: Final[int] = 10000
    
    # Formato de números en Excel
    NUMBER_FORMAT: Final[str] = '#,##0'
    
    # Ancho de columnas en Excel
    COLUMN_WIDTH: Final[int] = 15


class CacheConfig:
    """Configuración de caché."""
    
    # Tamaño máximo del caché LRU
    LRU_CACHE_SIZE: Final[int] = 32
    
    # TTL (Time To Live) del caché en segundos
    TTL_SECONDS: Final[int] = 300  # 5 minutos


class AnalyticsConfig:
    """Configuración de analytics."""
    
    # Período de retención de datos en días
    DATA_RETENTION_DAYS: Final[int] = 30
    
    # Período por defecto para reportes en días
    DEFAULT_REPORT_PERIOD_DAYS: Final[int] = 30


class OdooConfig:
    """Configuración de integración con Odoo."""
    
    # Número de reintentos de conexión
    CONNECTION_RETRIES: Final[int] = 3
    
    # Timeout de conexión en segundos
    CONNECTION_TIMEOUT_SECONDS: Final[int] = 30
    
    # Límite de registros por consulta (paginación)
    DEFAULT_LIMIT: Final[int] = 1000
    
    # Batch size para lectura de datos
    BATCH_SIZE: Final[int] = 100


class SecurityConfig:
    """Configuración de seguridad."""
    
    # Rate limiting (requests por minuto)
    RATE_LIMIT_PER_MINUTE: Final[int] = 60
    
    # Rate limiting para exportaciones (por hora)
    EXPORT_RATE_LIMIT_PER_HOUR: Final[int] = 10
    
    # Longitud mínima de contraseña (si se implementa)
    MIN_PASSWORD_LENGTH: Final[int] = 12
    
    # Rotación de secrets (días)
    SECRET_ROTATION_DAYS: Final[int] = 90


class AppConfig:
    """Configuración general de la aplicación."""
    
    # Modo debug (solo development)
    DEBUG: Final[bool] = False
    
    # Host y puerto para desarrollo
    DEV_HOST: Final[str] = '0.0.0.0'  # nosec B104 — intencional, producción usa reverse proxy
    DEV_PORT: Final[int] = 5000
    
    # Número de workers para producción (Gunicorn)
    PRODUCTION_WORKERS: Final[int] = 4
    
    # Timeout de requests en segundos
    REQUEST_TIMEOUT_SECONDS: Final[int] = 120


class LoggingConfig:
    """Configuración de logging."""
    
    # Nivel de logging por defecto
    DEFAULT_LEVEL: Final[str] = 'INFO'
    
    # Formato de fecha en logs
    DATE_FORMAT: Final[str] = '%Y-%m-%d %H:%M:%S'
    
    # Tamaño máximo de archivo de log (bytes)
    MAX_LOG_FILE_SIZE: Final[int] = 10 * 1024 * 1024  # 10 MB
    
    # Número de archivos de log a mantener (rotación)
    BACKUP_COUNT: Final[int] = 5


# Configuración consolidada para fácil acceso
class Config:
    """Clase contenedora de todas las configuraciones."""
    
    Session = SessionConfig
    Export = ExportConfig
    Cache = CacheConfig
    Analytics = AnalyticsConfig
    Odoo = OdooConfig
    Security = SecurityConfig
    App = AppConfig
    Logging = LoggingConfig
