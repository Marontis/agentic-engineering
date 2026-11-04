# Jailbreak Connectivity in Multimodal LLMs: Defensive Lessons

> **Source**: [arXiv:2610.38091](https://arxiv.org/abs/2610.38091) — Xu Zhang, Ziqing Hu, Shuo Han, Ren Wang (Illinois Institute of Technology; Perplexity AI; University of Illinois Chicago), published 2026-10-28. Praxis ID: `src:2610-38091v1`.

> [!IMPORTANT]
> **Defensive-Only Brief**: This document records the threat model, empirical vulnerability surfaces, and defensive implications of continuous adversarial manifolds in Multimodal Large Language Models (MLLMs). It omits offensive optimization recipes and is intended strictly for hardening multimodal agent pipelines and safety filters.

## Summary

Zhang et al. demonstrate that adversarial visual perturbations capable of jailbreaking safety-aligned Multimodal Large Language Models (MLLMs) are **not isolated points** in pixel space, but form **continuous, low-loss 1D manifolds** (parameterized via quadratic Bézier curves connecting distinct PGD endpoints). When regularized by CLIP-based surrogate feature predictors (`Safety Classifier` $f_{\text{safe}}$ and `Jailbreak Success Predictor` $f_{\text{success}}$), every point sampled along the curve remains a high-fluency, transferable, and query-agnostic jailbreak across open-weight and commercial black-box MLLMs.

## Key Vulnerability Findings for Defenders

1. **Point-Specific Adversarial Patching Fails Against Connected Manifolds**:
   - While linear interpolation between two PGD adversarial images on `Qwen3-VL-8B-Instruct` hits a loss barrier of `5.26` and succeeds at only `57.14%` (`12/21` sampled points), a quadratic Bézier path keeps the loss below $10^{-4}$ across the entire curve and achieves **`100%` (`21/21` points)** attack success.
   - Across `MM-SafetyBench` (`13` prohibited scenarios, 5 runs), path-connected visual perturbations raise average white-box Attack Success Rate (`ASR`) to **`84.01% ± 1.61`** on `Qwen3-VL-8B-Instruct` (vs `22.97%` for single-point PGD `Adv Example` and `24.55%` for `Query Image`), **`85.77% ± 1.05`** on `InternVL3.5-8B` (vs `26.17%` / `27.83%`), and **`97.95% ± 0.49`** on `Gemma-3-12B-IT` (vs `24.93%` / `29.59%`).
2. **Cross-Architecture & Commercial Black-Box Transferability**:
   - Perturbations optimized on `Qwen3-VL-8B-Instruct` transfer zero-shot at **`70.01% ± 0.91` ASR** to `InternVL3.5-8B` and **`78.56% ± 0.90` ASR** to `Gemma-3-12B-IT` (outperforming `FORCE` at `66.14%` and `74.62%`). Removing Bézier path optimization (`w/o Path`) causes transfer ASR to collapse by `42.33–45.91 percentage points` (`27.68%–35.04%`), proving that flat, connected loss basins drive cross-model transfer.
   - Against commercial black-box MLLMs, zero-shot transfer reaches **`41.94% ± 0.98` ASR** on `GPT-5.6` (vs `17.25% ± 0.87` for `FigStep`, `+24.69 pp`, winning all 13 scenarios) and **`47.05% ± 1.23` ASR** on `Gemini 3.1 Pro` (vs `19.71% ± 0.79` for `FigStep`, `+27.34 pp`, winning all 13 scenarios).
3. **Query-Agnostic Universal Reuse**:
   - A single universal Bézier path optimized over 100 harmful sentences succeeds on **`85.0%` (`34/40`)** of unseen harmful queries on `Qwen3-VL-8B-Instruct` (double the `42.5%` [`17/40`] of single-point PGD) and transfers zero-shot to **`55.0%` (`22/40`)** of unseen queries on `InternVL3.5-8B`.
4. **Perplexity Filters Cannot Detect Manifold Jailbreaks**:
   - Responses induced by path-connected visual attacks exhibit **lower perplexity (`PPL`)** than both plain-text refusals and single-point visual attacks across 11 of 13 scenarios per model (`PPL = 5.07` on `Qwen3-VL-8B-Instruct`, `4.57` on `InternVL3.5-8B`, `5.07` on `Gemma-3-12B-IT` vs `8.91–9.77` for single-point `Adv Example`). Output fluency/perplexity monitors are therefore ineffective as a standalone defense.

## Defensive Takeaways for Multimodal Agent Systems

- **Do not rely on signature blacklists, single-point adversarial training, or output perplexity filters** to secure vision-enabled agents against image-based prompt injection or jailbreaks: an attacker with a connected Bézier path can sample infinitely many distinct adversarial images with near-zero loss and high output fluency.
- **Decouple visual perception from privileged tool execution and safety adjudication**: When a multimodal agent ingests external images, either (a) pass image-derived task intents through a **text-only safety/policy verifier** that never receives raw visual embeddings, or (b) apply input-space randomized smoothing / loss-landscape curvature checks before vision-encoder features enter the language backbone.

## Why Not a Skill?

This paper presents an offensive multimodal jailbreak optimization method. Per repository policy (`output/AGENTS.md`), dual-use offensive attack papers are documented strictly as defensive-only research briefs and defensive rule evidence, never as procedural skills.
