from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from backend.modules.cv.builders.base_builder import (
    BaseBuilder,
    BuildResult,
)
from backend.modules.cv.models.cv_education import CVEducation


@dataclass
class EducationBuildData:
    """
    Structured result produced by EducationBuilder.

    The CV may contain both formal education and continuous
    professional training inside the same extracted section.

    They are kept separate here so CVDocumentBuilder can map them
    to different canonical fields.
    """

    education: List[CVEducation] = field(
        default_factory=list
    )

    continuous_training: List[CVEducation] = field(
        default_factory=list
    )


class EducationBuilder(
    BaseBuilder[EducationBuildData]
):
    """
    Build structured education records from semi-structured CV text.

    The DOCX extraction layer can merge adjacent text runs. Therefore
    this builder supports formats such as:

        Industrial and Systems EngineeringUniversity of the Valley of Mexico (UVM)

        Google Data Analytics Professional CertificateCoursera

        Continuous Training in:Artificial Intelligence,
        Flutter, and Software Architecture

    The builder distinguishes:

        1. Formal education
        2. Continuous professional training

    It does NOT classify certifications here. Certifications are handled
    by CertificationsBuilder.
    """

    # ============================================================
    # HEADERS
    # ============================================================

    _HEADERS = {
        "education",
        "educacion",
        "educación",
        "academicbackground",
        "formacionacademica",
        "formaciónacadémica",
    }

    # ============================================================
    # CONTINUOUS TRAINING MARKERS
    # ============================================================

    _CONTINUOUS_TRAINING_MARKERS = (
        "continuous training",
        "continuous education",
        "professional development",
        "professional training",
        "continuing education",
        "training in",
        "training:",
        "capacitación",
        "capacitacion",
        "formación continua",
        "formacion continua",
        "desarrollo profesional",
    )

    # ============================================================
    # INSTITUTION MARKERS
    # ============================================================

    _INSTITUTION_MARKERS = (
        "university",
        "universidad",
        "college",
        "institute",
        "instituto",
        "coursera",
        "udemy",
        "platzi",
        "edx",
        "school",
        "academy",
        "academia",
    )

    # ============================================================
    # KNOWN INSTITUTIONS
    # ============================================================

    _KNOWN_INSTITUTIONS = (
        "University of the Valley of Mexico (UVM)",
        "University of the Valley of Mexico",
        "Coursera",
        "Udemy",
        "Platzi",
        "edX",
    )

    # ============================================================
    # PUBLIC API
    # ============================================================

    def build(
        self,
        text: str,
    ) -> BuildResult[EducationBuildData]:
        """
        Build formal education and continuous training records.
        """

        warnings: list[str] = []

        if not text or not text.strip():
            warnings.append(
                "Sección de educación vacía."
            )

            return BuildResult(
                data=EducationBuildData(),
                confidence=0.0,
                warnings=warnings,
            )

        normalized = self._normalize_text(text)

        blocks = self._split_blocks(normalized)

        formal_education: list[CVEducation] = []
        continuous_training: list[CVEducation] = []

        seen_education: set[
            tuple[str, str, str]
        ] = set()

        seen_training: set[
            tuple[str, str, str]
        ] = set()

        for block in blocks:
            if self._is_continuous_training(block):
                parsed = self._parse_continuous_training(
                    block
                )

                if parsed is None:
                    continue

                institution, degree, period = parsed

                record = self._create_education(
                    institution=institution,
                    degree=degree,
                    period=period,
                )

                if record is None:
                    continue

                key = self._record_key(
                    record
                )

                if key in seen_training:
                    continue

                seen_training.add(key)
                continuous_training.append(record)

                continue

            parsed = self._parse_block(block)

            if parsed is None:
                continue

            institution, degree, period = parsed

            record = self._create_education(
                institution=institution,
                degree=degree,
                period=period,
            )

            if record is None:
                continue

            key = self._record_key(
                record
            )

            if key in seen_education:
                continue

            seen_education.add(key)
            formal_education.append(record)

        if not formal_education and not continuous_training:
            warnings.append(
                "No se pudieron identificar registros educativos válidos."
            )

            return BuildResult(
                data=EducationBuildData(),
                confidence=0.0,
                warnings=warnings,
            )

        if continuous_training:
            warnings.append(
                "Formación continua separada de educación formal."
            )

        return BuildResult(
            data=EducationBuildData(
                education=formal_education,
                continuous_training=continuous_training,
            ),
            confidence=100.0,
            warnings=warnings,
        )

    # ============================================================
    # RECORD CREATION
    # ============================================================

    @staticmethod
    def _create_education(
        institution: str,
        degree: str,
        period: str,
    ) -> CVEducation | None:
        """
        Create a CVEducation object safely.

        `CVEducation` is intentionally reused for continuous training
        because both records share the same academic structure.
        """

        institution = EducationBuilder._clean_value(
            institution
        )

        degree = EducationBuilder._clean_value(
            degree
        )

        period = EducationBuilder._clean_value(
            period
        )

        if not institution and not degree:
            return None

        return CVEducation(
            institution=institution,
            degree=degree,
            period=period,
            level="",
        )

    @staticmethod
    def _record_key(
        record: CVEducation,
    ) -> tuple[str, str, str]:
        return (
            record.institution.casefold(),
            record.degree.casefold(),
            getattr(
                record,
                "period",
                "",
            ).casefold(),
        )

    # ============================================================
    # CONTINUOUS TRAINING
    # ============================================================

    @classmethod
    def _is_continuous_training(
        cls,
        block: str,
    ) -> bool:
        """
        Detect continuous/professional training.

        Examples:

            Continuous Training in:Artificial Intelligence...

            Continuous Training in:
            Artificial Intelligence...

            Professional Development:
            Flutter and Python
        """

        normalized = cls._normalize_for_matching(
            block
        )

        compact = re.sub(
            r"\s+",
            " ",
            normalized,
        ).strip()

        for marker in cls._CONTINUOUS_TRAINING_MARKERS:
            marker_normalized = cls._normalize_for_matching(
                marker
            )

            if marker_normalized in compact:
                return True

        return False

    def _parse_continuous_training(
        self,
        block: str,
    ) -> tuple[str, str, str] | None:
        """
        Parse continuous training.

        Example:

            Continuous Training in:
            Artificial Intelligence, Flutter,
            and Software Architecture

        becomes:

            institution =
                "Continuous Training in"

            degree =
                "Artificial Intelligence, Flutter,
                 and Software Architecture"
        """

        period = self._extract_period(
            block
        )

        lines = [
            self._clean_value(line)
            for line in block.splitlines()
            if self._clean_value(line)
        ]

        if not lines:
            return None

        content = " ".join(lines)

        # --------------------------------------------------------
        # Colon format
        # --------------------------------------------------------

        colon_match = re.match(
            r"^(?P<label>"
            r"continuous\s+training"
            r"|continuous\s+education"
            r"|professional\s+development"
            r"|professional\s+training"
            r"|continuing\s+education"
            r"|training"
            r"|capacitaci[oó]n"
            r"|formaci[oó]n\s+continua"
            r"|desarrollo\s+profesional"
            r")"
            r"(?:\s+in)?"
            r"\s*:\s*"
            r"(?P<content>.+)$",
            content,
            re.IGNORECASE,
        )

        if colon_match:
            label = self._clean_value(
                colon_match.group("label")
            )

            right = self._clean_value(
                colon_match.group("content")
            )

            if right:
                return (
                    f"{label} in"
                    if " in" not in label.casefold()
                    else label,
                    right,
                    period,
                )

        # --------------------------------------------------------
        # "Continuous Training in ..." without colon
        # --------------------------------------------------------

        prefix_match = re.match(
            r"^(?P<label>"
            r"continuous\s+training"
            r"|continuous\s+education"
            r"|professional\s+development"
            r"|professional\s+training"
            r"|continuing\s+education"
            r")"
            r"(?:\s+in)?"
            r"\s+(?P<content>.+)$",
            content,
            re.IGNORECASE,
        )

        if prefix_match:
            label = self._clean_value(
                prefix_match.group("label")
            )

            right = self._clean_value(
                prefix_match.group("content")
            )

            if right:
                return (
                    f"{label} in",
                    right,
                    period,
                )

        # --------------------------------------------------------
        # Fallback
        # --------------------------------------------------------

        return (
            "Continuous Training",
            content,
            period,
        )

    # ============================================================
    # NORMALIZATION
    # ============================================================

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:
        """
        Normalize extracted text without destroying block boundaries.
        """

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        text = text.replace(
            "\u200b",
            "",
        )

        text = text.replace(
            "\u200c",
            "",
        )

        text = text.replace(
            "\u200d",
            "",
        )

        text = text.replace(
            "\ufeff",
            "",
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    @staticmethod
    def _split_blocks(
        text: str,
    ) -> list[str]:
        """
        Split the education section into logical blocks.
        """

        return [
            block.strip()
            for block in re.split(
                r"\n\s*\n",
                text,
            )
            if block.strip()
        ]

    # ============================================================
    # BLOCK PARSING
    # ============================================================

    def _parse_block(
        self,
        block: str,
    ) -> tuple[str, str, str] | None:
        """
        Parse one formal education block.
        """

        lines = [
            self._clean_value(line)
            for line in block.splitlines()
            if self._clean_value(line)
        ]

        if not lines:
            return None

        lines = [
            line
            for line in lines
            if not self._is_header(line)
        ]

        if not lines:
            return None

        period = self._extract_period(
            block
        )

        # --------------------------------------------------------
        # Known institutions first.
        # --------------------------------------------------------

        for line in lines:
            known = self._split_known_institution(
                line
            )

            if known is not None:
                degree, institution = known

                return (
                    institution,
                    degree,
                    period,
                )

        # --------------------------------------------------------
        # Multiple lines.
        # --------------------------------------------------------

        if len(lines) >= 2:
            first = lines[0]
            second = lines[1]

            if self._looks_like_institution(
                second
            ):
                return (
                    second,
                    first,
                    period,
                )

            if self._looks_like_institution(
                first
            ):
                return (
                    first,
                    second,
                    period,
                )

            return (
                second,
                first,
                period,
            )

        # --------------------------------------------------------
        # Single line.
        # --------------------------------------------------------

        line = lines[0]

        split = self._split_merged_education(
            line
        )

        if split is not None:
            degree, institution = split

            return (
                institution,
                degree,
                period,
            )

        # --------------------------------------------------------
        # Colon format.
        # --------------------------------------------------------

        colon_split = self._split_colon_education(
            line
        )

        if colon_split is not None:
            institution, degree = colon_split

            return (
                institution,
                degree,
                period,
            )

        # --------------------------------------------------------
        # Pipe format.
        # --------------------------------------------------------

        if "|" in line:
            left, right = [
                self._clean_value(part)
                for part in line.split(
                    "|",
                    1,
                )
            ]

            if self._looks_like_institution(
                right
            ):
                return (
                    right,
                    left,
                    period,
                )

            if self._looks_like_institution(
                left
            ):
                return (
                    left,
                    right,
                    period,
                )

        # --------------------------------------------------------
        # Conservative fallback.
        # --------------------------------------------------------

        return (
            "",
            line,
            period,
        )

    # ============================================================
    # KNOWN INSTITUTIONS
    # ============================================================

    def _split_known_institution(
        self,
        line: str,
    ) -> tuple[str, str] | None:
        """
        Detect known institutions even when DOCX extraction removes
        the space between degree and institution.
        """

        normalized_line = line.casefold()

        for institution in sorted(
            self._KNOWN_INSTITUTIONS,
            key=len,
            reverse=True,
        ):
            institution_lower = (
                institution.casefold()
            )

            # ----------------------------------------------------
            # Institution at end.
            # ----------------------------------------------------

            if normalized_line.endswith(
                institution_lower
            ):
                start = (
                    len(line)
                    - len(institution)
                )

                degree = self._clean_value(
                    line[:start]
                )

                if degree:
                    return (
                        degree,
                        institution,
                    )

            # ----------------------------------------------------
            # Institution at beginning.
            # ----------------------------------------------------

            if normalized_line.startswith(
                institution_lower
            ):
                end = len(institution)

                degree = self._clean_value(
                    line[end:]
                )

                if degree:
                    return (
                        degree,
                        institution,
                    )

        return None

    # ============================================================
    # MERGED EDUCATION
    # ============================================================

    def _split_merged_education(
        self,
        line: str,
    ) -> tuple[str, str] | None:
        """
        Recover institution boundaries from merged DOCX text.
        """

        marker_pattern = "|".join(
            re.escape(marker)
            for marker in self._INSTITUTION_MARKERS
        )

        match = re.search(
            rf"(?P<before>"
            rf"[A-Za-zÀ-ÿ0-9()&,.\- ]+?"
            rf")"
            rf"(?P<institution>"
            rf"(?:{marker_pattern})"
            rf"[A-Za-zÀ-ÿ0-9()&.,'\- ]*"
            rf")$",
            line,
            re.IGNORECASE,
        )

        if match:
            degree = self._clean_value(
                match.group("before")
            )

            institution = self._clean_value(
                match.group("institution")
            )

            if degree and institution:
                institution = (
                    self._normalize_institution(
                        institution
                    )
                )

                return (
                    degree,
                    institution,
                )

        for institution in self._KNOWN_INSTITUTIONS:
            match = re.search(
                re.escape(institution),
                line,
                re.IGNORECASE,
            )

            if not match:
                continue

            degree = self._clean_value(
                line[:match.start()]
            )

            if degree:
                return (
                    degree,
                    institution,
                )

        return None

    # ============================================================
    # COLON FORMAT
    # ============================================================

    def _split_colon_education(
        self,
        line: str,
    ) -> tuple[str, str] | None:
        """
        Parse:

            Continuous Training in:
            Artificial Intelligence...

        This method is retained for compatibility with normal
        education parsing. Continuous training is intercepted before
        this method is called.
        """

        if ":" not in line:
            return None

        left, right = line.split(
            ":",
            1,
        )

        left = self._clean_value(left)
        right = self._clean_value(right)

        if not left or not right:
            return None

        return (
            left,
            right,
        )

    # ============================================================
    # INSTITUTION DETECTION
    # ============================================================

    @classmethod
    def _looks_like_institution(
        cls,
        value: str,
    ) -> bool:
        normalized = cls._normalize_for_matching(
            value
        )

        return any(
            marker in normalized
            for marker in cls._INSTITUTION_MARKERS
        )

    # ============================================================
    # HEADERS
    # ============================================================

    @classmethod
    def _is_header(
        cls,
        value: str,
    ) -> bool:
        normalized = re.sub(
            r"[^a-z]",
            "",
            cls._normalize_for_matching(
                value
            ),
        )

        headers = {
            re.sub(
                r"[^a-z]",
                "",
                cls._normalize_for_matching(
                    header
                ),
            )
            for header in cls._HEADERS
        }

        return normalized in headers

    # ============================================================
    # PERIOD
    # ============================================================

    @staticmethod
    def _extract_period(
        text: str,
    ) -> str:
        range_match = re.search(
            r"\b((?:19|20)\d{2})"
            r"\s*(?:-|–|—|to|a)\s*"
            r"((?:19|20)\d{2}|Present|Presente|Current|Actualidad)\b",
            text,
            re.IGNORECASE,
        )

        if range_match:
            return (
                f"{range_match.group(1)} - "
                f"{range_match.group(2)}"
            )

        year_match = re.search(
            r"\b(?:19|20)\d{2}\b",
            text,
        )

        if year_match:
            return year_match.group(0)

        return ""

    # ============================================================
    # MATCHING NORMALIZATION
    # ============================================================

    @staticmethod
    def _normalize_for_matching(
        value: str,
    ) -> str:
        value = value.casefold()

        replacements = str.maketrans(
            "áéíóúüñ",
            "aeiouun",
        )

        return value.translate(
            replacements
        )

    # ============================================================
    # INSTITUTION NORMALIZATION
    # ============================================================

    @staticmethod
    def _normalize_institution(
        value: str,
    ) -> str:
        replacements = {
            "university of the valley of mexico": (
                "University of the Valley of Mexico"
            ),
            "coursera": "Coursera",
            "udemy": "Udemy",
            "platzi": "Platzi",
            "edx": "edX",
        }

        clean = EducationBuilder._clean_value(
            value
        )

        key = clean.casefold()

        for source, target in replacements.items():
            if key == source.casefold():
                return target

        return clean

    # ============================================================
    # CLEANING
    # ============================================================

    @staticmethod
    def _clean_value(
        value: str,
    ) -> str:
        if not value:
            return ""

        value = value.strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()