# J-Anchor: Defending Against Prefill Attacks via J-Space Selective Refusal Restoration

> **Source**: [arXiv:2611.01342](https://arxiv.org/abs/2611.01342) — Running Yang, Beidi Zhao, Xiaoxiao Li (University of British Columbia; Vector Institute), published 2026-10-31. Praxis ID: `src:2611-01342v1`.

## Summary

**Prefill attacks** bypass LLM safety alignment by injecting an affirmative or harmful prefix directly into the beginning of the assistant's response turn before autoregressive generation starts. Yang et al. show that while standard instruction-tuned models encode user-prompt harmfulness and refusal intent along distinct internal directions, prefilling suppresses the **refusal projection** along the output trajectory while leaving the **harmfulness signal** intact at user-prompt token positions. Furthermore, under **deep prefill attacks** ($k = 500$ forced harmful tokens), existing static activation-steering defenses (`Refusal Vector`, `CAST`, `AlphaSteer`) completely collapse (`71.1%–92.7%` Attack Success Rate), while periodic probe-based monitors (`ADA-RK`, `ADA-LP`) trigger severe benign over-refusal (`37.6%–68.0%` on `XSTest`/`OKTest`).

The authors propose **J-Anchor**, a training-free white-box decoding defense that uses a local **Jacobian lens** ($J_\ell = \frac{\partial h_L}{\partial h_\ell}$) to map intermediate layer representations ($\ell \in [40\%, 85\%]$ depth) into the final-layer space:

1. **J-Space Subspace Decoupling**: Extracts an output-aligned refusal subspace $U_R^\ell$ (SVD rank $r_R^\ell$ capturing $\ge 90\%$ energy) and orthogonalizes the prompt-harmfulness difference vector against $U_R^\ell$ to obtain a pure rank-1 harmfulness detector $U_H^\ell$.
2. **Pre-Generation Harmfulness Gating**: Before generating new tokens, evaluates a normalized harmfulness score $s_{\text{harm}}(x)$ across the top-3 AUROC-calibrated layers $\mathcal{L}_{\text{gate}}$. If $s_{\text{harm}}(x) \le \tau$ ($\tau = 0.75$), decoding proceeds untouched, preserving benign compliance and reasoning.
3. **Selective Refusal Anchor Restoration**: If $s_{\text{harm}}(x) > \tau$, projects out the prefill-corrupted refusal component at every decoding step and replaces it with a scaled clean refusal anchor ($\rho \in \{2, 3\}$), restoring refusal mid-generation even after 500 forced harmful tokens.

## Key Quantitative Findings

- **Fixed Prefill Defense (`StrongREJECT` 313 / `AdvBench` 100 / `HarmBench` 159)**:
  - `Llama-3.1-8B-Instruct`: Fixed Prefill raises Base ASR from `1.9% / 6.0% / 10.1%` to `65.2% / 65.0% / 54.1%`. `J-Anchor` reduces ASR to **`1.0% / 0.0% / 3.8%`** while keeping `XSTest` / `OKTest` Over-Refusal Rate (`ORR`) at **`7.6% / 23.3%`** (matching Clean Base `7.6% / 22.0%`, whereas `Refusal Vector` hits `60.8% / 64.7%` ORR and `ADA-RK` hits `40.8% / 47.7%`).
  - `Gemma-4-E4B-IT`: Fixed Prefill Base ASR `82.7% / 89.0% / 80.5%` drops to **`0.0% / 0.0% / 0.6%`** under `J-Anchor` with **`16.0% / 26.7%`** ORR (vs `60.4% / 68.0%` ORR for `ADA-LP` and `37.6% / 41.7%` for `ADA-RK`).
  - `Qwen3.5-4B` (hybrid Gated DeltaNet–attention): Fixed Prefill Base ASR `77.3% / 79.0% / 64.2%` drops to **`0.3% / 0.0% / 0.0%`** with **`6.4% / 17.0%`** ORR (vs `40.8% / 52.3%` ORR for `ADA-LP`).
  - `Qwen3-8B`: Fixed Prefill Base ASR `67.7% / 82.0% / 69.2%` drops to **`3.8% / 0.0% / 5.0%`** with **`5.6% / 11.7%`** ORR (vs `21.2% / 30.0%` ORR for `ADA-LP`).
- **Deep Prefill ($k = 500$ Forced Tokens) Resilience**:
  - Static steering (`CAST`, `AlphaSteer`, `Refusal Vector`) fails completely under 500-token prefill (`71.1%–92.7%` ASR across all 4 models).
  - `J-Anchor` reduces 500-token Deep Prefill ASR (`StrongREJECT` / `AdvBench` / `HarmBench`) to **`0.3% / 0.0% / 2.5%`** on `Llama-3.1-8B-Instruct`, **`0.0% / 0.0% / 0.0%`** on `Gemma-4-E4B-IT`, **`0.0% / 1.0% / 0.0%`** on `Qwen3.5-4B`, and **`11.5% / 1.0% / 2.5%`** on `Qwen3-8B`.
- **Why the Jacobian Lens Matters (Table 3 Ablation on `StrongREJECT`)**:
  - Replacing the Jacobian lens with an identity map (`Logit-lens refusal`, $J_\ell = I$) degrades Deep Prefill ASR from **`0.3%` to `79.9%`** on `Llama-3.1-8B-Instruct` and from **`0.0%` to `31.9%`** on `Qwen3.5-4B`, confirming that intermediate refusal directions are misaligned with final-layer output space without Jacobian projection.
- **Zero Reasoning Collapse**: On `GSM8K` (`100`) and `MATH500` (`100`), `J-Anchor` maintains `87.0% / 51.0%` (`Llama-3.1-8B`), `91.0% / 91.0%` (`Gemma-4-E4B-IT`), `92.0% / 90.0%` (`Qwen3.5-4B`), and `93.0% / 86.0%` (`Qwen3-8B`), whereas `Refusal Vector` collapses to `4.0% / 35.0%` on `Llama-3.1-8B` and `ADA-LP` drops 6–12 points on `Qwen3.5-4B`.

## Why Not a Skill?

`J-Anchor` requires white-box access to internal transformer residual streams and pre-computed layer-to-final Jacobian matrices ($J_\ell$) during token-by-token decoding. It cannot be implemented as a model-agnostic agent workflow or harness skill when calling hosted or black-box LLM APIs. Its operational takeaway for agent and gateway builders—that deep assistant-turn prefilling defeats prompt-level alignment and static steering—is captured as a rule in `output/rules/agent-sandbox-safety.md`.
