# BaseRSI: Recursive Self-Improvement of a Base Vision-Language Model via Training-Free Harness Internalization

> **Source**: [arXiv:2611.24578](https://arxiv.org/abs/2611.24578) — Mingda Zhang, Yuanhao Dong, Qiang Huang, Rui Qian, Yanjin Li, Zhenyu Liu, Xiao Huang, Zihao Yang, Jian Wang, Pinjia He, Xiaoying Tang (CUHK-Shenzhen, NUS, Fudan University, UIUC, University of Melbourne, Shanghai Jiao Tong University, November 2026)
> **Praxis Source ID**: `src:2611-24578v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`BaseRSI` is a **white-box Transformer weight-editing algorithm** (`ReGap` + `ReKey`) that directly rewrites vision patch-embedding kernels ($\mathbf{K}' = \mathbf{B}^\top \mathbf{K}$) and low-activity SwiGLU MLP gate/up/down neuron rows across `64` hybrid linear/full-attention blocks using per-block causal hidden-state replay in PyTorch. Because it requires direct tensor access to internal Transformer sublayers and vision patch projections, it is not a model-agnostic prompt/tool workflow skill. We document its training-free harness internalization mechanics and critical ablations here and distill its multi-benchmark gating and internalization invariants into [`recursive-improvement.md`](../rules/recursive-improvement.md).

---

## Core Mechanism: Forward-Only Harness Discovery & `ReGap`/`ReKey` Internalization

External harness RSI (`RRSI`, `Meta-Harness`, `GEPA`, `SkillOpt`) leaves base weights untouched and permanently pays inference-time token/wrapper overhead, while gradient post-training (`SFT`, `GRPO`) costs `3.5x–5.1x` more GPU hours and degrades OOD visual grounding on small self-labeled splits (`arXiv:2611.24578`). `BaseRSI` turns transient harness gains into permanent base-model weight edits **with zero backward passes and zero external API calls**:

1. **Leave-One-Benchmark-Out (`LOBO`) Harness Discovery (`8` Generations, `269` Candidates)**:
   - Using the current VLM itself as proposer on `640` development items (`270` fitting + `370` validation across `5` ID benchmarks), `BaseRSI` searches over input-view transforms and reasoning/counting wrappers, accepting a harness entry **only if it improves macro validation accuracy AND stays non-negative on every leave-one-benchmark-out subset under Holm-corrected sign-flip testing ($\alpha = 0.10$)**.
   - Across `8` generations on `Qwen3.8-27B` (`27.78B` total / `25.62B` LM weights, $L = 64$ blocks: `48` linear-attention + `16` full-attention, $H = 5120$), the gate admitted exactly `2` complementary entries: a **finer visual grid** (`patch size 16 -> 8`, `2,048–4,096` image tokens) and a **structured counting procedure**.
2. **Site-Matched `ReKey` + Block-Local Causal `ReGap` (`0.230%` Modified Weights)**:
   - **Vision site (`ReKey`)**: Internalizes the finer-grid view directly into the vision patch-projection kernel via adjoint resampling $\mathbf{K}' = \mathbf{B}^\top \mathbf{K}$ rather than forcing language MLP layers to compensate for missing pixels.
   - **Reasoning site (`ReGap` + SwiGLU `ReKey`)**: Measures each block $\ell$'s **causal activation gap** by running **only block $\ell$** under the teacher harness context while keeping blocks $1 \dots \ell-1$ on the clean student prefix (isolating block $\ell$'s marginal causal contribution rather than raw multi-layer state drift: unit step along `ReGap` cuts teacher KL from `0.0977` to **`0.0003`** [`99.65%` next-token agreement; `< 10^{-10}` in `fp32`] vs. `0.0235` under raw state difference).
   - **Least-active neuron targeting & `J = 3` student-response replay**: Projects rank-`64` SVD factors of `ReGap` into the **`65` least-active SwiGLU neurons per block** (`4,160` neurons = `63,897,600` scalars = **`0.230%` of total weights** / `0.249%` of LM weights, leaving **`99.77%` bit-identical**; line-searched step $\gamma = 1.8$) over $J = 3$ rounds of the **student's own generated responses** (`344` responses) so edited weights remain calibrated on their own rollout distribution.

---

## Key Empirical Results (`3` Seeds `0, 1, 2`)

### 1. `Qwen3.8-27B` ID (`5` Benchmarks, `640` Items) & Strictly Held-Out OOD (`5` Benchmarks, `640` Items) (`Tables 1, 5, 6`)

ID benchmarks: `BabyVision`, `BLINK`, `CharXiv`, `VisuLogic`, `VLMs Are Biased`. Held-out OOD benchmarks: `ChartQAPro`, `HallusionBench`, `PerceptionBench`, `SpatialViz`, `VisualPuzzles`.

| Method Category & System | ID Mean (`%`) | Held-Out OOD Mean (`%`) | Compute (`H800` GPU h) | External API Tokens |
|:---|:---:|:---:|:---:|:---:|
| **Base `Qwen3.8-27B`** (zero-shot) | `60.4` | `64.5` | `0` | `0` |
| **Prompting / Zoom**: `CoT` / `Self-Refine` / `Two-stage zoom-in` | `62.4` / `62.2` / `63.4` | `67.1` / `68.4` / `68.4` | — | `0` |
| **Harness RSI**: `ACE` / `VideoHarness-RSI` / `SkillOpt` / `GEPA` / `Meta-Harness` / `RRSI` | `59.3`–`65.1` (`RRSI` `65.1`) | `65.0`–`68.3` (`RRSI` `68.3`) | `51.4`–`186.6` | `0`–frontier |
| **Gradient Post-Training**: `SFT` / `GRPO` / `PixelProof` / `LBS-27B` | `60.9` / `61.2` / `61.7` / `62.7` | `65.1` / `63.9` / `65.3` / `64.3` | `159.3` (`GRPO`)–`230.9` (`SFT`) | `0` |
| **Closed References**: `Claude Haiku 5.5` / `GPT-6 Luna` | `57.4` / `54.4` | `65.6` / `57.4` | — | API |
| **Un-internalized discovered harness** (kept in prompt at test time) | `69.6` | `68.4` | `40.9` | `0` |
| **`BaseRSI` (Internalized Base Model, `0` test-time harness)** | **`72.1`** (**`+11.7 pp`**, $p = 0.003$) | **`70.7`** (**`+6.1 pp`**, $p = 0.005$) | **`45.5`** (`40.9` search + `4.6` edit) | **`0`** |

- **Internalized weights beat the live external harness itself (`+2.5 pp` ID, `+2.3 pp` OOD)**: Removing prompt-wrapper verbosity and multi-pass interference via `ReGap`/`ReKey` lifted accuracy *above* running the exact same discovered harness at inference (`72.1%` vs. `69.6%` ID; `70.7%` vs. `68.4%` OOD) at base-model inference cost, while using fewer GPU hours (`45.5 h`) than every harness-search (`51.4–186.6 h`) and gradient-training (`159.3–230.9 h`) baseline.
- **Cross-architecture replication (`Table 18`, `30/30` benchmark cells positive)**: Across `Gemma-4-31B` (`44.6% -> 56.0%` ID `[+11.4]`, `59.9% -> 65.2%` OOD `[+5.3]`), `Qwen3.6-27B` (`48.3% -> 58.2%` `[+9.8]`, `60.5% -> 64.4%` `[+4.0]`), and `Qwen3.5-9B` (`46.7% -> 52.7%` `[+6.0]`, `56.7% -> 59.1%` `[+2.4]`), every single ID and OOD benchmark improved across all four backbones.

### 2. Failure-Mode Ablations (`Tables 2, 8–14, 19–24`)

- **Block-local `ReGap` vs. output-logit distillation**: Standard output-only logit distillation reached `68.9%` ID / `67.9%` OOD (`69.8%` / `69.1%` on the same `4,160` neurons), and gradient output-loss updates yielded negative latent restoration (`-0.052 ± 0.159` vs. `+0.593 ± 0.043` closed-form `ReKey`).
- **Catastrophic interference when overwriting active neurons or wrong physical sites**: Overwriting the **`65` most-active neurons** instead of the `65` least-active neurons collapsed restoration to **`-2.119 ± 0.742`** and ID/OOD accuracy to **`65.1% / 65.3%`**. Writing the visual-grid entry into language MLP neurons instead of the patch kernel collapsed ID/OOD to **`62.6% / 65.2%`** (`BabyVision` `60.7% -> 38.3%`).
- **Student-response replay & LOBO gating**: Fitting `ReKey` on teacher-only (`70.8% / 68.3%`) or base-only (`70.5% / 67.9%`) responses trailed `J = 3` student-response replay (`72.1% / 70.7%`), and replacing LOBO sign-flip gating with macro-average-only acceptance dropped ID/OOD to `71.1% / 68.8%`.

---

## Related Artifacts

- **Rules**: [`recursive-improvement.md`](../rules/recursive-improvement.md) (`"DO: Internalize leave-one-benchmark-out verified harness gains via site-matched causal activation gaps and student-response replay into low-activity neurons"` and `"DO: Alternate model weight updates and harness search"`)
- **Skills**: [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md) (`RRSI`, `arXiv:2609.24972`)
- **Research Briefs**: [`joint-harness-weight-optimization`](./joint-harness-weight-optimization.md) (`WHALE`, `arXiv:2609.00196`), [`self-evolving-multimodal-agents-cross-scenario-survey`](./self-evolving-multimodal-agents-cross-scenario-survey.md) (`arXiv:2611.14256`)
