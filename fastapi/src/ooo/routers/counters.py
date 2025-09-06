from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from ooo.db import AsyncSession, yield_async_session
from ooo.db.models import Counter
from ooo.types import CounterCreate, CounterRead

router = APIRouter()


# SQLite Counter CRUD


@router.post("/v1/counters/sqlite", summary="Create a counter.")
async def create_counter(
    session: Annotated[AsyncSession, Depends(yield_async_session)],
    body: CounterCreate,
) -> CounterRead:
    if await session.get(Counter, body.name):
        raise HTTPException(status_code=409, detail="Counter already exists")
    counter = Counter.model_validate(body)
    session.add(counter)
    await session.commit()
    await session.refresh(counter)
    logger.info(f"Created counter: {counter}")
    return counter


@router.get("/v1/counters/sqlite", summary="Get a counter.")
async def get_counter(
    session: Annotated[AsyncSession, Depends(yield_async_session)],
    name: Annotated[str | None, Query()],
) -> CounterRead:
    counter = await session.get(Counter, name)
    if counter is None:
        raise HTTPException(status_code=404, detail="Counter not found")
    logger.info(f"Retrieved counter: {counter}")
    return counter


@router.put("/v1/counters/sqlite/increment", summary="Increment a counter.")
async def increment_counter(
    session: Annotated[AsyncSession, Depends(yield_async_session)],
    name: Annotated[str | None, Query()],
) -> CounterRead:
    counter = await session.get(Counter, name)
    if counter is None:
        counter = Counter(name=name)
    counter.value += 1
    session.add(counter)
    await session.commit()
    await session.refresh(counter)
    logger.info(f"Incremented counter: {counter}")
    return counter


@router.delete("/v1/counters/sqlite", summary="Delete a counter.")
async def delete_counter(
    session: Annotated[AsyncSession, Depends(yield_async_session)],
    name: Annotated[str | None, Query()],
) -> CounterRead:
    counter = await session.get(Counter, name)
    if counter is None:
        raise HTTPException(status_code=404, detail="Counter not found")
    await session.delete(counter)
    await session.commit()
    logger.info(f'Deleted counter "{name}"')
    return counter
