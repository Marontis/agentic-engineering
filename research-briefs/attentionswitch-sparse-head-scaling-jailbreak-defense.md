# AttentionSwitch: Jailbreak Defense for LLMs via Joint Learning of Sparse Attention-Head Selection and Scaling

> **Source**: [arXiv:2611.08752](https://arxiv.org/abs/2611.08752) — Obidov, Yu, Guo, & Yang (2026)
> **Praxis Source ID**: `src:2611-08752v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`AttentionSwitch` is an internal white-box model intervention that requires registering forward hooks inside the multi-head self-attention layers of a frozen open-weight transformer and running three-stage gradient-based optimization (Gumbel-Softmax Top-$K$ relaxation) over internal attention-head outputs. Because it operates on internal model activations and gradients rather than at the agent harness, prompt, tool, or orchestration layer, it cannot be executed as a model-agnostic agent engineering procedure and is captured here as a research brief.

---

## Core Contribution

Existing component-level jailbreak defenses (such as `ASGuard`, `DeTAM`, `CAST`, and `AdaSteer`) follow a sequential *diagnose-then-intervene* paradigm: they first identify safety-relevant layers or attention heads using a static heuristic and subsequently optimize an intervention at those fixed locations. Because the optimal subset of heads depends on how strongly each head is modified—and vice versa—decoupling site selection from intervention strength yields suboptimal robustness, especially in low-data regimes.

**AttentionSwitch** is the first jailbreak defense to **jointly optimize where to intervene (sparse attention-head selection) and how strongly to intervene (query-conditioned multiplicative scaling)** under a shared autoregressive defense objective within a frozen LLM:

1. **Direction-Preserving Whole-Head Output Scaling**: For a selected head $h$ in layer $\ell$ at input-prompt token position $t$, `AttentionSwitch` multiplies the head-output vector $\mathbf{o}_{\ell ht} \in \mathbb{R}^{d_h}$ by a single positive scalar $\alpha_{\ell ht} > 0$:
   $$\widehat{\mathbf{o}}_{\ell ht} = \alpha_{\ell ht}\,\mathbf{o}_{\ell ht}, \qquad \alpha_{\ell ht} = \exp\!\left[\lambda\,g\!\left(\frac{\widetilde{\mathbf{q}}_{\ell ht}^{\top}\mathbf{w}_{\ell h}}{\sqrt{d_h}} + b_{\ell h}\right)\right]$$
   where $\widetilde{\mathbf{q}}_{\ell ht}$ is the RMS-normalized query vector of head $h$. Applying a uniform positive scalar per head changes the magnitude of the head's contribution ($\alpha_{\ell ht} < 1$ attenuates, $\alpha_{\ell ht} > 1$ amplifies, $\alpha_{\ell ht} = 1$ is identity) while strictly preserving the direction and relative feature composition of $\mathbf{o}_{\ell ht}$.
2. **Input-Prefill-Only Execution**: At inference time, scaling is applied **only while processing the input prompt** and never at generated-token positions. The defense shapes autoregressive decoding solely through the cached key and value (KV) states of the input prompt, adding only $K(d_h + 1)$ controller parameters ($\sim 10^4$ parameters, or $1.9 \times 10^{-4}\%$ to $3.8 \times 10^{-4}\%$ of base model parameters at a $20\%$ head budget).
3. **Three-Stage Joint Gumbel-Top-$K$ Optimization**: Each of the $N$ attention heads is assigned a trainable selector logit $s_j$ perturbed with $\operatorname{Gumbel}(0, 1)$ noise ($z_j = s_j + \gamma_j$), using discrete $K$-hot forward selection $\overline{m}_j = \mathbb{I}[j \in \operatorname{TopK}(\mathbf{z}, K)]$ and straight-through softmax surrogate gradients $\widetilde{\mathbf{m}} = K\operatorname{softmax}(\mathbf{z}/\tau)$ in the backward pass:
   - **Stage 1 (Initialization)**: Optimize scaling parameters $\phi = \{\mathbf{w}_{\ell h}, b_{\ell h}\}$ with all $N$ heads active.
   - **Stage 2 (Joint Search)**: Simultaneously optimize head-selector logits $\psi = \{s_j\}_{j=1}^N$ and scaling parameters $\phi$ under the shared negative log-likelihood objective (pairing harmful prompts with native model refusal continuations and benign prompts with undefended continuations).
   - **Stage 3 (Refinement)**: Remove Gumbel noise, fix the deterministic Top-$K$ heads ($20\%$ by default), discard $\psi$, and fine-tune $\phi$ on the fixed sparse head subset.

---

## Key Empirical Results

Evaluated across **5 open-weight LLMs** (`Llama-3.1-8B-Instruct`, `DeepSeek-LLM-7B-Chat`, `OpenChat-3.5-1210`, `Vicuna-13B-v1.5`, and `Gemma-3-27B-IT`) against **9 jailbreak attacks** (`Plain Harmful`, `Human-Crafted`, `GCG` seen during training; `PEZ`, `UAT`, `AutoPrompt`, `GBDA`, `GCG-M`, and `PAIR` evaluated zero-shot across $2,115$ unseen harmful test prompts, $500$ benign instruction prompts, and $250$ contextual over-refusal prompts):

### 1. Main Robustness vs. Utility Trade-Off ($n = 30$ and $n = 120$ Training Samples)

| Metric (5-Model Average) | Undefended | AttentionSwitch ($n=30$ / $n=120$) | SFT ($n=30$ / $n=120$) | LoRA-SFT ($n=30$ / $n=120$) | ASGuard ($n=30$ / $n=120$) | DDPO ($n=30$ / $n=120$) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Attack Rejection Rate (ARR % $\uparrow$)** | 71.21% | **96.58%** / **99.05%** | 96.14% / 98.74% | 95.63% / 88.04% | 79.46% / 85.56% | 95.98% / 97.29% |
| **Benign Pass Rate (BPR % $\uparrow$)** | 99.08% | **97.68%** / **96.84%** | 24.64% / 25.64% | 67.60% / 61.08% | **97.84%** / 93.16% | 91.16% / 95.64% |
| **Over-Refusal Rate (ORR % $\downarrow$)** | 8.64% | **10.08%** / 13.04% | 81.60% / 83.76% | 32.72% / 40.80% | 11.68% / 16.88% | 12.16% / **9.28%** |
| **MMLU ($\uparrow$)** | 57.68 | **57.72** / **57.66** | 32.43 / 32.21 | 41.82 / 25.91 | 57.49 / 57.47 | 55.43 / 54.60 |

- **Per-Model Highlights (Table 1)**:
  - `Llama-3.1-8B-Instruct`: ARR rises from `87.47%` (None) to `99.57%` ($n=30$) and `99.43%` ($n=120$) with `98.00%` / `97.80%` BPR and `53.63` / `53.13` MMLU (vs. SFT collapsing BPR to `4.40%` / `10.40%` and MMLU to `24.15`).
  - `DeepSeek-LLM-7B-Chat`: ARR rises from `61.70%` (None) to `92.10%` ($n=30$) and `98.53%` ($n=120$) with `97.60%` / `96.40%` BPR (vs. `ASGuard` stuck at `62.13%` / `62.74%` ARR).
  - `OpenChat-3.5-1210`: ARR jumps from `43.22%` (None) to `91.58%` ($n=30$) and `97.35%` ($n=120$) with `98.20%` / `97.00%` BPR and `4.40%` / `7.60%` ORR.
  - `Vicuna-13B-v1.5`: ARR rises from `77.83%` (None) to `99.76%` ($n=30$) and `100.00%` ($n=120$) with `95.40%` / `93.60%` BPR.
  - `Gemma-3-27B-IT`: ARR rises from `85.82%` (None) to `99.86%` ($n=30$) and `99.95%` ($n=120$) with `99.20%` / `99.40%` BPR and `72.65` MMLU.

### 2. Ablations: Joint vs. Sequential Selection and Head Sparsity Budget

- **Joint Selection vs. All-Heads and Sequential Selection ($n=30$)**: Jointly selecting and scaling $20\%$ of heads achieves **96.58% ARR** (`97.68%` BPR), outperforming scaling **100% of heads** (**92.26% ARR**, `97.36%` BPR) and **non-joint selection** where the top $20\%$ of heads are chosen by `ASGuard` first and then scaled by `AttentionSwitch` (**94.73% ARR**, `97.52%` BPR). On prompts where `AttentionSwitch` and the comparison variant disagree, `AttentionSwitch` makes the correct rejection decision in **85.58%** of cases against the all-head variant and **79.60%** of cases against the sequential `ASGuard`-selector variant.
- **Sparsity Sweet Spot (Table 6)**: Across $n \in \{30, 60, 120\}$, ARR peaks when **20%–30% of attention heads** are scaled and degrades when either too few or too many heads are modified:
  - At **1% of heads**, average ARR is only `81.70%` (`77.55%` at $n=30$, `81.80%` at $n=60$, `85.76%` at $n=120$) with high standard error ($\pm 7.99\%$ to $\pm 8.87\%$).
  - At **20% of heads**, average ARR reaches `98.11%` (`96.58%` at $n=30$, `98.69%` at $n=60$, `99.05%` at $n=120$) with `97.24%` average BPR and low standard error ($\pm 0.50\%$ to $\pm 1.93\%$).
  - At **30% of heads**, ARR reaches `96.43%` ($n=30$), `98.68%` ($n=60$), and `99.28%` ($n=120$).
  - At **100% of heads**, ARR drops back to `92.26%` ($n=30$), `95.83%` ($n=60$), and `96.73%` ($n=120$) with rising variance.

### 3. Adaptive Attacks and Runtime Overhead

- **Adaptive White-Box (`Adaptive GCG`) and Black-Box (`Adaptive PAIR`) Attacks**: When attackers optimize directly against the defended model ($n_{\text{train}}=30$, $20\%$ heads, 50 test prompts), `AttentionSwitch` maintains **86.80% average ARR** under `Adaptive GCG` (vs. `97.62%` non-adaptive, achieving `100.00%` on `Llama-3.1` and `Gemma-3`, `92.00%` on `Vicuna`, `90.00%` on `OpenChat-3.5`, and `52.00%` on `DeepSeek`) and **77.60% average ARR** under `Adaptive PAIR` (vs. `92.26%` non-adaptive).
- **Training and Inference Efficiency**: Training takes **63.20 s** ($n=30$) and **294.66 s** ($n=120$) on average—more than $2\times$ faster than full SFT (`152.53 s` and `616.87 s`) and faster than LoRA-SFT (`107.02 s` and `437.41 s`). Because scaling executes only during input prefill, per-sample generation latency averages **202.07 ms** compared with **196.93 ms** for the undefended LLM (+`5.14 ms`, or $+2.6\%$) and **226.94 ms** for `DDPO`.

---

## Takeaways for Agentic Systems

1. **Sparse, Coupled Intervention Outperforms Dense Fine-Tuning in Low-Data Regimes**: With as few as 15 harmful and 15 benign examples ($n=30$), full SFT and LoRA-SFT destroy general reasoning utility (MMLU drops from `57.68` to `32.43` and `41.82`; BPR drops to `24.64%` and `67.60%`), whereas rescaling $20\%$ of attention heads via magnitude-only scalars preserves `57.72` MMLU and `97.68%` BPR.
2. **Prefill-Only KV-Cache Conditioning Suffices for Refusal Steering**: Modifying attention-head magnitudes strictly over input-prompt tokens—without intervening during token-by-token autoregressive generation—is sufficient to steer the KV cache toward refusal on adversarial inputs while keeping decoding latency virtually unchanged.

## Cross-References

- [`hallucination-mean-shift-probe`](../skills/hallucination-mean-shift-probe/SKILL.md) — Lightweight internal activation probing for model reliability
- [`layered-defense-ensemble`](../skills/layered-defense-ensemble/SKILL.md) — Combining model-level and harness-level safety defenses
- [`addition-by-subtraction-safety-alignment.md`](addition-by-subtraction-safety-alignment.md) — Related internal head/component surgical safety alignment findings
- [`active-adaptation-preventative-steering.md`](active-adaptation-preventative-steering.md) — Representation steering defenses for LLM safety
- [`rules/adk-security-and-evaluation.md`](../rules/adk-security-and-evaluation.md) — Security evaluation and red-teaming standards
