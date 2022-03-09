import multiprocessing

bind = "unix:/var/lib/skyline/skyline.sock"
workers = (1 + multiprocessing.cpu_count()) // 2
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 3600
keepalive = 5
reuse_port = True
proc_name = "skyline"
log_level = "debug"
accesslog = "/var/log/kolla/skyline/access.log"
errorlog = "/var/log/kolla/skyline/error.log"
