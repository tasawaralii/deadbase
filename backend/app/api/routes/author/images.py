from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.deps import get_current_author
from app.media import resolve_image_urls
from app.schemas.admin import AdminImageUploadPublic
from app.storage import upload_image

router = APIRouter(
    prefix="/images", tags=["author"], dependencies=[Depends(get_current_author)]
)

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/")
async def create_image(
    file: UploadFile = File(...), kind: Literal["poster", "backdrop"] = Form(...)
) -> AdminImageUploadPublic:
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, or WEBP images are allowed",
        )

    file_bytes = await file.read(_MAX_UPLOAD_BYTES + 1)
    if len(file_bytes) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Image must be 10MB or smaller")

    key = upload_image(file_bytes, kind)
    return AdminImageUploadPublic(
        image=key, urls=resolve_image_urls("bucket", key, kind)
    )
