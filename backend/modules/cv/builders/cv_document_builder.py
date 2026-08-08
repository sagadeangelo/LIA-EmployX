"""
CV Document Builder
============================================================

Orchestrates the construction of the canonical CVDocument from
the sections detected by CVSectionSplitter.

Responsibilities
----------------
- Build contact information.
- Build professional experience.
- Build formal education.
- Build continuous training.
- Build skills.
- Build languages.
- Build certifications.
- Recover certifications incorrectly classified as education.
- Build the canonical CVDocument.

The builder is intentionally deterministic and conservative.
It does not invent information that is not present in the CV.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from backend.modules.cv.builders.certifications_builder import (
    CertificationsBuilder,
)
from backend.modules.cv.builders.education_builder import (
    EducationBuilder,
)
from backend.modules.cv.builders.experience_builder import (
    ExperienceBuilder,
)
from backend.modules.cv.builders.languages_builder import (
    LanguagesBuilder,
)
from backend.modules.cv.builders.personal_info_builder import (
    PersonalInfoBuilder,
)
from backend.modules.cv.builders.skills_builder import (
    SkillsBuilder,
)
from backend.modules.cv.models.cv_document import CVDocument
from backend.modules.cv.models.cv_metadata import CVMetadata
from backend.modules.cv.language.language_result import LanguageResult


logger = logging.getLogger(__name__)


class CVDocumentBuilder:
    """
    Orchestrates construction of the canonical CVDocument.
    """

    def __init__(self) -> None:
        self.personal_info_builder = PersonalInfoBuilder()
        self.experience_builder = ExperienceBuilder()
        self.education_builder = EducationBuilder()
        self.skills_builder = SkillsBuilder()
        self.languages_builder = LanguagesBuilder()
        self.certifications_builder = CertificationsBuilder()

    # ============================================================
    # PUBLIC API
    # ============================================================

    def build(
        self,
        metadata: CVMetadata,
        raw_text: str,
        sections: dict[str, Any],
        language: LanguageResult,
        ocr_text: str = "",
    ) -> CVDocument:
        """
        Build the canonical CVDocument.

        Args:
            metadata:
                Canonical CV metadata.

            raw_text:
                Complete extracted document text.

            sections:
                Sections detected by CVSectionSplitter.

            language:
                Detected document language.

            ocr_text:
                Optional OCR-derived text used primarily for
                contact recovery.

        Returns:
            Fully constructed CVDocument.
        """

        logger.info(
            "CVDocumentBuilder: Iniciando construcción del CVDocument"
        )

        # ========================================================
        # SECTION ACCESSOR
        # ========================================================

        def get_text(key: str) -> str:
            value = sections.get(key)

            if hasattr(value, "text"):
                return str(value.text or "")

            if value is None:
                return ""

            return str(value)

        # ========================================================
        # PERSONAL INFORMATION
        # ========================================================

        personal_info_text = self._build_personal_info_input(
            section_text=get_text("personal_info"),
            ocr_text=ocr_text,
        )

        personal_info_result = (
            self.personal_info_builder.build(
                personal_info_text
            )
        )

        # ========================================================
        # EXPERIENCE
        # ========================================================

        experience_result = (
            self.experience_builder.build(
                get_text("experience")
            )
        )

        # ========================================================
        # EDUCATION
        # ========================================================

        education_result = (
            self.education_builder.build(
                get_text("education")
            )
        )

        # EducationBuilder now returns EducationBuildData:
        #
        # education_result.data.education
        # education_result.data.continuous_training
        #
        # Keep both collections separate.

        formal_education = list(
            education_result.data.education
        )

        continuous_training = list(
            education_result.data.continuous_training
        )

        # ========================================================
        # CERTIFICATIONS
        # ========================================================

        explicit_certification_text = (
            get_text("certifications")
        )

        certifications_result = (
            self.certifications_builder.build(
                explicit_certification_text
            )
        )

        # ========================================================
        # RECOVER CERTIFICATIONS MISCLASSIFIED AS EDUCATION
        # ========================================================

        (
            formal_education,
            recovered_certification_text,
        ) = self._separate_misclassified_certifications(
            formal_education
        )

        if recovered_certification_text:
            recovered_result = (
                self.certifications_builder.build(
                    recovered_certification_text
                )
            )

            certifications_result = (
                self._merge_build_results(
                    certifications_result,
                    recovered_result,
                )
            )

        certifications_data = list(
            certifications_result.data
        )

        # ========================================================
        # SKILLS
        # ========================================================

        skills_result = (
            self.skills_builder.build(
                get_text("skills")
            )
        )

        # ========================================================
        # LANGUAGES
        # ========================================================

        languages_result = (
            self.languages_builder.build(
                get_text("languages")
            )
        )

        # ========================================================
        # LOGGING
        # ========================================================

        self._log_result(
            "PersonalInfo",
            personal_info_result,
        )

        self._log_result(
            "Experience",
            experience_result,
        )

        self._log_result(
            "Education",
            education_result,
        )

        self._log_result(
            "Skills",
            skills_result,
        )

        self._log_result(
            "Languages",
            languages_result,
        )

        self._log_result(
            "Certifications",
            certifications_result,
        )

        # ========================================================
        # PROFESSIONAL SUMMARY
        # ========================================================

        summary_text = get_text(
            "summary"
        ).strip()

        # ========================================================
        # CLEAN SECTIONS
        # ========================================================

        clean_sections = {
            key: get_text(key)
            for key in sections.keys()
        }

        # ========================================================
        # CANONICAL CV DOCUMENT
        # ========================================================

        document = CVDocument(
            metadata=metadata,
            detected_language=language,
            contact=personal_info_result.data,
            professional_summary=summary_text,
            experiences=experience_result.data,
            education=formal_education,
            continuous_training=continuous_training,
            skills=skills_result.data,
            languages=languages_result.data,
            certifications=certifications_data,
            raw_text=raw_text,
            cleaned_text=raw_text,
            sections=clean_sections,
        )

        return document

    # ============================================================
    # CERTIFICATION RECOVERY
    # ============================================================

    @classmethod
    def _separate_misclassified_certifications(
        cls,
        education_data: list[Any],
    ) -> tuple[list[Any], str]:
        """
        Separate certification-like education records.

        Example:

            institution = "Coursera"
            degree = "Google Data Analytics Professional Certificate"

        becomes:

            Google Data Analytics Professional Certificate — Coursera

        Only strong certification indicators are moved.
        """

        remaining_education: list[Any] = []
        certification_lines: list[str] = []

        for education in education_data:
            degree = cls._safe_string(
                getattr(
                    education,
                    "degree",
                    None,
                )
            )

            institution = cls._safe_string(
                getattr(
                    education,
                    "institution",
                    None,
                )
            )

            if cls._looks_like_certification(
                degree=degree,
                institution=institution,
            ):
                certification_line = (
                    cls._format_certification_for_builder(
                        degree=degree,
                        institution=institution,
                    )
                )

                if certification_line:
                    certification_lines.append(
                        certification_line
                    )

                continue

            remaining_education.append(
                education
            )

        return (
            remaining_education,
            "\n".join(
                certification_lines
            ),
        )

    @staticmethod
    def _looks_like_certification(
        degree: str,
        institution: str,
    ) -> bool:
        """
        Determine whether an education record is actually
        a professional certification.
        """

        normalized_degree = (
            CVDocumentBuilder._normalize_match(
                degree
            )
        )

        normalized_institution = (
            CVDocumentBuilder._normalize_match(
                institution
            )
        )

        # --------------------------------------------------------
        # Explicit certification terminology
        # --------------------------------------------------------

        certification_terms = (
            "certificate",
            "certification",
            "certified",
        )

        if any(
            term in normalized_degree
            for term in certification_terms
        ):
            return True

        # --------------------------------------------------------
        # Known providers combined with certification wording
        # --------------------------------------------------------

        known_providers = {
            "coursera",
            "udemy",
            "platzi",
            "edx",
        }

        if (
            normalized_institution
            in known_providers
            and any(
                term in normalized_degree
                for term in (
                    "professional",
                    "certificate",
                    "certification",
                )
            )
        ):
            return True

        return False

    @staticmethod
    def _format_certification_for_builder(
        degree: str,
        institution: str,
    ) -> str:
        """
        Convert a recovered education record into deterministic
        CertificationsBuilder input.
        """

        degree = degree.strip()
        institution = institution.strip()

        if degree and institution:
            return (
                f"{degree} — {institution}"
            )

        return degree or institution

    # ============================================================
    # BUILD RESULT MERGING
    # ============================================================

    @staticmethod
    def _merge_build_results(
        original: Any,
        recovered: Any,
    ) -> Any:
        """
        Merge two compatible BuildResult objects.

        Used for explicit certifications plus certifications
        recovered from the education section.
        """

        original_data = list(
            original.data
        )

        recovered_data = list(
            recovered.data
        )

        # --------------------------------------------------------
        # Deduplicate recovered certifications.
        # --------------------------------------------------------

        data: list[Any] = []
        seen: set[str] = set()

        for item in (
            original_data
            + recovered_data
        ):
            key = (
                CVDocumentBuilder
                ._certification_key(item)
            )

            if key in seen:
                continue

            seen.add(key)
            data.append(item)

        # --------------------------------------------------------
        # Merge warnings without duplicates.
        # --------------------------------------------------------

        warnings: list[str] = []

        for warning in (
            list(original.warnings)
            + list(recovered.warnings)
        ):
            if warning not in warnings:
                warnings.append(warning)

        # --------------------------------------------------------
        # Confidence.
        # --------------------------------------------------------

        if data:
            confidence = max(
                original.confidence,
                recovered.confidence,
            )
        else:
            confidence = min(
                original.confidence,
                recovered.confidence,
            )

        return type(original)(
            data=data,
            confidence=confidence,
            warnings=warnings,
        )

    @staticmethod
    def _certification_key(
        certification: Any,
    ) -> str:
        """
        Create a deterministic deduplication key.
        """

        name = CVDocumentBuilder._normalize_match(
            getattr(
                certification,
                "name",
                "",
            )
        )

        issuer = CVDocumentBuilder._normalize_match(
            getattr(
                certification,
                "issuer",
                "",
            )
        )

        return (
            f"{name}|{issuer}"
        )

    # ============================================================
    # PERSONAL INFORMATION
    # ============================================================

    @staticmethod
    def _build_personal_info_input(
        section_text: str,
        ocr_text: str,
    ) -> str:
        """
        Build the input sent to PersonalInfoBuilder.

        OCR is deliberately isolated from the normal section
        pipeline to avoid contaminating section detection.
        """

        section_text = (
            section_text.strip()
        )

        ocr_text = (
            ocr_text.strip()
        )

        if (
            section_text
            and ocr_text
        ):
            return (
                f"{section_text}\n\n"
                f"--- OCR CONTACT RECOVERY ---\n"
                f"{ocr_text}"
            )

        if section_text:
            return section_text

        if ocr_text:
            return ocr_text

        return ""

    # ============================================================
    # NORMALIZATION
    # ============================================================

    @staticmethod
    def _normalize_match(
        value: str,
    ) -> str:
        """
        Normalize text for deterministic comparisons.
        """

        value = (
            value
            .casefold()
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("ü", "u")
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    @staticmethod
    def _safe_string(
        value: Any,
    ) -> str:
        """
        Safely convert optional model values to strings.
        """

        if value is None:
            return ""

        return str(value).strip()

    # ============================================================
    # LOGGING
    # ============================================================

    @staticmethod
    def _log_result(
        name: str,
        result: Any,
    ) -> None:
        """
        Log builder warnings and confidence.
        """

        if result.warnings:
            logger.warning(
                "CVDocumentBuilder [%s]: "
                "Confidence %.1f%% - %s",
                name,
                result.confidence,
                result.warnings,
            )