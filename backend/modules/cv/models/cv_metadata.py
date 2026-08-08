from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CVMetadata(BaseModel):
    """
    Metadata técnica del documento.

    No representa información del candidato,
    sino información del archivo procesado.
    """

    file_name: str

    original_name: str

    extension: str

    mime_type: str

    file_size: int

    pages: int = 0

    language: str = "unknown"

    uploaded_at: datetime

    processed_at: datetime | None = None

    processing_time_ms: int | None = None

    parser_version: str = "1.0"

    extractor: str | None = None

    sha256: str | None = None

    storage_path: str

    success: bool = True