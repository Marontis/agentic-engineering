---
name: hallucination-mean-shift-probe
description: >
  How to detect LLM hallucinations using simple linear probes that
  exploit the mean-shift signal in hidden states.  Covers layer
  selection, probe training, multi-layer aggregation (LayerMix),
  and deployment as a zero-cost quality gate.
  Derived from "The Hallucination Signal Is a Mean Shift" (arXiv:2608.28930).
---

# Hallucination Mean-Shift Probe

Use this skill when you need to detect whether an LLM is
hallucinating, and you have access to hidden-state activations
(self-hosted models or models exposing internal representations).

## When to Use

- You're running a self-hosted model and need a hallucination detector
- You want zero-additional-inference-cost hallucination detection
- You need to decide whether to trust a model's output before serving it
- You're building a quality gate for agentic outputs

## Core Insight

Hallucination in LLMs manifests as a **mean shift** in hidden-state
representations.  When a model generates a hallucinated statement,
the hidden-state vector shifts its mean relative to factual statements.
This shift is:

1. **Linearly detectable** — a simple logistic regression probe suffices
2. **Distributed across layers** — no single layer is always best;
   the optimal layer varies by model, but middle layers are usually
   strongest
3. **Distributed across neurons** — the signal isn't concentrated in
   a few dimensions

**Evidence**: LayerMix, a multi-layer aggregation method, matches or
exceeds complex detection methods while remaining a single-pass linear
operation on activations that are already computed during generation.

## Procedure

### Step 1: Collect labeled hidden states

Create a dataset of (prompt, response, label) triples where label
is hallucinated vs. factual:

1. **Factual examples**: Prompts with verifiable answers where the
   model answers correctly
2. **Hallucinated examples**: Prompts where the model generates
   statements not supported by its input context

For each example, run a forward pass and extract hidden states from
all layers.

### Step 2: Identify informative layers

Score each layer by how well a simple probe (logistic regression)
separates hallucinated from factual states:

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

layer_scores = {}
for layer_idx in range(num_layers):
    features = hidden_states[:, layer_idx, -1, :]  # last token
    probe = LogisticRegression(max_iter=1000)
    score = cross_val_score(probe, features, labels, cv=5).mean()
    layer_scores[layer_idx] = score
```

**Key finding**: Middle layers (around L//2) are usually best, but
adjacent layers also carry signal.  Don't commit to a single layer.

### Step 3: Train LayerMix aggregation

Instead of picking one layer, aggregate across multiple informative
layers:

1. **Score layers**: Rank layers by probe accuracy (Step 2)
2. **Select top-k**: Choose the top-k layers (k=3–5 typically works)
3. **Aggregate**: Concatenate features from selected layers, then
   train a single logistic regression on the concatenated features

```python
import numpy as np

# Select top-k layers
top_k = sorted(layer_scores, key=layer_scores.get, reverse=True)[:5]

# Concatenate features
multi_layer_features = np.concatenate(
    [hidden_states[:, l, -1, :] for l in top_k], axis=1
)

# Train aggregated probe
probe = LogisticRegression(max_iter=1000)
probe.fit(multi_layer_features, labels)
```

### Step 4: Deploy as a generation-time gate

At inference time:

1. Run the forward pass (already happening for generation)
2. Extract hidden states from the selected layers
3. Concatenate and classify with the probe
4. If hallucination is detected:
   - Block the response and regenerate
   - Or flag for human review
   - Or fall back to a more conservative generation strategy

**Cost**: One matrix multiply on already-computed activations.
Effectively zero additional inference cost.

### Step 5: Calibrate confidence thresholds

The probe outputs a probability.  Calibrate the threshold on
held-out data:

- **High threshold** (e.g., 0.9): Only flag obvious hallucinations;
  low false positive rate but misses subtle ones
- **Low threshold** (e.g., 0.5): Catch more hallucinations but
  flag some factual responses incorrectly
- Choose based on your cost of false positives vs. false negatives

## Environment Caveats

- **API-only models**: You need hidden-state access.  If using an
  API, check if logprobs are available — they provide a weaker but
  still useful signal.  Otherwise, self-host an open-weight model
  for the quality gate.
- **Different model families**: The optimal layers and probe
  weights are model-specific.  Retrain when switching models.
- **Fine-tuned models**: If you fine-tune the base model, the
  hidden-state geometry may shift.  Re-validate and possibly
  retrain the probe.
- **Long-context inputs**: The signal may be weaker for very long
  contexts where the relevant evidence is far from the generation
  point.

## Failure Modes

- **Single-layer commitment**: Using only one layer misses signal
  that distributes across layers.  Always use multi-layer aggregation.
- **Training distribution mismatch**: A probe trained on Wikipedia
  factual claims may not transfer to domain-specific hallucinations.
  Include domain-relevant examples in training data.
- **Confusing uncertainty with hallucination**: A model that says
  "I think..." may trigger the probe even when the hedged statement
  is appropriate.  Train on hedged-but-correct examples too.

## Cross-References

- [`rag-evidence-triage`](../rag-evidence-triage/SKILL.md) —
  Evidence triage detects insufficient/conflicting evidence *before*
  generation; this probe detects hallucination *during* generation.
  They're complementary.

## Sources

- The Hallucination Signal Is a Mean Shift: Why Simple Probes Suffice (arXiv:2608.28930)
