"""Backward-compatible DOCX loader backed by the strategy extraction engine."""

from __future__ import annotations

from pathlib import Path

from docx import Document

from backend.modules.cv.loader.base_loader import BaseLoader
from backend.modules.cv.loader.extraction_models import DocumentExtractionError, ExtractionResult
from backend.modules.cv.loader.extraction_strategy_resolver import ExtractionStrategyResolver


class DOCXLoader(BaseLoader):
    """
    Extrae texto de documentos Word (.docx).
    Responsabilidad única: leer el archivo y retornar texto plano.
    """

    def __init__(self, resolver: ExtractionStrategyResolver | None = None) -> None:
        self._resolver = resolver or ExtractionStrategyResolver()

    def extract(self, file_path: str | Path) -> ExtractionResult:
        """Return extracted text together with a source-aware report."""
        return self._resolver.extract(file_path)

    def load(self, file_path: str | Path) -> str:
        """Legacy text-only API; an empty result is never silently returned."""
        result = self.extract(file_path)
        if not result.report.is_success:
            raise DocumentExtractionError(result.report)
        return result.raw_text

    def _legacy_paragraph_only_load(self, file_path: str | Path) -> str:
        file_path = Path(file_path)
        doc = Document(file_path)

        # ── AUDIT POINT 1a: paragraphs ──────────────────────────────────────
        paragraphs = [
            paragraph.text.strip()
            for paragraph in doc.paragraphs
            if paragraph.text.strip()
        ]
        raw_from_paragraphs = "\n".join(paragraphs)
        print(f"[AUDIT][DOCXLoader] paragraphs count : {len(doc.paragraphs)}")
        print(f"[AUDIT][DOCXLoader] non-empty paragraphs: {len(paragraphs)}")
        print(f"[AUDIT][DOCXLoader] raw_from_paragraphs length: {len(raw_from_paragraphs)}")

        # ── AUDIT POINT 1b: tables ───────────────────────────────────────────
        table_lines: list[str] = []
        for t_idx, table in enumerate(doc.tables):
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        table_lines.append(cell_text)
        raw_from_tables = "\n".join(table_lines)
        print(f"[AUDIT][DOCXLoader] tables found      : {len(doc.tables)}")
        print(f"[AUDIT][DOCXLoader] raw_from_tables length: {len(raw_from_tables)}")

        # ── AUDIT POINT 1c: combined raw_text ───────────────────────────────
        combined_parts = []
        if raw_from_paragraphs:
            combined_parts.append(raw_from_paragraphs)
        if raw_from_tables:
            combined_parts.append(raw_from_tables)
        raw_text = "\n".join(combined_parts)
        print(f"[AUDIT][DOCXLoader] TOTAL raw_text length: {len(raw_text)}")
        print(f"[AUDIT][DOCXLoader] raw_text[:500]:\n{raw_text[:500]}")
        print(f"[AUDIT][DOCXLoader] ─────────────────────────────────────────")

        return raw_text
