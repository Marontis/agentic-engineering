# AutoFyn: Non-Parametric Expert Iteration for Long-Horizon Agents

> **Paper**: [AutoFyn Technical Report: Non-Parametric Expert Iteration for Long-Horizon Agent Tasks](https://arxiv.org/abs/2609.05446)
> **Praxis source**: src:2609-05446

## Why Not a Skill?

AutoFyn describes an Expert Iteration harness that updates persistent state rather than model weights, which closely overlaps with the existing `knowledge-compounding-loop` (WikiSkill) and `reference-trajectory-harness-evolution` (HarnessEvolve) skills. The core loop pattern (explore → verify → distill into persistent state → repeat) is already captured. The non-parametric framing is a useful architectural variant but not a distinct subtask procedure.

---

## Core Concept

AutoFyn adapts a frozen LLM across many rounds by updating persistent state from verified reward signals rather than model weights. Each round starts from a fresh model session; durable information is reintroduced only through explicit interfaces (persistent memory files, reports, repository state). An orchestrator explores and builds alternative approaches while a task-grounded verifier supplies objective reward for measuring progress. This reward is distilled back into persistent state, updating the effective policy.

### Key Finding

- **Primary Result**: Non-parametric expert iteration — updating persistent context rather than weights — enables a frozen model to improve across rounds on long-horizon agent tasks without fine-tuning.
- **Secondary Result**: The explicit separation between ephemeral sessions and durable state prevents catastrophic forgetting and enables clean rollback of failed iterations.

## Relevance to Praxis

- **Validates existing patterns**: Confirms the `knowledge-compounding-loop` architecture (raw → knowledge → skill layers with persistent state surviving rollbacks).
- **Frozen model + state update**: Useful design rule — frozen models with updated prompts/context can substitute for weight updates in many agent improvement scenarios.
- **Verifier-grounded selection**: The reward → state distillation loop is the same pattern as `reward-hacking-immunization` — verify before committing to persistent state.
