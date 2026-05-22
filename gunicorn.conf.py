import multiprocessing
import os

# Bind to PORT env var (Render sets this automatically)
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Use threads instead of workers for I/O-bound Flask app
# This prevents the "no tunnel here" issue caused by single-threaded blocking
workers = 1
threads = 4
worker_class = "gthread"

# Timeouts - important for mobile connections with slow uploads
timeout = 120
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = "-"    # stdout
errorlog = "-"     # stderr
loglevel = "info"

# Prevent memory leaks in long-running workers
max_requests = 1000
max_requests_jitter = 100

# Security
forwarded_allow_ips = "*"  # Render uses reverse proxy
