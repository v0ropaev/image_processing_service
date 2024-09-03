from os import getenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import datetime
from contextlib import asynccontextmanager
from typing import List
from uuid import uuid4
from app.schemas import ImageTaskResponse, TaskToDatabase

DATABASE_URL = getenv('DATABASE_URL')

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


@asynccontextmanager
async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)


class ImageTask(Base):
    __tablename__ = 'image_tasks'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    task_id = Column(String)
    img_link = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey('users.id'))

    user = relationship("User")


async def get_user_history(user_id: str) -> List[ImageTaskResponse]:
    async with get_session() as db:
        result = await db.execute(select(ImageTask).filter_by(user_id=user_id))
        tasks = result.scalars().all()
        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found for this user")
        history = [ImageTaskResponse(**task.__dict__) for task in tasks]
        return history


async def save_tasks_to_db(tasks: TaskToDatabase):
    async with get_session() as db:
        for link in tasks.image_links:
            new_task = ImageTask(task_id=tasks.task_id, img_link=link, user_id=tasks.user_id)
            db.add(new_task)
        await db.commit()
