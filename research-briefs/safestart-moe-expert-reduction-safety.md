# SafeStart: Mitigating the Overlooked Safety Cost of Active Expert Reduction in MoE LLM Serving

> **Source**: [arXiv:2611.06147](https://arxiv.org/abs/2611.06147) | `src:2611-06147`
> **Authors**: Erfan Baghaei Potraghloo, Saeid Shokoufa, Seyedarmin Azizi, Arya Fayyazi, Souvik Kundu, Mehdi Kamal, Massoud Pedram (University of Southern California & Intel Labs)
> **Date**: November 2026
> **Categories**: cs.CR, cs.AI, cs.CL, cs.LG

---

## Summary

`SafeStart` investigates a critical deployment vulnerability in Mixture-of-Experts (`MoE`) LLM serving: inference-time active expert reduction (`top-k` truncation, dynamic `top-p` routing, threshold-based `ACE`, and layer-adaptive `LExI`), which drops lower-weight experts per token to accelerate small-batch decoding (`15%–28%` speedup at batch size `8`), **silently degrades safety refusal** even when standard capability (`MMLU`, `GSM8K`) and over-refusal (`XSTest`) benchmarks appear virtually unchanged.

Across `9` open-weight `MoE` models in `vLLM 0.11.0` evaluated on `472` harmful prompts (`159` `HarmBench` + `313` `StrongREJECT`) and `889` held-out requests (`AdvBench` + `CatQA`), the authors trace the failure mechanism to two interacting factors: (1) models that **do not renormalize router gate weights** after dropping experts lose gate mass ($m_k(x) < 1$), shifting the final prompt token's hidden state along the refusal direction toward the harmless compliance side; and (2) **refusal commitment happens at the very start of generation**—on `Qwen1.5-MoE`, `92` of `101` safety flips diverge at the **first generated token**, and truncating only the prompt plus the first token reproduces `91%` of the full-sequence attack success rate (`ASR`) increase (`62%` on `OLMoE-0125`).

To fix this without sacrificing decode throughput, `SafeStart` modifies the `vLLM` fused MoE Triton kernel (`~160` lines) to run the full expert budget $k$ during **prefill** ($P$ prompt tokens) and the **first $N=8$ generated tokens**, switching to the reduced budget $k'$ only from token $N+1$ onward (and disabling expert reduction above batch size $B=32$, where large batches already activate nearly every expert).

---

## Key Findings

1. **Active expert reduction causes large, statistically significant ASR spikes invisible to capability benchmarks**: Keeping $k' = \lceil 2k/3 \rceil$ experts under refusal-suppression framing raises `Llama Guard 3` `ASR` by `+18.4 pp` on `Qwen1.5-MoE` (`46.6%` $\to$ `65.0%`), `+9.5 pp` on `OLMoE-0125` (`24.2%` $\to$ `33.7%`), and `+6.6 pp` on `DeepSeek-V2-Lite` (`43.6%` $\to$ `50.2%`), while `MMLU` drops by at most `1.8` points (`GSM8K` by at most `3.5` points) across 8 models and `XSTest` benign refusal on `Qwen1.5-MoE` actually decreases (`24.0%` $\to$ `18.8%`). At half budget ($k' \approx k/2$), `ASR` jumps by `+13.4` to `+36.0 pp` (up to `+36.0 pp` on `OLMoE-0125`).
2. **Dynamic and layer-adaptive expert skipping are equally or more vulnerable**: At the ~2/3 budget under refusal suppression, dynamic `top-p` routing raises `ASR` by `+30.1 pp` (`Qwen1.5-MoE`), `+11.2 pp` (`DeepSeek-V2-Lite`), and `+8.9 pp` (`OLMoE-0125`). Layer-adaptive `LExI` (`448` targets) raises `ASR` from `35.7%` to `51.8%` (`Qwen1.5-MoE`), `15.6%` to `46.4%` (`OLMoE-0125`), and `51.3%` to `67.0%` (`DeepSeek-V2-Lite`). Per-token `ACE` at ~50% skipping raises `ASR` by `+21.0 pp` (`36.38%` $\to$ `57.37%` on `Qwen1.5-MoE`) and `+12.9 pp` (`14.96%` $\to$ `27.90%` on `OLMoE-0125`).
3. **Missing gate-weight renormalization drives the refusal-direction shift**: Every evaluated `MoE` model that does *not* renormalize retained router weights after top-$k$ selection (`Qwen1.5-MoE`, `DeepSeek-V2-Lite`, `OLMoE-0125`, plus held-out `DeepSeek-MoE-16B` and `Qwen2-57B-A14B`) suffers significant `ASR` increases under expert reduction. Restoring the original hidden-state projection along the single refusal direction at the final prompt token removes `97%` of the first-token `ASR` increase on `Qwen1.5-MoE` and `71%` on `OLMoE-0125`.
4. **Protecting prefill + the first $N=8$ tokens eliminates `90%` of the safety loss at full decode speedup**: `SafeStart` ($N=8$) bounds `ASR` changes under refusal suppression at $k' = \lceil 2k/3 \rceil$ to between `-2.1` and `+1.3 pp` across `top-k`, `top-p`, and `ACE` (pooled `top-k` $\Delta\text{ASR} = +0.4\text{ pp}$, 90% CI `[-0.6, 1.6]`). On `889` held-out requests where truncation raises `ASR` by `+21.4`, `+5.8`, and `+10.3 pp`, `SafeStart` leaves only `+0.6`, `+2.6`, and `+0.8 pp` (`90%` pooled reduction vs. `81%` for $N=1$, $p = 0.043$), while retaining `85%–101%` of truncation's offline decode speedup at batch size `8` and `88%–104%` at batch size `32` (`95.6%` of generated tokens still use $k'$).
5. **Delayed-refusal jailbreaks can outlast a fixed $N=8$ token window**: While `SafeStart` neutralizes plain and refusal-suppression prompts, adversarial framings that force benign preamble tokens before the refusal decision—such as **prefix injection** (`+12.5 pp` `ASR` on `Ling-lite-1.5` vs. `+6.8 pp` under plain truncation) and **distractor templates** (`+5.1 pp` on `Qwen1.5-MoE`)—push the refusal commitment past token $N=8$.

---

## Quantitative Summary

### Refusal-Suppression ASR (`%`) and Speedup at ~2/3 Expert Budget ($k' = \lceil 2k/3 \rceil$)

| Model (`Total / Active`, $k$, Renorm) | Full Budget `ASR` (`%`) | `Top-k` Truncation $\Delta\text{ASR}$ (`pp`) | `Top-p` Routing $\Delta\text{ASR}$ (`pp`) | `SafeStart` ($N=8$, `Top-k`) $\Delta\text{ASR}$ (`pp`) | `SafeStart` Held-Out (`889` reqs) vs. Truncation | Offline Speedup Retention (`BS=8` / `BS=32`) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `Qwen1.5-MoE` (`14.3B/2.7B`, $k=4$, No) | `46.6%` | **`+18.4 pp`** (`65.0%`) | **`+30.1 pp`** | **`-0.6 pp`** | `+0.6 pp` (vs. `+21.4 pp`) | `85%–101%` / `88%–104%` across 6 models |
| `OLMoE-0125` (`6.9B/1.3B`, $k=8$, No) | `24.2%` | **`+9.5 pp`** (`33.7%`) | **`+8.9 pp`** | **`+1.3 pp`** | `+0.8 pp` (vs. `+10.3 pp`) | (`95.6%` of decode tokens run at $k'$) |
| `DeepSeek-V2-Lite` (`15.7B/2.7B`, $k=6$, No) | `43.6%` | **`+6.6 pp`** (`50.2%`) | **`+11.2 pp`** | **`+0.6 pp`** | `+2.6 pp` (vs. `+5.8 pp`) | `TTFT` within `1%` of full budget at `BS=8` |
| Pooled 3 Non-Renorm Models | — | **`+11.5 pp`** | **`+16.7 pp`** | **`+0.4 pp`** (`[-0.6, 1.6]`) | Removes **`90%`** of rise (`81%` at $N=1$) | Kernel overhead $\le 1.0\%$ at `BS=8` (`\le 2.4%` TPOT) |

### Batch-Size Economics of MoE Expert Reduction (`vLLM 0.11.0`, RTX A6000)

| Batch Size | Offline Decode Speedup from $k' = \lceil 2k/3 \rceil$ | Why |
|:---:|:---:|:---|
| `BS = 8` | **`15%` to `28%`** across all 6 timed models (`38%–44%` at $k' \approx k/2$) | Memory-bandwidth bound: skipping experts avoids loading expert weight matrices from HBM |
| `BS = 128` | **`\le 5%`** on 4 of 6 models (`\le 3.9%` decode time saved on 3 profiled models) | Compute/routing saturation: across `128` concurrent tokens, the union of selected experts covers nearly all $E$ experts anyway |

---

## Why Not a Skill?

1. **Serving-kernel implementation scope**: `SafeStart` is a `~160`-line Triton/Python kernel modification inside `vLLM`'s fused MoE layer rather than a multi-step reasoning or workflow procedure executed by an agent.
2. **Complements existing serving checklist**: The evaluation protocol directly extends [`serving-stack-eval-checklist`](../skills/serving-stack-eval-checklist/SKILL.md) and [`moe-safety-sensitive-experts.md`](moe-safety-sensitive-experts.md) rather than warranting a separate standalone skill.

---

## Actionable Takeaways

- **Never validate MoE expert-skipping optimizations on `MMLU`/`GSM8K`/`XSTest` alone**: Active expert reduction can leave `MMLU` within `1.8` points while spiking jailbreak `ASR` by `+18.4` to `+36.0 pp`. Always include refusal-suppression (`HarmBench` / `StrongREJECT`) gates in serving-stack CI.
- **Protect prefill and the first $N=8$ decode tokens from expert pruning**: When deploying `top-k`, `top-p`, or threshold expert reduction on non-renormalizing `MoE` models, keep all $k$ experts active for prefill and the first $N=8$ generated tokens (and disable expert reduction when batch size $> 32$).
- **Combine `SafeStart` with output prefix/jailbreak guards if prefix-injection attacks are in scope**: Because prefix injection and distractor templates delay the refusal token past $N=8$ (`+12.5 pp` on `Ling-lite-1.5`), pair token-window expert protection with input/output framing defenses.

---

## Related Artifacts

- **Research Brief**: [`moe-safety-sensitive-experts.md`](moe-safety-sensitive-experts.md) — Pinpointing and protecting safety-critical routed experts in MoE LLMs.
- **Skill**: [`serving-stack-eval-checklist`](../skills/serving-stack-eval-checklist/SKILL.md) — Pre-deployment checklist for LLM serving optimizations.
- **Rules**: [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Serving-stack parity and safety regression gates.
- **Rules**: [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — Inference-time and model-level safety invariants.
