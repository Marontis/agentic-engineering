# Piccolo: Co-Evolving Decision Models and Data through Recursive Self-Improvement

> **Source**: [arXiv:2611.24651](https://arxiv.org/abs/2611.24651) — Zhenqing Ling, Qirui Jiao, Daoyuan Chen, Yilun Huang, Boshengustc, Xuchen Pan, Yushuo Chen, Bolin Ding, Yaliang Li, Jingren Zhou et al. (`Piccolo Team`, Alibaba Group, November 2026)
> **Praxis Source ID**: `src:2611-24651v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`Piccolo` is a **large-scale model-family technical report** (`Piccolo-0.8B`, `2B`, `4B`, `9B`, and `27B`) documenting `647` archived `27B` training attempts (`~600` in overview prose) across `~6,300` `PPU-ZW810E` accelerator-hours (`~2.8 × 10^21` peak BF16 FLOPs at `123 TFLOP/s`), coupled with custom bidirectional-attention single-token logit architectures (`Choice`, `Score`, and `Noul` refusal token), `DataJuicer-Panel` / `DataJuicer-Sandbox` infrastructure, two-range half-step Transformer layer recurrence, and parameter-space delta merges. General black-box agent–data co-evolution is already covered by [`agent-data-mutual-evolution`](../skills/agent-data-mutual-evolution/SKILL.md). We capture `Piccolo`'s decision-head formulation and quantitative failure modes here and add its empirical pitfalls directly to existing entries in [`recursive-improvement.md`](../rules/recursive-improvement.md).

---

## Core Architecture & Governed Co-Evolution Loop

Instead of autoregressive rationale generation (`LLM-as-a-judge`), `Piccolo` casts agentic harness routing, data curation, and multimodal judgment as **single-forward-pass calibrated logit readout** over bidirectional full-attention prompts (`causal mask disabled` across prompt tokens):

1. **Unified Single-Token Decision Interface (`Choice`, `Score`, `Noul`)**:
   - Discrete selection reads normalized probabilities over single-token candidate identifiers (`A, B, ...`), scalar quality scoring computes expected value over integer score tokens (`0–9`), and an explicit abstention/uncertainty token (`Noul`) absorbs out-of-scope or ambiguous inputs without multi-token decoding latency.
2. **`13`-Axis Governed Data Pool (`663K` Curated Items from `6.65M` Records / `8.93M` Questions)**:
   - Built from `43` text collections plus multimodal sources into `311K` text and `352K` image–text items annotated by an ensemble of models along `13` semantic axes (`551` selectable values, including `334` domains, `144` capabilities, and `20` task functions) plus difficulty and per-sample loss trajectories.
   - Candidate interventions are screened on a `~4,000`-question tuning split and gated on a **disjoint `2,000`-question confirmation split** before entering lineage history.

---

## Key Empirical Results & RSI Pitfalls

### 1. `Decision-Index-Vision` Leaderboard Standing (`86` Entrants)

| Model | `Full` Score | `Private` Split | `Public` Split | `HarnessJevBench` | `DataJevBench` | `JevBench` |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **`Piccolo-27B`** (`#1` Overall) | **`75.59`** | **`70.97`** | **`80.22`** | **`84.41`** (`#1`, `+1.36` vs. `Sieve 31B v3` `83.05`) | **`82.60`** | **`92.21`** |
| **`Piccolo-9B`** (`#1` Private in size class) | **`68.35`** | **`65.04`** | `71.67` | `71.53` | `72.40` | `88.74` |
| **`Piccolo-4B`** (`#1` Private in size class) | **`67.46`** | **`63.49`** | `71.42` | `66.10` | `70.20` | `87.01` |
| **`Piccolo-2B`** | — | — | `66.64` | `56.10` | `52.80` | `86.15` |
| **`Piccolo-0.8B`** | — | — | `55.17` | `51.19` | `52.20` | `75.32` |

### 2. Four Documented Co-Evolution Pitfalls (`Table 1`, `Figs. 9 & 11`, `§4–5`)

1. **Continuous-Loss vs. Discrete-Accuracy Reversal (`Table 1`, `341` Fixed Workflow Questions)**:
   - Across consecutive training stages on `341` tracked workflow-decision items, mean target–prediction KL divergence **decreased monotonically (`2.19 -> 0.66 -> 0.64`)**, yet discrete argmax accuracy surged by **`+78` net items** in the earlier stage and **reversed to `-13` net items** in the later stage as probability mass sharpened onto runner-up distractors—requiring automated mixture-ratio throttling (`4.69% -> 5.36% -> 5.14%`) gated on discrete flip counts rather than validation loss.
2. **Fixed-Weight Prompt-Layout Interference & Static-Pool Over-Exposure (`Fig. 11`)**:
   - Reorganizing prompt input layout **at fixed weights** improved `Public Text` by `+1.14` points while simultaneously regressing **`DataJevBench` by `-3.00` points**.
   - Repeating `1.024M` (`1M` in prose) additional sample exposures on an unrefreshed static data pool nudged `DataJevBench` `+0.60` while degrading `Public Text` by **`-1.29`** and `HarnessJevBench` by **`-1.69`**, whereas targeted `10%` error-driven sample replacement beat random replacement by **`+2.11` dev points (`56.56` vs. `54.45`)**.
3. **Backbone–Recipe Non-Monotonicity Across Newer Base Releases (`Fig. 9b`)**:
   - Replaying the **exact same training recipe and data order** across three successive `27B` base checkpoints inverted benchmark rankings: the older `Qwen3.5-27B` achieved the highest `Public Vision` score (**`79.97`** vs. `79.59` on `Qwen3.6-27B` and `77.86` on `Qwen3.8-27B`), whereas `Qwen3.8-27B` dominated `HarnessJevBench` (**`85.93`** vs. `80.85` and `81.36`). Data mixtures cannot be ported blindly across newer base-model generations without re-profiling per-axis transfer.
4. **Curation-Granularity Trade-Offs, Layer Recurrence, and Negated Regressive Deltas (`§4.2–5.3`)**:
   - Domain-ratio rebalancing alone favored `Public Text` (`67.93` vs. `67.36` fixed), whereas combining source-level quality filtering boosted `HarnessJevBench` (`84.58`) and `DataJevBench` (`82.20`) at a slight `Public Text` cost (`66.98`).
   - Two-range half-step forward layer recurrence (`residual scaled by 0.5`) lifted `HarnessJevBench` from `80.85` to **`87.12`** and `Public Text` dev from `69.15` to `69.75` (whereas quarter-step scaling collapsed to `67.41`), and subtracting parameter-delta components from a *regressive* continuation branch (**negative merge coefficient**) recovered a superior checkpoint in weight space.

---

## Related Artifacts

- **Rules**: [`recursive-improvement.md`](../rules/recursive-improvement.md) (`"DON'T: Accept modifications based on aggregate metrics alone"` and `"DO: Alternate model weight updates and harness search"`)
- **Skills**: [`agent-data-mutual-evolution`](../skills/agent-data-mutual-evolution/SKILL.md) (`EvoMCP`, `arXiv:2610.41479`)
- **Research Briefs**: [`joint-harness-weight-optimization`](./joint-harness-weight-optimization.md) (`WHALE`, `arXiv:2609.00196`)
