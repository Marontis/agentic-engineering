# A Structured Debate-Mixture-of-Agents Framework for Complex Clinical Diagnostic Decision Support

> **Paper**: [A Structured Debate-Mixture-of-Agents Framework for Complex Clinical Diagnostic Decision Support](https://arxiv.org/abs/2609.05069)
> **Praxis source**: `src:2609-05069v1`
> **Primary topic**: Agent Self-Improvement & Harness Engineering

## Why Not a Skill?

This paper applies multi-agent patterns to a domain-specific use case. While the multi-agent architecture has general elements, the procedure is heavily tied to the specific application domain and does not generalize as a standalone agent engineering skill.

---

## Core Concept

Large language models (LLMs) show potential for medical tasks, but their single-turn question-answer format does not reflect how clinical diagnosis is performed in practice. As a result, they remain limited in complex diagnostic settings. We developed Debate-Mixture-of-Agents (DMoA), a novel multi-agent framework that structures role-based interaction to support iterative diagnostic reasoning. Base models and DMoA were evaluated on 297 rare disease cases and 1,719 challenging cases. Across both datasets, DMoA improved most likely diagnosis accuracy by 10.21 percentage points and safety rate by 11.36 percentage points over GPT-4o baseline. Ablation experiments showed that the gains were not simply due to the use of more models or longer outputs, but also reflected the contribution of the structured workflow. Further analyses examined how framework design, base model choice, and token budget affected performance. DMoA performed better with a 4*2 structure, stronger base models, and a larger token budget. These findings demonstrate the potential of DMoA for clinical tasks and suggest further investigation of multi-agent frameworks.

### Key Findings

- **Primary Result**: Across both datasets, DMoA improved most likely diagnosis accuracy by 10.21 percentage points and safety rate by 11.36 percentage points over GPT-4o baseline.

## Relevance to Praxis

- Relevant to agent self-improvement loops and harness engineering.
