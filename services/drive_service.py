"""
Servicio para interactuar con Google Drive
Sube, actualiza y busca archivos en la carpeta de catálogos
Usa Service Account para autenticación sin intervención del usuario
"""
import io
import os
from pathlib import Path
from typing import Optional, Dict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from config import GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_DRIVE_FOLDER_ID, BASE_DIR
from utils.logger import logger

# Scopes requeridos para Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']


class DriveService:
    """Maneja operaciones con Google Drive usando Service Account"""

    def __init__(self):
        self.service = None
        self.folder_id = GOOGLE_DRIVE_FOLDER_ID
        self._authenticate()

    def _authenticate(self):
        """Autentica con Google Drive API usando Service Account (sin intervención del usuario)"""
        credentials_path = BASE_DIR / GOOGLE_SERVICE_ACCOUNT_FILE

        if not credentials_path.exists():
            logger.error(f"❌ Archivo de Service Account no encontrado: {credentials_path}")
            logger.error("Por favor, crea una Service Account en Google Cloud Console")
            return

        try:
            # Cargar credenciales desde el archivo de Service Account
            creds = Credentials.from_service_account_file(
                str(credentials_path),
                scopes=SCOPES
            )

            # Crear servicio
            self.service = build('drive', 'v3', credentials=creds)

            # Validar conexión
            self.service.about().get(fields="user").execute()
            logger.info("✅ Autenticación con Service Account exitosa")
            logger.info("✅ Servicio de Google Drive inicializado")

        except Exception as e:
            logger.error(f"❌ Error al autenticar con Service Account: {str(e)}")
            self.service = None
    
    def search_file(self, file_name: str) -> Optional[Dict]:
        """
        Busca un archivo en la carpeta de catálogos
        
        Args:
            file_name: Nombre del archivo a buscar
            
        Returns:
            Información del archivo si existe, None en caso contrario
        """
        if not self.service:
            logger.error("Servicio de Google Drive no disponible")
            return None
        
        try:
            query = f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, modifiedTime, size)',
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                logger.debug(f"Archivo encontrado en Drive: {file_name}")
                return files[0]  # Retornar el primero si hay múltiples
            else:
                logger.debug(f"Archivo no encontrado en Drive: {file_name}")
                return None
                
        except HttpError as e:
            logger.error(f"❌ Error al buscar archivo en Drive: {str(e)}")
            return None
    
    def upload_file(self, file_content: bytes, file_name: str) -> Optional[str]:
        """
        Sube un nuevo archivo a Google Drive
        
        Args:
            file_content: Contenido del archivo en bytes
            file_name: Nombre del archivo
            
        Returns:
            ID del archivo creado o None si hay error
        """
        if not self.service:
            logger.error("Servicio de Google Drive no disponible")
            return None
        
        try:
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id]
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype='application/pdf',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name'
            ).execute()
            
            logger.info(f"✅ Archivo subido a Drive: {file_name} (ID: {file.get('id')})")
            return file.get('id')
            
        except HttpError as e:
            logger.error(f"❌ Error al subir archivo a Drive: {str(e)}")
            return None
    
    def update_file(self, file_id: str, file_content: bytes, file_name: str) -> bool:
        """
        Actualiza un archivo existente en Google Drive
        
        Args:
            file_id: ID del archivo en Drive
            file_content: Nuevo contenido del archivo
            file_name: Nombre del archivo
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        if not self.service:
            logger.error("Servicio de Google Drive no disponible")
            return False
        
        try:
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype='application/pdf',
                resumable=True
            )
            
            self.service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id, name, modifiedTime'
            ).execute()
            
            logger.info(f"✅ Archivo actualizado en Drive: {file_name}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Error al actualizar archivo en Drive: {str(e)}")
            return False
    
    def upload_or_update(self, file_content: bytes, file_name: str) -> Dict[str, any]:
        """
        Sube un archivo o lo actualiza si ya existe
        
        Args:
            file_content: Contenido del archivo
            file_name: Nombre del archivo
            
        Returns:
            Diccionario con el resultado de la operación
        """
        # Buscar si el archivo ya existe
        existing_file = self.search_file(file_name)
        
        if existing_file:
            # Actualizar archivo existente
            success = self.update_file(existing_file['id'], file_content, file_name)
            return {
                'success': success,
                'action': 'updated',
                'file_id': existing_file['id'],
                'file_name': file_name
            }
        else:
            # Crear nuevo archivo
            file_id = self.upload_file(file_content, file_name)
            return {
                'success': bool(file_id),
                'action': 'created',
                'file_id': file_id,
                'file_name': file_name
            }
