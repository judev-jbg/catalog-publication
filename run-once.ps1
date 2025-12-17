# ============================================
# Script de Ejecución Única - Catalog Publication
# ============================================
# Este script:
# 1. Crea el entorno virtual si no existe
# 2. Instala/actualiza las dependencias
# 3. Ejecuta main.py una sola vez
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Catalog Publication - Ejecución Única" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Obtener la ruta del directorio del script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# ============================================
# 1. Verificar/Crear Entorno Virtual
# ============================================
Write-Host "[1/4] Verificando entorno virtual..." -ForegroundColor Yellow

if (-Not (Test-Path ".venv")) {
    Write-Host "  Entorno virtual no encontrado. Creando..." -ForegroundColor Cyan
    python -m venv .venv

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: No se pudo crear el entorno virtual" -ForegroundColor Red
        Write-Host "Verifica que Python esté instalado correctamente" -ForegroundColor Red
        Write-Host ""
        pause
        exit 1
    }

    Write-Host "  Entorno virtual creado exitosamente" -ForegroundColor Green
} else {
    Write-Host "  Entorno virtual encontrado" -ForegroundColor Green
}

Write-Host ""

# ============================================
# 2. Actualizar pip
# ============================================
Write-Host "[2/4] Actualizando pip..." -ForegroundColor Yellow
& .venv\Scripts\python.exe -m pip install --upgrade pip --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "  pip actualizado" -ForegroundColor Green
} else {
    Write-Host "  Advertencia: No se pudo actualizar pip (continuando...)" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# 3. Instalar/Actualizar Dependencias
# ============================================
Write-Host "[3/4] Instalando dependencias..." -ForegroundColor Yellow

if (-Not (Test-Path "requirements.txt")) {
    Write-Host ""
    Write-Host "ERROR: No se encontró requirements.txt" -ForegroundColor Red
    Write-Host ""
    pause
    exit 1
}

& .venv\Scripts\pip.exe install -r requirements.txt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Dependencias instaladas correctamente" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "ERROR: No se pudieron instalar las dependencias" -ForegroundColor Red
    Write-Host "Revisa el archivo requirements.txt" -ForegroundColor Red
    Write-Host ""
    pause
    exit 1
}

Write-Host ""

# ============================================
# 4. Ejecutar main.py
# ============================================
Write-Host "[4/4] Ejecutando main.py..." -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Iniciando Proceso Principal" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que main.py existe
if (-Not (Test-Path "main.py")) {
    Write-Host ""
    Write-Host "ERROR: No se encontró main.py" -ForegroundColor Red
    Write-Host ""
    pause
    exit 1
}

# Ejecutar main.py
& .venv\Scripts\python.exe main.py

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "  Ejecución completada exitosamente" -ForegroundColor Green
} else {
    Write-Host "  Ejecución completada con errores (código: $exitCode)" -ForegroundColor Red
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Preguntar si desea ver los logs
$viewLogs = Read-Host "¿Deseas ver los últimos logs? (s/n)"

if ($viewLogs -eq "s" -or $viewLogs -eq "S") {
    if (Test-Path "logs") {
        Write-Host ""
        Write-Host "Logs disponibles:" -ForegroundColor Cyan
        Get-ChildItem -Path "logs" -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object {
            Write-Host "  - $($_.Name) ($(Get-Date $_.LastWriteTime -Format 'yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray
        }
        Write-Host ""

        $logFile = Read-Host "Ingresa el nombre del archivo log (o presiona Enter para omitir)"

        if ($logFile -and (Test-Path "logs\$logFile")) {
            Write-Host ""
            Write-Host "Últimas 30 líneas de $logFile" -ForegroundColor Cyan
            Write-Host "============================================" -ForegroundColor Gray
            Get-Content "logs\$logFile" -Tail 30
            Write-Host "============================================" -ForegroundColor Gray
        }
    } else {
        Write-Host ""
        Write-Host "No se encontró la carpeta de logs" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Presiona cualquier tecla para salir..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Salir con el código de salida del script principal
exit $exitCode
