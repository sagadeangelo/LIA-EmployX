# ExtractionChunkMerger Algorithm Audit

**Input document:** `CV_Miguel_Tovar_Full_Stack.docx`  
**Scope:** evidence only; no merge implementation was changed.

## Current algorithm

```python
for chunk in chunks:
    text = "\n".join(line.strip() for line in chunk.text.splitlines() if line.strip())
    key = (chunk.part_name, chunk.identity)
    if not text or key in seen:
        continue
    seen.add(key)
    merged.append(ExtractionChunk(text, chunk.source, chunk.part_name, chunk.ordinal, chunk.identity))
return "\n".join(chunk.text for chunk in merged).strip(), tuple(merged)
```

The algorithm has no model for paragraph, block, heading, original delimiter,
or reading-order metadata. Its only de-duplication key is `(part_name,
identity)`.

## Input inventory

| Strategy | Input chunks | Input chars | Newlines in inputs | Blank-line separators in inputs |
| --- | ---: | ---: | ---: | ---: |
| `standard_paragraphs` | 0 | 0 | 0 | 0 |
| `word_textboxes` | 90 | 3,252 | 0 | 0 |
| `drawingml` | 0 | 0 | 0 | 0 |
| `openxml_recovery` | 1 | 3,282 | 0 | 0 |
| **Total** | **91** | **6,534** | **0** | **0** |

Every textbox chunk is non-empty, has no leading or trailing newline, and has
zero original newline characters. Therefore the merge’s line-normalization at
line 31 does not remove a delimiter from these chunks: no delimiter has been
captured in the `ExtractionChunk` contract. The contract already lacks the
structural information the merger is asked to preserve.

## Complete textbox chunk manifest

All rows are from `word/document.xml`; each row has `newlines=0`,
`blank_pairs=0`, `leading_newline=false`, and `trailing_newline=false`.

| Ordinal(s) | Exact input text / relationship |
| --- | --- |
| 0 | `EXPERIENCIA DESTACADA` |
| 1 | `Founder & Lead Full Stack Developer` |
| 2 | `LIA-Tech` |
| 3 | `2025 – Actualidad` |
| 4 | 248-character professional-description paragraph |
| 5 | `LOGROS` |
| 6–10 | Five individual achievement paragraphs |
| 11 | `Tecnologías.` |
| 12 | 102-character technologies list |
| 13–25 | Exact repetition of chunks 0–12 |
| 26 | `PERFIL` |
| 27 | 371-character professional-profile paragraph |
| 28–29 | Exact repetition of chunks 26–27 |
| 30 | `🌎 IDIOMAS` |
| 31 | `Español — Nativo` |
| 32 | `Inglés — B2` |
| 33–35 | Exact repetition of chunks 30–32 |
| 36 | `🧩 ECOSISTEMA LIA` |
| 37–41 | `LIA-Tech`, `LIA EmployX`, `LIA Staylo`, `LIA Publish`, `Narrative Engine` |
| 42–47 | Exact repetition of chunks 36–41 |
| 48 | `🤖 AI TOOLKIT` |
| 49–56 | `ChatGPT`, `GitHub`, `Copilot`, `Google AI Studio`, `Prompt Engineering`, `ComfyUI`, `Stable Diffusion`, `AI-assisted Development` |
| 57–65 | Exact repetition of chunks 48–56 |
| 66 | `🚀 CORE TECHNOLOGIES` |
| 67–71 | `Flutter / Python`, `Dart / JavaScript`, `REST APIs / SQLite`, `Git / GitHub`, `Cloudflare / AI Agents` visual rows |
| 72–77 | Exact repetition of chunks 66–71 |
| 78 | `🎓 EDUCACIÓN` |
| 79–83 | Industrial Systems Engineering, UVM, Google Data Analytics, and two continuous-training lines |
| 84–89 | Exact repetition of chunks 78–83 |

The 91st chunk is `openxml_recovery[0]`: a single 3,282-character,
zero-newline concatenation beginning `EXPERIENCIA DESTACADAFounder & Lead Full
Stack DeveloperLIA-Tech...`. It represents the same visual content at a
different XML ancestor identity, so the current key cannot remove it.

## Transformation trace

| Step | Chunks | Characters | Newlines | Blank separators |
| --- | ---: | ---: | ---: | ---: |
| Strategy output | 91 | 6,534 | 0 | 0 |
| Per-chunk normalization | 91 | 6,534 | 0 | 0 |
| Identity de-duplication | 91 | 6,534 | 0 | 0 |
| Final `"\n".join(...)` | 91 | 6,624 | 90 | 0 |
| Splitter normalization | 1 block | 6,344 | many | 0 |

The transformation that produces the single splitter block is the final
single-newline join. `CVSectionSplitter._split_blocks()` requires `"\n\n"`;
there are zero such separators in the final raw text.

## Proven root cause

There are two independent contract defects in the merger boundary:

1. `ExtractionChunk` has no explicit source-boundary metadata, so original
   paragraph and block delimiters are unavailable to the merger.
2. `merge()` synthesizes only a single newline between every retained chunk.
   This creates a continuous line stream incompatible with the existing
   splitter’s paragraph-block contract. Its identity-only de-duplication also
   retains the concatenated OpenXML recovery representation.

This is the evidence basis for the design in
`MERGE_ARCHITECTURE_PROPOSAL.md`; no correction has been implemented.
