# AutoFyn: Non-Parametric Expert Iteration for Long-Horizon Agents

> **Paper**: [AutoFyn Technical Report: Non-Parametric Expert Iteration for Long-Horizon Agent Tasks](https://arxiv.org/abs/2609.05446)
> **Praxis source**: src:2609-05446

## Why Not a Skill?

AutoFyn describes an Expert Iteration harness that updates persistent state rather than model weights, which closely overlaps with the existing `knowledge-compounding-loop` (WikiSkill) and `reference-trajectory-harness-evolution` (HarnessEvolve) skills. The core loop pattern (explore → verify → distill into persistent state → repeat) is already captured. The non-parametric framing is a useful architectural variant but not a distinct subtask procedure.

---

## Core Concept

AutoFyn adapts a frozen LLM across many rounds by updating persistent state from verified reward signals rather than model weights. Each round starts from a fresh model session; durable information is reintroduced only through explicit interfaces (persistent memory files, reports, repository state). An orchestrator explores and builds alternative approaches while a task-grounded verifier supplies objective reward for measuring progress. This reward is distilled back into persistent state, updating the effective policy.

### Key Finding

- **Primary Result**: Non-parametric expert iteration — updating persistent context rather than weights — let frozen models improve across rounds **where a task-grounded verifier supplies an objective reward**. Demonstrations: on the six 2026 IMO problems, every model with room to improve scored higher under AutoFyn than in its provider's own coding agent; AutoFyn built the top-ranked agent on Spider 2.0 dbt; it produced 16 maintainer-confirmed vulnerability advisories. This is a technical report with demonstrations in three domains, not a controlled comparison across many tasks.
- **Design property (not a measured result)**: each round starts from a fresh session and durable information re-enters only through explicit interfaces (memory files, reports, repository state). That makes state inspectable and revertible, but the report does not measure forgetting or rollback.

## Relevance to Praxis

- **Validates existing patterns**: Confirms the `knowledge-compounding-loop` architecture (raw → knowledge → skill layers with persistent state surviving rollbacks).
- **Frozen model + state update**: frozen models with updated persistent context can substitute for weight updates **when weights are not trainable and an objective verifier exists**; where weights are trainable, see `rules/recursive-improvement.md` "DO: Alternate model weight updates and harness search" (WHALE). Persistent-state updates still pass "DO: Pass every self-modification through one acceptance gate".
- **Verifier-grounded selection**: The reward → state distillation loop is the same pattern as `reward-hacking-immunization` — verify before committing to persistent state.
