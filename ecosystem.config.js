module.exports = {
  apps: [
    {
      name: 'catalog-publication',
      script: 'main.py',
      // Usar pythonw.exe (sin ventana visible) del entorno virtual (.venv)
      interpreter: '.venv/Scripts/pythonw.exe',
      interpreter_args: '',
      // Directorio actual del proyecto
      cwd: 'C:/Users/junior.marketing/Documents/catalog-publication',
      instances: 1,
      autorestart: false, // false para cron jobs
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PYTHONUNBUFFERED: '1',
        PYTHONPATH: 'C:/Users/junior.marketing/Documents/catalog-publication'
      },
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_file: './logs/pm2-combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      // Reiniciar en caso de fallo
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
      // Configuración de cron (cada 15 minutos de 8am a 4pm, lunes a viernes)
      // Si quieres que corra continuamente, comenta la línea cron_restart
      cron_restart: '*/15 8-16 * * 1-5',
      // Variables de entorno (cargadas desde .env automáticamente)
      env_file: '.env'
    }
  ]
};
