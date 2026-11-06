---
name: history-grounded-project-takeover
description: >
  Reconstruct and update multi-turn project state during mid-stream agent
  handoffs and project takeovers using deterministic Requirement Atom state
  replay, explicit clarification gating, and artifact-diff delivery verification.
  Eliminates silent constraint dropping and unverified completion claims.
  Derived from Wang et al. (arXiv:2611.07307).
source: https://arxiv.org/abs/2611.07307
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# History-Grounded Project Takeover

> **Source**: [arXiv:2611.07307](https://arxiv.org/abs/2611.07307) — Wang et al. (2026), *"Take It From Here: Evaluating Coding Agents On Project Takeover"*.
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Overview

In real-world software engineering, coding agents rarely build greenfield projects from a single clean specification; instead, they must **take over ongoing, multi-turn projects mid-stream** (`18–1,075` interaction turns, mean `181.43`, median `110` turns) where requirements have been iteratively introduced, modified, deferred, resumed, or removed, and where earlier assistant claims ("I have fixed the layout") frequently diverge from the actual workspace artifact.

Evaluated on **ReqMemBench** (`349` diagnostic takeover targets—`312` `Gold-ACT` and `37` `Gold-CLARIFY`—across `44` multi-turn projects spanning full-stack software, Word templates/reports, and ESP32 KiCad PCB design, plus `37` executable delivery targets across `7` projects) using six frontier model-harness configurations (`Codex CLI v0.155.1` with `GPT-6 Astra`, `GPT-6 Sol`, `GPT-5.6 Sol`, `GPT-5.6 Terra`; `Claude Code v2.1.283` with `Claude Opus 5.5` and `Claude Sonnet 5`), current coding agents fail catastrophically at project takeover:

- **End-to-end takeover delivery averages only `4.95%` under Full History (`C1`)** (`GPT-6 Astra` highest at `10.81%` [`4/37`], `Sonnet 5` at `0.00%` [`0/37`]), where `DeliveryRate = Build ∧ Target ∧ Regression`.
- **Naive message filtering hurts delivery (`C2` drops to `2.70%`)**: Passing only turn-level relevant history (`C2`, mean `8.70` turns vs. `186.86` turns in `C1`) lowers mean complete delivery from `4.95%` to `2.70%` (`Build`: `58.56% -> 47.30%`, `Target`: `6.31% -> 3.15%`, `Regression`: `51.35% -> 40.54%`) because stripping conversational context severs cross-requirement dependencies.
- **`0 / 312` (`0.00%`) Exact Post-Request State Accuracy across all six frontier configurations**: While models achieve high evidence recall (`0.6670–0.9211` under `C1`), their conditional attribute reconstruction on matched requirements is only `0.2424–0.2813` (`C1`), and **every single model scores `0.00%` exact post-request state match (`Post-State Score` `0.0535–0.1670`)**. Even when `Claude Opus 5.5` correctly reconstructs `100%` of pre-request requirements (`1.0` precision/recall), it silently drops valid historical constraints when computing the post-request target state.
- **Providing the researcher-verified `Oracle Post-State` fixes regressions (`90.99%`) but leaves target implementation at `9.01%`**: When given the exact gold post-request specification (`Oracle Post-State`), agents raise `Build` from `58.56%` to **`96.40%`** and `Regression` preservation from `51.35%` to **`90.99%`** (`100.00%` on both in `Claude Code`), yet **184 of 219 submitted artifacts (`84.02%`) still fail the `Target` test** (`8.11%` complete delivery)—often because the agent updates a summary JSON or markdown report while leaving the actual binary/code artifact untouched.

This skill provides a four-stage **Deterministic Requirement Replay & Takeover Protocol** to reconstruct project state, gate ambiguity, preserve active constraints during state updates, and verify physical artifact modification before completion.

## When to Use

- Taking over an existing codebase, design repository, or long-running agent/human conversation thread mid-project.
- Resuming work after a context window reset, subagent handoff, or session migration where multiple requirements have evolved across dozens or hundreds of turns.
- Auditing why an inherited project fails regression tests or contradicts earlier user instructions despite recent "completed" assistant messages.

## Four-Stage Project Takeover Protocol

### Stage 1: Reconstruct Pre-Request State (`G_q^-`) via Requirement Atom Event Replay

Do not summarize a long project history with free-form prose or naive turn filtering (`C2`). Instead, parse the interaction history chronologically up to the takeover point using the three-tier hierarchy: **"Family organizes; Requirement owns state; Event records evidence."**

1. **Instantiate independent Requirement Atoms**: Group related features under a top-level `Family`, but track every concrete deliverable or constraint as an independent **Requirement Atom** (`req_id`) with five explicit state dimensions:
   - `attributes`: Key-value dictionary of active parameters, dimensions, thresholds, and technical constraints.
   - `lifecycle_status`: Exactly one of `ACTIVE`, `DEFERRED`, `REMOVED`, or `null`.
   - `scope`: Target `persistence`, `components`, and `contexts` where the requirement applies.
   - `ambiguity`: List of open unresolved conflicts or underspecified parameters categorized by dimension (`VALUE`, `SCOPE`, or `LIFECYCLE`) with turn provenance.
   - `execution`: Independent workspace verification state—`CLAIMED_WORKING`, `FAILED`, `VERIFIED_WORKING`, or `null`.
2. **Replay historical turns through eight deterministic event transition operators**:
   - `INTRODUCE`: Initialize the Requirement Atom with `lifecycle_status = ACTIVE` and populate initial `attributes` and `scope`.
   - `MODIFY`: **Execute as a two-step delta, never a destructive overwrite**: first delete only the keys explicitly listed in `value_removals`, then apply key-value updates while **carrying forward all unchanged historical attributes**, and reset `execution` to `null`.
   - `DEFER` / `RESUME`: Transition `lifecycle_status` between `ACTIVE` and `DEFERRED` without erasing stored `attributes`.
   - `REMOVE`: Terminal lifecycle transition (`lifecycle_status = REMOVED`). Reject any silent reintroduction or modification of a removed requirement unless an explicit new user directive re-instantiates it.
   - `AMBIGUOUS`: Record an open ambiguity entry on the atom (`VALUE`, `SCOPE`, or `LIFECYCLE`). Clear an open ambiguity **only** when a subsequent turn provides an explicit resolution event (`resolves_ambiguity_event_ids`).
   - `IMPLEMENTATION_CLAIM` vs. `RUNTIME_FAILURE` vs. `RUNTIME_VERIFICATION`: **Never equate an earlier assistant's `IMPLEMENTATION_CLAIM` with `VERIFIED_WORKING`** or with lifecycle removal. An assistant saying *"I updated the PCB mounting holes"* sets `execution = CLAIMED_WORKING` while keeping `lifecycle_status = ACTIVE`; a subsequent user bug report or test failure transitions `execution` to `FAILED`.

### Stage 2: Apply the New User Request (`G_q^- -> G_q^+`) Without Constraint Dropping

When the takeover request arrives at turn `q`, compute the post-request requirement state `G_q^+` as a strict transactional delta over the reconstructed pre-request state `G_q^-`:

1. **Copy all `ACTIVE` Requirement Atoms from `G_q^-` into `G_q^+` as the baseline**:
   - The primary cause of the `0 / 312` (`0.00%`) Exact Post-State Accuracy failure in frontier agents is **attentional constraint dropping**: agents focus on the newly requested delta (e.g., adding a new sensor or UI route) and omit unmodified active requirements (e.g., `req_power_board_outline` requiring `8 mounting holes` and `M2.5` screws on target `43214420_T004`) from their post-request working specification.
   - Every `ACTIVE` requirement in `G_q^-` that is not explicitly deferred or removed by turn `q` **must remain present with all its attributes intact in `G_q^+`**.
2. **Apply turn `q`'s event transitions (`INTRODUCE`, `MODIFY`, `DEFER`, `RESUME`, `REMOVE`, `AMBIGUOUS`)**:
   - Check whether the new request conflicts with any active attribute in `G_q^-` or references an underspecified target component.
   - If turn `q` modifies an existing atom, retain all non-conflicting prior attributes in that atom and reset its `execution` status to `null` so it is scheduled for re-verification.

### Stage 3: Execute the Clarification Gate (`ACT` vs. `CLARIFY`)

Before touching any workspace file, evaluate the ambiguity state of the target Requirement Atoms in `G_q^+`:

1. **Trigger `CLARIFY` if and only if a blocking ambiguity exists on a target requirement**:
   - If any requirement targeted by turn `q` has an unresolved `AMBIGUOUS` entry (`VALUE`, `SCOPE`, or `LIFECYCLE`) with no resolving event in the history, **halt coding (`CLARIFY`)** and formulate a targeted question citing the conflicting turn IDs and the exact unresolved parameter.
2. **Avoid over-clarification (`Gold-ACT` paralysis)**:
   - In ReqMemBench, when models were given the `Oracle Pre-State`, **86 of 222 runs (`38.7%`)** falsely chose `CLARIFY` on actionable `Gold-ACT` tasks and refused to write code.
   - Do **not** select `CLARIFY` merely because the history is long or because an earlier implementation claim failed; if the user's desired `attributes`, `scope`, and `lifecycle_status` in `G_q^+` are unambiguous, proceed directly to **`ACT`**.

### Stage 4: Ground Workspace Reality and Verify Three-Part Delivery (`Build ∧ Target ∧ Regression`)

Once `ACT` is selected, bridge the gap between the structured specification `G_q^+` and the physical workspace files:

1. **Audit the inherited workspace against `G_q^-` before editing**:
   - Inspect the actual repository files, build scripts, and binary/design artifacts on disk. Do not trust summary markdown files, `artifact_model.json` mirrors, or prior assistant turn claims (`CLAIMED_WORKING`) as proof that a feature is already implemented.
2. **Implement the delta while enforcing active regression invariants**:
   - Use the complete set of `ACTIVE` atoms in `G_q^+` as a regression checklist. Constructing an explicit post-request state table before coding is what lifts `Build` pass rate from `58.56%` to **`96.40%`** and `Regression` pass rate from `51.35%` to **`90.99%`**.
3. **Prevent "Metadata-Only / No-Op Artifact" failures (`84.02%` of Oracle Post-State failures)**:
   - Even with a perfect specification, agents fail `Target` tests on `84.02%` (`184 / 219`) of submitted runs because they edit auxiliary documentation, text summaries, or intermediate JSON representations while leaving the primary deliverable file (e.g., the `.kicad_pcb` board, `.docx` template, or production source module) byte-identical to the initial archive.
   - Before concluding the turn, run a **three-part verification gate**:
     1. **Physical Artifact Diff Check**: Verify via `git status` / `git diff` or file hashes that the primary deliverable artifact targeted by the user's request has actually been modified on disk.
     2. **Target Requirement Verification (`Target`)**: Execute a deterministic check or test that inspects the parsed primary artifact directly to confirm every newly added or modified attribute in `G_q^+` is satisfied.
     3. **Build and Regression Verification (`Build ∧ Regression`)**: Run the project build/compiler and verify that every pre-existing `ACTIVE` requirement in `G_q^+` remains intact (`execution = VERIFIED_WORKING`).

## Quantitative Reference Summary (ReqMemBench)

### Diagnostic Requirement Understanding (`349` Takeover Targets Across `44` Projects)

| Model & Harness (`v0.155.1` / `v2.1.283`) | `C1` Evidence Recall / Precision | `C1` Pre-State Req Coverage (`RQ2`) | `C1` Conditional Attr Score (`RQ2`) | `C1` Exact Post-State Acc (`312` Gold-ACT) | `C1` Continuous Post-State Score | `C2` Continuous Post-State Score |
|:------------------------------------------|:---------------------------------|:------------------------------------|:------------------------------------|:-------------------------------------------|:---------------------------------|:---------------------------------|
| **`GPT-6 Astra`** (`Codex CLI`) | `0.9211` / `0.2254` | `0.6777` | `0.2683` | **`0.00%`** (`0 / 312`) | `0.1539` | `0.1710` |
| **`GPT-6 Sol`** (`Codex CLI`) | `0.8706` / `0.2564` | `0.6194` | `0.2738` | **`0.00%`** (`0 / 312`) | `0.1456` | `0.1563` |
| **`GPT-5.6 Sol`** (`Codex CLI`) | `0.8180` / `0.2896` | `0.5622` | `0.2424` | **`0.00%`** (`0 / 312`) | `0.1190` | `0.1235` |
| **`GPT-5.6 Terra`** (`Codex CLI`) | `0.6670` / `0.4254` | `0.4950` | `0.2813` | **`0.00%`** (`0 / 312`) | `0.0535` | `0.0569` |
| **`Claude Opus 5.5`** (`Claude Code`) | `0.7854` / `0.3802` | `0.6400` | `0.2768` | **`0.00%`** (`0 / 312`) | `0.1670` (`0.2036` cond.) | `0.1665` |
| **`Claude Sonnet 5`** (`Claude Code`) | `0.7429` / `0.3547` | `0.5858` | `0.2588` | **`0.00%`** (`0 / 312`) | `0.1112` | `0.1231` |

### End-to-End Takeover Delivery Across Information Conditions (`37` Executable Targets, `6` Models)

| Information Condition | Mean Complete `DeliveryRate` (`Build ∧ Target ∧ Regression`) | Mean `Build` Pass Rate | Mean `Target` Pass Rate | Mean `Regression` Pass Rate | Primary Bottleneck Revealed |
|:----------------------|:-------------------------------------------------------------|:-----------------------|:------------------------|:----------------------------|:----------------------------|
| **Relevant History (`C2`, mean `8.70` turns)** | **`2.70%`** (`0.00%–5.41%`) | `47.30%` | `3.15%` | `40.54%` | Naive turn filtering strips cross-requirement context and breaks builds/regressions |
| **Full History (`C1`, mean `186.86` turns)** | **`4.95%`** (`0.00%–10.81%`) | `58.56%` | `6.31%` | `51.35%` | Silent constraint dropping during `G_q^- -> G_q^+` update (`0%` exact post-state) |
| **`Oracle Pre-State` (Gold `G_q^-` provided)** | **`4.50%`** (`0.00%–8.11%`) | `60.36%` | `4.95%` | `54.05%` | `86 / 222` runs (`38.7%`) falsely select `CLARIFY` and never enter coding |
| **`Oracle Post-State` (Gold `G_q^+` provided)** | **`8.11%`** (`2.70%–13.51%`) | **`96.40%`** (`100%` Claude) | **`9.01%`** | **`90.99%`** (`100%` Claude) | Eliminates build/regression breakage, but `84.02%` (`184/219`) fail `Target` due to unedited primary artifacts |

## Related Artifacts

- **Rules**: [agent-evaluation-quality.md](../../rules/agent-evaluation-quality.md) and [multi-agent-coordination.md](../../rules/multi-agent-coordination.md) (project takeover state reconstruction and handoff verification rules).
- **Skills**: `requirements-driven-code-generation` (formalizing requirements into verifiable contracts before coding), `dependency-scoped-plan-validation` (validating that pending actions derive from un-superseded state dependencies), and `persistent-agent-migration` (preserving agent state across session and harness handoffs).
