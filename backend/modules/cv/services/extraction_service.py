"""
LIA EmployX
CV Extraction Service

Coordinates the complete CV extraction pipeline.

Pipeline

Upload
    ↓
Storage
    ↓
Loader  (→ raw text only)
    ↓
CVMetadata  (built here, single source of truth)
    ↓
Language Detector
    ↓
Section Splitter
    ↓
CVDocument  (assembled here)
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from backend.modules.cv.language.language_detector import LanguageDetector
from backend.modules.cv.language.language_result import LanguageResult
from backend.modules.cv.loader.loader_factory import LoaderFactory
from backend.modules.cv.loader.extraction_models import DocumentExtractionError
from backend.modules.cv.models.cv_document import CVDocument
from backend.modules.cv.models.cv_metadata import CVMetadata
from backend.modules.cv.parser.cv_section_splitter import CVSectionSplitter
from backend.modules.cv.builders.cv_document_builder import CVDocumentBuilder
from backend.modules.cv.services.validation_service import ValidationService
from backend.utils.logger import AppLogger


_MIME_MAP: dict[str, str] = {
    ".pdf":  "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc":  "application/msword",
    ".txt":  "text/plain",
}


class ExtractionService:
    """
    Main orchestration service responsible for processing CV files.

    Only this service knows how to assemble a CVMetadata and CVDocument.
    Loaders know only how to convert files to raw text.
    """

    def __init__(self) -> None:
        self.loader_factory = LoaderFactory()
        self.language_detector = LanguageDetector()
        self.section_splitter = CVSectionSplitter()
        self.document_builder = CVDocumentBuilder()
        self.validation_service = ValidationService()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def process(self, file_path: str | Path, mission_id: str = None) -> CVDocument:
        """
        Executes the complete CV extraction pipeline.

        Args:
            file_path:
                Path to the uploaded CV.
            mission_id:
                Correlation ID for logging.

        Returns:
            CVDocument with fully populated CVMetadata.
        """

        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        upload_time = datetime.utcnow()

        AppLogger.info("Parser", f"Processing CV: {file_path.name}", mission_id=mission_id)

        # -------------------------------------------------
        # 1. Load document → raw text only
        # -------------------------------------------------

        loader_start = AppLogger.get_time_ms()
        loader = self.loader_factory.get_loader(file_path)
        if hasattr(loader, "extract"):
            extraction_result = loader.extract(file_path)
            if not extraction_result.report.is_success:
                AppLogger.error(
                    "Parser",
                    f"Document extraction did not produce text: {extraction_result.report.summary()}",
                    mission_id=mission_id,
                )
                raise DocumentExtractionError(extraction_result.report)
            raw_text = extraction_result.raw_text
            AppLogger.info(
                "Parser",
                f"DOCX extraction report: {extraction_result.report.summary()}",
                mission_id=mission_id,
            )
        else:
            raw_text = loader.load(file_path)
        loader_duration = AppLogger.get_time_ms() - loader_start
        AppLogger.info("Parser", "Document loaded successfully", mission_id=mission_id, duration_ms=loader_duration)

        # ── AUDIT POINT 2: raw_text after loader ─────────────────────────────

        # -------------------------------------------------
        # 2. Build CVMetadata (single source of truth)
        # -------------------------------------------------

        metadata = CVMetadata(
            file_name=file_path.name,
            original_name=file_path.name,
            extension=extension,
            mime_type=_MIME_MAP.get(extension, "application/octet-stream"),
            file_size=file_path.stat().st_size,
            uploaded_at=upload_time,
            storage_path=str(file_path),
            extractor=loader.__class__.__name__,
        )

        # -------------------------------------------------
        # 3. Detect language
        # -------------------------------------------------

        lang_start = AppLogger.get_time_ms()
        language: LanguageResult = self.language_detector.detect(raw_text)
        lang_duration = AppLogger.get_time_ms() - lang_start
        metadata.language = language.language   # ISO code string → CVMetadata.language (str)
        AppLogger.info("Parser", f"Detected language: {language}", mission_id=mission_id, duration_ms=lang_duration)

        # -------------------------------------------------
        # 4. Split sections
        # -------------------------------------------------

        # ── AUDIT POINT 3a: raw_text BEFORE splitter ─────────────────────────

        split_start = AppLogger.get_time_ms()
        sections = self.section_splitter.split(raw_text)
        split_duration = AppLogger.get_time_ms() - split_start
        AppLogger.info("Parser", f"Detected {len(sections)} sections", mission_id=mission_id, duration_ms=split_duration)

        # ── AUDIT POINT 3b: sections after splitter ───────────────────────────

        # -------------------------------------------------
        # 5. Assemble CVDocument
        # -------------------------------------------------

        processed_time = datetime.utcnow()
        metadata.processed_at = processed_time
        metadata.processing_time_ms = int((processed_time - upload_time).total_seconds() * 1000)

        build_start = AppLogger.get_time_ms()
        document = self.document_builder.build(
            metadata=metadata,
            raw_text=raw_text,
            sections=sections,
            language=language,
        )
        
        document = self.validation_service.validate(document)
        build_duration = AppLogger.get_time_ms() - build_start

        AppLogger.info("Parser", "CVDocument assembled and validated successfully", mission_id=mission_id, duration_ms=build_duration)

        return document

    # ---------------------------------------------------------
    # Convenience methods
    # ---------------------------------------------------------

    def process_pdf(self, file_path: str | Path, mission_id: str = None) -> CVDocument:
        """Processes a PDF CV."""
        return self.process(file_path, mission_id=mission_id)

    def process_docx(self, file_path: str | Path, mission_id: str = None) -> CVDocument:
        """Processes a DOCX CV."""
        return self.process(file_path, mission_id=mission_id)

    def process_text(self, text: str) -> CVDocument:
        """
        Processes raw text without loading from disk.
        Useful for testing. Creates a minimal CVDocument with a stub metadata.
        """
        now = datetime.utcnow()
        language: LanguageResult = self.language_detector.detect(text)
        sections = self.section_splitter.split(text)

        metadata = CVMetadata(
            file_name="inline_text",
            original_name="inline_text",
            extension=".txt",
            mime_type="text/plain",
            file_size=len(text.encode("utf-8")),
            uploaded_at=now,
            storage_path="memory",
            language=language.language,   # ISO code string only
            processed_at=now,
        )

        document = self.document_builder.build(
            metadata=metadata,
            raw_text=text,
            sections=sections,
            language=language,
        )

        return self.validation_service.validate(document)
