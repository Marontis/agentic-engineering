# SENTINEL: Intention-Aware Input–Output Matching Against Jailbreaks

> **Paper**: [Reactivating Alignment: Defending LLMs from Jailbreaks via Intention-Aware Input–Output Matching](https://arxiv.org/abs/2610.04470)
> **Praxis source**: src:2610-04470

## Why Not a Skill?

SENTINEL is a white-box, model-internal defense: it needs hidden activations
and a refusal direction from the protected model. It does not transfer as a
procedure to agents built on closed API models, so it is kept as context.

---

## Core Concept

Instead of perturbing the whole input or suppressing harmful outputs,
SENTINEL locates where malicious intent sits in an adversarial prompt. It
extracts an intent subsequence by matching context-window features of the
input against the output (framed as Wasserstein-distance minimization with an
upper-bound surrogate), aggregates at token level, sanitizes adaptively, and
scores the extracted sequence by projection onto the refusal direction
(Arditi et al., 2024). The threshold τ is set two standard deviations above
the mean benign projection, which the authors describe as leaving about 97.5%
of benign prompts unaffected.

### Key Finding

- **Primary Result**: on HarmBench (300 test cases per attack; GCG, AutoDAN,
  GPT-Fuzz, FewShot, PAIR, plus RADICAL and DSA), attack success rate stays
  below 5% even for weakly aligned models such as Mistral-7B-v0.2 and close
  to 3% for Llama-3-8B.
- **Secondary Result**: the authors report a lower over-refusal rate on
  OR-Bench (2,000 sampled boundary questions) than baselines with similar
  defense strength (RPO, Circuit Breaker, LAT, IBProtector, MoGU). Per-method
  over-refusal figures are in tables that could not be extracted from the
  HTML; check the paper before quoting them.
- Intent-extraction precision correlated with defense performance, and an
  adaptive attacker optimizing 20 embedding-suffix positions against the
  matcher was evaluated.

## Relevance to Praxis

- **Localize intent before judging**: scoring the extracted harmful span
  rather than the whole camouflaged prompt is the same idea as span-level
  sanitization in [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md),
  applied at the model layer.
- **Only for self-hosted models**: useful where the agent stack runs
  open-weight models and can read activations; irrelevant for API-only
  deployments.
