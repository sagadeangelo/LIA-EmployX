# ROOT CAUSE - PersonalInfoBuilder (vacío) — DIAGNÓSTICO DEFINITIVO

## Hallazgo

Los datos personales de Miguel (nombre, email, teléfono, LinkedIn) **NO están en ningún nodo de texto extractable** del DOCX.

Evidencia:
- El DOCX **no tiene `word/header*.xml`** — no hay header de documento Word.
- El primer `wps:txbx` (índice 0) está **vacío** en el XML — es el contenedor visual donde visualmente aparece el nombre.
- El primer `mc:AlternateContent` (fallback 0) también **no tiene texto** — no hay representación textual alternativa.
- Las 4 imágenes del documento (`image1.png`, `image2.jpeg`, `image3.png`, `image4.png`) contienen el banner visual del CV con el nombre y datos de contacto del candidato.

## Causa raíz real

El nombre, email, teléfono y LinkedIn de Miguel están **incrustados como imagen** (banner visual del CV), no como texto en el XML del documento Word. No hay representación textual disponible sin OCR.

## Arquitectura del DOCX

```
word/document.xml
  mc:AlternateContent [0]   → wps:txbx vacío → imagen con nombre/contacto (NO TEXTO)
  mc:AlternateContent [1]   → 🎓 EDUCATION + contenido (duplicado de w:t)
  mc:AlternateContent [2]   → 🤖 AI TOOLKIT
  mc:AlternateContent [3]   → 🚀 CORE TECHNOLOGIES
  mc:AlternateContent [4]   → 🧩 LIA ECOSYSTEM
  mc:AlternateContent [5]   → 🌎 LANGUAGES
  mc:AlternateContent [6]   → FEATURED EXPERIENCE
  mc:AlternateContent [7]   → PROFESSIONAL SUMMARY
word/media/image1.png       → Banner visual con nombre y contacto del candidato
word/media/image2.jpeg      → (imagen decorativa)
word/media/image3.png       → (imagen decorativa)
word/media/image4.png       → (imagen decorativa)
```

## Implicación

La extracción del header del documento Word no aplica aquí porque no existe `word/header*.xml`.
No se puede extraer el nombre/contacto de este DOCX sin OCR, lo cual está fuera del alcance permitido.

## Estado de personal_info

**Vacío de forma correcta y esperada** dado el diseño del CV de Miguel.
El `PersonalInfoBuilder` recibe texto vacío y devuelve un `CVContact` por defecto — comportamiento correcto.

## Decisión requerida

Opciones:
1. **Aceptar** que `personal_info` quede vacío para este CV específico. El pipeline puede continuar con los demás datos completos.
2. **Habilitar OCR** para la imagen de contacto — fuera del alcance permitido actualmente.
3. **Permitir ingreso manual** de datos de contacto vía API/Flutter después del upload.

## Estado: DETENIDO — Esperando decisión del usuario sobre personal_info vacío.
