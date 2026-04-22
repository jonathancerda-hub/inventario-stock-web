# logging_config.py - Configuración de logging estructurado para la aplicación

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """
    Formatter personalizado que agrega colores a los logs en consola.
    
    Colores por nivel:
    - DEBUG: Cyan
    - INFO: Verde
    - WARNING: Amarillo
    - ERROR: Rojo
    - CRITICAL: Rojo brillante
    """
    
    # Códigos de color ANSI
    grey = "\x1b[38;21m"
    cyan = "\x1b[36;21m"
    green = "\x1b[32;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    FORMATS = {
        logging.DEBUG: cyan + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: green + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def setup_logging(
    name: str = 'inventario-stock',
    level: Optional[str] = None,
    log_to_file: bool = True,
    log_dir: str = 'logs'
) -> logging.Logger:
    """
    Configura el sistema de logging de la aplicación.
    
    Args:
        name: Nombre del logger (por defecto: 'inventario-stock')
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Si es None, usa la variable de entorno LOG_LEVEL o INFO por defecto.
        log_to_file: Si True, guarda logs en archivo rotativo
        log_dir: Directorio donde guardar los logs
    
    Returns:
        Logger configurado
    
    Features:
        - Logs coloridos en consola
        - Rotación automática de archivos (10MB max, 5 backups)
        - Formato estructurado con timestamp, nombre y nivel
        - Configuración por entorno (development/production)
    
    Example:
        >>> logger = setup_logging('odoo_manager')
        >>> logger.info('Conexión establecida')
        >>> logger.error('Error al conectar', exc_info=True)
    """
    # Obtener nivel desde parámetro, variable de entorno o usar INFO por defecto
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Convertir string a nivel de logging
    numeric_level = getattr(logging, level, logging.INFO)
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Evitar duplicados si ya está configurado
    if logger.handlers:
        return logger
    
    # Handler para consola con colores
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # Handler para archivo (solo si está habilitado)
    if log_to_file:
        # Crear directorio de logs si no existe
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Archivo de log con fecha
        log_filename = os.path.join(
            log_dir,
            f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # RotatingFileHandler: max 10MB por archivo, mantener 5 backups
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        
        # Formato sin colores para archivo
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger hijo del logger principal.
    
    Args:
        name: Nombre del módulo/componente
    
    Returns:
        Logger configurado
    
    Example:
        >>> from logging_config import get_logger
        >>> logger = get_logger('analytics_db')
        >>> logger.info('Iniciando conexión')
    """
    return logging.getLogger(f'inventario-stock.{name}')


# Logger principal de la aplicación
app_logger = setup_logging(
    name='inventario-stock',
    level=os.getenv('LOG_LEVEL', 'INFO'),
    log_to_file=os.getenv('ENVIRONMENT', 'development') == 'production'
)
