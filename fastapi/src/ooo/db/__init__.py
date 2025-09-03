from contextlib import asynccontextmanager, contextmanager
from functools import lru_cache
from typing import AsyncGenerator, Callable, Generator

from async_lru import alru_cache
from loguru import logger
from sqlalchemy import Engine, NullPool
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import Session, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from ooo.configs import ENV_CONFIG
from ooo.db.models import OooSQLModel


def _create_db_engine(
    db_url: str,
    *,
    engine_create_fn: Callable[..., Engine | AsyncEngine] | None = None,
    echo: bool = False,
) -> Engine:
    if engine_create_fn is None:
        engine_create_fn = create_engine
    engine = engine_create_fn(
        db_url,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
        echo=echo,
    )
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    except ImportError:
        logger.warning("Skip sqlalchemy instrumentation.")
    else:
        SQLAlchemyInstrumentor().instrument(
            engine=engine if isinstance(engine, Engine) else engine.sync_engine,
            enable_commenter=True,
            commenter_options={},
        )
    return engine


@lru_cache(maxsize=1)
def create_db_engine() -> Engine:
    engine = _create_db_engine(ENV_CONFIG.db_path)
    return engine


@alru_cache(maxsize=1)
async def create_db_engine_async() -> AsyncEngine:
    engine = _create_db_engine(ENV_CONFIG.db_path, engine_create_fn=create_async_engine)
    return engine


def yield_session() -> Generator[Session, None, None]:
    with Session(create_db_engine()) as session:
        yield session


async def yield_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(await create_db_engine_async(), expire_on_commit=False) as session:
        yield session


# Sync Session context manager
sync_session = contextmanager(yield_session)
# Async Session context manager
async_session = asynccontextmanager(yield_async_session)


async def _create_tables(engine: AsyncEngine) -> bool:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(OooSQLModel.metadata.create_all)
            await conn.commit()
    except Exception as e:
        logger.exception(f"Failed to create DB tables: {e}")
        if not isinstance(e, OperationalError):
            raise
    return False


async def migrate_db():
    engine = await create_db_engine_async()
    migrated = [
        await _create_tables(engine),
    ]
    if any(migrated):
        logger.success("DB migrations performed.")
    else:
        logger.success("No DB migrations performed.")
    # Clean up connection pool
    # https://docs.sqlalchemy.org/en/20/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
    await engine.dispose()
