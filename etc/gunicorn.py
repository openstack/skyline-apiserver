bind = ['0.0.0.0:28000']
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 3600
keepalive = 5
reuse_port = True
proc_name = "skyline-apiserver"
log_level = "debug"
