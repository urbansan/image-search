import os
from hashlib import sha256
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import pytest_asyncio
from _pytest.monkeypatch import MonkeyPatch
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncConnection

import image_search.worker
from image_search.image.dal import add_image, get_image, get_image_ids
from image_search.image.processing import process_image
from image_search.webapp.main import app, download_image, find_similar_images, get_recently_added, upload_image


@pytest_asyncio.fixture
async def populate_db_with_image_data(db_connection: AsyncConnection, redis_client: Redis, image_folder: Path):
    for filename in os.listdir(image_folder):
        with (image_folder / filename).open("rb") as img_file:
            image_id = await add_image(db_connection, img_file.read(), filename)
            await process_image(db_connection, redis_client, image_id)


@pytest.mark.asyncio
async def test_get_recently_added(
    redis_client: Redis,
    test_app_client: AsyncClient,
    populate_db_with_image_data: None,
    monkeypatch: MonkeyPatch,
    db_connection: AsyncConnection,
    data_folder: Path,
):
    # Given
    max_images_to_fetch = 4

    # When
    response = await test_app_client.get(
        app.url_path_for(get_recently_added.__name__), params={"max_images": max_images_to_fetch}
    )

    # Then
    assert response.status_code == 200
    json_response = response.json()

    image_ids_in_db = await get_image_ids(db_connection, max_images=100)

    matching_ids = set(json_response["image_ids"]) & set(image_ids_in_db)
    assert len(matching_ids) == max_images_to_fetch


@pytest.mark.asyncio
async def test_upload_image_and_download_image(
    test_app_client: AsyncClient,
    monkeypatch: MonkeyPatch,
    db_connection: AsyncConnection,
    image_folder: Path,
):
    # Given
    images = await get_image_ids(db_connection)
    assert len(images) == 0

    first_image, *_ = os.listdir(image_folder)
    first_image_path = image_folder / first_image

    monkeypatch.setattr(image_search.webapp.main, "broker", MagicMock(startup=AsyncMock(), shutdown=AsyncMock()))
    monkeypatch.setattr(
        image_search.webapp.main,
        image_search.webapp.main.process_image_in_worker.__name__,
        MagicMock(kiq=AsyncMock()),
    )

    # When: upload
    response = await test_app_client.post(
        app.url_path_for(upload_image.__name__), files={"file": first_image_path.open("rb")}
    )

    # Then
    assert response.status_code == 200
    json_response = response.json()
    assert json_response

    uploaded_image = await get_image(db_connection, json_response["image_id"])
    assert uploaded_image is not None

    # When: download
    response = await test_app_client.get(
        app.url_path_for(download_image.__name__), params={"image_id": uploaded_image.id}
    )
    # Then
    assert response.status_code == 200
    assert (
        sha256(response.content).hexdigest() == sha256(first_image_path.open("rb").read()).hexdigest()
    ), "Downloaded file is different than uploaded"


@pytest.mark.asyncio
async def test_find_similar_images(
    redis_client: Redis,
    test_app_client: AsyncClient,
    populate_db_with_image_data: None,
    monkeypatch: MonkeyPatch,
    db_connection: AsyncConnection,
    data_folder: Path,
):
    # Given
    first_image_id, *_ = await get_image_ids(db_connection, max_images=1)

    # When
    response = await test_app_client.get(
        app.url_path_for(find_similar_images.__name__), params={"image_id": first_image_id}
    )

    # Then
    assert response.status_code == 200
    json_response = response.json()

    assert json_response["image_ids"]


@pytest.mark.asyncio
async def test_download_image__image_id_does_not_exist(
    test_app_client: AsyncClient,
    monkeypatch: MonkeyPatch,
    db_connection: AsyncConnection,
):
    # Given
    images = await get_image_ids(db_connection)
    assert len(images) == 0
    nonexisting_image_id = str(uuid4())

    # When: download
    response = await test_app_client.get(
        app.url_path_for(download_image.__name__), params={"image_id": nonexisting_image_id}
    )

    assert response.status_code == 404
