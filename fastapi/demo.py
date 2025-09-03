import asyncio

from gunicorn.app.base import BaseApplication

from ooo.api import app
from ooo.configs import ENV_CONFIG


class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


# Gunicorn post_fork hook
def post_fork(server, worker):
    pass


if __name__ == "__main__":
    options = {
        "bind": f"{ENV_CONFIG.host}:{ENV_CONFIG.port}",
        "workers": ENV_CONFIG.workers,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "limit_concurrency": 100,
        "timeout": 600,
        "graceful_timeout": 60,
        "max_requests": 2000,
        "max_requests_jitter": 200,
        "keepalive": 60,  # AWS ALB and Nginx default to 60 seconds
        "post_fork": post_fork,
        "loglevel": "error",
    }
    StandaloneApplication(app, options).run()
