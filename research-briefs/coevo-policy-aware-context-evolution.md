# COEVO: Policy-Aware Co-Evolution of Context and Weights

> **Paper**: [COEVO: Co-Evolving Context and Parameters for Recursive Self-Improvement](https://arxiv.org/abs/2609.33398)
> **Praxis source**: src:2609-33398v1

## Why Not a Skill?

The method is an RL training recipe (GRPO with periodic prompt-scaffold
edits) that needs attention access and an RL stack. Its transferable lesson,
alternate weights and context and drive context edits by the policy's state
rather than reward alone, is already the subject of the WHALE rule in
`rules/recursive-improvement.md`; this paper adds evidence there.

---

## Core Concept

The system prompt is split into a fixed task specification and an
editable strategy scaffold. Training alternates:

1. **RL window**: GRPO updates the weights under the current prompt.
2. **Characterize** the frozen checkpoint every 5 RL steps by policy
   entropy (relative to its history) and prompt-conditioned attention per
   scaffold section (a proxy for which instructions are used).
3. **Choose an edit direction** from the entropy/attention state:
   Expand, Relax, Clarify or Consolidate.
4. **Generate 8 candidate scaffolds** with the frozen checkpoint.
5. **Select** a candidate only if it moves the policy state in the
   intended direction while keeping task performance within a tolerance
   (no numeric value is given); otherwise keep the incumbent.

The premise: the same scaffold is used differently as weights change, so
context edits should follow the policy, not just the reward.

### Key Findings

- **Math (AIME 2025, 30 problems, Average@12 / Pass@12)**, against
  fixed-prompt GRPO with Simple, Medium or Detail prompts (weights-only):
  - Qwen3.5-4B: 44.17% / 73.33% vs best fixed 40.55% / 66.67%.
  - Qwen3.5-9B: 65.56% / 93.33% vs 61.39% / 86.67% (best per metric).
  - Qwen3.8-27B: 81.67% / 100.00% vs 77.78% / 100.00%.
- **Code (LiveCodeBench v6 dev set, 100 tasks)**: Qwen3.5-4B 30.40% /
  43.33% vs best fixed 28.56% / 41.00%; Qwen3.5-9B 34.12% / 55.67% vs
  30.42% / 47.33%.
- **Ablation (Qwen3.5-4B math)**: attention-only 40.2%, entropy-only
  42.0%, reward-driven prompt co-evolution (E-SPL) 41.6%, COEVO 44.3%
  Average@12. E-SPL trained better but converged early (final entropy
  0.31 vs 0.52).
- **Limitations**: single training seed (42); AIME 2025 has 30
  problems, so a few problems move the averages; no context-only
  (no-RL) baseline; E-SPL only in the ablation; attention is a proxy,
  not shown to be causal; gains on 4B are 2–5 points.

## Relevance to Praxis

- **Supports** `rules/recursive-improvement.md` "DO: Alternate model
  weight updates and harness search": weights-only RL with any fixed
  prompt lost to alternation at every scale tested.
- **Adds a nuance**: the context step can be steered by policy state
  (entropy, instruction use) instead of reward-only search; the
  reward-driven co-evolution variant did worse here. Single seed, so
  treat as suggestive.
- COEVO's "within tolerance" selection is search-time selection; keeping
  a trained checkpoint still goes through "DO: Pass every
  self-modification through one acceptance gate", with δ from repeated
  baseline runs (this paper reports one).

> Source: COEVO: Co-Evolving Context and Parameters for Recursive Self-Improvement (arXiv:2609.33398)
