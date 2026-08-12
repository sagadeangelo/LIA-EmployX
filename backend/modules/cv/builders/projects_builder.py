"""
LIA EmployX
Projects Builder
============================================================

Construye una lista estructurada de proyectos a partir de la
sección "projects" detectada por CVSectionSplitter.

Principios
----------
- Determinista.
- Conservador.
- No inventa proyectos.
- No usa IA.
- No convierte tecnologías o habilidades en proyectos.
- Soporta listas con bullets.
- Soporta proyectos separados por saltos de línea.
- Elimina duplicados.
- Ignora encabezados conocidos.
- Mantiene el orden original del CV.
"""

from __future__ import annotations

import re

from backend.modules.cv.builders.base_builder import (
    BaseBuilder,
    BuildResult,
)


class ProjectsBuilder(BaseBuilder[list[str]]):
    """
    Builds a deterministic list of project names.

    The current canonical CVDocument contract stores projects as:

        list[str]

    Therefore this builder intentionally returns project names
    instead of introducing a new domain model prematurely.
    """

    # ==========================================================
    # CONSTANTS
    # ==========================================================

    SECTION_HEADERS = {
        "projects",
        "project",
        "proyectos",
        "proyecto",
        "personalprojects",
        "professionalprojects",
        "selectedprojects",
        "featuredprojects",
    }

    NOISE_HEADERS = {
        "technologies",
        "technology",
        "tecnologias",
        "tecnologia",
        "skills",
        "skill",
        "habilidades",
        "tools",
        "herramientas",
        "portfolio",
        "githubportfolio",
    }

    BULLET_PREFIX = re.compile(
        r"""
        ^\s*
        (?:
            [-•●▪◦*✓✔➜➤►]
            |
            \d+[\.\)]
            |
            [a-zA-Z][\.\)]
        )
        \s*
        """,
        re.VERBOSE,
    )

    WHITESPACE_PATTERN = re.compile(
        r"\s+"
    )

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def build(
        self,
        text: str,
    ) -> BuildResult[list[str]]:
        """
        Build project names from extracted section text.

        Args:
            text:
                Raw text belonging to the projects section.

        Returns:
            BuildResult containing:

                data:
                    list[str]

                confidence:
                    deterministic confidence percentage

                warnings:
                    non-fatal extraction warnings
        """

        warnings: list[str] = []

        if not text or not text.strip():
            warnings.append(
                "Sección de proyectos vacía."
            )

            return BuildResult(
                data=[],
                confidence=0.0,
                warnings=warnings,
            )

        lines = self._prepare_lines(text)

        if not lines:
            warnings.append(
                "No se encontraron líneas válidas de proyectos."
            )

            return BuildResult(
                data=[],
                confidence=0.0,
                warnings=warnings,
            )

        projects = self._extract_projects(lines)

        if not projects:
            warnings.append(
                "No se pudieron identificar proyectos."
            )

            return BuildResult(
                data=[],
                confidence=25.0,
                warnings=warnings,
            )

        confidence = self._calculate_confidence(
            projects
        )

        return BuildResult(
            data=projects,
            confidence=confidence,
            warnings=warnings,
        )

    # ==========================================================
    # PREPARATION
    # ==========================================================

    def _prepare_lines(
        self,
        text: str,
    ) -> list[str]:
        """
        Normalize raw project text into clean candidate lines.
        """

        normalized = (
            text
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )

        lines: list[str] = []

        for raw_line in normalized.split("\n"):
            line = self._clean_line(raw_line)

            if not line:
                continue

            lines.append(line)

        return lines

    @classmethod
    def _clean_line(
        cls,
        line: str,
    ) -> str:
        """
        Remove bullets and normalize whitespace.
        """

        value = line.strip()

        value = cls.BULLET_PREFIX.sub(
            "",
            value,
        )

        value = cls.WHITESPACE_PATTERN.sub(
            " ",
            value,
        )

        return value.strip()

    # ==========================================================
    # PROJECT EXTRACTION
    # ==========================================================

    def _extract_projects(
        self,
        lines: list[str],
    ) -> list[str]:
        """
        Extract project names while filtering section noise.
        """

        projects: list[str] = []

        for line in lines:
            normalized = self._normalize_match(
                line
            )

            # --------------------------------------------------
            # Ignore section headers.
            # --------------------------------------------------

            if normalized in self.SECTION_HEADERS:
                continue

            if normalized in self.NOISE_HEADERS:
                continue

            # --------------------------------------------------
            # Ignore empty / punctuation-only fragments.
            # --------------------------------------------------

            if not self._contains_meaningful_text(
                line
            ):
                continue

            # --------------------------------------------------
            # Ignore obvious technology lines.
            # --------------------------------------------------

            if self._looks_like_technology_list(
                line
            ):
                continue

            # --------------------------------------------------
            # Ignore URLs.
            # --------------------------------------------------

            if self._looks_like_url(line):
                continue

            # --------------------------------------------------
            # Ignore email addresses.
            # --------------------------------------------------

            if "@" in line:
                continue

            # --------------------------------------------------
            # Ignore very long descriptive paragraphs.
            #
            # A project name should normally be concise.
            # --------------------------------------------------

            if len(line) > 140:
                continue

            # --------------------------------------------------
            # Normalize project name.
            # --------------------------------------------------

            project = self._normalize_project_name(
                line
            )

            if not project:
                continue

            projects.append(project)

        return self._deduplicate(projects)

    # ==========================================================
    # PROJECT NAME NORMALIZATION
    # ==========================================================

    @staticmethod
    def _normalize_project_name(
        value: str,
    ) -> str:
        """
        Normalize a project name without destroying its
        original capitalization.
        """

        value = value.strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        value = value.strip(
            " \t\r\n-–—|:;,"
        )

        return value

    # ==========================================================
    # FILTERS
    # ==========================================================

    @staticmethod
    def _contains_meaningful_text(
        value: str,
    ) -> bool:
        return bool(
            re.search(
                r"[A-Za-zÀ-ÿ0-9]",
                value,
            )
        )

    @staticmethod
    def _looks_like_url(
        value: str,
    ) -> bool:
        normalized = value.casefold()

        return (
            normalized.startswith(
                "http://"
            )
            or normalized.startswith(
                "https://"
            )
            or normalized.startswith(
                "www."
            )
            or "github.com/" in normalized
            or "linkedin.com/" in normalized
        )

    @staticmethod
    def _looks_like_technology_list(
        value: str,
    ) -> bool:
        """
        Detect lines that are clearly technology inventories
        rather than projects.
        """

        normalized = value.casefold()

        technology_tokens = {
            "flutter",
            "python",
            "dart",
            "javascript",
            "typescript",
            "sqlite",
            "github",
            "cloudflare",
            "firebase",
            "rest apis",
            "api integration",
            "generative ai",
            "ai agents",
            "software architecture",
            "document processing",
            "stable diffusion",
            "comfyui",
            "chatgpt",
            "github copilot",
            "google ai studio",
            "prompt engineering",
            "ai-assisted development",
        }

        if normalized in technology_tokens:
            return True

        separators = (
            "·",
            "|",
            ",",
        )

        if any(
            separator in value
            for separator in separators
        ):
            tokens = [
                token.strip().casefold()
                for token in re.split(
                    r"[·|,]",
                    value,
                )
                if token.strip()
            ]

            if tokens and all(
                token in technology_tokens
                for token in tokens
            ):
                return True

        return False

    # ==========================================================
    # DEDUPLICATION
    # ==========================================================

    def _deduplicate(
        self,
        projects: list[str],
    ) -> list[str]:
        """
        Deduplicate projects while preserving CV order.
        """

        result: list[str] = []
        seen: set[str] = set()

        for project in projects:
            key = self._normalize_match(
                project
            )

            if not key:
                continue

            if key in seen:
                continue

            seen.add(key)
            result.append(project)

        return result

    # ==========================================================
    # NORMALIZATION FOR COMPARISON
    # ==========================================================

    @staticmethod
    def _normalize_match(
        value: str,
    ) -> str:
        """
        Normalize a value for deterministic comparisons.
        """

        value = value.casefold()

        replacements = str.maketrans(
            {
                "á": "a",
                "é": "e",
                "í": "i",
                "ó": "o",
                "ú": "u",
                "ü": "u",
                "ñ": "n",
            }
        )

        value = value.translate(
            replacements
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        value = re.sub(
            r"[^a-z0-9\s_-]",
            "",
            value,
        )

        return value.strip()

    # ==========================================================
    # CONFIDENCE
    # ==========================================================

    @staticmethod
    def _calculate_confidence(
        projects: list[str],
    ) -> float:
        """
        Calculate deterministic confidence.

        Confidence is based on the fact that projects were
        actually extracted and survived the conservative
        filters.
        """

        if not projects:
            return 0.0

        confidence = 100.0

        # Extremely long lists are slightly less certain.
        if len(projects) > 15:
            confidence -= 5.0

        if len(projects) > 25:
            confidence -= 10.0

        return max(
            0.0,
            min(
                100.0,
                confidence,
            ),
        )