# Root Cause: DOCX Loader Structural Boundary Loss

## Input

Affected input: `CV_Miguel_Tovar_Full_Stack.docx`.

The valid DOCX package has 174 text nodes and produced 90 textbox chunks plus one OpenXML recovery chunk. The loader reports `success` and returns 6,624 non-empty characters.

## Expected output

The `raw_text` passed to `CVSectionSplitter` must preserve paragraph/block boundaries. The splitter’s input model expects blank-line separators:

```python
# CVSectionSplitter._split_blocks, line 236
text.split("\n\n")
```

The CV should therefore arrive as multiple blocks, allowing its headers to delimit personal information, experience, education, skills, languages, and certifications.

## Actual output

`ExtractionChunkMerger.merge()` has a lossy normalization operation and joins chunks with a single newline:

```python
# ExtractionChunkMerger.merge, lines 31 and 37
text = "\n".join(line.strip() for line in chunk.text.splitlines() if line.strip())
return "\n".join(chunk.text for chunk in merged).strip(), tuple(merged)
```

For this specific DOCX, every input textbox chunk already has zero newline characters, so line 31 does not remove a captured blank line; it demonstrates that delimiters are absent from the current `ExtractionChunk` contract. Line 37 then creates only single-newline separators. The 6,624-character result normalizes to 6,344 characters and has exactly one block. The splitter classifies that block as `experience`; every other candidate section is empty.

## Exact failure point

| Item | Location |
| --- | --- |
| First loss | `ExtractionChunkMerger.merge()` |
| File | `backend/modules/cv/loader/extraction_strategy_resolver.py` |
| Exact lines | **31** is lossy if a source delimiter exists; **37** joins chunks with only `"\n"` |
| First observable failure | `CVSectionSplitter._split_blocks()` |
| File | `backend/modules/cv/parser/cv_section_splitter.py` |
| Exact line | **236**: `text.split("\n\n")` returns one block |

## Root cause

The extraction engine correctly recovers character content but its chunk contract omits source-boundary metadata and its merger emits only single-newline separators. This is not a strategy, builder, mapper, repository, API, runtime, or Flutter rendering failure. It is boundary-separator loss at the merge boundary.

## Correction proposal — not implemented

Keep the strategies unchanged. Correct only the merger’s output contract by preserving paragraph breaks and separating chunks with `"\n\n"`, or introduce an explicit chunk-to-block adapter before the splitter. The smallest compatible correction is the former, followed by a regression test using this exact document and asserting all expected sections before any builder executes.

No implementation was made because the sprint requires this report before a correction can be considered.
