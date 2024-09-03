import os
from io import BytesIO
import boto3

s3 = boto3.client(
    's3',
    endpoint_url=os.getenv('MINIO_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('MINIO_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('MINIO_SECRET_KEY')
)

bucket_name = os.getenv('S3_BUCKET_NAME')


def upload_to_s3(image: BytesIO, file_name: str):
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=image)


def download_from_s3(file_name: str) -> BytesIO:
    response = s3.get_object(Bucket=bucket_name, Key=file_name)
    return response['Body'].read()
