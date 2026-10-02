# The Wisdom of Artificial Deliberative Crowds

> **Source**: Barrera-Lemarchand, Sigman & Navajas, arXiv:2609.22497, Sep 2026
> **Status**: Research Brief — controlled empirical study (4 domains, heterogeneous vs clone groups)

## Why Not a Skill?

The protocol is short and taken from human-crowd research (independent answer, short chat to consensus, private revision). The paper's contribution is the evidence of **when** it works: only with models from different families. That is a decision criterion for multi-agent aggregation, so it goes into the rules, not a new procedure.

## Core Concept

Three-stage deliberation, run with small models from three providers (Claude Haiku 4.5, GPT-5-nano, Gemini 3.1 Flash Lite):

1. **Stage i1**: each model answers independently with up to 200 tokens of reasoning (250 in Study 4).
2. **Stage c**: groups of three chat in short messages (7 words on average), at most ten rounds, one message per model per round in random order, until they agree.
3. **Stage i2**: each model sees its original answer plus the transcript and gives a private final answer.

Compared against the classical wisdom of crowds (averaging many independent Stage i1 answers) and against **clone groups** (three copies of one model, same protocol, same group size).

## Key Findings

- **Deliberation beats aggregation in all four domains** (jar estimation, NeurIPS 2024 peer review of 100 papers, AI-safety monitoring of 50 agent trajectories, 2026 World Cup forecasting on 44 events). Averaging a few group consensuses beat averaging many more independent answers (e.g. Study 2: z = 19.35, Cohen's d = 6.71; Study 3: z = 19.30, d = 4.30; Study 4: z = 19.11, d = 3.32).
- **The gain is not just averaging**: each group's consensus beat the mean of its own three opening answers (Study 2 paired d = 0.25; Study 3 paired d = 0.30; Study 4 paired d = 0.29).
- **Weak monitors catch a stronger saboteur better together**: in Study 3 (25 sabotage trajectories from the Monitor Red Teaming dataset) the consensus improved on the independent crowd in **19 of 25** cases (paired d = 0.90). No harmless trajectory was flagged on aggregate (highest mean consensus 2.8/10).
- **Clones gain nothing**: groups of three copies of the same model did not improve on pooling that model's own independent answers. Study 1: Anthropic ×3 p = 0.22, OpenAI ×3 p = 0.61, Google ×3 p = 0.76, while the size-matched heterogeneous groups did improve (z = 3.61, p = 3.1 × 10⁻⁴, d = 0.48). Bayes factors favoured the null (BF = 5.60, 3.99, 6.19). Study 2 repeats this (heterogeneous p = 0.023; homogeneous p = 0.098, 0.87, 0.64).
- **Expert dominance, and the leader changes by domain**: in three of four domains one model alone beat the heterogeneous crowd (Gemini in Studies 1 and 4, Claude in Study 2). But Gemini was the **weakest** monitor in Study 3, so the best model "could not have been known" in advance.
- **Private revision copies the consensus**: in Study 2, 82 of 100 papers had post-discussion ratings equal to the agreed value; in Study 3, 417 of 447 re-ratings did.
- **Limits**: small models only; a Study 3 dataset built from older agents; deliberation over long trajectories may cost too much.

## Relevance to Praxis

- **Directly scopes H2** in the deconfliction report. `rules/multi-agent-coordination.md` "DON'T: Expand candidate model pools with arbitrary heterogeneous architectures" (2609.17306, same-family pools for routing/voting) should not be read as advice for **deliberation or verification** pools. For those, this paper shows same-model groups get zero benefit and cross-family groups get a significant one. This matches the existing "DON'T: Assume multi-agent debate eliminates shared misconceptions".
- Supports cross-family monitor panels in guard-agent topologies (`rules/agent-sandbox-safety.md` "DO: Decouple safety and fairness monitoring into dedicated guard-agent topologies").
- A counterpoint to [`llm-group-consensus-overstatement`](llm-group-consensus-overstatement.md): consensus can be right, but only with diversity, and the high Stage i2 copy rate means post-deliberation answers are **not** independent votes.
- Related skills: [`debate-consensus-memory-calibration`](../skills/debate-consensus-memory-calibration/SKILL.md), [`debate-layer-disagreement-analysis`](../skills/debate-layer-disagreement-analysis/SKILL.md).

> Source: Barrera-Lemarchand, Sigman & Navajas, "The Wisdom of Artificial Deliberative Crowds" (arXiv:2609.22497)
