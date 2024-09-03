from os import getenv
from alembic import context
from app.alembic_config import get_metadata, get_sync_engine

config = context.config

sql_url = getenv('DATABASE_URL').replace('+asyncpg', '')
config.set_main_option('sqlalchemy.url', sql_url)

target_metadata = get_metadata()


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = get_sync_engine()

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
