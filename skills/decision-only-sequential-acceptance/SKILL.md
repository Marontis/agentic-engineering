---
name: decision-only-sequential-acceptance
description: >
  Decide which self-modifications to promote when the same frozen
  evaluation set is reused for every round of a self-improvement loop.
  Return only accept/reject decisions to the proposer, test each
  candidate against the incumbent with a one-sided paired sign test,
  spend a global error budget across rounds, prior promotions and
  candidates, and keep a running certificate of cumulative gain.
  Use it as the statistical core of the acceptance gate when the loop
  runs many rounds against one benchmark.
  Derived from "Which Self-Improvements Should We Trust? Reliable
  Self-Improvement When Agents Reuse Their Benchmarks" (arXiv:2609.33180).
source: https://arxiv.org/abs/2609.33180
---

# Decision-Only Sequential Acceptance (Reuse)

Use this skill when a propose → evaluate → promote loop reuses one fixed
evaluation set across many rounds, and you need the promoted changes to
be real improvements rather than lucky draws or benchmark overfitting.

## When to Use

- Many rounds (tens to hundreds) and several candidates per round are
  scored on the same acceptance set.
- The proposer sees earlier evaluation results and conditions its next
  candidates on them, so the acceptance set is quietly becoming a
  training set.
- You want a stated error level α for "this promotion was a real
  improvement" instead of a hand-set margin.
- Outcomes are per-task pass/fail (or per-task results that can be
  paired between candidate and incumbent).

This skill implements the acceptance decision only. It does not replace
"DO: Pass every self-modification through one acceptance gate"
(`rules/recursive-improvement.md`): the gate still requires behavioural
evidence, held-out tasks, a negative security testbed that is always
strict (zero tolerance, no margin), and no regression beyond the noise
margin δ (estimated from repeated runs of the unchanged baseline) on
previously-correct cases. Use this procedure to decide whether a gain is
real, and the gate for everything else.

## Core Insight

A reused benchmark fails in three ways: within-round selection bias
(the best of K looks better than it is), false discoveries from testing
over many rounds, and adaptive overfitting, when later candidates are
built from earlier scores on the same set. Multiple-testing corrections
such as Bonferroni handle the first two. Only cutting what flows back to
the proposer handles the third: if the proposer sees only promote/reject
decisions, its candidates depend on the benchmark only through the
promotion history, and the error budget can be split over every history
that could have happened.

**Evidence** (binary classification on Covertype; Qwen2.5-7B-Instruct
proposes scikit-learn pipeline edits; T = 200 rounds, K = 8 candidates per
round, 30 seeds; false promotions are summed over the 30 runs and judged
on a held-out set that no method sees):

| Method (n = 2,000 eval set) | Pop. improvement (pp) | Promotions/run | False promotions |
|---|---|---|---|
| Empirical best-of-K | 7.04 ± 0.08 | 13.0 | 75 |
| Elite | 6.72 ± 0.14 | 14.3 | 89 |
| DGM-style | 3.89 ± 0.17 | 6.4 | 34 |
| PACE-style | 6.45 ± 0.19 | 6.4 | 4 |
| Bonferroni-style | 2.35 ± 0.37 | 1.3 | 0 |
| **Reuse** | **7.02 ± 0.26** | 3.2 | **0** |

At n = 10,000, Reuse reached 7.19 ± 0.13 pp with 0 false promotions,
against 7.19 ± 0.06 pp and 71 false promotions for empirical best-of-K and
6.90 ± 0.12 pp for Bonferroni-style. The paper describes best-of-K's 75
false promotions at n = 2,000 as "nearly 20 percent" of its accepted
updates. Reuse matched the greedy baseline's real gain with a quarter of
the promotions and none of the false ones, while Bonferroni lost most of
the gain on the small set.

---

## Procedure

### 0. Set Up

- Freeze the acceptance set S (n tasks). Keep a separate held-out set
  that the loop never touches, for reporting.
- Choose the global error level α (the probability that any promotion
  in the whole run is not a real improvement), the per-round candidate
  count K, and a split ρ of each round's budget between the test and
  the certificate (step 4).
- Keep any search oracle (training split, rubric scores, traces) that
  the proposer may learn from **separate** from S (see "DO: Separate
  exploration from evaluation", `rules/recursive-improvement.md`).

### 1. Feed Back Decisions Only

After each round, tell the proposer only whether a candidate was
promoted (and which), never the scores, task-level outcomes or
certificate from S. Rich trace feedback is fine on the search split; it
must not come from S.

### 2. Allocate the Error Budget

At round t, with p promotions so far:

```
δ_{t,p} = α · w_t · v_p / [ C(t-1, p) · K^(p+1) ]
w_t = 1 / [t (t+1)]        v_p = 1 / [(p+1)(p+2)]
```

The binomial term and the K^(p+1) term account for every promotion
history the proposer could have seen. The budget shrinks as rounds and
promotions accumulate, so later promotions need stronger evidence.
(This δ_{t,p} is a per-test error level, not the noise margin δ of the
acceptance gate.)

### 3. Paired Sign Test Against the Incumbent

For each candidate k, on the same tasks of S:

- n₊ = tasks the candidate solves and the incumbent fails
- n₋ = tasks the incumbent solves and the candidate fails
- M = n₊ + n₋ (agreements are dropped)
- p-value π = P(Bin(M, 1/2) ≥ n₊), with π = 1 when M = 0 (one-sided,
  H₀: no improvement)

The candidate passes if π ≤ ρ · δ_{t,p}. If several pass, promote the
one with the largest mean paired improvement. If none pass, keep the
incumbent.

### 4. Keep a Running Certificate (Audit Only)

For a promoted candidate, compute a lower confidence bound ℓ on its
improvement at level (1 − ρ) · δ_{t,p} (the paper combines an exact
sign-test bound with a Bernstein bound) and add max(ℓ, 0) to the running
certificate C_t. C_t is a lower bound on cumulative gain over the start
system. Log it; do not show it to the proposer.

### 5. Hand Off to the Acceptance Gate

A promotion here means "the gain is real on this distribution at level
α". Before keeping or deploying the change, run the rest of the gate:
behavioural evidence, held-out tasks, previously-correct cases within the
noise margin δ, and the negative security testbed with zero tolerance.

---

## Environment Caveats

- **Not tested on agents.** The only experiment is a tabular
  classification pipeline edited by a 7B LLM. The authors name coding and
  model post-training loops as next steps. The guarantee is statistical
  and holds whenever its assumptions do; the effect sizes are unverified
  for agent loops.
- **Slow and conservative.** Decision-only feedback and a shrinking
  budget raise the minimum detectable improvement, which the paper says
  scales as √(L_{t,p}/n). With a small S, real but small gains will be
  rejected; report the missed-improvement rate too (see "DO: Measure
  acceptance-gate errors in both directions").
- **Single metric.** The method controls one primary metric. The paper
  lists controlling safety and cost as future work, so keep those as
  separate non-compensatory guards.
- **α in the experiments** could not be confirmed from the paper text
  when this skill was written; check the paper before quoting a value.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Adaptive overfitting to S | Proposer sees scores on S | Decision-only feedback (step 1) |
| Lucky best-of-K | Taking the max of K noisy scores | K^(p+1) term in δ_{t,p}; paired test per candidate (steps 2–3) |
| False discoveries over many rounds | Testing every round at a fixed level | Round weights w_t and promotion weights v_p (step 2) |
| Real gains rejected | Small S, tiny effects | Larger S; report missed improvements; don't loosen α silently |
| Leak through the certificate | C_t shown to the proposer | Keep C_t in the audit log only (step 4) |

## Cross-References

- `rules/recursive-improvement.md`: "DO: Pass every self-modification
  through one acceptance gate", "DO: Separate exploration from
  evaluation", "DO: Measure acceptance-gate errors in both directions".
- [`regularized-harness-evolution`](../regularized-harness-evolution/SKILL.md):
  its step 2 gives the proposer an evidence log with score changes. That
  is safe on the evolve set only if the final acceptance decision uses a
  set whose scores never reach the proposer, as here.
- Briefs: [`reliable-self-evolution-two-gate`](../../research-briefs/reliable-self-evolution-two-gate.md),
  [`process-level-self-evolution-evaluation`](../../research-briefs/process-level-self-evolution-evaluation.md).

> Source: Sun, Zeng, She & Wang, "Which Self-Improvements Should We
> Trust? Reliable Self-Improvement When Agents Reuse Their Benchmarks"
> (arXiv:2609.33180), Sep 2026.
