import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from image_search.image.dal import add_image, get_image, get_image_ids


@pytest.mark.asyncio
async def test_add_image(db_connection: AsyncConnection):
    # Given
    images = await get_image_ids(db_connection)
    assert images == []

    image_data = b"some_bytes"

    # When
    image_id = await add_image(db_connection, image_data, "some-name.jpeg")

    # Then
    image_from_db = await get_image(db_connection, image_id)
    assert image_from_db is not None
    assert image_from_db.id == image_id

    images = await get_image_ids(db_connection)
    assert len(images) == 1
    assert images[0] == image_from_db.id
