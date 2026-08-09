from __future__ import annotations

import re

from backend.modules.cv.drafts.experience_draft import ExperienceDraft
from backend.modules.cv.models.cv_experience import CVExperience
from backend.modules.cv.models.partial_date import (
    DatePrecision,
    PartialDate,
)
from backend.modules.cv.normalizers.normalization_result import (
    NormalizationResult,
)


class ExperienceNormalizer:
    """
    Normalizes an ExperienceDraft into the canonical CVExperience model.

    Important:
    Company names may contain hyphens, for example:

        LIA-Tech

    Therefore the hyphen character is NOT treated as a company/position
    separator.

    The preferred separator between company and position is '|'.
    """

    @classmethod
    def normalize(
        cls,
        draft: ExperienceDraft,
    ) -> NormalizationResult[CVExperience]:

        warnings: list[str] = []
        confidence = 100.0

        # ==========================================================
        # COMPANY / POSITION
        # ==========================================================

        company = ""
        position = ""

        title_line = (
            draft.raw_title_line or ""
        ).strip()

        # ----------------------------------------------------------
        # Preferred internal format:
        #
        #   LIA-Tech | Founder & Lead Full Stack Developer
        #
        # IMPORTANT:
        # Do NOT split on '-' because company names can contain it.
        # ----------------------------------------------------------

        if "|" in title_line:
            company_part, position_part = (
                title_line.split("|", 1)
            )

            company = company_part.strip()
            position = position_part.strip()

        else:
            # ------------------------------------------------------
            # Conservative fallback.
            #
            # We deliberately do NOT split on hyphens.
            # ------------------------------------------------------

            separator_match = re.split(
                r"\s+\b(?:como|as)\b\s+",
                title_line,
                maxsplit=1,
                flags=re.IGNORECASE,
            )

            if len(separator_match) == 2:
                company = separator_match[0].strip()
                position = separator_match[1].strip()

            elif title_line:
                # If the builder could not provide an explicit
                # company/position separator, preserve the title
                # instead of corrupting it.
                company = title_line
                position = "Desconocido"

                warnings.append(
                    "Position inferred as missing/combined with company."
                )

                confidence -= 20.0

        company = cls._clean_value(company)
        position = cls._clean_value(position)

        if not company:
            company = "Desconocido"

        if not position:
            position = "Desconocido"

            warnings.append(
                "Position inferred as missing/combined with company."
            )

            confidence -= 20.0

        # ==========================================================
        # DATES
        # ==========================================================

        start_date = cls._parse_date(
            draft.raw_start_date
        )

        end_date = None
        is_current = False

        raw_end_date = (
            draft.raw_end_date or ""
        ).strip()

        if re.search(
            r"\b("
            r"presente"
            r"|actualidad"
            r"|actual"
            r"|present"
            r"|now"
            r"|current"
            r")\b",
            raw_end_date,
            re.IGNORECASE,
        ):
            is_current = True

            warnings.append(
                "End date interpreted as Present"
            )

        else:
            end_date = cls._parse_date(
                raw_end_date
            )

        # ==========================================================
        # DESCRIPTION
        # ==========================================================

        description = (
            draft.raw_description or ""
        ).strip()

        # ==========================================================
        # MODEL
        # ==========================================================

        experience = CVExperience(
            company=company,
            position=position,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            description=description,
            achievements=[],
            technologies=[],
            skills=[],
        )

        return NormalizationResult(
            data=experience,
            confidence=max(confidence, 0.0),
            warnings=warnings,
        )

    # ==========================================================
    # DATE PARSING
    # ==========================================================

    @classmethod
    def _parse_date(
        cls,
        raw: str,
    ) -> PartialDate | None:

        if not raw:
            return None

        year_match = re.search(
            r"\b((?:19|20)\d{2})\b",
            raw,
        )

        if not year_match:
            return None

        return PartialDate(
            year=int(
                year_match.group(1)
            ),
            precision=DatePrecision.YEAR,
        )

    # ==========================================================
    # CLEANING
    # ==========================================================

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