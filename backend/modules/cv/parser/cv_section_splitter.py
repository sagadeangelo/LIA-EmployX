"""
LIA EmployX
CV Section Splitter
===================

Divide el texto plano de un CV en secciones semánticas.

Responsabilidades
-----------------
- Detectar encabezados reales.
- Detectar encabezados pegados al contenido.
- Evitar falsos positivos.
- Mantener separadas las secciones principales.
- Deduplicar bloques repetidos.
- Limpiar artefactos de extracción DOCX.
- Recuperar información personal desplazada.
- Recuperar información personal fragmentada.
- Evitar "Technologies" como falso encabezado dentro de Experience.
- Soportar CVs con columnas/textboxes cuya estructura visual se pierde
  durante la extracción.
- No ejecutar OCR.
- No construir modelos de dominio.

La salida de este módulo es:

    dict[str, SectionResult]

Los Builders son responsables de convertir cada sección
en modelos de dominio.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Final, Literal


# ============================================================================
# TYPES
# ============================================================================

SectionKey = str

DetectionMethod = Literal[
    "header",
    "structural",
    "recovery",
    "none",
]


@dataclass(slots=True)
class SectionResult:
    text: str
    confidence: float
    detection: DetectionMethod


SectionMap = dict[SectionKey, SectionResult]


# ============================================================================
# EMPTY CONTRACT
# ============================================================================

_EMPTY_SECTIONS: Final[dict[SectionKey, str]] = {
    "personal_info": "",
    "summary": "",
    "experience": "",
    "education": "",
    "skills": "",
    "languages": "",
    "certifications": "",
    "projects": "",
}


# ============================================================================
# SECTION HEADERS
# ============================================================================

_SECTION_HEADERS: Final[
    dict[SectionKey, list[str]]
] = {
    "summary": [
        "perfil profesional",
        "professional profile",
        "professional summary",
        "resumen profesional",
        "career objective",
        "objetivo profesional",
        "about me",
        "about",
        "summary",
        "resumen",
        "perfil",
        "objetivo",
    ],

    "experience": [
        "experiencia laboral",
        "experiencia profesional",
        "professional experience",
        "work experience",
        "employment history",
        "career history",
        "featured experience",
        "experiencia",
        "empleo",
        "trayectoria profesional",
        "trayectoria",
    ],

    "education": [
        "formacion academica",
        "formacion",
        "educacion",
        "estudios",
        "academic background",
        "academic education",
        "education",
        "academic",
    ],

    "skills": [
        "habilidades tecnicas",
        "habilidades clave",
        "habilidades",
        "competencias clave",
        "competencias",
        "aptitudes",
        "technical skills",
        "core competencies",
        "core skills",
        "competencies",
        "strengths",
        "skills",
        "core technologies",
        "ai toolkit",
        "ai tools",
        "artificial intelligence toolkit",
        "technical toolkit",
        "technology stack",
        "tech stack",
        "herramientas de ia",
        "herramientas ia",
        "tecnologias y sistemas ia utilizados",
        "tecnologias",
        "technologies",
        "herramientas y plataformas",
        "desarrollo y arquitectura",
    ],

    "languages": [
        "idiomas",
        "languages",
        "language",
    ],

    "certifications": [
        "certificaciones",
        "certificados",
        "certifications",
        "certification",
        "licenses",
        "licencias",
    ],

    "projects": [
        "proyectos personales",
        "proyectos",
        "projects",
        "project",
        "open source",
        "portafolio",
        "portfolio",
        "lia ecosystem",
        "lia tech ecosystem",
        "ecosistema lia",
    ],
}


# ============================================================================
# REGEX
# ============================================================================

_DECORATIVE_PREFIX_RE = re.compile(
    r"^[^A-Za-z0-9À-ÖØ-öø-ÿ]+"
)

_EMAIL_RE = re.compile(
    r"\b[A-Z0-9._%+\-]+"
    r"@"
    r"[A-Z0-9.\-]+"
    r"\.[A-Z]{2,}\b",
    re.IGNORECASE,
)

_PHONE_RE = re.compile(
    r"(?<!\d)"
    r"(?:\+\d{1,3}[\s.\-]?)?"
    r"(?:\(?\d{2,4}\)?[\s.\-]?)?"
    r"\d{3}[\s.\-]?"
    r"\d{3,4}"
    r"(?:[\s.\-]?\d{2,4})?"
    r"(?!\d)"
)

_LINKEDIN_RE = re.compile(
    r"\blinkedin\b",
    re.IGNORECASE,
)

_GITHUB_RE = re.compile(
    r"\bgithub\b",
    re.IGNORECASE,
)


# ============================================================================
# SIGNALS
# ============================================================================

_CONTACT_MARKERS: Final[tuple[str, ...]] = (
    "linkedin",
    "github",
    "portfolio",
    "email",
    "gmail",
    "hotmail",
    "outlook",
    "phone",
    "mobile",
    "tel",
    "telefono",
    "correo",
)

_TECH_MARKERS: Final[tuple[str, ...]] = (
    "python",
    "flutter",
    "react",
    "java",
    "javascript",
    "typescript",
    "node",
    "sql",
    "docker",
    "aws",
    "html",
    "css",
    "ai",
    "ia",
    "artificial intelligence",
    "inteligencia artificial",
    "chatgpt",
    "prompt",
)


_PROFILE_TITLE_MARKERS: Final[tuple[str, ...]] = (
    "developer",
    "engineer",
    "designer",
    "architect",
    "manager",
    "analyst",
    "consultant",
    "specialist",
    "founder",
    "director",
    "lead",
    "product manager",
    "product owner",
    "software developer",
    "software engineer",
    "full stack",
    "frontend",
    "backend",
    "desarrollador",
    "ingeniero",
    "diseñador",
    "arquitecto",
    "gerente",
    "analista",
    "consultor",
    "especialista",
    "fundador",
    "lider",
    "líder",
)


_LOCATION_MARKERS: Final[tuple[str, ...]] = (
    "mexico",
    "méxico",
    "coahuila",
    "piedras negras",
    "monterrey",
    "guadalajara",
    "saltillo",
    "usa",
    "united states",
    "united states of america",
    "texas",
    "utah",
)


# ============================================================================
# CLASS
# ============================================================================


class CVSectionSplitter:
    """
    Divide un CV en secciones semánticas.

    La estrategia es deliberadamente conservadora:
    primero se detectan encabezados explícitos y después se intenta
    recuperar información personal desplazada por la extracción DOCX.
    """

    def __init__(self) -> None:
        self._patterns = self._compile_patterns()
        self._embedded_headers = (
            self._compile_embedded_headers()
        )

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def split(
        self,
        text: str,
    ) -> SectionMap:
        normalized = self._normalize(text)

        if not normalized:
            return self._empty_result()

        blocks = self._split_blocks(normalized)

        blocks = self._expand_embedded_headers(
            blocks
        )

        return self._build_sections(blocks)

    def process(
        self,
        text: str,
    ) -> SectionMap:
        sections = self.split(text)

        self.print_summary(sections)

        return sections

    def print_summary(
        self,
        sections: SectionMap,
    ) -> None:
        print()
        print("=" * 70)
        print("CV Sections")
        print("=" * 70)
        print()

        for key in _EMPTY_SECTIONS:
            result = sections.get(
                key,
                SectionResult(
                    "",
                    0.0,
                    "none",
                ),
            )

            print(
                f"  {key:<20}"
                f"{len(result.text):>6} caracteres "
                f"[{result.detection}]"
            )

        print()

    def debug(
        self,
        text: str,
    ) -> SectionMap:
        print()
        print("=" * 70)
        print("DEBUG — CV Section Splitter")
        print("=" * 70)

        normalized = self._normalize(text)

        blocks = self._split_blocks(
            normalized
        )

        expanded = self._expand_embedded_headers(
            blocks
        )

        detected = self._detect_boundaries(
            expanded
        )

        sections = self._build_sections(
            expanded
        )

        print()
        print(
            f"  Bloques originales: "
            f"{len(blocks)}"
        )

        print(
            f"  Bloques después de expansión: "
            f"{len(expanded)}"
        )

        print()
        print("  Límites detectados:")
        print()

        if not detected:
            print("    (ninguno)")

        for item in detected:
            header = item["text"].split(
                "\n",
                1,
            )[0]

            print(
                f"    bloque {item['index']:>4} "
                f"[{item['section']:<16}] "
                f"conf:{item['confidence']:.2f} "
                f"({item['detection']}) "
                f"{header[:60]}"
            )

        print()

        for key in _EMPTY_SECTIONS:
            result = sections[key]

            print("-" * 70)
            print(
                f"{key.upper()} "
                f"[{result.confidence:.2f} | "
                f"{result.detection}]"
            )
            print("-" * 70)

            if not result.text:
                print("(vacío)")
                print()
                continue

            lines = result.text.splitlines()

            for line in lines[:12]:
                print(
                    f"  {line}"
                )

            if len(lines) > 12:
                print("  ...")

            print()

        return sections

    # ========================================================================
    # NORMALIZATION
    # ========================================================================

    def _normalize(
        self,
        text: str,
    ) -> str:
        if not text:
            return ""

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        text = text.replace(
            "\t",
            " ",
        )

        # Eliminar caracteres de control.
        text = "".join(
            char
            for char in text
            if char == "\n"
            or not unicodedata.category(
                char
            ).startswith("Cc")
        )

        text = re.sub(
            r"[ ]{2,}",
            " ",
            text,
        )

        text = re.sub(
            r"\n[ ]+",
            "\n",
            text,
        )

        text = re.sub(
            r"[ ]+\n",
            "\n",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    def _split_blocks(
        self,
        text: str,
    ) -> list[str]:
        return [
            block.strip()
            for block in re.split(
                r"\n\s*\n",
                text,
            )
            if block.strip()
        ]

    # ========================================================================
    # MATCHING NORMALIZATION
    # ========================================================================

    @staticmethod
    def _normalize_for_matching(
        text: str,
    ) -> str:
        normalized = unicodedata.normalize(
            "NFD",
            text,
        )

        return "".join(
            char
            for char in normalized
            if unicodedata.category(
                char
            ) != "Mn"
        )

    @staticmethod
    def _semantic_key(
        text: str,
    ) -> str:
        return "".join(
            char.casefold()
            for char in text
            if char.isalnum()
        )

    # ========================================================================
    # PATTERNS
    # ========================================================================

    def _compile_patterns(
        self,
    ) -> dict[
        SectionKey,
        list[re.Pattern[str]],
    ]:
        compiled: dict[
            SectionKey,
            list[re.Pattern[str]],
        ] = {}

        for section, headers in (
            _SECTION_HEADERS.items()
        ):
            patterns: list[
                re.Pattern[str]
            ] = []

            for header in headers:
                normalized = (
                    self._normalize_for_matching(
                        header
                    )
                )

                escaped = r"\s+".join(
                    re.escape(word)
                    for word in normalized.split()
                )

                patterns.append(
                    re.compile(
                        rf"^[^A-Za-z0-9À-ÖØ-öø-ÿ]*"
                        rf"{escaped}"
                        rf"[^A-Za-z0-9À-ÖØ-öø-ÿ]*$",
                        re.IGNORECASE,
                    )
                )

            compiled[section] = patterns

        return compiled

    def _compile_embedded_headers(
        self,
    ) -> list[
        tuple[
            str,
            SectionKey,
            re.Pattern[str],
        ]
    ]:
        result: list[
            tuple[
                str,
                SectionKey,
                re.Pattern[str],
            ]
        ] = []

        for section, headers in (
            _SECTION_HEADERS.items()
        ):
            for header in headers:
                normalized = (
                    self._normalize_for_matching(
                        header
                    )
                )

                escaped_words = r"\s+".join(
                    re.escape(word)
                    for word in normalized.split()
                )

                result.append(
                    (
                        header,
                        section,
                        re.compile(
                            rf"^{escaped_words}",
                            re.IGNORECASE,
                        ),
                    )
                )

        result.sort(
            key=lambda item: len(item[0]),
            reverse=True,
        )

        return result

    # ========================================================================
    # EMBEDDED HEADERS
    # ========================================================================

    def _expand_embedded_headers(
        self,
        blocks: list[str],
    ) -> list[str]:
        expanded: list[str] = []

        for block in blocks:
            expanded.extend(
                self._split_leading_embedded_header(
                    block
                )
            )

        return [
            item.strip()
            for item in expanded
            if item.strip()
        ]

    def _split_leading_embedded_header(
        self,
        block: str,
    ) -> list[str]:
        working = block.strip()

        if not working:
            return []

        prefix_match = (
            _DECORATIVE_PREFIX_RE.match(
                working
            )
        )

        content_start = (
            prefix_match.end()
            if prefix_match
            else 0
        )

        candidate = working[
            content_start:
        ]

        normalized_candidate = (
            self._normalize_for_matching(
                candidate
            )
        )

        for (
            header,
            _section,
            pattern,
        ) in self._embedded_headers:

            match = pattern.match(
                normalized_candidate
            )

            if not match:
                continue

            header_length = len(header)

            if len(candidate) <= header_length:
                return [working]

            actual_header = candidate[
                :header_length
            ].strip()

            remaining = candidate[
                header_length:
            ].strip()

            if not remaining:
                return [working]

            return [
                actual_header,
                remaining,
            ]

        return [working]

    # ========================================================================
    # HEADER DETECTION
    # ========================================================================

    def _match_header(
        self,
        block: str,
    ) -> SectionKey | None:
        first_line = block.split(
            "\n",
            1,
        )[0].strip()

        normalized_line = (
            self._normalize_for_matching(
                first_line
            )
        )

        best_section: SectionKey | None = None
        best_length = 0

        for (
            section,
            patterns,
        ) in self._patterns.items():

            for index, pattern in enumerate(
                patterns
            ):
                if not pattern.fullmatch(
                    normalized_line
                ):
                    continue

                header_length = len(
                    _SECTION_HEADERS[
                        section
                    ][index]
                )

                if header_length > best_length:
                    best_length = header_length
                    best_section = section

        return best_section

    def _is_ignored_contextual_header(
        self,
        section: SectionKey,
        block_index: int,
        blocks: list[str],
    ) -> bool:
        normalized = (
            self._normalize_for_matching(
                blocks[block_index]
            )
            .casefold()
        )

        # Technologies dentro de Experience
        # NO debe abrir Skills.
        if normalized in ("technologies", "tecnologias"):
            previous = (
                self._detect_previous_real_sections(
                    block_index,
                    blocks,
                )
            )

            return (
                "experience"
                in previous
            )

        # Language aislado dentro de Experience
        # puede ser una etiqueta interna.
        if normalized == "language":
            previous = (
                self._detect_previous_real_sections(
                    block_index,
                    blocks,
                )
            )

            if (
                "experience" in previous
                and "languages"
                not in previous
            ):
                return True

        return False

    def _detect_previous_real_sections(
        self,
        block_index: int,
        blocks: list[str],
    ) -> set[SectionKey]:
        sections: set[
            SectionKey
        ] = set()

        for index in range(
            block_index
        ):
            section = self._match_header(
                blocks[index]
            )

            if section is not None:
                sections.add(
                    section
                )

        return sections

    # ========================================================================
    # STRUCTURAL DETECTION
    # ========================================================================

    def _detect_structural_boundary(
        self,
        block: str,
    ) -> SectionKey | None:
        normalized = (
            self._normalize_for_matching(
                block
            )
        )

        role_pattern = re.compile(
            r"\b("
            r"developer|"
            r"desarrollador|"
            r"engineer|"
            r"ingeniero|"
            r"manager|"
            r"gerente|"
            r"consultant|"
            r"consultor|"
            r"analyst|"
            r"analista|"
            r"architect|"
            r"arquitecto|"
            r"director|"
            r"coordinator|"
            r"coordinador|"
            r"designer|"
            r"diseñador|"
            r"specialist|"
            r"especialista|"
            r"lead|"
            r"lider|"
            r"founder|"
            r"full stack|"
            r"frontend|"
            r"backend"
            r")\b",
            re.IGNORECASE,
        )

        date_pattern = re.compile(
            r"\b(?:19|20)\d{2}\b"
            r"|"
            r"\bpresent\b"
            r"|"
            r"\bactualidad\b",
            re.IGNORECASE,
        )

        if (
            role_pattern.search(
                normalized
            )
            and date_pattern.search(
                normalized
            )
        ):
            return "experience"

        return None

    def _detect_boundaries(
        self,
        blocks: list[str],
    ) -> list[
        dict[str, Any]
    ]:
        found: list[
            dict[str, Any]
        ] = []

        for index, block in enumerate(
            blocks
        ):
            section = self._match_header(
                block
            )

            if section is not None:
                if self._is_ignored_contextual_header(
                    section,
                    index,
                    blocks,
                ):
                    continue

                found.append(
                    {
                        "index": index,
                        "section": section,
                        "confidence": 0.98,
                        "detection": "header",
                        "text": block,
                    }
                )

                continue

            structural = (
                self._detect_structural_boundary(
                    block
                )
            )

            if structural is not None:
                found.append(
                    {
                        "index": index,
                        "section": structural,
                        "confidence": 0.75,
                        "detection": "structural",
                        "text": block,
                    }
                )

        return found

    # ========================================================================
    # BUILD
    # ========================================================================

    def _build_sections(
        self,
        blocks: list[str],
    ) -> SectionMap:
        accumulator: dict[
            SectionKey,
            list[str],
        ] = {
            key: []
            for key in _EMPTY_SECTIONS
        }

        confidences: dict[
            SectionKey,
            float,
        ] = {}

        detections: dict[
            SectionKey,
            DetectionMethod,
        ] = {}

        detected = (
            self._detect_boundaries(
                blocks
            )
        )

        if not detected:
            accumulator[
                "personal_info"
            ] = list(blocks)

            self._recover_personal_info(
                accumulator,
                confidences,
                detections,
            )

            return self._join_sections(
                accumulator,
                confidences,
                detections,
            )

        first_index = detected[
            0
        ]["index"]

        accumulator[
            "personal_info"
        ] = blocks[
            :first_index
        ]

        for index, boundary in enumerate(
            detected
        ):
            section = boundary[
                "section"
            ]

            start = boundary[
                "index"
            ]

            if (
                index + 1
                < len(detected)
            ):
                end = detected[
                    index + 1
                ]["index"]
            else:
                end = len(blocks)

            content = blocks[
                start + 1:end
            ]

            if (
                section == "summary"
                and self._is_duplicate_summary(
                    detected,
                    index,
                )
            ):
                self._split_duplicate_summary_region(
                    content,
                    accumulator,
                )
            else:
                accumulator[
                    section
                ].extend(
                    content
                )

            confidence = float(
                boundary[
                    "confidence"
                ]
            )

            if confidence >= confidences.get(
                section,
                0.0,
            ):
                confidences[
                    section
                ] = confidence

                detections[
                    section
                ] = boundary[
                    "detection"
                ]

        # Deduplicar antes de recuperar.
        for section in accumulator:
            accumulator[
                section
            ] = (
                self._deduplicate_section_blocks(
                    accumulator[
                        section
                    ]
                )
            )

        # Educación puede contener una cabecera personal
        # por pérdida del layout del DOCX.
        self._remove_personal_profile_from_education(
            accumulator,
            confidences,
            detections,
        )

        # Recuperación global.
        self._recover_personal_info(
            accumulator,
            confidences,
            detections,
        )

        accumulator[
            "languages"
        ] = self._clean_languages_blocks(
            accumulator[
                "languages"
            ]
        )

        return self._join_sections(
            accumulator,
            confidences,
            detections,
        )

    # ========================================================================
    # EDUCATION CONTAMINATION
    # ========================================================================

    def _remove_personal_profile_from_education(
        self,
        accumulator: dict[
            SectionKey,
            list[str],
        ],
        confidences: dict[
            SectionKey,
            float,
        ],
        detections: dict[
            SectionKey,
            DetectionMethod,
        ],
    ) -> None:
        education_blocks = (
            accumulator.get(
                "education",
                [],
            )
        )

        if not education_blocks:
            return

        start = (
            self._find_profile_contamination_start(
                education_blocks
            )
        )

        if start is None:
            return

        contaminated = education_blocks[
            start:
        ]

        recovered = (
            self._recover_fragmented_contact(
                contaminated
            )
        )

        if recovered is None:
            return

        personal_text, remaining = (
            recovered
        )

        if not personal_text.strip():
            return

        accumulator[
            "education"
        ] = (
            education_blocks[:start]
            + remaining
        )

        accumulator[
            "personal_info"
        ].append(
            personal_text
        )

        confidences[
            "personal_info"
        ] = max(
            confidences.get(
                "personal_info",
                0.0,
            ),
            0.95,
        )

        detections[
            "personal_info"
        ] = "recovery"

    def _find_profile_contamination_start(
        self,
        blocks: list[str],
    ) -> int | None:
        if not blocks:
            return None

        for start_index, candidate in enumerate(
            blocks
        ):
            if not self._looks_like_name_line(
                candidate
            ):
                continue

            window = blocks[
                start_index:
                min(
                    len(blocks),
                    start_index + 25,
                )
            ]

            has_title = any(
                self._looks_like_profile_title(
                    value
                )
                for value in window
            )

            if not has_title:
                continue

            contact_signals = sum(
                1
                for value in window
                if self._is_contact_fragment(
                    value
                )
            )

            if contact_signals >= 2:
                return start_index

        return None

    # ========================================================================
    # DUPLICATE SUMMARY
    # ========================================================================

    def _is_duplicate_summary(
        self,
        detected: list[
            dict[str, Any]
        ],
        boundary_index: int,
    ) -> bool:
        current = detected[
            boundary_index
        ]

        if current[
            "section"
        ] != "summary":
            return False

        return any(
            item["section"]
            == "summary"
            for item in detected[
                :boundary_index
            ]
        )

    def _split_duplicate_summary_region(
        self,
        content: list[str],
        accumulator: dict[
            SectionKey,
            list[str],
        ],
    ) -> None:
        if not content:
            return

        start = (
            self._find_contact_block_start(
                content
            )
        )

        if start is None:
            accumulator[
                "summary"
            ].extend(
                content
            )
            return

        summary_part = content[
            :start
        ]

        contact_part = content[
            start:
        ]

        if summary_part:
            accumulator[
                "summary"
            ].extend(
                summary_part
            )

        recovered = (
            self._recover_fragmented_contact(
                contact_part
            )
        )

        if recovered is None:
            accumulator[
                "personal_info"
            ].extend(
                contact_part
            )
            return

        personal_text, remaining = (
            recovered
        )

        if personal_text:
            accumulator[
                "personal_info"
            ].append(
                personal_text
            )

        if remaining:
            accumulator[
                "summary"
            ].extend(
                remaining
            )

    def _find_contact_block_start(
        self,
        blocks: list[str],
    ) -> int | None:
        if not blocks:
            return None

        # Nombre completo o nombre partido.
        for index in range(
            len(blocks) - 1
        ):
            if not self._looks_like_name_line(
                blocks[index]
            ):
                continue

            if not self._looks_like_name_line(
                blocks[index + 1]
            ):
                continue

            window = blocks[
                index:
                min(
                    len(blocks),
                    index + 20,
                )
            ]

            signal_count = sum(
                1
                for candidate in window
                if self._is_contact_fragment(
                    candidate
                )
            )

            if signal_count >= 2:
                return index

        # Nombre en un único bloque.
        for index, block in enumerate(
            blocks
        ):
            if not self._looks_like_name_line(
                block
            ):
                continue

            window = blocks[
                index:
                min(
                    len(blocks),
                    index + 20,
                )
            ]

            signal_count = sum(
                1
                for candidate in window
                if self._is_contact_fragment(
                    candidate
                )
            )

            if signal_count >= 2:
                return index

        return None

    # ========================================================================
    # PERSONAL INFO RECOVERY
    # ========================================================================

    def _recover_personal_info(
        self,
        accumulator: dict[
            SectionKey,
            list[str],
        ],
        confidences: dict[
            SectionKey,
            float,
        ],
        detections: dict[
            SectionKey,
            DetectionMethod,
        ],
    ) -> None:
        """
        Recupera contacto desplazado desde cualquier sección.

        Esto es especialmente importante para DOCX con columnas,
        textboxes o elementos gráficos.

        Orden:

        1. Summary.
        2. Experience.
        3. Education.
        4. Skills.
        5. Languages.
        6. Certifications.
        7. Projects.
        8. Fallback de bloques individuales.
        """

        search_sections: tuple[
            SectionKey,
            ...
        ] = (
            "summary",
            "experience",
            "education",
            "skills",
            "languages",
            "certifications",
            "projects",
        )

        # ------------------------------------------------------------------
        # Si ya tenemos contacto fuerte, no mover más contenido.
        # ------------------------------------------------------------------

        existing = "\n".join(
            accumulator[
                "personal_info"
            ]
        )

        if (
            existing
            and self._region_has_enough_contact_signals(
                existing.splitlines()
            )
        ):
            confidences.setdefault(
                "personal_info",
                0.95,
            )

            detections.setdefault(
                "personal_info",
                "recovery",
            )

            return

        # ------------------------------------------------------------------
        # Intentar recuperar una cabecera completa.
        # ------------------------------------------------------------------

        for section_key in search_sections:
            blocks = accumulator.get(
                section_key,
                [],
            )

            if not blocks:
                continue

            recovered = (
                self._recover_fragmented_contact(
                    blocks
                )
            )

            if recovered is None:
                continue

            personal_text, remaining = (
                recovered
            )

            if not personal_text.strip():
                continue

            accumulator[
                "personal_info"
            ].append(
                personal_text
            )

            accumulator[
                section_key
            ] = remaining

            confidences[
                "personal_info"
            ] = 0.95

            detections[
                "personal_info"
            ] = "recovery"

            return

        # ------------------------------------------------------------------
        # Fallback: extraer únicamente bloques con contacto fuerte.
        # ------------------------------------------------------------------

        for section_key in search_sections:
            blocks = accumulator.get(
                section_key,
                [],
            )

            if not blocks:
                continue

            recovered_blocks: list[
                str
            ] = []

            remaining_blocks: list[
                str
            ] = []

            for block in blocks:
                if (
                    self._looks_like_personal_info(
                        block
                    )
                    and self._is_meaningful_contact_block(
                        block
                    )
                ):
                    recovered_blocks.append(
                        block
                    )
                else:
                    remaining_blocks.append(
                        block
                    )

            if not recovered_blocks:
                continue

            accumulator[
                "personal_info"
            ].append(
                "\n".join(
                    recovered_blocks
                )
            )

            accumulator[
                section_key
            ] = remaining_blocks

            confidences[
                "personal_info"
            ] = 0.90

            detections[
                "personal_info"
            ] = "recovery"

            return

    # ========================================================================
    # FRAGMENTED CONTACT RECOVERY
    # ========================================================================

    def _recover_fragmented_contact(
        self,
        blocks: list[str],
    ) -> tuple[
        str,
        list[str],
    ] | None:
        """
        Recupera una cabecera fragmentada.

        Ejemplo:

            MIGUEL
            TOVAR AMARAL
            Full Stack Developer
            linkedin
            github
            +52...
            email...

        También soporta un único bloque multilinea.
        """

        if not blocks:
            return None

        # ------------------------------------------------------------------
        # CASO 1: bloque multilinea.
        # ------------------------------------------------------------------

        for block_index, block in enumerate(
            blocks
        ):
            lines = [
                line.strip()
                for line in block.splitlines()
                if line.strip()
            ]

            if len(lines) < 2:
                continue

            signal_indexes = [
                index
                for index, line in enumerate(
                    lines
                )
                if self._is_contact_fragment(
                    line
                )
            ]

            if len(signal_indexes) < 2:
                continue

            first_signal = min(
                signal_indexes
            )

            last_signal = max(
                signal_indexes
            )

            start = (
                self._find_contact_region_start(
                    lines,
                    first_signal,
                )
            )

            end = (
                last_signal + 1
            )

            while (
                end < len(lines)
                and end <= last_signal + 6
            ):
                candidate = lines[
                    end
                ]

                if self._is_contact_fragment(
                    candidate
                ):
                    end += 1
                    continue

                if self._looks_like_contact_continuation(
                    candidate
                ):
                    end += 1
                    continue

                break

            region = lines[
                start:end
            ]

            if not self._region_has_enough_contact_signals(
                region
            ):
                continue

            personal_text = "\n".join(
                region
            ).strip()

            if not personal_text:
                continue

            remaining_lines = (
                lines[:start]
                + lines[end:]
            )

            remaining_text = (
                "\n".join(
                    remaining_lines
                ).strip()
            )

            updated_blocks = list(
                blocks
            )

            if remaining_text:
                updated_blocks[
                    block_index
                ] = remaining_text
            else:
                updated_blocks.pop(
                    block_index
                )

            return (
                personal_text,
                updated_blocks,
            )

        # ------------------------------------------------------------------
        # CASO 2: bloques independientes.
        # ------------------------------------------------------------------

        for start_index, candidate in enumerate(
            blocks
        ):
            if not self._looks_like_name_line(
                candidate
            ):
                continue

            window_end = min(
                len(blocks),
                start_index + 30,
            )

            window = blocks[
                start_index:
                window_end
            ]

            signal_positions = [
                relative_index
                for relative_index, value in enumerate(
                    window
                )
                if self._is_contact_fragment(
                    value
                )
            ]

            if len(signal_positions) < 2:
                continue

            last_signal_relative = max(
                signal_positions
            )

            end_index = (
                start_index
                + last_signal_relative
                + 1
            )

            # Incluir título profesional
            # y fragmentos de URL.
            while end_index < window_end:
                value = blocks[
                    end_index
                ]

                if self._is_contact_fragment(
                    value
                ):
                    end_index += 1
                    continue

                if self._looks_like_contact_continuation(
                    value
                ):
                    end_index += 1
                    continue

                if end_index <= (
                    start_index + 5
                ):
                    if self._looks_like_profile_title(
                        value
                    ):
                        end_index += 1
                        continue

                break

            region = blocks[
                start_index:
                end_index
            ]

            if not self._region_has_enough_contact_signals(
                region
            ):
                continue

            personal_text = "\n".join(
                value.strip()
                for value in region
                if value.strip()
            ).strip()

            if not personal_text:
                continue

            updated_blocks = (
                blocks[:start_index]
                + blocks[end_index:]
            )

            return (
                personal_text,
                updated_blocks,
            )

        return None

    def _find_contact_region_start(
        self,
        lines: list[str],
        first_signal: int,
    ) -> int:
        if first_signal <= 0:
            return first_signal

        search_start = max(
            0,
            first_signal - 8,
        )

        # Buscar título profesional.
        for index in range(
            first_signal - 1,
            search_start - 1,
            -1,
        ):
            if self._looks_like_profile_title(
                lines[index]
            ):
                name_start = (
                    self._find_name_before(
                        lines,
                        index,
                    )
                )

                if name_start is not None:
                    return name_start

                return index

        # Buscar dos fragmentos de nombre.
        for index in range(
            first_signal - 2,
            search_start - 1,
            -1,
        ):
            if index < 0:
                continue

            if (
                self._looks_like_name_line(
                    lines[index]
                )
                and index + 1 < len(lines)
                and self._looks_like_name_line(
                    lines[index + 1]
                )
            ):
                return index

        return first_signal

    def _find_name_before(
        self,
        lines: list[str],
        title_index: int,
    ) -> int | None:
        if title_index <= 0:
            return None

        previous = (
            title_index - 1
        )

        if not self._looks_like_name_line(
            lines[previous]
        ):
            return None

        if (
            previous > 0
            and self._looks_like_name_line(
                lines[previous - 1]
            )
        ):
            return previous - 1

        return previous

    # ========================================================================
    # NAME DETECTION
    # ========================================================================

    def _looks_like_name_line(
        self,
        line: str,
    ) -> bool:
        value = line.strip()

        if not value:
            return False

        if len(value) > 45:
            return False

        if any(
            char.isdigit()
            for char in value
        ):
            return False

        if any(
            char in value
            for char in (
                "@",
                "/",
                ":",
                "+",
                "·",
            )
        ):
            return False

        words = value.split()

        if not 1 <= len(words) <= 4:
            return False

        normalized = (
            self._normalize_for_matching(
                value
            )
            .casefold()
        )

        # Evitar falsos nombres.
        excluded_markers = (
            "building",
            "designed",
            "experienced",
            "specializing",
            "specialized",
            "powered",
            "services",
            "applications",
            "platform",
            "focused",
            "professional",
            "profesional",
            "developer",
            "desarrollador",
            "engineer",
            "ingeniero",
            "founder",
            "fundador",
            "product",
            "producto",
            "technology",
            "tecnologia",
            "tecnología",
        )

        if any(
            marker in normalized
            for marker in excluded_markers
        ):
            return False

        return all(
            re.fullmatch(
                r"[A-Za-zÀ-ÖØ-öø-ÿÑñ'’-]+",
                word,
            )
            is not None
            for word in words
        )

    def _looks_like_profile_title(
        self,
        line: str,
    ) -> bool:
        normalized = (
            self._normalize_for_matching(
                line
            )
            .casefold()
        )

        if not normalized:
            return False

        return any(
            re.search(
                rf"\b{re.escape(marker)}\b",
                normalized,
                re.IGNORECASE,
            )
            for marker in _PROFILE_TITLE_MARKERS
        )

    # ========================================================================
    # CONTACT
    # ========================================================================

    def _is_contact_fragment(
        self,
        line: str,
    ) -> bool:
        value = line.strip()

        if not value:
            return False

        normalized = (
            self._normalize_for_matching(
                value
            )
            .casefold()
        )

        if _EMAIL_RE.search(
            value
        ):
            return True

        if self._looks_like_phone(
            value
        ):
            return True

        if _LINKEDIN_RE.search(
            value
        ):
            return True

        if _GITHUB_RE.search(
            value
        ):
            return True

        if any(
            marker in normalized
            for marker in _LOCATION_MARKERS
        ):
            return True

        # Check for tech overload that overrides weak contact signals like "github"
        tech_hits = sum(1 for m in _TECH_MARKERS if m in normalized)
        if tech_hits >= 2:
            return False

        if any(
            marker in normalized
            for marker in _CONTACT_MARKERS
        ):
            return True

        # Artefactos típicos de extracción.
        if any(
            marker in normalized
            for marker in (
                "gmail",
                "hotmail",
                "outlook",
            )
        ):
            return True

        if normalized in {
            "in",
            "com",
            "comv",
            "com/",
            "in/",
            ".com",
            "gmailcom",
            "@gmailcom",
            "hotmailcom",
            "@hotmailcom",
            "outlookcom",
            "@outlookcom",
        }:
            return True

        return False

    def _looks_like_phone(
        self,
        text: str,
    ) -> bool:
        if not text:
            return False

        digits = re.sub(
            r"\D",
            "",
            text,
        )

        if len(digits) < 7:
            return False

        return bool(
            _PHONE_RE.search(
                text
            )
        )

    def _region_has_enough_contact_signals(
        self,
        lines: list[str],
    ) -> bool:
        if not lines:
            return False

        joined = "\n".join(
            lines
        )

        strong = 0
        weak = 0

        if _EMAIL_RE.search(
            joined
        ):
            strong += 2

        if self._looks_like_phone(
            joined
        ):
            strong += 2

        if _LINKEDIN_RE.search(
            joined
        ):
            strong += 1

        if _GITHUB_RE.search(
            joined
        ):
            strong += 1

        for line in lines:
            normalized = (
                self._normalize_for_matching(
                    line
                )
                .casefold()
            )

            tech_hits = sum(1 for m in _TECH_MARKERS if m in normalized)
            if tech_hits >= 2:
                # Demasiadas tecnologías para ser información personal
                return False

            if any(
                marker in normalized
                for marker in _LOCATION_MARKERS
            ):
                weak += 1

            if any(
                marker in normalized
                for marker in _CONTACT_MARKERS
            ):
                weak += 1

            if any(
                marker in normalized
                for marker in (
                    "gmail",
                    "hotmail",
                    "outlook",
                )
            ):
                weak += 1

            if self._looks_like_phone(
                line
            ):
                weak += 2

        if strong >= 2:
            return True

        return weak >= 3

    def _looks_like_contact_continuation(
        self,
        line: str,
    ) -> bool:
        normalized = (
            self._normalize_for_matching(
                line
            )
            .casefold()
        )

        if normalized in {
            "in",
            "com",
            "comv",
            "com/",
            "in/",
            ".com",
            "gmailcom",
            "@gmailcom",
            "hotmailcom",
            "@hotmailcom",
            "outlookcom",
            "@outlookcom",
        }:
            return True

        if normalized.endswith(
            (
                "com",
                "com/",
                "in/",
                "comv",
            )
        ):
            return True

        if normalized.startswith(
            (
                "@",
                ".",
                "/",
                "-",
            )
        ):
            return True

        return False

    # ========================================================================
    # PERSONAL INFO FALLBACK
    # ========================================================================

    def _looks_like_personal_info(
        self,
        block: str,
    ) -> bool:
        if not block.strip():
            return False

        normalized = (
            self._normalize_for_matching(
                block
            )
            .casefold()
        )

        score = 0

        if _EMAIL_RE.search(
            block
        ):
            score += 2

        if self._looks_like_phone(
            block
        ):
            score += 2

        if _LINKEDIN_RE.search(
            block
        ):
            score += 1

        if _GITHUB_RE.search(
            block
        ):
            score += 1

        tech_hits = sum(
            1 for marker in _TECH_MARKERS if marker in normalized
        )
        if tech_hits >= 2:
            return False

        marker_hits = sum(
            1
            for marker in _CONTACT_MARKERS
            if marker in normalized
        )

        score += min(
            marker_hits,
            2,
        )

        if score >= 2:
            return True

        return (
            self._looks_like_phone(
                block
            )
            and self._looks_like_profile_title(
                block
            )
        )

    def _is_meaningful_contact_block(
        self,
        block: str,
    ) -> bool:
        lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip()
        ]

        if not lines:
            return False

        if len(lines) == 1:
            value = lines[0].casefold()

            if value in {
                "linkedin",
                "github",
                "com",
                "com/",
                "in",
                "in/",
                "gmailcom",
                "@gmailcom",
            }:
                return False

        signals = 0

        if _EMAIL_RE.search(
            block
        ):
            signals += 1

        if self._looks_like_phone(
            block
        ):
            signals += 1

        if _LINKEDIN_RE.search(
            block
        ):
            signals += 1

        if _GITHUB_RE.search(
            block
        ):
            signals += 1

        return signals >= 2

    # ========================================================================
    # LANGUAGE CLEANUP
    # ========================================================================

    def _clean_languages_blocks(
        self,
        blocks: list[str],
    ) -> list[str]:
        if not blocks:
            return []

        cleaned: list[str] = []
        seen: set[str] = set()

        for block in blocks:
            value = block.strip()

            if not value:
                continue

            semantic = self._semantic_key(
                value
            )

            if not semantic:
                continue

            if (
                len(semantic) == 1
                and semantic.isalpha()
            ):
                continue

            if semantic in seen:
                continue

            seen.add(
                semantic
            )

            cleaned.append(
                value
            )

        return cleaned

    # ========================================================================
    # DEDUPLICATION
    # ========================================================================

    def _deduplicate_section_blocks(
        self,
        blocks: list[str],
    ) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()

        for block in blocks:
            value = block.strip()

            if not value:
                continue

            key = self._semantic_key(
                value
            )

            if not key:
                continue

            if key in seen:
                continue

            seen.add(
                key
            )

            result.append(
                value
            )

        return result

    # ========================================================================
    # JOIN
    # ========================================================================

    def _join_sections(
        self,
        accumulator: dict[
            SectionKey,
            list[str],
        ],
        confidences: dict[
            SectionKey,
            float,
        ],
        detections: dict[
            SectionKey,
            DetectionMethod,
        ],
    ) -> SectionMap:
        result: SectionMap = {}

        for key in _EMPTY_SECTIONS:
            text = "\n\n".join(
                block.strip()
                for block in accumulator.get(
                    key,
                    [],
                )
                if block.strip()
            ).strip()

            result[key] = SectionResult(
                text=text,
                confidence=confidences.get(
                    key,
                    0.0,
                ),
                detection=detections.get(
                    key,
                    "none",
                ),
            )

        return result

    # ========================================================================
    # EMPTY
    # ========================================================================

    @staticmethod
    def _empty_result() -> SectionMap:
        return {
            key: SectionResult(
                text="",
                confidence=0.0,
                detection="none",
            )
            for key in _EMPTY_SECTIONS
        }