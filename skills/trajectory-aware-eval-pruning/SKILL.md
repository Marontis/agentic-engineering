---
name: trajectory-aware-eval-pruning
description: >
  Trajectory-aware evaluation subset selection and cost pruning for software
  engineering and multi-step agent benchmarks. Fuses process-level execution
  features with outcome signals to reduce benchmark costs by 65–80% without
  compromising ranking fidelity. Derived from PTA-IRT (arXiv:2609.01603).
source: https://arxiv.org/abs/2609.01603
---

# Trajectory-Aware Evaluation Pruning

Use this skill when designing, pruning, or selecting evaluation suites for
coding agents and long-horizon autonomous systems.

## When to Use

- Full benchmark runs (e.g., SWE-bench, RepoQA, HumanEval) are too costly
  or slow for continuous integration / PR validation
- Selecting a representative sub-benchmark (e.g., 50 tasks instead of 500)
  for daily evaluation cycles
- Avoiding uninformative evaluation tasks that have zero discriminative power
  (tasks that either all models pass trivially or all models fail completely)
- Assessing model capabilities across diverse problem-solving trajectories

## Core Insight

Conventional benchmark down-sampling relies on **outcome-only** signals
(historical pass/fail matrices or static problem descriptions). This ignores
the critical process dimension of agentic coding: **how** agents explore,
navigate, and repair codebases.

Fusing **process signals** (trajectory length, tool calling diversity, error
recovery attempts, code modification span) with outcome signals enables
selecting evaluation items that maximize discriminative capability across
models while reducing execution tokens and compute costs by 65–80%.

---

## Procedure

### Step 1: Extract Trajectory Fingerprints from Pilot Runs

Run a small pilot fleet of diverse models across candidate benchmark tasks.
For each task $i$ and agent $j$, extract process features:

| Trajectory Metric | Description | Diagnostic Value |
|:---|:---|:---|
| **Step Count ($S_{ij}$)** | Total turns taken to reach completion | Measures reasoning horizon and search efficiency |
| **Tool Entropy ($H_{ij}$)** | Shannon entropy of invoked tool distribution | Distinguishes diverse explorers from repetitive loopers |
| **Recovery Cycles ($R_{ij}$)** | Number of syntax/test failures followed by self-correction | Measures error tolerance and reflection capability |
| **Edit Radius ($E_{ij}$)** | Number of distinct files and functions modified | Separates localized fixes from architectural changes |

### Step 2: Compute Task Discrimination & Information Value

Fit an Item Response Theory (IRT) model augmented with trajectory process
features:

1. **Difficulty Parameter ($\beta_i$)**: Tasks where low-tier models fail but
   frontier models succeed have high discrimination. Discard tasks where all
   models pass (trivial) or all models fail (impossible noise).
2. **Trajectory Sensitivity ($\gamma_i$)**: High trajectory sensitivity means
   agents exhibit markedly different problem-solving behaviors on this task.
3. **Execution Cost ($C_i$)**: Average token spend and runtime seconds per task.

### Step 3: Solve Cost-Constrained Item Selection

Select the subset of $K$ tasks that maximizes total test information within
a predefined compute budget $B$:

$$\max_{S \subseteq \mathcal{D}} \sum_{i \in S} \text{Information}(i) \quad \text{subject to} \quad \sum_{i \in S} C_i \le B$$

- Prioritize high-discrimination, moderate-cost tasks.
- Ensure representative coverage across project languages, repository sizes,
  and bug classes.

### Step 4: Validate Ranking Fidelity

Assert the pruned benchmark produces ranking decisions concordant with the
full benchmark:

- Compute Spearman rank correlation ($\rho$) between model scores on the pruned
  subset vs. the full benchmark.
- Require $\rho \ge 0.95$. If $\rho < 0.95$, increase the budget or rebalance
  task categories.

---

## Environment Caveats

- **Model Evolution Drift**: As new frontier models emerge, task difficulty
  parameters ($\beta_i$) drift downward. Re-calibrate item parameters every
  quarterly evaluation cycle.
- **Flaky Tests**: Tests with nondeterministic failures (race conditions,
  network flakiness) artificially distort discrimination scores. Exclude flaky
  items before running subset selection.

## Failure Modes

- **Length Bias Selection**: Over-indexing on very long trajectories, resulting
  in a sub-benchmark composed entirely of slow, timeout-prone tasks.
- **Static Description Overfitting**: Selecting tasks purely based on lexical
  diversity of the issue descriptions rather than actual execution difficulty.
- **Trivial-Pass Saturation**: Filling the benchmark with simple 1-line syntax
  fixes that show high success rates but fail to distinguish frontier agent
  capabilities.

## Cross-References

- [`agent-working-memory-eval`](../agent-working-memory-eval/SKILL.md) — Measuring
  context usage during benchmark runs.
- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md) —
  Attributing errors across evaluation trajectories.

## Sources

- Efficient SWE Agent Benchmarking via Trajectory-Aware Evaluation (arXiv:2609.01603)
