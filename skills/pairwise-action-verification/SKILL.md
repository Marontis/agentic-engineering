---
name: pairwise-action-verification
description: >
  Spend test-time compute per step of a terminal or coding agent: sample
  N candidate commands from the same history, pick one with a pairwise
  verifier (margin-weighted win rate), and execute only the winner.
  Covers choosing listwise vs pointwise vs pairwise verification,
  decision-only verifier outputs to cut cost, distilling a frontier
  verifier into the agent's own model, and composing with trajectory-level
  best-of-T or sequential refinement.
  Derived from "Mid-Harness: Scaling Actions Between Model and Harness
  for Terminal Agents" (arXiv:2609.39982).
source: https://arxiv.org/abs/2609.39982
---

# Pairwise Action Verification (Mid-Harness)

Use this skill when a terminal or coding agent's single bad command can
derail the rest of the trajectory, and you have budget for extra model
calls per step but not for many full environment re-runs.

## When to Use

- Each executed command changes the environment, so a poor action early
  costs more than a poor final answer.
- Sampling several actions from the model at the same step shows that
  better options exist (high pass@k, low pass@1).
- Trajectory-level scaling (best-of-T, retries) is limited because
  environment runs are expensive or the environment can't be
  snapshotted cheaply.
- You can't or don't want to change the generator model or the harness
  itself; this sits between them.

Not a security control. The verifier picks the most useful action; it
is not trained or tested to reject malicious ones. For untrusted inputs,
keep a pre-execution safety audit (see
[`pre-execution-action-auditing`](../pre-execution-action-auditing/SKILL.md))
and command classification ("DO: Classify every agent command before
execution", `rules/agent-sandbox-safety.md`).

## Core Insight

Wider sampling only helps as much as the verifier can exploit it. With a
weak (listwise) verifier, going from 4 to 8 candidates barely moved
pass@1; with a pairwise verifier the same candidates gave more. Pairwise
comparison is the most expensive mechanism but the most accurate, and
asking for a bare A/B decision instead of a reasoned one kept or improved
accuracy while cutting cost.

**Evidence** (TMAX-9B generator on TerminalBench-Lite, Vanillux2 harness,
base pass@1 50.00%):

- Candidate coverage: an oracle-strength verifier (GPT-5.6 Sol) choosing
  among N = 8 candidates reached 68.03% pass@1 (64.63% at N = 4).
- Self-verification by TMAX-9B at N = 8: listwise 51.02%, pairwise
  54.76% pass@1 (pass@3 67.35% vs 71.43%). Listwise at N = 4 was 49.32%.
- Distilling 117k GPT-5.6 Sol pairwise comparisons (from 732
  trajectories) into TMAX-9B with LoRA: 57.14% pass@1 and 75.51% pass@3
  at N = 8, without changing the generator.
- Decision-only pairwise verification improved pass@1 while cutting
  reference-priced token cost by 20.9% (zero-shot) and 24.1%
  (distilled) at N = 8.
- Composition: best-of-T (T = 3) alone 55.10%; with distilled
  Mid-Harness 66.33%, same 3 environment runs. Sequential refine (R = 1)
  55.10% → 60.20% with distilled Mid-Harness. Distilled Mid-Harness at
  N = 8 matched best-of-T at T = 5 (57.14%) at about one third of its
  reference-priced token cost.
- Transfer (pass@1): Terminal-Bench 2.1 21.72% → 27.34% (zero-shot)
  / 26.59% (distilled); FeatureBench-Mini 1.45% → 7.25% (distilled);
  SWE-bench Verified Mini 46.67% → 48.67% (distilled). Other generators
  gained less: Qwen3.5-9B 40.48% → 42.52%, Nemotron3.5 Lightning
  41.16% → 43.20% (zero-shot).

---

## Procedure

### 1. Measure Candidate Coverage First

Before building a verifier, check that the generator produces useful
alternatives: sample N actions per step and let the strongest verifier
you can afford choose. If pass@1 under that strong chooser barely beats
the base agent, the generator lacks coverage and no verifier will help.

### 2. Sample N Candidates per Step

At each step, sample N candidate actions from the same model and the
same history. The paper used N = 4 and N = 8. Execute nothing yet.

### 3. Choose the Verification Mechanism

- **Pairwise (default)**: the verifier compares two candidates and
  returns a preference with a margin. Run all pairs (28 calls for
  N = 8, parallelizable) and pick the candidate with the highest
  margin-weighted win rate.
- **Listwise**: one call ranks all N. Cheapest, but weakest in the paper;
  ranking many options at once is hard.
- **Pointwise**: one score per candidate. Parallel, but scores across
  different action types are poorly comparable.

Ask for a **decision only** (A or B, with margin) rather than a written
rationale unless you need the rationale for audit; it was cheaper and no
worse.

### 4. Execute Only the Winner

Run the selected action, append its observation to the history, and
repeat. The harness and generator stay unchanged.

### 5. Distill the Verifier (Optional)

If a frontier verifier is too costly per step, collect its pairwise
judgements on your own trajectories and fine-tune the agent's model
(LoRA in the paper) as the verifier. Hold out tasks to measure
agreement with the frontier judge before deploying. In the paper's
offline check on 21 held-out tasks, pairwise agreement with the frontier
verifier rose from 59.01% (zero-shot) to 74.58% (distilled).

### 6. Compose With Trajectory Scaling

If you already run best-of-T or sequential refinement, add action-level
verification inside each trajectory instead of raising T. Compare at
equal token cost and equal environment runs, not at equal T.

---

## Environment Caveats

- **Late-episode decay.** Distilled-verifier agreement fell from 68.13%
  in turns 1–4 to 54.07% in turns 17–32. Long episodes get less benefit.
- **The verifier can't run the command.** 67.4% of the distilled
  verifier's remaining disagreements involved command semantics or
  execution feasibility, i.e. predicting what the command will do in
  this environment.
- **More verifier samples did not reliably help** (the paper's appendix
  analysis); spend extra budget on candidates or distillation instead.
- **Distillation data**: 117k frontier comparisons from 732
  trajectories. Scalability to other domains is not shown.
- **No action-level ground truth.** Coverage and verifier quality were
  inferred from trajectory success, not from labelled correct actions.
- Gains depend on the generator: the RL-trained TMAX models gained
  most; other 9B-class generators gained about 2 points.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Width without benefit | Raising N with a weak verifier | Pairwise verification (step 3); check coverage first (step 1) |
| Verifier cost explodes | O(N²) pairwise calls with rationales | Decision-only outputs; parallelize; distill (step 5) |
| Wrong choice late in long episodes | Verifier agreement decays with turn index | Keep trajectory-level checks; consider smaller N late |
| Plausible but infeasible command chosen | Verifier can't predict environment effects | Pair with a dry-run or sandboxed execution where possible |
| Treated as safety gate | Useful-action verifier selects a harmful action | Separate pre-execution safety audit |

## Cross-References

- [`harness-value-planning-vs-verification`](../../research-briefs/harness-value-planning-vs-verification.md):
  trajectory-level release verifier; this skill verifies per action.
- `rules/recursive-improvement.md` "DO: Invest in standalone verifiers
  before planning components".
- [`speculative-macro-commit`](../speculative-macro-commit/SKILL.md),
  [`mcts-coding-agent`](../../research-briefs/mcts-coding-agent.md).

> Source: Kang, Hachiuma, Zhang et al., "Mid-Harness: Scaling Actions
> Between Model and Harness for Terminal Agents" (arXiv:2609.39982),
> Sep 2026.
