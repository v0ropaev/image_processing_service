from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    JWT_SECRET_KEY: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    REDIS_PASSWORD: str
    MINIO_ENDPOINT_URL: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    S3_BUCKET_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
