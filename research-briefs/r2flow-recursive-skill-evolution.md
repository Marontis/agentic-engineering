# R2 Flow: Evidence-Gated Recursive Skill Evolution

> **Paper**: [R2 Flow: Recursive Self-Improvement via Recursive Skill Evolution](https://arxiv.org/abs/2609.33867)
> **Praxis source**: src:2609-33867v1

## Why Not a Skill?

The full method depends on a GFlowNet-style training objective (R2TB) over
a shared-state orchestration graph, which is a research system rather than
a procedure that transfers across projects. The transferable parts (decide
library edits on credible bounds rather than point estimates, separate how
often a skill is used from whether it helps, defer when evidence is thin)
are recorded here as design guidance next to the existing skill-lifecycle
skills.

---

## Core Concept

Each phase trains a flow policy over a skill-orchestration graph with a
frozen executor (Qwen3.5-9B), then reads two quantities per skill:

- **Flow share**: how much reward passes through the skill (usage).
- **Signed utility**: whether the skill helps or hurts when used.

Independent verifiers label a budgeted sample of skill invocations (the
budget follows flow share), and hierarchical Beta posteriors pool that
evidence per context. Library operations (defer, split, refine, prune,
generate) are decided on **credible bounds**: wide intervals mean defer; a
skill is pruned only when confirmed weak and non-positive in utility. A
change is committed only after paired rollouts are non-inferior on
success, reward, tokens and latency, and phase gains are measured on
held-out verified scores. The graph merges reorderings of independent
steps into one state so their evidence pools.

### Key Findings

- **Against SkillOpt (strongest skill-evolution baseline), 5 runs**:
  HotpotQA EM 91.09 vs 88.12; AIME 2026 76.00 vs 66.67; ALFWorld 88.75
  vs 85.00. Held-out OOD: MuSiQue 85.31 vs 80.94; SWE-bench resolved
  44.22 vs 40.62; WebShop 89.53 vs 85.78.
- **Edit precision**: 33 of 37 committed edits raised held-out verified
  accuracy (0.89); 11 of 12 deliberately injected harmful skills were
  pruned by phase 8.
- **Executor transfer**: the evolved library raised six frozen executors
  by 15.70–24.64 points on average.
- **Ablations (IID)**: removing shared states cost 7.31 points, phase-state
  retention 5.0, the learned backward policy 4.52, signed utility 3.61,
  credible bounds (using posterior means instead) 2.23.
- **Limitations**: needs independent verifiers, expensive where no cheap
  oracle exists; 8 phases only, drift beyond that untested; sparse
  contexts fall back to skill-level priors; the utility discount is
  hand-tuned.

## Relevance to Praxis

- **Agrees with the acceptance gate** (`rules/recursive-improvement.md`
  "DO: Pass every self-modification through one acceptance gate"): paired
  non-inferiority checks and held-out verified scores are a form of it.
  Systems adopting R2 Flow's operations should still estimate δ from
  repeated baseline runs and keep the negative security testbed strict.
- **Supports** "DON'T: Accept modifications based on aggregate metrics
  alone": signed utility and credible bounds outperformed point estimates.
- The 11-of-12 harmful-skill pruning result is relevant to
  [`skill-evolution-defense`](../skills/skill-evolution-defense/SKILL.md),
  but injected skills were the authors' own, not adaptive attacks.
- Related procedures: [`controlled-skill-lifecycle-management`](../skills/controlled-skill-lifecycle-management/SKILL.md),
  [`attribution-guided-skill-graph-update`](../skills/attribution-guided-skill-graph-update/SKILL.md).

> Source: R2 Flow: Recursive Self-Improvement via Recursive Skill Evolution (arXiv:2609.33867)
