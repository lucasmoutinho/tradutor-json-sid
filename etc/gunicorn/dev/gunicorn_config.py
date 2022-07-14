import json
import logging

bind = "0.0.0.0:8000"

worker_class = "sync"
workers = 17
# threads = 2  # not applicable for sync
timeout = 240
# keepalive = 60  # not applicable for sync

preload_app = True

# Logging configuration
with open('/tmp/gunicorn_logconfig.json', 'r') as f:
    log_cfg = json.load(f)
logconfig_dict = log_cfg
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s'


# Server hooks
def post_worker_init(worker):
    logger = logging.getLogger('gunicorn.error')
    logger.info(f'{worker} is ready to serve requests')
