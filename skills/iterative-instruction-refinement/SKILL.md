---
name: iterative-instruction-refinement
description: >
  How to iteratively improve agent instructions (system prompts, skill text,
  workflow guidelines) using a single-lineage revision loop with sliding-window
  rollout feedback. A teacher model revises instructions based on recent
  execution traces and rewards, without population-based search or complex
  optimization. Covers the NPO algorithm, teacher-model leverage, controlled
  evaluation, and cross-model prompt transfer.
  Derived from "Naive Prompt Optimization" (arXiv:2608.27266).
source: https://arxiv.org/pdf/2608.27266
related_skills:
  - skill-design-methodology
  - knowledge-compounding-loop
---

# Iterative Instruction Refinement

How to improve agent instructions through simple, single-lineage revision
using execution feedback — without the complexity of population-based search,
beam search, or Pareto selection.

## The Problem

Agent instructions (system prompts, skill text, workflow guidelines) often
need iterative refinement. The temptation is to reach for sophisticated
optimization: maintain a population of candidates, apply tournament
selection, use Bayesian optimization, or build multi-candidate Pareto
frontiers.

But this complexity has diminishing returns:

1. **Complex search doesn't scale with teacher quality**: as the revision
   model gets stronger, the marginal benefit of sophisticated search
   shrinks — the teacher's reasoning compensates for optimizer complexity
2. **Population maintenance costs rollouts**: maintaining and evaluating
   multiple candidates consumes the same rollout budget that could feed
   richer feedback to a single lineage
3. **Overengineering masks the real bottleneck**: feedback quality matters
   more than search strategy. Rich rollout traces with rewards beat
   sparse signals with complex search.

**The evidence**: a simple single-lineage method (NPO) matches or beats
GEPA (a complex multi-candidate search with Pareto selection) on IFBench
and HotpotQA, using fewer rollouts. The advantage increases with stronger
teacher models.

> Source: Chang & Chen (2026), Figure 4, Qwen3-8B student

---

## The NPO Algorithm

### Overview

Maintain a single instruction lineage. Each iteration: run the agent,
collect traces and rewards, show a sliding window of recent performance
to a teacher model, get a revised instruction, repeat.

### The Procedure

```
Input:
  - Initial instruction P(0) (the current system prompt or skill text)
  - Task dataset D (examples the agent will execute)
  - Minibatch size N (how many tasks per iteration)
  - Sliding window size W (how many iterations of history to show)
  - Teacher model T (the model that produces revised instructions)
  - Number of iterations Y

For each iteration i = 0 to Y-1:
  1. Sample a minibatch B_i of N tasks from D
  2. Run the agent with current instruction P(i) on B_i
  3. Collect rollout traces and rewards R_i
  4. Construct sliding-window context:
     - Include the W most recent iterations (i-W+1 through i)
     - For each: the instruction version, rollout traces, rewards
  5. Ask the teacher T to revise P(i) into P(i+1) given this context
  6. Optionally evaluate P(i+1) on a held-out validation set

Return: the instruction version with the best validation score
```

### Key Design Choices

**Single lineage, not population**: only one active instruction at a time.
No branching, no merging, no candidate pool. This concentrates all rollout
budget into feedback quality for one line of improvement.

**Sliding window, not full history**: show only the W most recent
iterations to the teacher. This keeps the teacher's context focused on
recent performance trends rather than being overwhelmed by early-iteration
noise. Typical setting: W = 2.

**Rich rollout traces, not just scores**: unlike OPRO (which shows only
prior prompts and their scalar scores), NPO provides the teacher with
complete rollout traces — the agent's reasoning, actions, observations,
and per-rollout rewards. This rich context is what enables simple search
to rival complex search.

**Larger minibatches, fewer iterations**: NPO uses bigger minibatches
(40-50 examples) with fewer iterations (10-20), while methods like GEPA
use smaller minibatches (3) with more iterations. Larger minibatches
give the teacher a more representative sample of performance per revision.

---

## Teacher-Model Leverage

The most important finding for practical use: **NPO's advantage increases
with stronger teacher models**.

| Teacher Model | NPO vs GEPA on IFBench | NPO vs GEPA on HotpotQA |
|:-------------|:----------------------|:------------------------|
| Same as student (Qwen3-8B) | Comparable | Comparable |
| DeepSeek-V4-Flash | NPO ahead | NPO ahead |
| GPT-5.5 | NPO clearly ahead | NPO clearly ahead |

**Why this matters**: if you're going to invest compute anywhere in the
refinement process, invest in a stronger teacher model rather than a more
complex optimizer. Stronger reasoning partially substitutes for search
complexity.

**Practical implication**: use the strongest available model as your
revision teacher, even if the agent that will *use* the instructions is
a cheaper model. The teacher only runs during refinement (offline), not
during deployment.

---

## Cross-Model Instruction Transfer

Instructions optimized for one model transfer to others:

- **Within-family transfer** is strongest: prompts optimized on Qwen3-8B
  improve Qwen3-14B and Qwen3-32B by similar or larger margins
- **Cross-family transfer** works but with more variance: Qwen-optimized
  prompts improve Llama models, and vice versa
- **Transfer is mostly positive**: across all tested combinations, most
  settings show positive gains with only a few exceptions

**Implication**: you don't need to re-run optimization for every model
you deploy to. Optimize once on a representative student, then apply
the resulting instructions verbatim to other models. Monitor for
regressions but expect gains.

---

## Controlled Evaluation Methodology

When comparing instruction versions or comparing prompt optimization
against RL-based approaches, two techniques reduce noise:

### Shared Pseudorandomness

Generate environment instances from predefined random seeds and reuse
the same seed sequence across instruction versions. This ensures that
performance differences come from the instructions, not from variation
in instance difficulty.

### Constrained Decoding

Separate decision quality from format-following quality. If the agent
fails because it produced "row 3 and then column 4" instead of "[3,4]",
that's a formatting error, not a decision error. Use constrained
decoding to enforce output format, so you're measuring whether the
instruction improved *decisions*, not whether it improved *formatting*.

**When to use this**: whenever you're comparing two instruction versions
and need to attribute the performance difference to the instructions
rather than to environmental noise or formatting artifacts.

---

## When to Use This

### Use iterative instruction refinement when:

- You have agent instructions (system prompts, skill text, guidelines)
  that need improvement
- You can run the agent on a sample of tasks and measure success
- You have access to a teacher model (can be the same model or stronger)
- You want to avoid the complexity of population-based optimization

### Use more complex approaches when:

- Your task distribution is highly multimodal (different tasks need
  fundamentally different instructions — a single lineage can't cover
  all modes)
- You're optimizing for Pareto-frontier tradeoffs across competing
  objectives (e.g., speed vs. accuracy)
- Your teacher model is weak relative to the task difficulty (complex
  search may compensate for weak reasoning)

### Don't use this when:

- You have no way to measure task success (the loop needs rewards)
- The instruction is already at or near ceiling performance
- You need RL-level adaptation (some tasks respond better to weight
  updates than instruction changes — especially tasks requiring
  fast strategic planning in interactive games)

---

## Practical Settings

Based on the paper's experimental configurations:

| Setting | IFBench / QA | Interactive Games |
|:--------|:-------------|:-----------------|
| Minibatch size N | 40–50 | 24 episodes |
| Iterations Y | 10–20 | 17 |
| Window size W | 2 | 2 |
| Validation set | 300 examples | Separate eval episodes |
| Total rollout budget | 3,500–6,800 | 408 episodes |

These are starting points. Adjust based on:
- Context window limits of the teacher model
- Cost per rollout
- Variance in task difficulty

---

## Connection to Other Skills

| Skill | Relationship |
|:------|:------------|
| `knowledge-compounding-loop` | Provides the structured knowledge context that makes revision *informed*. NPO revises instructions; the knowledge layer tells the teacher *what to focus on*. |
| `skill-design-methodology` | The revised instruction should still pass the skill authoring checklist — subtask level, text format, high utility score. NPO is the revision *mechanism*; skill design is the quality *gate*. |
| `agent-self-improvement-loop` | WCF surfaces issues; NPO can be the mechanism for revising instructions to address those issues. |

---

## Evidence Summary

| Finding | Source | Scale |
|:--------|:------|:------|
| NPO matches/beats GEPA with fewer rollouts | Chang & Chen 2026, Fig. 4 | IFBench + HotpotQA |
| Advantage increases with stronger teachers | Chang & Chen 2026, Fig. 4 | 3 teacher models |
| Optimized prompts transfer across student models | Chang & Chen 2026, Fig. 5 | 5+ student models |
| Within-family transfer strongest, cross-family also positive | Chang & Chen 2026, §3.2 | Qwen + Llama families |
| GRPO complements on tasks less amenable to prompt optimization | Chang & Chen 2026, Fig. 6 | 22 TextArena games |
| Rich rollout feedback > sparse score feedback | Chang & Chen 2026 vs OPRO | Architectural comparison |

## References

- **Paper**: [Naive Prompt Optimization: Rethinking the Need for Complex Prompt Search](https://arxiv.org/abs/2608.27266) — Chang, Chen (Purdue University)
- **Praxis source**: `src:2608-27266`
