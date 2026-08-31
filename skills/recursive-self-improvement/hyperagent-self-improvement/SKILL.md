---
name: hyperagent-self-improvement
description: >
  Patterns for building self-improving AI agents where the improvement
  mechanism itself is improvable. Derived from Hyperagents (arXiv:2603.19461).
  Covers hyperagent program structure (task agent + meta agent), archive-based
  evolutionary loops, metacognitive self-modification, persistent memory,
  performance tracking, cross-domain transfer, and safety constraints.
category: recursive-self-improvement
source: https://arxiv.org/pdf/2603.19461
related_skills:
  - algorithmic-design-evaluation
---

# Hyperagent Self-Improvement

Skill for building self-referential agent systems where the agent can improve
not only how it solves tasks but also how it generates future improvements.

## Core Problem

Traditional self-improving AI systems have a fixed meta-level: a handcrafted
mechanism generates improvement instructions, and the task agent evolves within
the boundaries that mechanism defines. Adding a meta-meta system doesn't solve
this — it shifts the bottleneck upward into infinite regress.

The **alignment assumption** compounds the problem: the Darwin Gödel Machine
(DGM) works in coding because improving at coding directly improves
self-modification ability. But this alignment doesn't hold across domains —
improving at poetry doesn't improve the ability to rewrite your own code.

## Key Insight

Combine the task agent and meta agent into a **single editable program** called
a **hyperagent**. The meta agent's modification procedure is itself part of the
editable codebase, enabling **metacognitive self-modification** — improving not
only task-solving behavior but also the mechanism that generates future
improvements. No domain alignment required.

## Architecture: DGM-Hyperagents (DGM-H)

```
┌─────────────────────────────────────────────────────────────┐
│ ARCHIVE (population of hyperagents — grows over time)       │
│                                                             │
│   [H₁] [H₂] [H₃] [H₄] ... [Hₙ]                          │
│                                                             │
│   Parent selection: P(select) ∝ performance / num_children  │
│   (favors high-performing agents with unexplored potential) │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ METACOGNITIVE SELF-MODIFICATION                             │
│                                                             │
│   Selected parent hyperagent generates a modified copy.     │
│   The meta agent can modify:                                │
│     • The task agent (how it solves problems)               │
│     • The meta agent (how it generates modifications)       │
│     • Both simultaneously                                   │
│                                                             │
│   Input: agent's repo + past evaluation results + budget    │
│   Output: code diff → new hyperagent                        │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ EVALUATION                                                  │
│                                                             │
│   Staged evaluation (computational efficiency):             │
│   1. Quick pre-filter on small task subset                  │
│   2. Full evaluation only if promising                      │
│   3. Result added to archive as stepping stone              │
└─────────────────────────────────────────────────────────────┘
```

## Hyperagent Program Structure

A hyperagent is a single Python program containing two editable modules:

```python
class Hyperagent:
    """Self-referential agent: task_agent + meta_agent in one editable program."""

    def task_agent(self, task_inputs):
        """Solve the target task. Initially: single FM call."""
        # This module is editable by the meta_agent.
        # Over time, evolves into multi-stage pipelines,
        # structured decision frameworks, domain knowledge bases.
        return fm_call(task_inputs)

    def meta_agent(self, agent_repo, past_evaluations, budget):
        """Modify this hyperagent (including this method itself).

        This is the key innovation: meta_agent can rewrite meta_agent.
        It receives the entire codebase and full evaluation history.
        """
        # Analyze past performance trends
        # Identify which changes produced gains vs regressions
        # Propose code diff targeting task_agent AND/OR meta_agent
        return code_diff
```

### Design Principles

| Principle | Rationale |
|:----------|:----------|
| **Simple initial agent** (single FM call + bash + file tools) | Broad search space; avoids constraining possible improvements |
| **Python** (Turing-complete) | Hyperagent can build any computable machine |
| **Frozen FM** (weights never modified) | Agent modifies scaffolding/prompts/pipelines, not the model |
| **Everything is editable** (except outer loop, for safety) | No artificial ceiling on what can be improved |

## Parent Selection Algorithm

The archive-based evolutionary loop uses performance-proportional,
child-count-inverse selection:

```python
def select_parent(archive: list[Hyperagent]) -> Hyperagent:
    """Select parent for next self-modification round.

    Bias toward hyperagents that:
    - Perform well (high scores)
    - Have unexplored potential (few children that compiled)
    """
    weights = []
    for agent in archive:
        perf = agent.validation_score  # or training score if no validation
        children = count_compiled_children(agent)
        weight = perf / (children + 1)  # +1 to avoid division by zero
        weights.append(weight)
    return weighted_sample(archive, weights)
```

## Staged Evaluation Protocol

To reduce computational cost, agents are evaluated in stages:

```python
def staged_evaluate(hyperagent, tasks, stage_sizes=[10, 100]):
    """Evaluate in stages: quick pre-filter → full evaluation."""
    for stage_size in stage_sizes:
        subset = tasks[:stage_size]
        score = evaluate(hyperagent.task_agent, subset)
        if score < min_threshold:
            # Agent fails pre-filter → assign zero for remaining tasks
            return 0.0
    return evaluate(hyperagent.task_agent, tasks)
```

## Emergent Capabilities

The DGM-H autonomously develops general-purpose engineering tools without
being instructed to. These emergent capabilities are what transfer across
domains:

### Performance Tracking

```python
class PerformanceTracker:
    """Tracks performance metrics across agent generations.
    Autonomously invented by DGM-H during self-improvement runs."""

    def __init__(self, tracking_file="./outputs/performance_history.json"):
        self.tracking_file = tracking_file
        self.history = self._load_history()

    def record_generation(self, generation_id, domain, score, metadata=None):
        """Record performance for a generation."""
        self.history.append({
            "generation_id": generation_id,
            "domain": domain,
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        self._save_history()

    def get_improvement_trend(self, domain=None, window=5):
        """Calculate improvement trend using moving average."""
        filtered = [h for h in self.history if not domain or h.get('domain') == domain]
        if len(filtered) < window * 2:
            return None
        recent_avg = sum(h['score'] for h in filtered[-window:]) / window
        older_avg = sum(h['score'] for h in filtered[-window*2:-window]) / window
        return recent_avg - older_avg  # Positive if improving
```

### Persistent Memory

The hyperagent stores synthesized insights, causal hypotheses, and
forward-looking plans that are actively consulted during subsequent
self-modification steps:

```json
{
  "best_performers_analysis": {
    "value": "Gen55: 63% acc but too harsh. Gen64: 61% acc, BEST BALANCE.
     Key Insight: Need to combine gen55's critical reasoning with gen64's balance.",
    "timestamp": "2026-01-07T00:43:27"
  },
  "gen66_results": {
    "value": "CRITICAL ISSUE: Paper review went backwards —
     gen65 changes over-corrected.",
    "timestamp": "2026-01-07T01:03:41"
  },
  "iteration_66_improvement": {
    "value": "CORRECTED after gen65 over-correction.
     New approach: (1) Clear REJECT criteria, (2) Decision Protocol with
     explicit thresholds (~40%/~60%), (3) Borderline defaults to REJECT.",
    "timestamp": "2026-01-07T01:06:35"
  }
}
```

This enables later generations to **avoid repeating past mistakes** and
**build on earlier discoveries**.

### Structured Decision Machinery

In paper review: evolves from surface-level prompt tweaks ("be rigorous")
to explicit multi-stage evaluation pipelines with checklists, decision rules,
and clearly defined accept/reject criteria.

In robotics reward design: incrementally builds an internal knowledge base of
environment constraints, valid state variables, and reward-scaling heuristics.

## Cross-Domain Transfer

Meta-level improvements learned in one domain transfer to completely new
domains. This is the paper's strongest result.

### Transfer Agent Selection

```python
def select_transfer_agent(archive, metric="lineage_discounted_improvement"):
    """Select transfer agent based on descendant performance.

    Uses lineage-discounted criterion: favor agents that reliably produce
    strong improvements within fewer self-modification steps, since
    improvements many iterations later are less attributable to the agent.
    """
    best_agent = None
    best_score = -float('inf')
    for agent in archive:
        score = compute_descendant_improvement(agent, discount_by_depth=True)
        if score > best_score:
            best_score = score
            best_agent = agent
    return best_agent
```

### Transfer Protocol

1. Select transfer hyperagent from source domain runs
2. Carry over the entire implementation (both task agent and meta agent)
3. Use transfer meta agent to generate new task agents in target domain
4. Transfer task agent serves as initial agent for new variants

### Quantitative Results

| Transfer Setup | imp@50 on Math Grading (unseen domain) |
|:---------------|:--------------------------------------|
| Initial meta agent (DGM w/o self-improve) | 0.000 |
| Initial meta agent (DGM-H w/o self-improve) | 0.000 |
| Transfer from DGM-custom | 0.000 |
| Transfer from DGM-H | **0.630** |

Transfer hyperagents achieve imp@50 = 0.630 on a completely unseen domain —
from 0.0 to 0.63 accuracy in 50 iterations using only meta-level strategies
learned elsewhere.

## Task Performance Benchmarks

| Domain | Initial → DGM-H (test) | vs Static Baseline |
|:-------|:----------------------|:-------------------|
| Coding (Polyglot) | 0.084 → 0.267 | Comparable to DGM |
| Paper Review | 0.000 → **0.710** | Beats AI-Scientist-v2 (0.630) |
| Robotics Reward Design | 0.060 → **0.372** | Beats default reward (0.348) |
| Olympiad Math Grading | 0.000 → 0.610 | Improved ProofAutoGrader 0.561 → 0.601 |

## Critical Ablations

| Ablation | Result | Conclusion |
|:---------|:-------|:-----------|
| DGM-H w/o self-improve | Collapses (p < 0.05) | Self-improving meta agent is essential |
| DGM-H w/o open-ended exploration | Collapses (p < 0.05) | Archive-based diversity is essential |
| Both present (DGM-H full) | Sustained improvement | Both components necessary together |

## Safety Constraints

| Measure | Implementation |
|:--------|:---------------|
| **Sandboxing** | All agent-generated code runs in sandboxed environments |
| **Resource limits** | Timeouts, restricted internet access |
| **Human oversight** | Maintained throughout all experiments |
| **Fixed outer loop** | Parent selection + evaluation protocols not self-modifiable (in main experiments) |
| **Predefined metrics** | Tasks and evaluation criteria fixed before runs |

> **Critical limitation**: "As AI systems gain the ability to modify themselves
> in increasingly open-ended ways, they can potentially evolve far more rapidly
> than humans can audit or interpret."

## When to Use This Skill

- Building self-improving agent systems (any domain)
- Designing archive-based evolutionary agent loops
- Implementing persistent cross-generation memory for agent systems
- Creating agents that improve their own improvement process
- Setting up transfer learning between agent populations across domains
- Designing safety guardrails for self-modifying systems

## Diagnostic Check (via companion skill)

> **Cross-reference**: Use the `algorithmic-design-evaluation` skill to verify
> that your hyperagent's meta-agent is doing real algorithmic design — changing
> loss functions, update rules, and supervision signals — rather than just
> tuning hyperparameters. AI4AI-Bench found that 53.6% of agent submissions
> never touch how the model learns, even when explicitly told to improve the
> training algorithm.

## Design Patterns to Extract

1. **Hyperagent = task_agent + meta_agent in one editable program**: the meta
   agent can rewrite itself, eliminating the fixed-meta-level bottleneck
2. **Archive-based open-ended exploration**: population of stepping stones
   prevents premature convergence; performance/child-count selection balances
   exploitation and exploration
3. **Staged evaluation**: quick pre-filter on small subset, expand only if
   promising — critical for computational efficiency
4. **Emergent instrumentation**: let the agent invent its own performance
   tracking, persistent memory, and diagnostic tools
5. **Transfer via lineage-discounted selection**: select agents whose
   descendants improved most, discounted by depth, for cross-domain warm-start

## References

- **Paper**: [HyperAgents: Recursive Metacognitive Self-Improvement](https://arxiv.org/abs/2603.19461) — Zhang, Zhao, Yang, Foerster, Clune, Jiang, Devlin, Shavrina (Meta FAIR, UBC, Edinburgh, NYU)
- **Code**: https://github.com/facebookresearch/Hyperagents
- **Praxis source**: `src:arxiv-2603-19461`
