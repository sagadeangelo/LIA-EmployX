"""Coordinates isolated DOCX strategies and builds a diagnostic result."""

from __future__ import annotations

from pathlib import Path

from backend.modules.cv.loader.docx_strategies import (
    DOCXExtractionStrategy,
    DrawingMLStrategy,
    HeaderStrategy,
    OpenXMLStrategy,
    StandardParagraphStrategy,
    TextBoxStrategy,
)
from backend.modules.cv.loader.extraction_models import (
    ExtractionChunk,
    ExtractionReport,
    ExtractionResult,
    ExtractionStatus,
    StrategyExecution,
)
from backend.modules.cv.loader.openxml_package import (
    InvalidOpenXMLPackage,
    OpenXMLPackage,
)


class ExtractionChunkMerger:
    """Compose one structured text stream from overlapping extraction views.

    Chunk text is treated as opaque input: this component never trims or
    collapses source whitespace. Independent text-bearing chunks are separated
    by a blank line because the established splitter contract uses blank lines
    as document-block boundaries.
    """

    _RECOVERY_SOURCE = "openxml_recovery"

    def merge(
        self,
        chunks: list[ExtractionChunk],
    ) -> tuple[str, tuple[ExtractionChunk, ...]]:
        canonical: list[ExtractionChunk] = []
        seen_identities: set[tuple[str, str]] = set()
        semantic_sources: dict[tuple[str, str], set[str]] = {}

        for chunk in chunks:
            if not chunk.text:
                continue

            if chunk.source == self._RECOVERY_SOURCE:
                continue

            identity = (chunk.part_name, chunk.identity)
            semantic_key = (
                chunk.part_name,
                self._semantic_key(chunk.text),
            )

            prior_sources = semantic_sources.get(
                semantic_key,
                set(),
            )

            if identity in seen_identities or (
                prior_sources
                and chunk.source not in prior_sources
            ):
                continue

            seen_identities.add(identity)
            semantic_sources.setdefault(
                semantic_key,
                set(),
            ).add(chunk.source)

            canonical.append(chunk)

        for chunk in chunks:
            if (
                not chunk.text
                or chunk.source != self._RECOVERY_SOURCE
            ):
                continue

            if self._is_covered_recovery(
                chunk,
                canonical,
            ):
                continue

            identity = (chunk.part_name, chunk.identity)
            semantic_key = (
                chunk.part_name,
                self._semantic_key(chunk.text),
            )

            prior_sources = semantic_sources.get(
                semantic_key,
                set(),
            )

            if identity in seen_identities or (
                prior_sources
                and chunk.source not in prior_sources
            ):
                continue

            seen_identities.add(identity)
            semantic_sources.setdefault(
                semantic_key,
                set(),
            ).add(chunk.source)

            canonical.append(chunk)

        raw_text = self._compose_blocks(canonical)

        return raw_text, tuple(canonical)

    @staticmethod
    def _semantic_key(text: str) -> str:
        """Compare text views independently of layout whitespace and casing."""
        return "".join(
            character.casefold()
            for character in text
            if character.isalnum()
        )

    def _is_covered_recovery(
        self,
        recovery: ExtractionChunk,
        canonical: list[ExtractionChunk],
    ) -> bool:
        """Suppress a fallback view when it repeats selected structured chunks."""
        recovery_key = self._semantic_key(recovery.text)

        candidates = [
            self._semantic_key(chunk.text)
            for chunk in canonical
            if (
                chunk.part_name == recovery.part_name
                and len(self._semantic_key(chunk.text)) >= 8
            )
        ]

        if not candidates:
            return False

        covered = sum(
            candidate in recovery_key
            for candidate in candidates
        )

        return covered / len(candidates) >= 0.8

    @staticmethod
    def _compose_blocks(
        chunks: list[ExtractionChunk],
    ) -> str:
        """Preserve chunk text and add only missing block boundaries."""
        if not chunks:
            return ""

        output = chunks[0].text

        for chunk in chunks[1:]:
            separator = (
                ""
                if output.endswith(
                    ("\n\n", "\r\n\r\n")
                )
                else "\n\n"
            )

            output = f"{output}{separator}{chunk.text}"

        return output


class ExtractionStrategyResolver:
    """Open/closed resolver: new layout sources are registered as strategies."""

    def __init__(
        self,
        strategies: tuple[DOCXExtractionStrategy, ...] | None = None,
    ) -> None:
        self._strategies = strategies or (
            # Header MUST execute first so candidate contact information
            # precedes the main document body.
            HeaderStrategy(),
            StandardParagraphStrategy(),
            TextBoxStrategy(),
            DrawingMLStrategy(),
            OpenXMLStrategy(),
        )

        self._merger = ExtractionChunkMerger()

    def extract(
        self,
        file_path: str | Path,
    ) -> ExtractionResult:
        path = Path(file_path)

        try:
            package = OpenXMLPackage.open(path)
            text_node_count, signals = package.signal_summary()

        except InvalidOpenXMLPackage as error:
            report = ExtractionReport(
                status=ExtractionStatus.UNSUPPORTED,
                file_path=str(path),
                errors=[str(error)],
            )

            return ExtractionResult(
                raw_text="",
                report=report,
            )

        all_chunks: list[ExtractionChunk] = []
        executions: list[StrategyExecution] = []
        errors: list[str] = []

        for strategy in self._strategies:
            try:
                chunks = strategy.extract(package)

                all_chunks.extend(chunks)

                executions.append(
                    StrategyExecution(
                        strategy.name,
                        len(chunks),
                        sum(
                            len(chunk.text)
                            for chunk in chunks
                        ),
                    )
                )

            except Exception as error:
                # Strategy isolation protects recoverable content.
                executions.append(
                    StrategyExecution(
                        strategy.name,
                        0,
                        0,
                        f"{type(error).__name__}: {error}",
                    )
                )

                errors.append(
                    f"{strategy.name}: "
                    f"{type(error).__name__}: {error}"
                )

        raw_text, merged_chunks = self._merger.merge(
            all_chunks
        )

        if raw_text:
            status = ExtractionStatus.SUCCESS
            warnings: list[str] = []

        elif package.image_count:
            status = ExtractionStatus.IMAGE_ONLY

            warnings = [
                "The DOCX contains embedded images but no "
                "extractable text. OCR is not enabled for "
                "DOCX ingestion."
            ]

        elif errors and len(errors) == len(
            self._strategies
        ):
            status = ExtractionStatus.FAILED
            warnings = []

        else:
            status = ExtractionStatus.EMPTY

            warnings = [
                "The DOCX is valid but contains no text "
                "supported by the configured extraction "
                "strategies."
            ]

        report = ExtractionReport(
            status=status,
            file_path=str(path),
            strategies=executions,
            warnings=warnings,
            errors=errors,
            text_node_count=text_node_count,
            image_count=package.image_count,
            signals=signals,
        )

        return ExtractionResult(
            raw_text=raw_text,
            report=report,
            chunks=merged_chunks,
        )