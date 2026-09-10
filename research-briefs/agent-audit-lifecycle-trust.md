# AgentAudit: An Open, Extensible Framework for Full-Lifecycle Trust Evaluation of AI Agents

> **Paper**: [AgentAudit](https://arxiv.org/abs/2609.09875)
> **Praxis source**: `src:2609-09875v1`

## Why Not a Skill?

Framework â€” provides an evaluation framework for agent trust across the full lifecycle (design, deployment, operation, retirement). Too broad for a subtask skill.

---

## Core Concept

Agent trust should be evaluated across the full lifecycle, not just at deployment. AgentAudit defines trust dimensions (reliability, safety, privacy, accountability) and provides evaluation protocols for each lifecycle phase.

## Relevance to Praxis

- Complements the `harness-tampering-audit` skill â€” AgentAudit covers the full lifecycle while harness-tampering focuses on detection
- Informs the `agent-sandbox.spec` template's evaluation section
