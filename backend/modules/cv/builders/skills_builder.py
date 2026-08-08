from __future__ import annotations

import re
from typing import List

from backend.modules.cv.builders.base_builder import BaseBuilder, BuildResult
from backend.modules.cv.models.cv_skill import CVSkill


class SkillsBuilder(BaseBuilder[List[CVSkill]]):
    """
    Build structured technical skills from semi-structured CV text.

    The builder is intentionally conservative.

    It extracts actual skills such as:

        Flutter
        Python
        Dart
        REST APIs
        JavaScript
        SQLite
        Git
        GitHub
        Cloudflare
        AI Agents
        Generative AI
        Software Architecture
        API Integration
        Document Processing

    It avoids treating project names, narrative sentences, section headers,
    or descriptive CV content as skills.

    The implementation is deterministic and does not require external
    services or machine-learning models.
    """

    # ============================================================
    # SECTION HEADERS
    # ============================================================

    _SECTION_HEADERS = {
        "coretechnologies",
        "coretech",
        "skills",
        "habilidades",
        "technologies",
        "tecnologias",
        "technology",
        "tools",
        "herramientas",
        "liaecosystem",
        "ecosistema",
        "frameworks",
        "softskills",
        "hardskills",
        "competencias",
        "aiskillset",
        "aitoolkit",
        "aitoolset",
        "toolkit",
    }

    # ============================================================
    # NON-SKILL / PROJECT TERMS
    # ============================================================

    _EXCLUDED_EXACT = {
        "lia-tech",
        "lia employx",
        "lia staylo",
        "lia publish",
        "narrative engine",
    }

    _EXCLUDED_PREFIXES = (
        "lia-",
        "lia ",
    )

    _NON_SKILL_PHRASES = (
        "building modern",
        "building full stack",
        "building ai-powered",
        "designing apis",
        "designing modern",
        "integrated generative",
        "implemented apis",
        "managed deployments",
        "designed the complete",
        "transform traditional",
        "accelerate software development",
        "solve real-world problems",
        "professional summary",
        "featured experience",
        "key achievements",
        "full stack developer",
    )

    # ============================================================
    # KNOWN SKILL NORMALIZATION
    # ============================================================

    _KNOWN_SKILLS = {
        "flutter": "Flutter",
        "python": "Python",
        "dart": "Dart",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "sqlite": "SQLite",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "firebase": "Firebase",
        "git": "Git",
        "github": "GitHub",
        "gitlab": "GitLab",
        "cloudflare": "Cloudflare",
        "rest api": "REST APIs",
        "rest apis": "REST APIs",
        "api": "API Integration",
        "api integration": "API Integration",
        "document processing": "Document Processing",
        "ai agents": "AI Agents",
        "generative ai": "Generative AI",
        "artificial intelligence": "Artificial Intelligence",
        "software architecture": "Software Architecture",
        "prompt engineering": "Prompt Engineering",
        "comfyui": "ComfyUI",
        "stable diffusion": "Stable Diffusion",
        "chatgpt": "ChatGPT",
        "github copilot": "GitHub Copilot",
        "google ai studio": "Google AI Studio",
        "ai-assisted development": "AI-Assisted Development",
        "web": "Web Development",
        "frontend": "Frontend",
        "backend": "Backend",
        "flutter web": "Flutter Web",
    }

    # ============================================================
    # BUILD
    # ============================================================

    def build(
        self,
        text: str,
    ) -> BuildResult[List[CVSkill]]:
        """
        Build structured skills from CV section text.
        """

        warnings: list[str] = []

        if not text or not text.strip():
            warnings.append("Sección de habilidades vacía.")

            return BuildResult(
                data=[],
                confidence=0.0,
                warnings=warnings,
            )

        normalized = self._normalize_text(text)

        candidates = self._extract_candidates(normalized)

        skills: list[CVSkill] = []

        seen: set[str] = set()

        for candidate in candidates:
            skill = self._normalize_skill(candidate)

            if not skill:
                continue

            if self._is_excluded(skill):
                continue

            if self._is_narrative(skill):
                continue

            if not self._looks_like_skill(skill):
                continue

            key = skill.casefold()

            if key in seen:
                continue

            seen.add(key)

            skills.append(
                CVSkill(
                    name=skill,
                    category=self._categorize(skill),
                    source="Skills",
                )
            )

        if not skills:
            warnings.append(
                "No se extrajeron habilidades reconocibles."
            )

            return BuildResult(
                data=[],
                confidence=0.0,
                warnings=warnings,
            )

        return BuildResult(
            data=skills,
            confidence=95.0,
            warnings=warnings,
        )

    # ============================================================
    # NORMALIZATION
    # ============================================================

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:
        """
        Normalize extracted text while preserving line boundaries.
        """

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        text = text.replace("\u200b", "")
        text = text.replace("\u200c", "")
        text = text.replace("\u200d", "")
        text = text.replace("\ufeff", "")

        text = text.replace("\\:", ":")

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

    # ============================================================
    # CANDIDATE EXTRACTION
    # ============================================================

    def _extract_candidates(
        self,
        text: str,
    ) -> list[str]:
        """
        Extract candidate skill strings.

        Handles:

            one skill per line
            bullet lists
            comma-separated lists
            middle-dot separated lists
            "Technologies: ..."
        """

        candidates: list[str] = []

        for raw_line in text.splitlines():
            line = self._clean_line(raw_line)

            if not line:
                continue

            # ----------------------------------------------------
            # Remove section headers.
            # ----------------------------------------------------

            if self._is_header(line):
                continue

            # ----------------------------------------------------
            # Technologies: Flutter · Dart · Python ...
            # ----------------------------------------------------

            technologies_match = re.match(
                r"^technologies\s*:\s*(.+)$",
                line,
                re.IGNORECASE,
            )

            if technologies_match:
                candidates.extend(
                    self._split_skill_list(
                        technologies_match.group(1)
                    )
                )
                continue

            # ----------------------------------------------------
            # A line containing obvious list separators.
            # ----------------------------------------------------

            if any(
                separator in line
                for separator in (
                    ",",
                    "·",
                    "•",
                    "✓",
                    "✔",
                    "►",
                    "▪",
                    "◆",
                )
            ):
                candidates.extend(
                    self._split_skill_list(line)
                )
                continue

            # ----------------------------------------------------
            # Plain single candidate.
            # ----------------------------------------------------

            candidates.append(line)

        return candidates

    def _split_skill_list(
        self,
        value: str,
    ) -> list[str]:
        """
        Split a skill list while preserving multi-word skills.
        """

        value = re.sub(
            r"^[^A-Za-z0-9]+",
            "",
            value,
        )

        parts = re.split(
            r"[,\u00b7•✓✔►▪◆]+",
            value,
        )

        return [
            self._clean_line(part)
            for part in parts
            if self._clean_line(part)
        ]

    # ============================================================
    # SKILL NORMALIZATION
    # ============================================================

    def _normalize_skill(
        self,
        value: str,
    ) -> str:
        """
        Normalize a candidate against known skills.
        """

        value = self._clean_line(value)

        if not value:
            return ""

        # Remove trailing punctuation.
        value = re.sub(
            r"[.;:]+$",
            "",
            value,
        ).strip()

        key = value.casefold()

        # Exact known skill.
        known = self._KNOWN_SKILLS.get(key)

        if known:
            return known

        # --------------------------------------------------------
        # Known skill embedded in noisy text.
        # --------------------------------------------------------

        for known_key, canonical in sorted(
            self._KNOWN_SKILLS.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            if key == known_key:
                return canonical

        return value

    # ============================================================
    # FILTERS
    # ============================================================

    def _is_excluded(
        self,
        skill: str,
    ) -> bool:
        """
        Reject project names and ecosystem products.
        """

        normalized = skill.casefold().strip()

        if normalized in self._EXCLUDED_EXACT:
            return True

        for prefix in self._EXCLUDED_PREFIXES:
            if normalized.startswith(prefix):
                return True

        return False

    def _is_narrative(
        self,
        skill: str,
    ) -> bool:
        """
        Reject prose accidentally extracted from CV layout.
        """

        normalized = skill.casefold()

        for phrase in self._NON_SKILL_PHRASES:
            if phrase in normalized:
                return True

        # A skill should not normally look like a sentence.
        word_count = len(skill.split())

        if word_count > 7:
            return True

        # Sentence-like punctuation.
        if any(
            punctuation in skill
            for punctuation in (
                "!",
                "?",
                "✓",
                "✔",
            )
        ):
            return True

        return False

    def _looks_like_skill(
        self,
        skill: str,
    ) -> bool:
        """
        Conservative heuristic for skill-like values.
        """

        if not skill:
            return False

        normalized = skill.casefold().strip()

        # Exact known skill is always accepted.
        if normalized in self._KNOWN_SKILLS:
            return True

        if skill in self._KNOWN_SKILLS.values():
            return True

        # --------------------------------------------------------
        # Common technical indicators.
        # --------------------------------------------------------

        technical_terms = (
            "api",
            "apis",
            "ai",
            "sdk",
            "sql",
            "cloud",
            "git",
            "python",
            "dart",
            "flutter",
            "javascript",
            "typescript",
            "firebase",
            "database",
            "backend",
            "frontend",
            "architecture",
            "development",
            "processing",
            "integration",
            "automation",
            "engineering",
            "framework",
            "docker",
            "linux",
            "aws",
            "azure",
            "gcp",
        )

        if any(
            term in normalized
            for term in technical_terms
        ):
            return True

        # --------------------------------------------------------
        # Reject obvious prose.
        # --------------------------------------------------------

        if re.search(
            r"\b(the|and|with|from|into|that|this|using|to|for)\b",
            normalized,
        ):
            return False

        return False

    # ============================================================
    # CATEGORIZATION
    # ============================================================

    @staticmethod
    def _categorize(
        skill: str,
    ) -> str:
        """
        Assign a lightweight technical category.
        """

        normalized = skill.casefold()

        if normalized in {
            "python",
            "dart",
            "javascript",
            "typescript",
        }:
            return "Programming Language"

        if normalized in {
            "flutter",
            "flutter web",
        }:
            return "Framework"

        if normalized in {
            "sqlite",
            "mysql",
            "postgresql",
            "firebase",
        }:
            return "Database"

        if normalized in {
            "git",
            "github",
            "gitlab",
        }:
            return "Version Control"

        if normalized in {
            "cloudflare",
            "aws",
            "azure",
            "gcp",
        }:
            return "Cloud"

        if "ai" in normalized:
            return "Artificial Intelligence"

        if normalized in {
            "rest apis",
            "api integration",
            "document processing",
        }:
            return "Backend"

        if normalized in {
            "software architecture",
            "prompt engineering",
            "ai-assisted development",
        }:
            return "Architecture & AI"

        return "Technical"

    # ============================================================
    # HELPERS
    # ============================================================

    @classmethod
    def _is_header(
        cls,
        value: str,
    ) -> bool:
        """
        Detect a skills subsection header.
        """

        normalized = re.sub(
            r"[^a-z]",
            "",
            value.casefold(),
        )

        return normalized in cls._SECTION_HEADERS

    @staticmethod
    def _clean_line(
        value: str,
    ) -> str:
        """
        Clean one extracted line.
        """

        if not value:
            return ""

        value = value.strip()

        value = re.sub(
            r"^[•►▪◆★⭐✓✔\-\–—:]+",
            "",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()