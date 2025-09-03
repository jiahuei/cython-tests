import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from gunicorn.app.base import BaseApplication
from loguru import logger
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

from ooo.configs import ENV_CONFIG
from ooo.db import migrate_db
from ooo.routers import counters

asyncio.run(migrate_db())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info(f"Using configuration: {ENV_CONFIG}")
    yield
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Counter API",
    logger=logger,
    default_response_class=ORJSONResponse,  # Should be faster
    openapi_url="/api/public/openapi.json",
    docs_url="/api/public/docs",
    redoc_url="/api/public/redoc",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    lifespan=lifespan,
)

# Programmatic Instrumentation
FastAPIInstrumentor.instrument_app(app)
RedisInstrumentor().instrument()
HTTPXClientInstrumentor().instrument()

# Mount
app.include_router(
    counters.router,
    prefix="/api",
    tags=["Counters"],
)
# Permissive CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"])
async def health() -> ORJSONResponse:
    """Health check."""
    return ORJSONResponse(status_code=200)


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
