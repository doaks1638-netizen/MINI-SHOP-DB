from pathlib import Path
from app.settings import settings
from fastapi import UploadFile, HTTPException
from uuid import uuid4

MEDIA_PRODUCTS_DIR = settings.BASE_DIR / "media" / "products"
MEDIA_PRODUCTS_DIR.mkdir(exist_ok=True, parents=True)
ALLOWED_PRODUCT_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


async def save_product_image(file: UploadFile) -> str:

    if file.content_type not in ALLOWED_PRODUCT_MIME_TYPES:
        raise HTTPException(400, detail="Only JPG, PNG, WEBP images are allowed")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(400, detail="Image is too large")

    file_name = f"{uuid4()}{Path(file.filename or '').suffix.lower() or '.jpg'}"
    file_path = MEDIA_PRODUCTS_DIR / file_name

    file_path.write_bytes(content)

    return f"/media/products/{file_name}"


def remove_product_image(url: str | None) -> None:

    if not url:
        return

    file_path = settings.BASE_DIR / (url.lstrip("/"))

    file_path.unlink(missing_ok=True)
