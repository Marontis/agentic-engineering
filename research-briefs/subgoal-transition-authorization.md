# Runtime Authorization of Self-Generated Subgoals

> **Paper**: [Runtime Authorization of Self-Generated Subgoals in Long-Horizon Tool-Using AI Agents](https://arxiv.org/abs/2610.04975)
> **Praxis source**: src:2610-04975

## Why Not a Skill?

A formal-methods paper: a root-task contract, transition witnesses, theorems,
and a bounded reference implementation. Its central lesson (local per-call
allowlists are insufficient once agents create their own subgoals) is
already reflected in existing authorization skills, and the mechanism is too
specialized to restate as a general procedure.

---

## Core Concept

Long-horizon agents decompose tasks into self-generated subgoals. A per-call
allowlist can approve every individual operation while the trajectory drifts
away from the root task. The paper authorizes **transitions** between
subgoals against a root-task contract, using history (trace prefixes),
typed resources, freshness, and explicit join evidence for delegated and
parallel branches, with effect reservation and commit, receipts for audit,
and fail-closed behavior. It proves root-task safety, conditional preservation
of root-task success, and that a memoryless local allowlist is insufficient
(Lemma B3).

### Key Finding

- **Drift blocked without hurting benign runs**: on 96 matched cases across
  25 structural schemas (24 of 48 templates mapped to identifiers from four
  public benchmark artifacts), the full mechanism committed zero forbidden
  states in 48 drifted cases and completed all 48 benign counterparts.
- **History alone is not enough**: a history-aware continuation comparator
  blocked every modeled bad trace prefix, yet committed all operations in 11
  cases whose violations lay in typed resources, freshness, or join evidence
  outside its trace projection.
- **Implementation check**: an executable model explored 340 states and 419
  transitions; two upstream runtime paths executed 258 native dispatches
  across 32 cases with every decision and receipt chain matching. The
  authors state the scale study characterizes a finite profile, not
  production scalability.

## Relevance to Praxis

- **Authorize subgoal transitions, not just calls**: supports the existing
  [`runtime-resource-authorization-bounds`](../skills/runtime-resource-authorization-bounds/SKILL.md)
  and [`authorization-closure-repair`](../skills/authorization-closure-repair/SKILL.md)
  skills; trajectory-level checks need resource types and freshness, not
  only the sequence of tool names.
- **Fail closed with receipts**: every commit carries an auditable receipt,
  which pairs with [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md).
