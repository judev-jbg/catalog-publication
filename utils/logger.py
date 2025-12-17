"""
Sistema de logging centralizado con colores y archivos rotativos
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import colorlog

from config import LOGS_DIR, LOG_LEVEL


def setup_logger(name: str = "catalog_publisher") -> logging.Logger:
    """
    Configura un logger con salida a consola (con colores) y archivo
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Formato para consola (con colores)
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # Formato para archivo (sin colores)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (log diario)
    log_file = LOGS_DIR / f"catalog_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


# Logger principal
logger = setup_logger()
