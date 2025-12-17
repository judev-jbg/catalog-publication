"""
Servicio para subir archivos al FTP de Selk
"""
import ftplib
from typing import Optional
from io import BytesIO

from config import FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD, FTP_UPLOAD_PATH
from utils.logger import logger


class FTPService:
    """Maneja operaciones con el servidor FTP"""
    
    def __init__(self):
        self.host = FTP_HOST
        self.port = FTP_PORT
        self.user = FTP_USER
        self.password = FTP_PASSWORD
        self.upload_path = FTP_UPLOAD_PATH
        self.ftp = None
    
    def _connect(self) -> bool:
        """
        Establece conexión con el servidor FTP
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            self.ftp = ftplib.FTP()
            self.ftp.connect(self.host, self.port, timeout=30)
            self.ftp.login(self.user, self.password)
            
            # Cambiar al directorio de subida
            try:
                self.ftp.cwd(self.upload_path)
            except ftplib.error_perm:
                logger.warning(f"Directorio {self.upload_path} no existe, intentando crear...")
                # Intentar crear directorios recursivamente
                self._create_directory_recursive(self.upload_path)
                self.ftp.cwd(self.upload_path)
            
            logger.info(f"✅ Conectado al FTP: {self.host}:{self.port}")
            return True
            
        except ftplib.all_errors as e:
            logger.error(f"❌ Error al conectar con FTP: {str(e)}")
            self.ftp = None
            return False
    
    def _create_directory_recursive(self, path: str):
        """
        Crea directorios recursivamente en el FTP
        
        Args:
            path: Ruta a crear
        """
        parts = path.strip('/').split('/')
        current_path = ''
        
        for part in parts:
            current_path += '/' + part
            try:
                self.ftp.cwd(current_path)
            except ftplib.error_perm:
                try:
                    self.ftp.mkd(current_path)
                    logger.debug(f"Directorio creado en FTP: {current_path}")
                except ftplib.error_perm as e:
                    logger.warning(f"No se pudo crear directorio {current_path}: {str(e)}")
    
    def _disconnect(self):
        """Cierra la conexión FTP"""
        if self.ftp:
            try:
                self.ftp.quit()
                logger.debug("Desconectado del FTP")
            except:
                try:
                    self.ftp.close()
                except:
                    pass
            self.ftp = None
    
    def upload_file(self, file_content: bytes, remote_filename: str) -> bool:
        """
        Sube un archivo al servidor FTP
        
        Args:
            file_content: Contenido del archivo en bytes
            remote_filename: Nombre del archivo en el servidor
            
        Returns:
            True si la subida fue exitosa, False en caso contrario
        """
        if not self._connect():
            return False
        
        try:
            # Crear un objeto BytesIO para simular un archivo
            file_obj = BytesIO(file_content)
            
            # Subir archivo
            self.ftp.storbinary(f'STOR {remote_filename}', file_obj)
            
            logger.info(f"✅ Archivo subido al FTP: {remote_filename}")
            return True
            
        except ftplib.all_errors as e:
            logger.error(f"❌ Error al subir archivo al FTP: {str(e)}")
            return False
            
        finally:
            self._disconnect()
    
    def file_exists(self, remote_filename: str) -> bool:
        """
        Verifica si un archivo existe en el servidor FTP
        
        Args:
            remote_filename: Nombre del archivo a verificar
            
        Returns:
            True si el archivo existe, False en caso contrario
        """
        if not self._connect():
            return False
        
        try:
            # Listar archivos en el directorio actual
            files = self.ftp.nlst()
            exists = remote_filename in files
            
            logger.debug(f"Archivo {'existe' if exists else 'no existe'} en FTP: {remote_filename}")
            return exists
            
        except ftplib.all_errors as e:
            logger.error(f"❌ Error al verificar archivo en FTP: {str(e)}")
            return False
            
        finally:
            self._disconnect()
    
    def delete_file(self, remote_filename: str) -> bool:
        """
        Elimina un archivo del servidor FTP
        
        Args:
            remote_filename: Nombre del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        if not self._connect():
            return False
        
        try:
            self.ftp.delete(remote_filename)
            logger.info(f"🗑️  Archivo eliminado del FTP: {remote_filename}")
            return True
            
        except ftplib.all_errors as e:
            logger.error(f"❌ Error al eliminar archivo del FTP: {str(e)}")
            return False
            
        finally:
            self._disconnect()
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión FTP
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        result = self._connect()
        self._disconnect()
        return result
