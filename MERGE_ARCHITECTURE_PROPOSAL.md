# ExtractionChunkMerger Structural-Preservation Design

## Goal

Produce one `raw_text` string without destroying the document structure needed
by `CVSectionSplitter`. Strategies remain independent; builders, splitter,
runtime, profile architecture, and Flutter remain unchanged.

## Proposed model

```mermaid
flowchart LR
    A[Strategy chunks] --> B[Chunk provenance adapter]
    B --> C[Reading-order resolver]
    C --> D[Representation reconciler]
    D --> E[Structural boundary composer]
    E --> F[raw_text with preserved blocks]
```

The merger is redesigned as four cohesive collaborators rather than one loop:

| Collaborator | Responsibility |
| --- | --- |
| `ChunkProvenanceAdapter` | Represents text as opaque content plus part, XML identity, source strategy, container type, original boundary evidence, and document order key. It never trims text. |
| `ReadingOrderResolver` | Orders canonical chunks by part/story and source document position, never by strategy execution order. |
| `RepresentationReconciler` | Selects one canonical representation of overlapping content. A recovery chunk that semantically contains already-selected textbox chunks is diagnostic fallback data, not additional display text. |
| `StructuralBoundaryComposer` | Emits original delimiter evidence verbatim. If an independent Word paragraph has no explicit delimiter in the legacy source contract, it applies the documented fallback `\n\n` block separator. |

## Boundary contract

Introduce a merge-only boundary value object:

```text
StructuralBoundary(
  before: original delimiter or None,
  after: original delimiter or None,
  container: paragraph | textbox | drawingml | table_cell | recovery,
  is_heading_candidate: bool,
  document_order_key: stable XML/story position,
)
```

Rules:

1. Never call `strip()` or collapse whitespace on chunk text.
2. Preserve `\r\n`, `\n`, tabs, and intentional blank lines when provided.
3. Between independent paragraph/textbox chunks with no captured separator,
   emit `\n\n`; this maintains the existing splitter contract.
4. Preserve a heading as its own block: heading, then `\n\n`, then following
   content.
5. Preserve strategy provenance for diagnostics, but do not use strategy order
   as reading order.
6. Reconcile equivalent fallback representations before composing text; do not
   concatenate a recovery view with its constituent textbox view.

## Result for the audited CV

The canonical textbox sequence becomes multiple blank-line-separated blocks.
For example:

```text
EXPERIENCIA DESTACADA

Founder & Lead Full Stack Developer

LIA-Tech

...

🌎 IDIOMAS

Español — Nativo
```

The OpenXML concatenated recovery chunk is retained in the report as fallback
evidence but is excluded from the canonical composed text because its semantic
content overlaps selected textbox chunks.

## Compatibility and verification plan

The external result remains a single `raw_text` string. Existing
`CVSectionSplitter` receives the paragraph blocks it already expects; no change
to its code is required. Before implementation, approve the boundary model and
canonical-representation policy. After approval, tests must verify whitespace
preservation, source order, fallback suppression, repeated-layout handling, and
the expected populated section map for this exact DOCX.
