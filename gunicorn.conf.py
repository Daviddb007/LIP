import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5

# Restart workers after this many requests (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')

# Process naming
proc_name = 'construyamos_colombia'

# Server mechanics
preload_app = True
daemon = False
pidfile = None
umask = 0o022
tmp_upload_dir = None

# SSL (uncomment if not using reverse proxy)
# certfile = '/path/to/cert.pem'
# keyfile = '/path/to/key.pem'

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190
