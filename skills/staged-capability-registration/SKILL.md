---
name: staged-capability-registration
description: >
  Run a self-improving agent's capability loop as fast discovery with slow
  registration. Weight failures by the consequence of the error, cluster
  them into capability gaps, and build candidate tools freely. Admit a
  candidate to the persistent toolkit only after it shows a mean gain above
  a margin, with no increase in consequence-weighted cost, across K fresh
  prospective cohorts. Prevents one bad tool from contaminating later
  self-improvement rounds.
  Derived from "MedRSI: Recursive Self-Improvement for Medical Agents via
  Clinically Aligned Self-Evolution" (arXiv:2609.24838).
source: https://arxiv.org/abs/2609.24838
---

# Staged Capability Registration

Use this skill when an agent writes, composes, or trains its own tools
from its failures, and those tools persist and shape future rounds of
self-improvement.

## When to Use

- A self-improvement loop adds tools, skills, or models to a persistent
  registry that later rounds build on
- Errors differ in cost (a missed critical case is not a borderline
  disagreement) and fixing the most frequent errors is the wrong target
- You see early gains followed by decline as the toolkit grows
- You need an auditable record of why each capability was admitted

## Core Insight

Keep **discovery** permissive and **registration** conservative. A tool
that helped on the cases that motivated it may not help on new cases. Once
it is registered, the planner uses it, its outputs enter the execution
records, and later reflection learns from those records. An unstable tool
therefore also corrupts the direction of future improvement.

**Evidence** (glaucoma trajectory, GPT-4o backbone, 5 seeds each):

- **Immediate registration** led at first (89.6% vs 88.6% balanced accuracy
  at round 8), then fell to **82.4% at round 20 and 76.9% at round 30** with
  57 tools. Full MedRSI kept **94.4% at round 30** with 18 tools.
- **Case study**: one texture tool gained 6.1 points on its discovery
  cohort, then −2.3, −5.4, and −3.1 on the next three cohorts. Once
  registered, the planner called it in 81% of subsequent cases, and within
  four rounds the agent built three tools to post-process its flawed output.
- **Rejections**: over 30 rounds, slow registration rejected 43 tools that
  immediate registration would have accepted. 29 of them showed negative
  mean trial gain.
- **Uniform failure priority** reached 97.8% training but only 88.7% test
  balanced accuracy (a 9.1-point gap, versus 1.6 points for MedRSI).
  Clinical cost was 6.0 per 100 patients, versus 2.5.

---

## Procedure

### 1. Fix the Envelope

Freeze the reasoning model and the execution workflow for the whole
trajectory. Let self-improvement act **only** on the tool registry (tool
descriptions, code, trained checkpoints). Partition data by entity (for
example, patient or customer), not by record, into: builder training data,
experience batches, a discovery set, K trial cohorts, and a locked final
test set.

### 2. Diagnose, Then Score Consequence

Run the stable agent on an experience batch, committing predictions
before labels are revealed. For each error `e_i = 1`, have a frozen judge
(fixed prompt, model version, rubric, and output schema) assign an ordinal
consequence `s_i ∈ {0..4}` from the change in downstream action the error
implies. Calibrate the judge against expert labels once (for example,
weighted κ), then keep it frozen across rounds and ablations. Mark cases
with insufficient evidence as unresolved and leave them out of
prioritization.

Priority: `q_i = e_i · (1 + λ · s_i/4)`. The paper found λ = 2 best, with a
stable range of about 1–4. λ = 8 over-focused on a few severe cases (92.4%
vs 94.1%).

### 3. Cluster Failures into Capability Gaps

Group high-priority failures by task, modality, failed intermediate
operation, and tool-use pattern. Fill the reflection buffer round-robin:
take the top-`q` case from each cluster before second picks, so that one
recurrent failure cannot consume the budget. Without clustering, the
builder produced four near-duplicate candidates and reached 90.2% instead
of 94.1%.

For each cluster, reflection writes a **capability specification**: the
missing operation, supporting evidence, inputs, and outputs, the endpoint
on which benefit will be judged, compatible existing tools, and the
development route.

### 4. Build Candidates by Every Available Route

- **Code generation** for deterministic measurement and transformation, with
  explicit unit, shape, and missing-value contracts
- **Composition** of registered tools into higher-level procedures
- **Model development** when the capability must be learned (the builder
  picks the architecture and hyperparameters and trains only on its own
  data partition)

The routes are complementary. Code-only reached 79.8%, without model
development 84.3%, without composition 89.1%, and all three 94.1%. Package
each candidate with code, weights, schemas, a calling description,
dependencies, the development record, and a **version hash**. Run
functional checks before any evaluation.

### 5. Discovery Screen (Permissive)

Compare the stable agent with the stable agent plus the candidate
(available to the planner, not forced) on the discovery set under matched
settings and seeds. If `ΔP_disc > 0`, the candidate enters the
**experimental pool**. Freeze its package: any later edit creates a new
candidate with a new history. Only evaluator copies of the agent may see
pool tools. The stable agent never uses them.

### 6. Prospective Trials, Then Registration (Conservative)

Evaluate each frozen candidate on K fresh cohorts (the paper's default
K = 3) that were not used to fit or discover it, recording `ΔP_k` and the
consequence-weighted cost change `ΔC_k`. Register the candidate only if
both hold:

```
mean_k ΔP_k > δ          (δ = 0.005 balanced accuracy in the paper)
mean_k ΔC_k ≤ 0          (no increase in consequence-weighted cost)
```

A candidate with trial gains of +3, −1, −2 has mean 0 and is rejected. If
an eligible cohort is not yet available, leave the candidate pending; do
not register on partial evidence.

### 7. Commit Serially

Before registering, compare the candidate's reference-registry hash with the
current registry. If the registry changed during the trial, re-evaluate the
candidate in the new context. Package updates to shared components together
with the dependents they affect, and evaluate them as one change. Archive
rejected candidates with their trial records. They can inform later
reflection, but they never reach stable trajectories.

---

## Environment Caveats

- **K trades speed for stability**: K = 1 admitted 39 tools and reached
  84.7% at round 30. K = 3 admitted 18 tools at 94.4%. K = 5 admitted 12
  tools at 94.3%, but each candidate took two more rounds to qualify.
- **Cost**: one public-task trajectory used 212 A100 hours and 1.9 billion
  tokens over 4.5 days. Model training took 68% of the accelerator hours.
- Requires enough labelled data to fill K independent cohorts. Small
  cohorts make `ΔP_k` noisy (the whole heart-disease trial partition was
  19 subjects).
- The consequence judge is itself a model. If it drifts, the priorities
  drift with it, so freeze it.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:--|:--|:--|
| Self-reinforcing degradation | Discovery-set winner registered immediately | Steps 5–6: experimental pool plus K-cohort trials |
| Improving the wrong errors | Frequency-weighted reflection | Step 2 consequence weighting |
| Duplicate tools | Reflecting on single failures | Step 3 clustering |
| Context-dependent gain | Registry changed during the trial | Step 7 hash check and re-evaluation |
| Aggregate gain bought with worse severe errors | Mean accuracy up, severe errors up | The `ΔC ≤ 0` condition in step 6 |
| Evaluator gaming | Agent edits the judge or trial data | Keep the judge, rubric, and cohorts outside the editable envelope (step 1) |

---

## Cross-References

- `skills/recursive-self-improvement-loop/SKILL.md`: the AIDE²
  propose-benchmark-select loop commits on selection-suite gains. Put
  steps 5–6 of this skill between its "Select" and "Commit" steps.
- `skills/controlled-skill-lifecycle-management/SKILL.md`: typed failure
  diagnosis and versioned promotion for skills rather than tools
- `skills/stable-skill-evolution/SKILL.md`: damping oscillation in
  skill-text updates
- `rules/recursive-improvement.md`: "DON'T: Accept modifications based on
  aggregate metrics alone" and "DO: Evaluate evolved instructions against
  immutable, held-out negative security testbeds"
- `rules/skill-system-design.md`: "DO: Bound the search space of harness
  self-evolution"
- `research-briefs/process-level-self-evolution-evaluation.md`: measured
  harmful-commit and missed-improvement rates for acceptance gates

## Sources

> Wu, Zhu, Hu et al., "MedRSI: Recursive Self-Improvement for Medical
> Agents via Clinically Aligned Self-Evolution" (arXiv:2609.24838),
> Sep 2026.
