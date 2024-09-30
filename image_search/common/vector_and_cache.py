from redis import Redis as SyncRedis
from redis.asyncio import Redis

from image_search.common.settings import ENVS


def get_redis():
    return Redis(host=ENVS.redis_host, port=ENVS.redis_port, db=0)


def get_sync_redis():
    return SyncRedis(host=ENVS.redis_host, port=ENVS.redis_port, db=0)
