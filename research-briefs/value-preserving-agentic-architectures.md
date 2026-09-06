# Value-Preserving Architectures for Agentic AI Systems

> **Paper**: [Value-Preserving Architectures for Agentic AI Systems](https://arxiv.org/abs/2609.03920)  
> **Praxis source**: `src:2609-03920`

## Why Not a Skill?

This paper introduces macro-architectural design patterns for aligning multi-agent systems (MAS) with human-centered values (privacy, pluralism, fairness, and safety). Rather than defining a single procedural algorithm, it establishes system topologies and coordination mechanisms that structure multi-agent interaction. Its core topology patterns—specifically the dedicated guard-agent pattern—are codified into `rules/agent-sandbox-safety.md`.

---

## Core Concept

Traditional software engineering focuses on functional correctness, but multi-agent LLM systems exhibit emergent behaviors that can inadvertently compromise human-centered values. In MAS, high-level architectural choices—such as coordination topology, information visibility, and task routing—exert a dominant influence on whether the collective behaves ethically, safely, and equitably.

The authors formulate a taxonomy of **value-preserving architectural patterns**:

```
                       Multi-Agent System Topologies
                                     │
      ┌──────────────────────────────┼──────────────────────────────┐
      ▼                              ▼                              ▼
Privacy-Aware Pattern       Pluralistic Pattern            Guard-Agent Pattern
(Federated Topology)       (Distributed Topology)         (Supervisory Topology)
Local context preservation, Multi-perspective voting,    Dedicated monitor agents
zero ambient data sharing    preventing monoculture bias   for fairness & safety gates
```

### 1. Privacy-Aware Architecture (Federated Topology)
- Partitions agent roles such that private user data never leaves local boundaries.
- Uses localized agent instances that extract minimal semantic summaries or abstract parameters before communicating with orchestrator agents.
- Eliminates ambient authority and unintended cross-tenant data leakage in enterprise agent swarms.

### 2. Distributed Architecture (Pluralism & Diversity)
- Deploys ensembles of specialized agents with heterogeneous base models, prompting perspectives, or demographic context priors.
- Prevents majority skew and algorithmic monoculture during consensus-seeking or evaluation phases.
- Complements debate and voting mechanisms by structurally enforcing cognitive divergence.

### 3. Guard-Agent Architecture (Fairness & Safety Auditing)
- Decouples task execution from safety and fairness monitoring by introducing dedicated **Guard Agents**.
- Guard agents inspect intermediate agent communications, tool arguments, and proposed actions out-of-band before state transitions are committed.
- Isolates audit responsibilities from worker agents who may suffer from context saturation or prompt injection.

---

## Relevance to Praxis

- **System Topologies**: Praxis multi-agent workflows (intake, extraction, verification, skill synthesis) benefit from decoupling task synthesis from safety gating via explicit guard-agent topologies.
- **Architectural Rules**: Demonstrates that safety and alignment cannot be solved solely via prompt engineering; topological constraints and boundary enforcement provide superior deterministic guarantees.
