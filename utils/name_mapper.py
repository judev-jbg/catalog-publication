"""
Utilidad para normalizar nombres de archivos de catálogos
"""
from config import CATALOG_NAME_MAPPING
from utils.logger import logger


def normalize_catalog_name(filename: str) -> tuple[str, bool]:
    """
    Normaliza el nombre de un catálogo según el mapping configurado

    Args:
        filename: Nombre del archivo original

    Returns:
        Tupla con (nombre_normalizado, encontrado_en_mapeo)
    """
    # Búsqueda exacta primero
    if filename in CATALOG_NAME_MAPPING:
        logger.debug(f"Normalizado: {filename} -> {CATALOG_NAME_MAPPING[filename]}")
        return CATALOG_NAME_MAPPING[filename], True

    # Búsqueda flexible (sin distinguir mayúsculas/minúsculas y espacios)
    normalized_input = filename.lower().replace(" ", "")

    for original, mapped in CATALOG_NAME_MAPPING.items():
        normalized_key = original.lower().replace(" ", "")
        if normalized_key == normalized_input:
            logger.debug(f"Normalizado (flexible): {filename} -> {mapped}")
            return mapped, True

    # Si no se encuentra, devolver el original y registrar advertencia
    logger.warning(f"No se encontró mapeo para: {filename}")
    return filename, False


def get_all_mapped_names() -> dict:
    """
    Obtiene todo el mapeo de nombres
    
    Returns:
        Diccionario con el mapeo completo
    """
    return CATALOG_NAME_MAPPING.copy()
