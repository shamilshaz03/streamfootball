"""
File upload endpoint used by the admin panel to upload match thumbnails and
team/tournament logos. Returns a public URL path the caller stores on the
relevant record via the PUT /matches/{id} or PUT /teams/{id} endpoints.
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.config import settings
from app.dependencies import require_role
from app.models.admin import AdminUser
from app.models.enums import AdminRole

router = APIRouter(prefix="/upload", tags=["Uploads"])

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    admin: AdminUser = Depends(require_role(AdminRole.MODERATOR)),
):
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP or GIF images are accepted")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB limit",
        )

    ext = Path(file.filename or "upload.jpg").suffix.lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest = upload_dir / filename
    dest.write_bytes(data)

    return JSONResponse({"url": f"/static/uploads/{filename}"})
