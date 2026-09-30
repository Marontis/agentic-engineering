# ResidualAuth: What Authorization State Must Language Agents Preserve under Revocable Delegation?

> **Paper**: [ResidualAuth](https://arxiv.org/abs/2609.08062)
> **Praxis source**: `src:2609-08062v1`

## Why Not a Skill?

Analysis paper — identifies what authorization state agents must preserve when delegations are revoked, but doesn't provide a complete implementation procedure. The key findings become context for the `unified-capability-gateway` and `multi-agent-federation-governance` skills.

---

## Core Concept

When an agent's delegated capabilities are revoked mid-task, what state must the agent preserve? ResidualAuth shows that the current permission set is not enough: two delegation histories can have identical current permissions and identical all-pairs reachability, yet require opposite decisions after the same direct-edge revocation.

### Key Findings

- **Current permissions are not sufficient state.** The paper proves that exponentially many future-distinct states can share one transitive closure, and bounds the state an exact monitor needs.
- **Summaries lose the decisive history.** In paired language-agent episodes across four open-weight models, a fixed 256-token summary solved 0–2 of 16 pairs and sham reads 0/16, while authenticated current-query reads solved 15–16/16.
- **Exact ledgers fit; model-written memory doesn't.** In a held-out online-memory diagnostic, exact ledger serializations fit all 128 pairs at 768 and 1,024 tokens, while model-written memories solved at most 1/128 pairs per model.
- **A hard gate closes the gap.** A hard gate reduced eight observed unauthorized effects to zero.

## Relevance to Praxis

- Directly informs the `multi-agent-federation-governance` skill's revocation protocol
- Relevant to the `unified-capability-gateway`'s capability lifecycle management
