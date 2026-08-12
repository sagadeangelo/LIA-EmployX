"""Coordinates isolated DOCX extraction strategies and builds a diagnostic result."""

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
from backend.modules.cv.loader.ocr_strategy import OCRStrategy


class ExtractionChunkMerger:
    """
    Builds the canonical extraction stream from multiple DOCX strategies.

    Extraction priority:

        1. Structured OpenXML extraction
        2. OpenXML recovery, only when structured extraction is empty
        3. OCR, always preserved as an independent recovery source

    The important rule is that ``openxml_recovery`` must NEVER be appended
    to an already successful structured extraction. Recovery is a fallback,
    not another copy of the document.

    OCR is different: OCR may contain information that does not exist as
    textual OpenXML content, such as contact information rendered inside
    images.
    """

    _RECOVERY_SOURCE = "openxml_recovery"
    _OCR_SOURCE = "ocr"

    def merge(
        self,
        chunks: list[ExtractionChunk],
    ) -> tuple[str, tuple[ExtractionChunk, ...]]:
        """
        Merge all extraction chunks into the canonical CV representation.
        """

        non_empty = [
            chunk
            for chunk in chunks
            if chunk.text and chunk.text.strip()
        ]

        # ---------------------------------------------------------
        # Separate extraction channels
        # ---------------------------------------------------------

        structured = [
            chunk
            for chunk in non_empty
            if chunk.source not in {
                self._RECOVERY_SOURCE,
                self._OCR_SOURCE,
            }
        ]

        recovery = [
            chunk
            for chunk in non_empty
            if chunk.source == self._RECOVERY_SOURCE
        ]

        ocr = [
            chunk
            for chunk in non_empty
            if chunk.source == self._OCR_SOURCE
        ]

        # ---------------------------------------------------------
        # Canonical result
        # ---------------------------------------------------------

        canonical: list[ExtractionChunk] = []

        seen_identities: set[tuple[str, str]] = set()

        # ---------------------------------------------------------
        # 1. Structured extraction
        # ---------------------------------------------------------

        structured = self._remove_duplicate_sequences(
            structured
        )

        for chunk in structured:
            identity = (
                chunk.part_name,
                chunk.identity,
            )

            if identity in seen_identities:
                continue

            seen_identities.add(identity)
            canonical.append(chunk)

        # ---------------------------------------------------------
        # 2. Recovery
        #
        # IMPORTANT:
        #
        # Recovery is used ONLY if structured extraction produced
        # no usable text.
        #
        # This prevents the generic OpenXML recovery strategy from
        # injecting a second compressed copy of the entire CV.
        # ---------------------------------------------------------

        structured_text_length = sum(
            len(chunk.text.strip())
            for chunk in canonical
        )

        if structured_text_length == 0:
            recovery = self._remove_duplicate_sequences(
                recovery
            )

            for chunk in recovery:
                identity = (
                    chunk.part_name,
                    chunk.identity,
                )

                if identity in seen_identities:
                    continue

                seen_identities.add(identity)
                canonical.append(chunk)

        # ---------------------------------------------------------
        # 3. OCR
        #
        # OCR is intentionally independent from structured text.
        #
        # Example:
        #
        #   DOCX text → structured extraction
        #   Contact card image → OCR
        #
        # Both may contain valuable information.
        # ---------------------------------------------------------

        ocr = self._remove_duplicate_sequences(
            ocr
        )

        for chunk in ocr:
            identity = (
                chunk.part_name,
                chunk.identity,
            )

            if identity in seen_identities:
                continue

            seen_identities.add(identity)
            canonical.append(chunk)

        # ---------------------------------------------------------
        # 4. Compose final text
        # ---------------------------------------------------------

        raw_text = self._compose_blocks(
            canonical
        )

        return raw_text, tuple(canonical)

    @classmethod
    def _remove_duplicate_sequences(
        cls,
        chunks: list[ExtractionChunk],
    ) -> list[ExtractionChunk]:
        """
        Remove immediately repeated contiguous sequences.

        Example:

            A
            B
            C
            A
            B
            C

        becomes:

            A
            B
            C

        A minimum sequence length of three is used deliberately.
        This prevents legitimate repeated words or short labels from
        being accidentally removed.
        """

        if len(chunks) < 6:
            return chunks

        result: list[ExtractionChunk] = []

        index = 0

        while index < len(chunks):
            sequence_length = (
                cls._find_duplicate_sequence_length(
                    chunks,
                    index,
                )
            )

            if sequence_length > 0:
                result.extend(
                    chunks[
                        index:index + sequence_length
                    ]
                )

                index += sequence_length * 2

                continue

            result.append(
                chunks[index]
            )

            index += 1

        return result

    @classmethod
    def _find_duplicate_sequence_length(
        cls,
        chunks: list[ExtractionChunk],
        start: int,
    ) -> int:
        """
        Detect an immediately repeated sequence beginning at ``start``.
        """

        remaining = len(chunks) - start

        if remaining < 6:
            return 0

        max_length = remaining // 2

        for length in range(
            max_length,
            2,
            -1,
        ):
            first = chunks[
                start:start + length
            ]

            second = chunks[
                start + length:start + (length * 2)
            ]

            if len(second) != length:
                continue

            if cls._sequence_matches(
                first,
                second,
            ):
                return length

        return 0

    @classmethod
    def _sequence_matches(
        cls,
        first: list[ExtractionChunk],
        second: list[ExtractionChunk],
    ) -> bool:
        """
        Compare two sequences using semantic text identity.
        """

        if len(first) != len(second):
            return False

        for left, right in zip(
            first,
            second,
        ):
            if cls._semantic_key(
                left.text
            ) != cls._semantic_key(
                right.text
            ):
                return False

        return True

    @staticmethod
    def _semantic_key(
        text: str,
    ) -> str:
        """
        Normalize text for semantic comparison.

        Differences in:

        - casing
        - punctuation
        - whitespace

        do not affect identity.
        """

        return "".join(
            character.casefold()
            for character in text
            if character.isalnum()
        )

    @staticmethod
    def _compose_blocks(
        chunks: list[ExtractionChunk],
    ) -> str:
        """
        Compose the final canonical text.

        Source text is never rewritten. Only block separators are inserted
        between independent extraction chunks.
        """

        if not chunks:
            return ""

        output = chunks[0].text

        for chunk in chunks[1:]:
            if output.endswith(
                (
                    "\n\n",
                    "\r\n\r\n",
                )
            ):
                separator = ""
            else:
                separator = "\n\n"

            output = (
                f"{output}"
                f"{separator}"
                f"{chunk.text}"
            )

        return output


class ExtractionStrategyResolver:
    """
    Coordinates all DOCX extraction strategies.

    Each strategy is isolated so that failure in one extraction mechanism
    does not prevent other mechanisms from recovering content.
    """

    def __init__(
        self,
        strategies: tuple[
            DOCXExtractionStrategy,
            ...,
        ]
        | None = None,
    ) -> None:

        self._strategies = strategies or (
            # -----------------------------------------------------
            # 1. Header
            # -----------------------------------------------------
            #
            # Headers may contain contact information and therefore
            # are intentionally processed first.
            #
            HeaderStrategy(),

            # -----------------------------------------------------
            # 2. Standard paragraphs
            # -----------------------------------------------------
            StandardParagraphStrategy(),

            # -----------------------------------------------------
            # 3. Word text boxes
            # -----------------------------------------------------
            #
            # Important for CV layouts built with text boxes.
            #
            TextBoxStrategy(),

            # -----------------------------------------------------
            # 4. DrawingML
            # -----------------------------------------------------
            DrawingMLStrategy(),

            # -----------------------------------------------------
            # 5. Generic OpenXML recovery
            # -----------------------------------------------------
            #
            # This strategy remains available as a fallback.
            #
            OpenXMLStrategy(),

            # -----------------------------------------------------
            # 6. OCR
            # -----------------------------------------------------
            #
            # Used to recover information rendered inside images.
            #
            OCRStrategy(),
        )

        self._merger = ExtractionChunkMerger()

    def extract(
        self,
        file_path: str | Path,
    ) -> ExtractionResult:
        """
        Execute the complete DOCX extraction pipeline.
        """

        path = Path(file_path)

        # =========================================================
        # 1. Open DOCX package
        # =========================================================

        try:
            package = OpenXMLPackage.open(
                path
            )

            text_node_count, signals = (
                package.signal_summary()
            )

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

        # =========================================================
        # 2. Execute strategies independently
        # =========================================================

        all_chunks: list[ExtractionChunk] = []

        executions: list[StrategyExecution] = []

        errors: list[str] = []

        for strategy in self._strategies:

            try:
                chunks = strategy.extract(
                    package
                )

                all_chunks.extend(
                    chunks
                )

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

                # -------------------------------------------------
                # Strategy isolation
                # -------------------------------------------------
                #
                # A failing OCR strategy, for example, must not
                # destroy otherwise valid OpenXML extraction.
                #
                executions.append(
                    StrategyExecution(
                        strategy.name,
                        0,
                        0,
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),
                    )
                )

                errors.append(
                    f"{strategy.name}: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        # =========================================================
        # 3. Merge extraction results
        # =========================================================

        raw_text, merged_chunks = (
            self._merger.merge(
                all_chunks
            )
        )

        # =========================================================
        # 4. Determine extraction status
        # =========================================================

        if raw_text.strip():

            status = ExtractionStatus.SUCCESS

            warnings: list[str] = []

        elif package.image_count:

            status = ExtractionStatus.IMAGE_ONLY

            warnings = [
                (
                    "The DOCX contains embedded images "
                    "but no extractable text."
                )
            ]

        elif (
            errors
            and len(errors) == len(
                self._strategies
            )
        ):

            status = ExtractionStatus.FAILED

            warnings = []

        else:

            status = ExtractionStatus.EMPTY

            warnings = [
                (
                    "The DOCX is valid but contains "
                    "no text supported by the configured "
                    "extraction strategies."
                )
            ]

        # =========================================================
        # 5. Diagnostic report
        # =========================================================

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

        # =========================================================
        # 6. Final result
        # =========================================================

        return ExtractionResult(
            raw_text=raw_text,
            report=report,
            chunks=merged_chunks,
        )