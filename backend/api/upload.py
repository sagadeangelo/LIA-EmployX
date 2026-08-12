from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter(prefix="/api/v1", tags=["Upload"])

# Carpeta raíz del backend
BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "storage" / "uploads"

PDF_DIR = UPLOAD_DIR / "pdf"
DOCX_DIR = UPLOAD_DIR / "docx"

PDF_DIR.mkdir(parents=True, exist_ok=True)
DOCX_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_cv(file: UploadFile = File(...)):

    suffix = Path(file.filename).suffix.lower()

    if suffix not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed."
        )

    file_id = str(uuid4())

    if suffix == ".pdf":
        destination = PDF_DIR / f"{file_id}.pdf"
    else:
        destination = DOCX_DIR / f"{file_id}.docx"

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "file_id": file_id,
        "filename": file.filename,
        "stored_as": destination.name,
        "path": str(destination),
        "size": destination.stat().st_size,
        "extension": suffix
    }