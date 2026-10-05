# A Cheap Verifier is Good Enough: Rubric Rewards in RL Post-Training

> **Paper**: [A Cheap Verifier is Good Enough: LLM Post-training is Robust to Erroneous Rewards](https://arxiv.org/abs/2609.33467)
> **Praxis source**: src:2609-33467v1

## Why Not a Skill?

An empirical study of which LLM judge to use as the reward model in GRPO
post-training on rubric-graded tasks. It yields a decision criterion (do not
pick the training verifier by agreement alone) but no transferable
procedure; the authors say their low-cost picks were chosen retrospectively
from training outcomes, not by a validated selection rule.

---

## Core Concept

In semi-verifiable domains (medical, legal, finance answers graded against
rubrics) the reward comes from an LLM verifier that is itself imperfect. The
paper asks whether agreement with a strong reference judge ("golden
verifier") predicts how good a policy the verifier trains. It does not
introduce synthetic reward noise: errors are the verifiers' natural
disagreements with the golden judges.

## Key Findings

- **Setting**: Qwen3 1.7B, 4B and 8B trainees on HealthBench; Qwen3 8B on
  PRBench (legal, finance). GRPO, 8 rollouts per prompt, 120 prompts per
  batch, constant LR 5×10⁻⁶, no effective KL penalty. 52 candidate judges
  screened, 12 used as training verifiers. Golden verifiers: Claude Opus
  4.6, Gemini 3.1 Pro, GPT-5.5. About 11.3k H100 GPU-hours.
- **Agreement is not the selection criterion**: "higher verifier agreement
  does not consistently identify the best training verifier". Agreement
  still helps screen out very weak verifiers, which can harm training. No
  correlation coefficient is reported.
- **Cheap verifiers come close**: the "balanced" pick (Gemma 4 26B) had a
  +0.010 score gap to the best verifier per cell, captured 95% of the
  available uplift, at a 98.8% cost reduction versus the golden protocol.
  The "cost-reducing" pick: +0.027 gap, 82% uplift, 99.7% cost reduction.
  The abstract summarises this as average gaps of 1–3 points, with larger
  losses in individual settings.
- **Cost probe (HealthBench)**: Gemma 4 26B at $0.45 per 1,000 tasks (4.3
  calls, 5,514 tokens per task) versus Claude Opus 4.6 at $133.20 (11.6
  calls, 21,321 tokens).
- **Length drift**: mean response length on PRBench grew from about 1.9k
  (legal) and 2.4k (finance) tokens to about 4.9k, near the 5,000-token
  cap. The authors ran no dedicated reward-hacking test.
- **Limitations stated by the authors**: trainees up to 8B and one GRPO
  setup; golden labels are LLM references, not human ground truth (human
  review covered 50 HealthBench criteria); agreement measured on fixed
  responses, not on each trained policy's outputs; no controlled
  replication, so training randomness and verifier effects are not
  separated; the low-cost picks were selected using observed training
  outcomes.

## Relevance to Praxis

- **Training reward vs acceptance gate are different jobs.** A reward
  verifier's errors are averaged over many GRPO updates; an acceptance gate
  makes one discrete keep/reject decision per change. This paper concerns
  the former only. It gives no licence to loosen "Pass every
  self-modification through one acceptance gate" or "Invest in standalone
  verifiers before planning components" (`rules/recursive-improvement.md`),
  which concern inference-time and keep-time verification where a single
  false pass ships.
- **Screen by agreement, choose by outcome.** Use agreement with a strong
  judge to discard weak verifiers, then compare the survivors on a short
  post-training sweep. This partially qualifies agreement-based surrogate
  calibration ("Use bilevel surrogate rubrics with rank-correlation
  calibration", `rules/recursive-improvement.md`), which assumes agreement
  with the oracle tracks usefulness.
- **Watch length.** Unconstrained length growth under rubric rewards is the
  first thing to monitor; see
  [`reward-hacking-immunization`](../skills/reward-hacking-immunization/SKILL.md).
- Related: [`multi-solver-disagreement-rewards`](multi-solver-disagreement-rewards.md),
  [`verifier-survey-no-free-checker`](verifier-survey-no-free-checker.md),
  and WEFT's task–verifier consistency filter in
  [`execution-driven-environment-repair`](../skills/execution-driven-environment-repair/SKILL.md).

> Source: A Cheap Verifier is Good Enough: LLM Post-training is Robust to Erroneous Rewards (arXiv:2609.33467)
