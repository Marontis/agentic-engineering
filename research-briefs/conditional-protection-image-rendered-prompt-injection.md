# What Survives the Shift from Text to Pixels? Conditional Protection & Whole-Page Command Spread in Image-Rendered Documents

> **Source**: [arXiv:2611.24231](https://arxiv.org/abs/2611.24231) — Haoyang Liu, Yinong Xu, Zhe Lang, Zhenyu Guan & Qianyun Zhang (*What Survives the Shift from Text to Pixels? Conditional Protection against Prompt Injection in Image-Rendered Documents*, Nov 2026)
> **Praxis Source ID**: `src:2611-24231v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is a controlled behavioral, presentation, and mechanistic audit of rendering untrusted prose documents into page images (`Pictionary`, `arXiv:2609.36121`, already documented in [`pictionary-render-untrusted-content`](pictionary-render-untrusted-content.md) and `"DO: Consider rendering untrusted prose as images as one prompt-injection layer, per model"` in [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md)). Rather than introducing a standalone new defensive build pipeline, it establishes the **exact boundary conditions where text-to-image rendering fails**—operation-dependent survival (`77.96%` `Replace` vs. `5.01%` `Append` on `Qwen3-VL-8B`), typography/layout swings (`> 25` pp), `k = 8` candidate framing search (`100%` `Format` on susceptible VLMs), multi-span synthesis utility drops (`61.99%` Utility Ratio), and vision-encoder dispersion of injected commands across non-attack page tokens (`46.88% / 76.04%` execution even when `100%` of attack-span attention is blocked)—refining [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) in place per `output/AGENTS.md` (*"Add evidence before adding entries"*).

---

## Experimental Setup (`§3`)

- **Matched Text vs. Page-Image Corpus**: `191` English document QA sources from `LongBench` (`80` `Qasper`, `69` `MultiFieldQA-en`, `42` `HotpotQA`) rendered under `W1` (`876` px width, CSS font `26`) so text and image arms share identical wording, system prompt, and trusted user question, plus **`191` two-span integration questions** requiring synthesis across two distant passages (`90`-source stratified subset [`30`/dataset] for layout, presentation, candidate-search, and mechanistic suites).
- **Three Non-Overlapping Injected Operations**:
  - **`Append`**: Answer the user's question normally and append a neutral verification marker.
  - **`Format`**: Answer the user's question inside a prescribed benign wrapper format.
  - **`Replace`**: Abandon the document QA answer and emit only a fixed neutral replacement string.
- **Six Vision-Language Models**: Open-weight `Qwen3-VL-8B-Instruct` (with white-box hidden-state and `36`-layer attention access) plus `GPT-5-nano`, `Claude Haiku 5.5`, `Gemini 3.1 Flash-Lite`, `GLM-5.3-Flash`, and `DeepSeek V4.1 Flash 1017`.

---

## Core Behavioral & Presentation Findings (`§4–§6`, `Tables 1–4`)

### 1. Modality Shift Depends Strongly on Model, Operation, and Multi-Span Utility (`Tables 1–2`)

| Model | `Append` (`Text -> Image ASR %`) | `Format` (`Text -> Image ASR %`) | `Replace` (`Text -> Image ASR %`) | Clean `Orig.` QA F1 (`Text -> Image`, `UR`) | Clean `2-Span Integr.` QA F1 (`Text -> Image`, `UR`) |
|:------|:--------------------------------:|:--------------------------------:|:---------------------------------:|:-------------------------------------------:|:----------------------------------------------------:|
| **`Qwen3-VL-8B-Instruct`** | `73.78 -> 5.01` (`-68.77`) | `71.72 -> 11.35` (`-60.37`) | **`98.73 -> 77.96`** (`-20.77`) | `50.99 -> 50.33` (`98.71%`) | **`59.22 -> 36.71` (`61.99%`)** |
| **`GPT-5-nano`** | `77.95 -> 0.00` (`-77.95`) | `72.12 -> 0.00` (`-72.12`) | `29.53 -> 1.12` (`-28.41`) | `50.11 -> 49.83` (`99.44%`) | **`86.72 -> 77.48` (`89.35%`)** |
| **`Claude Haiku 5.5`** | `2.46 -> 0.00` (`-2.46`) | `5.11 -> 0.00` (`-5.11`) | `0.93 -> 0.00` (`-0.93`) | `46.50 -> 47.25` (`101.61%`) | `78.52 -> 80.53` (`102.56%`) |
| **`Gemini 3.1 Flash-Lite`** | **`93.97 -> 47.27`** (`-46.70`) | **`97.85 -> 59.79`** (`-38.06`) | `30.57 -> 0.24` (`-30.33`) | `55.66 -> 55.52` (`99.75%`) | `89.65 -> 90.29` (`100.71%`) |
| **`GLM-5.3-Flash`** | `65.10 -> 4.48` (`-60.62`) | `61.63 -> 1.92` (`-59.71`) | `0.24 -> 0.00` (`-0.24`) | `53.20 -> 52.93` (`99.49%`) | `86.26 -> 87.12` (`101.00%`) |
| **`DeepSeek V4.1 Flash`** | `64.87 -> 0.61` (`-64.26`) | `89.26 -> 6.69` (`-82.57`) | `3.60 -> 0.00` (`-3.60`) | `54.82 -> 51.15` (`93.31%`) | `87.84 -> 85.13` (`96.91%`) |

- **Operation reversal within the same model**: Evaluating only `Append`/`Format` makes `Qwen3-VL-8B` look protected (`5.01%` / `11.35%`), yet full-output **`Replace` survives at `77.96%`** (and `Gemini 3.1 Flash-Lite` shows the exact opposite profile: `0.24%` `Replace` vs. **`47.27%` `Append` and `59.79%` `Format`**). On the `46` `Qwen` sources where both modalities achieved `F1 = 1` clean QA, inline `Append` still fell `72.39% -> 3.37%`.
- **Hidden multi-span synthesis tax (`Table 2`)**: Standard `LongBench` questions show near-100% Utility Ratio (`93.31%–101.61%`), masking a **`-22.51` F1 drop (`61.99%` UR) on `Qwen3-VL-8B`** and `-9.24` F1 (`89.35%` UR) on `GPT-5-nano` once answers require integrating two evidence spans across rendered pages.

### 2. Separate-Page Layouts, Typography, & Small-Budget Candidate Search (`§5`, `Table 3`, `Figs. 2–3`)

- **Separate-page question-referencing layout (`Table 3`, `90` sources, Natural phrase / Random string)**: Moving the directive onto its own rendered page with question-bound framing collapses `Qwen3-VL-8B`'s inline protection—lifting strict image `Append` to **`51.11% / 59.44%`** (vs. `73.89% / 87.22%` text), `Format` to **`73.89%` (`+5.00` pp *above* text's `68.89%`) / `77.78%`**, and `Replace` to **`80.56%` (`+1.12` pp above text) / `73.33%`**, while `Gemini` reaches `25.56% / 51.11%` (`Append`) and `41.67% / 71.11%` (`Format`), and `GPT-5-nano` stays `<= 2.26%`.
- **Legibility vs. safety trade-off & framing leverage (`§5.2–5.4`)**: Increasing CSS font `20 -> 32` (at width `876`) or page width `704 -> 1280` px (at font `26`) each raises `Qwen` image `Replace` `ASR` by **`> 25` percentage points**, whereas the coarsest setting cuts clean QA F1 from `48.72` to `42.21`. `Question-bound` wording adds **`+17.78` to `+30.00` pp** over `Generic` (`Evidence-bound` is weakest in images, and placing inline attacks *farther* from cited evidence increases image execution); `2` concentrated copies add **`+24.44` pp** to `Qwen` image `Format`.
- **Candidate search (`§5.5`)**: Ranking `16` fixed candidate framings (`8` lead-ins $\times$ `2` wordings; *note abstract shorthand "eight fixed attack candidates" refers to the `k = 8` top-ranked query budget evaluated on the `60`-source test split after ranking on `30` dev sources*) shrinks `Qwen`'s `Append` modality gap from **`-37.37` pp (`k = 1`) to `-3.33` pp (`k = 8`)** and drives **`Format` to `100%` in both text and image** (`Gemini` likewise closes `Append` and `Format`, whereas `GPT-5-nano` retains its image deficit through `k = 8`).

### 3. Reading-vs-Following Dissociation & Mechanistic Whole-Page Spread (`§6–§7`, `Tables 4–6`)

- **Models read unexecuted image directives (`Table 4`)**: Under diagnostic `Report` (`R`) / `Untrusted-quote` (`U`) / `Act` (`A`) prompts on inline images, `GPT-5-nano` read and identified **`51.75%–85.56%`** of directives while executing **`0.00%–2.22%`**; `Qwen` read **`66.86%` (`Append`) and `71.97%` (`Format`)** while executing **`0.00%` and `2.22%`** (`3.70%` conditional `A | R`); and feeding `Qwen`'s own noisy OCR transcripts back as text (`89` sources) jumped execution from **`1.11%` (image) to `41.80%` (raw OCR text)** vs. `70.96%` clean text (`+14.44` pp strict / `+3.33` pp unresolved gain when manually fixing OCR errors). Trusted user `Permit` drove `Gemini` image execution to **`100%`** on unchanged page pixels.
- **Linear decodability vs. causal activation patching (`§7.1–7.2`, `Table 5`)**: On `Qwen3-VL-8B` (`48` test sources), a layer-`11` linear probe decoded the bound `4`-letter target code at **`100.00%` (text) and `98.44%` (image)**. Yet cross-code donor patching at `L11`/`L17` switched text outputs to the donor code (`54.51%* / 55.28%*` `Append`, `28.47%* / 28.61%*` `Format`, `0.00%` recipient) while image `Format` kept emitting the **recipient page's code (`57.29% / 59.38%`, `0.00%–2.08%` donor)**.
- **Attention blocking proves whole-page visual feature spread (`§7.3`, `Table 6`, `48` test sources)**:

| Attention Block Condition (`All 36 Decoder Layers`, `Qwen3-VL-8B`) | Text `Append` / `Format` Strict `%` | Image `Append` / `Format` Strict `%` | Clean QA F1 (`Append` / `Format` Image) |
|:-------------------------------------------------------------------|:-----------------------------------:|:------------------------------------:|:---------------------------------------:|
| **`No block`** | `90.63%` / `83.33%` | `53.13%` / `79.17%` | `55.66` / `55.66` |
| **`Block Attack Span A` (`100%` of injected tokens/patches)** | **`0.00%` / `0.00%`** | **`46.88%` / `76.04%`** | `52.88` / `54.53` |
| **`Block Random Equal-Size Span`** | `91.67%` / `85.42%` | `50.00%` / `78.13%` | `55.50` / `55.50` |
| **`Block Entire Instruction Page`** | `0.00%` / `0.00%` | **`0.00%` / `0.00%`** | `56.00` / `56.00` |

  Blocking decoder attention to the exact attack span $A$ eliminates text execution (`0.00%`) yet leaves image execution nearly untouched (`+84.38` and `+80.21` pp modality-by-blocking interaction), because the vision tower (`main` + `3` `DeepStack` visual feature streams) mixes the command and its `4`-letter code into **outside-$A$ visual tokens of the same page** (replacing outside-$A$ visual features with clean/neutral features drops image execution to **`0.00%`**, and splicing a donor code's outside-$A$ visual features while $A$ stays blocked drives donor execution to **`46.88% / 76.04%`** with `0.00%` recipient). Consequently, **localized visual-patch masking or bounding-box redaction inside the VLM token stream cannot sanitize an injected page image—quarantine must operate at the whole-page boundary (or pre-encoder pixel crop before vision encoding)**.

---

## Relevance to Praxis

- **Rules**: Refines `"DO: Consider rendering untrusted prose as images as one prompt-injection layer, per model"` in [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) in place with operation-asymmetry, `k = 8` framing-search, multi-span integration utility, and whole-page quarantine requirements.
- **Related Artifacts**: [`pictionary-render-untrusted-content`](pictionary-render-untrusted-content.md) (`arXiv:2609.36121`), [`scale-induced-semantic-shift-vlm-web-agents`](scale-induced-semantic-shift-vlm-web-agents.md) (`SISS`, `arXiv:2611.16744`), [`erase-multimodal-prompt-injection-self-distillation`](erase-multimodal-prompt-injection-self-distillation.md) (`arXiv:2610.41307`), and [`mpidetector-multimodal-prompt-injection-reasoning`](mpidetector-multimodal-prompt-injection-reasoning.md) (`arXiv:2610.30202`).
