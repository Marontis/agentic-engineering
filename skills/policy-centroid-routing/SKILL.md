---
name: policy-centroid-routing
description: >
  How to select which policy rules to activate before an agent acts,
  using centroid-based routing over embedded policy regimes.  Reduces
  rule-bloat overhead while maintaining safety coverage.
  Derived from "Which Rules Matter Now?" (arXiv:2608.30757).
---

# Policy-Centroid Routing

Use this skill when your agent has a large rule set and you need to
select which rules are relevant to a given action before evaluation,
rather than loading all rules into context.

## When to Use

- Your agent operates under many policy rules but only a few apply
  to any given action
- Loading all rules into context is too expensive or causes
  attention dilution
- You need to route actions to the correct policy regime(s) before
  enforcement begins
- You're building a rule selection layer for a governed agent system

## Core Insight

Before an agent can decide whether an action is allowed, it must
first determine **which rules the action implicates**.  A single
action can fall under multiple policy regimes simultaneously, and
their requirements can stack, overlap, or qualify one another.
Loading all rules into context wastes attention and invites
misapplication.

The solution is **geometric routing**: embed both actions and policy
regimes into the same vector space, compute proximity, and select
the k-nearest policy centroids.  This is a retrieval problem, not
a reasoning problem — and it should happen before reasoning begins.

## Procedure

### Step 1: Represent each policy regime as a centroid

For each distinct policy regime (safety rules, data rules, access
control, etc.):

1. Collect the text of all rules in that regime
2. Embed each rule using a sentence embedding model
3. Compute the centroid (mean vector) of all rule embeddings in
   that regime
4. Store the centroid with its regime metadata

```python
# Example: compute policy centroids
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

regimes = {
    "sandbox-safety": ["Classify every command...", "Snapshot before uncertain...", ...],
    "data-access": ["Route through capability gateway...", "Don't self-declare identity...", ...],
    "skill-quality": ["Decompose to subtask level...", "Write as text not code...", ...],
}

centroids = {}
for regime_name, rules in regimes.items():
    embeddings = model.encode(rules, normalize_embeddings=True)
    centroids[regime_name] = embeddings.mean(axis=0)
    centroids[regime_name] /= np.linalg.norm(centroids[regime_name])
```

### Step 2: Embed the proposed action

When the agent proposes an action, embed the action description
(including tool name, parameters, and any stated intent) using the
same embedding model.

### Step 3: Route to nearest policy centroids

Compute cosine similarity between the action embedding and each
policy centroid.  Select regimes above a similarity threshold or
the top-k nearest regimes.

```python
action_emb = model.encode(action_description, normalize_embeddings=True)

scores = {name: float(action_emb @ centroid)
          for name, centroid in centroids.items()}

# Select regimes above threshold or top-k
relevant = [name for name, score in scores.items() if score > threshold]
```

### Step 4: Load only relevant rules

Inject only the rules from selected regimes into the agent's
context for evaluation.  This reduces context size and focuses
attention on applicable rules.

### Step 5: Handle multi-regime overlap

When an action implicates multiple regimes:

- Load all implicated regimes (not just the nearest one)
- If regimes conflict, apply the more restrictive rule
- Document which regimes were consulted in the audit log

## Environment Caveats

- **Small rule sets** (<20 rules): Centroid routing may be
  overkill.  Load all rules if they fit comfortably in context.
- **Highly overlapping regimes**: If most rules apply to most
  actions, routing doesn't save much.  Reorganize regimes to
  be more orthogonal.
- **Dynamic rules**: If rules change frequently, recompute
  centroids after each update.  This is cheap (just re-embedding
  and averaging).
- **Action description quality**: Routing accuracy depends on
  how well the action is described.  Vague action descriptions
  produce poor routing.  Include tool name, parameters, and intent.

## Failure Modes

- **Under-routing**: If the similarity threshold is too high,
  relevant rules may be missed.  Err on the side of including
  too many regimes rather than too few — safety requires
  over-inclusion.
- **Centroid collapse**: If a regime contains very diverse rules,
  the centroid may not represent any individual rule well.
  Split heterogeneous regimes into sub-regimes.
- **Adversarial action descriptions**: An agent might describe
  its action in terms that avoid triggering relevant policy
  regimes.  The action description used for routing should come
  from the tool call itself, not the agent's stated intent.

## Cross-References

- [`capability-aware-skill-selection`](../capability-aware-skill-selection/SKILL.md) —
  Same geometric routing principle applied to skill selection
  instead of rule selection
- [`unified-capability-gateway`](../unified-capability-gateway/SKILL.md) —
  Policy enforcement happens after routing; the gateway is where
  enforcement occurs

## Sources

- Which Rules Matter Now? Policy-Centroid Routing Before an Intelligent System Acts (arXiv:2608.30757)
