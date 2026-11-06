---
name: post-migration-behavioral-differential-testing
description: >
  Gate LLM and agent code repairs after library or runtime API migrations using
  release-note boundary inputs and fail-closed legacy differential validation.
  Eliminates silent false acceptances caused by typical-input test suites and
  self-generated test filtering. Derived from Chen et al. (arXiv:2611.08269).
source: https://arxiv.org/abs/2611.08269
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Post-Migration Behavioral Differential Testing

> **Source**: [arXiv:2611.08269](https://arxiv.org/abs/2611.08269) — Chen et al. (2026), *"Accepted but Wrong: Silent Failures of LLM Code Repairs after API Migrations"*.
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Overview

When upgrading a runtime or library (`A_0 -> A_1`), API changes fall into two behavioral regimes: **explicit breaks** (which raise syntax errors, `ImportError`, `TypeError`, or runtime exceptions on standard inputs) and **silent behavioral migrations** (where deprecated flags, default parameter shifts, parser rules, or return formats change semantics without raising an exception). Standard release gates that run only **typical consumer tests (`T`)** fail catastrophically on post-migration repairs: across 52 affected migration tasks in 49 documented-change clusters spanning real upgrades (`CPython 3.9.6 -> 3.12.15`, `Node.js 20.20.2 -> 24.21.0`, and `SQLite CLI 3.51.0 -> 3.54.0`), a typical-input gate falsely accepts **41.0%** (`FA = 0.410`) of plausible candidate programs that violate the hidden migration contract, and accepts **99.0%** (`FA hard = 0.990`) of legacy-matching hard distractors.

Even worse, two intuitive LLM testing defenses fail in practice:
1. **Repairer self-testing (`S`)**: Having the repairing model generate its own regression tests before patching fails to achieve statistically significant false-acceptance reductions after family-wise Holm correction in any evaluated model family (`smallest strict Holm p = 0.132`).
2. **Self-filtered `legacy-binding` guards (`G_k`)**: Asking an isolated test-writer model to flag which of its generated inputs are `legacy-binding` and discarding unflagged inputs **backfires**, degrading false acceptance from `0.070` (`W_3`) to `0.157` (`G_3`) (`0.492` on hard distractors) because models systematically mislabel change-revealing boundary inputs as non-binding.

This skill provides a four-stage **Release-Note Differential Gate** that combines isolated blind boundary-input synthesis from official upgrade documentation with fail-closed ground-truth execution on the legacy runtime (`A_0`), cutting model-free false acceptance from `0.410` to `0.065–0.070` (`0.058` on hard distractors) and reducing per-attempt wrong releases across local and frontier repair models by **60%–89%**.

## When to Use

- Automated or agent-assisted dependency, SDK, interpreter, or database engine upgrades (e.g., Python minor/major bumps, Node.js LTS upgrades, SQLite/PostgreSQL upgrades, framework v1-to-v2 migrations).
- Reviewing LLM-generated patches for deprecation warnings, removed API symbols, or altered parser/serializer defaults.
- Building CI/CD admission gates for repository-wide migration PRs where existing unit tests only exercise happy-path ("typical") inputs.
- Evaluating whether a breaking runtime change admits a safe in-place code repair or requires **explicit abstention (`no-safe-repair`)** and architectural escalation.

## Four-Stage Differential Migration Gate

### Stage 1: Pin the Upgrade Contract & Extract Release-Note Clauses

Before invoking any repair agent or generating candidate diffs, formalize the migration context into an explicit five-part contract:

1. **Pin both runtime environments (`A_0` and `A_1`)**: Maintain reproducible, isolated execution sandboxes for both the pre-upgrade runtime `A_0` ( running the unmodified legacy procedure `p_0`) and the target runtime `A_1`.
2. **Isolate verbatim release-note clauses**: Retrieve the exact official release-note or migration-guide entry governing the affected API surface. Record what changed in `A_1`:
   - Removed or renamed functions, classes, keywords, or CLI flags.
   - Changed default parameter values, strictness modes, or error-handling policies (e.g., SQLite `NOT NULL` / `UNION` / `Triggers` edge cases, CPython `urllib`, ` configparser`, `ast`, `datetime`, or `sqlite3` behavioral shifts, Node.js `Buffer`, `fs`, or `url` changes).
   - Altered output formatting, sorting, precision, or side-effect ordering.
3. **Define consumer requirement predicates**: Separate invariant functional requirements into:
   - **Consumer assertions (`C`)**: Structural, type, and invariant checks that every valid output on `A_1` must satisfy.
   - **Legacy-equality obligations (`d_0`)**: Specific output fields or return values that must remain byte-for-byte or semantically identical to the legacy implementation `p_0` under `A_0`.
   - **State and file-preservation invariants (`p_0`)**: Side-effect checks verifying that persistent files, database tables, or configuration states are not silently corrupted or truncated.
4. **Check for `no-safe-repair` conditions**: If the target runtime `A_1` completely removes a capability required by the consumer specification with no compliant substitute within the permitted dependency scope, classify the task as requiring `no-safe-repair` abstention rather than forcing a broken workaround.

### Stage 2: Blind Boundary-Input Synthesis (`W_k`)

Synthesize up to `k = 3` targeted boundary inputs using a **capability-tiered, information-isolated test writer** before exposing any repair candidates:

1. **Enforce strict information isolation**: Provide the test-writer model **only**:
   - The natural-language consumer requirement summary.
   - The verbatim pinned release-note excerpt describing the `A_0 -> A_1` change.
   - The input schema (parameter names and types), one typical example input with its legacy output on `A_0`, and the consumer assertion signatures.
   - **Withhold** the legacy source code `p_0`, the candidate repair diff/fragments, and any hidden evaluation suites so the writer cannot overfit to implementation shortcuts.
2. **Use the strongest available reasoning model as the test writer**: Empirical cross-writer benchmarks (Stage 1 Table 8 and Stage 3 Table 12) show that **writer capability dominates writer independence**:
   - A strong blind writer (`GPT-5.6-luna`, `W_3`) reduces model-free false acceptance to `0.070` in Stage 1, `0.053` in Stage 2 (`1,491` fragments), and `0.058` in Stage 3 (`1,689` fragments including `233` hard distractors), matching human author-written release-note edge inputs (`E`: `0.065`, `0.045`, `0.058`).
   - Weak local test writers fail preregistered safety bounds: `Qwen3-8B` leaves false acceptance at `0.182` (exceeding the `0.10` ceiling), while `qwen3.6-35b-a3b` drives false rejection up to `0.083` (exceeding the `0.05` ceiling).
   - When the strong writer generates the test suite, gating is equally effective whether the repairing model is from the same model family (`FA = 0.161` on the 21 common tasks) or a different model family (`FA = 0.187`).
3. **Target the semantic divergence boundary**: Instruct the writer to construct up to 3 inputs (`W_3`) that specifically trigger the clause described in the release note—such as boundary values, malformed or edge-format strings, deprecated option combinations, empty/null collections, or multi-step stateful sequences where the old idiom and the migrated runtime diverge.

### Stage 3: Fail-Closed Ground-Truth Calibration on `A_0`

Never trust an LLM test writer to predict expected output values or to self-censor its test cases:

1. **Execute candidate inputs on `p_0` under `A_0`**: Run every writer-proposed input `x_i` through the original, unmodified code `p_0` inside the legacy runtime `A_0`.
2. **Apply fail-closed input admission**:
   - If `p_0(x_i)` under `A_0` raises an unhandled exception, times out, violates the input schema, or fails the baseline consumer assertions, **discard `x_i` immediately** (in the benchmark, this fail-closed check automatically dropped 27 invalid writer inputs while retaining 176 valid boundary inputs across 69 tasks).
   - If `p_0(x_i)` succeeds and satisfies all baseline invariants under `A_0`, record its exact deterministic execution output `y_0 = p_0(x_i)` and post-execution file state as the authoritative reference oracle for `x_i`.
3. **Retain all validated boundary inputs without `legacy-binding` filtering**:
   - Include **every** input `x_i` that passes fail-closed execution on `A_0` in the visible gate set `X_v = T U W_3`.
   - **Never filter out validated inputs based on an LLM's self-annotation of whether the input is `legacy-binding` (`G_k`)**. In controlled evaluation, allowing the writer to drop inputs it labeled non-binding discarded 35 of 176 valid boundary inputs, causing stale-code detection to drop from `50/52` (`W_3`) to `42/52` (`G_3`) and more than doubling false acceptance (`0.070 -> 0.157`).

### Stage 4: Repair Generation, Differential Gating, and Abstention

Evaluate candidate repairs `p_cand` on the target runtime `A_1` against the full visible input set `X_v = T U E` or `X_v = T U W_3`:

1. **Verify stale-code failure visibility**: Run the unmodified legacy code `p_0` on `A_1` across `X_v`. Under typical inputs (`T`) alone, stale code fails visibly on only `34/52` affected tasks (`65.4%`); adding a release-note edge input (`E`) or 3 blind writer inputs (`W_3`) forces stale procedures to fail visibly on `52/52` (`100%`) and `50/52` (`96.2%`) of tasks, respectively, giving the repair agent an actionable error trace when explicit or silent failures occur.
2. **Enforce the conjunctive acceptance gate on `A_1`**: Accept a candidate repair `p_cand` if and only if, for **every** input `x` in `X_v`:
   - `p_cand(x)` executes cleanly on `A_1` without unhandled exceptions or timeouts.
   - `p_cand(x)` satisfies all consumer requirement assertions `C(x, y_1)`.
   - `p_cand(x)` matches the recorded `A_0` reference output `y_0` on all legacy-binding output keys (`d_0`) and preserves all required file/state invariants (`p_0`).
3. **Reject "legacy-matching" superficial patches**: During repair, LLMs frequently select distractors that preserve surface syntax or silence an exception on typical inputs while breaking edge-case semantics on `A_1`. Evaluating on `W_3` or `E` catches **83.2%–84.7%** of hard legacy-matching distractors that pass typical tests (`FA hard` drops from `0.990` under `T` to `0.168` under `E` and `0.153` under `W_3`).
4. **Require explicit `no-safe-repair` abstention when blocked**: If no candidate repair passes the conjunctive gate on `X_v` (or when Stage 1 identifies an unrepairable breaking removal), output an explicit `no-safe-repair` verdict with the failing boundary input `x`, the `A_0` reference output `y_0`, and the `A_1` failure trace, rather than shipping a repair that passes only `T`.

## Quantitative Reference Summary

### Model-Free Gate Discrimination Across Frozen Evaluation Stages

| Gate Configuration (`X_v`) | Stage 1 (`405` fragments, `52` test tasks) `FA` / `FR` | Stage 1 Stale Fails Visibly | Stage 2 Large Menu (`1,491` fragments) `FA` / `FR` | Stage 3 Hard Distractors (`1,689` fragments, `233` hard) `FA` / `FR` | Stage 3 Hard-Origin `FA hard` |
|:---------------------------|:-------------------------------------------------------|:----------------------------|:---------------------------------------------------|:---------------------------------------------------------------------|:------------------------------|
| **Typical inputs only (`T`)** | `0.410` / `0.010` | `34 / 52` (`65.4%`) | `0.278` / `0.014` | `0.337` / `0.010` | `0.990` |
| **Guarded writer (`G_3`, filtered)** | `0.157` / `0.010` | `42 / 52` (`80.8%`) | `0.106` / `0.043` | `0.135` / `0.042` | `0.492` |
| **Blind writer (`W_3`, `GPT-5.6-luna`)** | `0.070` / `0.010` | `50 / 52` (`96.2%`) | `0.053` / `0.043` | `0.058` / `0.042` | `0.153` |
| **Author release-note edge (`E`)** | `0.065` / `0.010` | `52 / 52` (`100.0%`) | `0.045` / `0.014` | `0.058` / `0.010` | `0.168` |

### End-to-End LLM Repair Outcomes Across Gates (456 Attempts per Arm on Test Partition)

| Repair Model Family | Stage 1 `T` (`CC / FA / FR`) | Stage 1 `S` Self-Test (`CC / FA / FR`) | Stage 1 `E` Edge Gate (`CC / FA / FR`) | Stage 1 Per-Attempt `FA` (`T -> E`, `H1`) | Stage 2 `FA` (`T -> E`, `LH1`) | Stage 3 Hard `FA` (`T -> E`, `HA1`) |
|:--------------------|:-----------------------------|:---------------------------------------|:---------------------------------------|:------------------------------------------|:-------------------------------|:------------------------------------|
| **`Qwen3-8B`** (confirmatory) | `268 / 98 / 0` | `271 / 80 / 0` | `270 / 24 / 0` | `0.233 -> 0.057` (`-0.176`, $p < 0.001$) | `0.253 -> 0.062` ($p < 0.001$) | `0.250 -> 0.050` ($p < 0.001$) |
| **`gpt-oss-20b`** (confirmatory) | `320 / 71 / 0` | `327 / 47 / 1` | `353 / 8 / 0` | `0.181 -> 0.020` (`-0.161`, $p < 0.001$) | `0.212 -> 0.038` ($p < 0.001$) | `0.218 -> 0.043` ($p < 0.001$) |
| **`qwen3.6-35b-a3b`** (descriptive) | `354 / 49 / 0` | `363 / 30 / 0` | `368 / 7 / 0` | `0.120 -> 0.018` (`-0.102`, $p = 0.004$) | `0.177 -> 0.023` ($p < 0.001$) | `0.198 -> 0.028` ($p < 0.001$) |
| **`GPT-5.6-luna`** (descriptive) | `398 / 22 / 0` | `403 / 9 / 0` | `408 / 7 / 0` | `0.048 -> 0.015` (`-0.038`, $p = 0.499$) | `0.074 -> 0.031` ($p = 0.378$) | `0.107 -> 0.031` ($p = 0.063$) |

## Anti-Patterns to Avoid

- **Relying on exception-free execution on typical inputs (`T`)**: Silent behavioral migrations (`25/66` affected tasks in the benchmark) raise zero runtime errors on `T` while producing corrupted outputs or side effects on `A_1`.
- **Letting the repair agent write its own migration gate (`S`)**: A repairing model shares the same blind spots about `A_1` semantics during test generation as during code repair; self-tests never achieved statistically significant false-acceptance reduction after Holm correction.
- **Filtering test inputs with an LLM `legacy-binding` classifier (`G_k`)**: Models frequently confuse newly tightened `A_1` behavior with "unspecified legacy behavior" and discard the exact boundary test needed to catch a broken migration. Use fail-closed execution on `p_0` under `A_0` as the sole admission filter.
- **Using a small or quantized local model as the blind test writer**: Under-capable writers either miss the release-note boundary (`Qwen3-8B`, `FA = 0.182`) or generate malformed tests that inflate false rejections (`qwen3.6-35b-a3b`, `FR = 0.083`). Always allocate a frontier reasoning model to Stage 2 input synthesis, even when using smaller models for candidate code generation.

## Related Artifacts

- **Rules**: [agent-evaluation-quality.md](../../rules/agent-evaluation-quality.md) (post-migration differential gating and test-writer capability rules).
- **Skills**: `contract-verified-test-mock-generation` (verifying interaction contracts in unit tests), `requirements-driven-code-generation` (decomposing requirements into formal pre-implementation contracts), and `counterexample-guided-repair` (refining artifacts from executable witness traces).
