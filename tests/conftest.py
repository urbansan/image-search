from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient
from pytest import MonkeyPatch
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

import image_search
from image_search.common.db_handler import EchoLevel, get_engine
from image_search.common.vector_and_cache import get_redis
from image_search.image.vector_search_methods.histogram import create_histogram_index
from image_search.webapp.dependencies import get_connection
from image_search.webapp.main import app


@pytest_asyncio.fixture
async def _cached_sqla_engine() -> AsyncGenerator[AsyncEngine, ...]:
    engine = get_engine(autocommit=False, echo_level=EchoLevel.DEBUG)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db_connection(
    _cached_sqla_engine: AsyncEngine, monkeypatch: MonkeyPatch
) -> AsyncGenerator[AsyncConnection, ...]:
    async with _cached_sqla_engine.connect() as db_connection:
        mocked_engine = MagicMock(
            return_value=MagicMock(
                connect=MagicMock(
                    return_value=AsyncMock(
                        __aenter__=AsyncMock(return_value=db_connection),
                        __aexit__=AsyncMock(),
                    ),
                ),
            ),
        )

        monkeypatch.setattr(
            image_search.common.db_handler,
            image_search.common.db_handler.get_engine.__name__,
            mocked_engine,
        )

        yield db_connection


@pytest.fixture
def data_folder() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture
def image_folder(data_folder: Path) -> Path:
    return data_folder / "lidl"


@pytest_asyncio.fixture
async def redis_client() -> AsyncGenerator[Redis, ...]:
    create_histogram_index()
    async with get_redis() as _redis_client:
        try:
            yield _redis_client
        finally:
            await _redis_client.flushall()


@pytest.fixture
def test_app_client(db_connection: AsyncConnection):

    async def _inner():
        yield db_connection

    app.dependency_overrides[get_connection] = _inner
    return AsyncClient(app=app, base_url="http://test")
