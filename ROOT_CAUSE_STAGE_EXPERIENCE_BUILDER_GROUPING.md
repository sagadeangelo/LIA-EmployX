# ROOT CAUSE - ExperienceBuilder Grouping Logic

## A. Input real
El texto exacto que recibe `ExperienceBuilder` (incluyendo duplicados producidos por etapas anteriores):
```text
FEATURED EXPERIENCE

Founder & Lead Full Stack Developer

LIA-Tech2025 – Present

Designed and developed a Full Stack platform powered by Artificial Intelligence to transform traditional reading into immersive experiences through synchronized narration, automatic image generation, and editorial automation.

KEY ACHIEVEMENTS

✓ Designed the complete architecture of the LIA ecosystem.

✓ Built Full Stack applications using Flutter and Python.

✓ Integrated Generative AI to automate complex processes.

✓ Implemented APIs and document processing workflows.

✓ Managed deployments using GitHub and Cloudflare.

FEATURED EXPERIENCE

Founder & Lead Full Stack Developer
... (se repite lo mismo)
```

## B. Experiencias reales esperadas
1 sola experiencia real (aunque el texto venga duplicado, la lógica de agrupación debería reconocer 1 o 2 bloques de experiencia que luego se pueden deduplicar, pero internamente cada bloque debe ser 1 objeto):
- **Company**: LIA-Tech
- **Position**: Founder & Lead Full Stack Developer
- **Start Date**: 2025
- **End Date**: Present
- **Description / Achievements**: "Designed and developed a Full Stack platform... KEY ACHIEVEMENTS ✓ Designed the complete architecture..."

## C. Experiencias que produce actualmente
Produce **20 experiencias separadas**, entre ellas:
1. Company: "FEATURED EXPERIENCE", Position: "Desconocido"
2. Company: "Founder & Lead Full Stack Developer", Position: "Desconocido"
3. Company: "LIA-Tech2025 – Present", Position: "Desconocido", Start Date: "2025", End Date: "None"
4. Company: "Designed and developed...", Position: "Desconocido"
5. Company: "KEY ACHIEVEMENTS", Position: "Desconocido"
6. Company: "✓ Designed the complete architecture...", Position: "Desconocido"
... y así sucesivamente para cada línea y su duplicado.

## D. Cómo se están fragmentando
El texto está siendo fragmentado **línea por línea**. Cada fragmento de la experiencia real (el cargo, la empresa+fechas, el párrafo descriptivo, cada bullet point de los logros) está separado en el texto crudo por un doble salto de línea (`\n\n`). Al dividir el texto por `\n\n`, el Builder aísla cada uno de estos elementos semánticos y fuerza su conversión a un objeto `CVExperience` independiente.

## E. Regla actual responsable
El constructor de `ExperienceBuilder` agrupa usando:
```python
blocks = re.split(r'\n\s*\n', text.strip())
```
Y luego procesa cada `block` asumiendo que contiene 1 experiencia completa (tomando la primera línea como empresa/cargo y el resto como descripción). Dado que los bloques resultantes son a menudo de una sola línea, la descripción queda vacía y todo se asume como "title_line".

## F. Nueva regla de agrupación propuesta
Una experiencia no está delimitada por `\n\n`. Se deben agrupar múltiples líneas no vacías hasta que se detecte el inicio de la siguiente experiencia.
Los indicadores estructurales disponibles para detectar una **nueva experiencia** o agrupar sus partes son:
1. **Línea de Fechas**: Líneas que contienen patrones de fechas (`YYYY - YYYY`, `YYYY – Present`, `Actualidad`, `Current`). Esto suele indicar que la línea actual o la inmediatamente anterior pertenecen a la cabecera de la experiencia.
2. **Ignorar Encabezados de Sección**: Ignorar líneas exactas como `FEATURED EXPERIENCE` o `EXPERIENCE` mediante limpieza de caracteres no alfanuméricos.
3. **Agrupación semántica por "Chunks"**: 
   - Línea 1 (después del encabezado): Asumir como Cargo (`Position`).
   - Línea 2 (a menudo con fechas): Asumir como Empresa y Rango de Fechas.
   - Líneas siguientes: Descripción y Logros. (Acumular todo el texto, incluyendo "KEY ACHIEVEMENTS" y bullets con "✓" o "-", hasta encontrar el próximo cargo/empresa que coincida con una nueva línea de fechas).

## G. Ejemplo

**INPUT:**
```text
FEATURED EXPERIENCE
Founder & Lead Full Stack Developer
LIA-Tech2025 – Present
Designed and developed a Full Stack platform...
✓ Designed the complete architecture of the LIA ecosystem.
```

**DEBERÍA PRODUCIR:**
```json
{
    "company": "LIA-Tech",
    "position": "Founder & Lead Full Stack Developer",
    "start_date": "2025-01-01",
    "end_date": "Present",
    "description": "Designed and developed a Full Stack platform...\n✓ Designed the complete architecture of the LIA ecosystem."
}
```

## H. Cómo evitar que FEATURED EXPERIENCE se convierta en una empresa
Igual que se hizo en `LanguagesBuilder`:
1. Normalizar la línea a minúsculas y eliminar caracteres no alfanuméricos (`re.sub(r'[^a-z]', '', line.lower())`).
2. Comprobar si el texto normalizado coincide exactamente con variaciones conocidas de encabezados: `experience`, `featuredexperience`, `workexperience`, `experienciaprofesional`, etc.
3. Si hay coincidencia, simplemente hacer `continue` y no procesarla ni como inicio de bloque ni como descripción.

---

# Otras Observaciones de Regresiones en el Pipeline

## EducationBuilder
**Input real observado:**
`🎓 EDUCATION\n\nIndustrial and Systems EngineeringUniversity of the Valley of Mexico (UVM)\n\n...`
**Problema:**
- Ignora que `🎓 EDUCATION` es un encabezado y lo convierte en una institución con `degree` vacío.
- Las instituciones y los títulos están fusionados sin saltos de línea (e.g. `Industrial and Systems EngineeringUniversity of the Valley of Mexico (UVM)`), y el builder asume que la línea completa es la institución.
- Fragmenta la educación de la misma forma (asume que cada doble salto de línea es una nueva educación, por lo que el certificado de Coursera queda desvinculado si hubiera un título).

## SkillsBuilder
**Input real observado:**
`🚀 CORE TECHNOLOGIES\n\nFlutter\n\nPython...`
**Problema:**
- Procesa el encabezado `🚀 CORE TECHNOLOGIES` como si fuera el nombre de una habilidad (`Name: ? CORE TECHNOLOGIES | Category: Technical`).
- También sufre la duplicación masiva proveniente del chunk merger, procesando `Flutter` múltiples veces (aunque esto puede ser manejado por deduplicación posterior, el problema semántico es el encabezado tratado como habilidad).
