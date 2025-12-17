"""
Servicio para manejo de archivos en rutas UNC
Incluye: listar, leer, copiar y eliminar archivos PDF
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from config import SOURCE_PATH, DEST_PATH
from utils.logger import logger


class FileService:
    """Maneja operaciones con archivos en rutas UNC"""
    
    def __init__(self):
        self.source_path = Path(SOURCE_PATH)
        self.dest_path = Path(DEST_PATH)
        logger.info(f"FileService inicializado - Source: {self.source_path}")
    
    def list_catalogs(self) -> List[Dict[str, any]]:
        """
        Lista todos los archivos PDF en la carpeta origen
        
        Returns:
            Lista de diccionarios con información de archivos
        """
        try:
            if not self.source_path.exists():
                logger.error(f"La ruta origen no existe: {self.source_path}")
                return []
            
            pdf_files = list(self.source_path.glob("*.pdf"))
            
            catalogs = []
            for pdf_file in pdf_files:
                try:
                    stat = pdf_file.stat()
                    catalogs.append({
                        'fileName': pdf_file.name,
                        'fullPath': str(pdf_file),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'exists': True
                    })
                except Exception as e:
                    logger.warning(f"Error al obtener info de {pdf_file.name}: {str(e)}")
            
            logger.info(f"✅ Encontrados {len(catalogs)} catálogos en {self.source_path}")
            return catalogs
            
        except Exception as e:
            logger.error(f"❌ Error al listar catálogos: {str(e)}")
            return []
    
    def read_file(self, file_path: str) -> Optional[bytes]:
        """
        Lee el contenido binario de un archivo
        
        Args:
            file_path: Ruta completa del archivo
            
        Returns:
            Contenido del archivo en bytes o None si hay error
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"Archivo no encontrado: {file_path}")
                return None
            
            with open(path, 'rb') as f:
                content = f.read()
            
            logger.debug(f"Archivo leído: {path.name} ({len(content)} bytes)")
            return content
            
        except Exception as e:
            logger.error(f"❌ Error al leer archivo {file_path}: {str(e)}")
            return None
    
    def copy_to_destination(self, source_file: str, dest_filename: str) -> bool:
        """
        Copia un archivo a la carpeta destino
        
        Args:
            source_file: Ruta del archivo origen
            dest_filename: Nombre del archivo destino
            
        Returns:
            True si la copia fue exitosa, False en caso contrario
        """
        try:
            source = Path(source_file)
            destination = self.dest_path / dest_filename
            
            if not source.exists():
                logger.error(f"Archivo origen no existe: {source}")
                return False
            
            # Crear carpeta destino si no existe
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivo
            shutil.copy2(source, destination)
            
            logger.info(f"✅ Archivo copiado: {source.name} -> {destination}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al copiar archivo {source_file}: {str(e)}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """
        Elimina un archivo
        
        Args:
            file_path: Ruta completa del archivo a eliminar
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.warning(f"Archivo no existe (ya eliminado?): {file_path}")
                return True  # Considerar exitoso si ya no existe
            
            path.unlink()
            logger.info(f"🗑️  Archivo eliminado: {path.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al eliminar archivo {file_path}: {str(e)}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """
        Verifica si un archivo existe
        
        Args:
            file_path: Ruta completa del archivo
            
        Returns:
            True si existe, False en caso contrario
        """
        return Path(file_path).exists()
