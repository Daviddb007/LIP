"""Configuración de Gunicorn para producción.

Referencia: https://docs.gunicorn.org/en/stable/settings.html
"""
import multiprocessing
import os


# Puerto de escucha
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Workers
cpu_count = multiprocessing.cpu_count()
workers = cpu_count * 2 + 1
worker_class = "sync"
worker_connections = 1000

# Timeouts
timeout = 120
graceful_timeout = 30
keepalive = 5

# Reinicio de workers (previene memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")

# Preload de la app (comparte memoria entre workers)
preload_app = True

# Seguridad
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Naming
proc_name = "construyamos_v3"
