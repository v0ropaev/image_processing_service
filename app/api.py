from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from app import security, tasks, image_processing
from app.db import User, get_user_history
from app.schemas import UserCreate, Token, ImageTaskCreate, ImageTaskResponse, StatusResponse, IDResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}


@router.post("/registration", response_model=Token)
async def register(user: UserCreate) -> Token:
    return await security.register_user(user.email, user.password)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    return await security.authenticate_user(form_data.username, form_data.password)


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/upload", response_model=ImageTaskCreate)
async def upload_images(files: List[UploadFile] = File(...),
                        user: User = Depends(security.get_user_from_token)) -> ImageTaskCreate:
    if user:
        task_id = ''
        for file in files:
            if not allowed_file(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Only .jpg and .png files are allowed."
                )

            file_bytes = await file.read()
            async_result = tasks.process_image.delay(file_bytes, user.id)
            task_id = async_result.task_id

        return ImageTaskCreate(task_id=task_id)


@router.get("/status/{task_id}", response_model=StatusResponse)
async def get_status(task_id: str, user: User = Depends(security.get_user_from_token)) -> StatusResponse:
    if user:
        status = tasks.get_task_status(task_id)
        return StatusResponse(task_status=status)


@router.get("/get_my_id", response_model=IDResponse)
async def get_my_id(user: User = Depends(security.get_user_from_token)) -> IDResponse:
    if user:
        return IDResponse(your_id=user.id)


@router.get("/history/{user_id}", response_model=List[ImageTaskResponse])
async def get_history(user_id: str, user: User = Depends(security.get_user_from_token)) -> List[ImageTaskResponse]:
    if user:
        history = await get_user_history(user_id)
        return history


@router.get("/task/{task_id}", response_class=StreamingResponse)
async def download_task_images(task_id: str, user: User = Depends(security.get_user_from_token)) -> StreamingResponse:
    if user:
        zip_buffer = await image_processing.download_images_zip(task_id)
        return StreamingResponse(
            zip_buffer,
            media_type='application/zip',
            headers={"Content-Disposition": f"attachment; filename={task_id}.zip"}
        )
