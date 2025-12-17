"""
Configuración centralizada del proyecto
Carga variables de entorno y valida credenciales
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================
# PATHS
# ============================================
BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ============================================
# RUTAS UNC
# ============================================
SOURCE_PATH = os.getenv(
    "SOURCE_PATH", r"\\dataserver\Comunes\MARKETING\01.CATALOGOS SELK\PUBLICACION_CATALOGOS")
DEST_PATH = os.getenv(
    "DEST_PATH", r"\\dataserver\Comunes\MARKETING\01.CATALOGOS SELK")

# ============================================
# GOOGLE DRIVE (Service Account - Sin intervención del usuario)
# ============================================
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE", "credentials-service.json")
GOOGLE_DRIVE_FOLDER_ID = os.getenv(
    "GOOGLE_DRIVE_FOLDER_ID", "10q24v4-L8PQNL1nXqIGybAyWr4WhGJJ-")

# ============================================
# FTP
# ============================================
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", 21))
FTP_USER = os.getenv("FTP_USER")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")
FTP_UPLOAD_PATH = os.getenv("FTP_UPLOAD_PATH", "/selk/upload/productos")

# ============================================
# MONGODB
# ============================================
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "catalog_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "catalog_operations")

# ============================================
# EMAIL NOTIFICATIONS (SMTP)
# ============================================
EMAIL_NOTIFICATIONS_ENABLED = os.getenv(
    "EMAIL_NOTIFICATIONS_ENABLED", "true").lower() == "true"
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.office365.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
NOTIFICATION_EMAILS = os.getenv(
    "NOTIFICATION_EMAILS", "junior.marketing@selk.es")


# ============================================
# SLACK NOTIFICATIONS
# ============================================
SLACK_NOTIFICATIONS_ENABLED = os.getenv(
    "SLACK_NOTIFICATIONS_ENABLED", "true").lower() == "true"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#catalog-publication")
SLACK_USERNAME = os.getenv("SLACK_USERNAME", "Catalog-Bot")

# ============================================
# SCHEDULE
# ============================================
SCHEDULE_TIME = int(os.getenv("SCHEDULE_TIME", 15))

# ============================================
# LOGGING
# ============================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================
# MAPEO DE NOMBRES DE CATALOGOS
# ============================================
CATALOG_NAME_MAPPING = {
    "ANCLAJES Y FIJACIONES.pdf": "ANCLAJES_FIJACIONES.pdf",
    "CINTAS TECNICAS.pdf": "CINTAS_TECNICAS.pdf",
    "CLIMATIZACION.pdf": "CLIMATIZACION.pdf",
    "CORTE Y PERFORACION.pdf": "CORTE_PERFORACION.pdf",
    "CORTE, LIJADO Y PULIDO.pdf": "CORTE_LIJADO_PULIDO.pdf",
    "EMBALAJES.pdf": "EMBALAJES.pdf",
    "EQUIPAMIENTO DE CONSTRUCCION.pdf": "EQUIPAMIENTO_CONSTRUCCION.pdf",
    "EQUIPAMIENTO DE TALLER.pdf": "EQUIPAMIENTO_TALLER.pdf",
    "GRIFERIA.pdf": "GRIFERIA.pdf",
    "GUIAS, SOPORTES, ABRAZADERAS.pdf": "GUIAS_SOPORTES_ABRAZDERAS.pdf",
    "HERRAMIENTA ELECTRICA.pdf": "HERRAMIENTA_ELECTRICA.pdf",
    "HERRAMIENTA MANUAL.pdf": "HERRAMIENTA_MANUAL.pdf",
    "HERRAMIENTA MEDICION.pdf": "HERRAMIENTA_MEDICION.pdf",
    "HERRAMIENTA Y ACCESORIOS NEUMATICA.pdf": "HERRAMIENTA_ACCESORIOS_NEUMATICA.pdf",
    "ILUMINACION.pdf": "ILUMINACION.pdf",
    "LIMPIEZA INDUSTRIAL.pdf": "LIMPIEZA_INDUSTRIAL.pdf",
    "PEQUEÑO MATERIAL ELECTRICO.pdf": "PEQUENIO_MATERIAL_ELECTRICO.pdf",
    "PEQUEÑO MATERIAL SANITARIO.pdf": "PEQUENIO_MATERIAL_SANITARIO.pdf",
    "QUIMICOS.pdf": "QUIMICOS.pdf",
    "REMACHES.pdf": "REMACHES.pdf",
    "REPARACION DE ROSCAS.pdf": "REPARACION_ROSCAS.pdf",
    "ROPA LABORAL.pdf": "ROPA_LABORAL.pdf",
    "SEGURIDAD LABORAL.pdf": "SEGURIDAD_LABORAL.pdf",
    "SELLADO Y PEGADO.pdf": "SELLADO_PEGADO.pdf",
    "SOLDADURA.pdf": "SOLDADURA.pdf",
    "TORNILLERIA.pdf": "TORNILLERIA.pdf",
    "FIJACION SOLAR.pdf": "FIJACION_SOLAR.pdf",
    "PEQUEÑO MATERIAL CARPINTERIA.pdf": "PEQUENIO_MATERIAL_CARPINTERIA.pdf",
}


def validate_config():
    """Valida que las configuraciones mínimas estén presentes"""
    errors = []

    if not FTP_HOST:
        errors.append("FTP_HOST no está configurado")
    if not FTP_USER:
        errors.append("FTP_USER no está configurado")
    if not FTP_PASSWORD:
        errors.append("FTP_PASSWORD no está configurado")

    if errors:
        print("⚠️  Advertencias de configuración:")
        for error in errors:
            print(f"   - {error}")
        print("\nEl sistema funcionará con funcionalidades limitadas.")

    return len(errors) == 0
