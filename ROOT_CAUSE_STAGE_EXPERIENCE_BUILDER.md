# ROOT CAUSE - ExperienceBuilder

## Input
```text
FEATURED EXPERIENCE

Founder & Lead Full Stack Developer

LIA-Tech2025 – Present

Designed and developed a Full Stack platform powered by Artificial Intelligence to transform traditional reading into immersive experiences through synchronized narration, automatic image generation, and editorial automation.
```

## Expected output
1 object of type `CVExperience` with:
- company: "LIA-Tech" (or "LIA")
- position: "Founder & Lead Full Stack Developer"
- start_date: "2025"
- end_date: "Present"
- description: "Designed and developed a Full Stack platform..."

## Actual output
Multiple separated `CVExperience` objects because the text is split by `\n\n`.
1. Company: "FEATURED EXPERIENCE", Position: "Desconocido"
2. Company: "Founder & Lead Full Stack Developer", Position: "Desconocido"
3. Company: "LIA-Tech2025 – Present", Position: "Desconocido", Start Date: "2025", End Date: "None"
4. Company: "Designed and developed...", Position: "Desconocido"

Total extracted: 20 (including duplicates from the loader).

## Pydantic model
```python
class CVExperience(BaseModel):
    company: str
    position: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: str = ""
```

## ValidationError
None raised. It fails silently by creating logically incorrect and scattered objects.

## Archivo
`backend/modules/cv/builders/experience_builder.py`

## Clase
`ExperienceBuilder`

## Método
`build(self, text: str)`

## Línea
`blocks = re.split(r'\n\s*\n', text.strip())`
y
`title_line = lines[0]`
(Líneas 18 y 30)

## Causa raíz
El constructor divide el texto por dobles saltos de línea (`\n\s*\n`), asumiendo que CADA bloque separado por una línea en blanco es una experiencia distinta. Sin embargo, en el CV parseado, el título de la sección, el cargo, la empresa/fecha y la descripción están separados por dobles saltos de línea. Esto causa que cada fragmento de la misma experiencia se parsee como una experiencia separada, infiriendo erróneamente empresas (e.g. "FEATURED EXPERIENCE" o "Founder...").

## Corrección mínima propuesta
1. Eliminar o ignorar la línea del encabezado (e.g., "FEATURED EXPERIENCE", "EXPERIENCE", "EXPERIENCIA").
2. Cambiar la lógica de agrupación. En lugar de asumir que cada doble salto de línea es una experiencia separada, agrupar las líneas según patrones (por ejemplo, buscar fechas que indiquen el inicio de una nueva experiencia o roles reconocibles) o simplemente procesar el bloque completo si no hay múltiples experiencias.
3. Actualizar `ExperienceDraft` con la lógica ajustada sin romper `ExperienceNormalizer`.
