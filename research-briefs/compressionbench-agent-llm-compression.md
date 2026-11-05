# CompressionBench: How Can Your Coding Agents Compress LLMs?

> **Source**: [arXiv:2611.06858](https://arxiv.org/abs/2611.06858) | `src:2611-06858v1`
> **Authors**: Xinrui Zhong, Zhifeng Li, Zhiming Wang, Yongqi Liu, Shanglin Yang, Yang Zhou, Zikun Li, Zhuoming Chen, Beidi Chen (Carnegie Mellon University)
> **Category**: `cs.LG` / `cs.AI` (Autonomous Coding Agents / Model Compression & Quantization Benchmark)

---

## Executive Summary

**CompressionBench** evaluates whether autonomous coding agents can compress frontier open-weight LLMs end-to-end under strict disk and runtime GPU memory caps within an **8-hour** wall-clock budget on a single NVIDIA H200 NVL GPU (`vLLM 0.32.0`). Across **6** tasks — **3** models (`Nemotron-3.5 Super VL 120B-A12B` MoE, `Qwen3.5 122B-A10B` MoE, and dense `Qwen3.8 27B`) $\times$ **2** storage tiers (**32 GiB / 48 GiB** for MoEs; **8 GiB / 12 GiB** for the 27B dense model) — and **6** frontier coding agents (`Claude Sonnet 5.5`, `Claude Opus 5.5`, `GLM 5.3`, `Kimi K3.1 Pro`, `MiniMax M3.1 Flash`, `DeepSeek V4.1 Flash 1017`, all run in `Claude Code` at maximum reasoning effort), **29 of 36** submissions pass verification (**18/18** at looser limits, **11/18** at tighter limits). Selecting the lowest-perplexity verified submission per task yields only a **3.4%** average perplexity increase over BF16 while retaining **77.33%** downstream accuracy (vs **79.56%** for BF16). Crucially, trajectory analysis reveals that local layer-wise proxy metrics (weight MSE, layer-output MSE, or small-subset calibration loss) reversed rank order against complete-model evaluation in **17 of 79** matched comparisons, and likelihood improvements diverged from downstream generation accuracy or decoding throughput when agents modified kernels without end-to-end checks.

---

## Key Findings

1. **Dual Storage Enforcement (Disk Package + Post-Inference GPU Resident Memory) Is Essential**:
   - CompressionBench enforces the byte budget $C$ independently on both the serialized checkpoint directory $S_{\text{pkg}}(a) \le C$ and the live GPU memory footprint $S_{\text{res}}(a) \le C$ measured both after model loading and after inference execution (catching implementations that store packed weights on disk but leave dequantized BF16 copies resident in GPU memory during `vLLM` execution).
   - At looser budgets (`48 GiB` MoE / `12 GiB` dense), **18 of 18** runs pass both storage checks and the $\rho = 0.8$ (80%) downstream accuracy retention gate across `GSM8K` (50 items, 4-shot), `HumanEval` (50 items, 0-shot), and `TriviaQA` (50 items, 5-shot). At tighter budgets (`32 GiB` MoE / `8 GiB` dense), **11 of 18** pass (**6** fail the 80% accuracy gate and **1** times out).

2. **Complete-Model Reward Feedback Frequently Reverses Local Layer Proxies**:
   - During iterative refinement, agents routinely optimize fast local proxies (weight reconstruction MSE, per-layer activation MSE, or short calibration subsets) before querying the complete-model reward oracle (perplexity over 256 contexts $\times$ 1,536 BF16-sampled continuation tokens = 393,216 tokens from `Dolma 3 Dolmino`).
   - Across **79** matched proxy-vs-oracle comparisons from 26 runs, complete-model evaluation **reversed 17 prior local rankings** (21.5%), triggering **8** explicit rollbacks (`Kimi K3.1 Pro`: 5 rollbacks; `DeepSeek V4.1 Flash`: 3 rollbacks).
   - Conversely, within a fixed bit allocation, representation-level refinements (clipping ratios, GPTQ Hessian damping, group size tuning) that changed package size by $\le \mathbf{0.01\text{ GiB}}$ improved complete-model perplexity in **21 of 24** recorded revisions (for example, `Kimi K3.1 Pro` on `Qwen3.5 32 GiB` reduced PPL from **3.738** to **3.132**).

3. **Perplexity Optimization Alone Can Degrade Downstream Generation or Kernel Throughput**:
   - On `Qwen3.8 27B` (`8 GiB`), `Claude Opus 5.5` used bit-allocation search and self-distillation to reduce verification PPL increase from **6.17%** to **4.64%**, yet its `GSM8K` exact-match accuracy simultaneously fell from **88%** to **72%**.
   - On `Qwen3.8 27B` (`12 GiB`), `Claude Sonnet 5.5` achieved verification PPL **3.253** and **76.67%** average accuracy — outperforming both the human-engineered `GSQ-RCO` baseline (**3.334** PPL, **66.00%** accuracy) and the BF16 reference accuracy (**74.00%**) — but its custom dequantization path decoded at only **16.7 tokens/s** compared to **74.6 tokens/s** for `GSQ-RCO` and **61.4 tokens/s** for BF16.

4. **Batched-vs-Sequential Kernel Consistency Checks Catch Silent Indexing Bugs**:
   - When writing custom quantized execution paths for MoE models (`Nemotron-3.5 Super VL 120B-A12B`), `MiniMax M3.1 Flash` explicitly compared token log-probabilities between batched inference and per-expert sequential inference, uncovering an expert-indexing bug in its custom kernel and cutting verification PPL increase over BF16 from **~11%** down to **4.5%**.
   - In **17 of 36** runs, agents continued modifying model weights or code after their first natural-language completion declaration when remaining wall-clock budget allowed further iterations.

---

## Quantitative Summary

### Table 1: Task Specifications and Best Verified Agent Results vs. BF16 Reference

| Source Model | Budget $C$ | BF16 Ref PPL | BF16 Ref Acc (%) | BF16 TPS | Verified Agents | Best Verified Agent (Lowest PPL) | Best Agent PPL ($\Delta$ vs BF16) | Best Agent Acc (%) |
|:---|---:|---:|---:|---:|---:|:---|---:|---:|
| **`Nemotron-3.5 120B-A12B`** | 48 GiB | 1.688 | 80.00 | 147.5 | 6 / 6 | `Kimi K3.1 Pro` | **1.711** (+1.4%) | 79.33 |
| **`Nemotron-3.5 120B-A12B`** | 32 GiB | 1.688 | 80.00 | 147.5 | 4 / 6 | `Kimi K3.1 Pro` | **1.760** (+4.3%) | 76.67 |
| **`Qwen3.5 122B-A10B`** | 48 GiB | 2.755 | 84.67 | 158.3 | 6 / 6 | `Claude Opus 5.5` | **2.801** (+1.7%) | 84.00 |
| **`Qwen3.5 122B-A10B`** | 32 GiB | 2.755 | 84.67 | 158.3 | 4 / 6 | `Kimi K3.1 Pro` | **2.927** (+6.2%) | 80.67 |
| **`Qwen3.8 27B` (Dense)** | 12 GiB | 3.221 | 74.00 | 61.4 | 6 / 6 | `Claude Sonnet 5.5` | **3.253** (+1.0%) | 76.67 |
| **`Qwen3.8 27B` (Dense)** | 8 GiB | 3.221 | 74.00 | 61.4 | 3 / 6 | `Claude Opus 5.5` | **3.370** (+4.6%) | 66.67 |
| **6-Task Mean** | — | — | **79.56** | — | **29 / 36** | **Task-Best Ensemble** | **+3.4% avg PPL** | **77.33** |

*(Note: The $\rho = 0.8$ accuracy gate is evaluated against fixed reference accuracies $A(p)$ of **81.33%** for `Nemotron-3.5`, **85.33%** for `Qwen3.5`, and **74.00%** for `Qwen3.8`.)*

### Table 2: Trajectory & Verification Diagnostics Across 36 Agent Runs

| Diagnostic Metric | Measured Value | Operational Implication |
|:---|---:|:---|
| **Looser-budget verification pass rate** | **18 / 18** (100%) | All 6 frontier agents reliably solve 4-bit / mixed-precision packaging at 48 GiB / 12 GiB. |
| **Tighter-budget verification pass rate** | **11 / 18** (61.1%) | Sub-3-bit compression (32 GiB MoE / 8 GiB dense) causes 6 accuracy-gate failures and 1 timeout. |
| **Local proxy vs. complete-model rank reversals** | **17 / 79** (21.5%) | Layer/weight MSE frequently misranks quantization edits; caused 8 explicit rollbacks. |
| **Fixed-size ($\le 0.01\text{ GiB}$) representation wins** | **21 / 24** (87.5%) | Tuning clipping, damping, and group scales improves PPL without increasing byte footprint. |
| **Runs modifying weights after first completion claim** | **17 / 36** (47.2%) | Natural-language "done" claims are unreliable stopping signals when compute budget remains. |

---

## Why Not a Skill?

`CompressionBench` is a benchmark suite and empirical trajectory study evaluating how existing coding agents (`Claude Code` with 6 LLM backbones) tackle LLM quantization under fixed hardware constraints, rather than proposing a novel agent algorithm or reusable subtask skill. Its value lies in its quantitative findings on proxy-vs-oracle rank reversals, dual disk/VRAM storage verification, and batched-vs-sequential kernel consistency checks.

---

## Actionable Takeaways

1. **Gate Systems/ML Optimization Loops on Complete-Model Oracles, Not Layer-Local Proxies**: Because local layer MSE and small calibration subsets reverse rankings on **21.5% (17/79)** of candidate revisions, use local proxies only to filter obvious failures and require a full-model validation check before committing a checkpoint (enabling the 8 rollbacks observed in `Kimi` and `DeepSeek`).
2. **Audit Both Disk Footprint and Post-Inference Resident VRAM, Plus Decoding Throughput**: When evaluating agent-generated model compression or systems patches, verify resident GPU memory *after* running a warmup + generation pass (to catch persistent dequantized buffers) and include a minimum tokens/sec floor alongside perplexity and multi-task generation accuracy (`GSM8K`, `HumanEval`, `TriviaQA`).
3. **Require Batched-vs-Sequential Equivalence Tests for Custom MoE/Quantized Kernels**: When an agent writes or patches custom inference routing or dequantization code, require a deterministic test asserting that batched token log-probabilities match single-token / per-expert sequential execution (which caught an expert-indexing bug in `MiniMax` and cut PPL degradation from ~11% to 4.5%).

---

## Related Artifacts

- [`rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Multi-metric evaluation gates and benchmark integrity rules.
- [`rules/recursive-improvement.md`](../rules/recursive-improvement.md) — "DO: Build a diagnostic instrument before acting" and "DON'T: Accept modifications based on aggregate metrics alone".
