---
name: bayesian-backward-disagreement-anchor
description: >
  Resolve multi-agent disagreement without ground-truth labels
  using Bayesian backward reasoning.  Traces disagreements back
  to divergent evidence interpretations and anchors resolution
  in probabilistic consistency rather than majority vote.
  Derived from "When Agents Disagree" (arXiv:2609.11709).
---

# Bayesian Backward Disagreement Anchor

Use this skill when multiple agents disagree on a conclusion
and you have no ground-truth labels to decide who is right.

## When to Use

- Multi-agent debate produces conflicting conclusions
- No ground-truth oracle is available for the task
- Majority vote is unreliable (agents share biases)
- You need a principled way to assess which agent's reasoning
  is more likely correct

## Core Insight

When agents disagree, **backward reasoning** asks: "Given each
agent's conclusion, how well does it explain the shared evidence?"
The conclusion that better explains the evidence — measured by
Bayesian posterior probability — is more likely correct, even
without ground-truth labels.  This is the inverse of forward
reasoning (evidence → conclusion) and exploits the asymmetry
that correct conclusions are better explanations of evidence
than incorrect ones.

## Procedure

### Step 1: Collect the disagreement set

For each agent, extract:

- **Conclusion**: The agent's final answer/recommendation
- **Evidence cited**: The specific pieces of evidence the agent
  used to reach its conclusion
- **Reasoning chain**: The logical steps from evidence to conclusion

### Step 2: Identify shared vs. divergent evidence

- **Shared evidence**: Evidence cited by all disagreeing agents
  (they saw the same thing but reached different conclusions)
- **Agent-specific evidence**: Evidence only one agent cited
  (they had different information)

If agents disagree on shared evidence, it's an interpretation
dispute (see Step 3).  If they disagree because they saw different
evidence, it's an information dispute (resolve by sharing evidence).

### Step 3: Backward probability estimation

For each agent's conclusion, estimate the backward probability:

```
P(evidence | conclusion) = How well does this conclusion
                           explain the observed evidence?
```

Score each conclusion on:

1. **Completeness**: Does the conclusion account for ALL shared
   evidence, or does it ignore inconvenient data points?
2. **Parsimony**: Does the conclusion require fewer auxiliary
   assumptions to explain the evidence?
3. **Consistency**: Is the conclusion internally consistent
   with all cited evidence, or are there contradictions?

### Step 4: Compute posterior ranking

Rank conclusions by their posterior probability:

```
P(conclusion | evidence) ∝ P(evidence | conclusion) × P(conclusion)
```

Where P(conclusion) is the prior — how plausible is this
conclusion independent of the evidence?  Use base rates from
similar tasks if available; otherwise use uniform priors.

### Step 5: Anchor resolution

The conclusion with the highest posterior becomes the **anchor**:

- If the anchor's posterior is much higher than alternatives
  (>2× ratio), adopt it with high confidence
- If posteriors are close (within 1.5×), flag as genuinely
  ambiguous and present both conclusions with confidence levels
- If the anchor contradicts majority opinion, flag for human
  review — the majority may share a bias the backward analysis
  exposed

## Environment Caveats

- **Symmetric evidence**: When evidence equally supports multiple
  conclusions, backward reasoning can't distinguish them.
  This correctly identifies genuine ambiguity.
- **Complex reasoning chains**: For multi-step reasoning, backward
  analysis should be applied at each reasoning step, not just
  the final conclusion.
- **Evidence quality**: Backward reasoning assumes evidence is
  reliable.  If evidence itself is unreliable, garbage-in
  garbage-out applies.

## Failure Modes

- **Prior dominance**: If the prior P(conclusion) is too strong,
  it overwhelms the evidence.  Use weak/uniform priors for
  novel tasks.
- **Evidence cherry-picking**: An agent may cite only evidence
  that supports its conclusion.  The completeness check in
  Step 3 catches this.
- **Computational cost**: Full Bayesian computation is expensive
  for complex evidence sets.  Use approximations (e.g., score
  each factor on a 1–5 scale rather than computing exact
  probabilities).

## Cross-References

- [`debate-layer-disagreement-analysis`](../debate-layer-disagreement-analysis/SKILL.md) —
  Layer analysis classifies disagreement types; Bayesian backward
  reasoning resolves them
- [`debate-consensus-memory-calibration`](../debate-consensus-memory-calibration/SKILL.md) —
  R²-MAD calibrates against shared misconceptions; backward
  reasoning provides a complementary label-free resolution

## Sources

- When Agents Disagree: Bayesian Backward Reasoning as a Label-Free Anchor (arXiv:2609.11709)
