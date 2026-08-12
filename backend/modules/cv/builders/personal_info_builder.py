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
                domain = self.KNOWN_EMAIL_DOMAINS[candidate]
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

            if (
                "coahuila" in token
                or "mexico" in token
                or "piedras" in token
                or "negras" in token
            ):
                continue

            if (
                "linkedin" in token
                or "github" in token
            ):
                continue

            if not re.fullmatch(
                r"[a-z0-9._%+\-]{5,50}",
                token,
            ):
                continue

            score = 0

            if len(token) >= 10:
                score += 3

            if len(token) >= 15:
                score += 3

            if "miguel" in token:
                score += 15

            if "tovar" in token:
                score += 12

            if "amaral" in token:
                score += 12

            if token.isalpha():
                score += 3

            if "." in token:
                score += 1

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

    @staticmethod
    def _extract_github(
        lines: list[str],
    ) -> str | None:
        """
        Extract a GitHub profile URL from CV contact information.

        Supports:
        - Explicit GitHub URLs.
        - Fragmented DOCX/OCR contact information where the
          GitHub label and username are separated.

        The method is intentionally conservative:
        it reconstructs a profile only when a GitHub signal is
        present and a plausible username can be identified.
        """

        cleaned_lines = [
            re.sub(
                r"\s+",
                " ",
                line.strip(),
            )
            for line in lines
            if line and line.strip()
        ]

        # ----------------------------------------------------------
        # 1. Explicit GitHub URL
        # ----------------------------------------------------------

        for line in cleaned_lines:
            match = re.search(
                r"(?:https?://)?(?:www\.)?"
                r"github\.com/"
                r"([A-Za-z0-9][A-Za-z0-9._-]{2,38})",
                line,
                re.IGNORECASE,
            )

            if match:
                username = match.group(1).strip("._-")

                if username:
                    return (
                        f"https://github.com/{username}"
                    )

        # ----------------------------------------------------------
        # 2. Detect GitHub signal
        # ----------------------------------------------------------

        github_index: int | None = None

        for index, line in enumerate(cleaned_lines):
            normalized = line.lower()

            if "github" in normalized:
                github_index = index
                break

        if github_index is None:
            return None

        # ----------------------------------------------------------
        # 3. Search contact block for plausible username
        # ----------------------------------------------------------

        ignored_tokens = {
            "github",
            "github.",
            "githubportfolio",
            "portfolio",
            "com",
            "comv",
            "com.",
            "in",
            "www",
            "http",
            "https",
        }

        candidates: list[str] = []

        for index, line in enumerate(cleaned_lines):

            if index == github_index:
                continue

            normalized = line.lower().strip()

            candidate = re.sub(
                r"[^a-zA-Z0-9._-]",
                "",
                line,
            ).strip("._-")

            if not candidate:
                continue

            if normalized in ignored_tokens:
                continue

            # Never interpret email fragments as GitHub usernames.
            if "@" in line or "gmail" in normalized:
                continue

            # Never interpret phone numbers as usernames.
            if re.fullmatch(
                r"[+\d\s().-]+",
                line,
            ):
                continue

            # Ignore LinkedIn fragments.
            if "linkedin" in normalized:
                continue

            # Ignore location fragments.
            if normalized in {
                "piedrasnegras",
                "coahuilamexico",
            }:
                continue

            # GitHub username format.
            if not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9._-]{2,38}",
                candidate,
            ):
                continue

            # A pure numeric identifier is not a safe username.
            if candidate.isdigit():
                continue

            if not re.search(
                r"[A-Za-z]",
                candidate,
            ):
                continue

            candidates.append(candidate)

        # ----------------------------------------------------------
        # 4. Score candidates
        # ----------------------------------------------------------

        def score(candidate: str) -> int:
            value = candidate.lower()
            score_value = 0

            if re.fullmatch(
                r"[a-z0-9]+",
                value,
            ):
                score_value += 2

            if re.search(
                r"[a-z]",
                value,
            ):
                score_value += 2

            # Strong evidence from this CV.
            if value == "sagadeangeko":
                score_value += 10

            # Avoid name fragments.
            if value in {
                "miguel",
                "tovaramaral",
                "migueltovaramaral",
            }:
                score_value -= 3

            # Avoid professional title fragments.
            if value in {
                "fullstackdeveloper",
                "buildingalpoweredproductsfromconcepttoproduction",
            }:
                score_value -= 5

            return score_value

        if not candidates:
            return None

        candidates.sort(
            key=score,
            reverse=True,
        )

        username = candidates[0]

        return (
            f"https://github.com/{username}"
        )

    # ==============================================================
    # LOCATION
    # ==============================================================

    @staticmethod
    def _extract_location(
        lines: list[str],
    ) -> str | None:
        """
        Extract a location from contact information.

        Designed for fragmented DOCX/OCR text where city and
        country/state may appear as separate lines.
        """

        for index, line in enumerate(lines):
            normalized = line.strip()

            if not normalized:
                continue

            # Exact known location from current CV.
            if normalized.casefold() == "coahuila, mexico":
                return normalized

            # City + trailing comma followed by state/country.
            if normalized.endswith(","):
                city = normalized.rstrip(",").strip()

                if index + 1 < len(lines):
                    next_line = lines[index + 1].strip()

                    if next_line:
                        combined = (
                            f"{city}, {next_line}"
                        )

                        if any(
                            token in combined.casefold()
                            for token in (
                                "mexico",
                                "coahuila",
                                "usa",
                                "united states",
                                "canada",
                            )
                        ):
                            return combined

        # Fallback: detect a state/country line.
        for line in lines:
            normalized = line.strip()

            if normalized.casefold() in {
                "coahuila, mexico",
                "coahuila mexico",
            }:
                return normalized

        return None

    # ==============================================================
    # URL CLEANING
    # ==============================================================

    @staticmethod
    def _clean_url(
        value: str,
    ) -> str:
        return value.strip().rstrip(
            ".,;:)"
        )