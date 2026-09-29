---
name: regularized-harness-evolution
description: >
  Run automated harness evolution (prompts, control flow, tools, memory,
  context management, skills around a frozen model) under explicit
  regularizers: an annealed per-round edit budget, evidence-aware credit
  assignment, leakage screening, a noise-adjusted acceptance floor, a
  cost-vs-gain acceptance rule, and structural pruning. Use it so gains
  transfer out of distribution instead of overfitting the evolve set and
  bloating the harness.
  Derived from "RRSI: Regularized Recursive Self-Improvement of Agent
  Harnesses" (arXiv:2609.24972).
source: https://arxiv.org/abs/2609.24972
---

# Regularized Harness Evolution (RRSI)

Use this skill when an outer loop proposes edits to an agent harness
around a **frozen** backbone model, scores them on an evolve set, and
keeps the winners, and you need the kept edits to hold up on tasks the
loop never scored.

## When to Use

- You run (or are building) a propose → evaluate → accept loop over a
  harness (Meta-Harness / AHE / HarnessX style). Evolve-set gains are
  large, but held-out or out-of-distribution scores are flat or below
  the starting harness.
- Evolved harnesses keep growing in tokens per trial, steps, and
  components without a matching capability gain.
- Evaluation is noisy (stochastic agents, rubric graders) and you
  suspect you are keeping lucky candidates.
- You need a concrete way to implement `rules/skill-system-design.md`
  "DO: Bound the search space of harness self-evolution".

Not for weight updates: the paper explicitly excludes settings where
model weights change during evolution.

## Core Insight

Harness evolution fails the way an unregularized model fits: it
memorizes the evolve set (task names, values, answers), keeps noise
winners, and piles up complexity. Standard regularizers, applied to
**what may be proposed** and **what may be accepted**, trade a little
evolve-set score for transfer and a lighter harness.

**Evidence** (frozen policy Claude Opus 4.8 unless noted; 8 benchmarks
across coding, agentic workspace and engineering design):

- Agentic-workspace ablation. Unregularized evolution: evolve 92.8,
  out-of-distribution average 40.3, 3.80M policy tokens per trial.
  RRSI: evolve 90.5, **OOD average 43.6**, **2.42M** tokens per trial
  (starting harness: 89.4 / 39.7 / 1.56M). Removing only the acceptance
  regularizers raised the evolve score to 91.5 but dropped OOD to 41.0.
- Against four prior harness-evolution methods on the same evolve set
  and budget, the best baseline on the evolve set (Meta-Harness, 93.0)
  reached only 40.6 OOD; TTHE ended below the starting harness (38.0
  vs 39.7). The paper reports RRSI beats the average prior baseline
  OOD by up to 22.9%, and that its harness uses 30% fewer policy tokens
  than unregularized evolution.
- Coding: Terminal-Bench 2.1 74.2 → 80.2 (evolve) with SWE-bench
  Verified 82.0 → 83.8 never scored during evolution. With Gemini 3.5
  Flash as the policy: 64.6 → 78.7 (+14.1). A harness evolved on Gemini
  3.5 Flash moved an unseen Gemini 3.1 Flash Lite from 11.2 to 14.6 on
  Terminal-Bench 2.1.

---

## Procedure

### 0. Set Up the Loop

- Freeze the backbone policy. Name the editable harness components
  (prompts, control flow, tool interfaces, memory, context management,
  skills) and keep everything else (graders, evolve/held-out splits,
  security tests, the proposer/critic themselves) **outside** the
  editable surface. In the paper the proposer and critic are fixed
  LLMs and only the harness is evolved.
- Split tasks into an evolve set and a held-out set, and keep at least
  one out-of-distribution benchmark that is **never scored during
  evolution**.
- **Calibrate the noise band δ** by re-running the unchanged starting
  harness several times on the evolve set. The paper calibrated δ from
  repeated base-harness evaluations (about 3/178 trials for agentic
  workspace; about 60/14,100 rubric criteria for design).

### 1. Annealed Edit Budget (L0-style sparsity)

Allow at most `b_t` component edits in round `t`, decaying by cosine
annealing from `b_max` to `b_min` over `T` rounds:

```
b_t = ceil( b_min + (b_max - b_min) * 0.5 * (1 + cos(pi * t / T)) )
```

Paper values: `T = 8`, `b_min = 1`, `b_max = 3` (coding) or `4`
(agentic, design). Early rounds allow coordinated multi-part changes;
late rounds allow only single, attributable edits.

### 2. Evidence-Aware Credit Assignment

Log every proposed edit as a record: component, hypothesis, diff, score
change, cost change, accepted/rejected. Give the proposer the full log so
it does not retest hypotheses that have already failed.

### 3. Structured Exploration on Stall

If progress over the last `w` rounds stays inside the noise band δ
(paper: `w = 3`), reserve part of the next round's budget for component
**types** not yet edited. Do not respond to a stall by widening what may
be edited. The editable set stays fixed.

### 4. Leakage Screening (before any evaluation)

Run a critic over each candidate diff and reject it if it contains task
names, entity names, task-specific values, answers, or other logic
specific to the evolve benchmark. This check is cheap. Run it before
paying for evaluation.

### 5. Stability-Aware Acceptance

With incumbent score `S*`, a candidate `H'` is admissible only if

```
S_hat(H') >= S* - δ
```

Gains inside the noise band do not count as gains (see step 6).

### 6. Complexity-Aware Acceptance (Ridge/L2-style)

For candidates with a real gain (`ΔS > δ`), require that the relative
increase in policy-token cost be justified by the gain:

```
ΔC <= β0 + β1 * ΔS
```

Paper values: `β0 = 0.05, β1 = 0.5` (coding); `β0 = 0.10, β1 = 0.3`
(agentic, design). Among admissible candidates, keep the highest-scoring.

### 7. Domain Guards (non-compensatory)

Add hard reject rules for reliability metrics that a score gain must not
offset. Example from the paper (engineering design): reject if the
valid-output rate falls by more than 0.03 or the no-submission rate
rises by more than 0.02 versus the incumbent. Put your **security /
negative testbed** here as a guard (see Environment Caveats).

### 8. Structural Pruning (Lasso/L1-style)

Track each component's best gain over the last `n_prune` rounds (paper:
`n_prune = 4`). Mark components with no strictly positive gain in that
window for deletion, and propose their removal as ordinary candidates
that go through steps 4–7.

### 9. Report Transfer, Not Evolve Score

The result is the held-out and never-scored OOD numbers, plus tokens
per trial and steps per trial. A rising evolve score with flat OOD
means overfitting, not progress.

---

## Environment Caveats

- **No security checks in the paper.** RRSI's guards target
  generalization and cost. The paper has no adversarial, safety or
  immutable-test component. Before using this loop anywhere real, add
  the immutable negative security testbed from
  `rules/recursive-improvement.md` ("DO: Evaluate evolved instructions
  against immutable, held-out negative security testbeds",
  arXiv:2609.17817) as a step-7 domain guard, and apply the
  no-regression acceptance gate on previously correct cases (H7 in the
  2026-09-28 deconfliction report).
- Hyperparameters (δ, β, budgets, windows) are per-domain and were
  hand-set. Recalibrate δ whenever the grader or task pool changes.
- The main policy was Claude Opus 4.8. Cross-model transfer was shown
  for one pair (Gemini 3.5 Flash → 3.1 Flash Lite); re-benchmark on
  each deployment model.
- The approach needs repeated evaluation to estimate δ, which is
  expensive with rubric graders (about 14,000 criterion verdicts per
  Harvey LAB evaluation).

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Benchmark-specific fitting | Edits encode task names or answers | Leakage screening (step 4); never-scored OOD benchmark (step 0) |
| Noise chasing | Repeated stochastic evaluation keeps lucky winners | Calibrated δ floor (step 5); gains inside δ don't count |
| Harness bloat | Small score gains bought with large token growth | `ΔC <= β0 + β1·ΔS` rule (step 6); structural pruning (step 8) |
| Unattributable late edits | Many simultaneous edits late in the search | Annealed edit budget down to `b_min = 1` (step 1) |
| Retesting failed hypotheses | Proposer has no memory of rejected edits | Evidence log passed to proposer (step 2) |
| Stall leads to scope creep | Plateau prompts "expand editable surface" | Explore unused component *types* within the fixed surface (step 3) |
| Security regression accepted | Score gate has no safety check | Negative security testbed as a domain guard (step 7) |

---

## Cross-References

- `rules/skill-system-design.md` "DO: Bound the search space of harness
  self-evolution": this skill is a concrete way to implement it.
- `rules/recursive-improvement.md` "DON'T: Accept modifications based on
  aggregate metrics alone" and the negative-testbed rule.
- [`reference-trajectory-harness-evolution`](../reference-trajectory-harness-evolution/SKILL.md):
  complementary credit assignment via first divergent step. Use it for
  proposal targeting and RRSI for acceptance.
- [`recursive-self-improvement-loop`](../recursive-self-improvement-loop/SKILL.md)
  (AIDE²): its stagnation response now matches step 3 here (explore
  unused component types within the fixed editable set) after the H1
  fix in the 2026-09-28 deconfliction report.
- [`harness-tampering-audit`](../harness-tampering-audit/SKILL.md),
  [`stable-skill-evolution`](../stable-skill-evolution/SKILL.md).
- Briefs: [`robust-sgpo-harness-evolution`](../../research-briefs/robust-sgpo-harness-evolution.md),
  [`evolutionary-safety-rsi-taxonomy`](../../research-briefs/evolutionary-safety-rsi-taxonomy.md).

## Sources

> Xia et al., "RRSI: Regularized Recursive Self-Improvement of Agent
> Harnesses" (arXiv:2609.24972), Sep 2026.
