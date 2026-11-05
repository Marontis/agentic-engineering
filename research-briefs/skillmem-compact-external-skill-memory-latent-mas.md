# SkillMem: Compact External Skill Memory for Latent Multi-Agent Reasoning

> **Source**: [arXiv:2610.37935](https://arxiv.org/abs/2610.37935) — Zhu et al. (Rensselaer Polytechnic Institute & IBM Research, 2026-10-27)  
> **Praxis Source ID**: `src:2610-37935`  
> **Tier**: Research Brief
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

SkillMem compiles textual reasoning skills into compact external latent memories ($\bm{Z}_s \in \mathbb{R}^{8 \times 256}$, `9.6 KB` per skill including retrieval embedding) for continuous latent multi-agent reasoning (`LatentMAS`: `Planner -> Critic -> Refiner -> Judger`). Rather than prefilling skill text into every agent's prompt or storing bulky per-skill KV caches (`13.0 MB`/skill) or LoRA adapters (`30.7 MB`/skill), SkillMem inserts a shared role-conditioned cross-attention reader (`34.5 MB` total across 4 layers `{L/4, L/2, 3L/4, L-1}`) trained via 200 steps of token-level behavioral distillation to match the log-probability shift $\Delta_t^{\text{text},\rho} = \ell_t^{\text{text},\rho} - \ell_t^{\text{base},\rho}$ induced by the textual skill. On `Qwen3-4B`, SkillMem recovers the severe accuracy drop of unguided `LatentMAS` (`17.97% -> 35.63%` on `GPQA-Diamond`, `21.84% -> 61.50%` on `MedQA`, `72.40% -> 89.90%` on `GSM8K`), reduces 100-skill storage by `38.3x` vs. KV caches and `86.6x` vs. LoRA adapters, and achieves a `4.23x` end-to-end speedup over `TextMAS` (`1.63x` over `LatentMAS + Text Skill`).

## Key Findings

### 1. Accuracy Across Model Scales: Strong Recovery at `4B`, Ceiling at `14B`

Evaluated across 6 benchmarks (`3` seeds: `41, 42, 43`) with `8–10` skills per benchmark discovered from `20` disjoint calibration pairs:

| Benchmark | `Qwen3-4B`: `TextMAS` / `LatentMAS` / `KV` / `SP` / `S2L` / **`SkillMem`** | `Qwen3-8B`: `TextMAS` / `LatentMAS` / `KV` / `SP` / `S2L` / **`SkillMem`** | `Qwen3-14B`: `TextMAS` / `LatentMAS` / `KV` / `SP` / `S2L` / **`SkillMem`** |
|:---|:---|:---|:---|
| `GSM8K` | `89.40` / `72.40` / `84.90` / `89.20` / `84.13` / **`89.90`** | `90.80` / `92.33` / `92.60` / `92.20` / `92.27` / **`93.07`** | `94.00` / `94.30` / `94.30` / `93.70` / `94.00` / `92.60` |
| `GPQA-D` | `29.94` / `17.97` / `22.46` / `30.24` / `27.54` / **`35.63`** | `33.53` / `36.53` / `40.72` / `35.33` / `34.33` / **`37.72`** | `37.72` / `31.74` / `28.14` / `35.33` / `34.13` / **`35.33`** |
| `ARC-E` | `96.87` / `92.67` / `96.27` / `97.27` / `93.00` / **`97.53`** | `97.60` / `98.90` / `98.40` / `98.20` / `98.53` / **`97.80`** | `98.40` / `98.70` / `99.00` / `98.80` / `98.60` / **`98.90`** |
| `ARC-C` | `90.53` / `83.67` / `86.27` / `89.80` / `82.67` / **`91.20`** | `91.80` / `92.40` / `92.80` / `92.60` / `92.47` / `91.80` | `93.40` / `94.20` / `94.40` / `93.33` / `93.00` / **`93.93`** |
| `MedQA` | `60.10` / `21.84` / `33.57` / `55.63` / `33.65` / **`61.50`** | `64.56` / `67.84` / `68.55` / `66.43` / `67.14` / **`69.49`** | `70.42` / `71.60` / `69.25` / `68.08` / `69.01` / `69.72` |
| `MBPP+` | `67.75` / `32.74` / `40.12` / `60.96` / `31.07` / **`65.39`** | `65.11` / `70.23` / `70.23` / `69.65` / `68.72` / **`71.56`** | `66.86` / `72.09` / `70.93` / `71.61` / `70.64` / **`67.25`** |

### 2. Storage, Latency, and Compilation Efficiency (`Qwen3-8B`)

| Metric | `TextMAS` | `LatentMAS` | `Text Skill` | `KV Skill` | `LoRA Skill` (`S2L`) | `SkillMem` |
|:---|:---|:---|:---|:---|:---|:---|
| Per-skill storage | — | — | `173 B` | `13.0 MB` | `30.7 MB` | **`9.6 KB`** (`+34.5 MB` shared reader) |
| Total storage ($N = 100$ skills) | — | — | `17.3 KB` | `1.36 GB` | `3.07 GB` | **`35.5 MB`** (`38.3x` vs KV, `86.6x` vs LoRA) |
| Total storage ($N = 1000$ skills) | — | — | `173 KB` | `13.59 GB` | `30.69 GB` | **`44.1 MB`** (`308x` vs KV, `696x` vs LoRA) |
| End-to-end latency / Speedup | `33.65 s` (`1.00x`) | `8.18 s` (`4.11x`) | `12.98 s` (`2.59x`) | `12.01 s` (`2.80x`) | — | **`7.95 s` (`4.23x`)** |
| Peak GPU memory | `34.02 GB` | `33.83 GB` | `36.13 GB` | `34.97 GB` | — | **`33.86 GB`** |
| Compilation time (`10` MedQA skills) | — | — | — | — | `110 min` | **`11.7 min`** (`9.4x` faster) |

### 3. Critical Ablations: Role Conditioning, Memory Over-Parameterization, and Zero-Training Collapse

- **Role-Conditioned Reader Is Essential**: Removing role conditioning ($\bm{e}_\rho$) drops 5-benchmark average accuracy on `Qwen3-4B` from `75.15%` to `67.37%` (`-7.78` pp; `MedQA` falls from `61.50%` to `40.61%`, `GSM8K` from `89.90%` to `75.70%`), and training separate memories per role (`Per-role Memory`, $4\times$ storage) scores lower (`72.52%` on `4B`, `76.76%` vs. `77.97%` on `8B`) than sharing a single memory via role-conditioned cross-attention.
- **Small Memory ($M=8$) Beats Larger Memory ($M=16$)**: Across `GSM8K` and `GPQA-D` on `4B/8B`, $M=8$ achieves the highest average (`64.08%`, with $M=2$ close behind at `63.63%`), whereas doubling capacity to $M=16$ degrades accuracy on all four settings to `60.09%` (`-3.99` pp).
- **All Three Behavioral Distillation Terms Matter**: Removing $\mathcal{L}_{\text{shift}}$ (matching $\Delta_t^{\text{mem},\rho}$ to $\Delta_t^{\text{text},\rho}$), $\mathcal{L}_{\text{safe}}$ (preserving base behavior where skill support $w_t^\rho$ is low), or $\mathcal{L}_{\text{token}}$ drops the 6-setting macro-average from `64.55%` to `62.43%`, `62.47%`, and `62.93%`, respectively.
- **Direct Zero-Training Latent Extraction Collapses (`Appendix F`)**: Bypassing textual skill extraction and behavioral distillation by taking contrastive hidden-state differences ($Z_{\text{success}} - Z_{\text{failure}}$) or running 8 steps of latent reflection yields `<= +0.27` pp on `GSM8K`/`MedQA` and triggers a **`-32.53` pp catastrophic collapse** into repetitive text degeneration on `GPQA-D` (`-4.96` pp for latent generation).

## Why Not a Skill?

SkillMem is an architecture-specific neural module designed for white-box continuous latent multi-agent pipelines (`LatentMAS`), requiring intermediate Transformer layer hooks (`{L/4, L/2, 3L/4, L-1}`) and gradient-based behavioral distillation on open-weight models, and its accuracy gains vanish by `14B` parameters (`Qwen3-14B`). Its broader design lessons—extracting skills in natural language from paired $(\tau^+, \tau^-)$ trajectories before compiling them via behavioral shift matching, and conditioning skill consumption on agent role—are captured as a rule in `output/rules/skill-system-design.md`.
