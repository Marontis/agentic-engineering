---
name: algorithmic-design-evaluation
description: >
  Methodology for evaluating whether an AI agent is performing real algorithmic
  design (changing loss functions, update rules, supervision signals) or just
  tuning hyperparameters. Derived from AI4AI-Bench (arXiv:2608.20318). Covers
  the RSI level taxonomy, 8-family change classification, unified scoring,
  explore/replay/evaluate protocol, and diagnostic-first methodology.
category: recursive-self-improvement
source: https://arxiv.org/pdf/2608.20318
related_skills:
  - hyperagent-self-improvement
---

# Algorithmic Design Evaluation

Skill for measuring whether an AI agent is doing real algorithmic work —
changing how a model learns — versus adjusting execution parameters within a
fixed learning procedure.

## Core Problem

When an agent "improves" a training pipeline, it's easy to conflate three
fundamentally different kinds of changes. Most benchmarks measure only the
outcome (did the score go up?) without distinguishing what produced the gain.
This distinction is critical for recursive self-improvement (RSI): only
algorithmic changes compound unboundedly.

## The RSI Level Taxonomy

Three levels of improvement, only one of which compounds:

| Level | What Changes | Examples | Bounded By |
|:------|:------------|:---------|:-----------|
| **Systems engineering** | How computation maps to hardware | FlashAttention, ZeRO sharding, Megatron-LM, kernel fusion | Hardware roofline — once a kernel hits compute or memory bandwidth ceiling, no more gains |
| **Data engineering** | What the model trains on | Mixture reweighting, instruction filtering, data synthesis, curriculum design | Finite human text stock, power-law diminishing returns, model collapse from recursive reuse |
| **Algorithmic design** | How the model learns | Loss functions, update rules, regularization, schedules, objectives | **Nothing fundamental** — a better algorithm changes the compute/capability exchange rate for every subsequent run |

> "Adam, layer normalization, DPO and GRPO were each paid for once and have
> been earning since; if RSI is going to compound, most of the compounding has
> to come from [the algorithmic] level."

### Why This Matters for Agent Builders

If your agent is improving training pipelines, you need to know which level
it's working at. A systems-level optimization (faster kernels) helps the
current run. A data-level optimization (better curriculum) helps this
generation. An algorithmic-level optimization (better loss function) helps
**every generation that follows**, including the one that produces the next
agent.

## The 8-Family Change Classification

Every agent submission can be classified into 8 families on two sides of a
critical line:

### Run Side: "How this run goes"

These changes adjust execution parameters within a fixed learning procedure:

| Family | Description | Example |
|:-------|:-----------|:--------|
| **Duration/checkpointing** | How long it trains, how often it saves | Increase epochs from 3 to 10, save every 500 steps |
| **Hyperparameters** | Training knobs the algorithm takes as given | Learning rate 3e-4 → 1e-4, batch size 32 → 64 |
| **Checkpoint selection** | Which of the produced checkpoints to keep | Select based on validation loss vs. last checkpoint |
| **Trainable capacity** | How much and where to attach parameters | LoRA rank 8 → 16, add adapter to attention layers |

### Learning Side: "How the model learns"

These changes modify the learning algorithm itself:

| Family | Description | Example |
|:-------|:-----------|:--------|
| **Loss function** | Add, remove, or reweight objective terms | Add KL penalty, replace CE with focal loss, add auxiliary consistency loss |
| **Supervision signal** | Introduce a signal the procedure didn't have | Add optimal-move labels, create synthetic demonstrations, build a reward model |
| **Update rule** | Replace the optimization algorithm | Adam → Lion, SGD → Shampoo, add gradient clipping strategy |
| **Training data** | Change what the procedure trains on | Filter low-quality examples, synthesize hard negatives, curriculum ordering |

### The Critical Statistic

From AI4AI-Bench (263 classified submissions across 6 systems, 10 tasks):

- **53.6%** of submissions stayed entirely on the run side
- Only **46.4%** touched how the model learns at all
- Only **8.7%** changed the update rule itself
- Only **8.0%** changed the training data

Submissions that reached the learning side averaged **0.226** vs **0.126** for
run-side-only — a gap of 0.100 (SE: 0.022).

## Applying the Classification

To audit whether your agent (or an agent you're evaluating) is doing real
algorithmic work, classify every change it makes:

```python
CHANGE_FAMILIES = {
    # Run side
    "duration_checkpointing": {
        "side": "run",
        "signals": ["num_epochs", "save_steps", "max_steps", "checkpoint_interval",
                     "training_duration", "early_stopping"],
    },
    "hyperparameters": {
        "side": "run",
        "signals": ["learning_rate", "lr", "batch_size", "warmup", "weight_decay",
                     "gradient_accumulation", "scheduler"],
    },
    "checkpoint_selection": {
        "side": "run",
        "signals": ["best_checkpoint", "model_selection", "eval_strategy",
                     "save_best_model", "load_best"],
    },
    "trainable_capacity": {
        "side": "run",
        "signals": ["lora_rank", "adapter", "num_layers", "hidden_size",
                     "freeze_layers", "trainable_params"],
    },
    # Learning side
    "loss_function": {
        "side": "learning",
        "signals": ["loss", "objective", "criterion", "kl_penalty", "reward_weight",
                     "auxiliary_loss", "regularization_term"],
    },
    "supervision_signal": {
        "side": "learning",
        "signals": ["labels", "demonstrations", "reward_model", "teacher",
                     "distillation", "imitation", "feedback_signal"],
    },
    "update_rule": {
        "side": "learning",
        "signals": ["optimizer", "update_step", "gradient_transform",
                     "momentum", "second_order", "natural_gradient"],
    },
    "training_data": {
        "side": "learning",
        "signals": ["dataset", "data_filter", "data_synthesis", "curriculum",
                     "data_augmentation", "sampling_strategy"],
    },
}

def classify_submission(diff: str) -> dict:
    """Classify a code diff into change families.
    Returns which families were touched and which side dominates."""
    touched = {family: False for family in CHANGE_FAMILIES}
    for family, info in CHANGE_FAMILIES.items():
        for signal in info["signals"]:
            if signal in diff.lower():
                touched[family] = True
    
    run_count = sum(1 for f, t in touched.items() 
                    if t and CHANGE_FAMILIES[f]["side"] == "run")
    learn_count = sum(1 for f, t in touched.items() 
                      if t and CHANGE_FAMILIES[f]["side"] == "learning")
    
    return {
        "families_touched": {f: t for f, t in touched.items() if t},
        "reaches_learning_side": learn_count > 0,
        "run_count": run_count,
        "learn_count": learn_count,
    }
```

## Unified Scoring Function

When evaluating across tasks with incommensurable metrics (perplexities,
pass rates, aesthetic scores), use a progress coordinate with three reference
points:

```python
import math

def unified_score(metric_value: float, baseline: float, optimum: float,
                  uninformative: float, direction: str = "up",
                  use_log: bool = False) -> float:
    """Map any metric onto a [0, 1] scale.

    Args:
        metric_value: the raw metric value
        baseline: score of the shipped/existing algorithm
        optimum: best attainable value (rate=1, ppl=1, nll=0)
        uninformative: score of a model with no task knowledge
        direction: "up" if higher is better, "down" if lower is better
        use_log: True for perplexity-like metrics (exponential of cross-entropy)

    Returns:
        σ ∈ [0, 1] where 0.1 = baseline, 1.0 = optimum
    """
    # Apply progress coordinate
    phi = (lambda x: -math.log(x)) if use_log else (lambda x: x)
    if direction == "down":
        phi_orig = phi
        phi = lambda x: -phi_orig(x)

    phi_x = phi(metric_value)
    phi_b = phi(baseline)
    phi_bot = phi(uninformative)
    phi_star = phi(optimum)

    if phi_x <= phi_b:
        # Below baseline: measure how far short
        sigma = 0.1 * (phi_x - phi_bot) / (phi_b - phi_bot) if phi_b != phi_bot else 0.0
    else:
        # Above baseline: measure distance to optimum closed
        sigma = 0.1 + 0.9 * (phi_x - phi_b) / (phi_star - phi_b) if phi_star != phi_b else 0.1

    return max(0.0, min(1.0, sigma))
```

### Scale Interpretation

| σ value | Meaning |
|:--------|:--------|
| 0.0 | Uninformative model (random chance) or returned nothing |
| 0.1 | Matches the shipped/existing algorithm exactly |
| 0.1–0.4 | Beats baseline modestly |
| 0.4+ | Closes more than a third of the distance to optimum |
| 1.0 | Task optimum |

## Evaluation Protocol: Explore / Replay / Evaluate

The protocol enforces separation of concerns:

### Phase 1: Exploration (agent has access)

- Time budget: 4 hours (or configurable)
- Resources: 1 GPU
- Agent can: read code, edit code, run training, query proxy metric freely
- Agent outputs: **source code** (not weights, not cached state)

### Phase 2: Replay (agent has no access)

- Fresh container, clean start
- Submitted source code run from initialization
- Time budget: up to 12 hours
- 3 most recent checkpoints saved, best one scored

### Phase 3: Evaluation (frozen, agent never sees)

- Evaluator fixed before the first run
- No access to agent's workspace
- Predetermined metric on predetermined asset

> **Key design property**: the boundary guarantees that no agent could score a
> candidate under the metric that decides its result. The agent can probe its
> proxy metric, but the final evaluator is completely out of reach.

## Diagnostic-First Methodology

The exceptional submissions in AI4AI-Bench all share one trait: they **built
something measurable before acting**. This is the pattern that separates real
algorithmic design from hyperparameter tuning.

### The Three Exemplars

**1. OWL (Pruning → Distillation Pipeline)**
- Diagnosis: found that activation propagation was overwriting layer-0 inputs
  with layer-31's activations
- Action: replaced one-shot pruning with a 3-stage pipeline (weight selection
  + layerwise distillation + masked KD fine-tune)
- Result: perplexity 53.4 → ~13

**2. Model Soup (Closed Form → Optimization)**
- Diagnosis: built a custom evaluation rig (0.38s vs ~190s per score)
- Action: used the fast rig to compare 5 methods, found greedy soup and
  learned coefficients tied
- Result: systematic method comparison impossible without the instrument

**3. RAGEN (RL → Imitation Learning)**
- Diagnosis: judged that Sokoban's structure made imitation superior to RL
- Action: replaced GRPO entirely with supervised imitation learning (generate
  boards, label optimal moves, fine-tune with DAgger)
- Result: perfect score

### The Diagnostic Loop

```
Read training dynamics → Name the failing mechanism → Change that mechanism
     ↑                                                        │
     └────────────── Measure the effect ──────────────────────┘
```

What to read:
- Loss curve shape and spikes
- Gradient norms (vanishing? exploding?)
- Policy entropy (collapsed?)
- Divergence from reference model
- Distribution of advantages
- Per-token loss breakdowns
- Reward model saturation patterns

## Reasoning Effort and Algorithmic Willingness

More reasoning effort doesn't make algorithmic improvements *better* — it makes
agents *willing to attempt them*:

| Effort Level | Share Reaching Learning Side | Mean Score |
|:------------|:----------------------------|:-----------|
| none (lowest) | **8%** | 0.094 |
| low | 39% | — |
| medium | 33% | — |
| high | 49% | — |
| xhigh | 65% | — |
| max (highest) | **64%** | 0.196 |

> "Reasoning effort works by making an agent attempt the thing that pays
> rather than by making the attempt itself better."

Implication: if you're building an agent that should do algorithmic design,
the bottleneck is more likely **willingness to attempt structural changes**
than ability to execute them well. System prompts, tool design, and reasoning
budget all affect this.

## Benchmark Performance (August 2026)

| System | Mean σ | Best Config σ | Cost (median) |
|:-------|:-------|:-------------|:--------------|
| Claude Opus 5 | 0.250 | 0.288 | $181 |
| GPT-5.6 Sol | 0.191 | 0.245 | $434 |
| Kimi K3 | 0.174 | 0.174 | $30 |
| Claude Sonnet 5 | 0.145 | 0.216 | $98 |
| GPT-5.6 Terra | 0.135 | 0.228 | $43 |
| GPT-5.6 Luna | 0.117 | 0.147 | $17 |

Even the best system closes less than a fifth of the distance between the
shipped algorithm and the task optimum.

## When to Use This Skill

- Evaluating whether your agent is doing real algorithmic work vs. tuning knobs
- Designing benchmark protocols for AI research agents
- Building agents that diagnose training dynamics before proposing changes
- Classifying agent submissions by what they actually change
- Understanding the RSI capability frontier of current systems
- Setting up explore/replay/evaluate separation for fair agent benchmarking

## Connection to Hyperagent Self-Improvement

> **Cross-reference**: The `hyperagent-self-improvement` skill provides patterns
> for building agents that improve their own improvement mechanism. Use this
> skill to verify that those improvements are happening at the **algorithmic
> level** (loss, update rule, supervision) rather than the run level
> (hyperparameters, checkpointing, capacity). The emergent capabilities
> documented in Hyperagents — persistent memory, performance tracking,
> structured decision pipelines — are examples of what the "diagnostic-first"
> capability looks like when it works.

## Design Patterns to Extract

1. **RSI level classification**: always know whether a change is systems,
   data, or algorithmic — only algorithmic compounds unboundedly
2. **8-family change taxonomy**: audit every submission against run-side vs.
   learning-side families to understand what the agent actually did
3. **Explore/replay/evaluate separation**: the agent proposes source code,
   someone else runs it — prevents overfitting to evaluation
4. **Unified scoring with progress coordinates**: map incommensurable metrics
   onto one scale with baseline=0.1 and optimum=1.0
5. **Diagnostic-first methodology**: build an instrument, measure, name the
   failing mechanism, then change it — not the other way around

## References

- **Paper**: [AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement](https://arxiv.org/abs/2608.20318) — Chi, Li, Hong, Wang, Gao, Yang, He, Zheng, Xiao, Na (Einsia.AI / Tsinghua)
- **Code**: https://github.com/Einsia/AI4AI-Bench
- **Homepage**: https://lab.einsia.ai/ai4ai
- **Praxis source**: `src:arxiv-2608-20318`
