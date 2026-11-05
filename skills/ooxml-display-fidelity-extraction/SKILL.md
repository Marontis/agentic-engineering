---
name: ooxml-display-fidelity-extraction
description: >-
  Extract text and tables from Office Open XML documents (DOCX, XLSX, PPTX)
  with strict visual display fidelity to prevent silent content omissions,
  hidden-content prompt injections, number-format inversions, and spatial
  reading-order scrambles. Derived from Prism (arXiv:2611.05806).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# OOXML Display-Fidelity Extraction

> **Source**: [arXiv:2611.05806](https://arxiv.org/abs/2611.05806) — *When File Ingestion Misleads Language Models: Measuring and Mitigating Divergences in Office Documents* (Li, 2026) | `src:2611-05806v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use This Skill

Use this procedure whenever building, auditing, or hardening a document-ingestion pipeline, RAG indexer, or file-reading tool that converts Office Open XML (`DOCX`, `XLSX`, `PPTX`) files into plain text or Markdown for an LLM. Standard document extractors (`markitdown`, `python-docx`, `openpyxl`, `pandas`, `python-pptx`, `unstructured`, `Docling`, `Apache Tika/POI`, `calamine`, `docx2python`) parse underlying XML trees without interpreting ECMA-376 visibility, formatting, and layout semantics. Across 8 commercial chat assistants and coding agents (400 end-to-end trials), exploiting these extraction divergences misled agents in **64%** of trials overall (**75%** on chat assistants, and **88%** under XLSX number-format divergence), even when documents contained no imperative prompt-injection phrases.

---

## The Core Problem: Four Structural Divergence Classes

Across 10 widely used open-source extractors, hybrid static-dynamic analysis reveals **31** distinct element/attribute channels where extracted LLM text diverges from what a human sees in the default Office view (**19** hidden-injection channels and **12** silent-omission channels), plus systematic presentation divergences:

1. **Hidden Content Injection (19 channels: 10 PPTX, 4 DOCX, 5 XLSX)**: Extractors emit content invisible in the human default view — such as `<w:vanish/>` / `<w:webHidden/>` runs, 1-pt or zero-opacity text, font color matching cell/page background color, `<w:del>` tracked deletions, hidden XLSX worksheets (`state="hidden"` / `"veryHidden"`), hidden rows/columns (`hidden="1"`), cell comments, PPTX speaker notes (`ppt/notesSlides`), hidden slides (`show="0"`), and off-slide or occluded shapes.
2. **Silent Visible Content Omission (12 channels: 1 PPTX, 8 DOCX, 3 XLSX)**: Extractors silently drop content that humans read on the page — including DOCX headers (`w:hdr`), footers (`w:ftr`), footnotes (`w:footnote`), floating text boxes (`w:txbxContent`), structured document tags / content controls (`w:sdtContent`), tracked insertions (`w:ins`), and `mc:AlternateContent` `mc:Choice` branches (dropped by 9 of 10 extractors). In a 2,229-document benign government corpus (`govdocs1`), **56%** of DOCX files use footers, **24%** headers, **13%** footnotes, and **12%** text boxes.
3. **Display Formatting Divergence**: In XLSX, **6 of 7** extractors (`markitdown`, `openpyxl`, `pandas`, `unstructured`, `calamine`, `Docling`) emit raw stored `<v>` floats (`1000000`) rather than applying the ECMA-376 `numFmt` display mask (`"$#,##0,"` $\rightarrow$ `$1,000`, or custom literal overrides), reversing financial and policy conclusions in **88%** of agent trials. In DOCX, **6 of 6** extractors concatenate adjacent `<w:r>` runs without checking visibility boundaries, fusing a hidden `<w:vanish/>` prefix (`un`) with visible `authorized` into `unauthorized`.
4. **Spatial Reading-Order Inversion**: In PPTX and multi-shape DOCX layouts, XML sibling order (`python-pptx`, `Tika/POI`) and strict geometric $(y, x)$ coordinate sorting (`markitdown`, `unstructured`) scramble multi-column and 2D grid layouts whenever shapes have slight vertical offsets (e.g., 0.1 inch).

---

## Step-by-Step Procedure: The Two-Tier Prism Extraction Pipeline

Implement document ingestion as a compositional five-stage static interpreter — `serialize(order(display(visible(atoms(f)))))` — backed by a conditional multi-renderer visual oracle for documents with complex floating geometry.

### Step 1: Enumerate Reference-Bound Content Atoms (`atoms(f)`)

Do not traverse only `word/document.xml` or iterate blindly over every XML part in the ZIP archive (attackers can place unreferenced `header99.xml` files inside the archive).
1. **Resolve Relationship Graphs (`.rels`)**: Starting from the root document part (`word/document.xml`, `xl/workbook.xml`, `ppt/presentation.xml`), traverse only parts explicitly bound via active relationship IDs (`r:id`) in the document body or section properties (`w:headerReference`, `w:footerReference`, `w:footnoteReference`, `w:endnoteReference`).
2. **Select Markup Compatibility `mc:Choice` Branches**: When encountering `<mc:AlternateContent>`, parse the `mc:Choice` branch (representing modern Office rendering) and discard the `mc:Fallback` branch so text inside modern shapes and text boxes is neither dropped nor duplicated.
3. **Include Structured Document Tags and Tracked Insertions**: Traverse inside `<w:sdtContent>` (content controls) and `<w:ins>` (accepted/visible tracked insertions) while excluding `<w:del>` (tracked deletions) and `<w:moveFrom>`.

---

### Step 2: Filter by Effective Visual Visibility (`visible(...)`)

Before emitting any atom, evaluate its effective visibility across the full style-inheritance hierarchy (run properties $\rightarrow$ paragraph style $\rightarrow$ table/cell style $\rightarrow$ document defaults $\rightarrow$ theme palette):
1. **DOCX Visibility Gates**:
   - Exclude runs with `<w:vanish/>` or `<w:webHidden/>` (unless explicitly overridden by `val="0"` / `"false"`).
   - Compute effective font size (`w:sz` in half-points) and exclude sub-legible text ($\le 2\text{ pt}$, i.e., `w:sz <= 4`).
   - Resolve effective foreground text color (`w:color`, theme references `w:themeColor` + `w:themeTint`/`w:themeShade`, and text fill alpha `w14:alpha`) against the effective background color (run highlight `w:highlight`, run shading `w:shd`, paragraph shading, table-cell shading, or page background). Drop runs whose foreground-to-background contrast is zero or near-transparent.
2. **XLSX Visibility Gates**:
   - Exclude worksheets whose `<sheet>` entry in `workbook.xml` has `state="hidden"` or `state="veryHidden"`.
   - Exclude rows `<row hidden="1">` and columns `<col hidden="1">`, and skip zero-height rows (`ht="0"`) or zero-width columns (`width="0"`).
   - Exclude cells whose resolved font color matches the resolved cell fill color (`fgColor` in `styles.xml`), and exclude non-displayed cell comments (`xl/comments*.xml`) from primary table extraction (or quarantine them in a separately labeled metadata block).
3. **PPTX Visibility Gates**:
   - Exclude slides with `<p:sld show="0">`.
   - Exclude speaker notes (`ppt/notesSlides/*.xml`) from slide body text (or emit them only in an explicitly untrusted `[Speaker Notes]` quarantine block).
   - Exclude shapes with `<p:nvPr hidden="1">`, zero-opacity fills (`<a:alpha val="0"/>`), font color matching slide/shape fill color, bounding boxes completely outside the slide canvas $([0, \text{cx}] \times [0, \text{cy}])$, or shapes fully occluded by a higher z-order opaque shape.

---

### Step 3: Apply Spec-Compliant Display Formatting (`display(...)`)

Never emit raw XML `<v>` cell strings or concatenate raw `<w:t>` runs before visibility filtering:
1. **ECMA-376 Number Formatting in XLSX**: Look up each numeric or date cell's style index (`s` attribute $\rightarrow$ `cellXfs` $\rightarrow$ `numFmtId`) against built-in and custom `<numFmt formatCode="..."/>` definitions in `xl/styles.xml`. Apply thousands-scaling commas (`"$#,##0,"` divides by $10^3$), percentage multipliers, date serial conversions, conditional `[>1000]` branches, and literal display strings. If a custom `formatCode` replaces a numeric value with a pure literal string or scales it by orders of magnitude, emit the rendered display string (and in audit/checking mode, flag the discrepancy between raw `<v>` and formatted display value).
2. **Visibility-First Run Segmentation in DOCX**: Filter out hidden `<w:r>` runs in Step 2 *before* joining adjacent runs within a paragraph, and preserve whitespace attributes (`xml:space="preserve"`), tabs (`<w:tab/>`), and line breaks (`<w:br/>`) so hidden runs cannot bridge or corrupt visible words.

---

### Step 4: Reconstruct Visual Reading Order (`order(...)` and `serialize(...)`)

1. **Vertical Banding for Positioned Text Boxes**: When sorting positioned shapes or floating DOCX text boxes (`wp:anchor`), do **not** sort by raw $(y, x)$ coordinates, where a 1-pt vertical jitter inverts left-to-right column order. Group shapes into horizontal rows using a vertical tolerance band ($\Delta y \le 6\text{ pt}$ in DOCX, or proportional row-overlap clustering on slides), sort bands top-to-bottom, and sort shapes left-to-right ($x$) within each band.
2. **Section-Scoped Header/Footer/Footnote Placement**: Emit referenced headers at the top of their section, body paragraphs and tables in document order, and referenced footnotes/footers at the bottom in explicit labeled sections.

---

### Step 5: Route Complex Spatial Layouts Through a Multi-Renderer Consensus Oracle

Static XML interpretation resolves visibility, number formatting, and standard document flow in **0.5 ms** per document on average (**0.1 ms** DOCX, **1.3 ms** XLSX vs **63 ms** for `markitdown`), blocking all **17** invisible DOCX/XLSX injection channels and recovering all **10** omitted DOCX channels (**84/84** correct LLM answers across 28 generalization payloads vs **0/84** for naive extraction). However, documents containing multiple arbitrarily positioned shapes or overlapping floating objects (**4%** of benign XLSX, **21%** of DOCX, and **99%** of PPTX) can have reading orders that depend on visual layout:

1. **Structural Routing Trigger**: Run the fast static interpreter on every file. Trigger the render oracle only when the static pass detects positioned/floating shape geometry (`wp:anchor`, multi-shape PPTX slides) or when operating in high-assurance audit mode.
2. **Independent Dual Rendering**: Render the document to page/slide images using two independent layout engines (for example, `LibreOffice` headless and `Apple Quick Look` / native platform renderer) and transcribe visible text in visual reading order using a Vision-Language Model.
3. **Consensus Check**:
   - If both rendered transcriptions agree with each other but diverge from static XML extraction, adopt the rendered visual reading order (recovering **14/14** unambiguous spatial layouts, including **8/8** spatial-inversion attacks).
   - If the two renderers disagree with each other (for example, on deliberately ambiguous overlapping shapes — **1 of 26** tested layouts), flag the document as **layout-ambiguous** and surface a warning to the user or downstream agent rather than silently guessing an order.

---

## Operating Modes: Extraction vs. Divergence Checking

You can deploy this pipeline in two modes:
- **Sanitized Extraction Mode**: Directly feed the output of Step 1–5 to the LLM in place of `markitdown` / `python-docx` / `openpyxl`.
- **Divergence Checking Mode**: Diff the output of the legacy extractor against the display-fidelity output and flag any document where hidden channels appear, visible channels vanish, or `numFmt` display strings contradict raw values. On 193 benign Apache POI test documents (56 XLSX, 54 DOCX, 83 PPTX), divergence checking flags only **2.6%** (5 documents containing genuinely hidden template elements) while catching **100%** of tested content and formatting attacks.

---

## Related Skills and Rules

- [`covert-tool-injection-defense`](../covert-tool-injection-defense/SKILL.md) — Defending against indirect prompt injection in tool outputs.
- [`mcp-decode-provenance-binding`](../mcp-decode-provenance-binding/SKILL.md) — Provenance binding and taint tracking across decode boundaries.
- [`rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — "DO: Sanitize all tool outputs before injecting into agent context" and "DO: Bind cryptographic provenance at decode boundaries and verify both data and context lineage at critical sinks".
