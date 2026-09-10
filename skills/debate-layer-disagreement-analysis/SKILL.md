---
name: debate-layer-disagreement-analysis
description: >
  Analyze and leverage disagreement in multi-agent LLM debate systems
  by decomposing disagreement into layers (factual, interpretive,
  strategic) and using layer-specific resolution strategies.
  Derived from "A Layered Analysis of Disagreement" (arXiv:2609.08016).
---

# Debate Layer Disagreement Analysis

Use this skill when running multi-agent LLM debate and you need
to understand why agents disagree and how to resolve disagreements
productively.

## When to Use

- Your multi-agent debate system produces inconsistent quality
- Agents disagree but you can't tell if the disagreement is productive
- You want to filter noise disagreements from signal disagreements
- You need to design better aggregation strategies for debate outputs

## Core Insight

Not all disagreement in multi-agent debate is equal.  Disagreements
decompose into layers — **factual**, **interpretive**, and
**strategic** — and each layer requires a different resolution
strategy.  Treating all disagreements uniformly (e.g., majority vote)
collapses productive disagreement and amplifies noise.

## Procedure

### Step 1: Classify disagreement layers

When agents disagree, classify the disagreement:

| Layer | Definition | Example | Resolution |
|:------|:-----------|:--------|:-----------|
| **Factual** | Agents disagree about facts | "The paper uses BERT" vs. "The paper uses GPT" | Verify against source — one agent is wrong |
| **Interpretive** | Agents agree on facts but disagree on meaning | Both see the same results but one calls it "significant" and the other "marginal" | Surface both interpretations with evidence |
| **Strategic** | Agents agree on facts and interpretation but disagree on what to do | Both agree the metric is low but disagree on the fix | Evaluate trade-offs explicitly |

### Step 2: Extract disagreement signals

For each debate round:

1. Align agent responses at the claim level (decompose responses
   into individual claims)
2. Identify claim pairs where agents make contradictory assertions
3. Classify each contradiction into the appropriate layer

### Step 3: Layer-specific resolution

**Factual disagreements** → Ground in evidence:
- Retrieve the source material cited by each agent
- Verify which claim is supported
- The unsupported claim is a hallucination — correct it

**Interpretive disagreements** → Preserve as perspectives:
- Both interpretations may be valid
- Present them as alternative perspectives with supporting evidence
- Let the downstream consumer (human or system) decide

**Strategic disagreements** → Evaluate trade-offs:
- Make the trade-off explicit: what does each strategy optimize for?
- Estimate costs and risks of each strategy
- Select based on the task's priority (speed vs. accuracy, etc.)

### Step 4: Quality-weighted aggregation

Weight agent contributions by their disagreement patterns:

- Agents whose factual claims are consistently verified get
  higher weight on factual matters
- Agents who surface productive interpretive disagreements get
  higher weight on nuanced questions
- Agents whose strategic recommendations correlate with task
  success get higher weight on action decisions

### Step 5: Detect unproductive debate patterns

Flag and intervene on:

- **Echo chamber**: All agents agree immediately → likely
  shared blind spot, not consensus.  Inject a devil's advocate.
- **Circular disagreement**: Same arguments repeated across
  rounds with no resolution → escalate to a different
  resolution mechanism.
- **Factual deadlock**: Agents disagree on facts but neither
  cites sources → force evidence retrieval before continuing.

## Environment Caveats

- **Two-agent debate**: Layer classification is still useful but
  you lose the statistical signal of multi-agent patterns.
- **Homogeneous agents**: If all agents use the same model,
  disagreements tend to cluster in interpretive/strategic layers.
  Use diverse models for better factual coverage.
- **Domain expertise**: Layer classification requires understanding
  what counts as "factual" in the domain.  In ambiguous domains,
  the factual/interpretive boundary is blurred.

## Failure Modes

- **Misclassified layers**: Treating an interpretive disagreement
  as factual forces a "winner" when both perspectives are valid.
- **Over-trusting consensus**: High agreement doesn't mean high
  quality — it may mean shared hallucination.
- **Ignoring strategic disagreements**: Defaulting to majority
  vote on strategic questions hides important trade-offs.

## Cross-References

- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md) —
  Failure attribution identifies the responsible agent; debate
  analysis identifies the type of disagreement between agents
- [`debate-consensus-memory-calibration`](../debate-consensus-memory-calibration/SKILL.md) —
  R²-MAD calibrates against shared misconceptions; this skill
  provides the layer decomposition for understanding why calibration
  is needed

## Sources

- A Layered Analysis of Disagreement And Answer Quality in Multi-Agent LLM Debate (arXiv:2609.08016)
