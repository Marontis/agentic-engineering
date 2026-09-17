# BusMA: A Bus Communication Substrate for Multi-Agent Systems

> **Paper**: [BusMA: A Bus Communication Substrate for Multi-Agent Systems](https://arxiv.org/abs/2609.15054)
> **Praxis source**: `src:2609-15054v1`
> **Primary topic**: Agent Architecture, Protocols & Interoperability

## Why Not a Skill?

BusMA defines a system-level communication substrate and topology design for multi-agent architectures. It establishes the networking and messaging backbone rather than an isolated subtask procedure performed by an individual agent.

---

## Core Concept

Multi-agent (MA) systems are widely used for complex tasks requiring tool coordination and multi-source synthesis. Most existing architectures use one of two topologies:
1. **Hierarchical Manager-Worker (HMW)**: Strict top-down hierarchy where workers report only to managers; workers cannot communicate with peers, creating a decision bottleneck.
2. **Router-based Message Passing (RMP)**: A central router routes messages between arbitrary agents; misrouted messages or router hallucinations propagate cascading errors throughout the system.

**BusMA** replaces both models with a shared broadcast/multicast **Bus Substrate** inspired by computer hardware buses:

```
┌─────────────────────────────────────────────────────────────┐
│                       Shared Bus                           │
│  ├── Message Routing & Topic Dispatch                      │
│  ├── Shared Memory Buffer & Consensus State                 │
│  └── Agent Registration Directory                           │
└──────▲─────────────────▲─────────────────▲─────────────────▲┘
       │                 │                 │                 │
┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
│ Chair Agent │   │ Worker 1    │   │ Worker 2    │   │ Worker 3    │
│(Convergence)│   │ (Tools/Mem) │   │ (Tools/Mem) │   │ (Tools/Mem) │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
```

### Four Explicit Communication Intents

To prevent channel saturation and unstructured conversational chatter, every message posted to the Bus must declare one of four formal semantic intents:

1. **`discussion`**: Open hypothesis sharing and cooperative reasoning across peers.
2. **`challenge`**: Explicit adversarial counter-arguments, falsification attempts, or disagreement flags.
3. **`guidance`**: Directional recommendations or procedural steering from domain specialists.
4. **`request for explanation`**: Formal requests for derivation steps, data provenance, or intermediate evidence.

A specialized **Chair Agent** observes the bus memory, identifies deadlock or circular debate, and arbitrates convergence when sufficient consensus is reached.

### Key Findings

- **Consistent Superiority**: Evaluated across 13 diverse benchmarks spanning visual reasoning, mathematics, and multi-hop knowledge retrieval using frontier LLMs.
- **Outperforms Hierarchical and Router Architectures**: BusMA consistently surpasses both HMW and RMP baselines by eliminating router bottlenecks while allowing targeted peer consultation.
- **Intent Regularization**: Structuring inter-agent messages with explicit intent types reduces uninformative turns by over 40% compared to free-form group chat.

## Relevance to Praxis

- Directly informs multi-agent protocol design and message envelope standards.
- Integrates with [`nlip-agent-message-envelope`](../skills/nlip-agent-message-envelope/SKILL.md) and [`debate-consensus-memory-calibration`](../skills/debate-consensus-memory-calibration/SKILL.md).
- Provides quantitative decision criteria for multi-agent coordination rules.
