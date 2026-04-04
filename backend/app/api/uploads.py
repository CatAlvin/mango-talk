import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import get_current_user
from app.core.config import settings
from app.models.user import User

router = APIRouter(prefix="/uploads", tags=["uploads"])

IMAGE_MIME_PREFIX = "image/"
ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}
DISALLOWED_MIME_TYPES = {
    "application/x-msdownload",
    "application/x-sh",
    "text/x-python",
    "application/javascript",
}


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def build_upload_dir(kind: str) -> tuple[str, str]:
    now = datetime.now()
    relative_dir = os.path.join(kind, now.strftime("%Y"), now.strftime("%m"))
    absolute_dir = os.path.join(settings.UPLOAD_ROOT, relative_dir)
    ensure_dir(absolute_dir)
    return relative_dir, absolute_dir


def guess_attachment_type(content_type: str | None) -> str:
    if content_type and content_type.startswith(IMAGE_MIME_PREFIX):
        return "image"
    return "file"


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未选择文件",
        )

    content_type = file.content_type or "application/octet-stream"

    if content_type in DISALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前文件类型不允许上传",
        )

    attachment_type = guess_attachment_type(content_type)
    relative_dir, absolute_dir = build_upload_dir("messages")

    ext = os.path.splitext(file.filename)[1].lower()
    stored_name = f"{uuid.uuid4().hex}{ext}"
    absolute_path = os.path.join(absolute_dir, stored_name)

    total_size = 0
    chunk_size = 1024 * 1024

    try:
        with open(absolute_path, "wb") as out_file:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break

                total_size += len(chunk)
                if total_size > settings.MAX_UPLOAD_SIZE:
                    out_file.close()
                    if os.path.exists(absolute_path):
                        os.remove(absolute_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"文件大小不能超过 {settings.MAX_UPLOAD_SIZE // (1024 * 1024)} MB",
                    )

                out_file.write(chunk)
    finally:
        await file.close()

    relative_path = os.path.join(relative_dir, stored_name).replace("\\", "/")
    file_url = f"{settings.UPLOAD_URL_PREFIX}/{relative_path}"

    return {
        "message": "upload success",
        "data": {
            "uploaded_by": current_user.id,
            "attachment_type": attachment_type,
            "original_name": file.filename,
            "stored_name": stored_name,
            "storage_path": absolute_path,
            "file_url": file_url,
            "mime_type": content_type,
            "file_size": total_size,
        },
    }