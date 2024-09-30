import os
from pathlib import Path

import pytest
from redis.asyncio.client import Pipeline
from sqlalchemy.ext.asyncio import AsyncConnection

from image_search.image.dal import add_image, get_image
from image_search.image.processing import process_image
from image_search.image.vector_search_methods.histogram import (
    create_histogram_index,
    remove_image_from_index,
    search_for_similar_images,
)


@pytest.mark.asyncio
async def test_process_image(db_connection: AsyncConnection, data_folder: Path, redis_client: Pipeline):
    # Given
    images_path = data_folder / "lidl"
    first_img, *_ = os.listdir(images_path)

    with (images_path / first_img).open("rb") as f_img:
        image_data = f_img.read()

    image_id = await add_image(db_connection, image_data, first_img)

    image_result = await get_image(db_connection, image_id)
    assert image_result.thumbnail is None

    # Histogram index is created
    create_histogram_index()

    # When
    await process_image(db_connection, redis_client, image_id)

    # Then check DB is updated
    image_result = await get_image(db_connection, image_id)
    assert image_result.thumbnail is not None
    assert image_result.hist_vector_bytes is not None

    # Then search image
    await search_for_similar_images(redis_client, image_result.hist_vector_bytes)

    # cleanup
    await remove_image_from_index(redis_client, image_id)
