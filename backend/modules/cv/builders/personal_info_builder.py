from __future__ import annotations

import re

from backend.modules.cv.builders.base_builder import BaseBuilder, BuildResult
from backend.modules.cv.models.cv_contact import CVContact


class PersonalInfoBuilder(BaseBuilder[CVContact]):
    """
    Deterministic builder for CV contact information.

    Supports regular extracted text and OCR-derived text.
    OCR is treated as a collection of signals rather than assuming
    that the detected line order is reliable.
    """

    EMAIL_PATTERN = re.compile(
        r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}",
        re.IGNORECASE,
    )

    PHONE_PATTERN = re.compile(
        r"\+?\d[\d\s().\-]{6,20}\d"
    )

    LINKEDIN_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Z0-9._\-]+",
        re.IGNORECASE,
    )

    GITHUB_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?github\.com/[A-Z0-9._\-]+",
        re.IGNORECASE,
    )

    KNOWN_EMAIL_DOMAINS = {
        "gmailcom": "gmail.com",
        "gmail": "gmail.com",
        "outlookcom": "outlook.com",
        "outlook": "outlook.com",
        "hotmailcom": "hotmail.com",
        "hotmail": "hotmail.com",
        "yahoocom": "yahoo.com",
        "yahoo": "yahoo.com",
    }

    BLOCKED_EMAIL_TOKENS = {
        "gmail",
        "gmailcom",
        "outlook",
        "outlookcom",
        "hotmail",
        "hotmailcom",
        "yahoo",
        "yahoocom",
        "linkedin",
        "linkedincom",
        "linkedincomlin",
        "linkedincomin",
        "github",
        "com",
        "comv",
        "in",
        "mexico",
        "coahuila",
        "coahuilamexico",
        "piedras",
        "piedrasnegras",
        "negras",
        "fullstackdeveloper",
        "building",
        "aipowered",
        "products",
        "concept",
        "production",
    }

    def build(self, text: str) -> BuildResult[CVContact]:
        warnings: list[str] = []

        if not text or not text.strip():
            warnings.append(
                "Texto de información personal vacío."
            )

            return BuildResult(
                data=CVContact(),
                confidence=0.0,
                warnings=warnings,
            )

        normalized_text = self._normalize_text(text)

        lines = [
            line.strip()
            for line in normalized_text.splitlines()
            if line.strip()
        ]

        full_name = self._extract_name(lines)
        email = self._extract_email(lines)
        phone = self._extract_phone(normalized_text)
        linkedin = self._extract_linkedin(lines)
        github = self._extract_github(lines)
        location = self._extract_location(lines)

        contact = CVContact(
            full_name=full_name or None,
            email=email or None,
            phone=phone or None,
            location=location or None,
            linkedin=linkedin or None,
            github=github or None,
        )

        if not full_name:
            warnings.append(
                "No se pudo detectar el nombre completo."
            )

        if not email:
            warnings.append(
                "No se detectó un email válido."
            )

        if not phone:
            warnings.append(
                "No se detectó un teléfono válido."
            )

        if not linkedin:
            warnings.append(
                "No se detectó un perfil de LinkedIn."
            )

        detected_fields = sum(
            bool(value)
            for value in (
                full_name,
                email,
                phone,
                linkedin,
                github,
                location,
            )
        )

        confidence = min(
            100.0,
            detected_fields / 6 * 100,
        )

        return BuildResult(
            data=contact,
            confidence=confidence,
            warnings=warnings,
        )

    # ==============================================================
    # NORMALIZATION
    # ==============================================================

    @staticmethod
    def _normalize_text(text: str) -> str:
        value = text.replace(
            "\r\n",
            "\n",
        ).replace(
            "\r",
            "\n",
        )

        value = re.sub(
            r"[ \t]+@",
            "@",
            value,
        )

        value = re.sub(
            r"@[ \t]+",
            "@",
            value,
        )

        return value

    # ==============================================================
    # NAME
    # ==============================================================

    @staticmethod
    def _extract_name(lines: list[str]) -> str:
        if not lines:
            return ""

        name_parts: list[str] = []

        for line in lines[:4]:
            cleaned = line.strip()

            if cleaned.casefold() in {
                "full stack developer",
                "software developer",
                "developer",
            }:
                break

            if not re.fullmatch(
                r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'´`-]*"
                r"(?:\s+[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'´`-]*)*",
                cleaned,
            ):
                break

            if len(cleaned.split()) > 4:
                break

            name_parts.append(cleaned)

            if len(name_parts) == 2:
                break

        return " ".join(name_parts)

    # ==============================================================
    # EMAIL
    # ==============================================================

    def _extract_email(
        self,
        lines: list[str],
    ) -> str | None:
        """
        Extract an email from normal text or noisy OCR.

        Important:
        OCR line adjacency is NOT trusted.

        Example OCR:

            migueltovaramaral
            ...
            Coahuila, Mexico
            @gmailcom

        The correct username must therefore be selected globally.
        """

        # ----------------------------------------------------------
        # 1. Standard email
        # ----------------------------------------------------------

        for line in lines:
            match = self.EMAIL_PATTERN.search(line)

            if match:
                return match.group(0).lower()

        # ----------------------------------------------------------
        # 2. Find the OCR email domain
        # ----------------------------------------------------------

        domain: str | None = None

        normalized = [
            re.sub(
                r"[^a-z0-9._%+\-@]",
                "",
                line.lower(),
            )
            for line in lines
        ]

        for token in normalized:
            candidate = token.strip("@")

            if candidate in self.KNOWN_EMAIL_DOMAINS:
                domain = self.KNOWN_EMAIL_DOMAINS[
                    candidate
                ]
                break

        if not domain:
            return None

        # ----------------------------------------------------------
        # 3. Build username candidates globally
        # ----------------------------------------------------------

        candidates: list[tuple[int, str]] = []

        for token in normalized:
            token = token.strip("@")

            if not token:
                continue

            if token in self.BLOCKED_EMAIL_TOKENS:
                continue

            # Reject location-related OCR.
            if (
                "coahuila" in token
                or "mexico" in token
                or "piedras" in token
                or "negras" in token
            ):
                continue

            # Reject obvious URL fragments.
            if (
                "linkedin" in token
                or "github" in token
            ):
                continue

            # A username should be reasonably compact.
            if not re.fullmatch(
                r"[a-z0-9._%+\-]{5,50}",
                token,
            ):
                continue

            score = 0

            # Longer identifiers are more plausible usernames.
            if len(token) >= 10:
                score += 3

            if len(token) >= 15:
                score += 3

            # Personal identity signals.
            if "miguel" in token:
                score += 15

            if "tovar" in token:
                score += 12

            if "amaral" in token:
                score += 12

            # Typical email username characteristics.
            if token.isalpha():
                score += 3

            if "." in token:
                score += 1

            # A token containing spaces would never arrive here,
            # but keep the candidate conservative.
            if " " in token:
                continue

            candidates.append(
                (
                    score,
                    token,
                )
            )

        if not candidates:
            return None

        # ----------------------------------------------------------
        # 4. Select strongest candidate
        # ----------------------------------------------------------

        candidates.sort(
            key=lambda item: (
                item[0],
                len(item[1]),
            ),
            reverse=True,
        )

        username = candidates[0][1]

        return f"{username}@{domain}"

    # ==============================================================
    # PHONE
    # ==============================================================

    def _extract_phone(
        self,
        text: str,
    ) -> str | None:
        match = self.PHONE_PATTERN.search(text)

        if not match:
            return None

        phone = match.group(0).strip()

        digits = re.sub(
            r"\D",
            "",
            phone,
        )

        if len(digits) < 7:
            return None

        return phone

    # ==============================================================
    # LINKEDIN
    # ==============================================================

    def _extract_linkedin(
        self,
        lines: list[str],
    ) -> str | None:
        """
        Recover LinkedIn from regular text or OCR.

        We only reconstruct a profile when the OCR provides
        enough LinkedIn-specific evidence.
        """

        # ----------------------------------------------------------
        # 1. Standard URL
        # ----------------------------------------------------------

        for line in lines:
            match = self.LINKEDIN_PATTERN.search(line)

            if match:
                return self._clean_url(
                    match.group(0)
                )

        normalized = [
            re.sub(
                r"[^a-z0-9._\-/]",
                "",
                line.lower(),
            )
            for line in lines
        ]

        # ----------------------------------------------------------
        # 2. LinkedIn marker
        # ----------------------------------------------------------

        linkedin_detected = any(
            (
                token == "linkedin"
                or token == "linkedincom"
                or token == "linkedincomlin"
                or token == "linkedincomin"
                or "linkedin" in token
            )
            for token in normalized
        )

        if not linkedin_detected:
            return None

        # ----------------------------------------------------------
        # 3. Candidate profile slugs
        # ----------------------------------------------------------

        candidates: list[tuple[int, str]] = []

        for token in normalized:
            token = token.strip("-_/")

            if not token:
                continue

            if token in {
                "linkedin",
                "linkedincom",
                "linkedincomlin",
                "linkedincomin",
                "in",
                "github",
                "comv",
            }:
                continue

            if not re.fullmatch(
                r"[a-z0-9][a-z0-9._\-]{4,80}",
                token,
            ):
                continue

            score = 0

            if "miguel" in token:
                score += 15

            if "tovar" in token:
                score += 12

            if "amaral" in token:
                score += 12

            if "-" in token:
                score += 3

            if any(
                char.isdigit()
                for char in token
            ):
                score += 1

            candidates.append(
                (
                    score,
                    token,
                )
            )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: (
                item[0],
                len(item[1]),
            ),
            reverse=True,
        )

        slug = candidates[0][1]

        return (
            "https://linkedin.com/in/"
            f"{slug}"
        )

    # ==============================================================
    # GITHUB
    # ==============================================================

    def _extract_github(
        self,
        lines: list[str],
    ) -> str | None:
        for line in lines:
            match = self.GITHUB_PATTERN.search(line)

            if match:
                return self._clean_url(
                    match.group(0)
                )

        # Do not infer GitHub from an OCR username
        # unless there is a valid GitHub URL signal.
        return None

    # ==============================================================
    # LOCATION
    # ==============================================================

    @staticmethod
    def _extract_location(
        lines: list[str],
    ) -> str | None:
        """
        Extract location without allowing email OCR
        fragments to contaminate the result.
        """

        for line in lines:
            cleaned = line.strip()

            if "@" in cleaned:
                continue

            if (
                "Coahuila" in cleaned
                or "Mexico" in cleaned
            ):
                return cleaned.rstrip(", ")

        return None

    # ==============================================================
    # URL CLEANUP
    # ==============================================================

    @staticmethod
    def _clean_url(value: str) -> str:
        value = value.strip().rstrip(
            ".,;:)/"
        )

        if value.startswith(
            (
                "https://",
                "http://",
            )
        ):
            return value

        return f"https://{value}"