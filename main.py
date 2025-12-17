"""
Script principal para la publicación automatizada de catálogos
Migración del flujo n8n a Python
"""
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, List, Tuple

import schedule

from config import SCHEDULE_TIME, SOURCE_PATH, validate_config
from utils.logger import logger
from utils.name_mapper import normalize_catalog_name
from services.file_service import FileService
from services.drive_service import DriveService
from services.ftp_service import FTPService
from services.mongo_service import MongoService
from services.notifications import NotificationManager, run_notification_sync


class CatalogPublisher:
    """Orquesta el proceso de publicación de catálogos"""

    def __init__(self):
        """Inicializa todos los servicios"""
        logger.info("=" * 80)
        logger.info("🚀 Iniciando CatalogPublisher")
        logger.info("=" * 80)

        # Validar configuración
        if not validate_config():
            logger.warning("⚠️  Configuración incompleta, algunas funcionalidades pueden no estar disponibles")

        # Inicializar servicios
        self.file_service = FileService()
        self.drive_service = DriveService()
        self.ftp_service = FTPService()
        self.mongo_service = MongoService()
        self.notifier = NotificationManager()

        logger.info("✅ Servicios inicializados")

    def process_catalog(self, catalog: Dict, execution_id: str) -> Dict:
        """
        Procesa un catálogo individual: copia local, sube a Drive y FTP

        Args:
            catalog: Información del catálogo
            execution_id: ID de ejecución

        Returns:
            Diccionario con el resultado del procesamiento
        """
        file_name = catalog['fileName']
        full_path = catalog['fullPath']

        logger.info(f"\n{'='*60}")
        logger.info(f"📄 Procesando: {file_name}")
        logger.info(f"{'='*60}")

        result = {
            'fileName': file_name,
            'local': False,
            'drive': False,
            'ftp': False,
            'errors': []
        }

        # 1. Normalizar nombre del archivo
        normalized_name = normalize_catalog_name(file_name)

        if "No se ha encontrado" in normalized_name or normalized_name == file_name:
            error_msg = f"No se encontró mapeo para el archivo: {file_name}"
            logger.error(f"❌ {error_msg}")
            result['errors'].append(error_msg)
            run_notification_sync(
                self.notifier.notify_critical_error(
                    "Normalización de nombre",
                    error_msg,
                    {"archivo": file_name}
                )
            )
            return result

        logger.info(f"📝 Nombre normalizado: {normalized_name}")

        # 2. Leer contenido del archivo
        file_content = self.file_service.read_file(full_path)
        if not file_content:
            error_msg = f"No se pudo leer el archivo: {full_path}"
            logger.error(f"❌ {error_msg}")
            result['errors'].append(error_msg)
            return result

        # 3. Copiar a carpeta local de destino
        logger.info("📋 Paso 1/3: Copiando a carpeta local...")
        if self.file_service.copy_to_destination(full_path, file_name):
            result['local'] = True
            self.mongo_service.insert_log(
                execution_id, file_name, "local", "success",
                {'source': full_path, 'action': 'copy'}
            )
        else:
            error_msg = f"Error al copiar archivo localmente"
            result['errors'].append(error_msg)
            self.mongo_service.insert_log(
                execution_id, file_name, "local", "error",
                {'error': error_msg}
            )
            run_notification_sync(
                self.notifier.notify_critical_error(
                    "Copia local",
                    error_msg,
                    {"archivo": file_name}
                )
            )

        # 4. Subir/actualizar en Google Drive
        logger.info("☁️  Paso 2/3: Subiendo a Google Drive...")
        drive_result = self.drive_service.upload_or_update(file_content, file_name)

        if drive_result['success']:
            result['drive'] = True
            self.mongo_service.insert_log(
                execution_id, file_name, "drive", "success",
                {'action': drive_result['action'], 'file_id': drive_result.get('file_id')}
            )
        else:
            error_msg = f"Error al subir a Drive"
            result['errors'].append(error_msg)
            self.mongo_service.insert_log(
                execution_id, file_name, "drive", "error",
                {'error': error_msg}
            )
            run_notification_sync(
                self.notifier.notify_critical_error(
                    f"Google Drive ({drive_result['action']})",
                    error_msg,
                    {"archivo": file_name}
                )
            )

        # 5. Subir a FTP
        logger.info("🌐 Paso 3/3: Subiendo a FTP...")
        if self.ftp_service.upload_file(file_content, normalized_name):
            result['ftp'] = True
            self.mongo_service.insert_log(
                execution_id, file_name, "ftp", "success",
                {'normalized_name': normalized_name}
            )
        else:
            error_msg = f"Error al subir a FTP"
            result['errors'].append(error_msg)
            self.mongo_service.insert_log(
                execution_id, file_name, "ftp", "error",
                {'error': error_msg, 'normalized_name': normalized_name}
            )
            run_notification_sync(
                self.notifier.notify_critical_error(
                    "FTP",
                    error_msg,
                    {"archivo": file_name, "nombre_normalizado": normalized_name}
                )
            )

        # Resumen del procesamiento
        if result['local'] and result['drive'] and result['ftp']:
            logger.info(f"✅ Archivo procesado exitosamente: {file_name}")
        else:
            logger.warning(f"⚠️  Archivo procesado parcialmente: {file_name}")
            logger.warning(f"   Local: {result['local']}, Drive: {result['drive']}, FTP: {result['ftp']}")

        return result

    def cleanup_source_files(self, execution_id: str) -> Tuple[List[str], List[str]]:
        """
        Limpia archivos que se procesaron exitosamente en todas las etapas

        Args:
            execution_id: ID de ejecución

        Returns:
            Tupla con (archivos_eliminados, archivos_con_error)
        """
        logger.info("\n🗑️  Iniciando limpieza de archivos...")

        # Obtener archivos que pueden ser eliminados
        files_to_check = self.mongo_service.get_files_to_delete(execution_id)

        deleted_files = []
        error_files = []

        for file_info in files_to_check:
            file_name = file_info['fileName']
            can_delete = file_info['canDelete']

            if can_delete:
                # Construir ruta completa
                file_path = f"{SOURCE_PATH}\\{file_name}"

                # Intentar eliminar
                if self.file_service.delete_file(file_path):
                    deleted_files.append(file_name)
                    # Limpiar logs de MongoDB
                    self.mongo_service.delete_logs(execution_id, file_name)
                else:
                    error_files.append(file_name)
                    run_notification_sync(
                        self.notifier.notify_warning(
                            "Eliminación de archivo",
                            f"No se pudo eliminar el archivo del origen",
                            {"archivo": file_name}
                        )
                    )
            else:
                logger.info(f"⏭️  Archivo no eliminado (proceso incompleto): {file_name}")
                error_files.append(file_name)

        # Limpiar documentos de archivos que no se pudieron procesar completamente
        non_deletable = [f for f in files_to_check if not f['canDelete']]
        if non_deletable:
            for file_info in non_deletable:
                self.mongo_service.delete_logs(execution_id, file_info['fileName'])

        logger.info(f"✅ Limpieza completada: {len(deleted_files)} eliminados, {len(error_files)} con errores")

        return deleted_files, error_files

    def run(self):
        """Ejecuta el flujo completo de publicación"""
        logger.info("\n" + "="*80)
        logger.info("🔄 INICIANDO EJECUCIÓN DEL FLUJO")
        logger.info("="*80)

        # Generar ID de ejecución único
        execution_id = f"exec_{uuid.uuid4().hex[:12]}_{int(time.time())}"
        logger.info(f"📋 Execution ID: {execution_id}")

        try:
            # 1. Listar catálogos disponibles
            logger.info("\n📂 Buscando catálogos...")
            catalogs = self.file_service.list_catalogs()

            if not catalogs:
                logger.warning("⚠️  No se encontraron catálogos para procesar")
                return

            logger.info(f"✅ Encontrados {len(catalogs)} catálogos")

            # Notificar inicio
            run_notification_sync(
                self.notifier.notify_info(
                    "Iniciando publicación de catálogos",
                    f"Catálogos detectados: {len(catalogs)}"
                )
            )

            # 2. Procesar cada catálogo
            results = []
            for catalog in catalogs:
                result = self.process_catalog(catalog, execution_id)
                results.append(result)

            # 3. Limpieza de archivos procesados exitosamente
            deleted_files, error_files = self.cleanup_source_files(execution_id)

            # 4. Enviar resumen final
            logger.info("\n📤 Enviando resumen final...")

            # Preparar mensaje de resumen
            if deleted_files:
                success_msg = f"✅ Se publicaron {len(deleted_files)} catálogos exitosamente"
                run_notification_sync(
                    self.notifier.notify_success(
                        "Publicación completada",
                        success_msg
                    )
                )

            if error_files:
                error_msg = f"⚠️ {len(error_files)} catálogos con errores: {', '.join(error_files)}"
                run_notification_sync(
                    self.notifier.notify_warning(
                        "Catálogos con errores",
                        error_msg,
                        {"archivos_con_error": error_files}
                    )
                )

            # 5. Resumen final
            logger.info("\n" + "="*80)
            logger.info("📊 RESUMEN DE EJECUCIÓN")
            logger.info("="*80)
            logger.info(f"Total catálogos procesados: {len(results)}")
            logger.info(f"Publicados exitosamente: {len(deleted_files)}")
            logger.info(f"Con errores: {len(error_files)}")
            logger.info("="*80 + "\n")

        except Exception as e:
            error_msg = f"Error crítico en el flujo: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            run_notification_sync(
                self.notifier.notify_critical_error(
                    "Flujo principal",
                    error_msg,
                    {"traceback": str(e)}
                )
            )

    def run_scheduled(self):
        """Ejecuta el flujo en modo programado"""
        logger.info(f"⏰ Programando ejecución cada {SCHEDULE_TIME} minutos")
        logger.info("   Horario: Cada 15 minutos, de 8:00 a 16:00, Lunes a Viernes")
        logger.info("   (Presiona Ctrl+C para detener)\n")

        # Programar ejecución cada X minutos
        schedule.every(SCHEDULE_TIME).minutes.do(self.run)

        # Loop principal
        try:
            # Ejecutar inmediatamente al iniciar
            self.run()

            # Continuar con el schedule
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto

        except KeyboardInterrupt:
            logger.info("\n\n⏹️  Deteniendo el programador...")
            logger.info("👋 Hasta pronto!")


def main():
    """Función principal"""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║       📚 CATALOG PUBLICATION SYSTEM 📚               ║
    ║                                                       ║
    ║       Publicación automática de catálogos            ║
    ║       Local → Google Drive → FTP                     ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    # Crear instancia del publicador
    publisher = CatalogPublisher()

    # Determinar modo de ejecución
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Ejecución única
        logger.info("🔧 Modo: Ejecución única")
        publisher.run()
    else:
        # Ejecución programada
        logger.info("🔧 Modo: Ejecución programada")
        publisher.run_scheduled()


if __name__ == "__main__":
    main()
