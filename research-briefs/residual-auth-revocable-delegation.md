# ResidualAuth: What Authorization State Must Language Agents Preserve under Revocable Delegation?

> **Paper**: [ResidualAuth](https://arxiv.org/abs/2609.08062)
> **Praxis source**: `src:2609-08062v1`

## Why Not a Skill?

Analysis paper â€” identifies what authorization state agents must preserve when delegations are revoked, but doesn't provide a complete implementation procedure. The key findings become context for the `unified-capability-gateway` and `multi-agent-federation-governance` skills.

---

## Core Concept

When an agent's delegated capabilities are revoked mid-task, what state must the agent preserve? ResidualAuth formalizes the concept of "residual authorization" â€” the minimum state that must survive revocation to maintain system consistency.

### Key Findings

- Naive revocation (immediately strip all capabilities) can leave the system in an inconsistent state
- The agent must preserve enough state to complete in-flight operations or cleanly abort them
- Three categories of residual state: completion obligations (must finish), cleanup obligations (must undo), and notification obligations (must inform)

## Relevance to Praxis

- Directly informs the `multi-agent-federation-governance` skill's revocation protocol
- Relevant to the `unified-capability-gateway`'s capability lifecycle management
