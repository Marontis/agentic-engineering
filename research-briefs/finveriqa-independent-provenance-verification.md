# FinVeriQA: Financial Research Agents for Question Answering — Routing, Retrieval, MCP Tool Use, and Provenance-Aware Evidence Verification

> **Source**: [arXiv:2611.25071](https://arxiv.org/abs/2611.25071) — Meenakshi Rajpurohit, Anna Phan, Ravikumar Komandur Narayanan, Gunanidhi Ramakrishnan & Nathan Howland (San Jose State University, November 2026)
> **Praxis Source ID**: `src:2611-25071v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Evaluating `FinVeriQA` (`arXiv:2611.25071`) against [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md) classifies it as a **component-allocation & provenance-verification Research Brief** + rule contribution rather than a standalone `SKILL.md`:

1. **Prototype Case Study & Oracle Upper-Bound Experiment**: As the authors candidly document (`Sections 5.6, 5.8, and 6`), the `100`-item `D1` routing set is author-constructed pending external human sign-off, the live multi-agent prototype (`E6`, `5` queries) still suffered un-keyed `AMD` sample-data reuse in `data_agent` on `2` routes, and the independent-provenance verifier (`Check C` in `E8`) is evaluated using an **oracle reference value** as an upper bound rather than a general automated cross-filing entity/unit alignment procedure.
2. **Sharp Quantitative Component-Allocation & Verification Guardrails**: What transfers cleanly across quantitative RAG, financial analysis, and multi-agent tool pipelines are two strongly evidenced negative/positive rules: (i) **corrupted shared evidence breaks both `5`-sample self-consistency (`0.50 -> 0.00` accuracy at `0.59` agreement) and shared-passage validators (`35%` vs. `77%` independent-provenance catch rate, $p = 5.96 \times 10^{-8}$)**, and (ii) **small typed encoders (`Laya` `421M`, `0.86`) and deterministic `Python` (`100%`, `0.0007 ms`) strictly dominate `7B–12B` and `8B`-reasoning LLMs on discrete routing and ratio math**.

---

## Executive Summary

`FinVeriQA` audits component-by-component failure modes across a five-part financial QA architecture—typed query routing, deterministic `MCP` calculation and live-quote tools, `SEC 10-K` hybrid retrieval, multi-agent orchestration, and post-generation verification (`E1–E8`):

- **Discrete Routing Favors Small Typed Encoders Over `7B–12B` and Reasoning LLMs (`E1–E2, E7`)**: A `421M`-parameter `ModernBERT-large` typed-decision classifier (`Laya`) achieves **`0.86` `[0.79, 0.92]`** overall accuracy (`0.85` [`51/60`] intent routing in `~315–319 ms`) vs. **`0.68` `[0.60, 0.77]`** for `Mistral-7B` (`0.52` [`31/60`] intent, exact McNemar $p = 0.0003$, `21 vs 3`; keyword rules `0.65`; cascading low-confidence items to a weaker LLM fallback degraded intent routing to `0.62`). Scaling the generative router to `Mistral-NeMo-12B` (`7.1 GB`) yielded **zero gain (`0.68` overall, `32/60` intent, `0.35` vs. `0.37` intent macro-F1)**, while `DeepSeek-R1-8B` (`T = 0.6`) reached `0.77` (run 1: `40/60` [`0.6667`] intent) and `0.79` (run 2, $p = 0.0192$) only at **`9.9x` higher latency (`2,588 ms` vs. `262 ms`)**—still `18` intent points behind `Laya`.
- **Shared-Evidence Validation & Self-Consistency Fail Silently Under Upstream Data Corruption (`E6, E8`)**: When a single figure inside a retrieved `FinRank` passage is corrupted ($\times \{1.18, 1.27, 0.82, 0.73\}$), `5`-sample self-consistency on `Mistral-7B` ($n = 60$) **remains confident (`0.55 -> 0.59` agreement) while accuracy collapses from `0.50` to `0.00`** (`DeepSeek-R1-8B`, $n = 40$: **`0.35 -> 0.03` accuracy** at `0.26 -> 0.20` agreement). A validator reading the **same corrupted passage (`Check B`) catches only `35%` `[0.23, 0.47]`** (`65%` silent error rate), whereas cross-checking against an **independent-provenance source (`Check C`) catches `77%` `[0.65, 0.87]`** (`23%` silent error, exact McNemar $p = 5.96 \times 10^{-8}$, `25 vs 0` strict superset; **`90%` vs. `68%`**, $p = 0.003906$, `9 vs 0` on `DeepSeek-R1-8B`).

---

## Key Quantitative Findings

### 1. Component Allocation Across Routing, Math, Live Quotes & `10-K` Retrieval (`Tables 2–7`)

| Subtask & Evaluation Split | Generative LLM Baseline(s) | Specialized / Deterministic Component | Key Engineering Lesson |
|:---------------------------|:---------------------------|:--------------------------------------|:-----------------------|
| **Intent & Sentiment Routing** (`D1 = 100`: `60` intent, `40` sentiment; `Tables 2, 3, 7`) | `Mistral-7B`: **`0.68`** (`0.52` intent, `0.93` sentiment, `262–267 ms`)<br>`Mistral-NeMo-12B`: **`0.68`** (`32/60` intent, `0.35` F1, `305 ms`)<br>`DeepSeek-R1-8B`: **`0.77` / `0.79`** (`40/60` intent, **`2,588 ms`**) | **`Laya` (`421M` `ModernBERT-large`)**: **`0.86`** overall (**`0.85` [`51/60`] intent**, `0.88` sentiment, `~315–319 ms`; in-sample task-routed hybrid `0.88`) | Scale (`7B -> 12B`) adds `0.00` routing gain; reasoning (`R1-8B`) costs `9.9x` latency and still trails `Laya` on 4-class intent (`0.67` vs. `0.85`). |
| **Financial Ratio & Growth Math** (`100` programmatic items, `5` formulas; `Table 4`) | `Mistral-7B`: **`29%`** (`386 ms`; **`0%`** on QoQ, YoY, gross margin)<br>`Ministral 3 8B`: **`72%`** (`74%` on `50`; dropped `-` signs)<br>`gpt-5` (`50` items): **`98%`** (`49/50`, `1,323 ms`) | **Deterministic `Python` `MCP` Tool**: **`100%`** (`100/100`, **`0.0007 ms`**) | Never compute financial margins, YoY/QoQ growth, or P/E in LLM tokens; `Python` eliminates sign/rounding drift `10^6x` faster. |
| **Live Equity Quotes** (`10` tickers; `Table 5`) | Parametric `Mistral-7B`: **`210%` mean error** (`0/10` within `5%`) | **Live `Finnhub` Quote `MCP` Tool**: **`0.00%` error** (`10/10` exact) | Block parametric fallback on time-sensitive market prices. |
| **`SEC 10-K` Filing Retrieval** (`50` `AAPL`/`MSFT`/`NVDA` items; `Table 6`*) | Naive first-match `Item` regex: **`40`-char TOC stub** (`0%` body content) | **Longest-body `Item` deduplication (`114,916` chars) + `BM25 + dense RRF`**: **`76%` Hit@5**, **`0.74` MRR** | `10-K` Table-of-Contents lines match `Item 1A`/`Item 7` headers first; always select the header match followed by the most body text before chunking. |

*(Transparent manuscript note: prose in `Section 5.5` [line `1228`] refers to `"Table 7"` when citing the `50`-question `76%` Hit@5 and `0.74` MRR retrieval benchmark, which actually appears in `Table 6`; `Table 7` reports the `E7` `Mistral-NeMo-12B` and `DeepSeek-R1-8B` router scaling results.)*

### 2. Un-Keyed Shared Memory & Corrupted Shared Evidence (`E6 & E8, Tables 8–11`)

- **Silent Entity Swap Behind Passing Code Checks (`E6`, `Tables 8–9`)**: Across `5` live end-to-end orchestrator queries, `3` (`Q1` AMD R&D, `Q2` Apple supply chain, `Q3` NVDA P/E) returned grounded answers, **but `Q4` (`NVIDIA` revenue growth) and `Q5` (`Alphabet` cash flow) routed at `0.87` confidence and passed `2/2` code-level format/arithmetic validation checks while reporting bundled `AMD` figures under `NVIDIA`'s and `Alphabet`'s names** (plus a mis-numbered `[P2]` citation tag) because `data_agent` reused un-keyed `amd_*` shared memory entries.
- **Controlled Corruption Sweep (`E8`, `FinRank`, `Tables 10–11`)**: Perturbing a single source figure in each `FinRank` table/passage by $\times \{1.18, 1.27, 0.82, 0.73\}$ across `p \in \{0.0, 0.25, 0.5, 1.0\}` exposed a strict verification hierarchy:

| Generator Backbone | Clean -> `100%` Corrupted Accuracy | `5`-Sample Self-Consistency Agreement (`Clean -> Corrupted`) | `Check B`: Shared-Evidence Validator Flag Rate (`p = 1.0`) | `Check C`: Independent-Provenance Oracle Flag Rate (`p = 1.0`) | Exact McNemar (`Check C` vs. `Check B`) |
|:-------------------|:-----------------------------------|:-------------------------------------------------------------|:-----------------------------------------------------------|:---------------------------------------------------------------|:----------------------------------------|
| **`Mistral-7B` (`n = 60`)** | **`0.50 -> 0.00`** | `0.55 -> 0.59` *(confident & `100%` wrong)* | **`35%`** (`[0.23, 0.47]`; `65%` silent error) | **`77%`** (`[0.65, 0.87]`; `23%` silent error) | **`p = 5.96 x 10^-8`** (`25` `C`-only vs. `0` `B`-only) |
| **`DeepSeek-R1-8B` (`n = 40`)** | **`0.35 -> 0.03`** | `0.26 -> 0.20` | **`68%`** (`[0.53, 0.80]`; `32%` silent error) | **`90%`** (`[0.80, 0.97]`; `10%` silent error) | **`p = 0.003906`** (`9` `C`-only vs. `0` `B`-only) |

On **every single corrupted item** across both models (`0` exceptions out of `100` trials), `Check C` flagged every case `Check B` caught plus `25` (`Mistral-7B`) and `9` (`DeepSeek-R1-8B`) additional silent errors where the generator computed ratios faithfully from the corrupted passage.

---

## Actionable Takeaways

1. **Cross-check numerical RAG outputs against a second provenance-independent source (`Check C`)**: Self-consistency measures decoding stability conditioned on the prompt—not source truth (`0.59` agreement at `0.00` accuracy)—and shared-evidence validators miss `32%–65%` of corrupted upstream figures. Cross-verify extracted filing prose numbers against structured XBRL/EDGAR CompanyFacts API records or independent market feeds before surfacing quantitative claims.
2. **Namespace all shared multi-agent state and tool caches by `(entity_ticker, fiscal_period, source_id, route)`**: Require downstream validators to assert exact entity/ticker and fiscal-period match between the user query and every read memory key so passing arithmetic/format checks (`2/2` in `E6`) never mask cross-company cache contamination.
3. **Keep discrete taxonomy routing on small encoder classifiers (`~400M`) and financial calculations in deterministic `Python`**: Reserve generative/reasoning token budgets for multi-passage synthesis and contradiction resolution rather than `4`-way intent classification (`9.9x` slower and `-18` pp less accurate on `DeepSeek-R1-8B`) or arithmetic (`29%–72%` on `7B–8B` LLMs vs. `100%` in `Python`).

## Related Artifacts

- [`rag-hallucination-repair`](../skills/rag-hallucination-repair/SKILL.md) — Claim-level source verification and repair (`arXiv:2608.29307`)
- [`rag-evidence-triage`](../skills/rag-evidence-triage/SKILL.md) — Classifying retrieved evidence sufficiency and conflict (`arXiv:2608.27661`)
- [`receipt-bound-mcp-prose-supervision`](../skills/receipt-bound-mcp-prose-supervision/SKILL.md) — Provenance-gated durable memory and wire-mirror de-syndication (`Epistemic Guard`, `arXiv:2611.27095`)
- [`rules/adk-security-and-evaluation.md`](../rules/adk-security-and-evaluation.md) — `"DON'T: Feed unverified single-sided evidence passages into fact-checking judges without provenance and rebuttal checks"`
- [`rules/skill-system-design.md`](../rules/skill-system-design.md) — `"DO: Keep deterministic steps in code and explicit graph edges; delegate to LLMs only for reasoning"`
