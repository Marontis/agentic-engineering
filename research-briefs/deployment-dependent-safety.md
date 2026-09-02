# Not the Same Protector: Deployment-Dependent Protective Intervention in LLMs

> **Paper**: [Not the Same Protector: Deployment-Dependent Protective Intervention in LLMs](https://arxiv.org/abs/2608.29136)
> **Praxis source**: `src:2608-29136v1`

## Why Not a Skill?

Analysis paper â€” the key insight (safety is deployment-dependent) becomes a rule in `agent-sandbox-safety.md` rather than a standalone procedure.

---

## Core Concept

Safety behavior of LLMs changes based on deployment context. A model that's safe as a chatbot may not be safe as a coding agent, because the deployment context (system prompt, available tools, interaction pattern) activates different protective behaviors.

### Key Finding

The same model with identical safety training can:
- Refuse harmful requests in chat but comply in agentic mode
- Apply different safety thresholds depending on the system prompt
- Show different safety profiles with vs. without tool access

## Relevance to Praxis

- Key insight captured as a rule in gent-sandbox-safety.md: "DON'T assume safety transfers across deployment contexts"
- Informs the gent-sandbox.spec template â€” sandbox design must account for deployment-specific safety profiles
