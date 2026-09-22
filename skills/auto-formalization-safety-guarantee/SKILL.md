---
name: auto-formalization-safety-guarantee
description: >
  Generate executable programs with machine-checkable safety guarantees
  by auto-formalizing domain APIs into a verification-aware intermediate
  language (Dafny), verifying generated code against frozen
  specifications, and compiling back to the target language.
  Derived from "MAGS: Multi-agent Auto-formalization Guarantees Safety
  for Agentic Outputs" (arXiv:2609.19391).
source: https://arxiv.org/abs/2609.19391
---

# Auto-Formalization Safety Guarantee (MAGS)

Use this skill when agent-generated code must satisfy safety properties
that testing alone cannot guarantee — and you want machine-checkable
proofs rather than test-based confidence.

## When to Use

- Agent generates code in safety-critical domains (CUDA kernels,
  system scripts, robotic control, infrastructure automation)
- Fuzz testing / static analysis is insufficient — you need guarantees
  over ALL inputs, not just tested ones
- You want to reuse safety specifications across many generated
  programs in the same domain
- Human review of every generated program is infeasible at scale

## Core Insight

Separate the language in which a program **executes** from the language
in which its safety is **proved**. Auto-formalize domain APIs and
safety requirements once (human-audited, then frozen), then verify
every generated program against those frozen specs using Dafny as a
shared intermediate representation. This prevents proof agents from
weakening safety definitions to pass individual benchmarks.

**Evidence**: 100% verification success rate across 220 examples (100
CUDA kernels, 100 terminal scripts, 20 robotic tasks). Independent
safety oracles confirmed: CUDA 100/100, Robotics 20/20, Terminal
82/100 (gaps from incomplete API formalization). Cost: ~36–68 min and
$8.60–$10.17 per sample.

---

## Procedure

### 1. Construct Domain Semantics (One-Time Cost)

Build reusable, frozen specifications for each domain:

1. **Write core logic foundations** — small human-authored logical
   primitives defining abstract state and safety properties (e.g.,
   fractional permission separation logic for CUDA memory safety)
2. **Auto-formalize API semantics** — LLM agents derive formal specs
   from official API documentation; a critic agent checks faithfulness,
   consistency, and modularity
3. **Audit** — manually review a random 20% of generated semantics
   for structural errors, overly strong preconditions, unchecked safety
   conditions, or deviations from core logic
4. **Probe test** — generate 3 safe + 3 unsafe probe programs
   independently of the semantics; all safe must verify, all unsafe
   must be rejected
5. **Freeze** — lock the semantic library; no downstream agent can
   modify it during program verification

### 2. Translate to Verification Language

For each generated program:

1. A translation agent converts the program into Dafny and attaches
   the required safety specifications from the frozen library
2. A critic agent checks translation faithfulness
3. If the program uses unsupported APIs, extend semantics using the
   same pipeline (Step 1) — existing frozen specs remain locked

### 3. Plan and Execute Proof Strategies

1. A planning agent generates **multiple candidate proof strategies**
   and lightweight annotation sketches
2. Probe each strategy with the Dafny verifier before full integration
3. Explore plans **in parallel** — each initializes an independent
   annotation-repair process
4. First add proof annotations without changing executable behavior;
   permit code repair only if annotations alone fail
5. Critics review annotations for faithfulness and repairs for
   functional preservation
6. **Deterministic checks reject**: `assume`, axioms, disabled
   verification, or any proof-bypassing construct
7. Try up to 8 solver seeds and multiple verifier configs; accept if
   any attempt verifies within 500s

### 4. Compile Back to Target Language

1. Use Dafny's built-in compiler to emit target-language code
2. Apply **deterministic symbol substitution** to map verification
   API symbols back to real domain APIs
3. This step is mechanical, not generative — verified guarantees carry
   over when the mapping preserves formalized API semantics

### 5. Validate Functional Preservation

1. Run held-out functional tests (never exposed to proof agents)
   against both original and verified programs
2. Confirm non-decreasing functional behavior — verification should
   not achieve safety by removing functionality
3. If functional tests fail: inspect whether repair agents converged
   to vacuous solutions (safe but non-functional)
4. Mitigation: add lightweight task-specific success constraints
   during repair (not part of formal safety certificate)

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Incomplete API formalization | Safety-relevant API behavior not captured in specs | Audit 20% sample; probe with safe/unsafe programs; expand semantics incrementally |
| Vacuous safety (functionally dead code) | Repair agents remove behavior to satisfy specs | Add task-specific success steering constraints; run held-out functional tests |
| Proof-bypassing constructs | Agent inserts `assume` or disables verification | Deterministic syntactic checks reject these before acceptance |
| SMT solver instability | Same program verifies/fails non-deterministically | Try 8 solver seeds × multiple configs; accept if any verifies |
| Specification weakening | Agent modifies frozen specs to make verification easier | Freeze semantics before program verification; sandbox agents from spec files |
| High latency / cost | 36–68 min, $8–10 per sample | Best suited for safety-critical code, not rapid prototyping; reuse tactic library |

> Source: Wu et al., "MAGS: Multi-agent Auto-formalization Guarantees
> Safety for Agentic Outputs" (arXiv:2609.19391), Sep 2026.
