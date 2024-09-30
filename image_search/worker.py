from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from image_search.common.db_handler import get_engine
from image_search.common.settings import ENVS
from image_search.common.vector_and_cache import get_redis
from image_search.image.processing import process_image

broker = AioPikaBroker(ENVS.mq_str).with_result_backend(RedisAsyncResultBackend(ENVS.redis_str))


@broker.task
async def process_image_in_worker(image_id: str):
    async with get_engine().connect() as connection, get_redis() as redis_client:
        await process_image(connection, redis_client, image_id)
