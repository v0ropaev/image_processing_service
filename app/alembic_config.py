from sqlalchemy import create_engine, pool
from app.db import Base
from os import getenv


def get_sync_engine():
    return create_engine(
        getenv('DATABASE_URL').replace('+asyncpg', ''),
        poolclass=pool.NullPool
    )


def get_metadata():
    return Base.metadata
