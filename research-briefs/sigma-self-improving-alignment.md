# SIGMA: Self-Improving Alignment from a Model Spec

> **Paper**: [SIGMA: Self-Improving Alignment Generalization from a Model Spec](https://arxiv.org/abs/2610.07935)
> **Praxis source**: src:2610-07935

## Why Not a Skill?

SIGMA is a model-training pipeline (rejection-sampling SFT and GRPO on a
27B model). The transferable insight, that a model can generate and judge its
own alignment training data from a spec, matters for model developers rather
than as an agent-level procedure.

---

## Core Concept

Given only a Model Spec and high-level task domains, the candidate model acts
as a **task designer agent**: from 935 seed scenarios, 8 rollouts each with a
random spec section, it produces 7,137 alignment-dilemma task pairs (14,274
prompts) with rubrics, self-verified and refined. It then serves as **its own
reward model**: rejection-sampling SFT (N = 16 candidates per prompt) and
GRPO with a multiplicative reward R = R_rubric · R_spec. Base model:
Qwen3.6-27B. Training data is single-turn chat only.

### Key Finding

- **Transfers to agentic settings**: AgentHarm harm score fell from 22.6 to
  14.8 (176 harmful tasks, with benign counterparts tracked), and the Agentic
  Misalignment average (blackmail, leaking, murder scenarios) fell from 79.1
  to 3.8.
- **Beats spec-based baselines**: outperforms Deliberative Alignment,
  Constitutional AI (critique–revision against the spec), and the externally
  supervised STAR-1 dataset, while reducing power-seeking (InstrumentalEval)
  and sycophancy and preserving general capability.
- **What mattered**: a spec that balances harmlessness and helpfulness,
  test-time safety reasoning, and high-quality rubrics from the task designer;
  both reward terms were needed for broad generalization.

## Relevance to Praxis

- **Self-generated supervision can work for alignment**, not only for
  verifiable domains. This bears on recursive self-improvement loops where
  safety evaluation is the bottleneck; see `rules/recursive-improvement.md`.
- **Caution on self-judging**: the model is its own reward model here. For
  agent-harness self-modification, the knowledge base still requires the
  single acceptance gate with an always-strict security testbed rather than
  self-assessed safety.
- Related: [SSRFT](safe-role-internalization-alignment.md) also trains on a
  written role or spec rather than refusal examples.
