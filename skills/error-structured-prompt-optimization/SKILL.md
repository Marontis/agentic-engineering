---
name: error-structured-prompt-optimization
description: >
  Structured prompt optimization via Diagnose-Propose-Select to eliminate
  prompt bloat and validation overfitting. Clusters all errors into structural
  patterns, explores four diverse mutation operators, and selects via bootstrap
  stability. Derived from ESPO (arXiv:2609.04197).
source: https://arxiv.org/abs/2609.04197
---

# Error-Structured Prompt Optimization

Use this skill when optimizing agent system prompts, task instructions, or tool
descriptions using automated reflection loops, especially when facing prompt bloat
or validation overfitting.

## When to Use

- Automated prompt engineering pipelines (GEPA, DSPy MIPROv2, OPRO, APE) where prompts
  grow progressively longer across iterations without accuracy gains ("prompt bloat")
- System prompts accumulating dozens of ad-hoc "DO NOT" and "ALWAYS" rules that increase
  inference latency and degrade reasoning focus
- Small validation sets (30–100 examples) where evolutionary search selects overfitted
  candidates due to validation noise
- Cross-model prompt transfer where bloated prompts fail to generalize to smaller models

## Core Insight

Evolutionary prompt optimizers typically sample 3–8 random error traces per iteration,
causing three failure modes:
1. **Incomplete error observation**: By the coupon-collector theorem, observing all
   systematic failure patterns from random batches requires ~15 rounds; during this
   time, the optimizer accumulates contradictory rules targeting symptoms rather than
   root causes.
2. **Search bias lock-in**: Using a single mutation operator repeatedly appends caveats,
   bloating prompt length up to $3\times$.
3. **Selection instability**: Point estimation on small validation sets causes multiple-testing
   failures, picking verbose candidates that ranked first purely by noise.

Recasting prompt optimization as **Diagnose, Propose, and Stabilize (Select)**:
- **Diagnose**: Cluster *all* validation errors into 3–7 structural patterns simultaneously.
- **Propose**: Generate candidates via 4 complementary strategies (diagnostic revision,
  consolidation, ablation, factual injection).
- **Select**: Use bootstrap stability selection ($B=20$ resamples) to select the most
  statistically robust candidate.

Across 7 benchmarks, this approach achieved **+3.76 pp higher accuracy** than GEPA
(74.67% vs 70.91%) while producing prompts that were **47% shorter** (1,004 vs 1,878 chars)
and running significantly faster at inference (Liu et al., 2026).

---

## Procedure

### 1. Diagnose Phase: Global Error Clustering

Do not reflect on random individual errors. Evaluate the current candidate prompt on the
entire training/validation split and extract all failure instances:

1. **Extract error signatures**: For every incorrect example, log $(x, y_{\text{gold}}, \hat{y}, \text{trace})$.
2. **Cluster into structural patterns**: Embed error descriptions or use a strong LLM
   to group all failures into $K \in [3, 7]$ distinct thematic buckets (e.g.,
   *formatting violation*, *premature termination*, *misinterpreted operator*, *hallucinated entity*).
3. **Rank by prevalence**: Sort clusters by frequency to identify the top systematic failure
   mechanisms.

### 2. Propose Phase: Four Complementary Mutation Operators

Rather than asking the LLM for generic prompt improvements, generate exactly one candidate
under each of the four distinct inductive strategies:

- **Strategy 1: Diagnostic Revision (Targeted Fix)**
  - Prompt: Address the primary error cluster by introducing clear, actionable guidelines
    specifically correcting that systematic mechanism.
- **Strategy 2: Consolidation (Anti-Bloat)**
  - Prompt: Review the existing prompt and merge fragmented, overlapping rules into unified,
    compact principles. Remove redundant phrasing without dropping behavioral constraints.
- **Strategy 3: Ablation (Pruning)**
  - Prompt: Identify and remove 20–30% of the least impactful or overly specific instructions
    to test whether simpler framing improves model reasoning.
- **Strategy 4: Factual / Schema Injection (Grounding)**
  - Prompt: Inject missing domain definitions, boundary constraints, or input/output schema
    clarifications identified during diagnosis.

### 3. Select Phase: Bootstrap Stability Selection

Do not evaluate candidates on a single validation score. A candidate with 78% accuracy on
30 examples may simply have benefited from favorable sample variance.

1. **Evaluate candidates**: Score all $K=4$ proposed prompts across the validation dataset.
2. **Resample**: Draw $B=20$ bootstrap datasets $D_b$ (sampling with replacement from the
   validation set, $|D_b| = |D_{\text{val}}|$).
3. **Compute selection frequency**:
   For each bootstrap sample $b \in [1, B]$:
   $$\hat{k}_b = \arg\max_{k} \text{Metric}(P_k, D_b)$$
4. **Stable Selection Criterion**:
   Select candidate $P^*$ that maximizes the stability score:
   $$\Pi(P_k) = \frac{1}{B} \sum_{b=1}^{B} \mathbb{I}(\hat{k}_b = k)$$
   Tie-break towards the shortest prompt (Minimum Description Length).

> **Empirical Caution**: Adding proposal diversity *without* bootstrap stability selection
> decreases performance by **-1.20%** due to noisy winner selection. Both steps must be paired.

---

## Environment Caveats

- **Validation set size**: Effective on small validation splits ($N \in [30, 200]$).
  If validation data is $>1,000$ examples, standard split testing or $B=10$ resamples
  is sufficient to bound selection error.
- **Token budget constraints**: Set an explicit length penalty in prompt generation to
  actively reject prompts exceeding target character limits ($<1,200$ characters).

## Failure Modes

- **Cluster collapse**: The diagnostic LLM grouping all errors into one generic "reasoning error"
  bucket. Countermeasure: require cluster labels to reference observable step outputs.
- **Ablation over-pruning**: Stripping critical task constraints during Strategy 3.
  Bootstrap selection naturally catches this because ablated candidates fail stability checks.

## Cross-References

- [`iterative-instruction-refinement`](../iterative-instruction-refinement/SKILL.md) — Baseline single-lineage prompt optimization.
- [`reference-trajectory-harness-evolution`](../reference-trajectory-harness-evolution/SKILL.md) — Reference trajectory tracking during prompt evolution.
- [`trajectory-aware-eval-pruning`](../trajectory-aware-eval-pruning/SKILL.md) — Cost pruning of evaluation benchmark datasets.

## Sources

- **Paper**: [ESPO: Error-Structured Prompt Optimization via Diagnose, Diversify, and Stabilize](https://arxiv.org/abs/2609.04197) — Liu, Tang, Singh, Ghadar (AWS Agentic AI, 2026)
- **Praxis source**: `src:2609-04197v1`
