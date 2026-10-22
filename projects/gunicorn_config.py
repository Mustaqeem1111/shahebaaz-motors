"""
Gunicorn Configuration for Shahebaz Motors
==========================================
Use this for production deployment on Linux servers
(PythonAnywhere, Render, DigitalOcean, etc.)

Run with:
    gunicorn -c gunicorn_config.py app:app
"""

import multiprocessing
import os

# =========================================================
# SERVER SOCKET
# =========================================================

bind = "0.0.0.0:5000"

# =========================================================
# WORKERS
# =========================================================
# Formula: (2 × CPU cores) + 1
# For 2 CPU cores: 5 workers
# For 4 CPU cores: 9 workers
# For 1 CPU core: 3 workers

workers = (multiprocessing.cpu_count() * 2) + 1

# Worker class: sync (simple) or gevent (async)
# sync is fine for most cases
worker_class = "sync"

# Restart workers after this many requests (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 100

# =========================================================
# TIMEOUTS
# =========================================================

# Worker timeout (seconds)
timeout = 120

# Keep-alive connections
keepalive = 5

# Graceful restart timeout
graceful_timeout = 30

# =========================================================
# LOGGING
# =========================================================

accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# =========================================================
# PROCESS NAMING
# =========================================================

proc_name = "shahebaz_motors"

# =========================================================
# SECURITY
# =========================================================

# Limit request size (adjust if needed)
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# =========================================================
# PERFORMANCE
# =========================================================

# Preload app (saves memory, faster worker startup)
preload_app = True

# =========================================================
# DIRECTORIES
# =========================================================

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)