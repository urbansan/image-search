from io import BytesIO

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.responses import StreamingResponse

from image_search.image.dal import add_image, get_image, get_image_ids, get_similar_images_for_image_id
from image_search.webapp.dependencies import get_connection, get_redis_client
from image_search.webapp.model import ImageIds, ImageUploaded
from image_search.worker import broker, process_image_in_worker

app = FastAPI()


@app.post("/upload", response_model=ImageUploaded)
async def upload_image(file: UploadFile = File(...), connection: AsyncConnection = Depends(get_connection)):
    image_id = await add_image(connection, file.file.read(), file.filename or "")
    await broker.startup()
    await process_image_in_worker.kiq(image_id)
    await broker.shutdown()

    return ImageUploaded(image_id=image_id, filename=file.filename or "")


@app.get("/download")
async def download_image(
    image_id: str,
    connection: AsyncConnection = Depends(get_connection),
):
    image = await get_image(connection, image_id)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with {image_id=} does not exist",
        )
    return StreamingResponse(BytesIO(image.bytes_), media_type="image/jpeg")


@app.get("/similar", response_model=ImageIds)
async def find_similar_images(
    image_id: str,
    connection: AsyncConnection = Depends(get_connection),
    redis_client: Redis = Depends(get_redis_client),
):
    """Search for 5 most similar images using histogram method"""
    image_ids = await get_similar_images_for_image_id(connection, redis_client, image_id)
    return ImageIds(image_ids=image_ids)


@app.get("/recent", response_model=ImageIds)
async def get_recently_added(
    max_images: int = 5,
    connection: AsyncConnection = Depends(get_connection),
):
    image_ids = await get_image_ids(connection, max_images=max_images)
    return ImageIds(image_ids=image_ids)
