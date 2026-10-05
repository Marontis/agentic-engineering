# MiniRep: Reputation-Based Aggregation for Multi-Agent Debate

> **Paper**: [MiniRep: Robust Reputation-Based Aggregation for Multi-Agent Debate](https://arxiv.org/abs/2609.39297)
> **Praxis source**: src:2609-39297v1

## Why Not a Skill?

MiniRep is a specific aggregator with trained components (an MLP behaviour
detector, a 1.5B semantic verifier) evaluated on three 100-task datasets.
Its gains are large on one dataset and small or negative on clean tasks
elsewhere. The design lessons are useful context for the debate rules in
`rules/multi-agent-coordination.md`; the evidence is not strong enough for
a standalone procedure.

---

## Core Concept

Reputation from past tasks can be gamed: an agent builds a good record,
then attacks. MiniRep combines history with **current-task signals checked
before aggregation**:

1. **Response analyzer**: scores each proposal by agreement with others
   plus a semantic verifier; a behaviour detector flags instruction
   override and unexpected changes between rounds; unparseable or flagged
   proposals are blocked.
2. **Reputation-aware aggregator**: adjusts historical weights with
   current quality and risk, **limits the influence of clone groups**
   (agents running the same underlying model do not count as
   independent), selects k = 7 of n = 10 agents, and takes a
   reputation-weighted answer.
3. **State updater**: keeps long-term quality, recent quality and
   suspicious behaviour as separate records for the next task; it cannot
   change the current answer.

Threat model: up to f = 3 of 10 agents adversarial, including agents that
build reputation before attacking (on-off and adaptive attacks); seven
attack types; 112 attack conditions per dataset.

### Key Findings

- **MATH (levels 4–5)**: attacked accuracy 61.95% vs 54.37% for the best
  baseline (Beta reputation); clean accuracy 66.75% vs 59.25% for uniform
  majority. With 7 strong + 3 weak agents, MiniRep won all 28 attack
  conditions.
- **Other datasets, small or negative**: GoEmotions attacked 21.16% vs
  19.59%; HumanEval Pro attacked 78.15% vs 77.92%. Clean costs: GoEmotions
  F1 34.42% vs 36.42% and HumanEval Pro 77.75% vs 79.50% for uniform
  majority.
- **Reputation-building attacks** (HumanEval Pro, 8 conditions): better
  than the best baseline in 5, tied in 2, by 1–3 points.
- **When top-ranked agents are corrupted**: MATH diverse collusion 73% vs
  55% (Babylon); MATH boundary-value attack 69% vs 54%.
- **Limitations**: three datasets of 100 tasks; clone-group mapping
  assumed known; adversary capped at 3 of 10; robustness costs 1.75–2.00
  points on two of three clean tasks.

## Relevance to Praxis

- **Supports** `rules/multi-agent-coordination.md` "DON'T: Rely on group
  size or majority vote to dilute adversarial agents": uniform majority
  failed under coordinated attacks by 3 of 10 agents, and the fix was to
  limit untrusted influence (blocking, weighting, clone-group caps), not to
  add members.
- **Supports** "DO: Use heterogeneous, cross-family rosters for
  deliberation and joint verification": same-model clones are capped
  rather than counted as independent votes.
- **Caveat for** "DO: Preserve minority viewpoints in agent voting and
  consensus": down-weighting dissent cost clean accuracy on two of three
  datasets, so measure clean and attacked accuracy separately before
  deploying a robust aggregator.

> Source: MiniRep: Robust Reputation-Based Aggregation for Multi-Agent Debate (arXiv:2609.39297)
