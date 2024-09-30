import cv2
import numpy as np
from redis import ResponseError
from redis.asyncio import Redis
from redis.commands.search.field import VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from image_search.common.vector_and_cache import get_sync_redis

INDEX = "images_idx"


def generate_histogram_vector_bytes(image_data: bytes) -> bytes:
    img = cv2.imdecode(np.fromstring(image_data, np.uint8), cv2.IMREAD_GRAYSCALE)  # type: ignore
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    hist = cv2.normalize(hist, hist).flatten()

    return hist.tobytes()


def create_histogram_index():

    redis_client = get_sync_redis()
    # Define the index schema
    schema = (
        VectorField(
            "vector",
            "HNSW",  # Vector search algorithm
            {"TYPE": "FLOAT32", "DIM": 256, "DISTANCE_METRIC": "COSINE"},
        ),
    )

    try:
        # Create the index with Redisearch
        redis_client.ft("images_idx").create_index(
            fields=schema,
            definition=IndexDefinition(prefix=["image:"], index_type=IndexType.HASH),
        )
        print("Index created successfully")
    except ResponseError as err:
        if str(err) != "Index already exists":
            raise


async def add_histogram_to_vector_search(
    redis_client: Redis,
    image_id: str,
    hist_vector: bytes,
):
    # Store vector as a string to insert into the index
    await redis_client.hset(image_id, mapping={"vector": hist_vector})
    await redis_client.ft(INDEX).add_document(f"image:{image_id}", image_id=image_id, vector=hist_vector)


async def remove_image_from_index(redis_client: Redis, image_id: str) -> None:
    await redis_client.execute_command("FT.DEL", INDEX, image_id, "DD")


async def search_for_similar_images(redis_client: Redis, histogram_vector: bytes):
    query = (
        Query("*=>[KNN 5 @vector $query_vec]").sort_by("__vector_score").return_fields("image_id", "vector").dialect(2)
    )

    results = await redis_client.ft(INDEX).search(query, query_params={"query_vec": histogram_vector})  # type: ignore
    return results
