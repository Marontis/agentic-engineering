# World Model Science: Self-Organized Criticality, Weak Chaos, and Metastable Belief Dynamics in Long-Horizon LLM Agents

> **Paper**: [World Model Science: Self-Organized Criticality, Weak Chaos, and Metastable Belief Dynamics in Long-Horizon LLM Agents](https://arxiv.org/abs/2609.17419)
> **Praxis source**: `src:2609-17419v1`
> **Primary topic**: Agent Self-Improvement & Failure Dynamics

## Why Not a Skill?

This paper presents an empirical, theoretical, and dynamical systems diagnostic methodology for analyzing failure cascades in long-horizon LLM agent world models. It provides foundational scientific insights into agent failure regimes rather than an operational runtime procedure.

---

## Core Concept

In extended autonomous executions, agents must track world state across lengthy chains of observations, tool calls, and internal hypotheses. Evaluating agents solely by final task reward obscures how internal state representations degrade over time.

Song and Cai evaluate long-horizon trajectories across 22 experimental setups—spanning complex puzzle solving, multi-step tool use, embodied simulation, multi-hop retrieval, and cellular automata—through three physical and dynamical lenses:

```
               Agent Trajectory Evolution
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
[Self-Organized       [Weak Chaos &      [Metastable Belief
  Criticality]       Bounded Divergence]     Dynamics]
 ├── Stress accumulation ├── Error sequences  ├── Discrete belief
 │   in hidden states    │   exhibit long     │   basins
 └── Error avalanches    │   memory           └── Metastable
     triggered by local  └── Divergence is        transitions under
     misalignment            bounded, not         environmental
                             exponential          stress
```

### Key Findings

- **Local Validity vs. Global Collapse**: Agents routinely continue executing locally valid, syntactically correct tool actions long after their internal model of the global environment state has diverged from ground truth.
- **Stress Accumulation and Error Avalanches**: Uncorrected minor inconsistencies accumulate latent "stress" in the agent's context. When a threshold is breached, the agent experiences an abrupt cascade of multi-step failures ("error avalanche").
- **Long Memory in Error Propagation**: Error propagation does not follow simple memoryless Markov dynamics; early unverified assumptions exert strong gravitational pull on subsequent reasoning paths.
- **Metastable Belief Basins**: Agents do not drift continuously; rather, their belief states reside in discrete metastable basins. Switching between basins requires significant contradictory evidence or explicit prompt resets.
- **Absence of Universal Power Laws**: The authors refute claims that agent failure cascades follow universal scale-invariant critical power laws; error avalanche distributions are determined by the dependency graph depth of the underlying task.

## Relevance to Praxis

- Provides empirical backing for why periodic external verification gates and clean checkpoint rollbacks are essential.
- Highlights the critical risk of "silent drift" where tool calls appear syntactically valid but operate on fictitious state.
- Deepens the foundational theory behind [`neural-invariant-failure-diagnosis`](../skills/neural-invariant-failure-diagnosis/SKILL.md) and [`black-box-trajectory-risk-monitoring`](../skills/black-box-trajectory-risk-monitoring/SKILL.md).
