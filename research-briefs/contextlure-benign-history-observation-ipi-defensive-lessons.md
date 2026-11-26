# ContextLure: How Read-Only Access to Benign Conversation History Amplifies Indirect Prompt Injection (Defensive Lessons)

> **Source**: *ContextLure: Exploiting Benign Conversation History for Indirect Prompt Injection* (`arXiv:2611.31424`, 2026) — **Strictly Defensive Summary** (per [`output/AGENTS.md`](../AGENTS.md); zero injection-rewriting prompt templates or framing strings are reproduced here; focus is strictly on session-history read scoping and provenance-vs-permission authorization boundaries).

## Threat Model & Core Insight

Prior multi-turn and memory-injection studies (`MemHarmBench`, `Memory Injection`) assume the attacker **writes** malicious fragments into earlier turns or long-term memory. `ContextLure` isolates a strictly weaker, widespread deployment exposure: **what happens when an external untrusted source (or a read-scoped plugin, shared workspace observer, CC'd email thread, or leaked support transcript) merely *observes* a short, `100%` benign prior conversation prefix before delivering a single one-shot untrusted data item ($N_{\mathrm{payload}} = 1$, zero prior poisoning, zero within-episode retry feedback)?**

Prepending a frozen **`5`-message benign dialogue prefix** (sampled from `ABCD` and `Taskmaster-1/3`) to `AgentDojo` and `InjecAgent` episodes across multiple victim LLMs (`Qwen3.5-27B`, `Qwen3.6-35B-A3B`, `DeepSeek-V4-Flash`, `MiniMax-M2.7`, `GLM-5.1`), the paper shows that anchoring an external untrusted message to **verifiable facts from earlier benign turns** causes tool-using LLMs and existing prompt-level defenses to conflate **provenance continuity** ("this references a real earlier turn in the user's session") with **action authorization** ("the user authorized this side-effecting tool call").

---

## Key Empirical Findings & Manuscript Discrepancy Note

> **Manuscript Discrepancy Note (`Abstract` vs. `Table 1` / `§5.1` / `Appendix Table 3`)**: The Abstract (`p. 1`) and Introduction (`§1`) state *"we reach `67.4%` ASR on AgentDojo and `87.3%` on InjecAgent."* However, **`Table 1`, `§5.1`, and `Appendix Table 3` explicitly record `AgentDojo` (`Qwen3.5-27B` Overall) `(ASR, UA, JSR) = 33.8% / 67.4% / 16.3%`**—showing that `67.4%` in `Table 1` is **Utility under Attack (`UA`)**, while Overall `ASR` is **`33.8%`** (up from `20.3%` benchmark default, with suite `ASR` reaching **`74.70%` on `Banking`**, `40.8%` on `Slack`, `37.5%` on `Travel`, and `21.10%` on `Workspace`, and `Qwen3.6-35B-A3B` reaching **`84.0%` `ASR`** on `Task-Events` in `Table 5`). Both exact figures are preserved below.

### 1. One-Shot Benign-History Grounding Multiplies Hijacking Across Benchmarks & Models (`Tables 1, 3–5`)

- **`AgentDojo` (`Qwen3.5-27B` Overall, `Table 1`)**:
  - `Benchmark Default` (`ASR / UA / JSR`): `20.3% / 73.7% / 5.2%` $\to$ **`ContextLure`: `33.8% / 67.4% / 16.3%`** (`+13.5` pp `ASR`, **`3.1x` Joint Success Rate `JSR`** where both the benign user task and unauthorized tool call complete).
  - Consistent gains across all `4` evaluated backbones (`Appendix Table 3`): `GLM-5.1` `6.7% -> 11.2%`, `MiniMax-M2.7` `10.5% -> 20.0%`, `DeepSeek-V4-Flash` `23.9% -> 41.1%`, and `Qwen3.5-27B` `20.3% -> 33.8%`.
- **`InjecAgent` (`Qwen3.5-27B`, `Table 1`)**:
  - Overall `ASR` more than doubled from `40.8%` (`34.1%` Direct Harm / `47.0%` Data Stealing) to **`87.3%` (`+46.5` pp; `81.0%` Direct Harm / `93.3%` Data Stealing)**.
- **Controlled ablation isolating benign-history observation (`Tables 4–5`)**:
  - Compared against matched rewriting *without* benign-history exposure (`Low-Impact` baseline), grounding in the `5`-turn benign prefix lifted matched `AgentDojo` `ASR` (`N = 74` Overall / `N = 34` Travel) by **`+14.9` pp (`95%` CI `[1.4, 28.4]`) / `+41.2` pp (`[20.6, 61.8]`)** and `InjecAgent` (`N = 198`) by **`+39.9` to `+46.5` pp**.
  - On `Qwen3.6-35B-A3B` (`Table 5`), task-event grounding jumped `ASR` from **`16.8%` to `84.0%` (`+67.2` pp)**.

### 2. Existing Prompt & Classifier Defenses Degrade Sharply Under Verifiable History Citations (`Table 7`)

On `AgentDojo` (`ASR / UA %`, comparing `Benchmark Default` vs. `ContextLure [Evidence + Rewriting]`):

| Defense Layer | Default `ASR / UA` | With Benign-History Grounding (`ASR / UA`) | Defensive Limitation Exposed |
|:---|:---|:---|:---|
| **No defense** | `24.6% / 71.1%` | **`44.6% / 62.6%`** | Model treats accurate citation of earlier user turns as continuation authority |
| **Data delimiting (`Spotlighting`)** | `5.2% / 70.1%` | **`27.6% / 64.9%`** (`5.3x` `ASR`) | Delimiters mark channel origin (`data`), not whether cited prior context authorizes a write |
| **User-instruction repetition (`Sandwiching`)** | `2.3% / 74.2%` | **`21.6% / 68.0%`** (`9.4x` `ASR`) | Benign-history continuity bridges the repeated user goal to the side-effecting call |
| **Instructional prevention** | `5.8% / 72.5%` | **`19.4% / 66.8%`** (`3.3x` `ASR`) | Prompt-level rules yield when untrusted text frames action as resolving a prior turn |
| **`Lakera Guard`** | `3.1% / 69.5%` | **`16.5% / 63.4%`** (`5.3x` `ASR`) | Context-consistent operational prose lacks overt jailbreak lexical signatures |
| **`PI detector` (strict classifier)** | `1.9% / 35.1%` | **`6.2% / 28.2%`** (`3.3x` `ASR`) | Lowest `ASR`, **but destroys benign utility (`28.2%` `UA`)** via false positives |

---

## Defensive Architecture Lessons

> **Empirical Scope Note (`§6` & `Appendix D.2`)**: `ContextLure` empirically benchmarks the `5` prompt/detector defenses above (`Table 7`), while explicitly noting that its recommended authorization-boundary mitigations are architectural prescriptions rather than defenses empirically benchmarked inside `Table 7` (*"We do not infer the effectiveness of an untested authorization rule from the existing defense bars"*). Pairing `ContextLure`'s empirical failure diagnosis with our validated capability-gate studies (`CapLite` `arXiv:2611.17115`, `Conflux` `arXiv:2611.08768`, `Baya` `arXiv:2611.06039`) yields three concrete controls:

1. **Treat prior benign conversation transcripts as confidential session capabilities—never ambient read state**:
   - Do not expose full prior chat transcripts to third-party MCP plugins, webhook enrichers, public support threads, or untrusted retrieval routers (`read-only` transcript access alone suffices to raise downstream one-shot `InjecAgent` `ASR` from `40.8% -> 87.3%` and bypass `Spotlighting` `5.2% -> 27.6%`). Pass external read tools only minimal query parameters stripped of prior dialogue turns.
2. **Never equate verifiable provenance of a cited historical turn with permission to execute a tool**:
   - Even if an external email, ticket, or document accurately quotes a real timestamp, order ID, or topic from Turn `1–5` of the user's session, **untrusted external channels carry zero write/effect authority**. Authorize every side-effecting tool call and destination argument strictly against the **current authenticated user request** or a pre-read germline write plan (`CapLite`, `Germline`, `Conflux` Principal Context intersection), never because external data matches earlier session context.
3. **Avoid tightening lexical `PI detectors` to compensate for context-grounded IPI**:
   - Lowering classifier thresholds held `ASR` to `6.2%` only by collapsing `Utility under Attack` to `28.2%`; enforce deterministic write-boundary authorization instead of text-classifier sensitivity escalation.

---

## Why Not a Standalone Skill?

Per [`output/AGENTS.md`](../AGENTS.md) (`Lines 69–70`), indirect prompt-injection attack papers are distilled strictly for **defensive scoping and authorization lessons** (omitting payload-rewriting procedures), and `ContextLure`'s own authorization discussion (`Appendix D.2`) is architectural rather than a newly benchmarked standalone implementation—making it an ideal evidence addition alongside [`schema-derived-write-integrity-gate`](../skills/schema-derived-write-integrity-gate/SKILL.md), [`germline-isolated-tool-execution`](../skills/germline-isolated-tool-execution/SKILL.md), and [`principal-context-permission-intersection`](../skills/principal-context-permission-intersection/SKILL.md) in [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

## Related Artifacts

- [`tact-bench-adaptive-conversational-threats-pst`](tact-bench-adaptive-conversational-threats-pst.md) — How completing a benign prior task in-session raises conversational `AFR` by `+17.01` pp (`TrustPrime`, `arXiv:2611.31756`)
- [`memharmbench-cross-session-memory-injection`](memharmbench-cross-session-memory-injection.md) — Active cross-session memory write poisoning vs. `ContextLure`'s passive read-only benign-history observation (`arXiv:2611.01700`)
- [`schema-derived-write-integrity-gate`](../skills/schema-derived-write-integrity-gate/SKILL.md) — Pre-read write commitment and request-literal authority grounding (`CapLite`, `arXiv:2611.17115`)
- [`germline-isolated-tool-execution`](../skills/germline-isolated-tool-execution/SKILL.md) — Data-free germline destination authorization (`arXiv:2611.06585`)
- [`principal-context-permission-intersection`](../skills/principal-context-permission-intersection/SKILL.md) — Pointwise ACS permission intersection across influencing principals (`Conflux`, `arXiv:2611.08768`)
