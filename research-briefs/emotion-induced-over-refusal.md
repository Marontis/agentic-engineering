# EmoRSS: Emotion-Induced Over-Refusal

> **Paper**: [EmoRSS: Mitigating Emotion-Induced Over-Refusal in Large Language Models](https://arxiv.org/abs/2610.04998)
> **Praxis source**: src:2610-04998

## Why Not a Skill?

The method is activation steering with sparse-autoencoder features on a
self-hosted model. The transferable part is the finding that emotional
framing raises refusals on benign requests, which matters for evaluation
design rather than as a procedure.

---

## Core Concept

The paper builds 512 paired requests (from JailbreakBench, XSTest, OR-Bench
and HarmBench) that differ only in emotional expression, and shows emotion
shifts models toward refusing benign requests. EmoRSS locates a
refusal-sensitive layer with linear probes, builds a K = 32 refusal subspace
from SAE features aligned with the probe direction, estimates the mean shift
between regular and emotional versions of the same request, and applies the
reverse shift at inference without updating weights.

### Key Finding

- **Primary Result**: EmoRSS reduced the benign refusal rate (BRR) to 7.29%
  on both Llama-3.1-8B-it and Qwen3-8B, with harmful compliance (HCR) of
  0.00% and 2.08%. Among methods keeping HCR below 5% on both models, it had
  the lowest BRR.
- **Trade-off against baselines**: contrastive decoding (Self-CD) reached
  lower BRR (4.69% and 2.60%) but raised HCR to 31.77% and 18.23%.
  Prompting reduced BRR only to 15.10% and 41.15%.
- **Capability preserved**: MMLU 60.3% versus 58.4% without intervention;
  XSum 27.1% versus 27.0%. Substantive answers to 128 benign emotional
  requests rose from 98 to 112 (Llama) and 110 to 119 (Qwen).

## Relevance to Praxis

- **Test refusal behavior under emotional framing**: support, health, and
  crisis-facing agents see emotional input routinely; an evaluation set of
  neutral prompts will understate over-refusal. Pair neutral and emotional
  versions of the same request.
- **Report both directions**: the Self-CD result is a reminder that cutting
  over-refusal can buy harmful compliance; always report BRR and HCR together.
