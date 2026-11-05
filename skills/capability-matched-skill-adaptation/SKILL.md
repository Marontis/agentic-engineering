---
name: capability-matched-skill-adaptation
description: >-
  Audit and adapt agent skills (SKILL.md) across four executor capability
  bottlenecks—tool execution, context management, instruction following, and
  verification—when transferring skills from stronger models to weaker
  executors or evolving skills across heterogeneous agent runtimes. Derived
  from "Evolving to Match Capabilities: Improving Harness Self-Evolution via
  Skill Adaptation" (arXiv:2610.33024).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Capability-Matched Skill Adaptation

> **Source**: [arXiv:2610.33024](https://arxiv.org/abs/2610.33024) — *Evolving to Match Capabilities: Improving Harness Self-Evolution via Skill Adaptation* (`src:2610-33024`)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use This Skill

Use this skill when:

- **Transferring human-written or frontier-authored skills to smaller or weaker executors**: A `SKILL.md` package that substantially improves frontier models (e.g., `+29.2` points average across `GPT-5.6-luna` and `Claude-Opus-5`, and `+31.1` points on `GPT-5.6-luna`) stalls or degrades weaker executors (`+1.2` points average on weak models, and `-8.8` points on `Gemma-4-E4B`).
- **Running multi-round harness or skill self-evolution**: An executor iteratively rewrites its own `SKILL.md` from prior-round execution traces and verifier outputs, where unguided self-editing either drifts below baseline or fails to translate trajectory feedback into actionable verification steps.
- **Diagnosing why an agent ignores instructions already present in `SKILL.md`**: Across 103 skill-sensitive task-skill pairs (131 failure-mode labels), **86%** of failed weak-model runs with a skill violate a requirement that is already explicitly written in the injected `SKILL.md`.

Do **not** use this skill when:

- **The task failure is a domain-knowledge gap missing from the skill entirely**: When neither frontier nor moderate models gain from the skill (`< 0.10` improvement), the skill lacks necessary domain procedure rather than suffering from an executor-capability mismatch. Use [`skill-design-methodology`](../skill-design-methodology/SKILL.md) to author the missing procedure first.
- **A weak model is asked to rewrite a skill zero-shot without execution evidence**: Having a weak executor rewrite a skill without trajectory feedback degrades average score from `0.294` to `0.271` across `Qwen3.6-flash`, `Gemma-4-E4B`, and `Qwen3.5-9B`. One-shot static adaptation requires a strong rewriter model guided by the adaptation rubric.

---

## Core Principle: Capability Mismatch vs. Information Absence

Standard skill-transfer workflows assume that once domain knowledge is written into `SKILL.md`, any instruction-following agent can use it (`"DO: Evolve skills with stronger models, deploy to weaker ones"` in [`skill-system-design.md`](../../rules/skill-system-design.md)). Empirical evaluation across **607 tasks** from three benchmarks (**87** SkillsBench tasks on OpenHands, **186** DocOps tasks on Claude Code, and **334** Tessl tasks on Claude Code) and **7 models** reveals a sharp capability threshold on the **103 skill-sensitive task-skill pairs** (32 SkillsBench, 32 DocOps, 39 Tessl):

- **Frontier models** (`GPT-5.6-luna`, `Claude-Opus-5`) gain **+29.2 points** on average (`+31.1` points for `GPT-5.6-luna`), and moderate + frontier models gain **+27 points** on average.
- **Weak models** (`Gemma-4-E4B`, `Qwen3.5-9B`, `Qwen3.6-flash`) gain only **+1.2 points** on average, with `Gemma-4-E4B` dropping by **−8.8 points** when the skill is loaded.
- **The bottleneck is how the skill is expressed, not what is missing**: In **86%** of failed weak-model runs, the required rule or check is already stated in `SKILL.md`, but the skill's structure assumes implicit capabilities—resolving tool vs. file-format names, keeping long reference text from displacing the user prompt, parsing multi-clause prose constraints, and independently verifying outputs—that weaker executors lack.

---

## Step-by-Step Procedure

### Step 1: Diagnose the Executor Bottleneck in Priority Order

Inspect the skill text (and the previous round's trajectory digest and verifier output, if available) against four ordered failure modes. Address the **earliest** bottleneck where the executor breaks down before tuning later sections:

1. **Mode 1 — Tool Execution (`EXE`, $n = 51 / 131$ labels)**:
   - *Symptom*: The run makes only 1–2 tool calls, produces no deliverable artefact, treats a document format or library name in `SKILL.md` (e.g., `xlsx`, `pdf`, `docx`) as a callable tool name, or halts on the first missing binary or import error (e.g., `python: command not found`).
2. **Mode 2 — Context Management (`CTX`, $n = 28 / 131$ labels)**:
   - *Symptom*: Loading the skill *displaces* the user's task—the model succeeded without the skill or instead executes examples from `SKILL.md`, writes to a path shown in an example, or loses track of the user's target files amidst long reference blocks or external auxiliary files.
3. **Mode 3 — Instruction Following (`IF`, $n = 35 / 131$ labels)**:
   - *Symptom*: The model executes multiple tool calls and writes the deliverable to the right path, but silently violates stated constraints, edge-case rules, or negative branches buried in dense prose paragraphs.
4. **Mode 4 — Verification (`REF`, $n = 17 / 131$ labels)**:
   - *Symptom*: The deliverable is written and covers the surface workflow, but computed values, formatting, or schema details fail the verifier because the model treated *"I wrote the file"* or *"the script printed no error"* as completion without re-reading and checking the output.

### Step 2: Apply Bottleneck-Matched Prescriptions to `SKILL.md`

Rewrite the skill to match the target executor's operational bottlenecks while preserving all domain facts, formulas, thresholds, and edge cases:

- **For Tool Execution (`EXE`)**:
  1. Near the very top of `SKILL.md`, explicitly list which mentioned names are **callable harness tools** (e.g., `bash`, `read_file`) versus **document formats or libraries** (`xlsx`, `pdf`, `pandas`) that must be processed through a tool.
  2. Add a gated **environment preflight probe** as the first command (e.g., check `command -v python3 || command -v python`, verify required packages before running the main script).
  3. Provide **verbatim command templates** and an explicit fallback branch for the first likely execution error.
- **For Context Management (`CTX`)**:
  1. Place a boundary header at the top of `SKILL.md` instructing the agent to state the **user's actual task, allowed modification scope, and exact delivery path** before reading further.
  2. State in one explicit line that all subsequent sections and code blocks in `SKILL.md` are **reference templates, not targets to execute literally**.
  3. **Inline essential content** from auxiliary files directly into `SKILL.md` so the executor does not have to chain extra file-discovery reads that bloat context.
- **For Instruction Following (`IF`)**:
  1. Convert dense prose requirements into flat, single-line rules using the schema:
     `Action — Target — Completion Condition`
  2. Explicitly write out the **negative / no-op branch** for conditional rules (e.g., *"If `config.yaml` already defines `timeout`, stop and change nothing"*).
- **For Verification (`REF`)**:
  1. Append a mandatory **terminal verification block** at the end of the procedure:
     - Re-read the generated artefact from disk in a fresh command.
     - Recompute the target quantity or structural check via a **second, independent route** (e.g., a separate one-liner or schema parser, not the script that generated it).
     - Compare against the explicit threshold or rubric condition and loop until it holds.
     - Explicitly state: *"Writing the file or seeing exit code 0 is not verification."*

### Step 3: Run Pre-Admission Structural & Leakage Checks

Before evaluating or committing any adapted skill $o$ against original skill $S$, pass it through the deterministic validity check $G(o, S)$:

1. **No-Op Fallback**: If the rewriter emits `NO_CHANGE` (because no evidence-backed bottleneck applies), keep $S$ unchanged.
2. **Loadability Check**: Verify that $o$ is non-empty, writes to the existing skill file path, preserves valid YAML frontmatter with the exact `name` field unchanged, and stays within the character budget ($\le 64{,}000$ characters).
3. **Answer-Leakage Check**: Scan $o$ against any hidden test suite or reference solution. Reject $o$ and fall back to $S$ if the revision introduces $\ge 1$ expected decimal literal (with at least 2 decimal places) or $\ge 2$ specific identifiers ($\ge 8$ characters containing a digit or underscore) from hidden tests/reference solutions that were not already present in public task material or observed execution evidence.

### Step 4: Gate Acceptance Before Committing

When adapting skills inside an iterative self-evolution loop or deploying a revised skill to a shared library, never overwrite the incumbent unconditionally. Defer acceptance to **"DO: Pass every self-modification through one acceptance gate"** in [`rules/recursive-improvement.md`](../../rules/recursive-improvement.md) (and see [`self-evolution-stopping-rule`](../self-evolution-stopping-rule/SKILL.md) to stop evolution once consecutive rounds fail to clear the improvement threshold).

---

## Empirical Performance

### 1. One-Shot Adaptation Without Execution Evidence (Table 1)

On the 103 skill-sensitive pairs across 3 weak executors (`Qwen3.6-flash`, `Gemma-4-E4B`, `Qwen3.5-9B`), rewriting `SKILL.md` zero-shot (using only the skill text, without task prompts or rollout traces) shows a stark divide between weak self-rewrites and strong capability-matched rewrites:

| Rewriter Configuration | `Qwen3.6-flash` | `Gemma-4-E4B` | `Qwen3.5-9B` | Weak-Tier Mean |
|:---|:---:|:---:|:---:|:---:|
| **Original Skill** (unadapted) | 0.529 | 0.029 | 0.323 | 0.294 |
| **Weak (self) rewrite** w/ meta-skill | 0.476 | 0.056 | 0.280 | 0.271 (−2.3 pts) |
| **`GPT-5.6-sol`** w/ meta-skill | 0.563 | 0.139 | 0.303 | 0.335 (+4.1 pts) |
| **`GPT-5.6-luna`** w/ meta-skill | 0.602 | 0.119 | 0.307 | 0.343 (+4.9 pts) |
| **`GLM-5.3`** w/ meta-skill | 0.626 | 0.138 | 0.374 | 0.379 (+8.5 pts) |
| **`Kimi-K3`** w/o meta-skill (generic prompt) | 0.565 | 0.110 | 0.321 | 0.332 (+3.8 pts) |
| **`Kimi-K3`** w/ meta-skill | **0.616** (+8.7 pts) | **0.170** (+14.1 pts) | **0.374** (+5.1 pts) | **0.387** (+9.3 pts) |

Adding the four-mode adaptation meta-skill to `Kimi-K3` contributes **+5.1 to +6.0 points** beyond a generic one-sentence rewrite prompt (`0.387` vs. `0.332` mean).

### 2. Multi-Round Self-Evolution With Execution Evidence (Table 4)

When each executor rewrites its own skill over 5 rounds using round $t-1$ score, trajectory digest, and verifier output, the adaptation meta-skill improves round-5 scores across **all 7 executors** by **+2.0 to +5.1 points** (`+0.020` to `+0.051`) compared to self-evolution without the meta-skill:

| Executor Model | Base (w/ skill) | Round 5 (w/o Meta-Skill) | Round 5 (w/ Meta-Skill) | Meta-Skill Gain ($\Delta_5$) |
|:---|:---:|:---:|:---:|:---:|
| `Qwen3.6-flash` | 0.523 | 0.614 | **0.644** | **+0.030** (+3.0 pts) |
| `Gemma-4-E4B` | 0.104 | 0.096 *(below base all 5 rounds)* | **0.147** | **+0.051** (+5.1 pts) |
| `Qwen3.5-9B` | 0.314 | 0.317 *(peaked 0.364 at r3, drifted)* | **0.366** | **+0.049** (+4.9 pts) |
| `Qwen3.5-27B` | 0.578 | 0.693 | **0.739** | **+0.046** (+4.6 pts) |
| `Gemma-4-26B` | 0.075 | 0.100 | **0.120** | **+0.020** (+2.0 pts) |
| `Qwen3.5-plus` | 0.582 | 0.723 | **0.748** | **+0.025** (+2.5 pts) |
| `Kimi-K2.5` | 0.612 | 0.765 | **0.800** | **+0.035** (+3.5 pts) |

### 3. Why Static Rewriting and Self-Evolution Are Complementary (Table 2)

Breaking down the weak-executor gains by diagnosed failure mode reveals why static adaptation and trajectory-driven self-evolution target different bottlenecks:

- **One-shot adaptation (`Kimi-K3`, no trajectories)** excels at **Context Management (`+0.103`)**, **Tool Execution (`+0.056`)**, and **Instruction Following (`+0.055`)**, which are visible directly in the text structure of `SKILL.md`, but yields almost nothing on **Verification (`+0.003`)**.
- **Self-evolution at round 5 (with trajectories)** delivers its largest gain on **Verification (`+0.104`, which is `+0.101` higher than one-shot)** alongside **Tool Execution (`+0.065`)** and **Instruction Following (`+0.046`)**, because execution traces and verifier outputs expose whether a check was actually run or skipped.

---

## Environment Caveats & Failure Modes

- **Never let a weak executor rewrite `SKILL.md` without execution trajectories**: Without verifier feedback and trajectory digests, weak models (`Gemma-4-E4B`, `Qwen3.5-9B`, `Qwen3.6-flash`) delete domain constraints or introduce broken shell syntax, lowering mean performance from `0.294` to `0.271`.
- **Unguided self-evolution on weak models regresses or oscillates**: Without the four-mode adaptation rubric, `Gemma-4-E4B` stays below its `0.104` baseline across all 5 rounds of self-evolution (`0.096` at round 5), and `Qwen3.5-9B` peaks at round 3 (`0.364`) before drifting back to `0.317` at round 5.
- **Test-set overfitting during trajectory-driven evolution**: When an evolving agent has access to verifier outputs, it may copy expected numbers or test identifiers into `SKILL.md` instead of fixing the verification procedure. Always enforce the lexical answer-leakage filter in Step 3 alongside held-out acceptance gating.

---

## Related Artifacts

- **Rules**:
  - [`skill-system-design.md`](../../rules/skill-system-design.md) — Qualifies *"DO: Evolve skills with stronger models, deploy to weaker ones"* (skills authored by or for stronger models must be adapted across the four executor capability bottlenecks before weak-model deployment).
  - [`recursive-improvement.md`](../../rules/recursive-improvement.md) — Defers commit decisions to *"DO: Pass every self-modification through one acceptance gate"*.
- **Skills**:
  - [`skill-design-methodology`](../skill-design-methodology/SKILL.md) — Subtask-level decomposition and authoring checklist for creating initial skills.
  - [`self-evolution-stopping-rule`](../self-evolution-stopping-rule/SKILL.md) — Sequential stopping criterion for terminating multi-round skill evolution once gains saturate.
  - [`decision-only-sequential-acceptance`](../decision-only-sequential-acceptance/SKILL.md) — Leak-Bounded Sequential Acceptance (LBSA) for gating candidate revisions on reused benchmarks.
- **Research Briefs**:
  - [`skill-infinity-recursive-meta-skill-optimization.md`](../../research-briefs/skill-infinity-recursive-meta-skill-optimization.md) — Complementary work ($\text{Skill}^\infty$, `arXiv:2610.35434`) that optimizes the skill-optimization meta-skill itself for frontier executors (`GPT-6 Luna`, `GPT-5.6 Luna`).
