import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MINIO_STORAGE_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_STORAGE_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
MINIO_STORAGE_ENDPOINT = os.environ.get("MINIO_STORAGE_ENDPOINT")
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True
MINIO_STORAGE_MEDIA_BUCKET_NAME = "media"
MINIO_STORAGE_STATIC_BUCKET_NAME = "static"
