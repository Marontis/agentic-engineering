---
name: certified-task-verifier-harness
description: >
  Synthesize and certify executable task verifiers for agent tasks without
  ground-truth tests by isolating generation from scoring, prepending an
  observable-evidence header with state-over-dialogue precedence, mounting an
  on-demand domain-rule library, enforcing nine anti-leniency and
  weakest-comparison authoring principles, and certifying verifiers through a
  five-gate probe and single-repair harness. Derived from "Veritas: A
  Verifier Generation Harness for Agent Tasks" (arXiv:2611.13336).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Certified Task Verifier Harness

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Use this skill when you need **executable, deterministic-first task verifiers** (`evaluate(...) -> bool` scripts or automated grading harnesses) for agentic workflows—such as customer-support tool trajectories, repository patches, container/CLI administration, or scientific computing pipelines—where:

- **Hand-written tests do not exist at scale** (for example, synthesizing RLVR reward checkers, gating self-evolving memory/skill updates, or grading production agent rollouts from task descriptions $T$ and initial environments $\mathcal{E}_0$).
- **Plain coding harnesses produce erratic or non-delivering verifiers**: with the *exact same* backbone (`GLM-5.2`), seven unmodified agent harnesses span `0.164` to `0.726` $\kappa^*$ on $\tau^2$-bench and `-0.201` to `0.474` on `TB-Science 0.1`.
- **Existing benchmark or human-written verifiers require pre-use auditing** before serving as evaluation ground truth or training reward signals.

Do **not** use this skill for formal mathematical proof synthesis over pure functions where specifications already compile in Dafny or Lean (use [`three-surface-verified-code-audit`](../three-surface-verified-code-audit/SKILL.md)), or for unit-test mock contract validation inside an existing test suite (use [`contract-verified-test-mock-generation`](../contract-verified-test-mock-generation/SKILL.md)).

## Overview

Hand-written and agent-generated verifiers fail in **opposite directions** (`arXiv:2611.13336`):

- **Official hand-written verifiers fail mainly by false acceptance (excess leniency) and nondeterminism**: execution-backed audits confirmed defects in `27/82` public headless tasks in `Agents' Last Exam` (`91` too-lenient findings out of `158` refuted-surviving issues across `~43,000` LOC), `57/146` $\tau^2$-bench tasks (`24` airline tasks pass a no-op database comparison; `33` accept near-misses), `36/106` `DeepSWE` tasks (awarding full marks when one hunk of the gold patch is deleted), and `72/500` `MCP-Atlas` tasks flipping shared LLM-judge verdicts on identical inputs at `temperature=0` (`Table 8`).
- **Generated verifiers fail mainly by non-delivery and false rejection (excess strictness)**: plain coding agents explore until timeout without writing the verifier file (`67/189` missing verdicts for `pi` on `Terminal-Bench 4.0`), confuse exploration-time filesystem visibility with judgment-time evidence, miss unstated domain policy obligations, or assert brittle exact string equality that rejects valid reference solutions.

`Veritas` (`arXiv:2611.13336`) closes these gaps with a four-stage harness (`Packaging -> Generation -> Probe & One Repair -> Delivery`) built around three composable prompt/filesystem mechanisms: **Observable-Evidence Header (`E`)**, **Filesystem Domain Rule Library (`R`)**, and **Nine Authoring Principles (`H`)**. Holding `GLM-5.2` fixed, `Veritas` (`OpenCode + ERH`) ranks **#1 on all four execution-scored benchmarks**—`0.787` $\kappa^*$ on $\tau^2$-bench, `0.720` on `SWE-bench Verified`, `0.465` on `Terminal-Bench 4.0`, and `0.548` on `TB-Science 0.1`, plus `0.980` (`JudgeBench`) and `0.920` (`LLMBar`) two-order-consistent pairwise accuracy—while consuming fewer tokens than plain `OpenCode` (`97.0M` vs. `104.5M` prompt tokens on $\tau^2$-bench). Adding `ERH` unchanged to `OpenCode`, `Codex CLI`, and `Claude Code` improves `9/12` execution-scored pairs, lifting `Claude Code` from `0.238` to `0.586` (`+0.348`) on `Terminal-Bench 4.0` and from `0.144` to `0.465` (`+0.321`) on `TB-Science 0.1`.

---

## Step-by-Step Procedure

### Step 1: Package `(T, E_0)` with Layout-Enforced Generation–Scoring Isolation

Before launching the verifier-authoring agent, enforce a hard information barrier by module and container layout:

1. **Package only generation-time inputs**: Mount the task specification $T$ and a read-only or disposable copy of the initial environment $\mathcal{E}_0$ (repository snapshot, starting database state, or initial container image), and content-hash $(T, \mathcal{E}_0)$ for provenance.
2. **Isolate scoring artifacts structurally**: Ensure verifier-generation code **never imports, mounts, or shares directories with** candidate trajectories, reference solutions, gold patches, or benchmark scoring scripts. An agent cannot leak or overfit to candidate outputs that do not exist in its container namespace.

### Step 2: Prepend the Observable-Evidence Header (`E`) with State Precedence

Exploration-time visibility differs from judgment-time visibility: during generation the agent can browse $\mathcal{E}_0$ freely, whereas the finished verifier sees only the exact arguments passed to its entry point. Prepend an **Evidence Header (`E`)** ahead of the task contract that declares the exact judgment-time inputs (for example, $(\tau, \mathcal{E}_0, \mathcal{E}_f)$ for interactive tool tasks, patched repo $\mathcal{E}_f$ for code patches, or final container filesystem $\mathcal{E}_f$ for CLI/science tasks) and enforces **three mandatory derivation rules**:

1. **State precedence over dialogue**: Whenever initial-vs-final state comparison ($\mathcal{E}_0$ vs. $\mathcal{E}_f$) can witness a requirement, **state comparison is the gate**—if state fails, the verifier **must return `False`**, and nothing in the conversation or tool trace $\tau$ can override it (because $\tau$ is the easiest channel for an agent to fabricate or hallucinate). Inspect $\tau$ **only** for obligations that final state cannot witness (such as obtaining explicit user confirmation before a destructive action, verifying identity, or stating required policy disclosures).
2. **Closed-evidence boundary**: Derive expected outcomes strictly from $(T, \mathcal{E}_0)$ and the passed judgment arguments; forbid memorized benchmark answers, external network calls, or hardcoded hidden test values.
3. **Explicit omission of unwitnessable checks**: If a requirement in $T$ cannot be witnessed by any observable channel at judgment time, explicitly document it as unchecked and skip it rather than inventing brittle proxy checks.

> **Impact of `E`**: Removing `E` on `SWE-bench Verified` drops $\kappa^*$ from `0.741` to `0.579` because missing/broken verifier deliveries triple from `15` to `46` when the generator misjudges the runtime interface.

### Step 3: Mount an On-Demand Domain Rule Library (`R`) Only When $\tau$ Is Observed

Interactive tool-use domains carry implicit policy rules that individual task prompts $T$ leave unstated (for example, refund eligibility windows, identity-verification steps, or regulated financial/legal disclosures):

1. **Gate activation on $\tau$**: Mount the Domain Rule Library (`R`) **only when judgment-time evidence includes the interaction trajectory $\tau$**. Keep `R` disabled on pure final-state benchmarks (`SWE-bench`, `Terminal-Bench`, `TB-Science`) where task text and initial files fully specify the contract.
2. **Expose rules via progressive filesystem navigation, never prompt stuffing**: Mount a read-only directory tree at `/rubric_lib/` structured as `README.md -> INDEX.tsv -> <domain>/<category>.md` with deterministic stable rule IDs (such as `AIR-0021`; Veritas compiles `19,603` entries across finance, legal, airline, and banking corpora without bloating base prompt tokens).
3. **Require selective ID-cited instantiation**: Instruct the generator to inspect `INDEX.tsv` via `ls`/`grep`, read only categories matching $T$'s domain, instantiate checks only for rules triggered by $T$ and witnessable under Step 2, and tag each check with its stable rule ID in comments.

### Step 4: Enforce the Nine Authoring Principles (`H`) in Composition Order `E -> Contract -> H -> R`

> **Critical Ablation Warning**: Never deploy `E` and `R` without `H`! On $\tau^2$-bench, removing `H` while keeping `E + R` causes $\kappa^*$ to crash from `0.787` to **`0.250`**—far below plain `OpenCode` (`0.563`)—because detailed evidence headers and domain rulebooks induce hyper-strict assertions that reject valid trajectories (`Table 4`).

Assemble the prompt in exact order **`E` -> benchmark/interface contract -> `H` -> `R` (if $\tau$ in evidence)**, and enforce all **nine benchmark-agnostic authoring principles**:

- **What to judge**:
  1. *Closed-book inference*: Derive expected outcomes solely from $T$ and $\mathcal{E}_0$, never from memorized solutions.
  2. *Observable completion over private mechanics*: Judge externally observable state changes and required user-facing outcomes—never private helper names, internal variable names, exact tool-call counts, or rigid assistant phrasing.
- **How to compare**:
  3. *Anti-leniency*: Reject no-ops ($\mathcal{E}_f == \mathcal{E}_0$ when mutation is required), empty outputs, `TODO`/placeholder stubs, and partial completions.
  4. *Anti-strictness*: Accept equivalent valid formulations, key orderings, whitespace variations, numeric representations, and alternative valid tool sequences.
  5. *No fabrication or silent swallowing*: Never emit constant `return True` / `return False`, and never wrap assertions in bare `try/except` blocks that silently convert failed checks into passes.
  6. *No environment tampering or leakage*: Keep the verifier side-effect-free with respect to scored artifacts.
  7. *( Principle 8 in Veritas ) Weakest-comparison principle*: **Forbid exact equality (`==`) on strings, floats, paths, or collections unless $T$ explicitly mandates byte-for-byte identity.** Use the weakest check that still separates valid completion from near-miss failure: numeric tolerances (`math.isclose`), case/whitespace normalization, set membership, structural schema/AST checks, or functional execution probes.
- **How to deliver**:
  8. *( Principle 7 in Veritas ) Defensive parsing & bounded exploration*: Treat missing dictionary keys, malformed JSON, or absent output files cleanly as `False` rather than raising unhandled `KeyError`/`FileNotFoundError` crashes, and stop exploring well before timeout—an undelivered verifier scores worse than an imperfect one.
  9. *( Principle 9 in Veritas ) Mandatory pre-exit self-check*: Before terminating, run a syntax/import check on the written verifier file, confirm it resides at the exact required output path, and verify its callable entry-point signature matches the contract.

### Step 5: Execute Zero-Label Probe and At-Most-One-Repair Delivery Gate

Because no labeled candidate solutions exist at generation time, test the delivered verifier against zero-label structural invariants before accepting it:

1. **Run the benchmark probe** in a clean sandbox to classify the generated artifact into four outcomes:
   - `usable`: loads cleanly, matches required signature, and rejects known-trivial invalid state (such as unmodified initial state $\mathcal{E}_0$ / empty no-op candidate when $T$ requires state change).
   - `crash`: syntax error, import failure, missing entry function, or unhandled exception during probe execution.
   - `no signal`: returns `True` on a known-wrong/no-op state.
   - `not determinable`: task allows valid no-op states (for example, refusal tasks where $\mathcal{E}_f = \mathcal{E}_0$ is legitimately correct) and the verifier loads cleanly without crashing.
2. **Trigger at most one bounded repair**: Invoke a single repair turn **only** when the probe reports `crash` or `no signal`, appending the exact traceback or `no signal` diagnostic.
3. **Monotonic replacement rule**: Re-probe the repaired verifier; replace the original verifier **only if** the repaired version's own probe is clean. Never discard a working artifact for a broken repair.

### Step 6: Certify Reference or Benchmark Verifiers via Five Gates (`G1–G5`)

Whenever candidate trajectories or synthetic mutations are available—such as when auditing a benchmark's official verifiers before evaluation or certifying high-value verifiers for RL training—require every task–verifier pair to pass all **five certification gates (`G1–G5`)**:

1. **G1 — Reference pass**: At least one verified oracle/reference solution passes (`True`).
2. **G2 — Non-constant discrimination**: The verifier both rejects known failures (no-ops and corrupted/near-miss candidates return `False`) and accepts harmless equivalent reformulations (`True`).
3. **G3 — Check-deletion / mutation sensitivity**: Deleting any single check in the verifier (or removing a single hunk of a multi-hunk reference patch) is exposed by at least one candidate flipping verdict, eliminating dead or partial-credit blind spots (which affected `36/106` `DeepSWE` tasks).
4. **G4 — Manual/out-of-band mismatch adjudication**: Inspect every disagreement between intended candidate labels and verifier verdicts; remove or repair defective verifiers rather than silently filtering out candidates.
5. **G5 — Repeat-run determinism**: Execute `3` independent runs on identical inputs and require **`0` verdict flips** (catching nondeterministic container races such as `2` `SWE-bench Verified` `sympy` tasks and `72/500` `temperature=0` LLM-judge flips on `MCP-Atlas`).

> **Governance for iterative harness tuning**: If you evolve the verifier-generation prompt or principles across fit/validation splits, enforce a mechanical anti-overfitting lint (blocking task IDs, benchmark names, domain-specific strings, non-whitelisted file edits, and unstated numeric constants) and pass every candidate harness modification through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md)—requiring no regression beyond baseline noise margin $\delta$ (estimated from at least `3` baseline runs) on protected and held-out tasks, and strict zero tolerance on negative security testbeds.

---

## Environment Caveats

- **Harness–backbone pairing still matters at frontier scale**: While `Veritas` (`OpenCode + ERH`) beat vendor harnesses across all four execution benchmarks on `GLM-5.2`, `Qwen3.7-Plus` (vs. `Qwen Code`), and `Gemini 3.5 Flash` (vs. `Gemini CLI`), `Codex CLI` slightly led `Veritas` when paired with `GPT-5.6-sol` (`0.720` vs. `0.692` on `SWE-bench`; `0.540` vs. `0.423` on `TB-Science`). Because `ERH` is harness-agnostic, plug `E + R + H` into the strongest native harness for your chosen model family (for example, `Claude Code + ERH` reached `0.586` on `Terminal-Bench 4.0`, exceeding `OpenCode + ERH`'s `0.465`).
- **Residual false-rejection asymmetry on open-ended artifacts**: Even with `ERH`, generated verifiers on open-ended container/science tasks remain stricter than official tests—for instance, on `Terminal-Bench 4.0`, `Veritas` rejects `97%` of no-ops and `89%` of corrupted outputs (`Claude Code + ERH`: `100%` and `94%`), but accepts `45%` (`Claude Code + ERH`: `52%`) of oracle reference solutions due to unstated output-format conventions. Account for conservative false-negative bias when using generated verifiers as hard rejection filters.
- **Pairwise preference tasks (`LLMBar`, `JudgeBench`)**: When inputs are static response pairs $(x, y_1, y_2)$ with no environment state, evaluate both orders $(y_1, y_2)$ and $(y_2, y_1)$ and count a judgment as valid only when both orders agree (two-order consistency).

## Failure Modes

- **Adding domain rules or evidence specs without `H` (the strictness trap)**: Giving a coding agent `/rubric_lib` and an evidence header without the weakest-comparison and anti-strictness principles causes massive false rejection (`\tau^2`-bench $\kappa^*$ plunges from `0.787` to `0.250`).
- **Trusting dialogue $\tau$ over final state $\mathcal{E}_f$**: Checking whether the assistant *said* it refunded an order or called a tool without checking $\mathcal{E}_f$ lets hallucinated or rolled-back actions pass. Always enforce state precedence.
- **Stuffing domain rules inline into the prompt**: Inline rule dumps exhaust context and trigger irrelevant checks; always mount `R` on disk for selective `ls`/`grep` lookup and disable `R` when $\tau$ is absent.
- **Unbounded repair loops or unprobed replacements**: Running multi-round self-repair without ground-truth candidates drifts toward vacuous `return True` scripts; cap repair at **one** diagnostic turn triggered strictly by `crash` or `no signal`.

## Cross-References

- Evaluation integrity & benchmark preflight rules: [`agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md)
- Single acceptance gate for harness self-modification: [`recursive-improvement.md`](../../rules/recursive-improvement.md) (`"DO: Pass every self-modification through one acceptance gate"`)
- Using executable verifiers to gate runtime memory hypotheses: [`falsification-gated-memory-evolution`](../falsification-gated-memory-evolution/SKILL.md)
- Auditing stateful multi-agent traces with deterministic anchors: [`state-anchored-trajectory-auditing`](../state-anchored-trajectory-auditing/SKILL.md)
- Formal specification + test + code three-surface auditing: [`three-surface-verified-code-audit`](../three-surface-verified-code-audit/SKILL.md)
