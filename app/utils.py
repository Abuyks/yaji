from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
import asyncio
from io import BytesIO
from fastapi import UploadFile, HTTPException
from .config import settings
# import boto3, aioboto3
# from botocore.exceptions import NoCredentialsError, ClientError
import uuid
import os
# import filetype
import random
import mimetypes

# s3_client = boto3.client(
#     "s3",
#     region_name="af-south-1",
#     aws_access_key_id=settings.aws_access_key_id,
#     aws_secret_access_key=settings.aws_secret_access_key,
#     endpoint_url="https://s3.af-south-1.amazonaws.com"
# )

# S3_BUCKET_NAME = settings.s3_bucket_name #"hotostashbucket"
# CLOUDFRONT_URL = settings.cloudfront_url

# async def save_file_to_s3(file: UploadFile, filename: str) -> str:
#     """
#     Uploads a file to AWS S3 and returns the file's URL.
#     """
#     try:
#         # Read file content
#         file_content = await file.read()

#         # Upload the file to S3 with public-read ACL
#         s3_client.put_object(
#             Bucket=S3_BUCKET_NAME,
#             Key=filename,
#             Body=file_content,
#             ContentType=file.content_type,
#             ACL="public-read"  # 👈 Make it publicly accessible
#         )

#         # Generate the file's public URL (CloudFront or S3 direct URL)
#         # file_url = f"{CLOUDFRONT_URL}/{filename}"
#         file_url = f"https://{S3_BUCKET_NAME}.s3.af-south-1.amazonaws.com/{filename}"  # alternative if not using CloudFront

#         return file_url

#     except NoCredentialsError:
#         raise HTTPException(status_code=500, detail="AWS credentials not available")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


# session = aioboto3.Session()

def generate_unique_filename(filename: str) -> str:
    """
    Generate a unique filename by appending a UUID to the original filename.
    """
    # Split the filename into name and extension
    name, ext = os.path.splitext(filename)
    
    # Generate a unique identifier (UUID)
    unique_id = str(uuid.uuid4())
    
    # Create a new unique filename
    unique_filename = f"{name}_{unique_id}{ext}"
    
    return unique_filename

# def is_valid_image(file: UploadFile):
#     """
#     Validate the uploaded file to ensure it's a valid image file.
#     """
#     # Read a portion of the file and detect its type
#     file_content = file.file.read(2048)  # Read a chunk of the file
#     file.file.seek(0)  # Reset the file pointer to the beginning

#     # Detect the file type
#     kind = filetype.guess(file_content)
#     if kind is None or kind.mime not in ["image/jpeg", "image/png","image/webp"]:
#         raise HTTPException(status_code=400, detail="Invalid image file type")

#     return True