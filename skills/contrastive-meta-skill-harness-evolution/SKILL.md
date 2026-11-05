---
name: contrastive-meta-skill-harness-evolution
description: >-
  Precompute a reusable, frozen Meta-Skill from three-condition contrastive
  training rollouts (`act`, `hold`, and `avoid` directives across `start`,
  `during`, and `end` checkpoints) to guide task-local online harness evolution
  while resetting to the seed harness between tasks. Derived from Meta^2
  (arXiv:2611.05139).
---

# Contrastive Meta-Skill Harness Evolution

> **Source**: [arXiv:2611.05139](https://arxiv.org/abs/2611.05139) — *Meta$^2$: Precomputing Reusable Knowledge for Online Harness Evolution in Long-Horizon Agents* (Yuan et al., 2026) | `src:2611-05139v1`

## When to Use This Skill

Use this procedure when a long-horizon agent (such as a terminal workflow agent, software engineering repair agent, or data-pipeline orchestrator) faces heterogeneous tasks where a single static harness underperforms, yet carrying online harness mutations across tasks causes cross-task interference. Instead of freezing a task-optimized harness offline or accumulating unguided online edits across a stream of tasks, precompute a compact **Meta-Skill** $\mathcal{M}$ offline from paired contrastive trajectories, freeze $\mathcal{M}$ before deployment, and use it to steer bounded, task-local online harness edits that reset to the clean seed harness $h^{(0)}$ at the start of every new task.

---

## Core Architecture: Decoupling Meta-Knowledge from Harness State

Long-horizon harness optimization mixes two distinct objects:
1. **Cross-task meta-knowledge ($\mathcal{M}$)**: Reusable rules governing *when* to intervene in a live trajectory, *which* harness surface to edit, *when* to hold back, and *which* interventions backfire.
2. **Task-local harness state ($h_t$)**: The active system prompt additions, progress probes, pre-tool middleware, helper tools, and completion checks tailored to the specific trajectory currently unfolding.

Across tasks, $\mathcal{M}$ transfers reliably, whereas concrete harness edits $h_t$ frequently overfit to one repository or environment. On `Terminal-Bench 2.1` (60 test tasks, `mean@5`) and `DeepSWE 1.1` (75 test tasks across 91 repositories, `mean@3`) with `GPT-5.6-Terra`, precomputing and freezing a contrastive Meta-Skill while resetting $h_t \leftarrow h^{(0)}$ between tasks reaches **81.00 ± 0.91%** and **44.44 ± 0.77%** (+14.67 and +9.77 percentage points over the `NexAU` seed harness at **66.33%** and **34.67%**), outperforming both offline `Meta-Harness` (**73.33%** and **37.33%**) and cross-task `Continual Harness` (**72.67%** and **33.78%**). Retaining online harness edits across tasks instead of resetting to $h^{(0)}$ drops resolution to **78.33%** on `Terminal-Bench 2.1` (−2.67 pp) and **39.11%** on `DeepSWE 1.1` (−5.33 pp).

---

## Step-by-Step Procedure

### Phase 1: Offline Contrastive Trajectory Collection

On a small training split of tasks $\mathcal{D}_{\text{train}}$ (for example, 29 training tasks on `Terminal-Bench 2.1` or 38 on `DeepSWE 1.1`), initialize an empty Meta-Skill $\mathcal{M}^{(0)} = \emptyset$ and iterate for $r = 1, \dots, R$ rounds (typically $R = 3$). In each round, run every training task $x \in \mathcal{D}_{\text{train}}$ under three matched conditions starting from the same seed harness $h^{(0)}$:

1. **Condition A (Task Agent Alone)**: Run the task agent under the fixed seed harness $h^{(0)}$ with no online evolver interventions, producing trajectory $\tau_A$ and binary verifier outcome $v_A \in \{0, 1\}$.
2. **Condition B (Meta-Skill-Guided Online Evolver)**: Run the task agent alongside the online harness evolver guided by the current Meta-Skill $\mathcal{M}^{(r-1)}$, producing trajectory $\tau_B$, checkpoint edit log, and outcome $v_B \in \{0, 1\}$.
3. **Condition C (Verifier-Informed Online Evolver)**: Run the task agent alongside an online evolver that additionally observes privileged training-time diagnostic specifications (such as the ground-truth grading script or reference test expectations), producing trajectory $\tau_C$ and outcome $v_C \in \{0, 1\}$.
   - **Anti-leakage constraint**: The privileged verifier specification is used strictly during offline training to expose which trajectory failure modes were fixable through legitimate harness interventions. Every candidate rule distilled from Condition C must be audited to strip task-specific strings, expected outputs, filenames, and hidden grader checks before entering $\mathcal{M}^{(r)}$.

---

### Phase 2: Five-Way Contrastive Attribution (`REFLECT`)

For each training task $x$, compare the outcomes $(v_A, v_B, v_C)$ and their corresponding checkpoint trajectories $(\tau_A, \tau_B, \tau_C)$ across five contrast directions. Map each informative pair to one of three typed Meta-Skill entry classes — **`act`**, **`hold`**, or **`avoid`** — tagged with the lifecycle phase **`start`** (after turn 1), **`during`** (periodic mid-run checkpoints), or **`end`** (when the agent claims completion):

| Contrast Direction | Outcome Signature | Diagnostic Question | Target Entry Type |
|:---|:---|:---|:---|
| **Informed** | $v_C = 1,\; v_B = 0$ | What observable trajectory symptom did the verifier-informed evolver act on that the current Meta-Skill missed, and which harness primitive resolved it without referencing hidden grader details? | **`act`** (new positive intervention rule) |
| **Effective** | $v_B = 1,\; v_A = 0$ | Which specific checkpoint intervention in $\tau_B$ rescued a failure that occurred in the unguided run $\tau_A$? | **`act`** (validated positive intervention rule) |
| **Harmful** | $v_A = 1,\; v_B = 0$ | Which online intervention in $\tau_B$ disrupted a trajectory that would have succeeded under the unmodified seed harness $h^{(0)}$? | **`avoid`** (anti-intervention constraint) |
| **Overreach** | $v_B = 1,\; v_C = 0$ | Where did excessive diagnostic checking or heavy-handed harness rewriting in $\tau_B$ or $\tau_C$ derail execution? | **`avoid`** (anti-overreach constraint) |
| **Unnecessary** | $v_A = 1,\; v_B = 1$ | Which trajectory signals indicated healthy autonomous progress where online harness mutation added cost without changing the outcome? | **`hold`** (non-intervention rule) |

Each extracted task-level candidate entry must record four structured fields:
- **Phase**: `start`, `during`, or `end`.
- **Directive Type**: `act`, `hold`, or `avoid`.
- **Observable Trigger**: The domain-general behavioral signal in the agent's recent actions, tool outputs, or workspace state (for example, repeated command failures without state inspection, or a completion claim before running any independent verification check).
- **Prescribed Harness Operation**: Which bounded edit primitive to invoke (`notice`, `append_worker_prompt`, `register_check`, `register_probe`, `add_tool`, `add_skill`, `add_middleware`, or `rollback`), or explicit non-intervention (`noop`).

---

### Phase 3: Cross-Task De-Instantiation and Consolidation (`AGGREGATE` and `UPDATE`)

Raw task-level reflections contain instance-specific noise. Before updating $\mathcal{M}^{(r)}$, consolidate candidate entries across the training batch:

1. **Cluster by Behavioral Mechanism (`AGGREGATE`)**: Group task-level entries that share the same lifecycle phase, directive type, observable trajectory symptom, and harness primitive.
2. **Enforce Multi-Task Support**: Retain a new candidate pattern only if it is supported by evidence from **at least 2 distinct training tasks** ($\ge 2$ tasks), filtering out one-off task idiosyncrasies.
3. **De-Instantiate Domain Nouns**: Rewrite every retained entry to remove repository names, package names, file paths, and benchmark-specific constants so that triggers refer solely to observable process dynamics (such as edit-without-test loops, silent truncation, or unverified completion claims).
4. **Apply Structured Library Edits (`UPDATE`)**: Reconcile the aggregated families against $\mathcal{M}^{(r-1)}$ using five explicit operations:
   - `ADD`: Insert a newly supported `act`, `hold`, or `avoid` entry.
   - `MERGE`: Combine two overlapping entries into one canonical rule.
   - `REFINE`: Sharpen the trigger condition or narrow the prescribed harness primitive when a rule caused a `harmful` or `overreach` contrast on a subset of tasks.
   - `DELETE`: Remove an entry whose empirical contrast balance turned negative.
   - `NONE`: Leave validated entries unchanged.
5. **Acceptance Gate**: After round $R$, freeze $\mathcal{M} = \mathcal{M}^{(R)}$. Before promoting a revised Meta-Skill $\mathcal{M}$ or any persistent seed-harness change to production, evaluate it through the single acceptance gate in [`rules/recursive-improvement.md`](../../rules/recursive-improvement.md) ("DO: Pass every self-modification through one acceptance gate"), verifying non-regression within the noise margin $\delta$ on held-out tasks and strict zero-tolerance compliance on the negative security testbed.

---

### Phase 4: Bounded Task-Local Online Harness Evolution

At test time, freeze $\mathcal{M}$ and **reset the active harness to the clean seed $h^{(0)}$ at the start of every task**. Never carry online prompt edits, registered checks, or ad-hoc helper scripts from one task instance into the next.

Invoke the online evolver only at three event-driven checkpoints:
- **`start` checkpoint**: Immediately after turn 1, once the agent's initial inspection reveals the task structure and environment layout.
- **`during` checkpoints**: Every $L = 5$ execution steps (which achieves the Pareto frontier of accuracy and cost on `Terminal-Bench 2.1` at **81.00%** and \$64.72 online cost, outperforming $L = 1$ at **79.00%** / \$83.41 and $L = 3$ at **80.33%** / \$74.22).
- **`end` checkpoint**: Whenever the task agent attempts to declare completion, before final termination is permitted.

At each checkpoint, the evolver inspects the trajectory delta since the prior checkpoint against the phase-matched `act`, `hold`, and `avoid` entries in $\mathcal{M}$:
1. **Check `avoid` and `hold` rules first**: If the trajectory matches a `hold` condition (steady verified progress) or if a candidate edit matches an `avoid` rule, emit `noop` and let the task agent continue uninterrupted.
2. **Apply bounded `act` primitives**: When an `act` trigger fires, restrict modifications to lightweight, reversible channels:
   - **Steering notices (`notice`)**: Inject at most **1** concise steering message per checkpoint, capped at **2** mid-run notices and **2** terminal completion send-backs per task to prevent nag loops.
   - **Verification and observability hooks (`register_check`, `register_probe`)**: Register deterministic pre-completion checks or progress probes that run automatically before the agent is allowed to finish.
   - **Incremental harness extensions (`append_worker_prompt`, `add_tool`, `add_skill`, `add_middleware`)**: Prefer additive prompt guidance and small task-scoped verification helpers over full prompt rewrites (`rewrite_worker_prompt`).
   - **Immediate reversion (`rollback`)**: If an online harness edit degrades the subsequent $L$-step window (for example, introducing tool errors or stalling progress), invoke `rollback` at the next checkpoint to restore the prior harness snapshot.

---

## Failure Modes & Guardrails

| Failure Mode | Symptom | Mitigation |
|:---|:---|:---|
| **Self-distillation without contrastive anchors** | Evolver trained only on its own unguided successes/failures learns generic advice and misses non-intervention boundaries (**77.00** vs **81.00** points on `Terminal-Bench 2.1`; **35.56** vs **44.44** points on `DeepSWE 1.1`). | Require all three offline rollout conditions (A, B, C) so `hold` and `avoid` rules are grounded in explicit `A-pass/B-fail` and `A-pass/B-pass` contrasts. |
| **Cross-task harness accumulation** | Carrying online prompt edits, tools, or checks from task $i$ to task $i+1$ pollutes later tasks with stale repository assumptions (dropping `DeepSWE 1.1` by −5.33 pp from **44.44** to **39.11** points). | Freeze $\mathcal{M}$ during deployment and reset $h_t \leftarrow h^{(0)}$ before every new task. |
| **Verifier leakage during Condition C** | Offline reflections copy literal test assertions or expected output strings from the privileged grader into $\mathcal{M}$. | Audit every `informed` ($v_C=1, v_B=0$) candidate rule to strip literal grader strings and require $\ge 2$ distinct training tasks before admission. |
| **Over-frequent checkpointing ($L = 1$)** | Invoking the evolver after every step inflates online cost (+28.9% on `Terminal-Bench 2.1`) and interrupts valid multi-step plans (−2.00 pp accuracy). | Default to $L = 5$ step intervals plus turn-1 (`start`) and pre-completion (`end`) triggers, and enforce hard per-task caps on `notice` injections. |

---

## Related Skills and Rules

- [`regularized-harness-evolution`](../regularized-harness-evolution/SKILL.md) — Offline bounded harness evolution within a fixed editable set.
- [`reference-trajectory-harness-evolution`](../reference-trajectory-harness-evolution/SKILL.md) — Credit assignment for harness evolution using reference trajectories.
- [`selective-step-verification`](../selective-step-verification/SKILL.md) — Confidence-gated step verification inside long-horizon harnesses.
- [`rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — "DO: Pass every self-modification through one acceptance gate".
- [`rules/skill-system-design.md`](../../rules/skill-system-design.md) — "DO: Bound the search space of harness self-evolution".
