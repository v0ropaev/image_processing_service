import asyncio
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.main import app

DATABASE_URL = "postgresql+asyncpg://user:password@db:5432/testdatabase"

async_engine = create_async_engine(DATABASE_URL, echo=True)


@pytest_asyncio.fixture(scope='session')
async def async_db_engine():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope='function')
async def async_db(async_db_engine):
    async_session = sessionmaker(
        bind=async_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture(scope='session')
async def async_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url='http://testserver') as client:
        yield client


@pytest_asyncio.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
