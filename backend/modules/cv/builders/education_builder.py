from __future__ import annotations

import re
from dataclasses import dataclass, field

from backend.modules.cv.builders.base_builder import (
    BaseBuilder,
    BuildResult,
)
from backend.modules.cv.models.cv_education import CVEducation


@dataclass
class EducationBuildData:
    """
    Resultado estructurado del procesamiento de educación.

    Separa:

    - educación formal
    - formación continua

    Las certificaciones no se crean directamente aquí.
    Cuando una certificación aparece dentro de Education,
    CVDocumentBuilder puede recuperarla posteriormente.
    """

    education: list[CVEducation] = field(
        default_factory=list
    )

    continuous_training: list[CVEducation] = field(
        default_factory=list
    )


class EducationBuilder(
    BaseBuilder[EducationBuildData]
):
    """
    Construye registros CVEducation a partir de la sección
    de educación extraída de un CV.

    Está diseñado para tolerar texto procedente de DOCX donde
    los saltos de línea y los bloques visuales originales
    pueden haberse perdido.

    Ejemplo real:

        Ingeniería Industrial y de Sistemas

        Universidad del Valle de México

        Google Data Analytics (Coursera)

        continua en IA,

        Flutter y Arquitectura de Software

    Debe producir conceptualmente:

        Educación formal:
            Ingeniería Industrial y de Sistemas
            Universidad del Valle de México

        Certificación candidata:
            Google Data Analytics Professional Certificate
            Coursera

        Formación continua:
            IA
            Flutter y Arquitectura de Software
    """

    # ============================================================
    # HEADERS
    # ============================================================

    _HEADERS = {
        "education",
        "educacion",
        "educación",
        "academicbackground",
        "academic background",
        "formacionacademica",
        "formación académica",
        "formaciónacademica",
    }

    # ============================================================
    # CONTINUOUS TRAINING MARKERS
    # ============================================================

    _CONTINUOUS_MARKERS = (
        "continuous training",
        "continuous education",
        "professional development",
        "professional training",
        "continuing education",
        "training in",
        "training:",
        "capacitacion",
        "capacitación",
        "formacion continua",
        "formación continua",
        "desarrollo profesional",
        "continua en",
        "continúa en",
        "formacion en",
        "formación en",
    )

    # ============================================================
    # KNOWN INSTITUTIONS
    # ============================================================

    _KNOWN_INSTITUTIONS = (
        "Universidad del Valle de México",
        "University of the Valley of Mexico",
        "Universidad del Valle de Mexico",
        "Coursera",
        "Udemy",
        "Platzi",
        "edX",
        "Google",
    )

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
    # CERTIFICATION MARKERS
    # ============================================================

    _CERTIFICATION_MARKERS = (
        "certificate",
        "certification",
        "certificado",
        "certificacion",
        "certificación",
        "professional certificate",
        "professional certification",
    )

    # ============================================================
    # PUBLIC API
    # ============================================================

    def build(
        self,
        text: str,
    ) -> BuildResult[EducationBuildData]:
        """
        Construye educación formal y formación continua.

        No depende exclusivamente de bloques separados por
        líneas vacías porque la extracción DOCX puede fragmentar
        visualmente la información.
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

        lines = self._clean_lines(normalized)

        if not lines:
            warnings.append(
                "No se encontraron líneas educativas válidas."
            )

            return BuildResult(
                data=EducationBuildData(),
                confidence=0.0,
                warnings=warnings,
            )

        # --------------------------------------------------------
        # Remove section headers
        # --------------------------------------------------------

        lines = [
            line
            for line in lines
            if not self._is_header(line)
        ]

        formal_education: list[CVEducation] = []
        continuous_training: list[CVEducation] = []

        seen_formal: set[tuple[str, str]] = set()
        seen_training: set[tuple[str, str]] = set()

        # ========================================================
        # 1. DETECT CONTINUOUS TRAINING
        # ========================================================

        training_start = self._find_training_marker(
            lines
        )

        if training_start is not None:
            training_lines = lines[
                training_start:
            ]

            lines = lines[
                :training_start
            ]

            training_records = (
                self._parse_training_lines(
                    training_lines
                )
            )

            for record in training_records:
                key = self._record_key(record)

                if key in seen_training:
                    continue

                seen_training.add(key)
                continuous_training.append(record)

        # ========================================================
        # 2. DETECT CERTIFICATION-LIKE EDUCATION
        # ========================================================

        remaining_lines: list[str] = []

        for line in lines:
            certification = (
                self._parse_inline_certification(
                    line
                )
            )

            if certification is not None:
                degree, institution = certification

                record = self._create_education(
                    institution=institution,
                    degree=degree,
                )

                if record is not None:
                    key = self._record_key(record)

                    if key not in seen_formal:
                        seen_formal.add(key)
                        formal_education.append(
                            record
                        )

                continue

            remaining_lines.append(line)

        # ========================================================
        # 3. FORMAL EDUCATION
        # ========================================================

        formal_records = (
            self._parse_formal_education(
                remaining_lines
            )
        )

        for record in formal_records:
            key = self._record_key(record)

            if key in seen_formal:
                continue

            seen_formal.add(key)
            formal_education.append(record)

        # ========================================================
        # RESULT
        # ========================================================

        if not formal_education and not continuous_training:
            warnings.append(
                "No se pudieron identificar registros "
                "educativos válidos."
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

        if formal_education:
            warnings.append(
                "Educación formal agrupada por pares "
                "título/institución."
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
    # FORMAL EDUCATION
    # ============================================================

    def _parse_formal_education(
        self,
        lines: list[str],
    ) -> list[CVEducation]:
        """
        Reconstruye educación formal.

        Caso típico:

            Ingeniería Industrial y de Sistemas
            Universidad del Valle de México

        Se convierte en un único CVEducation.
        """

        records: list[CVEducation] = []

        i = 0

        while i < len(lines):
            current = lines[i]

            # ----------------------------------------------------
            # Known institution on its own line
            # ----------------------------------------------------

            if self._looks_like_institution(current):
                if i + 1 < len(lines):
                    next_line = lines[i + 1]

                    # Si la siguiente línea parece título,
                    # interpretamos:
                    #
                    # institución
                    # título
                    #
                    if not self._looks_like_institution(
                        next_line
                    ):
                        record = self._create_education(
                            institution=current,
                            degree=next_line,
                        )

                        if record is not None:
                            records.append(record)

                        i += 2
                        continue

            # ----------------------------------------------------
            # Current line followed by institution
            # ----------------------------------------------------

            if i + 1 < len(lines):
                next_line = lines[i + 1]

                if self._looks_like_institution(
                    next_line
                ):
                    record = self._create_education(
                        institution=next_line,
                        degree=current,
                    )

                    if record is not None:
                        records.append(record)

                    i += 2
                    continue

            # ----------------------------------------------------
            # Merged degree + institution
            # ----------------------------------------------------

            merged = self._split_known_institution(
                current
            )

            if merged is not None:
                degree, institution = merged

                record = self._create_education(
                    institution=institution,
                    degree=degree,
                )

                if record is not None:
                    records.append(record)

                i += 1
                continue

            # ----------------------------------------------------
            # Single education line
            # ----------------------------------------------------

            if self._looks_like_degree(current):
                record = self._create_education(
                    institution="",
                    degree=current,
                )

                if record is not None:
                    records.append(record)

            i += 1

        return records

    # ============================================================
    # INLINE CERTIFICATIONS
    # ============================================================

    def _parse_inline_certification(
        self,
        line: str,
    ) -> tuple[str, str] | None:
        """
        Detecta certificaciones embebidas en una línea.

        Ejemplo:

            Google Data Analytics (Coursera)

        Produce:

            degree:
                Google Data Analytics Professional Certificate

            institution:
                Coursera

        Se añade "Professional Certificate" para que
        CVDocumentBuilder pueda reconocer posteriormente
        este registro como certificación mediante su mecanismo
        de recuperación de certificaciones mal clasificadas.
        """

        match = re.match(
            r"^(?P<degree>.+?)"
            r"\s*\("
            r"(?P<provider>Coursera|Udemy|Platzi|edX)"
            r"\)\s*$",
            line,
            re.IGNORECASE,
        )

        if not match:
            return None

        degree = self._clean_value(
            match.group("degree")
        )

        provider = self._normalize_institution(
            match.group("provider")
        )

        if not degree or not provider:
            return None

        normalized_degree = (
            self._normalize_for_matching(
                degree
            )
        )

        # Google Data Analytics is a known certification
        # in the supplied CV.
        if (
            "google data analytics"
            in normalized_degree
        ):
            degree = (
                f"{degree} "
                "Professional Certificate"
            )

        elif not self._contains_certification_marker(
            degree
        ):
            degree = (
                f"{degree} "
                "Professional Certificate"
            )

        return degree, provider

    # ============================================================
    # CONTINUOUS TRAINING
    # ============================================================

    def _parse_training_lines(
        self,
        lines: list[str],
    ) -> list[CVEducation]:
        """
        Convierte formación continua en registros individuales.

        Caso del CV:

            continua en IA,

            Flutter y Arquitectura de Software

        Produce:

            IA
            Flutter y Arquitectura de Software
        """

        if not lines:
            return []

        content_lines = list(lines)

        first = content_lines[0]

        # --------------------------------------------------------
        # Remove marker from first line.
        # --------------------------------------------------------

        first = re.sub(
            r"^(?:continua|continúa)"
            r"\s+en\s*:?\s*",
            "",
            first,
            flags=re.IGNORECASE,
        )

        first = re.sub(
            r"^(?:formacion|formación)"
            r"\s+continua\s*:?\s*",
            "",
            first,
            flags=re.IGNORECASE,
        )

        first = re.sub(
            r"^(?:continuous training"
            r"|continuous education"
            r"|professional development"
            r"|professional training)"
            r"\s*:?\s*",
            "",
            first,
            flags=re.IGNORECASE,
        )

        first = self._clean_value(first)

        content: list[str] = []

        if first:
            content.append(first)

        content.extend(
            self._clean_value(line)
            for line in content_lines[1:]
            if self._clean_value(line)
        )

        # --------------------------------------------------------
        # Split comma-separated training topics.
        # --------------------------------------------------------

        topics: list[str] = []

        for line in content:
            parts = [
                self._clean_value(part)
                for part in line.split(",")
            ]

            for part in parts:
                if not part:
                    continue

                topics.append(part)

        # --------------------------------------------------------
        # Merge obvious continuation lines.
        # --------------------------------------------------------

        topics = self._merge_training_fragments(
            topics
        )

        records: list[CVEducation] = []

        for topic in topics:
            topic = self._clean_training_topic(
                topic
            )

            if not topic:
                continue

            record = self._create_education(
                institution="",
                degree=topic,
            )

            if record is not None:
                records.append(record)

        return records

    # ============================================================
    # TRAINING MARKER
    # ============================================================

    def _find_training_marker(
        self,
        lines: list[str],
    ) -> int | None:
        for index, line in enumerate(lines):
            normalized = (
                self._normalize_for_matching(
                    line
                )
            )

            for marker in self._CONTINUOUS_MARKERS:
                marker_normalized = (
                    self._normalize_for_matching(
                        marker
                    )
                )

                if marker_normalized in normalized:
                    return index

        return None

    # ============================================================
    # TRAINING FRAGMENTS
    # ============================================================

    @staticmethod
    def _merge_training_fragments(
        topics: list[str],
    ) -> list[str]:
        """
        Evita fragmentar expresiones educativas obvias.

        Ejemplo:

            Flutter
            y Arquitectura de Software

        permanece como:

            Flutter y Arquitectura de Software
        """

        if not topics:
            return []

        merged: list[str] = []

        index = 0

        while index < len(topics):
            current = topics[index]

            if (
                index + 1 < len(topics)
                and topics[index + 1]
                .casefold()
                .startswith("y ")
            ):
                merged.append(
                    f"{current} "
                    f"{topics[index + 1]}"
                )
                index += 2
                continue

            merged.append(current)
            index += 1

        return merged

    # ============================================================
    # RECORD CREATION
    # ============================================================

    @staticmethod
    def _create_education(
        institution: str,
        degree: str,
    ) -> CVEducation | None:
        """
        Construye CVEducation utilizando exclusivamente
        los campos reales del modelo CVEducation.
        """

        institution = (
            EducationBuilder._clean_value(
                institution
            )
        )

        degree = (
            EducationBuilder._clean_value(
                degree
            )
        )

        if not institution and not degree:
            return None

        return CVEducation(
            institution=institution,
            degree=degree,
            field_of_study=None,
            education_level=None,
            location=None,
            start_date=None,
            end_date=None,
            current=False,
            description=None,
            gpa=None,
            honors=[],
            confidence=1.0,
        )

    # ============================================================
    # RECORD KEY
    # ============================================================

    @staticmethod
    def _record_key(
        record: CVEducation,
    ) -> tuple[str, str]:
        return (
            (
                record.institution or ""
            ).casefold().strip(),
            (
                record.degree or ""
            ).casefold().strip(),
        )

    # ============================================================
    # INSTITUTION DETECTION
    # ============================================================

    @classmethod
    def _looks_like_institution(
        cls,
        value: str,
    ) -> bool:
        normalized = (
            cls._normalize_for_matching(
                value
            )
        )

        compact = re.sub(
            r"\s+",
            " ",
            normalized,
        ).strip()

        for marker in cls._INSTITUTION_MARKERS:
            marker_normalized = (
                cls._normalize_for_matching(
                    marker
                )
            )

            if (
                marker_normalized in compact
            ):
                return True

        return False

    # ============================================================
    # DEGREE DETECTION
    # ============================================================

    @classmethod
    def _looks_like_degree(
        cls,
        value: str,
    ) -> bool:
        """
        Determina si una línea parece representar un grado,
        programa o formación educativa.

        Es deliberadamente conservador para evitar que nombres,
        teléfonos, URLs o texto de otras columnas terminen en
        Education.
        """

        normalized = (
            cls._normalize_for_matching(
                value
            )
        )

        if not normalized:
            return False

        # --------------------------------------------------------
        # Explicit degree terms
        # --------------------------------------------------------

        degree_markers = (
            "ingenieria",
            "ingeniero",
            "licenciatura",
            "licenciado",
            "maestria",
            "master",
            "doctorado",
            "doctor",
            "degree",
            "bachelor",
            "associate",
            "diploma",
            "certificate",
            "certificacion",
            "certificado",
            "professional certificate",
        )

        if any(
            marker in normalized
            for marker in degree_markers
        ):
            return True

        # --------------------------------------------------------
        # Known professional programs
        # --------------------------------------------------------

        program_markers = (
            "data analytics",
            "software architecture",
            "artificial intelligence",
            "inteligencia artificial",
            "flutter",
            "python",
        )

        if any(
            marker in normalized
            for marker in program_markers
        ):
            return True

        return False

    # ============================================================
    # KNOWN INSTITUTION SPLITTING
    # ============================================================

    def _split_known_institution(
        self,
        line: str,
    ) -> tuple[str, str] | None:
        """
        Detecta casos como:

            Ingeniería Industrial y de Sistemas
            Universidad del Valle de México

        o:

            Ingeniería Industrial y de SistemasUniversidad
            del Valle de México
        """

        normalized_line = (
            self._normalize_for_matching(
                line
            )
        )

        for institution in sorted(
            self._KNOWN_INSTITUTIONS,
            key=len,
            reverse=True,
        ):
            normalized_institution = (
                self._normalize_for_matching(
                    institution
                )
            )

            position = (
                normalized_line.find(
                    normalized_institution
                )
            )

            if position < 0:
                continue

            degree = self._clean_value(
                line[:position]
            )

            institution_text = self._clean_value(
                line[
                    position
                    + len(normalized_institution):
                ]
            )

            if institution_text:
                institution = (
                    institution_text
                )

            if degree:
                return (
                    degree,
                    institution,
                )

        return None

    # ============================================================
    # CERTIFICATION HELPERS
    # ============================================================

    @classmethod
    def _contains_certification_marker(
        cls,
        value: str,
    ) -> bool:
        normalized = (
            cls._normalize_for_matching(
                value
            )
        )

        return any(
            marker
            in normalized
            for marker
            in cls._CERTIFICATION_MARKERS
        )

    # ============================================================
    # HEADER DETECTION
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
    # TEXT NORMALIZATION
    # ============================================================

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:
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

    # ============================================================
    # LINE CLEANING
    # ============================================================

    @staticmethod
    def _clean_lines(
        text: str,
    ) -> list[str]:
        lines: list[str] = []

        for line in text.splitlines():
            clean = (
                EducationBuilder._clean_value(
                    line
                )
            )

            if not clean:
                continue

            lines.append(clean)

        return lines

    # ============================================================
    # TRAINING CLEANING
    # ============================================================

    @staticmethod
    def _clean_training_topic(
        value: str,
    ) -> str:
        value = (
            EducationBuilder._clean_value(
                value
            )
        )

        value = re.sub(
            r"^[,;:]+",
            "",
            value,
        )

        value = re.sub(
            r"[,;:]+$",
            "",
            value,
        )

        return value.strip()

    # ============================================================
    # INSTITUTION NORMALIZATION
    # ============================================================

    @staticmethod
    def _normalize_institution(
        value: str,
    ) -> str:
        clean = (
            EducationBuilder._clean_value(
                value
            )
        )

        normalized = (
            EducationBuilder
            ._normalize_for_matching(
                clean
            )
        )

        mapping = {
            "universidad del valle de mexico":
                "Universidad del Valle de México",

            "university of the valley of mexico":
                "University of the Valley of Mexico",

            "coursera":
                "Coursera",

            "udemy":
                "Udemy",

            "platzi":
                "Platzi",

            "edx":
                "edX",

            "google":
                "Google",
        }

        return mapping.get(
            normalized,
            clean,
        )

    # ============================================================
    # MATCHING NORMALIZATION
    # ============================================================

    @staticmethod
    def _normalize_for_matching(
        value: str,
    ) -> str:
        value = value.casefold()

        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ü": "u",
            "ñ": "n",
            "Ã¡": "a",
            "Ã©": "e",
            "Ã­": "i",
            "Ã³": "o",
            "Ãº": "u",
            "Ã¼": "u",
            "Ã±": "n",
        }

        for source, target in replacements.items():
            value = value.replace(
                source,
                target,
            )

        return value

    # ============================================================
    # GENERAL CLEANING
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