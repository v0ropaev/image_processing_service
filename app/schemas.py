from typing import List
from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ImageTaskCreate(BaseModel):
    task_id: str


class TaskToDatabase(BaseModel):
    task_id: str
    image_links: List[str]
    user_id: str


class ImageTaskResponse(BaseModel):
    id: str
    task_id: str
    img_link: str
    created_at: datetime
    user_id: str

    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    task_status: str


class IDResponse(BaseModel):
    your_id: str
