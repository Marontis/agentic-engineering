# Reglos: A Self-Evolving Personal Memory Agent with Recursive Self-Improvement

> **Source**: [arXiv:2611.06049](https://arxiv.org/abs/2611.06049) | `src:2611-06049v1`
> **Authors**: Sen Yang, Jiaduo Lin, Zehong Huang, Wen Liu (Reglos.ai)
> **Date**: November 2026

## Executive Summary

Personal memory agents must adapt across two distinct timescales: an **inner loop** (Level 4 environment adaptation) that continuously extracts, updates, retracts, and consolidates facts about an individual user over months of conversation, and an **outer loop** (Level 2 strategy autonomy) that evolves the memory harness itself—its extraction schemas, recall routing, and reader policies—from observed failures. Most existing self-improving memory systems either mutate prompts directly on benchmark validation sets (which overfits rapidly) or optimize memory storage and retrieval while ignoring how the downstream reader model actually consumes retrieved memories.

Yang et al. present **Reglos**, a bitemporal Rust/PostgreSQL 16 memory engine paired with a Python harness whose code and prompts are evolved via a three-role outer loop (`Claude Opus 5.5` proposer on raw failure traces, cross-family `GPT-6.1 Sol` critic screening against label/template shortcuts, and a frozen evaluator enforcing cross-split and cross-reader acceptance gates). Tracing `159` development failures on `PersonaMem-v2` revealed a striking bottleneck: while `48%` of failures involved facts never stated in the conversation (setting an `~80%` ceiling), **`31%` occurred when the required evidence was already present in context but the reader chose wrongly**, compared to `16%` never written to memory and only `4%` written but not recalled. Guided by these traces, Reglos evolved tombstone-aware retraction, distinct-word per-option recall with raw excerpts, and an explicit memory-use policy—achieving state-of-the-art results across `PersonaMem-v2` (`61.3%`), `LongMemEval-S` (`84.0%` / `87.2%`), `LoCoMo` (`87.2%` / `89.5%`), and `BEAM` 500K (`65.0%`).

---

## Key Findings

1. **Reader Utilization—Not Retrieval Recall—Is the Largest Reachable Failure Mode in Agent Memory**:
   - Across `159` traced failures on `PersonaMem-v2`, `48%` were unanswerable from the transcript (`~80%` ceiling), **`31%` had the supporting evidence already in the retrieved context**, `16%` missed extraction at write time, and only `4%` failed retrieval after being written.
   - Simply injecting Reglos's evolved **memory-use policy** (how to weigh incomplete memories, sensitive identifiers, and retracted facts) into competing memory engines lifted every baseline by **`+3.3` to `+6.3` percentage points** on `PersonaMem-v2` (`EverOS` `53.6% -> 58.9%`, `MemOS` `53.8% -> 58.4%`, `Raw retrieval` `53.3% -> 58.1%`, `Full context` `49.3% -> 55.6%`, `Mem0` `45.0% -> 50.5%`), though Reglos (`61.3%`) still outperformed all policy-augmented baselines by `+2.4` to `+10.8` points.

2. **Naive Deletion Fails on User Retractions; Tombstone Records + Reader Policy Are Required**:
   - In the seed system (`0/9` forgetting accuracy on development), telling an agent *"please forget that I take sertraline"* caused the extractor to store the retraction sentence itself as an emphasized memory, or left stale derived preferences active.
   - Reglos implements **bitemporal tombstone retraction**: each fact tracks both world validity (`valid from`, `valid to`) and belief lineage (`ingested at`, `expired at`). A retraction matches existing records at cosine similarity $\ge 0.68$ or trigram overlap $\ge 0.6$ (expiring at most `6` facts per explicit forget request and `2` per correction) and writes an explicit tombstone record surfaced in context alongside an explicit policy not to re-infer expired facts. This raised forgetting accuracy from **`0/9` to `8/9`** on development, **`12/14`** on a held-out slice, and **`63.1%`** on the 5,000-question `PersonaMem-v2` test set (vs. `EverOS` `42.8%` and `Mem0` `11.8%`).

3. **Prompt-Only Harness Optimization Overfits; Code+Policy Evolution Requires Cross-Split and Cross-Reader Gating**:
   - Running a GEPA-style prompt-only optimizer over harness text gained **`+3.8` points** on the selection split but only **`+1.1` points** on unseen questions.
   - Reglos guards its outer loop with three structural gates: (a) the proposer (`Claude Code` / `Claude Opus 5.5`) inspects raw failure traces to propose code and policy edits; (b) a cross-family critic (`Codex` / `GPT-6.1 Sol`) rejects benchmark-specific option-template heuristics; and (c) a frozen evaluator accepts a commit only if it improves **both** persona-disjoint halves of the `1,317`-question validation set under `Qwen3.8-27B` while costing the second reader (`GPT-5.6 Luna`) at most `1.0` point.
   - Across four accepted outer-loop steps on the `1,317` validation questions, accuracy rose monotonically on the held-out trajectory: `seed` (`54.2%`) $\to$ `v1` (+ tombstone context & memory-use policy: `57.1%`) $\to$ `v2` (+ per-option recall on full option text: `56.4%`) $\to$ `v3a` (+ revised policy on incomplete memory & sensitive identifiers: `60.2%`) $\to$ `v3` (+ per-option recall on distinct option words & raw excerpts: **`60.7%`**, `+6.5` points total).

4. **Hybrid 6-Route Recall + Raw Excerpts Prevents Perspective and Temporal Collapse**:
   - Reglos fuses six recall routes via weighted Reciprocal Rank Fusion ($k = 60$, top `45` items / `8,100` tokens, `2.5 s` per-route timeout). Preserving **raw conversation excerpts** alongside user-centric extracted facts raised `LongMemEval-S` accuracy on `"Assistant said"` questions ($n = 56$) to **`98.2%`** vs. `EverOS` **`67.9%`**, and bitemporal date indexing achieved **`83.2%`** on `LoCoMo` Temporal questions ($n = 321$) vs. `Mem0` **`5.0%`** (which stores memories without dates).
   - Disabling model reasoning (`<think>`) during memory extraction reduced output tokens by **`75%`** (to one quarter) and per-call write latency from **`9.3 s` to `2.6 s`** without degrading recall quality.

---

## Quantitative Summary

All memory stores were populated using `Qwen3.8-27B` (non-thinking mode) for fair comparison across systems and evaluated with two distinct readers: `Qwen3.8-27B` and `GPT-5.6 Luna`.

| Benchmark / Slice | Reglos (`Qwen3.8-27B` / `GPT-5.6 Luna`) | Competing Memory Systems (`Qwen3.8-27B` / `GPT-5.6 Luna`) | Key Comparison / Insight |
|:---|:---|:---|:---|
| **`PersonaMem-v2`** (`5,000` official test questions) | **`61.3%` / `57.5%`** | `MemOS`: `53.8%` / `50.5%`<br>`EverOS`: `53.6%` / `49.6%`<br>`Raw retrieval`: `53.3%` / `50.6%`<br>`Full context`: `49.3%` / `44.6%`<br>`Mem0`: `45.0%` / `45.2%`<br>`No memory`: `40.0%` / `30.6%` | Beats all baselines by **`+7.5` to `+16.3` pts** (`+2.4` to `+10.8` pts even after giving baselines Reglos's memory-use policy); beats prior best published `MemStack` (`57.2%`) |
| **`PersonaMem-v2` Sub-Slices** (`Qwen3.8-27B`: Sensitive Info / Forgetting / Third-Party Prefs) | Sensitive: **`91.4%`**<br>Forgetting: **`63.1%`**<br>3rd-party ($n=522$): `20.5%` | Sensitive: `42.9%–47.6%`<br>Forgetting: `MemOS` `61.3%`, `EverOS` `42.8%`, `Mem0` `11.8%`<br>3rd-party: `19.0%–20.3%` | **`+43.8` pts** on sensitive identifiers; third-party preferences remain below chance (`25%`) for all systems |
| **`LongMemEval-S`** (full / `Assistant said` $n=56$) | **`84.0%` / `87.2%`**<br>(`83.4%` excl. 54 dev; `Assistant said`: **`98.2%`**) | `EverOS`: `80.4%` / `80.0%` (`Assistant said`: `67.9%`)<br>`Raw retrieval`: `78.8%` / `80.8%`<br>`MemOS`: `73.0%` / `74.0%`<br>`Full context`: `68.0%` / `68.8%`<br>`Mem0`: `65.6%` / `64.4%` (`Zep` 100-q sample: `34.0%` vs. Reglos `79.0%`) | Raw excerpt retention prevents assistant-turn loss (`+30.3` pts over `EverOS` on `Assistant said`) |
| **`LoCoMo`** (overall / Temporal $n=321$) | **`87.2%` / `89.5%`**<br>(Temporal: **`83.2%`**) | `EverOS`: `81.5%` / `86.1%`<br>`MemOS`: `75.7%` / `78.8%`<br>`Mem0`: `57.8%` / `62.4%` (Temporal: `5.0%`) | Bitemporal indexing yields **`+78.2` pts** over undated `Mem0` on temporal reasoning |
| **`BEAM` Long-Context** (`100K` / `500K` / `1M` sample) | `Qwen`: `67.9%` / `65.6%`<br>`Luna`: `65.9%` / **`65.0%`**<br>(`1M` 40-q sample: **`67.6%`**) | `MemOS` (`500K` Luna): `61.3%`<br>`Mem0` (`1M` sample): `64.3%` | Ranks 1st at `500K` (`GPT-5.6 Luna`) and on `1M`-token sample |
| **Growing History Stability** (`40` personas, `296` Q1 questions at `25%` $\to$ `100%` history) | **`59.1%`** (`25%`) $\to$ **`60.5%`** (`100%`) (range `55.7%–60.5%`) | Beats `Raw retrieval` by `1.0–5.1` pts and `Full history` by `3.7–10.5` pts | Zero degradation as distraction history grows `4x` |

---

## Why Not a Skill?

Reglos describes an end-to-end personal memory product architecture (a bitemporal Rust/PostgreSQL 16 storage engine coupled with a 6-route hybrid retriever and a outer-loop evolution harness tailored to conversational QA). Its transferable methodological contributions—such as cross-split/cross-reader acceptance gates for recursive harness evolution, tombstone retraction with reader-side policy enforcement, and pairing extracted facts with raw excerpts—directly strengthen existing rules in `recursive-improvement.md` and `skill-system-design.md` rather than constituting a new standalone subtask procedure.

---

## Actionable Takeaways

1. **Pair every memory retrieval upgrade with an explicit reader memory-use policy**: Because `31%` of conversational memory failures happen *after* the right evidence is placed in the prompt (nearly `8x` the `4%` retrieval-miss rate), explicitly instruct the reader model on how to resolve partial matches, sensitive identifiers, and superseded claims before tuning retrieval weights.
2. **Implement user retractions as surfaced bitemporal tombstones, not silent deletions or append-only notes**: When a user corrects or retracts a fact, expire matching records (cosine $\ge 0.68$ or trigram overlap $\ge 0.6$, capped at `6` facts for forget requests and `2` for corrections) *and* inject an explicit tombstone notice into the reader context so the LLM does not re-infer the retracted fact from surrounding conversation turns.
3. **Retain raw turn excerpts alongside distilled user facts**: User-centric fact extractors systematically discard what the *assistant* previously recommended or stated (`67.9%` on `EverOS`); indexing raw dialogue excerpts alongside structured facts raises assistant-turn recall to `98.2%`.
4. **Disable chain-of-thought reasoning during routine fact extraction**: Running extraction models in non-thinking mode cuts output token volume by `75%` and reduces write latency by `3.6x` (`9.3 s -> 2.6 s`) with no loss in downstream QA accuracy.
