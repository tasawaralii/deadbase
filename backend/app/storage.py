import io
import json
import uuid
from typing import Literal

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import HTTPException
from PIL import Image

from app.core.config import settings
from app.media import TMDB_SIZES

ImageKind = Literal["poster", "backdrop"]

_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    region_name=settings.S3_REGION,
    config=Config(signature_version="s3v4"),
)

_bucket_ready = False


def _ensure_bucket() -> None:
    global _bucket_ready
    if _bucket_ready:
        return
    try:
        _client.head_bucket(Bucket=settings.S3_BUCKET)
    except ClientError:
        _client.create_bucket(Bucket=settings.S3_BUCKET)
        _client.put_bucket_policy(
            Bucket=settings.S3_BUCKET,
            Policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{settings.S3_BUCKET}/*",
                        }
                    ],
                }
            ),
        )
    _bucket_ready = True


def upload_image(file_bytes: bytes, kind: ImageKind) -> str:
    """
    Resizes to the same width tiers used for tmdb images (see
    app.media.TMDB_SIZES) and uploads each variant under its size prefix.
    Returns the shared key to store on the model with source="bucket" -
    app.media.resolve_image_urls() builds the size-specific URLs from it.
    """
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")

    is_portrait = image.height >= image.width
    if kind == "poster" and not is_portrait:
        raise HTTPException(
            status_code=400,
            detail="Poster images must be portrait (taller than wide)",
        )
    if kind == "backdrop" and is_portrait:
        raise HTTPException(
            status_code=400,
            detail="Backdrop images must be landscape (wider than tall)",
        )

    _ensure_bucket()

    key = f"{uuid.uuid4()}.webp"

    for label in TMDB_SIZES[kind].values():
        target_width = min(int(label[1:]), image.width)
        ratio = target_width / image.width
        target_height = round(image.height * ratio)
        resized = image.resize(
            (target_width, target_height), resample=Image.Resampling.LANCZOS
        )

        buffer = io.BytesIO()
        # method=6 is WebP's max compression effort - smaller output at the
        # same quality, worth it since this only runs once per upload.
        resized.save(buffer, format="WEBP", quality=80, method=6)
        buffer.seek(0)

        _client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=f"{label}/{key}",
            Body=buffer,
            ContentType="image/webp",
        )

    return key
