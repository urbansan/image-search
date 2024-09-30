from uuid import uuid4

from redis.asyncio import Redis
from sqlalchemy import desc, select, update
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from image_search.common.db_model import Image
from image_search.image.model import ImageDto
from image_search.image.vector_search_methods.histogram import search_for_similar_images


async def get_image_ids(connection: AsyncConnection, max_images: int = 5) -> list[str]:
    result = await connection.execute(
        select(Image.id).select_from(Image).order_by(desc(Image.created_at)).limit(max_images)
    )
    return [row.id for row in result.fetchall()]


async def get_image(connection: AsyncConnection, image_id: str) -> ImageDto | None:
    result = await connection.execute(select(Image).where(Image.id == image_id))
    row = result.fetchone()
    if row is not None:
        return ImageDto.from_row(row)
    return None


async def add_image(connection: AsyncConnection, image_data: bytes, filename: str) -> str:
    new_id = str(uuid4())
    await connection.execute(insert(Image).values(bytes=image_data, id=new_id, size=len(image_data), filename=filename))
    return new_id


async def update_thumbnail_and_vectors(
    connection: AsyncConnection,
    image_id: str,
    thumbnail_data: bytes,
    hist_vector_bytes: bytes,
) -> None:
    await connection.execute(
        update(Image).values(thumbnail=thumbnail_data, hist_vector_bytes=hist_vector_bytes).where(Image.id == image_id)
    )


async def get_similar_images_for_image_id(
    db_connection: AsyncConnection,
    redis_client: Redis,
    image_id: str,
) -> list[str]:
    image = await get_image(db_connection, image_id)
    if image is None:
        return []  # image does not exist

    if image.hist_vector_bytes is None:
        return []  # image is not processed

    result = await search_for_similar_images(redis_client, image.hist_vector_bytes)
    return [doc.image_id for doc in result.docs if hasattr(doc, "image_id")]
