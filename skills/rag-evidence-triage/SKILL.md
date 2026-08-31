---
name: rag-evidence-triage
description: >
  Classify retrieved evidence as sufficient, insufficient, or conflicting
  using internal model representations.  Lightweight linear probe on
  hidden activations from a single layer outperforms prompting baselines.
  Derived from "Knowing Before Answering" (arXiv:2608.27661).
---

# RAG Evidence Triage

Use this skill when building retrieval-augmented generation systems that
need to determine whether retrieved documents provide sufficient,
insufficient, or conflicting evidence before generating an answer.

## When to Use

- Your RAG system sometimes answers from insufficient evidence
- You need to distinguish "I don't have enough info" from "my sources
  disagree" — these require different downstream responses
- You want to reduce hallucination without adding inference-time cost
- You're building a retrieval router or quality gate

## Core Insight

Language models internally encode whether retrieved evidence is
sufficient, insufficient, or conflicting.  This signal is linearly
decodable from a single hidden layer — no additional LLM inference
needed.  Collapsing to binary (answer vs. refuse) discards the
crucial distinction between "missing information" and "contradictory
information."

**Evidence**: Across 16 models (90M to 32B parameters), a logistic
regression probe on hidden activations achieves up to 0.91 accuracy
and reduces false answer rates by up to 75% compared to prompt-based
baselines — with zero additional tokens or inference cost.

## Procedure

### Step 1: Define the three evidence states

| State | Meaning | Downstream Action |
|:------|:--------|:-----------------|
| **Answer** | Evidence is sufficient and consistent | Generate answer with citations |
| **Refuse** | Evidence is insufficient to answer | Acknowledge gap, suggest follow-up retrieval |
| **Conflict** | Evidence contains contradictory claims | Surface the contradiction explicitly |

**Critical**: Do not collapse Refuse and Conflict into a single
"don't answer" class.  A model that confidently answers from
contradictory documents fails differently from one answering without
evidence.  The distinction matters for trust and downstream handling.

### Step 2: Create controlled training data

Build a diagnostic dataset that isolates evidence-state decisions:

1. **Answer instances**: Question + retrieved context that contains
   the correct answer with consistent supporting evidence
2. **Refuse instances**: Question + retrieved context that lacks the
   information needed (e.g., unrelated documents, partial coverage)
3. **Conflict instances**: Question + retrieved context containing
   mutually contradictory answers from different sources

**Key**: Use fictitious or synthetic information to prevent the model
from relying on parametric knowledge.  The probe should detect
evidence state from the retrieval context, not from memorized facts.

### Step 3: Extract hidden activations

For each training instance, run a forward pass through the language
model and extract hidden states from the target layer:

```python
# Run forward pass
outputs = model(input_ids, output_hidden_states=True)
# Extract hidden state from target layer
# Best layer is typically in the middle (layer L//2 ± 2)
hidden_state = outputs.hidden_states[target_layer]
# Use the last token position as the feature vector
feature = hidden_state[:, -1, :]  # shape: (batch, hidden_dim)
```

**Layer selection**: The most informative signals consistently emerge
in the **middle layers** of the network.  Start with layer L//2 and
probe adjacent layers to find the optimum.  This pattern holds across
model families and sizes.

### Step 4: Train the triage probe

Train a lightweight logistic regression (or linear SVM) on the
extracted features for 3-class classification:

```python
from sklearn.linear_model import LogisticRegression

probe = LogisticRegression(max_iter=1000, multi_class='multinomial')
probe.fit(train_features, train_labels)  # labels: answer/refuse/conflict
```

**Why linear**: A linear probe ensures you're decoding information
that's already represented in the model, not learning a new complex
mapping.  If a linear probe works, the model "knows" the answer.

### Step 5: Deploy as a pre-generation router

At inference time, before generating the answer:

1. Run the forward pass (you're doing this anyway for generation)
2. Extract the hidden state from the probe layer
3. Classify: answer / refuse / conflict
4. Route to the appropriate response strategy

```python
hidden = forward_pass(query + context)
evidence_state = probe.predict(hidden[target_layer][-1])

if evidence_state == "answer":
    generate_answer(query, context)
elif evidence_state == "refuse":
    acknowledge_insufficient_evidence(query)
elif evidence_state == "conflict":
    surface_contradiction(query, context)
```

**Zero additional cost**: The hidden states are already computed
during the forward pass.  The probe is a single matrix multiply.

### Step 6: Validate with selective abstention

Calibrate the probe's confidence threshold using held-out data:

- High-confidence predictions → trust the triage decision
- Low-confidence predictions → fall back to a safer default
  (e.g., refuse or request additional retrieval)

## Environment Caveats

- **API-only models**: You need access to hidden states, which
  API providers typically don't expose.  Alternatives:
  - Self-host an open-weight model for the triage step
  - Use prompt-based triage as a weaker fallback
  - Some APIs expose logprobs, which can serve as a partial signal
- **Different model families**: The optimal probe layer varies.
  Retrain the probe when switching models.
- **Domain shift**: The probe generalizes across question types
  but may need recalibration for radically different domains.

## Failure Modes

- **Parametric knowledge leakage**: If training data uses real facts,
  the model may answer from memory instead of from context.  Use
  synthetic/fictitious content for training.
- **Binary collapse**: Collapsing refuse + conflict into one class
  loses the information needed to handle each case appropriately.
- **Wrong layer**: Using the first or last layers instead of middle
  layers degrades probe accuracy significantly.
- **Overfitting to training distribution**: The probe may not
  generalize to evidence patterns not seen during training.

## Cross-References

- [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) —
  Evidence triage feeds into knowledge layer decisions about what to persist
- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md) —
  When the RAG system answers incorrectly despite having conflicting evidence,
  attribution identifies the triage step as the failure point

## Sources

- Knowing Before Answering: arXiv:2608.27661
