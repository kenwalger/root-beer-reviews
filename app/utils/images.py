"""Image upload utilities for AWS S3.

This module provides functions for uploading and deleting images to/from
AWS S3, with validation for file types and sizes.
"""
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from app.config import settings
import uuid
from datetime import datetime, UTC
from typing import Optional

# Initialize S3 client (only if credentials are provided)
s3_client: Optional[boto3.client] = None
if settings.aws_access_key_id and settings.aws_secret_access_key:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}  #: Allowed image file extensions
MAX_FILE_SIZE = 5 * 1024 * 1024  #: Maximum file size in bytes (5MB)

def _get_s3_client() -> boto3.client:
    """Get S3 client, raising error if not configured.
    
    :returns: Configured boto3 S3 client
    :rtype: boto3.client
    :raises HTTPException: If S3 is not configured
    """
    if not s3_client:
        raise HTTPException(
            status_code=500,
            detail="S3 is not configured. Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and S3_BUCKET_NAME."
        )
    if not settings.s3_bucket_name:
        raise HTTPException(
            status_code=500,
            detail="S3 bucket name is not configured. Please set S3_BUCKET_NAME."
        )
    return s3_client

async def upload_image(file: UploadFile, rootbeer_id: str) -> str:
    """Upload an image to S3.
    
    :param file: FastAPI UploadFile object
    :type file: UploadFile
    :param rootbeer_id: ID of the root beer (for organization)
    :type rootbeer_id: str
    :returns: Public URL of uploaded image
    :rtype: str
    :raises HTTPException: If upload fails or file is invalid
    """
    client = _get_s3_client()
    
    # Validate file extension
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file
    contents = await file.read()
    
    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Validate it's actually an image (basic check - file extension)
    # For MVP, we'll trust the file extension. Can add Pillow verification later.
    
    # Generate unique filename
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    # Preserve original extension
    filename = f"{rootbeer_id}/{timestamp}_{unique_id}{file_ext}"
    
    # Determine content type
    content_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    content_type = content_type_map.get(file_ext, 'image/jpeg')
    
    # Upload to S3
    try:
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=filename,
            Body=contents,
            ContentType=content_type,
            # Note: ACL is not used - bucket policy handles public access
        )
        
        # Construct S3 URL
        # Use the correct URL format based on region
        # For most regions: https://bucket.s3.region.amazonaws.com/key
        # For us-east-1: https://bucket.s3.amazonaws.com/key (no region in URL)
        if settings.aws_region == 'us-east-1':
            image_url = f"https://{settings.s3_bucket_name}.s3.amazonaws.com/{filename}"
        else:
            image_url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{filename}"
        
        return image_url
            
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")

async def delete_image(image_url: str) -> bool:
    """Delete an image from S3.
    
    :param image_url: Full URL of the image to delete
    :type image_url: str
    :returns: True if successful, False otherwise
    :rtype: bool
    
    .. note::
        This function will attempt to delete from S3. If deletion fails,
        it returns False but does not raise an exception, allowing the
        database update to proceed (to avoid orphaned references).
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        client = _get_s3_client()
    except HTTPException:
        # S3 not configured - log and return False
        logger.warning(f"S3 not configured. Cannot delete image: {image_url}")
        return False
    
    try:
        # Extract key from URL
        # URL format: https://bucket.s3.region.amazonaws.com/key or https://bucket.s3.amazonaws.com/key (us-east-1)
        if f"{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com" in image_url:
            key = image_url.split(f"{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/")[-1]
        elif f"{settings.s3_bucket_name}.s3.amazonaws.com" in image_url:
            # us-east-1 format (no region in URL)
            key = image_url.split(f"{settings.s3_bucket_name}.s3.amazonaws.com/")[-1]
        else:
            # Try to extract from any S3 URL format (fallback for edge cases)
            # Handle various S3 URL formats: bucket.s3.region.amazonaws.com/key or bucket.s3.amazonaws.com/key
            if '.s3.' in image_url and 'amazonaws.com' in image_url:
                # Extract everything after .amazonaws.com/ (S3 URLs use subdomain format with dots)
                if '.amazonaws.com/' in image_url:
                    key = image_url.split('.amazonaws.com/')[-1]
                else:
                    logger.warning(f"Could not parse S3 URL format: {image_url}")
                    return False
            else:
                logger.warning(f"URL does not appear to be a valid S3 URL: {image_url}")
                return False
        
        # Delete from S3 (boto3 calls are synchronous, but we're in an async context)
        client.delete_object(
            Bucket=settings.s3_bucket_name,
            Key=key
        )
        logger.info(f"Successfully deleted image from S3: {image_url}")
        return True
    except ClientError as e:
        logger.error(f"Failed to delete image from S3: {image_url}. Error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting image from S3: {image_url}. Error: {str(e)}")
        return False

