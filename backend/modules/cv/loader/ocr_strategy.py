"""OCR extraction strategy for embedded DOCX images."""

from __future__ import annotations

import easyocr

from backend.modules.cv.loader.extraction_models import ExtractionChunk
from backend.modules.cv.loader.openxml_package import OpenXMLPackage


class OCRStrategy:
    """
    Extract text from embedded DOCX images using EasyOCR.

    This strategy is intentionally isolated from the rest of the extraction
    pipeline. It receives an OpenXMLPackage and returns standard
    ExtractionChunk objects, allowing the existing merger and downstream
    pipeline to remain unchanged.
    """

    def __init__(
        self,
        languages: list[str] | None = None,
        gpu: bool = False,
    ) -> None:
        self._languages = languages or ["en", "es"]
        self._gpu = gpu
        self._reader: easyocr.Reader | None = None

    @property
    def name(self) -> str:
        """Return the strategy identifier."""
        return "ocr"

    def _get_reader(self) -> easyocr.Reader:
        """Create the OCR reader lazily on first use."""
        if self._reader is None:
            self._reader = easyocr.Reader(
                self._languages,
                gpu=self._gpu,
            )

        return self._reader

    def extract(
        self,
        package: OpenXMLPackage,
    ) -> list[ExtractionChunk]:
        """
        OCR every embedded image in the DOCX package.

        Each detected text region becomes an ExtractionChunk.
        """
        chunks: list[ExtractionChunk] = []

        if not package.media_parts():
            return chunks

        reader = self._get_reader()

        ordinal = 0

        for media_part in package.media_parts():
            image_bytes = package.read_media(media_part)

            try:
                results = reader.readtext(
                    image_bytes,
                    detail=1,
                    paragraph=False,
                )
            except Exception:
                continue

            for _, text, confidence in results:
                cleaned_text = text.strip()

                if not cleaned_text:
                    continue

                if confidence < 0.30:
                    continue

                chunks.append(
                    ExtractionChunk(
                        text=cleaned_text,
                        source=self.name,
                        part_name=media_part,
                        ordinal=ordinal,
                        identity=f"{media_part}#ocr-{ordinal}",
                    )
                )

                ordinal += 1

        return chunks