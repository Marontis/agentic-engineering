# Active Adaptation, Not Static Defense: Temporal Dynamics of Preventative Steering

> **Paper**: [Active Adaptation](https://arxiv.org/abs/2609.10142)
> **Praxis source**: `src:2609-10142v1`

## Why Not a Skill?

Training method â€” tied to specific adversarial fine-tuning architecture and representation engineering. Not a transferable subtask procedure.

---

## Core Concept

Safety defenses that are static (trained once) degrade over time as adversaries adapt. Active adaptation dynamically updates preventative steering vectors in response to observed attack patterns, treating safety as a temporal process rather than a fixed property.

### Key Insight

The temporal dynamics of safety matter â€” a defense that works today may not work tomorrow. Continuous adaptation outperforms periodic retraining because it responds to attack distribution shifts in real time.

## Relevance to Praxis

- Supports the `agent-sandbox-safety` rule: "DO test with evolving adversaries, not static attack sets"
- Connects to the `self-improving-red-team` skill's iterative adversarial testing
