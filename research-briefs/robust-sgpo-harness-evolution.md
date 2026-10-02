# RobustSGPO: Search-Space Control for Agent Harness Evolution

> **Source**: Zhao, Shi, Zhou et al. (Kuaishou), arXiv:2609.09646 (v2, 20 Sep 2026)
> **Status**: Research Brief — search-space controls for semantic-gradient harness evolution, one industrial workflow
> **Praxis source**: `src:2609-09646v1`

## Why Not a Skill?

The controls (edit requests, exact-target checks, predefined add/remove operations, a category archive) are tightly coupled to the SGPO/AgentX loop and were evaluated on one brainstorming workflow. The general lessons are recorded as evidence in `rules/skill-system-design.md` ("DO: Bound the search space of harness self-evolution").

## Core Concept

SGPO evolves a multi-agent harness from trace failures: it derives a natural-language loss and "semantic gradient", proposes an edit to an agent specification, replays the same tasks on old and new versions, and accepts or rolls back. The model, rubrics, verifiers and traces stay fixed. RobustSGPO makes three choices explicit:

1. **What to change**: a controller picks the edit scope (one agent, several existing agents, or structural add/remove/routing), the operation and the target agents before any text is generated. Permission can be scheduled periodically across these levels.
2. **Construct and check the patch**: an exact-target check rejects edits that touch other agents than requested; agent additions and removals are built by predefined code rather than free-form generation.
3. **Where to continue from**: a MAP-Elites-style archive keeps the best valid snapshot per scope–operation category as alternative parents. Every descendant must still beat the current incumbent to be admitted.

Admission requires a mean validation gain above ε = 0.05 over three paired replays plus passing safety checks; ties keep the incumbent.

## Key Findings

Setup: AgentX brainstorming workflow, 120 tasks (60 optimization / 30 validation / 30 test), five paired seeds, 95 runs and 7,350 candidate attempts; proposals capped at **120 changed lines and 6,000 added characters**. Scores are held-out test quality on a 0–5 rubric-judged scale.

- **Permission scheduling beats fixed maximum permission**: periodic scheduling that widens scope (one agent → existing agents → structural, repeating) finished at **4.34** vs **4.06** for fixed maximum (structural) permission, +0.28. Fixed permissions scored 3.85 (one agent), 4.07 (existing agents) and 4.06 (structural). Fixed permission led early; final rankings differed from early ones.
- **Broader permission alone did not help**: the paper states that broader permissions need not yield more valid edits or higher quality. Structured edit construction raised structural validity from 48.9% to 77.8%.
- **Cumulative controls add up**: round-30 test score rose from 3.82 (SGPO) to 4.30 (RobustSGPO); held-out completion rose from 60.0% to 80.0% (18/30 to 24/30), and cross-agent completion from 7/15 to 11/15.
- **At equal token cost** (20M tokens) the gain is smaller: 4.14 vs 3.77; the archive's overhead shrinks RobustSGPO's margin over Structured Search from 0.10 to 0.04.
- **Retention vs adaptation**: after a task shift, category retention had the smallest source-task loss (−0.15 vs −0.31 to −0.33), while random retention reached the highest destination score (4.18).

The paper does **not** show that unconstrained evolution is worse than no evolution; an earlier version of this brief said so, and that claim has been removed. Its comparisons are between controlled and less-controlled search, all with replay admission and safety checks.

## Relevance to Praxis

- Evidence for `rules/skill-system-design.md` "DO: Bound the search space of harness self-evolution": control *how* edits are chosen and built, not only how much is permitted.
- Admission (incumbent-relative gain over paired replays) is search-time selection; keeping a harness still defers to `rules/recursive-improvement.md` "DO: Pass every self-modification through one acceptance gate".
- Complements [`reference-trajectory-harness-evolution`](../skills/reference-trajectory-harness-evolution/SKILL.md) and [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md); related to [`stable-skill-evolution`](../skills/stable-skill-evolution/SKILL.md).
- Caveats: one workflow, one company's system, rubric-judged quality, no comparison with external harness-evolution systems on shared benchmarks.

> Source: Zhao et al., "RobustSGPO: Search-Space Control for Agent Harness Evolution" (arXiv:2609.09646)
