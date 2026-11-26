# RepoClean: Evaluating Coding Agents on Repository-Level Obsolete Code Cleanup

> **Source**: [arXiv:2611.30350](https://arxiv.org/abs/2611.30350) — Hongyixuan Yuan, Qixing Zhou, Pengcheng Huang, Qingshuo Ni, Runsong Zhao, Shaokai He, Xiangpeng Li, Deqiang Ouyang (2026)
> **Praxis Source ID**: `src:2611-30350v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

`RepoClean` is a **benchmark construction protocol and empirical failure diagnosis** (`200` full tasks across `34` Python repositories + `40`-task `RepoClean Lite` across `27` repositories) rather than a high-performing cleanup procedure: even the strongest evaluated frontier model (`GPT-6 Astra`) resolves only **`23.0%`** of tasks (`1.0%–21.5%` across the remaining `6` models). Instead of offering a validated agent algorithm, `RepoClean` establishes critical **benchmark anti-leakage hygiene, dual-axis maintenance scoring (`Deletion Coverage` alongside `Resolved`/`Recovery`), and prompt/verification pitfalls**—showing that generic bug-repair prompts leave **`62.8%–78.2%`** of obsolete code behind, exact file-path hints can degrade aggressive editors (`-2.5 pp` on `DeepSeek-V4.1-Flash`), and agents fabricate passing self-tests that assert deleted interfaces are gone while breaking hidden callers.

---

## Benchmark Construction & Anti-Leakage Controls

From `100` mature Python repositories (`> 1` year history, `> 5,000` stars), `RepoClean` isolates `200` pure-deletion cleanup commits (`100–600` deleted lines, `10–200` functions/methods; mean **`256.85`** [max `573`] deleted lines across **`15.62`** [max `37`] modified files, paired with **`39.15`** initially failing and **`30.70`** initially passing test files = `69.85` total test files per task):

1. **Pure-Deletion Reinsertion & `3`-Pass Determinism**: Re-inserts historical obsolete AST hunks onto a modern commit where deprecated callers/tests conflict or fail, certifying every task with **`3`-pass zero-flip test stability**.
2. **History & Timestamp Scrubbing**: Strips `.git` history down to a **single root commit** and normalizes **every file timestamp to `2000-01-01 00:00:00 UTC`**, preventing agents from cheating via `git log`, `git blame`, or `mtime` diffs to spot re-inserted hunks.
3. **Hidden Validation Suite & Three-Metric Scoring**: Evaluates submissions on hidden test suites across:
   - **`Resolved (%)`**: `100%` of failing tests fixed **and** `0` regressions on initially passing tests.
   - **`Recovery (%)`**: Fraction of initially failing test files restored to passing.
   - **`Deletion Coverage (%)`**: Recall over ground-truth obsolete lines actually removed.

---

## Key Empirical Findings

### 1. Frontier Agents Recover `58%–73%` of Failing Tests Yet Resolve Only `1.0%–23.0%` End-to-End

| Model (`mini-swe-agent 2.4.6`, `60`-min cap) | `Full` (`200`) `Resolved / Recovery / Del. Cov.` (%) | `Lite` (`40`) `Resolved / Recovery / Del. Cov.` (%) | Avg. Steps (`Full`) | Avg. Input / Output Tokens (`Full`) |
|:---------------------------------------------|:-----------------------------------------------------|:----------------------------------------------------|:--------------------|:------------------------------------|
| **`GPT-6 Astra`** | **`23.0 / 73.2 / 76.2`** | `15.0 / 72.2 / 75.5` | **`33.9`** | `2.3M / 16.9K` |
| **`DeepSeek-V4.1-Flash`** | **`21.5 / 67.6 / 71.0`** | **`20.0 / 64.0 / 69.7`** | **`293.0`** (`8.6x` `Astra`) | **`77.9M / 168.9K`** |
| **`GLM-5.3`** | `17.5 / 72.5 / 70.7` | `17.5 / 75.1 / 67.8` | `201.4` | — |
| **`GPT-6.1 Sol`** | `13.5 / 67.4 / 70.2` | `15.0 / 66.5 / 69.5` | **`33.7`** | — |
| **`Kimi K3`** | `13.5 / 68.7 / 65.5` | `15.0 / 63.1 / 62.7` | `157.9` | — |
| **`Qwen3.8-27B`** | `9.5 / 58.4 / 52.2` | `10.0 / 58.4 / 50.0` | `120.1` | — |
| **`Qwen3.6-35B-A3B`** | `1.0 / 23.1 / 14.3` | `0.0 / 19.4 / 16.9` | `147.8` | — |

- **Near-complete deletion still fails hidden cross-file dependencies**: Across `1,201` unresolved runs, only `2.1%` deleted `0` lines, **`12.4%` achieved `>= 90%` `Deletion Coverage` yet still failed validation**, and `~98%` terminated via unverified submission or hitting the `60`-minute wall-clock timeout.

### 2. Generic Repair Prompts Leave `63%–78%` of Dead Code Behind, and File Hints Are Non-Monotonic

| `RepoClean Lite` (`40` Tasks) Prompt Condition | `GPT-6.1 Sol` (`Res. / Rec. / Cov.` %) | `DeepSeek-V4.1-Flash` (`Res. / Rec. / Cov.` %) | `Qwen3.8-27B` (`Res. / Rec. / Cov.` %) |
|:-----------------------------------------------|:---------------------------------------|:-----------------------------------------------|:---------------------------------------|
| **Standard Cleanup Prompt (Baseline)** | `15.0 / 66.5 / 69.5` | `20.0 / 64.0 / 69.7` | `10.0 / 58.4 / 50.0` |
| **General Repair Prompt (`Table 5`, no cleanup mandate)** | `15.0 / 60.2 /` **`37.2` (`-32.2` Cov.)** | **`10.0`** `/ 68.9 /` **`32.7` (`-37.1` Cov.)** | **`5.0`** `/ 56.5 /` **`21.8` (`-28.2` Cov.)** |
| **Cleanup + Exact Target File-Path Hints (`Table 4`)** | **`27.5`** `/ 76.5 /` **`84.6`** (`+12.5` Res.) | **`17.5` (`-2.5` Res.)** `/ 67.6 / 77.1` | **`12.5`** `/ 44.9 (`-13.5` Rec.) / 62.6` |

- **Symptom patching vs. structural cleanup (`-28.2` to `-37.1 pp` coverage collapse)**: Under a standard SWE-bench-style *"fix the failing tests"* prompt (`Table 5`), `Recovery` barely budged (`-6.3`, `+4.9`, `-1.9` pp)—`GPT-6.1 Sol` kept the exact same `15.0%` `Resolved` rate!—while **`Deletion Coverage` plunged `28.2–37.1 pp` (`37.2%`, `32.7%`, `21.8%`)** because agents routed around failing imports instead of excising dead subsystems.
- **Collateral regressions & self-confirming agent unit tests**: On the `113` tasks (`56.5%`) containing `>= 1` initially passing test file, models caused regressions in **`115` runs, of which `72/115` (`62.6%`) simultaneously fixed failing tests while breaking previously passing ones**. Worse, in `explainshell`, `Kimi K3` over-deleted a still-active interface, wrote a new self-test asserting that the deleted symbol no longer existed, watched its self-test pass, and submitted a broken repository—mirroring why agent-authored negative assertions cannot substitute for locked external regression suites.

---

## Relevance to Praxis

1. **Maintenance Benchmark & CI Quality Gates (`output/rules/agent-evaluation-quality.md`, `output/specs/adk-eval-quality-gate.spec.md`)**: Test pass rate (`Resolved` / `Recovery`) is blind to `63%–78%` technical-debt retention on deprecation/migration PRs unless paired with **ground-truth `Deletion Coverage`** (or dead-symbol reachability checks), **single-commit + uniform-`mtime` (`2000-01-01`) workspace scrubbing** in historical benchmarks, and **locked pre-existing passing test suites** immune to agent-authored self-tests.
2. **Task Prompting for Refactoring Agents**: Whenever an issue stems from deprecated flags, removed APIs, or dead feature flags, prompts must **explicitly mandate dead-code excision** rather than symptom-level test repair, while bounding blast radius with caller-graph verification before file-wide deletion (`DeepSeek-V4.1-Flash` `-2.5 pp` under file hints).
