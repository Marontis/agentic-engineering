# SelfOp: Self-Improving Security Agents via Skill Optimization

> **Source**: Ullah, Kaya, Kruegel, Vigna, Stringhini, arXiv:2609.22792, Sep 2026
> **Status**: Research Brief — textual-gradient skill optimizer evaluated on CyberGym PoC generation

## Why Not a Skill?

SelfOp is a fourth prompt/skill optimizer alongside NPO, ESPO and CASD, which the 2026-09-28 deconfliction report (H6) already flags as giving opposite procedures for the same job. Its acceptance step is cross-task consensus filtering with **validation-free** stopping and no security constraint on the edits, which conflicts with the strict acceptance gate in H7. Adding it as a skill would widen both conflicts. Its useful, distinct findings (chain-rule error attribution, consensus thresholds, batch-size sensitivity, cross-model transfer) are recorded here as evidence for resolving H6/H7/M7.

## Core Concept

SelfOp treats the agent's SKILL.md and reference documents as the only learnable parameters (model weights and harness frozen) and runs a textual "backward pass" per failed task in three stages:

1. **Score analysis**: which evaluation criteria failed.
2. **Skill-blind trajectory analysis**: what the agent did wrong, reconstructed against task metadata (bug reports, developer patches, sanitizer traces).
3. **Skill-aware orchestration analysis**: which missing or weak skill instruction explains that behaviour.

Per-task findings are then accumulated across the batch: cluster into themes, rank by 0.4 × support + 0.6 × outcome weight, keep improvements with ≥ 20% support and strengths with ≥ 30%, and classify each surviving improvement as **hard** (missing content, may add text) or **soft** (already covered, may only edit the cited instruction). Stopping uses a novelty signal on hard gradients (stop when the z-score stays below 1.0 for three consecutive steps) instead of held-out validation runs.

## Key Findings

Setup: CyberGym vulnerability PoC generation (OSS-Fuzz), Codex with GPT-5.4-mini as agent and optimizer; 224 train, 40 validation, 80 test tasks (about 23% of CyberGym, for cost reasons).

- **Gains**: GPT-5.4-mini 38% → 55% test pass@1; GPT-5.4 49% → 67.5% (+18.5 points).
- **Transfer within a model family works both ways**: GPT-5.4's optimized skill lifts GPT-5.4-mini to 65% (above mini's own 55%); mini's skill lifts GPT-5.4 to 62%.
- **Three-stage attribution beats per-task single-stage analysis**: 48% vs 39% test, reaching 50% validation with 128 examples instead of 224.
- **Looser consensus thresholds generalize better**: loose 48% test, slightly strict 42%, strict 35%.
- **Batch size matters a lot**: batch 16 gave 55% test; doubling to 32 dropped it to 35%, because diverse vulnerability types dilute cross-task consensus.
- **Hard/soft annotation stops skill bloat**: without accumulation the skill grew from 126 to 2,677 words with no plateau; with annotation it stopped growing (3,808 words at steps 10 and 11) once all themes were soft.
- **Validation-free stopping picked a better checkpoint than validation did**: the novelty detector chose step 8 (55% test); validation-based selection chose step 11 (51%); the oracle best was 56.2% at step 12. Note the validation set had only 40 tasks, and repeating the test evaluation moved accuracy by ±2–3 points.
- **Metadata supervision carries much of the gain**: binary pass/fail alone 36% → 45%; metadata adds a further 11 points.
- Cost: a full CyberGym pass is about $3,000 in API credits; 80-task validation alone about $1,400.

## Relevance to Praxis

- **H6 (three prompt optimizers)**: SelfOp sides with ESPO ([`error-structured-prompt-optimization`](../skills/error-structured-prompt-optimization/SKILL.md)) on "cluster failures across the batch before editing" and against reflecting on single errors, but uses loose thresholds and small batches. It supports a decision rule where cross-task clustering is the default when rich failure metadata exists.
- **H7 (acceptance gates)**: SelfOp has no regression gate and no safety constraints on self-modification. For a security agent in particular, any SelfOp-style loop must still pass the frozen acceptance gate and negative security testbed in [`recursive-improvement`](../rules/recursive-improvement.md) ("DO: Evaluate evolved instructions against immutable, held-out negative security testbeds"). Validation-free stopping is a checkpoint-selection trick, not an acceptance gate.
- **M7 (transfer vs per-model benchmarking)**: evidence that skill transfer holds across tiers of one family (GPT-5.4 ↔ GPT-5.4-mini), consistent with [`skill-system-design`](../rules/skill-system-design.md) "DO: Evolve skills with stronger models, deploy to weaker ones". It says nothing about cross-family transfer.
- Related: [`stable-skill-evolution`](../skills/stable-skill-evolution/SKILL.md) (momentum against oscillation), [`dense-rubric-skill-evolution`](../skills/dense-rubric-skill-evolution/SKILL.md), [`cve-history-executable-detection`](../skills/cve-history-executable-detection/SKILL.md) (security-agent domain).

> Source: Ullah et al., "SelfOp: An Optimization Algorithm for Self-Improving Security Agents" (arXiv:2609.22792)
