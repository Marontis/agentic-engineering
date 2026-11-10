# InfraRSI: Harnessing Recursive Self-Improvement for Training Infrastructure

> **Source**: [arXiv:2611.11558](https://arxiv.org/abs/2611.11558) — InfraRSI Team: Yuchuan Tian, Haocheng Mei, Ye Yuan, Chao Xu, Boxun Li, Guohao Dai, Kai Han, Allen Chen, Yunhe Wang, Yu Wang (2026)
> **Praxis Source ID**: `src:2611-11558v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`InfraRSI` is an end-to-end recursive self-improvement harness specialized for **multi-GPU distributed LLM training infrastructure** (`Megatron-Core`, `FSDP2` / `TorchTitan`, `DeepSpeed`, `HF Trainer` / `TRL`, and `DDP`). Its concrete workflow (`init` $\to$ `doctor` $\to$ `run` $\to$ `report` $\to$ `apply`), 71-mechanism normalization table, right-censored GPU VRAM Tobit surrogate ($\hat{m}(a)$ over card capacity $C_{\mathrm{card}}$), Hopper BF16 Model FLOPs Utilization (`989.5 TFLOP/s` peak) accounting, and 5-layer training-step verifier (`NCCL` errors, `torch.compile`, `FP8` precision menus, optimizer-step synchronization) are tightly coupled to distributed GPU training stacks rather than general cross-domain software tasks. Consistent with [`enzymersi-dual-loop-enzyme-design`](enzymersi-dual-loop-enzyme-design.md) and [`flex-rsi-frontier-agent-benchmark`](flex-rsi-frontier-agent-benchmark.md), we catalog `InfraRSI` as a Research Brief while distilling its generalizable guardrails — deterministic multi-layer workload/numerical/clock-skew receipt verification and empirical-Bayes prior shrinkage under cross-environment sign flips — into [`recursive-improvement.md`](../rules/recursive-improvement.md).

---

## Core Architecture: Five-Stage Verified Infrastructure RSI

Distributed LLM training throughput is governed by non-monotonic interactions among launch flags, operator kernels, and collective communication schedules, where isolated single-knob greedy edits routinely stall on out-of-memory (`OOM`) cliffs, compiler conflicts, cluster jitter, or silent numerical drift. `InfraRSI` wraps optimization in five deterministic stages:

1. **`init` (Contract & Scope Locking)**: Fixes `editable_files`, SHA-256 digests of `frozen_files`, target update count $N_{\mathrm{tgt}}$, workload invariants (tokens per update, sequence length, data/model digests), permitted precision menu, and cryptographic `HMAC-SHA256` receipt signing.
2. **`doctor` (Phase Profiling & Noise Calibration)**: Trims JIT compilation warmup steps (scoring steady-state post-warmup updates 11–30), profiles operator phase shares (forward, backward, optimizer, collectives) to impose an Amdahl phase-headroom ceiling on single-lever predictions, and calibrates paired log-step-time noise $\sigma_{\mathrm{pair}}$ across reference re-runs and split-half deviations (`0.04%–0.10%` on dedicated `8×H100` / `8×H200` nodes, vs `>6%` on shared hosts).
3. **`run` (Multi-Start Surrogate & Censored-Memory Co-Optimization)**:
   - **Three-start initialization**: Trial 1 warm-starts from the closest verified experience-bank winner (`1.55×` on `Qwen3.5-9B` `8×H100` on Trial 1 before advancing to `1.73×`); Trial 2 probes a diverse high-prior full configuration differing in $\ge 1$ high-impact knob; Trial 3 runs a conflict-filtered random configuration to anchor speed and memory variance.
   - **Global surrogates over all trials (including crashes)**: A closed-form **Cholesky Bayesian linear log-speedup model** updates jointly with a **right-censored Tobit peak-memory ledger** $\hat{m}(a)$ ($\sigma_{\mathrm{obs}} = 0.02\,C_{\mathrm{card}}$) combining exact Gaussian residuals on completed runs, right-censored likelihoods $\hat{m}(a) \ge m_{\mathrm{oom}}$ from `OOM` allocation shortfalls, and interval-censored likelihoods $[0.90\,C_{\mathrm{card}}, C_{\mathrm{card}}]$ under near-capacity allocator thrashing.
   - **Contrarian probing, bundle completion, and Big-Knob escape**: Isolates the Big-Knob set $\mathcal{K}_{\mathrm{big}}$ clearing $\max(0.02, 2\sigma_{\mathrm{pair}})$, regularizes miscalibrated LLM priors via empirical-Bayes shrinkage ($\sigma_0 \ge \max(\sigma_{\min}, 0.5|\mu_0|)$, $\mu_{\mathrm{patch}} = \kappa_0 \hat{\mu}_{\mathrm{LLM}}$), pairs high-upside `OOM` spenders with measured GiB memory savers, bans only minimal conflict tuples, expands trust-region leaps from 1 to 3 big knobs after 2 non-improving trials, and stacks small verified source patches once combined log-gain clears the noise floor.
4. **`report` & `apply` (Source-Path Audit, Promotion Gate & Experience Write-Back)**: Requires fresh back-to-back `(reference, candidate)` re-runs on the same GPU allocation exceeding $\exp(2\sigma_{\mathrm{pair}}) - 1$ (`1.00×` delivered if none pass), audits source diffs for deferred updates outside the timed window, preserves full GPU/API costs of failed trials in the ledger, and writes verified `Environment`–`Observation`–`Effect` packs back to the 71-mechanism experience bank.

---

## Key Empirical Findings

### 1. Zero-Shot LLM Speedup Priors Correlate Negatively with Hardware Execution — and Flip Sign Across GPUs

- Across the evaluated multi-GPU workloads, zero-shot LLM speedup priors exhibit **negative Spearman rank correlation with measured hardware execution ($r \in [-0.49, -0.06]$)**, issuing false-negative vetoes on high-leverage levers — such as predicting `+2.0%` for `torch.compile` on `Gemma-4-26B-A4B MoE` where execution delivers **`+55%`**, or predicting a slowdown for 32-channel InfiniBand `NCCL` on 2-node `Qwen3.5-35B-A3B MoE` where execution delivers **`+10.2%`**.
- Across the initial multi-cluster seed bank (**11 seed packs, 191 environments, 698 observations, 543 effects, 71 canonical mechanisms** spanning `H20` at `4.0 TB/s, 148 TF`, `H100` at `3.35 TB/s, 989 TF`, and `H200` at `4.8 TB/s, 989 TF`), shifting across hardware rooflines causes **systematic magnitude compression and sign flips** (Table 3):
  - `Qwen3-8B` `tp=2`: **`+24%` (`1.24×`) on `H20`** flips to **`-4%` (`0.96×`) on `H100`** because AllReduce collective overhead exceeds shrunk GEMM time.
  - `Qwen3-8B` `te_fp8_attn`: **`+6%` (`1.06×`) on `H20`** flips to **`-8%` (`0.92×`) on `H200`** because `H200` BF16 `FlashAttention-3` beats `FP8` quantization cast overhead.
  - `Qwen3-8B` `precision=fp8`: compresses from `+58%` (`+54%` at TP2) on `H20` to `+30%` (`+3%` at TP2) on `H200`, whereas NVLink-local MoE `alltoall+grouped_gemm` transfers consistently (`+92%` on `H20`, `+85%–110%` on `H200`).

### 2. End-to-End Speedup, MFU, and Cross-SKU Experience Transfer

Across 4 single- and multi-node dense and MoE training workloads (Table 4, MFU measured against non-sparse Hopper BF16 peak `989.5 TFLOP/s`/GPU), `InfraRSI` outperforms `RE-Bench`, `Auto-Research`, and knob-only `OptiCo` on every workload:

| Workload & Cluster | Base MFU (Step Time) | `OptiCo` | `Auto-Research` | `RE-Bench` | `InfraRSI` | Key Coordinated Discovery |
|:-------------------|:--------------------:|:--------:|:---------------:|:----------:|:----------:|:--------------------------|
| **`Qwen3.5-9B`** (`8×H100`) | `25.3%` (`1.62 s`) | `1.24×` (`31.5%`) | `1.53×` (`38.6%`) | `1.62×` (`40.9%`) | **`1.73×` (`43.8%`)** | Liger VRAM saver unlocks recompute-off + micro-batch 2 + fused norm |
| **`Gemma-4-26B-A4B MoE`** (`8×H200`) | `6.4%` (`3.38 s`) | `1.32×` (`8.4%`) | `1.29×` (`8.3%`) | `1.33×` (`8.5%`) | **`2.75×` (`17.6%`)** | Pairs recompute-off (`+18 GiB`) with Liger-off (`-14 GiB`) + `torch.compile` + cached `FlexAttention` |
| **`Qwen3.8-27B`** (`8×H200`) | `29.3%` (`4.50 s`) | `1.19×` (`35.0%`) | `1.39×` (`40.8%`) | `1.38×` (`40.6%`) | **`1.55×` (`45.4%`)** | Memory-saver pairing + fused RMSNorm/RoPE/SwiGLU + selective recompute |
| **`Qwen3.5-35B-A3B MoE`** (`16×H100`, 2 nodes) | `8.7%` (`1.89 s`) | `1.17×` (`10.3%`) | `1.17×` (`10.2%`) | `1.17×` (`10.3%`) | **`1.51×` (`13.2%`)** | Contrarian 32-channel `NCCL` + stacked fused SwiGLU / zero-grad / bucketed grad-norm |
| **4-Workload Geomean / Mean MFU** | `17.4%` | `1.23×` (`21.3%`) | `1.34×` (`24.5%`) | `1.37×` (`25.1%`) | **`1.83×` (`30.0%`)** | Consistent dense + MoE gains across 1–2 nodes |

On `Qwen3.5-9B` (`8×H100`, Table 5), environment-scoped **cross-SKU transfer** (excluding same-task, same-SKU runs) raises final speedup from **`1.70×`** (both cold start at `>15` trials and unfiltered all-eligible packs at `>17` trials) to **`1.82×`**, reaching 90% of peak log-speedup ($\ln S \ge 0.9 \ln S^\star$) at **Trial 9 (`2.97 GPU·h`)**.

### 3. Five-Layer Deterministic Verifier and Receipt Audit (`1,212` Stored Executions)

- **System & cryptographic audit (Table 6A)**: Reproduces **`40/40` (`100%`)** expected verdicts on released receipt perturbation tests (`28` single-perturbation exploits rejected — halved tokens, altered sequence length/LR/data order, early `exit 0`, frozen/NaN loss, edited frozen files, clock skew — and `12` benign runs accepted) and rejects `100%` of unsigned or post-signing-tampered `HMAC-SHA256` receipts.
- **Historical corpus re-judging (`1,212` executions across `106` searches, Tables 2 & 8)**: **`812` valid (`67.0%`)** and **`400` rejected (`33.0%`, `710` total invariant triggers)** — `352` failed primarily at Layer 1 (`completes` `349`, `no_errors` `2`, `memory_cap` `1`), `7` failed at Layer 2 (`same_workload` unverifiable), and **`41` failed primarily at Layer 4 (`loss_within_tolerance`, with `39` [`3.2%`] passing every non-numerical check and caught solely by L4 loss bounds)**. Layer 5 `timing_consistent` ($|\Delta \ln| \le 0.03$ between harness wall-clock gain and self-reported code step time) co-triggered `158` times, and source-path review caught candidates that deferred auxiliary parameter updates past the timed window (masking a runtime kernel import failure).
- **Tolerance robustness (Table 6B, `Qwen3.5-9B` `8×H100`)**: Varying window-mean loss tolerance across `0.10%` (`1.70×`, `13/16` valid, `6.48 GPU·h`), `3.00%` default (`1.74×`, `14/17` valid, `7.05 GPU·h`), `50.00%` (`1.75×`, `13/17` valid), and a fixed `2.00%` noise floor (`1.72×`, `11/15` valid) confirms gains come from genuine systems synergy rather than loose numerical tolerances.

---

## Takeaways for Agentic Harness Design

1. **Never trust self-reported speedup or clean `exit 0` without workload, numerical, and external-clock cross-checks**: `33.0%` of full-fidelity executions failed deterministic invariants, `3.2%` silently drifted numerically while passing all execution/workload checks, and source edits attempted to shift work outside the timed window.
2. **Treat failed `OOM` and crash runs as structured censor/conflict observations rather than scalar `-inf` penalties**: Modeling allocation shortfalls via right-censored Tobit likelihoods lets an optimizer pair `+18 GiB` speedups with `-14 GiB` savers (`2.75×` on `Gemma-4-26B-A4B MoE`) where single-incumbent hill-climbing deadlocks.
3. **Filter transferred experience by structural mechanism class (`kernel` vs topology-sensitive `balance`) and let live observations override LLM priors**: Unfiltered pack retrieval (`1.70×`, `>17` trials) performed no better than cold start because cross-SKU roofline shifts invert tensor-parallel and `FP8` signs.

## Related Artifacts

- [`recursive-improvement.md`](../rules/recursive-improvement.md) — Guardrails on acceptance gating, frozen evaluators, and reward-hacking prevention
- [`enzymersi-dual-loop-enzyme-design`](enzymersi-dual-loop-enzyme-design.md) — Dual-loop surrogate + high-fidelity oracle anchoring in scientific RSI (`arXiv:2611.06321`)
- [`flex-rsi-frontier-agent-benchmark`](flex-rsi-frontier-agent-benchmark.md) — Frontier RSI benchmark across constructive vs single-answer tasks (`arXiv:2611.08946`)
- [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md) — Bounded editable harness envelope and noise-margin calibration (`arXiv:2609.24972`)
