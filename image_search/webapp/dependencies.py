from typing import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncConnection

from image_search.common.db_handler import get_engine
from image_search.common.vector_and_cache import get_redis


async def get_connection() -> AsyncGenerator[AsyncConnection, None]:
    async with get_engine().connect() as connection:
        yield connection


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    async with get_redis() as _redis_client:
        yield _redis_client
