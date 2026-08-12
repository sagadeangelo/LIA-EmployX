from __future__ import annotations

import re
from typing import List

from backend.modules.cv.builders.base_builder import (
    BaseBuilder,
    BuildResult,
)
from backend.modules.cv.drafts.experience_draft import (
    ExperienceDraft,
)
from backend.modules.cv.models.cv_experience import (
    CVExperience,
)
from backend.modules.cv.normalizers.experience_normalizer import (
    ExperienceNormalizer,
)


class ExperienceBuilder(
    BaseBuilder[List[CVExperience]]
):
    """
    Builds structured work experiences from the CV experience section.

    The parser is anchor-based.

    A date range marks the end of the header of an experience:

        Position
        Company
        2025 – Present

        Description...

    The two meaningful lines immediately before the date are interpreted
    as:

        position
        company

    Decorative labels such as:

        DESTACADA
        FEATURED

    are ignored.

    This approach is intentionally based on the structure of the user's
    CV rather than attempting to infer arbitrary company/position
    relationships from punctuation.
    """

    # ==========================================================
    # DATE PATTERN
    # ==========================================================

    _DATE_PATTERN = re.compile(
        r"(?P<start>(?:19|20)\d{2})"
        r"\s*"
        r"(?:-|–|—|a|al)"
        r"\s*"
        r"(?P<end>"
        r"(?:19|20)\d{2}"
        r"|presente"
        r"|actualidad"
        r"|actual"
        r"|present"
        r"|now"
        r"|current"
        r")",
        re.IGNORECASE,
    )

    # ==========================================================
    # DECORATIVE / NON-DATA LINES
    # ==========================================================

    _IGNORED_LABELS = {
        "destacada",
        "featured",
        "featured experience",
        "experiencia destacada",
        "work experience",
        "professional experience",
        "experience",
        "experiencia",
        "experiencia profesional",
    }

    # ==========================================================
    # BUILD
    # ==========================================================

    def build(
        self,
        text: str,
    ) -> BuildResult[List[CVExperience]]:

        warnings: list[str] = []

        if not text or not text.strip():
            warnings.append(
                "Sección de experiencia vacía."
            )

            return BuildResult(
                data=[],
                confidence=0.0,
                warnings=warnings,
            )

        lines = self._clean_lines(text)

        if not lines:
            warnings.append(
                "No se encontraron líneas válidas en experiencia."
            )

            return BuildResult(
                data=[],
                confidence=0.0,
                warnings=warnings,
            )

        # ======================================================
        # FIND DATE ANCHORS
        # ======================================================

        date_indexes: list[
            tuple[int, re.Match[str]]
        ] = []

        for index, line in enumerate(lines):

            match = self._DATE_PATTERN.search(
                line
            )

            if match:
                date_indexes.append(
                    (index, match)
                )

        if not date_indexes:
            warnings.append(
                "No se encontraron anclas de fecha en experiencia."
            )

            return BuildResult(
                data=[],
                confidence=40.0,
                warnings=warnings,
            )

        experiences: list[CVExperience] = []

        seen_drafts: set[
            tuple[str, str, str, str]
        ] = set()

        confidence_values: list[float] = []

        # ======================================================
        # BUILD ONE EXPERIENCE PER DATE ANCHOR
        # ======================================================

        for anchor_position, (
            date_index,
            date_match,
        ) in enumerate(date_indexes):

            # --------------------------------------------------
            # DATE VALUES
            # --------------------------------------------------

            start_date = (
                date_match.group("start")
            )

            end_date = (
                date_match.group("end")
            )

            # --------------------------------------------------
            # HEADER RANGE
            #
            # Everything after the previous date anchor and
            # before this date belongs to the current header.
            # --------------------------------------------------

            previous_date_index = (
                date_indexes[
                    anchor_position - 1
                ][0]
                if anchor_position > 0
                else -1
            )

            header_lines = lines[
                previous_date_index + 1:
                date_index
            ]

            header_lines = [
                line
                for line in header_lines
                if not self._is_ignored_label(
                    line
                )
            ]

            # --------------------------------------------------
            # DESCRIPTION RANGE
            # --------------------------------------------------

            next_date_index = (
                date_indexes[
                    anchor_position + 1
                ][0]
                if anchor_position
                + 1
                < len(date_indexes)
                else len(lines)
            )

            description_lines = lines[
                date_index + 1:
                next_date_index
            ]

            # --------------------------------------------------
            # EXTRACT POSITION / COMPANY
            #
            # For the CV structure:
            #
            # Position
            # Company
            # Date
            #
            # the final two meaningful header lines are used.
            # --------------------------------------------------

            position = ""
            company = ""

            if len(header_lines) >= 2:

                position = header_lines[-2]
                company = header_lines[-1]

            elif len(header_lines) == 1:

                # Conservative fallback.
                position = header_lines[0]
                company = ""

            # --------------------------------------------------
            # If company/position are reversed in a future CV,
            # the explicit pattern can be adapted here without
            # touching the normalizer.
            # --------------------------------------------------

            position = self._clean_value(
                position
            )

            company = self._clean_value(
                company
            )

            # --------------------------------------------------
            # BUILD NORMALIZER INPUT
            #
            # IMPORTANT:
            #
            # "|" is safe as an internal separator.
            #
            # "-" is NOT used because:
            #
            #     LIA-Tech
            #
            # must remain intact.
            # --------------------------------------------------

            if company and position:

                title_line = (
                    f"{company} | {position}"
                )

            elif position:

                title_line = position

            elif company:

                title_line = company

            else:

                title_line = "Desconocido"

            description = "\n".join(
                description_lines
            ).strip()

            draft_key = (
                title_line,
                start_date,
                end_date,
                description,
            )

            if draft_key in seen_drafts:
                continue

            seen_drafts.add(
                draft_key
            )

            draft = ExperienceDraft(
                raw_title_line=title_line,
                raw_start_date=start_date,
                raw_end_date=end_date,
                raw_description=description,
            )

            normalization = (
                ExperienceNormalizer.normalize(
                    draft
                )
            )

            experiences.append(
                normalization.data
            )

            confidence_values.append(
                normalization.confidence
            )

            warnings.extend(
                normalization.warnings
            )

        # ======================================================
        # FINAL RESULT
        # ======================================================

        if not experiences:

            warnings.append(
                "No se pudieron construir experiencias."
            )

            return BuildResult(
                data=[],
                confidence=0.0,
                warnings=warnings,
            )

        final_confidence = (
            sum(confidence_values)
            / len(confidence_values)
        )

        warnings.append(
            "Agrupación por anclas de fecha aplicada."
        )

        return BuildResult(
            data=experiences,
            confidence=final_confidence,
            warnings=warnings,
        )

    # ==========================================================
    # HELPERS
    # ==========================================================

    @classmethod
    def _clean_lines(
        cls,
        text: str,
    ) -> list[str]:

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        lines: list[str] = []

        for raw_line in text.split("\n"):

            line = (
                raw_line or ""
            ).strip()

            if not line:
                continue

            line = re.sub(
                r"\s+",
                " ",
                line,
            )

            if not line:
                continue

            lines.append(line)

        return lines

    @classmethod
    def _is_ignored_label(
        cls,
        value: str,
    ) -> bool:

        normalized = (
            value or ""
        ).strip().casefold()

        return (
            normalized
            in cls._IGNORED_LABELS
        )

    @staticmethod
    def _clean_value(
        value: str,
    ) -> str:

        value = (
            value or ""
        ).strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()