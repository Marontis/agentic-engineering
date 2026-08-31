---
name: capability-aware-skill-selection
description: >
  How to select which skills to load into an LLM agent's bounded context
  window. Covers the capability space model (supply/demand vectors with
  diminishing returns), the BPS algorithm with provable (1-1/e, 1) guarantee,
  parameter fitting from pass/fail outcomes, and the critical insight that
  skill selection is a set-level decision, not a ranking.
  Derived from "Optimal Skill Selection for LLM Agents" (arXiv:2608.19993).
source: https://arxiv.org/pdf/2608.19993
related_skills:
  - skill-design-methodology
---

# Capability-Aware Skill Selection

How to choose which skills to load into bounded context so the agent gets
the capabilities it needs without wasting tokens on redundancy or
irrelevant content.

## The Problem

Scoring skills independently by semantic relevance and assembling the set
by top-k or greedy packing has three failure modes:

1. **Missed complementarity**: a task needing capabilities A and B gets
   two skills both covering A — individually relevant but collectively
   useless
2. **Unpenalized redundancy**: loading a second skill covering the same
   capability costs tokens but adds near-zero marginal benefit
3. **Unmodeled degradation**: irrelevant context actively hurts — observed
   performance drops of up to 23pp from adding a semantically similar but
   task-irrelevant skill

**The evidence**: BPS (the algorithm below) reaches 0.73 task success vs
0.20–0.52 for released skill routers, text retrievers, and executor
self-selection, on 28% fewer tokens than the strongest deployed router.

---

## Core Model: Capability Space

Skills and queries live in a latent capability space with d dimensions.

### Supply and Demand

- **Skill supply vector** u_i ∈ ℝ^d₊ — how much of each capability a skill
  provides. For example, `pkzip_core` supplies "compression" but not
  "encoding"; `pk64_core` supplies "encoding" but not "compression".

- **Query demand vector** w_q ∈ ℝ^d₊ — how much of each capability the
  task needs. A "zip-then-encode" task demands both compression and encoding.

### Diminishing Returns Within, Complementarity Across

The gross benefit of injecting skill set S for query q:

```
G(q, S) = Σ_k  w_k · h(Σ_{i∈S} u_{i,k})

where h(x) = 1 − e^(−x)    (saturating, concave)
```

**Within a capability dimension** (e.g., "compression"): adding a second
skill covering the same capability hits diminishing returns — h is
concave, so the marginal benefit shrinks.

**Across capability dimensions** (e.g., "compression" + "encoding"):
uncovered dimensions are the bottleneck — h(0) = 0, so a missing
capability zeros out that dimension's contribution.

This means:
- Two skills covering different capabilities = **complementary** (high benefit)
- Two skills covering the same capability = **redundant** (low marginal benefit)
- A skill covering no demanded capability = **irrelevant** (zero benefit, nonzero cost)

### Context Penalty

Every injected token has a measurable cost:

```
cost(S) = κ · ℓ(S)
```

where ℓ(S) is total token length of the selected set and κ is the
executor's per-token context sensitivity. This penalty is not speculative —
compressing skill documents improves execution quality, and focused skills
outperform exhaustive ones.

### Selection Objective

Combine benefit and penalty under a hard token budget B:

```
max_{S: ℓ(S) ≤ B}  F(S) = G(S) − κ·ℓ(S)
```

This is regularized submodular maximization under a knapsack constraint.

---

## The BPS Algorithm

Best Prefix Selection — a polynomial-time algorithm with provable guarantees.

### Why Existing Methods Fail

- **Top-k by relevance**: scores skills independently, misses set-level
  interactions. Reaches optimum on only 7.5% of instances.
- **Density greedy**: adds the best marginal-benefit-per-token skill
  iteratively. Better, but stops too early or too late because the
  objective is non-monotone. Reaches optimum on 44% of instances.
- **BPS**: reaches the exact optimum on 100% of instances tested.

### The Algorithm

```
Input: skill library L, token budget B, fitted benefit G, penalty rate κ
Output: selected skill set S_BPS

1. Discard any skill i with ℓ_i > B
2. For each seed A ⊆ L with |A| ≤ 2 and ℓ(A) ≤ B:
   a. Initialize S ← A, record S in prefix pool P
   b. While some skill i ∉ S fits (ℓ(S) + ℓ_i ≤ B):
      - Pick i* = argmax_{i fits} [G(S ∪ {i}) − G(S)] / ℓ_i
      - S ← S ∪ {i*}
      - Record S in P
3. Return S_BPS = argmax_{S ∈ P}  [G(S) − κ·ℓ(S)]
```

### Key Design Choices

**Size-2 seed enumeration**: exhaustively trying all pairs guarantees
that the algorithm always considers the two highest-marginal-benefit
items from any optimal set. This is what enables the tight approximation.

**Record every prefix**: under non-monotone F = G − κℓ, the chain endpoint
isn't necessarily the best candidate — the optimum can sit inside the
chain where benefit minus penalty peaks. Recording every prefix and
selecting the best is what gives BPS its name and closes the gap.

**Density-greedy growth**: within each chain, items are added by
marginal benefit per token, not by marginal benefit alone. This ensures
the chain respects the token budget efficiently.

### The Guarantee

```
F(S_BPS) ≥ (1 − 1/e) · G(T) − κ·ℓ(T)    for all feasible T
```

BPS recovers at least ~63.2% of any feasible set's capability benefit
while paying its full context penalty. The coefficient 1−1/e is provably
optimal for polynomial-time algorithms — no algorithm can do better
unless P = NP.

### Complexity

O(d · L⁴) where d is capability dimensions and L is library size.
In practice L is the shortlist from a retrieval stage (tens to low
hundreds), not the full registry.

---

## Fitting the Model from Data

All latent parameters — supply vectors, demand vectors, κ — can be
learned from execution outcomes alone.

### What You Need

- A frozen executor E (the LLM that runs tasks with injected skills)
- A set of (query, skill_set, pass/fail) records from execution
- A choice of capability dimension d

### How to Fit

1. **Parameterize**: one supply vector û_i per skill (d values), one
   demand vector ŵ_q per task type (d values), one scalar κ̂

2. **Predict**: success probability = exp(F̂(q, S)) where
   F̂ = Σ_k ŵ_k · (1 − e^(−Σ_{i∈S} û_{i,k})) − κ̂·ℓ(S)

3. **Train**: minimize log loss of predicted vs measured pass/fail by
   gradient descent

4. **Validate**: check pairwise ranking accuracy on held-out set pairs

### How Many Parameters?

The structured model needs only **281 parameters** for 31 skills × 5
capabilities — and it beats neural set regressors (DeepSets, Set
Transformer) with 16,000+ parameters. The inductive bias of submodularity
is doing the heavy lifting.

### Error Transfer

If the fitted objective F̂ is uniformly within ε of the true execution
effect F*, then any near-optimal selection under F̂ is within 2ε + δ of
the true optimum, where δ is the optimization error (0 for BPS).

---

## When to Use This

### Use capability-aware selection when:

- Your skill library has **10+ skills** with overlapping capabilities
- Token budget is **binding** (you can't load everything)
- Skills have **variable length** (not all the same token cost)
- You observe that adding more skills sometimes **hurts** performance

### Use simpler methods (top-k by relevance) when:

- Library is small (< 10 skills) and everything fits in context
- Skills are non-overlapping (each covers a unique capability)
- Token budget is generous relative to library size
- You have no execution records to fit κ

### The decision flow:

```
Library size > 10?
├─ No → top-k by relevance is fine
└─ Yes → Do skills overlap in capability?
    ├─ No → top-k works, but monitor for degradation
    └─ Yes → Token budget binding?
        ├─ No → load all relevant skills
        └─ Yes → Use capability-aware selection (this skill)
```

---

## Practical Implementation Notes

### Choosing d (capability dimensions)

- If you know the capability families a priori (e.g., 5 API families),
  set d to that number
- If not, start with d = 8–16 and let the encoders learn the structure
- The model is not sensitive to overestimating d — unused dimensions
  will have near-zero supply and demand

### Cold start

Without execution records, you can bootstrap:
1. Run a sample of tasks with random skill subsets
2. Fit the model on the pass/fail outcomes
3. Use BPS from then on

The structured model learns fast — 281 parameters means you need far
fewer samples than a neural approach.

### Scaling to large libraries

BPS's O(L⁴) complexity means you need a retrieval pre-filter for
libraries with L > ~100. Use any high-recall retriever (BM25, dense
bi-encoder) to get L down to 20–50, then run BPS on the shortlist.

### Connection to skill utility

The skill-design-methodology's **skill utility score** (specificity ×
abstractness) operates at skill *design* time. This skill's capability
model operates at *selection* time. They're complementary:

- **Design time**: use skill utility to ensure each skill in the library
  is transferable (high specificity × abstractness)
- **Selection time**: use the capability model to pick the right subset
  for each specific task (maximize coverage, minimize redundancy and cost)

A library of high-utility skills with capability-aware selection is the
best of both: well-designed skills selected well.

---

## Evidence Summary

| Finding | Source | Scale |
|:--------|:------|:------|
| Skills interact as sets, not individually | Chen et al. 2026, Fig. 1 | 63,596 executions |
| BPS reaches exact optimum on 100% of instances | Chen et al. 2026, Fig. 5 | 80 instances |
| 0.73 success vs 0.20–0.52 for baselines | Chen et al. 2026, Fig. 5 | 80 instances, Qwen3-32B |
| 281-parameter model beats 16k-parameter neural | Chen et al. 2026, Fig. 4 | 2 evaluation protocols |
| Fitted supply recovers hidden coverage (AUC 0.996) | Chen et al. 2026, Fig. 2 | 155 skill-capability pairs |
| (1−1/e, 1) guarantee is provably tight | Chen et al. 2026, Theorem 1 | Theoretical |

## References

- **Paper**: [Optimal Skill Selection for LLM Agents with Provable Bicriteria Guarantees](https://arxiv.org/abs/2608.19993) — Chen, Chen, Wang, Li, Huang (Tsinghua University IIIS)
- **Related**: [Break It Down, Pass It On](https://arxiv.org/abs/2608.20274) (skill design); skill-design-methodology skill
- **Praxis source**: `src:arxiv-2608-19993`
