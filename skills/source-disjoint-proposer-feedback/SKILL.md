---
name: source-disjoint-proposer-feedback
description: >
  Prevent co-cheating in proposer-solver self-evolution loops, where the
  question proposer and the solver come to share the same wrong answers so
  internal agreement rises while real accuracy does not. Score each
  proposal with an auxiliary solver that never trained on pseudo-labels
  from the same source documents (CrossFit), and audit false agreement
  with an outside judge.
  Derived from "False Frontiers: Diagnosing and Mitigating Co-Cheating in Self-Evolving Search Agents" (arXiv:2609.39102).
source: https://arxiv.org/abs/2609.39102
---

# Source-Disjoint Proposer Feedback (CrossFit)

Use this skill when a self-evolving loop generates its own training tasks
from a corpus (a proposer writes questions from source documents, a solver
answers them, and the solver's results reward the proposer) and there is
no ground-truth label for the generated tasks.

## When to Use

- Data-free or self-play training of search, QA or tool-use agents where
  pseudo-labels come from the model itself.
- In-loop agreement or reward keeps rising but external benchmark
  accuracy is flat or falls.
- Several rounds of curriculum are planned, so an early wrong label can
  be reinforced in later rounds.

## Core Insight

**Co-cheating**: an incorrect pseudo-label trains the solver to repeat the
error on later questions from the same source; the proposer is then
rewarded for that agreement, and the error enters the next curriculum. No
coordination is needed. The fix is about **feedback provenance**: the
model that scores a proposal must not have trained on labels derived from
that proposal's source.

**Evidence** (Qwen3.5-4B / 9B, three rounds, 1,325 open-domain QA
questions over NQ, TriviaQA, PopQA, HotpotQA, 2WikiMultiHopQA, MuSiQue,
Bamboogle):

- False-agreement mass (pairs where label and solver match on the same
  wrong answer) was 6.1% / 8.8% for the coupled Dr. Zero loop; CrossFit
  cut it to 3.0% / 3.7%; MSV alone only to 5.7% / 7.2%; both together to
  0.4% / 0.1%.
- Cover-EM: CrossFit 48.8% / 51.2% vs Dr. Zero 40.0% / 42.8%. The gap grew
  from 4.2 / 4.3 points after round 2 to 8.8 / 8.4 after round 3.
- Adding MSV to CrossFit gave 0.491 / 0.515, only 0.3 points above
  CrossFit alone.
- Random (not source-level) partitioning only reduced false agreement to
  5.0% / 6.2%: the split must be by source.
- Cost relative to Dr. Zero: MSV +90%; CrossFit with 25 updates per fold
  +72% / +79%; half auxiliary budget +36% / +40% with nearly the same
  replay false-agreement mass.

---

## Procedure

### 1. Partition sources, not questions

Split the source documents into two folds A and B. Every question inherits
the fold of the document it was generated from. If sources are
near-duplicates or linked (same entity, overlapping evidence), put them in
the same fold; the paper names connected sources as an open problem.

### 2. Train two auxiliary solvers on one fold each

Each auxiliary solver trains only on admitted questions from its fold.
Half the auxiliary update budget is a reasonable starting point (see cost
above).

### 3. Score proposals cross-fold

Questions generated from A are scored by the auxiliary solver trained on
B, and vice versa. Keep the original reward shape (proposer credit by how
hard the question is for a solver); only the scorer changes. The main
solver still trains on all admitted questions.

### 4. Optionally gate label admission with multi-sample verification

MSV: sample the labeler three times with the source and three times
without it; admit the question only if both majorities exist and agree.
It costs six extra generations per candidate and added little on its own,
so use it when label precision matters more than compute.

### 5. Audit the loop with an outside judge

On saved training examples, outside the training loop, have an
independent judge score adopted-label correctness, solver correctness,
agreement, false-agreement mass and lost-credit mass (correct answers
denied by wrong labels). Alarm when agreement rises faster than solver
correctness.

### 6. Accept checkpoints through the gate

Rising in-loop reward is not evidence of improvement. Keep or promote a
checkpoint only through "DO: Pass every self-modification through one
acceptance gate" (`rules/recursive-improvement.md`): no regression beyond
a noise margin δ estimated from repeated baseline runs on held-out
external tasks, and the negative security testbed strict.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Shared pretraining errors | Both folds' solvers share the same base-model mistakes | Outside judge audit; held-out external benchmark in the gate |
| Lower false agreement from dropping hard tasks | Admission rejects difficult questions instead of learning them | Track admitted-question difficulty and coverage per round |
| Leakage across folds | Linked or near-duplicate sources split across A and B | Cluster sources before splitting |
| Compute | MSV + CrossFit is 2.6–2.7x the base budget | Start with half-budget CrossFit, add MSV only if audits demand it |

> Source: False Frontiers: Diagnosing and Mitigating Co-Cheating in Self-Evolving Search Agents (arXiv:2609.39102)
