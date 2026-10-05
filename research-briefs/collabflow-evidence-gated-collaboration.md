# CollabFlow: Evidence-Gated Messages and a Trained Team Director

> **Paper**: [CollabFlow: Recursive Self-Improvement of Agent Collaboration](https://arxiv.org/abs/2609.38662)
> **Authors**: Huang, Zhang, Zhang et al. (CUHK-Shenzhen, Fudan, Oxford)
> **Praxis source**: src:2609-38662v1
> **Status**: Research Brief — method with ablations

## Why Not a Skill?

The full method trains a team-construction policy with a flow-based
objective (collaborative trajectory balance), which needs an RL training
setup most projects will not build. The part that transfers without
training, the evidence gate on inter-agent messages, is one rule of thumb
and fits existing rule entries better than a new skill.

---

## Core Concept

Three pieces, around a frozen executor model (Qwen3.5-9B by default):

1. **Collab-Director**: a trainable policy builds a team (a graph of agents
   with protocol-labelled edges) from fixed agent profiles. Only the
   director retrains between rounds.
2. **Evidence-conditioned communication**: each candidate answer carries an
   evidence level: 2 if it passed an executable check, 1 if it has retrieval
   support, 0 otherwise. When agent i messages agent j, the gap
   Δ = level_i − level_j decides: Δ > κ, j adopts i's answer; Δ < −κ, j keeps
   its own; |Δ| ≤ κ, j makes one bounded revision call. With κ = 1, a
   two-level gap means adoption and a one-level gap means revision.
3. **Collaborative trajectory balance**: the director is trained to sample
   teams in proportion to reward, crediting each distinct team once however
   it was built, which keeps team diversity instead of collapsing on a few.

## Key Findings

- Averages over 6 in-distribution and 6 out-of-distribution benchmarks (QA,
  math, medical QA, ALFWorld, WebShop, code): 75.94 ± 1.27 IID and 69.92 ±
  1.00 OOD on the primary metric, five runs, gains significant at
  p < 10⁻² (Welch's t-test).
- **Ablations** (Table 2, IID datasets, full method → variant):
  - Removing the evidence gate: AIME 76.67 → 63.33, ALFWorld 97.66 → 92.19,
    HotpotQA EM 63.28 → 57.03, MBPP+ 85.16 → 81.25.
  - Always revising instead of gating: AIME 76.67 → 56.67, HotpotQA 63.28 →
    53.91, MBPP+ 85.16 → 75.78. Unconditional revision was worse than no
    gate.
  - Removing communication entirely: AIME 76.67 → 50.00, ALFWorld 97.66 →
    78.91.
- The paper reports that each removed component cost more out of
  distribution than in distribution.
- Weaker executors gained more (Pearson r = −0.96 in distribution), narrowing
  the spread across seven executors from 23.3 to 9.3 points.
- Team diversity: 26 distinct successful paths vs at most 15 for GRPO/PPO
  baselines.

## Relevance to Praxis

- Evidence for "DO: Dynamically calibrate consensus entropy and weight peer
  influence by evidence grounding in multi-agent debate"
  (`rules/recursive-improvement.md`): weighting a message by how it is
  grounded (executed check > retrieval > assertion) beat both ungated
  exchange and always-revise. See the proposed evidence addition in the
  2026-10-01 batch report.
- Concrete rule for inter-agent messages: let a verified answer override an
  unverified one; when evidence is comparable, revise once instead of copying
  or ignoring. Compare [`evidence-gated-adversarial-deliberation`](../skills/evidence-gated-adversarial-deliberation/SKILL.md),
  which gates *released claims* by citation validity.
- Depends on checkable evidence existing (tests, retrieval); the paper notes
  results depend on that and on fixed executor capability.
- The director's training loop is not a harness self-modification gate;
  if you adopt the "recursive" part and keep evolved teams or skills, they
  still go through "DO: Pass every self-modification through one acceptance
  gate" (`rules/recursive-improvement.md`).

> Source: Huang et al., "CollabFlow: Recursive Self-Improvement of Agent
> Collaboration" (arXiv:2609.38662)
