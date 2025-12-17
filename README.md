# 📚 Catalog Publication System

Sistema automatizado para la publicación de catálogos en múltiples plataformas (Local, Google Drive y FTP).

## 🎯 Funcionalidades

- ✅ **Detección automática** de catálogos PDF en carpeta origen
- ✅ **Normalización de nombres** según mapeo predefinido
- ✅ **Copia local** a carpeta de destino
- ✅ **Publicación en Google Drive** con Service Account (sin intervención del usuario)
- ✅ **Subida a servidor FTP**
- ✅ **Logging completo** en MongoDB
- ✅ **Notificaciones unificadas** por Email (SMTP) y Slack (Webhook)
- ✅ **Limpieza automática** de archivos procesados exitosamente
- ✅ **Ejecución programada** con PM2 o manual
- ✅ **Entorno virtual aislado** para dependencias

## 📋 Requisitos

- Python 3.11+
- Node.js y PM2 (para ejecución en producción)
- MongoDB (para logging)
- Acceso a rutas UNC (red local Windows)
- Google Service Account (Drive API)
- Credenciales de FTP
- Credenciales de Email SMTP
- Webhook de Slack

## 🚀 Inicio Rápido

### Opción 1: Script TODO-EN-UNO (Recomendado)

```powershell
# Ejecuta esto una vez para instalar todo y ejecutar
.\run-once.ps1
```

Este script hace TODO automáticamente:

- ✅ Crea el entorno virtual
- ✅ Instala dependencias
- ✅ Ejecuta el proyecto
- ✅ Muestra logs al finalizar

### Opción 2: Instalación Manual

```bash
# 1. Instalar entorno virtual y dependencias
install.bat

# 2. Probar conexiones
test_connection.bat

# 3. Ejecutar manualmente
run.bat
```

### Opción 3: Producción con PM2

```bash
# 1. Instalar dependencias
install.bat

# 2. Iniciar con PM2 (ejecución programada)
pm2 start ecosystem.config.js
pm2 save

# 3. Ver logs
pm2 logs catalog-publication
```

## 🛠️ Instalación Detallada

### 1. Configurar Credenciales

#### a) Compartir Carpeta de Google Drive con Service Account

⚠️ **IMPORTANTE:** Comparte la carpeta de Google Drive con el Service Account:

```
Email: drive-automation@drive-sync-automation.iam.gserviceaccount.com
Permisos: Editor
```

#### b) Archivo .env

Edita el archivo `.env` con tus credenciales:

```ini
# Rutas UNC (red local)
SOURCE_PATH=\\dataserver\Comunes\MARKETING\01.CATALOGOS SELK\PUBLICACION_CATALOGOS
DEST_PATH=\\dataserver\Comunes\MARKETING\01.CATALOGOS SELK

# Google Drive (Service Account - Sin intervención del usuario)
GOOGLE_SERVICE_ACCOUNT_FILE=credentials-service.json
GOOGLE_DRIVE_FOLDER_ID=10q24v4-L8PQNL1nXqIGybAyWr4WhGJJ-

# FTP
FTP_HOST=tu_servidor_ftp
FTP_USER=tu_usuario
FTP_PASSWORD=tu_password

# MongoDB
MONGO_URI=mongodb://localhost:27017/

# Email (SMTP)
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SENDER_EMAIL=noreply@toolstock.info
SENDER_PASSWORD=tu_password
NOTIFICATION_EMAILS=junior.marketing@selk.es

# Slack (Webhook)
SLACK_NOTIFICATIONS_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T09GN3RDCM8/...
SLACK_CHANNEL=#catalog-publication
```

#### c) Credenciales de Google Service Account

El archivo `credentials-service.json` ya está incluido del proyecto `Articulos_Selk`.

**No necesitas autenticación manual** - Todo funciona automáticamente.

### 2. Verificar Instalación

```bash
# Probar conexiones
test_connection.bat
```

Deberías ver:

```
✓ OK - Google Drive conectado correctamente
✓ Email: HABILITADO, Slack: HABILITADO
```

## 📋 Scripts Disponibles

| Script         | Descripción                       |
| -------------- | --------------------------------- |
| `run-once.ps1` | ⭐ TODO EN UNO: Instala y ejecuta |

## 🚀 Uso

### Ejecución Manual (Una vez)

```bash
# Opción 1: PowerShell (recomendado)
.\run-once.ps1

# Opción 2: Batch
run.bat
```

### Ejecución Programada con PM2

```bash
# Iniciar
pm2 start ecosystem.config.js

# Ver estado
pm2 status

# Ver logs en tiempo real
pm2 logs catalog-publication

# Detener
pm2 stop catalog-publication

# Reiniciar
pm2 restart catalog-publication
```

**Programación actual:**

- ⏰ Cada 15 minutos
- 🕐 De 8:00 AM a 4:00 PM
- 📆 Lunes a Viernes

Para cambiar, edita `ecosystem.config.js` línea 32.

### Ejecución en Modo Silencioso

PM2 está configurado para usar `pythonw.exe` (sin ventana visible):

- ✅ No aparecen ventanas emergentes
- ✅ No interrumpe tu trabajo
- ✅ Logs disponibles con `pm2 logs`

## 📁 Estructura del Proyecto

```
catalog-publication/
├── .env                          # Credenciales
├── .venv/                        # Entorno virtual Python
├── credentials-service.json      # Service Account
├── requirements.txt              # Dependencias Python
├── ecosystem.config.js           # Configuración PM2
├── config.py                     # Configuración centralizada
├── main.py                       # Script principal
│
├── services/                     # Servicios de integración
│   ├── __init__.py
│   ├── file_service.py          # Manejo de archivos UNC
│   ├── drive_service.py         # Google Drive (Service Account)
│   ├── ftp_service.py           # FTP
│   ├── notifications.py         # Email (SMTP) y Slack (Webhook)
│   └── mongo_service.py         # MongoDB logging
│
├── utils/                        # Utilidades
│   ├── __init__.py
│   ├── logger.py                # Logging centralizado
│   └── name_mapper.py           # Normalización de nombres
│
├── logs/                         # Logs del sistema (auto-generado)


```

## 🔄 Flujo de Trabajo

1. **Detección:** Lista todos los PDFs en la carpeta origen
2. **Normalización:** Convierte nombres a formato estándar
3. **Validación:** Verifica que el archivo tenga un mapeo válido
4. **Procesamiento por archivo:**
   - ✅ Copia a carpeta local de destino
   - ☁️ Sube/actualiza en Google Drive (Service Account)
   - 🌐 Sube a servidor FTP (con nombre normalizado)
   - 💾 Registra cada operación en MongoDB
5. **Limpieza:** Elimina archivos origen procesados exitosamente
6. **Notificaciones:**
   - 📧 Email con detalles de errores (SMTP)
   - 💬 Slack con resumen de ejecución (Webhook)
7. **Logging:** Registra toda la actividad en archivos y MongoDB

## 📊 Logs y Monitoreo

### Logs de PM2

```bash
# Ver logs en tiempo real
pm2 logs catalog-publication

# Ver últimos logs
pm2 logs catalog-publication --lines 100

# Ver solo errores
pm2 logs catalog-publication --err
```

Ubicación: `logs/pm2-*.log`

### Logs de la Aplicación

Los logs se guardan en `logs/catalog_YYYYMMDD.log`:

```
2025-12-17 10:30:15 - INFO - ✅ Encontrados 28 catálogos
2025-12-17 10:30:16 - INFO - 📄 Procesando: ANCLAJES Y FIJACIONES.pdf
2025-12-17 10:30:17 - INFO - ✅ Archivo procesado exitosamente
```

### Notificaciones

**Email:**

- Errores críticos
- Fallos en operaciones
- HTML formateado con detalles

**Slack:**

- Inicio de proceso
- Resumen de ejecución
- Lista de archivos exitosos/con errores

## 🔧 Configuración Avanzada

### Cambiar Programación de PM2

Edita `ecosystem.config.js`:

```javascript
// Cada 30 minutos
cron_restart: "*/30 * * * *";

// Cada hora
cron_restart: "0 * * * *";

// A las 9am, 12pm, 3pm y 6pm
cron_restart: "0 9,12,15,18 * * *";
```

### Mapeo de Nombres

Edita `config.py` para añadir/modificar nombres:

```python
CATALOG_NAME_MAPPING = {
    "NOMBRE ORIGINAL.pdf": "NOMBRE_NORMALIZADO.pdf",
}
```

### Nivel de Logging

Cambia `LOG_LEVEL` en `.env`:

```ini
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## ⚠️ Solución de Problemas

### Error: "No module named 'google'"

```bash
install.bat
```

### Error: "Permission denied" en Google Drive

Comparte la carpeta con el Service Account (ver sección de instalación).

### Error: "Cannot import MS_CLIENT_ID"

Los archivos antiguos ya fueron eliminados. Si persiste:

```bash
pm2 delete catalog-publication
pm2 start ecosystem.config.js
```

### PM2 muestra ventana emergente

Ya está configurado con `pythonw.exe`. Si persiste:

```bash
pm2 delete catalog-publication
pm2 start ecosystem.config.js
pm2 save
```

## 🎯 Ventajas del Sistema

✅ **Sin intervención del usuario** - Service Account de Google
✅ **Sin renovación de tokens** - Autenticación permanente
✅ **Entorno aislado** - Virtual environment (.venv)
✅ **Notificaciones unificadas** - Email + Slack
✅ **Ejecución silenciosa** - pythonw.exe sin ventanas
✅ **Fácil mantenimiento** - Scripts automatizados
✅ **Compatible con PM2** - Producción lista

## 🤝 Contribuir

Para añadir funcionalidades:

1. Activa el entorno virtual: `activate.bat`
2. Crea nuevos servicios en `services/`
3. Actualiza `config.py` y `.env`
4. Actualiza este README
5. Prueba con `run.bat`

## 📄 Licencia

Uso interno de la empresa.

## 👤 Autor

**judev**

## 📞 Soporte

Para problemas o dudas:

1. Revisa los logs: `pm2 logs catalog-publication`
2. Ejecuta test de conexiones: `test_connection.bat`
3. Consulta la documentación en la carpeta del proyecto

---

**Última actualización:** 17/12/2025
**Versión:** 2.0 - Automatización completa con Service Account y entorno virtual
