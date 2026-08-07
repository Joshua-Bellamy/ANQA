"""
app/routers/upload.py

Handles every kind of attachment Anqa accepts: images, videos, PDFs,
and generic files. Each type is routed to a small type-specific
handler in app/services/ingestion.py — this file just does validation,
storage, and response shaping.
"""

import mimetypes
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.security import get_current_user_id
from app.models.schemas import Attachment, AttachmentType, UploadOut
from app.services.ingestion import extract_pdf_text, save_upload

router = APIRouter(prefix="/upload", tags=["upload"])


def _classify(mime_type: str) -> AttachmentType:
    if mime_type in settings.allowed_image_types:
        return AttachmentType.image
    if mime_type in settings.allowed_video_types:
        return AttachmentType.video
    if mime_type in settings.allowed_doc_types:
        return AttachmentType.pdf
    return AttachmentType.file


@router.post("", response_model=UploadOut)
async def upload_file(
    file: UploadFile,
    user_id: str = Depends(get_current_user_id),
):
    mime_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.max_upload_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_upload_mb}MB limit",
        )

    attachment_type = _classify(mime_type)
    attachment_id = str(uuid.uuid4())
    stored_path: Path = save_upload(attachment_id, file.filename or "upload", contents)

    extracted_preview = None
    if attachment_type == AttachmentType.pdf:
        extracted_preview = extract_pdf_text(stored_path)[:500]

    attachment = Attachment(
        id=attachment_id,
        type=attachment_type,
        filename=file.filename or "upload",
        url=f"/files/{stored_path.name}",
        mime_type=mime_type,
    )
    return UploadOut(attachment=attachment, extracted_text_preview=extracted_preview)
