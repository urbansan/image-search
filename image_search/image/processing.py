from io import BytesIO

from PIL import Image as PILImage
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncConnection

from image_search.image.dal import get_image, update_thumbnail_and_vectors
from image_search.image.vector_search_methods.histogram import (
    add_histogram_to_vector_search,
    generate_histogram_vector_bytes,
)


async def process_image(
    connection: AsyncConnection,
    redis_client: Redis,
    image_id: str,
) -> None:
    image = await get_image(connection, image_id)
    if image is None:
        return
    thumbnail_bytes = generate_thumbnail(image.bytes_)
    hist_bytes = generate_histogram_vector_bytes(image.bytes_)
    await add_histogram_to_vector_search(redis_client, image_id, hist_bytes)
    await update_thumbnail_and_vectors(connection, image_id, thumbnail_bytes, hist_bytes)


def generate_thumbnail(image_bytes: bytes, size=(128, 128)) -> bytes:
    with BytesIO(image_bytes) as img_io, BytesIO() as thumb_io:
        img = PILImage.open(img_io)
        img.thumbnail(size)
        img.save(thumb_io, format=img.format)
        return thumb_io.getvalue()
