from __future__ import annotations

from typing import Any

from backend.modules.cv.models.cv_document import CVDocument
from backend.modules.profile.models.professional_profile import (
    Certification,
    Education,
    Experience,
    Language,
    PersonalInfo,
    ProfessionalProfile,
    Skills,
)


class ProfessionalProfileMapper:
    """
    Maps the canonical CVDocument extraction model into the
    ProfessionalProfile business model consumed by the Career OS
    and Flutter UI.

    Domain boundary:

        CVDocument
            ↓
        ProfessionalProfileMapper
            ↓
        ProfessionalProfile
    """

    # ==========================================================
    # GENERIC HELPERS
    # ==========================================================

    @staticmethod
    def _partial_date_to_string(value: Any) -> str:
        """
        Convert a PartialDate-like object into the string format
        expected by ProfessionalProfile.

        The conversion never invents missing date components.

        Examples:

            year=2025
                -> "2025"

            year=2025, month=6
                -> "2025-06"

            year=2025, month=6, day=15
                -> "2025-06-15"

        Empty or unknown dates become an empty string.
        """

        if value is None:
            return ""

        if isinstance(value, str):
            return value

        year = getattr(value, "year", None)
        month = getattr(value, "month", None)
        day = getattr(value, "day", None)

        if year is None:
            return ""

        if month is None:
            return f"{year:04d}"

        if day is None:
            return f"{year:04d}-{month:02d}"

        return f"{year:04d}-{month:02d}-{day:02d}"

    @staticmethod
    def _value(
        obj: Any,
        *names: str,
        default: Any = None,
    ) -> Any:
        """
        Return the first available non-None attribute from `names`.
        """

        for name in names:
            value = getattr(obj, name, None)

            if value is not None:
                return value

        return default

    @staticmethod
    def _construct_model(
        model_class: type,
        values: dict[str, Any],
    ) -> Any:
        """
        Construct a Pydantic model using only fields declared
        by the target model.

        This protects the mapper from harmless differences between
        the extraction and business models.
        """

        model_fields = getattr(
            model_class,
            "model_fields",
            {},
        )

        if not model_fields:
            return model_class(**values)

        filtered_values = {
            key: value
            for key, value in values.items()
            if key in model_fields
        }

        return model_class(**filtered_values)

    # ==========================================================
    # MAIN MAPPER
    # ==========================================================

    @staticmethod
    def from_cv_document(
        document: CVDocument,
    ) -> ProfessionalProfile:
        """
        Convert a validated CVDocument into ProfessionalProfile.

        No extraction or parsing happens here.

        This method only translates between domain models.
        """

        profile = ProfessionalProfile()

        # ======================================================
        # PERSONAL INFORMATION
        # ======================================================

        contact = document.contact

        current_position = ""

        if document.experiences:
            current_position = (
                document.experiences[0].position or ""
            )

        total_months = 0
        from datetime import datetime

        if document.experiences:
            intervals = []
            now = datetime.now()

            for exp in document.experiences:
                start_year = getattr(exp.start_date, "year", None)
                if not start_year:
                    continue

                start_month = getattr(exp.start_date, "month", 1) or 1
                start_abs = start_year * 12 + start_month

                end_year = getattr(exp.end_date, "year", None)
                if end_year:
                    end_month = getattr(exp.end_date, "month", 1) or 1
                else:
                    end_year = now.year
                    end_month = now.month
                end_abs = end_year * 12 + end_month

                if end_abs > start_abs:
                    intervals.append((start_abs, end_abs))

            if intervals:
                intervals.sort(key=lambda x: x[0])
                merged = [intervals[0]]
                for current in intervals[1:]:
                    last = merged[-1]
                    # If periods overlap or are exactly contiguous
                    if current[0] <= last[1]:
                        merged[-1] = (last[0], max(last[1], current[1]))
                    else:
                        merged.append(current)

                for start, end in merged:
                    total_months += (end - start)

        years_of_experience = max(0, total_months // 12)

        profile.personal_info = PersonalInfo(
            name=contact.full_name or "",
            email=contact.email or "",
            phone=contact.phone or "",
            location=contact.location or "",
            linkedin=contact.linkedin or "",
            portfolio=contact.portfolio or "",
            website=contact.website or "",
            professional_summary=(
                document.professional_summary or ""
            ),
            current_position=current_position,
            years_of_experience=years_of_experience,
        )

        # ======================================================
        # EXPERIENCE
        # ======================================================

        mapped_experiences: list[Experience] = []

        for exp in document.experiences:
            mapped_experiences.append(
                ProfessionalProfileMapper._construct_model(
                    Experience,
                    {
                        "company": (
                            exp.company or ""
                        ),

                        # CVExperience.position
                        # ->
                        # ProfessionalProfile.Experience.role
                        "role": (
                            exp.position or ""
                        ),

                        # PartialDate
                        # ->
                        # string
                        "start_date": (
                            ProfessionalProfileMapper
                            ._partial_date_to_string(
                                exp.start_date
                            )
                        ),

                        "end_date": (
                            ProfessionalProfileMapper
                            ._partial_date_to_string(
                                exp.end_date
                            )
                        ),

                        "description": (
                            exp.description or ""
                        ),

                        "achievements": (
                            exp.achievements or []
                        ),

                        "technologies": (
                            exp.technologies or []
                        ),

                        # CVExperience.skills
                        # ->
                        # ProfessionalProfile.Experience.skills_used
                        "skills_used": (
                            exp.skills or []
                        ),
                    },
                )
            )

        profile.experience = mapped_experiences

        # ======================================================
        # EDUCATION
        # ======================================================

        mapped_education: list[Education] = []

        for edu in document.education:
            mapped_education.append(
                ProfessionalProfileMapper._construct_model(
                    Education,
                    {
                        "institution": (
                            edu.institution or ""
                        ),

                        "degree": (
                            edu.degree or ""
                        ),

                        # CVEducation.education_level
                        # ->
                        # ProfessionalProfile.Education.level
                        "level": (
                            getattr(
                                edu,
                                "education_level",
                                None,
                            )
                            or ""
                        ),

                        # CVEducation has no `period` field.
                        # We construct it from its dates.
                        "period": (
                            ProfessionalProfileMapper
                            ._education_period(edu)
                        ),
                    },
                )
            )

        profile.education = mapped_education

        # ======================================================
        # SKILLS
        # ======================================================

        technical_skills: list[str] = []
        soft_skills: list[str] = []

        for skill in document.skills:
            category = (
                getattr(
                    skill,
                    "category",
                    "",
                )
                or ""
            ).strip().lower()

            name = (
                getattr(
                    skill,
                    "name",
                    "",
                )
                or ""
            ).strip()

            if not name:
                continue

            if category == "soft":
                soft_skills.append(name)
            else:
                technical_skills.append(name)

        profile.skills = Skills(
            technical_skills=technical_skills,
            soft_skills=soft_skills,
        )

        # ======================================================
        # LANGUAGES
        # ======================================================

        mapped_languages: list[Language] = []

        for lang in document.languages:
            # IMPORTANT:
            #
            # CVLanguage uses:
            #
            #     name
            #
            # ProfessionalProfile.Language uses:
            #
            #     language
            #
            # Therefore:
            #
            #     lang.name -> Language.language
            #
            language_name = (
                getattr(
                    lang,
                    "name",
                    "",
                )
                or ""
            ).strip()

            language_level = (
                getattr(
                    lang,
                    "level",
                    "",
                )
                or ""
            ).strip()

            certification = (
                getattr(
                    lang,
                    "certification",
                    "",
                )
                or ""
            ).strip()

            mapped_languages.append(
                ProfessionalProfileMapper._construct_model(
                    Language,
                    {
                        "language": language_name,
                        "level": language_level,
                        "certification": certification,
                    },
                )
            )

        profile.languages = mapped_languages

        # ======================================================
        # CERTIFICATIONS
        # ======================================================

        mapped_certifications: list[Certification] = []

        for cert in document.certifications:
            cert_name = (
                getattr(
                    cert,
                    "name",
                    "",
                )
                or ""
            ).strip()

            issuer = (
                getattr(
                    cert,
                    "issuer",
                    None,
                )
                or getattr(
                    cert,
                    "provider",
                    None,
                )
                or ""
            )

            issue_date = (
                getattr(
                    cert,
                    "issue_date",
                    None,
                )
                or getattr(
                    cert,
                    "date",
                    None,
                )
                or ""
            )

            mapped_certifications.append(
                ProfessionalProfileMapper._construct_model(
                    Certification,
                    {
                        "name": cert_name,
                        "provider": issuer,
                        "date": (
                            str(issue_date)
                            if issue_date
                            else ""
                        ),
                    },
                )
            )

        profile.certifications = mapped_certifications

        return profile

    # ==========================================================
    # EDUCATION PERIOD
    # ==========================================================

    @staticmethod
    def _education_period(
        education: Any,
    ) -> str:
        """
        Build the ProfessionalProfile education `period`
        from CVEducation start/end dates.

        No date is invented.

        Examples:

            start=2020, end=2024
                -> "2020 - 2024"

            start=2020
                -> "2020"

            end=2024
                -> "2024"
        """

        start_date = getattr(
            education,
            "start_date",
            None,
        )

        end_date = getattr(
            education,
            "end_date",
            None,
        )

        start = (
            ProfessionalProfileMapper
            ._partial_date_to_string(start_date)
        )

        end = (
            ProfessionalProfileMapper
            ._partial_date_to_string(end_date)
        )

        if start and end:
            return f"{start} - {end}"

        if start:
            return start

        if end:
            return end

        return ""