# GVS5H: Zero-Shot Self-Orchestration with Ledger-Based Control

> **Paper**: [Zero-Shot Self-Orchestration with Ledger-Based Control for Improved LLM Coding Performance](https://arxiv.org/abs/2608.26480) (arXiv:2608.26480v1)  
> **Code**: [slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)  
> **Praxis source**: src:2608-26480v1  
> **Related Skill**: [`ledger-orchestrated-coding-loop`](../skills/ledger-orchestrated-coding-loop/SKILL.md)

---

## Executive Overview

This paper introduces **GVS5H**, a training-free, zero-shot manager-worker scaffold operating over a shared filesystem workspace (`plan.md`, `notes.md`, `tasks.json`, `solution.py`). The core headline claim is that un-tuned, locally-hosted **Qwen3.8-27B** matches **Claude Fable 5** on the 100 latest Hard problems of LiveCodeBench (`release_v6`).

While the headline claim is technically reproducible within their evaluation protocol, cross-examination reveals a crucial structural asymmetry: **Fable 5 was evaluated single-call with zero execution**, whereas Qwen3.8-27B received up to 10 rounds of test-driven refinement grounded in actual Python subprocess test execution.

---

## Core Concept & Architecture

Instead of accumulating multi-turn conversation logs inside a single expanding context window, GVS5H decouples coordination into an external file ledger:

1. **Filesystem Ledger**: Subagents receive fresh zero-shot contexts containing only the current task, overarching strategy, curated notes (<800 words), and existing code.
2. **Structural Code-Ban During Ideation**: The initial worker is explicitly prohibited from writing code blocks, forcing prose analysis of algorithmic complexity ($O(N \log N)$ vs $O(N^2)$) and mathematical reductions before syntax generation.
3. **Subprocess Test Execution & Veto**: The harness executes candidate programs against public sample tests. If tests fail, the harness programmatically overrides the manager's `done` declaration and forces an iterative repair cycle.
4. **Active Memory Compaction**: Workers are instructed to rewrite `notes.md` to under 800 words, actively purging disproven hypotheses.

---

## Key Findings & Empirical Analysis

### 1. Benchmark Results (LiveCodeBench Hard, 5 Passes, 128k Cap)
* **Claude Fable 5 (Single Call, Unassisted)**: $87.4\% \pm 1.1\%$ — Cost: **$61.11** / 100 problems.
* **Qwen3.8-27B (Single Call, 128k Cap-Matched)**: $63.0\% \pm 4.1\%$ — Cost: **$20.44** / 100 problems.
* **Qwen3.8-27B + GVS5H Scaffold**: **$86.4\% \pm 2.7\%$** ($+23.4$ pts, $p = 0.73$ vs Fable 5) — Cost: **$51.75** / 100 problems (or free on local GPU).
* **GPT-5.6-Terra + GVS5H Scaffold**: **$85.0\% \pm 0.0\%$** ($+8.0$ pts vs single call) — Cost: **$11.71$** / 100 problems (**19% of Fable 5 cost**).
* **Claude Opus-5 + GVS5H Scaffold (Single Pass)**: **$91.0\%$** (Highest absolute score observed).

### 2. The Context Collapse & Runaway Deliberation Trap
Why did single-call Qwen3.8-27B score so poorly (63.0%)? The paper discovered a severe pathology: **degenerative reasoning loops**.
* On problem `abc399_e`, single-call Qwen spent the entire 250,000-token budget repeating the phrase *"Alphabet 5 with a<->b... no"* **7,743 times** without terminating.
* 35 of 500 single-call problem-passes failed simply because the model talked past the token limit without emitting code.
* The manager rescued 25 of these 35 empty cells (+5.0 percentage points of the +23.4 gain came purely from preventing truncation).

### 3. Non-Monotonicity and Negative Transfer on MoE
The scaffold is not universally beneficial:
* On **Qwen3.6-35B-A3B** (MoE with 3B active parameters), the scaffold caused a **net drop** ($-1.2$ pts at 16k, $-9.0$ pts at 128k with reasoning off).
* The ideation stage talked the model *out* of optimal algorithms (e.g. rejecting Convex Hull Trick DP as "too complex for Python" and picking a slow $O(N^3)$ approach).

### 4. LiveCodeBench Evaluator Bug Discovery
The authors uncovered a major defect in the official LiveCodeBench harness: `sys.stdin.buffer.readline()` was mocked statelessly as `inputs.split(b"\n")[0]`.
* Competitive programming fast-IO idioms used by Qwen failed 97% of the time on the official evaluator despite producing correct code.
* Replacing the mock binary view with a `BytesIO` stream restored correct grading across models without re-running generations.

---

## Relevance to Praxis & Agent Engineering

1. **Inference-Time Circuit Breakers for Mid-Sized Models**: Mid-sized models often possess competitive code generation ability but lack calibrated reasoning self-termination. External scaffolds act as a circuit breaker, preventing runaway loops.
2. **Economic Frontier Parity**: Using GPT-5.6-Terra with a manager matches Fable 5's single-call accuracy at 19% of the cost ($11.71 vs $61.11 per 100 problems).
3. **Execution Grounding Overcomes Raw Scale**: A 27B model equipped with subprocess execution feedback matches a frontier model operating blind, highlighting that tool grounding frequently dominates raw model scale.
