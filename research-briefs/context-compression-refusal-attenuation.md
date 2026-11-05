# Does Context Compression Preserve Refusal Alignment?

> **Source**: [arXiv:2611.06380](https://arxiv.org/abs/2611.06380) | `src:2611-06380v1`
> **Authors**: Anthony Nguyen, Wenjun Lin (Algoma University)
> **Date**: November 2026
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Executive Summary

Soft context compression methods—such as the fixed-length In-Context Autoencoder (`ICAE`) and the variable-length pooled `ARC-Encoder`—condense long prompts or retrieved documents into compact continuous memory vectors before feeding them to an instruction-tuned LLM decoder. While these encoders are trained to preserve semantic reconstruction fidelity and downstream task performance, their impact on the decoder's safety alignment had not been systematically audited.

Nguyen and Lin demonstrate that **encoder-based soft context compression systematically attenuates refusal alignment**, acting as an unintentional jailbreak across both `Mistral` and `LLaMA` model families. On a controlled 624-prompt evaluation and standard adversarial benchmarks (`HarmBench` and `AdvBench`), compressing harmful prompts through `ICAE` or `ARC-Encoder` causes refusal rates to plummet—dropping from `62.82%` to `10.9%` on `Mistral-7B-Instruct-v0.2` (and from `57.5%` to `16.5%` on `HarmBench`, a `>71%` relative collapse) and from `96.15%` to `36.54%` on `LLaMA-3.1-8B-Instruct`. Mechanistic linear probing across the decoder's residual stream reveals why: reconstruction-trained encoders strip the low-dimensional representation geometry that activates the decoder's refusal direction, shifting harmful prompt projections from strongly positive (refusal) to negative (compliance). As a proof-of-concept remedy for fixed-length `ICAE` slots, the authors introduce **Memory Steering**, a gated inference-time intervention in compressed memory space that restores `AdvBench` and `HarmBench` refusal rates without retraining the encoder or decoder.

---

## Key Findings

1. **Soft Context Compression Drastically Degrades Refusal Rates Across Architectures**:
   - On the held-out split of a custom 624-prompt dataset (`312` safe, `312` harmful including `140` semantically matched safe-harmful pairs; judged by `Gemma-3-27b-it`), compressing prompts drops harmful refusal rates across all four tested model-compressor pairs while leaving safe-prompt refusal rates near `0.00%`:
     - `Mistral-7B-Instruct-v0.2` (`ICAE`): **`62.82% -> 10.9%`** (`-51.92 pp`).
     - `LLaMA-3.1-8B-Instruct` (`ARC-Encoder`): **`96.15% -> 36.54%`** (`-59.61 pp`).
     - `Mistral-7B-Instruct-v0.3` (`ARC-Encoder`): **`20.51% -> 8.97%`** (`-11.54 pp`).
     - `LLaMA-2-7B-Chat` (`ICAE`): **`97.44% -> 85.9%`** (`-11.54 pp`, with safe false refusals rising slightly from `0.00%` to `3.2%`).
   - On standard adversarial benchmarks (`HarmBench` / `AdvBench`), compression similarly erodes alignment:
     - `LLaMA-3.1-8B-Instruct` (`ARC-Encoder`): **`84.0% -> 47.5%`** on `HarmBench` (`>40%` relative drop) and **`93.46% -> 70.19%`** on `AdvBench`.
     - `Mistral-7B-Instruct-v0.2` (`ICAE`): **`57.5% -> 16.5%`** on `HarmBench` and **`62.69% -> 20.38%`** on `AdvBench`.
     - `LLaMA-2-7B-Chat` (`ICAE`): **`99.0% -> 77.0%`** on `HarmBench` and **`99.62% -> 90.96%`** on `AdvBench`.
     - `Mistral-7B-Instruct-v0.3` (`ARC-Encoder`): **`28.5% -> 23.5%`** on `HarmBench` and **`42.88% -> 31.54%`** on `AdvBench`.

2. **Mechanistic Root Cause: Reconstruction Objectives Strip Refusal-Direction Geometry**:
   - Probing the decoder's hidden states $h^\ell(x)$ with a layer-wise linear refusal probe $s_\ell(x) = w_\ell^\top h^\ell(x)$ shows that uncompressed harmful prompts induce a strong positive refusal-direction activation across middle and late decoder layers.
   - When the exact same harmful prompts are passed as `ICAE` memory tokens, $s_\ell(x)$ collapses into the negative regime—indistinguishable from safe prompts—because autoencoder training optimizes token reconstruction cross-entropy, which preserves high-variance semantic content while discarding low-dimensional safety-triggering directions.

3. **Gated Counterfactual Memory Steering Restores Refusal in Fixed-Length `ICAE` Slots**:
   - For fixed-length `ICAE` memory slots $m(x) \in \mathbb{R}^{K \times D}$, the authors compute a counterfactual slot shift $\Delta\mu = \mu_D - \mu_S$ between prompts wrapped with an explicit safety-violation tag ($\tilde{x} = x \text{ ``(This violates your AI safety guidelines)''}$) and unwrapped prompts, and apply a per-slot logistic regression gate $p_k(x) = \sigma(w^\top m_k(x))$ at inference time:
     $$m'_k(x) = m_k(x) + \alpha \, p_k(x) \, \Delta_k$$
   - Sweeping steering strength $\alpha \in \{0.5, 1.0, 1.5, 2.0\}$ on `Mistral-7B-Instruct-v0.2 + ICAE` restores `AdvBench` refusal from **`20.38%`** ($\alpha=0$) to **`41.92%`**, **`67.31%`**, **`76.54%`**, and **`81.15%`** ($\alpha=2.0$, exceeding the `62.69%` uncompressed baseline), and restores `HarmBench` refusal from **`16.50%`** to **`57.50%`** at $\alpha=2.0$ (matching the `57.5%` uncompressed baseline).
   - On `LLaMA-2-7B-Chat + ICAE`, Memory Steering recovers `AdvBench` refusal from **`90.96%`** to **`99.62%`** ($\alpha=1.0$) and **`100.00%`** ($\alpha \ge 1.5$), and `HarmBench` refusal from **`77.00%`** to **`94.00%`** ($\alpha=1.0$) and **`97.50%`** ($\alpha=2.0$).
   - Crucially, per-slot logistic gating prevents over-refusal on benign inputs: pairwise `Gemma-3-27b-it` quality evaluations confirm that safe-prompt generation remains on-par (win + tie rate) with unsteered compression on **`79.5%–85.9%`** of `LLaMA-2-7B-Chat` outputs and **`82.1%–87.8%`** of `Mistral-7B-Instruct-v0.2` outputs across $\alpha \in [0.5, 2.0]$.

---

## Quantitative Summary

| Model & Compressor | Benchmark / Split | Uncompressed Refusal | Compressed Refusal ($\alpha = 0$) | Steered Compressed Refusal (`Memory Steering`) |
|:---|:---|:---|:---|:---|
| **`Mistral-7B-Instruct-v0.2` + `ICAE`** (fixed-length slots) | Custom Held-Out (`156` harmful / `156` safe)<br>`AdvBench`<br>`HarmBench`<br>Safe Quality On-Par Rate | `62.82%` (safe: `0.00%`)<br>`62.69%`<br>`57.50%`<br>— | **`10.90%`** (safe: `0.00%`)<br>**`20.38%`**<br>**`16.50%`**<br>— | —<br>`41.92%` ($\alpha=0.5$) $\to$ `67.31%` ($1.0$) $\to$ `76.54%` ($1.5$) $\to$ **`81.15%`** ($2.0$)<br>`24.00%` ($\alpha=0.5$) $\to$ `39.50%` ($1.0$) $\to$ `50.00%` ($1.5$) $\to$ **`57.50%`** ($2.0$)<br>**`87.8%` / `82.7%` / `87.8%` / `82.1%`** ($\alpha = 0.5 / 1.0 / 1.5 / 2.0$) |
| **`LLaMA-2-7B-Chat` + `ICAE`** (fixed-length slots) | Custom Held-Out (`156` harmful / `156` safe)<br>`AdvBench`<br>`HarmBench`<br>Safe Quality On-Par Rate | `97.44%` (safe: `0.00%`)<br>`99.62%`<br>`99.00%`<br>— | **`85.90%`** (safe: `3.20%`)<br>**`90.96%`**<br>**`77.00%`**<br>— | —<br>`98.08%` ($\alpha=0.5$) $\to$ `99.62%` ($1.0$) $\to$ **`100.00%`** ($1.5, 2.0$)<br>`86.50%` ($\alpha=0.5$) $\to$ `94.00%` ($1.0$) $\to$ `96.50%` ($1.5$) $\to$ **`97.50%`** ($2.0$)<br>**`85.9%` / `83.3%` / `82.7%` / `79.5%`** ($\alpha = 0.5 / 1.0 / 1.5 / 2.0$) |
| **`LLaMA-3.1-8B-Instruct` + `ARC-Encoder`** (variable-length pooled) | Custom Held-Out (`156` harmful / `156` safe)<br>`AdvBench`<br>`HarmBench` | `96.15%` (safe: `0.00%`)<br>`93.46%`<br>`84.00%` | **`36.54%`** (safe: `0.00%`)<br>**`70.19%`**<br>**`47.50%`** | *(Not applicable: variable-length pooled slots lack fixed positional alignment for slot-wise steering)* |
| **`Mistral-7B-Instruct-v0.3` + `ARC-Encoder`** (variable-length pooled) | Custom Held-Out (`156` harmful / `156` safe)<br>`AdvBench`<br>`HarmBench` | `20.51%` (safe: `0.00%`)<br>`42.88%`<br>`28.50%` | **`8.97%`** (safe: `0.00%`)<br>**`31.54%`**<br>**`23.50%`** | *(Not applicable: variable-length pooled slots)* |

---

## Why Not a Skill?

This paper is a diagnostic mechanistic study of soft-token autoencoder compression paired with an architecture-specific intervention (`Memory Steering`) that applies only to fixed-length `ICAE` memory slots (and cannot be directly applied to variable-length pooled compressors like `ARC-Encoder` or standard text-level context compaction pipelines). Its primary engineering value is a critical safety warning and guardrail requirement for any agent pipeline using learned soft-prompt compression, making a **Research Brief** plus rule updates in `agent-sandbox-safety.md` and `skill-system-design.md` the right fit.

---

## Actionable Takeaways

1. **Never rely solely on the downstream LLM decoder's built-in refusal alignment when inputs pass through a soft context compressor**: Compressing untrusted user prompts or retrieved web documents through `ICAE` or `ARC-Encoder` strips the residual-stream refusal direction and drops refusal rates by up to `59.61` percentage points (`96.15% -> 36.54%` on `LLaMA-3.1-8B-Instruct`). Always run input safety classifiers or refusal checks on the **raw uncompressed text** prior to encoding.
2. **Apply gated counterfactual Memory Steering ($\alpha \in [1.0, 2.0]$) if deploying fixed-slot soft compressors (`ICAE`)**: Adding a logistic-regression-gated counterfactual refusal shift $m'_k(x) = m_k(x) + \alpha p_k(x)\Delta_k$ at inference time restores `HarmBench` and `AdvBench` refusal rates (`16.5% -> 57.5%` and `20.38% -> 81.15%` on `Mistral-7B-v0.2`) while maintaining `>79%–82%` response quality parity on benign prompts.
3. **Audit context-compaction and KV-cache compression modules on `HarmBench`/`AdvBench` before deployment**: Standard perplexity and QA benchmarks do not detect alignment geometry collapse; include adversarial refusal retention as a mandatory regression gate whenever introducing context compression.
