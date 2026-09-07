"""Single analysis service used by the API, pipeline and CV agent."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal
from backend.modules.cv.engine.smart_cv_engine import SmartCVEngine
from backend.modules.cv.domain.professional_profile import ProfessionalProfile
from backend.modules.cv.parser.local_parser import LocalCVParser

MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARACTERS = 60000


class AIUnavailableError(RuntimeError):
    pass


@dataclass
class AnalysisResult:
    profile: ProfessionalProfile
    source_text: str
    extraction_method: str
    warnings: list[str]

    def to_dict(self):
        return asdict(self)


class CVAnalyzer:
    def __init__(self, ai_parser_factory=None):
        self.engine = SmartCVEngine()
        self.ai_parser_factory = ai_parser_factory

    def analyze_document(self, file_path, mode: Literal['local', 'lmstudio'] = 'local'):
        path = Path(file_path)
        if not path.is_file():
            raise ValueError("No se encontró el archivo.")
        if not 0 < path.stat().st_size <= MAX_FILE_BYTES:
            raise ValueError("El archivo está vacío o supera el límite de 10 MB.")
        document = self.engine.read(path)
        return self.analyze_text_result(document.text, mode)

    def analyze_text_result(self, text, mode='local'):
        if not text.strip():
            raise ValueError("No se encontró texto. Los PDF escaneados requieren OCR, aún pendiente.")
        if len(text) > MAX_TEXT_CHARACTERS:
            raise ValueError("El CV supera el límite de 60 000 caracteres.")
        if mode == 'local':
            profile = LocalCVParser().parse(text)
            warnings = ["Extracción básica sin IA: solo correo y campos explícitamente etiquetados. "
                        "Completa las demás secciones consultando el texto original."]
        elif mode == 'lmstudio':
            from backend.modules.cv.services.ai_cv_parser import AICVParser
            try:
                parser = (self.ai_parser_factory or AICVParser)()
                if not parser.is_ready():
                    raise AIUnavailableError("LM Studio no está disponible. Inicia su servidor y carga el modelo, "
                                             "o elige extracción básica sin IA.")
                profile = parser.parse(text)
            except AIUnavailableError:
                raise
            except Exception as error:
                raise AIUnavailableError("LM Studio no pudo completar el análisis. Comprueba el modelo "
                                         "y vuelve a intentar, o usa extracción básica sin IA.") from error
            warnings = ["Análisis con LM Studio. Revisa todos los datos antes de guardarlos; la IA puede equivocarse."]
        else:
            raise ValueError("Modo de análisis no admitido.")
        return AnalysisResult(profile, text, mode, warnings)

    def analyze(self, file_path, mode='local'):
        return self.analyze_document(file_path, mode).profile

    def analyze_text(self, text, mode='local'):
        return self.analyze_text_result(text, mode).profile

    def health(self):
        return {'engine': True, 'local_parser': True}
