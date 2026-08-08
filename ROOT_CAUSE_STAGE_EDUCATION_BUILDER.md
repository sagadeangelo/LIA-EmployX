# ROOT CAUSE - EducationBuilder

## Input
```text
🎓 EDUCATION

Industrial and Systems EngineeringUniversity of the Valley of Mexico (UVM)

Google Data Analytics Professional CertificateCoursera

Continuous Training in:Artificial Intelligence, Flutter, and Software Architecture
```
(Incluyendo duplicados por extracción)

## Expected output
3 objetos de tipo `CVEducation`:
1. Institution: "University of the Valley of Mexico (UVM)", Degree: "Industrial and Systems Engineering"
2. Institution: "Coursera", Degree: "Google Data Analytics Professional Certificate"
3. Institution: "Continuous Training in", Degree: "Artificial Intelligence, Flutter, and Software Architecture" (o mapeos razonables)

## Actual output
Produce **25 objetos separados** (incluyendo duplicados). Los primeros son:
1. Institution: "🎓 EDUCATION", Degree: ""
2. Institution: "Industrial and Systems EngineeringUniversity of the Valley of Mexico (UVM)", Degree: ""
3. Institution: "Google Data Analytics Professional CertificateCoursera", Degree: ""

## Pydantic model
```python
class CVEducation(BaseModel):
    institution: str
    degree: str
    level: str = ""
    period: str = ""
```

## ValidationError
Ninguno arrojado. Falla silenciosamente creando objetos sin sentido.

## Archivo
`backend/modules/cv/builders/education_builder.py`

## Clase
`EducationBuilder`

## Método
`build(self, text: str)`

## Línea
`blocks = re.split(r'\n\s*\n', text.strip())` y `title_line = lines[0]`, `degree = lines[1] if len(lines) > 1 else ""` (Líneas 13, 24, 25)

## Causa raíz
El constructor asume que cada bloque separado por doble salto de línea es una entrada educativa separada. Además:
1. No ignora el encabezado `🎓 EDUCATION`, por lo que lo convierte en una institución.
2. Como `ExtractionChunkMerger` no añadió nuevas líneas o espacios entre el `Degree` y la `Institution` (e.g. `Industrial and Systems EngineeringUniversity...`), ambas entidades terminan en la misma línea (`lines[0]`). El Builder espera que el Degree esté en `lines[1]`, por lo que el `Degree` queda vacío y la `Institution` recibe todo el texto fusionado.
3. El texto viene duplicado múltiples veces y no existe ninguna lógica de deduplicación.

## Corrección mínima propuesta
1. Eliminar encabezados (limpiando alfanuméricamente y comparando con "education", "educacion", etc.).
2. Deduplicar los bloques usando un `set`.
3. Ajustar la división de `Institution` y `Degree` dentro de la misma línea utilizando expresiones regulares o heurísticas para separar CamelCase fusionado (e.g., `EngineeringUniversity` -> `Engineering | University`) o dividir si se detectan palabras clave como "University", "Universidad", "Coursera", "Certificado", o usando el primer salto de línea disponible.
