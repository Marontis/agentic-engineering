---
name: hypergraph-augmented-mcts
description: >
  Make tree search over agent action trajectories reuse evidence across
  branches: record the outcome of each group of committed decisions
  (e.g. a flight-hotel pair, a set of cart items) independent of the
  order or prefix it was reached by, and add the pooled group value as
  a prior to UCT selection. Use for long-horizon planning with global
  constraints (budget, schedule) in a replayable environment.
  Derived from "HyperMCTS: Hypergraph-Augmented MCTS for Long-Horizon LLM Agents" (arXiv:2609.33920).
source: https://arxiv.org/abs/2609.33920
---

# Cross-Trajectory Decision-Group Priors for Agent MCTS

Use this skill when an LLM agent already runs (or could run) Monte
Carlo Tree Search over tool-use trajectories, each rollout is expensive,
and the same decisions keep reappearing on different branches in
different orders.

## When to Use

- Planning tasks where several commit decisions jointly decide success
  (shared budget, no double booking, all requirements covered), so
  most-correct plans still fail on one global constraint
- Search budgets of a handful of rollouts per task, where plain UCT
  cannot learn much per prefix
- Environments that can be replayed, snapshotted or simulated, so
  alternative histories can be explored without real side effects

Do not use it when actions are irreversible and there is no simulator,
or when outcomes depend strongly on order or on context your decision
identities leave out (see Failure Modes).

## Core Insight

Standard MCTS keeps statistics per history-action pair. Two branches
that pick the same flight and hotel in a different order update
separate nodes, so evidence about that pair is learned twice. HyperMCTS
keeps the ordered tree for execution history and adds a hypergraph
whose hyperedges are unordered sets of canonical decisions, each with a
visit count and mean return. At selection time, the values of the
hyperedges containing a candidate decision are aggregated into a prior
and added to the UCT score.

**Evidence** (DeepPlanning Travel and Shopping; SealQA; Qwen3.5-27B,
Qwen3.6-27B and Sonnet 4.6 in thinking mode; B=5 iterations, branching
b=3):
- Average case accuracy rose over the strongest baseline per model by
  7.3, 2.7 and 2.3 points (Qwen3.6-27B, Qwen3.5-27B, Sonnet 4.6).
  Baselines included ReAct, CoT, Reflexion, ToT, RAP, LATS and FLARE.
- Against the same MCTS without the hypergraph: 47.3% vs 38.2%
  (Qwen3.6-27B), 36.9% vs 30.9% (Qwen3.5-27B), 41.5% vs 35.7%
  (Sonnet 4.6). The ablation removes the whole hypergraph component,
  not only the prior term.
- Shopping cost study (120 cases, Qwen3.6-27B, b=3): 60.8% accuracy
  with about 122 LLM calls and 85K output tokens per case, versus RAP
  at 57.5% with 144 calls and 141K tokens. LATS and FLARE used 3.8x
  and 3.3x the output tokens. Raising b from 3 to 6 gained only 0.1-1.0
  points across methods.
- SealQA: +2.7 and +3.6 points over the strongest baseline on
  Qwen3.6-27B and Sonnet 4.6; a tie with ToT on Qwen3.5-27B.

---

## Procedure

### 1. Make alternatives safe to explore

- Run search against a replayable environment: restorable snapshots,
  prefix replay, or a simulator. Commit actions in search must only
  build a candidate solution (add to cart, draft an itinerary), never
  execute a real transaction.
- For anything that leaves the sandbox, apply "DO: Snapshot before
  uncertain commands" and "DON'T: Assume external API calls can be
  rolled back" (rules/agent-sandbox-safety.md). The paper assumes reversibility and
  lists irreversible tasks as out of scope.

### 2. Define canonical decision identities

- Decide which actions are **commit decisions** (selecting an item,
  hotel, document, plan component). Information-gathering steps stay in
  the history but do not become hypergraph nodes.
- Write a map from an action to a canonical identity that removes tree
  position but keeps what matters to the outcome: product ID; stage
  plus choice for staged plans (outbound transport, accommodation, day
  plan); action type plus arguments for search or lookup actions.
- Write down which context the identity drops. The paper notes an
  argument-only lookup identity can merge decisions made under
  different retrieval contexts.

### 3. Run MCTS with a hypergraph update after each rollout

Per iteration: select, expand (up to b distinct valid actions sampled
from the frozen policy), simulate to a terminal state, evaluate with a
terminal verifier, back up along the tree path, then:

- Collect the canonical identities of the recorded commit decisions.
- If there are at least two, add or update a **trajectory-level
  hyperedge** keyed by that unordered set: increment its count and
  update its mean with the rollout reward.
- If the verifier scores individual objectives (one requirement, one
  constraint), also update **objective-level hyperedges**, keyed by the
  decisions tied to that objective plus an objective label.
- Use exact set keys first. The paper's implementation notes also
  describe Jaccard merging of near-duplicate sets (threshold 0.8);
  merged records no longer equal the return of any single rollout.

### 4. Select with HyperUCT

For each expanded child action a at history h:

```
score(a) = Q_tree(h,a) + c * sqrt(log N(h) / N(h,a)) + lambda * Q_hyper(id(a))
```

- `Q_hyper` aggregates the hyperedges that contain the decision. Paper
  setting: 0.7 x (max objective-level value) + 0.3 x (mean
  trajectory-level value) when both exist, otherwise whichever exists,
  0 if none.
- Unvisited children score infinity, as in UCT. lambda = 0 recovers
  plain UCT.
- Paper settings: c = 1.414; lambda 0.3 to 0.7 on Travel, 0.5 on
  Shopping, 0.2 to 0.5 on SealQA. Stronger backbones peaked at higher
  lambda. These were picked from a sensitivity sweep on the evaluation
  tasks, so tune lambda on a held-out split of your own tasks.

### 5. Return the best evaluated trajectory

Return the highest-reward trajectory among those actually evaluated,
using stored rewards. The prior only steers search; it never changes
the verifier reward or the final choice.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Incompatible feedback pooled | Outcome depends on order or on context the identity drops | Add the missing context (stage, time slot, retrieval context) to the identity, or lower lambda |
| No gain over plain MCTS | Little overlap of decision groups across branches | Check the hyperedge reuse rate in logs; if groups rarely repeat, drop the hypergraph |
| Prior misleads early search | Weak backbone gives noisy rollouts | Use a moderate lambda (0.3 was best for the weaker model on Travel) |
| Real side effects during search | Commit action wired to a live API | Only candidate-building actions in search; execute the chosen plan once, after search, behind the usual action gates |
| Overfit lambda | lambda tuned on the evaluation set | Tune on held-out tasks; report the setting with results |
| Partial scores look good, plan still fails | Verifier rewards partial credit | Include the global-constraint pass/fail in the terminal reward; case accuracy, not composite score, is what failed in the paper's example (93.8% composite, failed plan) |

> Source: HyperMCTS: Hypergraph-Augmented MCTS for Long-Horizon LLM Agents (arXiv:2609.33920)
