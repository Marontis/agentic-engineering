---
name: cost-aware-hierarchical-analysis
description: >
  How to build a hierarchical multi-agent analysis pipeline that
  adaptively escalates from cheap to expensive modalities based on
  confidence and inter-agent agreement.  Reduces average analysis
  cost by ~44% while maintaining accuracy.
  Derived from "Cost-Aware Hierarchical Multi-Agent Ransomware
  Detection and Family Attribution" (arXiv:2609.04820).
---

# Cost-Aware Hierarchical Analysis

Use this skill when building an analysis pipeline where multiple
modalities or tools are available at different cost/latency tiers,
and you need to balance accuracy against computational budget.

## When to Use

- Your agent has access to multiple analysis tools of varying cost
  (e.g., static analysis → dynamic analysis → LLM verification)
- You need to process many items and cannot afford to run the full
  pipeline on every one
- You want to adaptively allocate expensive analysis only where
  cheap analysis is insufficient
- Your analysis requires specialized agents for different modalities

## Core Insight

Conventional multimodal analysis runs all available modalities on
every sample, resulting in unnecessary cost and latency.  A
**hierarchical architecture** organizes specialized agents into
domain controllers coordinated by a meta-orchestrator.  Cheap
modalities resolve most cases; expensive modalities are only
triggered when confidence is insufficient or specialists disagree.

**Key evidence**: The hierarchical system achieved 96.57% accuracy,
0.96 F1-score and 0.99 ROC-AUC while reducing average analysis cost
by 43.97% relative to exhaustive analysis.  56.05% of cases resolved
using the cheapest modality alone; only 4.33% required the complete
pipeline.

---

## Procedure

### 1. Define the Modality Hierarchy

Order your available analysis modalities by cost:

```
Tier 1 (cheapest):  Static/structural analysis
                    - Fast, deterministic, low-cost
                    - e.g., pattern matching, AST analysis,
                      metadata inspection

Tier 2 (moderate):  Dynamic/behavioral analysis
                    - Requires execution or deeper inspection
                    - e.g., runtime tracing, sandboxed execution,
                      API call analysis

Tier 3 (expensive): LLM-assisted verification
                    - Semantic understanding, complex reasoning
                    - e.g., LLM judge, code comprehension,
                      natural language analysis
```

Each tier has a **cost model** that tracks token/compute/time costs.

### 2. Assign Specialized Agents to Tiers

Each tier gets one or more **specialist agents** with domain
expertise:

- **Tier 1 agent**: Fast pattern-based analysis; produces a
  confidence score and initial classification
- **Tier 2 agent**: Deeper behavioral analysis; invoked only when
  Tier 1 confidence is below threshold
- **Tier 3 agent**: LLM-based verification for difficult cases;
  invoked only when Tier 1 + 2 produce low confidence or disagree

### 3. Implement the Meta-Orchestrator

The orchestrator is a **deterministic controller** that manages
escalation:

```python
def analyze(item):
    # Tier 1: Always run (cheapest)
    t1_result = tier1_agent.analyze(item)
    if t1_result.confidence >= HIGH_THRESHOLD:
        return t1_result  # Resolved cheaply

    # Tier 2: Escalate if Tier 1 is uncertain
    t2_result = tier2_agent.analyze(item)
    combined_confidence = aggregate(t1_result, t2_result)

    if combined_confidence >= HIGH_THRESHOLD:
        return merge(t1_result, t2_result)

    # Check inter-agent agreement
    if t1_result.label != t2_result.label:
        # Disagreement → must escalate
        pass

    # Tier 3: LLM verification for remaining hard cases
    t3_result = tier3_agent.verify(item, t1_result, t2_result)
    return merge(t1_result, t2_result, t3_result)
```

**Escalation policy parameters**:
- `HIGH_THRESHOLD`: Confidence above which no escalation is needed
  (tune on validation set; typical: 0.85–0.95)
- `DISAGREEMENT_POLICY`: Always escalate when specialists disagree
- `COST_BUDGET`: Maximum per-item cost; truncate pipeline if exceeded

### 4. Track Cost-Accuracy Trade-offs

Maintain a cost model that enables informed budget allocation:

- **Per-item cost**: Sum of tier costs for each analyzed item
- **Average cost**: Mean across all items (compare to exhaustive)
- **Accuracy by stopping tier**: What accuracy do you get if you
  stop at Tier 1? Tier 1+2? Full pipeline?
- **Escalation rate**: What fraction of items reach each tier?

Use these metrics to tune the orchestration policy — tighter
thresholds save cost but may sacrifice accuracy.

---

## Environment Caveats

- The orchestrator MUST be deterministic — do not use an LLM to
  make escalation decisions (it adds cost and non-determinism)
- Confidence calibration is critical — overconfident Tier 1 agents
  will prevent necessary escalation
- The cost model should include latency, not just token/compute cost

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Under-escalation | Tier 1 overconfident; misses hard cases | Calibrate confidence on a held-out set; audit a random sample of Tier 1 resolutions |
| Over-escalation | Threshold too tight; everything hits Tier 3 | Raise threshold; improve Tier 1/2 quality; track escalation rate and alert on spikes |
| Agent disagreement deadlock | Tier 1 and 2 always disagree | Check for systematic bias in either agent; retrain or adjust the disagreement policy |
| Cost budget exceeded | Complex batch exhausts budget | Implement priority ordering; analyze highest-risk items first within budget |

## Cross-References

- [`cost-effective-repo-exploration`](../../../../.gemini/config/skills/cost-effective-repo-exploration/SKILL.md) —
  Related: escalation-oriented search for code repository exploration
- [`trajectory-aware-eval-pruning`](../../../../.gemini/config/skills/trajectory-aware-eval-pruning/SKILL.md) —
  Related: cost reduction through intelligent subset selection

## Sources

- [Cost-Aware Hierarchical Multi-Agent Ransomware Detection and Family Attribution](https://arxiv.org/abs/2609.04820) (arXiv:2609.04820)
- Praxis source: `src:2609-04820`
