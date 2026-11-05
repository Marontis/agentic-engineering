---
name: history-guided-trajectory-collection
description: >-
  Collect diverse, high-signal coding agent training trajectories by compiling
  prior issue attempts into collector-private state detectors and short-horizon
  branch comparisons while keeping the agent's prompt strictly native. Derived
  from SWE-Trail (arXiv:2611.02074).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# History-Guided Trajectory Collection (`SWE-Trail`)

> **Source**: [arXiv:2611.02074](https://arxiv.org/abs/2611.02074) — Li et al. (University of Connecticut & Ant Group, 2026-11-01)  
> **Praxis Source ID**: `src:2611-02074`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use This Skill

Use this skill when collecting multi-turn software engineering or tool-use trajectories for supervised fine-tuning (SFT) or post-training where:
1. **Independent rollouts repeat the same mistakes**: Sampling $k$ independent rollouts per issue (`SeedBank`) repeatedly explores the same files ($J_{\text{explore}} = 0.625\text{--}0.665$) and edits the exact same patch targets ($J_{\text{patch}} = 0.745\text{--}0.918$, with `73.20%–89.96%` of 5-attempt patch coverage already exhausted on attempt 1).
2. **Prompt-injected experience hurts student generalization**: Passing prior attempt summaries or hints directly into the agent's prompt during data collection (`SWE-Exp`) creates a train-test interface mismatch—whether the advice is kept in SFT (`Advice retained`: `-1.11` to `-1.19` pp vs. collector-private branching) or stripped afterward (`Advice removed`: `-2.67` pp on `SWE-bench Multilingual`) because actions in the trajectory remain conditioned on unseen prompt hints.
3. **Outcome-only verifier filtering is insufficient**: Selecting more passing trajectories from a larger independent rollout pool (`Top-5-of-10`, `394/1,500` resolved) still underperforms history-guided trajectory collection (`SWE-Trail-H5`, `345/1,500` resolved) by `-1.56` pp on `SWE-bench Multilingual` and `-0.96` pp on `SWE-Pro`.

---

## Core Architectural Principle: Collector-Private History Boundary

Never expose prior trajectories, failure summaries, or branching instructions inside the coding agent's context window. Instead, enforce a strict boundary between two components:

- **Native Coding Agent Policy ($\pi_{\text{agent}}$)**: Receives only the standard issue description, repository workspace, and its own single-lineage action-observation history $(o_1, a_1, \dots, o_t)$.
- **History-Guided Trajectory Collector ($\mathcal{C}_{\text{trail}}$)**: Consumes $K$ prior trajectories (default $K = 5$, `H5`) on the same issue to decide *when* to checkpoint the sandbox, *which* native action proposal to branch on, and *which* short continuation to keep.

---

## Step-by-Step Procedure

### Stage 1: Compile Prior Attempts into Collector-Private Decision Rules

Given $K = 5$ prior trajectories $\{\tau^{(1)}, \dots, \tau^{(K)}\}$ on an issue (whether `stable-solved`, `mixed`, or `never-solved`), run the offline **History Compiler** once before collecting new trajectories:

1. **Extract Localized Divergence & Bottleneck States**:
   - For **mixed** histories (containing both resolved and unresolved attempts), align trajectories to locate the earliest localized divergence step where failed runs lock into a dead-end file, misdiagnose root cause, or skip reproduction/validation.
   - For **unsolved** (`never-solved`) or **uniform** (`stable-solved`) histories, identify recurring bottleneck states: repeated read loops on the same file span, unvalidated multi-hunk edits, or recurring test-runner failures.
2. **Emit Structured State-Trigger Rules**:
   - Compile each bottleneck into a collector-private rule $r_j = (\text{TriggerPredicate}, \text{AlternativeObjective}, \text{ComparisonCriterion})$:
     - `TriggerPredicate`: Observable trajectory state condition (e.g., agent has inspected target module $X$ and is about to edit function $Y$ without checking caller $Z$, or has repeated file reads $\ge 3$ times).
     - `AlternativeObjective`: What a distinct *native* next action should accomplish (e.g., inspect caller contract, run focused reproduction test, or target alternative module) without prescribing synthetic text.
     - `ComparisonCriterion`: What observable evidence in the next $L = 2$ environment observations indicates genuine semantic progress over the default path.

### Stage 2: Native Rollout with State-Triggered Checkpoint Branching

Run the coding agent normally in a checkpointable container sandbox (`OpenHands` or equivalent). At each step $t$:

1. **Check Collector Trigger & Admission Gate**:
   - Evaluate whether the current trajectory prefix $(o_1, a_1, \dots, o_t)$ matches an active compiled rule's `TriggerPredicate` (or a generic stagnation trigger if running `H0`) and passes admission (at most **1 active comparison per compiled rule** along a trajectory to cap compute).
   - If no trigger fires, execute the agent's greedy/default native action $a_t^{(0)}$ and continue to $t + 1$.
2. **Sample $M = 8$ Native Candidate Proposals**:
   - When a trigger fires at state $s_t$, query the **unmodified coding agent** ($\pi_{\text{agent}}$) with its exact native prompt to sample $M = 8$ candidate next actions $\{a_t^{(1)}, \dots, a_t^{(8)}\}$.
   - Filter out syntactic duplicates (`~89.8%` of triggered states yield distinct native actions). If all 8 proposals collapse to the same action, continue without branching.
3. **Select One Alternative Proposal ($a_t^{\text{alt}}$)**:
   - Have the collector rank the distinct native proposals against `AlternativeObjective` to pick a single distinct native candidate $a_t^{\text{alt}} \neq a_t^{\text{def}}$ that explores the under-covered hypothesis or verification step.

### Stage 3: Short-Horizon Two-Branch Execution ($L = 2$ Observations)

1. **Snapshot Sandbox State**:
   - Save the filesystem/container state at step $t$ before executing $a_t^{\text{def}}$.
2. **Roll Out Default Suffix ($\sigma_{\text{def}}$)**:
   - Execute $a_t^{\text{def}}$ and let the native agent take 1 further native step, collecting a short suffix of horizon $L = 2$ action-observation pairs: $\sigma_{\text{def}} = (a_t^{\text{def}}, o_{t+1}^{\text{def}}, a_{t+1}^{\text{def}}, o_{t+2}^{\text{def}})$.
3. **Restore Snapshot & Roll Out Alternative Suffix ($\sigma_{\text{alt}}$)**:
   - Restore the sandbox to step $t$, execute the native alternative action $a_t^{\text{alt}}$, and let the native agent take 1 further step to collect $\sigma_{\text{alt}} = (a_t^{\text{alt}}, o_{t+1}^{\text{alt}}, a_{t+1}^{\text{alt}}, o_{t+2}^{\text{alt}})$.

### Stage 4: Blind Selector Retention & Single-Lineage Export

1. **Run Blind Branch Selector**:
   - Present the trajectory prefix summary, the compiled `ComparisonCriterion`, and the two anonymized 2-step suffixes $(\sigma_{\text{def}}, \sigma_{\text{alt}})$ to the **Blind Selector** (with branch order randomized and labels hidden).
   - The selector evaluates which suffix produced stronger empirical grounding (e.g., localized a concrete symbol/traceback, falsified a bad hypothesis, or avoided a redundant edit/read loop) rather than enforcing an overly rigid "must immediately resolve the bug" filter (which degrades downstream student transfer by `-1.78` pp on `Multilingual`).
2. **Commit Winning Branch & Discard Loser**:
   - Keep the sandbox state and trajectory continuation of the winning branch ($\sigma^*$); permanently discard the losing branch.
3. **Export Pure Native Trajectory for SFT**:
   - When the rollout terminates, export the resulting single-lineage trajectory $\tau = (o_1, a_1, \dots, o_T, a_T)$. Because every action $a_t$ (including selected alternative branches) was sampled directly from $\pi_{\text{agent}}(\cdot \mid o_1, \dots, o_t)$ without prompt hints, the exported trajectory is 100% distributionally aligned with test-time inference.

---

## Recommended Hyperparameters & Operating Point

| Parameter | Recommended Value | Empirical Rationale (`src:2611-02074`) |
|:---|:---|:---|
| Prior history depth ($K$) | $K = 5$ (`SWE-Trail-H5`) | Captures `90%` of the gain of $K = 10$ (`65.67%` vs. `65.89%` on `Multilingual`) while keeping total token overhead at `<= +3.7%` over `H0` (`1.914B` vs. `1.845B` tokens), whereas $K = 10$ increases acquisition tokens by `+66.0%` (`510.0M` vs. `307.3M`). |
| Native candidate proposals ($M$) | $M = 8$ | Yields distinct native actions on `89.80%` (`1,030/1,147`) of triggered trajectories. |
| Branching width & horizon ($B \times L$) | $2$ branches $\times$ $L = 2$ steps | Keeps suffix rollout tokens to `43.1M` (`2.25%` of total collection tokens) while providing two environment observations to verify tool execution outcomes. |
| Post-collection curation | Combine with verifier (`Top-5-hybrid`) | Combining 5 `SeedBank` + 5 `H5` rollouts with test-verifier selection reaches `66.22%` on `Multilingual` (`+2.89` pp over `SeedBank`) and `43.14%` on `SWE-Pro` (`+1.92` pp). |

## Pitfalls to Avoid

- **DON'T inject prior trajectory summaries into the agent's system or user prompt during collection**: Even if you strip the injected advice before SFT (`Advice removed`), the agent's actions remain conditioned on information absent from the visible context, reducing `SWE-bench Multilingual` accuracy from `65.67%` (`H5`) to `63.00%` (`-2.67` pp).
- **DON'T replace state-triggered detection or blind selection with random branching**: Triggering comparisons at random steps (`random detection`) drops student performance by `-1.44` pp on `Multilingual` and `-1.28` pp on `SWE-Pro`; choosing branches at random (`random retention`) drops performance by `-0.89` pp and `-1.19` pp.
- **DON'T use an overly conservative selector that rejects exploratory branches unless they immediately fix the bug**: A stricter selector control achieved nearly identical collection resolution (`343/1,500` vs. `345/1,500`) but reduced downstream 124B student accuracy by `-1.78` pp on `Multilingual` (`63.89%`) and `-0.91` pp on `SWE-Pro` (`41.91%`).
