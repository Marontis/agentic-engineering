# TRACE: Training Reasoning Agents for Causal Exploration with Synthesized Rewards

> **Paper**: [TRACE](https://arxiv.org/abs/2609.10315)
> **Praxis source**: `src:2609-10315v1`

## Why Not a Skill?

Training method â€” RL with synthesized rewards for causal reasoning. Tied to specific model training architecture.

---

## Core Concept

Trains reasoning agents to explore causal relationships using synthesized reward signals. Instead of requiring human-labeled causal graphs, the system generates reward signals from the agent's own causal interventions â€” if the agent's predicted intervention effect matches the observed effect, it receives positive reward.

### Key Insight

Causal reasoning can be trained without causal labels if the agent can perform interventions and observe outcomes. The environment itself becomes the reward oracle.

## Relevance to Praxis

- The "environment as reward oracle" principle connects to the `self-verification-elicitation` skill â€” reality-grounded verification
- Relevant to how agents could self-improve their causal understanding during tool use
