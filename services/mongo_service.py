"""
Servicio para logging de operaciones en MongoDB
Registra cada operación de publicación de catálogos
"""
from typing import Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from utils.logger import logger


class MongoService:
    """Maneja el logging de operaciones en MongoDB"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Establece conexión con MongoDB"""
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Verificar conexión
            self.client.admin.command('ping')
            
            self.db = self.client[MONGO_DB]
            self.collection = self.db[MONGO_COLLECTION]
            
            logger.info(f"✅ Conectado a MongoDB: {MONGO_DB}.{MONGO_COLLECTION}")
            
        except ConnectionFailure as e:
            logger.error(f"❌ No se pudo conectar a MongoDB: {str(e)}")
            self.client = None
        except Exception as e:
            logger.error(f"❌ Error al conectar con MongoDB: {str(e)}")
            self.client = None
    
    def insert_log(self, execution_id: str, file_name: str, operation: str, 
                   status: str, details: Dict = None) -> bool:
        """
        Inserta un registro de operación en MongoDB
        
        Args:
            execution_id: ID único de ejecución
            file_name: Nombre del archivo
            operation: Tipo de operación (local, drive, ftp)
            status: Estado (success, error)
            details: Detalles adicionales
            
        Returns:
            True si se insertó correctamente, False en caso contrario
        """
        if not self.client:
            logger.warning("MongoDB no está conectado, no se puede insertar log")
            return False
        
        try:
            document = {
                'executionId': execution_id,
                'fileName': file_name,
                'operation': operation,
                'status': status,
                'timestamp': datetime.now(),
                'details': details or {}
            }
            
            result = self.collection.insert_one(document)
            logger.debug(f"Log insertado: {operation} - {file_name} - {status}")
            return bool(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Error al insertar log en MongoDB: {str(e)}")
            return False
    
    def get_logs_by_execution(self, execution_id: str) -> List[Dict]:
        """
        Obtiene todos los logs de una ejecución
        
        Args:
            execution_id: ID de ejecución
            
        Returns:
            Lista de documentos encontrados
        """
        if not self.client:
            logger.warning("MongoDB no está conectado")
            return []
        
        try:
            logs = list(self.collection.find({'executionId': execution_id}))
            logger.debug(f"Recuperados {len(logs)} logs para ejecución {execution_id}")
            return logs
            
        except Exception as e:
            logger.error(f"❌ Error al obtener logs: {str(e)}")
            return []
    
    def delete_logs(self, execution_id: str, file_name: Optional[str] = None) -> int:
        """
        Elimina logs de una ejecución
        
        Args:
            execution_id: ID de ejecución
            file_name: Nombre de archivo específico (opcional)
            
        Returns:
            Número de documentos eliminados
        """
        if not self.client:
            logger.warning("MongoDB no está conectado")
            return 0
        
        try:
            query = {'executionId': execution_id}
            if file_name:
                query['fileName'] = file_name
            
            result = self.collection.delete_many(query)
            deleted = result.deleted_count
            
            logger.debug(f"Eliminados {deleted} logs de MongoDB")
            return deleted
            
        except Exception as e:
            logger.error(f"❌ Error al eliminar logs: {str(e)}")
            return 0
    
    def get_files_to_delete(self, execution_id: str) -> List[Dict]:
        """
        Obtiene los archivos que pueden ser eliminados
        (aquellos que completaron exitosamente todas las operaciones)
        
        Args:
            execution_id: ID de ejecución
            
        Returns:
            Lista de archivos que pueden ser eliminados
        """
        logs = self.get_logs_by_execution(execution_id)
        
        if not logs:
            return []
        
        # Agrupar por archivo
        file_status = {}
        for log in logs:
            file_name = log.get('fileName')
            if not file_name:
                continue
            
            if file_name not in file_status:
                file_status[file_name] = {
                    'fileName': file_name,
                    'local': False,
                    'drive': False,
                    'ftp': False
                }
            
            if log.get('status') == 'success':
                operation = log.get('operation')
                if operation in ['local', 'drive', 'ftp']:
                    file_status[file_name][operation] = True
        
        # Retornar archivos que completaron todas las operaciones
        files_to_delete = [
            {
                'fileName': file_name,
                'canDelete': data['local'] and data['drive'] and data['ftp']
            }
            for file_name, data in file_status.items()
        ]
        
        deletable = [f for f in files_to_delete if f['canDelete']]
        logger.info(f"📋 {len(deletable)} archivos pueden ser eliminados de {len(files_to_delete)} procesados")
        
        return files_to_delete
    
    def close(self):
        """Cierra la conexión con MongoDB"""
        if self.client:
            self.client.close()
            logger.info("🔌 Conexión MongoDB cerrada")
