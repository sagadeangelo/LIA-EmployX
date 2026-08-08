from dataclasses import dataclass

@dataclass
class ExperienceDraft:
    """
    Datos crudos extraídos de la sección de experiencia laboral.
    No asume normalización ni validación estricta de tipos.
    """
    raw_title_line: str
    raw_start_date: str
    raw_end_date: str
    raw_description: str
