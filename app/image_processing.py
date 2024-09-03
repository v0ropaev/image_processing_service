import asyncio
import zipfile
from PIL import Image
from io import BytesIO
from sqlalchemy.future import select
from app.db import ImageTask, get_session
from app.s3_client import upload_to_s3, download_from_s3


def convert_image_to_bytes(image: Image, image_format: str) -> BytesIO:
    image_bytes = BytesIO()
    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)
    return image_bytes


async def download_images_zip(task_id: str) -> BytesIO:
    async with get_session() as db:
        result = await db.execute(select(ImageTask).filter_by(task_id=task_id))
        tasks = result.scalars().all()

    images = [f"{task.img_link}" for task in tasks]

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for img_name in images:
            img_data = download_from_s3(img_name)
            zipf.writestr(img_name, img_data)

    zip_buffer.seek(0)

    return zip_buffer


async def process_and_upload_image(file_bytes: bytes, task_id: str) -> list[str]:
    image = Image.open(BytesIO(file_bytes))

    original_image = image
    original_format = image.format
    if original_format is None:
        original_format = 'JPEG'

    format_extension = 'jpeg' if original_format == 'JPEG' else 'png'

    rotated_image = image.transpose(Image.Transpose.ROTATE_90)
    gray_image = image.convert('L')
    scaled_image = image.resize((image.width // 2, image.height // 2))

    original_image_bytes, rotated_image_bytes, gray_image_bytes, scaled_image_bytes = await asyncio.gather(
        asyncio.to_thread(convert_image_to_bytes, image=original_image, image_format=original_format),
        asyncio.to_thread(convert_image_to_bytes, image=rotated_image, image_format=original_format),
        asyncio.to_thread(convert_image_to_bytes, image=gray_image, image_format=original_format),
        asyncio.to_thread(convert_image_to_bytes, image=scaled_image, image_format=original_format)
    )

    await asyncio.gather(
        asyncio.to_thread(upload_to_s3, image=original_image_bytes, file_name=f"{task_id}_original.{format_extension}"),
        asyncio.to_thread(upload_to_s3, image=rotated_image_bytes, file_name=f"{task_id}_rotated.{format_extension}"),
        asyncio.to_thread(upload_to_s3, image=gray_image_bytes, file_name=f"{task_id}_gray.{format_extension}"),
        asyncio.to_thread(upload_to_s3, image=scaled_image_bytes, file_name=f"{task_id}_scaled.{format_extension}")
    )

    return [f"{task_id}_original.{format_extension}",
            f"{task_id}_rotated.{format_extension}",
            f"{task_id}_gray.{format_extension}",
            f"{task_id}_scaled.{format_extension}"]
