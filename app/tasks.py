import os
import asyncio
from celery import Celery
from celery.result import AsyncResult
from app.db import save_tasks_to_db
from app.image_processing import process_and_upload_image
from app.schemas import TaskToDatabase

celery_app = Celery('tasks', broker=os.getenv('CELERY_BROKER_URL'), backend=os.getenv('CELERY_RESULT_BACKEND'))


def get_task_status(task_id: str) -> str:
    return str(AsyncResult(task_id, app=celery_app).status)


async def process_image_async(file_bytes: bytes, task_id: str, user_id: str):
    image_links = await process_and_upload_image(file_bytes, task_id)
    await save_tasks_to_db(TaskToDatabase(task_id=task_id, image_links=image_links, user_id=user_id))


@celery_app.task
def process_image(file_bytes: bytes, user_id: str):
    task_id = process_image.request.id
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(process_image_async(file_bytes, task_id, user_id))
