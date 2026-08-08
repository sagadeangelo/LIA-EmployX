from __future__ import annotations

import re
from typing import List

from backend.modules.cv.builders.base_builder import BaseBuilder, BuildResult
from backend.modules.cv.models.cv_certification import CVCertification


class CertificationsBuilder(BaseBuilder[List[CVCertification]]):
    """
    Builds structured certification records from the certification
    section extracted from a CV.

    The builder is intentionally deterministic and conservative.

    It supports common CV extraction problems such as:

        Google Data Analytics Professional Certificate

        Google Data Analytics Professional Certificate — Coursera

        Google Data Analytics Professional CertificateCoursera

    The last form is especially important for DOCX files where text
    from different visual elements can become concatenated.
    """

    # ------------------------------------------------------------------
    # Known certification issuers.
    # ------------------------------------------------------------------

    _KNOWN_ISSUERS = (
        "Coursera",
        "Google",
        "Microsoft",
        "Amazon Web Services",
        "AWS",
        "IBM",
        "Meta",
        "Oracle",
        "Cisco",
        "CompTIA",
        "PMI",
        "Scrum.org",
        "Udemy",
        "Platzi",
        "edX",
        "LinkedIn Learning",
        "HubSpot",
        "Adobe",
        "Salesforce",
        "Red Hat",
        "NVIDIA",
        "DeepLearning.AI",
    )

    # ------------------------------------------------------------------
    # Words that strongly indicate a certification.
    # ------------------------------------------------------------------

    _CERTIFICATION_KEYWORDS = (
        "certificate",
        "certification",
        "certified",
        "professional certificate",
        "professional certification",
        "credential",
        "diploma",
        "nanodegree",
        "specialization",
        "professional course",
    )

    # ------------------------------------------------------------------
    # Headers that may accidentally arrive inside the section text.
    # ------------------------------------------------------------------

    _HEADERS = {
        "certification",
        "certifications",
        "certificate",
        "certificates",
        "certificado",
        "certificados",
        "certificacion",
        "certificaciones",
        "professionalcertifications",
        "professionalcertificates",
        "credentials",
        "credenciales",
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(
        self,
        text: str,
    ) -> BuildResult[List[CVCertification]]:
        """
        Parse raw certification-section text.

        Processing order:

        1. Normalize text.
        2. Split into candidate lines.
        3. Split merged certification/issuer text.
        4. Validate certification name.
        5. Deduplicate.
        6. Build CVCertification objects.
        """

        warnings: list[str] = []

        if not text or not text.strip():
            warnings.append("Sección de certificaciones vacía.")

            return BuildResult(
                data=[],
                confidence=0.0,
                warnings=warnings,
            )

        normalized = self._normalize(text)
        candidates = self._split_candidates(normalized)

        certifications: list[CVCertification] = []
        seen: set[tuple[str, str]] = set()

        for candidate in candidates:
            candidate = self._clean_candidate(candidate)

            if not candidate:
                continue

            # Ignore section headers.
            if self._is_header(candidate):
                continue

            # ----------------------------------------------------------
            # IMPORTANT:
            #
            # Split name and issuer BEFORE checking whether the text
            # looks like a certification.
            #
            # This allows:
            #
            #   CertificateCoursera
            #
            # to become:
            #
            #   Certificate
            #   Coursera
            # ----------------------------------------------------------

            name, issuer = self._split_name_issuer(candidate)

            name = self._clean_name(name)
            issuer = self._clean_issuer(issuer)

            if not name:
                continue

            # Validate the extracted certification name.
            if not self._looks_like_certification(name):
                continue

            key = (
                name.casefold(),
                (issuer or "").casefold(),
            )

            if key in seen:
                continue

            seen.add(key)

            certifications.append(
                CVCertification(
                    name=name,
                    issuer=issuer,
                    confidence=1.0,
                )
            )

        if not certifications:
            warnings.append(
                "No se encontraron certificaciones reconocibles."
            )

            return BuildResult(
                data=[],
                confidence=0.0,
                warnings=warnings,
            )

        return BuildResult(
            data=certifications,
            confidence=95.0,
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize(self, text: str) -> str:
        """
        Normalize whitespace without destroying meaningful punctuation.
        """

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        text = text.replace("\t", " ")

        # Normalize common visual separators.
        text = text.replace("•", "\n")
        text = text.replace("▪", "\n")
        text = text.replace("◆", "\n")
        text = text.replace("★", "\n")
        text = text.replace("✓", "\n")
        text = text.replace("✔", "\n")

        # Normalize excessive spaces.
        text = re.sub(r"[ ]{2,}", " ", text)

        # Normalize excessive empty lines.
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    # ------------------------------------------------------------------
    # Candidate splitting
    # ------------------------------------------------------------------

    def _split_candidates(self, text: str) -> list[str]:
        """
        Split the certification section into candidate records.

        Normally each certification is already on its own line.

        We additionally support common separators used by CVs:
        commas, bullets and semicolons.
        """

        candidates: list[str] = []

        for block in re.split(r"\n\s*\n|\n", text):
            block = block.strip()

            if not block:
                continue

            # A semicolon is usually a safe certification separator.
            parts = re.split(r"\s*;\s*", block)

            for part in parts:
                part = part.strip()

                if not part:
                    continue

                candidates.append(part)

        return candidates

    # ------------------------------------------------------------------
    # Cleaning
    # ------------------------------------------------------------------

    def _clean_candidate(self, value: str) -> str:
        """Remove decorative characters and surrounding whitespace."""

        value = value.strip()

        value = re.sub(
            r"^[•►▪◆★⭐✓✔\-\*]+\s*",
            "",
            value,
        )

        value = re.sub(r"\s+", " ", value)

        return value.strip()

    def _clean_name(self, value: str) -> str:
        """Clean the extracted certification name."""

        value = value.strip()

        value = re.sub(
            r"^[•►▪◆★⭐✓✔\-\*]+\s*",
            "",
            value,
        )

        value = re.sub(r"\s+", " ", value)

        # Remove trailing separators.
        value = re.sub(r"[\s\-–—:|]+$", "", value)

        return value.strip()

    def _clean_issuer(self, value: str | None) -> str | None:
        """Clean issuer text."""

        if not value:
            return None

        value = value.strip()
        value = re.sub(r"\s+", " ", value)
        value = value.strip(" -–—:|")

        if not value:
            return None

        # Canonicalize known issuers.
        for issuer in self._KNOWN_ISSUERS:
            if value.casefold() == issuer.casefold():
                return issuer

        return value

    # ------------------------------------------------------------------
    # Header detection
    # ------------------------------------------------------------------

    def _is_header(self, value: str) -> bool:
        """Return True when the value is only a certification header."""

        normalized = re.sub(
            r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ]",
            "",
            value.lower(),
        )

        normalized = (
            normalized
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("ñ", "n")
        )

        return normalized in self._HEADERS

    # ------------------------------------------------------------------
    # Certification detection
    # ------------------------------------------------------------------

    def _looks_like_certification(self, value: str) -> bool:
        """
        Determine whether a candidate looks like a certification.

        The check is deliberately conservative to avoid interpreting
        ordinary education or skills as certifications.
        """

        normalized = value.casefold()

        for keyword in self._CERTIFICATION_KEYWORDS:
            if keyword in normalized:
                return True

        return False

    # ------------------------------------------------------------------
    # Name / issuer extraction
    # ------------------------------------------------------------------

    def _split_name_issuer(
        self,
        candidate: str,
    ) -> tuple[str, str | None]:
        """
        Split certification name from issuer.

        Supports:

            Certificate — Coursera
            Certificate - Coursera
            Certificate: Coursera
            Certificate | Coursera

        And merged DOCX text:

            CertificateCoursera
        """

        candidate = candidate.strip()

        if not candidate:
            return "", None

        # --------------------------------------------------------------
        # 1. Explicit separators.
        # --------------------------------------------------------------

        explicit_match = re.match(
            r"^(?P<name>.+?)\s*(?:—|–|-|\||:)\s*"
            r"(?P<issuer>[A-Za-z][A-Za-z0-9&.\- ]+)$",
            candidate,
            re.IGNORECASE,
        )

        if explicit_match:
            name = explicit_match.group("name").strip()
            issuer = explicit_match.group("issuer").strip()

            if self._is_known_issuer(issuer):
                return name, issuer

            # Keep an explicit issuer if it looks reasonable.
            if len(issuer.split()) <= 5:
                return name, issuer

        # --------------------------------------------------------------
        # 2. Candidate ends with a known issuer.
        #
        # Handles:
        #
        #   Google Data Analytics Professional Certificate Coursera
        # --------------------------------------------------------------

        for issuer in sorted(
            self._KNOWN_ISSUERS,
            key=len,
            reverse=True,
        ):
            pattern = re.compile(
                rf"^(?P<name>.+?)(?P<issuer>{re.escape(issuer)})$",
                re.IGNORECASE,
            )

            match = pattern.match(candidate)

            if match:
                name = match.group("name").strip()

                if name:
                    return name, issuer

        # --------------------------------------------------------------
        # 3. Merged issuer with no whitespace.
        #
        # Handles:
        #
        #   CertificateCoursera
        #   CertificateGoogle
        #   CertificateMicrosoft
        #
        # Because the issuer is explicitly known, we can safely split
        # it without relying on variable-width look-behind.
        # --------------------------------------------------------------

        for issuer in sorted(
            self._KNOWN_ISSUERS,
            key=len,
            reverse=True,
        ):
            if not candidate.casefold().endswith(
                issuer.casefold()
            ):
                continue

            name_end = len(candidate) - len(issuer)

            if name_end <= 0:
                continue

            name = candidate[:name_end].strip()

            if not name:
                continue

            # Avoid splitting a certification that actually contains
            # the issuer as part of its name.
            if self._looks_like_certification(name):
                return name, issuer

        # --------------------------------------------------------------
        # 4. No issuer detected.
        # --------------------------------------------------------------

        return candidate, None

    def _is_known_issuer(self, value: str) -> bool:
        """Return True when value matches a known issuer."""

        return any(
            value.casefold() == issuer.casefold()
            for issuer in self._KNOWN_ISSUERS
        )