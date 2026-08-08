"""Build structured language entries from CV section text."""

from __future__ import annotations

import re
from typing import List

from backend.modules.cv.builders.base_builder import BaseBuilder, BuildResult
from backend.modules.cv.models.cv_language import CVLanguage


class LanguagesBuilder(BaseBuilder[List[CVLanguage]]):
    """
    Build structured language records from semi-structured CV text.

    Handles common extracted formats such as:

        Spanish: Native
        English: B2 — Upper-Intermediate

    and merged DOCX text such as:

        Spanish: NativeEnglish: B2 — Upper-Intermediate

    The parser is intentionally deterministic and conservative.
    """

    _HEADERS = {
        "languages",
        "language",
        "idiomas",
        "languageskills",
        "habilidadeslinguisticas",
        "habilidadeslingüísticas",
    }

    _LANGUAGE_NAMES = {
        "spanish",
        "español",
        "espanol",
        "english",
        "inglés",
        "ingles",
        "french",
        "français",
        "frances",
        "german",
        "alemán",
        "aleman",
        "italian",
        "italiano",
        "portuguese",
        "português",
        "portugues",
        "chinese",
        "mandarin",
        "japanese",
        "japonés",
        "japones",
        "korean",
        "coreano",
        "russian",
        "ruso",
        "arabic",
        "árabe",
        "arabe",
    }

    _LEVEL_PATTERN = (
        r"(?:"
        r"Native"
        r"|Fluent"
        r"|Basic"
        r"|Elementary"
        r"|Intermediate"
        r"|Advanced"
        r"|Professional"
        r"|Conversational"
        r"|Upper[- ]Intermediate"
        r"|Lower[- ]Intermediate"
        r"|Beginner"
        r"|[ABC][12]"
        r"(?:\s*[—–-]\s*"
        r"(?:Upper[- ]Intermediate|"
        r"Lower[- ]Intermediate|"
        r"Intermediate|"
        r"Advanced|"
        r"Basic|"
        r"Elementary|"
        r"Fluent|"
        r"Native)"
        r")?"
        r")"
    )

    def build(
        self,
        text: str,
    ) -> BuildResult[List[CVLanguage]]:
        """
        Build structured language entries.
        """

        warnings: list[str] = []

        if not text or not text.strip():
            warnings.append("Sección de idiomas vacía.")

            return BuildResult(
                data=[],
                confidence=0.0,
                warnings=warnings,
            )

        normalized = self._normalize_text(text)

        lines = self._expand_merged_languages(normalized)

        languages: list[CVLanguage] = []
        seen: set[tuple[str, str]] = set()

        for raw_line in lines:
            line = self._clean_line(raw_line)

            if not line:
                continue

            if self._is_header(line):
                continue

            parsed_entries = self._parse_line(line)

            for language_name, level in parsed_entries:
                language_name = self._clean_value(language_name)
                level = self._clean_value(level)

                if not language_name:
                    continue

                # Reject OCR fragments such as "S".
                if not self._looks_like_language(language_name):
                    continue

                key = (
                    language_name.casefold(),
                    level.casefold(),
                )

                if key in seen:
                    continue

                seen.add(key)

                languages.append(
                    CVLanguage(
                        name=language_name,
                        level=level or None,
                    )
                )

        if not languages:
            warnings.append(
                "No se pudieron identificar idiomas válidos "
                "en la sección."
            )

            return BuildResult(
                data=[],
                confidence=0.0,
                warnings=warnings,
            )

        return BuildResult(
            data=languages,
            confidence=100.0,
            warnings=warnings,
        )

    # ============================================================
    # NORMALIZATION
    # ============================================================

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize extracted text while preserving line boundaries.
        """

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        text = text.replace("\u200b", "")
        text = text.replace("\u200c", "")
        text = text.replace("\u200d", "")
        text = text.replace("\ufeff", "")

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    # ============================================================
    # MERGED LANGUAGE ENTRIES
    # ============================================================

    def _expand_merged_languages(
        self,
        text: str,
    ) -> list[str]:
        """
        Split merged language entries.

        Example:

            Spanish: NativeEnglish: B2 — Upper-Intermediate

        becomes:

            Spanish: Native
            English: B2 — Upper-Intermediate

        Uses a forward-looking regex and therefore avoids
        variable-length look-behind, which is unsupported by
        Python's regular expression engine.
        """

        expanded: list[str] = []

        pattern = re.compile(
            rf"({self._LEVEL_PATTERN})"
            rf"(?=(?:Spanish|Español|English|Inglés|"
            rf"French|Français|German|Deutsch|Italian|Italiano|"
            rf"Portuguese|Português|Chinese|Mandarin|Japanese|"
            rf"Korean|Russian|Arabic)\b)",
            re.IGNORECASE,
        )

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            pieces: list[str] = []
            last = 0

            for match in pattern.finditer(line):
                end = match.end()

                pieces.append(
                    line[last:end]
                )

                last = end

            pieces.append(line[last:])

            for piece in pieces:
                piece = piece.strip()

                if piece:
                    expanded.append(piece)

        return expanded

    # ============================================================
    # LINE PARSING
    # ============================================================

    def _parse_line(
        self,
        line: str,
    ) -> list[tuple[str, str]]:
        """
        Parse a single language line.

        Supported forms:

            Spanish: Native
            English - B2
            English — B2 — Upper-Intermediate
        """

        results: list[tuple[str, str]] = []

        # --------------------------------------------------------
        # Standard colon format
        # --------------------------------------------------------

        if ":" in line:
            name, level = line.split(":", 1)

            name = self._clean_value(name)
            level = self._clean_value(level)

            if self._looks_like_language(name):
                results.append((name, level))

                return results

        # --------------------------------------------------------
        # Dash format
        # --------------------------------------------------------

        match = re.match(
            rf"^(?P<name>[A-Za-zÀ-ÿ ]+?)"
            rf"\s*[-–—]\s*"
            rf"(?P<level>{self._LEVEL_PATTERN})"
            rf"(?:\s*[-–—]\s*(?P<extra>.+))?$",
            line,
            re.IGNORECASE,
        )

        if match:
            name = self._clean_value(
                match.group("name")
            )

            level = self._clean_value(
                match.group("level")
            )

            extra = self._clean_value(
                match.group("extra") or ""
            )

            if extra:
                level = f"{level} — {extra}"

            if self._looks_like_language(name):
                results.append((name, level))

                return results

        # --------------------------------------------------------
        # Bare language name
        # --------------------------------------------------------

        if self._looks_like_language(line):
            results.append(
                (
                    self._clean_value(line),
                    "",
                )
            )

        return results

    # ============================================================
    # DETECTION
    # ============================================================

    @classmethod
    def _normalize_header(cls, value: str) -> str:
        """
        Normalize a header for comparison.
        """

        value = value.casefold()

        replacements = str.maketrans(
            "áéíóúü",
            "aeiouu",
        )

        value = value.translate(replacements)

        return re.sub(
            r"[^a-z]",
            "",
            value,
        )

    @classmethod
    def _is_header(cls, value: str) -> bool:
        """
        Determine whether a line is a language section header.
        """

        normalized = cls._normalize_header(value)

        normalized_headers = {
            cls._normalize_header(header)
            for header in cls._HEADERS
        }

        return normalized in normalized_headers

    @classmethod
    def _looks_like_language(
        cls,
        value: str,
    ) -> bool:
        """
        Determine whether a string represents a known language.

        This intentionally rejects OCR fragments such as "S".
        """

        clean = cls._clean_value(value)

        if not clean:
            return False

        normalized = cls._normalize_header(clean)

        normalized_languages = {
            cls._normalize_header(name)
            for name in cls._LANGUAGE_NAMES
        }

        if normalized in normalized_languages:
            return True

        # Reject very short OCR fragments.
        if len(clean) < 3:
            return False

        # At this stage we intentionally remain conservative.
        # Unknown language names are not accepted automatically.
        return False

    # ============================================================
    # CLEANING
    # ============================================================

    @staticmethod
    def _clean_line(value: str) -> str:
        """
        Remove decorative prefixes and normalize whitespace.
        """

        value = value.strip()

        value = re.sub(
            r"^[^A-Za-zÀ-ÿ0-9]+",
            "",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    @staticmethod
    def _clean_value(value: str) -> str:
        """
        Clean a parsed language value.
        """

        if not value:
            return ""

        value = value.strip()

        value = re.sub(
            r"^[^A-Za-zÀ-ÿ0-9]+",
            "",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()