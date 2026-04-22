import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, UploadFile, HTTPException
from sqlalchemy import select

from models.database import AsyncSessionLocal
from models.orm import Upload
from models.schemas import UploadResponse
from services.pdf_reader import extract_text_from_pdf
from services.image_reader import encode_image_to_base64, get_media_type
from services.claude_service import parse_lab_results

router = APIRouter(prefix="/api")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
PDF_TYPES = {".pdf"}


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename or "file.bin").suffix.lower()
    file_bytes = await file.read()

    upload_id = str(uuid.uuid4())
    storage_path = str(UPLOAD_DIR / f"{upload_id}{ext}")

    async with aiofiles.open(storage_path, "wb") as f:
        await f.write(file_bytes)

    extracted_text = ""
    file_type = "unknown"

    if ext in PDF_TYPES:
        file_type = "pdf"
        extracted_text = extract_text_from_pdf(file_bytes)
    elif ext in IMAGE_TYPES:
        file_type = "image"
        # Use Claude Vision to extract text from the image
        b64 = encode_image_to_base64(file_bytes)
        media_type = get_media_type(file.filename or "image.jpg")
        parsed = await parse_lab_results(None, b64, media_type)
        # Convert parsed labs back to text representation for storage
        lines = []
        for lab in parsed:
            lines.append(
                f"{lab.get('panel','')} | {lab.get('analyte','')} | "
                f"{lab.get('result','')} {lab.get('unit','')} | "
                f"Ref: {lab.get('lab_ref_range','')} | {lab.get('status','')}"
            )
        extracted_text = "\n".join(lines)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF or image.")

    async with AsyncSessionLocal() as db:
        upload = Upload(
            id=upload_id,
            original_name=file.filename,
            file_type=file_type,
            storage_path=storage_path,
            extracted_text=extracted_text,
        )
        db.add(upload)
        await db.commit()

    return UploadResponse(
        upload_id=upload_id,
        filename=file.filename or "",
        file_type=file_type,
        extracted_text=extracted_text,
    )
