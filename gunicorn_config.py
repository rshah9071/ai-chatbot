# Gunicorn configuration file
# Binding address and port
bind = "0.0.0.0:5000"
# Number of worker processes
workers = 2
# Logging
accesslog = "-"  # Log to stdout (-), or provide a file path like "logs/access.log"
errorlog = "-"   # Log to stderr (-), or provide a file path like "logs/error.log"
# Timeout (important for potentially long AI responses)
timeout = 120