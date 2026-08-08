from enum import Enum
from pydantic import BaseModel

class DatePrecision(str, Enum):
    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"
    UNKNOWN = "UNKNOWN"

class PartialDate(BaseModel):
    """
    Representa una fecha extraída del CV donde no todos los componentes
    están presentes (ej: "2021" vs "Mayo 2021" vs "01/05/2021").
    Previene inventar datos (ej: asumir día 1) a nivel de dominio.
    """
    year: int | None = None
    month: int | None = None
    day: int | None = None
    precision: DatePrecision = DatePrecision.UNKNOWN
    
    @property
    def is_empty(self) -> bool:
        return self.year is None and self.month is None and self.day is None
