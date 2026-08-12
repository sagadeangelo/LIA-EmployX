"""
LIA EmployX
CV Extraction Service

Coordinates the complete CV extraction pipeline.

Pipeline

Upload
    ↓
Storage
    ↓
Loader
    ↓
ExtractionResult
    ├── raw_text
    └── OCR chunks
    ↓
CVMetadata
    ↓
Language Detector
    ↓
Section Splitter
    ↓
CVDocumentBuilder
    ↓
Validation
    ↓
CVDocument
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from backend.modules.cv.builders.cv_document_builder import CVDocumentBuilder
from backend.modules.cv.language.language_detector import LanguageDetector
from backend.modules.cv.language.language_result import LanguageResult
from backend.modules.cv.loader.extraction_models import (
    DocumentExtractionError,
    ExtractionChunk,
    ExtractionResult,
)
from backend.modules.cv.loader.loader_factory import LoaderFactory
from backend.modules.cv.models.cv_document import CVDocument
from backend.modules.cv.models.cv_metadata import CVMetadata
from backend.modules.cv.parser.cv_section_splitter import CVSectionSplitter
from backend.modules.cv.services.validation_service import ValidationService
from backend.utils.logger import AppLogger


_MIME_MAP: dict[str, str] = {
    ".pdf": "application/pdf",
    ".docx": (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),
    ".doc": "application/msword",
    ".txt": "text/plain",
}


class ExtractionService:
    """
    Main orchestration service responsible for processing CV files.

    The service coordinates:

        Loader
            ↓
        ExtractionResult
            ↓
        raw_text + OCR recovery
            ↓
        Language Detection
            ↓
        Section Splitting
            ↓
        CVDocumentBuilder
            ↓
        Validation

    Loaders remain responsible only for document extraction.

    CVDocumentBuilder remains responsible for constructing the
    canonical CVDocument.
    """

    def __init__(self) -> None:
        self.loader_factory = LoaderFactory()
        self.language_detector = LanguageDetector()
        self.section_splitter = CVSectionSplitter()
        self.document_builder = CVDocumentBuilder()
        self.validation_service = ValidationService()

    # =========================================================
    # PUBLIC API
    # =========================================================

    def process(
        self,
        file_path: str | Path,
        mission_id: str | None = None,
    ) -> CVDocument:
        """
        Execute the complete CV extraction pipeline.

        Args:
            file_path:
                Path to the uploaded CV.

            mission_id:
                Optional correlation ID for logging.

        Returns:
            A validated CVDocument.
        """

        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        upload_time = datetime.utcnow()

        AppLogger.info(
            "Parser",
            f"Processing CV: {file_path.name}",
            mission_id=mission_id,
        )

        # =====================================================
        # 1. LOAD DOCUMENT
        # =====================================================

        loader_start = AppLogger.get_time_ms()

        loader = self.loader_factory.get_loader(file_path)

        ocr_text = ""

        if hasattr(loader, "extract"):
            extraction_result: ExtractionResult = loader.extract(
                file_path
            )

            if not extraction_result.report.is_success:
                AppLogger.error(
                    "Parser",
                    (
                        "Document extraction did not produce text: "
                        f"{extraction_result.report.summary()}"
                    ),
                    mission_id=mission_id,
                )

                raise DocumentExtractionError(
                    extraction_result.report
                )

            raw_text = extraction_result.raw_text

            # -------------------------------------------------
            # OCR RECOVERY
            # -------------------------------------------------
            #
            # OCR is intentionally kept separate from raw_text.
            #
            # The loader already merges OCR chunks into the
            # ExtractionResult, but the structured OCR stream
            # must also be available to the PersonalInfoBuilder.
            #
            # This prevents image-based contact information
            # from being lost during section splitting.
            #

            ocr_chunks = self._get_ocr_chunks(
                extraction_result
            )

            ocr_text = self._compose_ocr_text(
                ocr_chunks
            )

            AppLogger.info(
                "Parser",
                (
                    "DOCX extraction report: "
                    f"{extraction_result.report.summary()}"
                ),
                mission_id=mission_id,
            )

            AppLogger.info(
                "Parser",
                (
                    f"OCR recovery: "
                    f"{len(ocr_chunks)} chunks / "
                    f"{len(ocr_text)} characters"
                ),
                mission_id=mission_id,
            )

        else:
            raw_text = loader.load(file_path)

        loader_duration = (
            AppLogger.get_time_ms() - loader_start
        )

        AppLogger.info(
            "Parser",
            "Document loaded successfully",
            mission_id=mission_id,
            duration_ms=loader_duration,
        )

        # =====================================================
        # 2. BUILD CV METADATA
        # =====================================================

        metadata = CVMetadata(
            file_name=file_path.name,
            original_name=file_path.name,
            extension=extension,
            mime_type=_MIME_MAP.get(
                extension,
                "application/octet-stream",
            ),
            file_size=file_path.stat().st_size,
            uploaded_at=upload_time,
            storage_path=str(file_path),
            extractor=loader.__class__.__name__,
        )

        # =====================================================
        # 3. DETECT LANGUAGE
        # =====================================================

        lang_start = AppLogger.get_time_ms()

        language: LanguageResult = (
            self.language_detector.detect(raw_text)
        )

        lang_duration = (
            AppLogger.get_time_ms() - lang_start
        )

        metadata.language = language.language

        AppLogger.info(
            "Parser",
            f"Detected language: {language}",
            mission_id=mission_id,
            duration_ms=lang_duration,
        )

        # =====================================================
        # 4. SPLIT SECTIONS
        # =====================================================

        split_start = AppLogger.get_time_ms()

        sections = self.section_splitter.split(
            raw_text
        )

        split_duration = (
            AppLogger.get_time_ms() - split_start
        )

        AppLogger.info(
            "Parser",
            f"Detected {len(sections)} sections",
            mission_id=mission_id,
            duration_ms=split_duration,
        )

        # =====================================================
        # 5. COMPLETE METADATA
        # =====================================================

        processed_time = datetime.utcnow()

        metadata.processed_at = processed_time

        metadata.processing_time_ms = int(
            (
                processed_time - upload_time
            ).total_seconds()
            * 1000
        )

        # =====================================================
        # 6. BUILD CV DOCUMENT
        # =====================================================

        build_start = AppLogger.get_time_ms()

        document = self.document_builder.build(
            metadata=metadata,
            raw_text=raw_text,
            sections=sections,
            language=language,
            ocr_text=ocr_text,
        )

        # =====================================================
        # 7. VALIDATE
        # =====================================================

        document = self.validation_service.validate(
            document
        )

        build_duration = (
            AppLogger.get_time_ms() - build_start
        )

        AppLogger.info(
            "Parser",
            (
                "CVDocument assembled and validated "
                "successfully"
            ),
            mission_id=mission_id,
            duration_ms=build_duration,
        )

        return document

    # =========================================================
    # OCR HELPERS
    # =========================================================

    @staticmethod
    def _get_ocr_chunks(
        extraction_result: ExtractionResult,
    ) -> list[ExtractionChunk]:
        """
        Return only OCR-generated extraction chunks.

        OCR chunks are identified by their strategy source:

            source == "ocr"

        No OCR text is inferred from raw_text here.
        """

        return [
            chunk
            for chunk in extraction_result.chunks
            if chunk.source == "ocr"
            and chunk.text.strip()
        ]

    @staticmethod
    def _compose_ocr_text(
        chunks: list[ExtractionChunk],
    ) -> str:
        """
        Compose OCR chunks into a deterministic text stream.

        Each OCR chunk represents an independent detected text
        region. A blank line is used between regions so downstream
        builders can preserve semantic boundaries.

        Source whitespace is not modified beyond removing empty
        chunks.
        """

        if not chunks:
            return ""

        return "\n\n".join(
            chunk.text.strip()
            for chunk in chunks
            if chunk.text.strip()
        )

    # =========================================================
    # CONVENIENCE METHODS
    # =========================================================

    def process_pdf(
        self,
        file_path: str | Path,
        mission_id: str | None = None,
    ) -> CVDocument:
        """Process a PDF CV."""

        return self.process(
            file_path,
            mission_id=mission_id,
        )

    def process_docx(
        self,
        file_path: str | Path,
        mission_id: str | None = None,
    ) -> CVDocument:
        """Process a DOCX CV."""

        return self.process(
            file_path,
            mission_id=mission_id,
        )

    def process_text(
        self,
        text: str,
    ) -> CVDocument:
        """
        Process raw text without loading a file.

        This path intentionally has no OCR because the input
        already consists of text.
        """

        now = datetime.utcnow()

        language: LanguageResult = (
            self.language_detector.detect(text)
        )

        sections = self.section_splitter.split(
            text
        )

        metadata = CVMetadata(
            file_name="inline_text",
            original_name="inline_text",
            extension=".txt",
            mime_type="text/plain",
            file_size=len(
                text.encode("utf-8")
            ),
            uploaded_at=now,
            storage_path="memory",
            language=language.language,
            processed_at=now,
        )

        document = self.document_builder.build(
            metadata=metadata,
            raw_text=text,
            sections=sections,
            language=language,
            ocr_text="",
        )

        return self.validation_service.validate(
            document
        )