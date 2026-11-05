# LatentTriad: Pre-Action Risk Representations for Malicious Agent Skill Detection

> **Source**: [arXiv:2611.05088](https://arxiv.org/abs/2611.05088) | `src:2611-05088`
> **Authors**: Zhe Yu, Yi Liu, Ying Zhang, Simin Chen
> **Category**: Research Brief (Agent Security / Malicious Skill Detection / Internal Representation Probing)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Overview

Yu et al. investigate whether an open-weight language model's own internal representations during a single prefill pass can serve as a pre-action gate against malicious agent skill packages—before generating any output tokens, invoking tools, or executing untrusted code. Because agent skills combine benign front-matter declarations (`SKILL.md` headers and introductory prose) with operational workflows, shell commands, Python scripts, and configuration files across multiple files, static keyword scanners and LLM-as-judge classifiers suffer severe false negatives when malicious payloads are disguised behind benign declarations or split across files.

Rather than treating the prompt as a single undifferentiated sequence or reading only the final token, **LatentTriad** decomposes each skill package's prefill token stream into three functional regions across 8 evenly spaced transformer layers:
1. **Declaration ($\mathbf{h}_\ell^D$)**: Pooled hidden states over the root front matter, title, and first prose section describing the skill's stated purpose (up to 8 sentence/line/block atoms in the full detector).
2. **Operation ($\mathbf{h}_\ell^O$)**: Pooled hidden states over the remaining root operational instructions plus readable auxiliary files concatenated in lexicographic path order (up to 256 atoms in the full detector, or 24 in the compact detector), weighted by a learned operational salience readout across atoms.
3. **Boundary ($\mathbf{h}_\ell^B = \mathbf{h}_{\ell, T}$)**: The hidden state at the final prompt token immediately preceding action generation.

LatentTriad combines region-specific linear probes on `Operation` and `Boundary` with a **Geometry** branch that fits 32-dimensional affine ridge transport maps ($T_\ell^{DO}$ and $T_\ell^{OB}$) exclusively on benign training skills, flagging packages whose declaration-to-operation or operation-to-boundary transitions deviate from normal benign skill geometry. The final risk score combines the three branches via a conservative pre-action rule:

$$s(x) = \max\bigl\{p_{\text{boundary}}(x),\; \min\bigl(p_{\text{operation}}(x),\, p_{\text{geometry}}(x)\bigr)\bigr\}$$

blocking execution whenever $s(x) \ge 0.5$.

## Key Findings

1. **Cross-Form Operational Invariance Emerges in Intermediate Layers**: In a controlled 800-example cross-form dataset (`10` task domains $\times$ `4` surface forms: natural language, Python, JSON, and mixed text; `5` domain-grouped folds), 32D probes trained across all forms achieve `98.86–100.00%` out-of-fold AUROC on `Operation` and `Boundary` across `Llama-3.1-8B-Instruct`, `Qwen2.5-7B-Instruct`, and `Mistral-7B-Instruct-v0.3`, while `Declaration`, TF-IDF, and length controls remain near chance. Holding out an entire surface form *and* task domain still preserves `90.09–100.00%` `Boundary` AUROC. Layer-wise curves show `Operation` separability peaks in intermediate layers (e.g., `1.000` AUROC at `L12` on `Llama-3.1-8B`) and attenuates toward the output, whereas `Boundary` separability rises in middle layers and persists to the end of prefill (`0.982` at `L31`).
2. **Operation Representations Causally Drive Boundary Risk States**: Activation-patching interventions that replace `Operation` span states with states from source-matched donor packages shift frozen Boundary diagnostic logits toward the donor's label by `2.376–2.909` logits across `3` backbones. Across `20` held-out attack families, normalized Boundary recovery reaches a median of `0.592` on `Llama-3.1-8B` (vs `0.384` for the strongest matched control) and `0.944` on `Qwen2.5-7B` (vs `0.613`). Multi-depth patching flips pass-to-block decisions by `34.5–66.1` percentage points more than matched random/declaration controls across all `7` backbones.
3. **Single-Token Boundary Readouts Miss Multi-File Routing Chains**: In a controlled `4,608`-presentation multi-state routing study where three auxiliary files have identical byte contents across conditions and security depends solely on workspace routing links, multi-state representations achieve `68.5–75.2%` authorization-pair accuracy compared to `48.8–53.8%` for `Boundary`-only readouts (with individual-node and partial-context controls near chance).
4. **Substantial Gains Over Static Scanners, LLM Judges, and Single-State Probes**: On the `5,830`-package `Large-ID` benchmark (`2,915` source-matched malicious–benign pairs across `5` sources, `1,954` content-linked components, `5` source-stratified folds), LatentTriad achieves `99.0–99.2%` pooled F1 and `93.0–94.6%` source-macro F1 (mean `93.9%`) across `7` open-weight backbones (`7B` to `30B-A3B`), outperforming `RouteGuard` (`76.5–80.9%` source-macro F1, mean `79.2%`), `AgentLens` (`28.8–83.7%`, mean `62.3%`), `SkillSieve L1` (`60.5%`), `Supervised Qwen text readout` (`58.4%`), `LLM-as-judge (Mistral-7B-Instruct-v0.3)` (`30.5%`), and `Cisco AI Skill Scanner` (`27.6%`).
5. **Pooled Metrics Hide Source-Distribution Skew**: Because `89.9%` of benign packages in `Large-ID` originate from a single source, pooled false positive rates (`1.1–1.4%` for LatentTriad) mask cross-source false alarms; under source-macro evaluation, LatentTriad's FPR is `8.0–11.2%` (still lower than `RouteGuard`'s `12.9–17.9%`).
6. **Generalization Boundaries Under Unseen Sources, Symbol Permutation, and White-Box Splitting**:
   - **Leave-one-source-out**: Holding out an entire data source during probe training reduces mean source-macro F1 from `93.9%` to `73.2%` (`80.3%` AUROC), though LatentTriad still outperforms same-backbone `RouteGuard` and `AgentLens` on all `7` models.
   - **CompoSkill & Symbol Permutation**: On `CompoSkill` (`690` matched attack–clean pairs), LatentTriad detects `93.0–97.2%` of attacks at `3.8–4.3%` FPR across `5` backbones, but when variable/function symbols are synthetically permuted across files, AUROC collapses to near-chance (`49.25–53.47%`), proving the probe relies on contextualized token semantics rather than symbolic dataflow resolution.
   - **Adversarial Evasion**: Against 7-round feedback-guided natural-language rewrites, LatentTriad retains `92.9–97.1%` detection (`1/9` new evasions on Llama, `0/8` on Qwen). However, white-box cross-file payload splitting achieves an `11.0%` equal-source attack success rate on `Llama-3.1-8B` while driving benign FPR from `32.3–40.8%` up to `49.3–80.4%`.

## Quantitative Summary

### Table 1: Main Detection Results on `Large-ID` (`5,830` Skill Packages, 5-Fold Cross-Validation)

| Detector / Backbone | Pooled FPR (%) | Pooled FNR (%) | Pooled F1 (%) | Source-Macro F1 (%) [95% CI] | Source-Macro AUROC (%) | Source-Macro AP (%) |
|:---|---:|---:|---:|---:|---:|---:|
| **Input-Level Baselines (No Hidden States)** | | | | | | |
| Regex baseline | 100.0 | 0.0 | 66.7 | 66.7 | — | — |
| SkillSieve L1 | 31.0 | 29.7 | 69.8 | 60.5 | — | — |
| Cisco AI Skill Scanner | 3.1 | 73.3 | 41.1 | 27.6 | — | — |
| LLM-as-judge (`Mistral-7B-Instruct-v0.3`) | 2.4 | 79.5 | 33.3 | 30.5 | 81.0 | — |
| Supervised Qwen text readout (`Qwen2.5-7B`) | 7.5 | 37.3 | 73.7 | 58.4 | 88.3 | — |
| **Hidden-State Baselines (Mean / Range Across 7 Backbones)** | | | | | | |
| AgentLens (single-state probe) | — | — | 44.6–96.8 | 62.3 (28.8–83.7) | — | — |
| RouteGuard (routing-state probe) | 12.9–17.9 (macro) | — | 84.9–85.3+ | 79.2 (76.5–80.9) | — | — |
| **LatentTriad (Per Backbone)** | | | | | | |
| `Llama-3.1-8B-Instruct` | 1.1 | 0.8 | 99.0 | 94.4 [92.1, 96.5] | 99.1 | 99.3 |
| `Qwen2.5-7B-Instruct` | 1.4 | 0.6 | 99.0 | 94.3 [92.4, 96.3] | 99.1 | 99.3 |
| `Mistral-7B-Instruct-v0.3` | 1.3 | 0.5 | 99.1 | 93.4 [91.0, 95.9] | 98.7 | 98.9 |
| `InternLM2.5-7B` | 1.1 | 0.5 | 99.2 | 94.6 [92.6, 96.5] | 99.2 | 99.4 |
| `Qwen2.5-14B` | 1.1 | 0.7 | 99.1 | 94.3 [92.1, 96.6] | 98.9 | 99.1 |
| `Phi-3-medium-14B` | 1.1 | 0.9 | 99.0 | 93.3 [90.5, 96.3] | 99.2 | 99.2 |
| `Qwen3-30B-A3B` | 1.2 | 0.6 | 99.1 | 93.0 [90.3, 96.0] | 98.9 | 99.1 |

### Table 2: Branch Ablations Across 7 Backbones (Source-Macro Means at Threshold $0.5$)

| Branch Configuration | Source-Macro AUROC (%) | Source-Macro F1 (%) | Source-Macro FPR (%) | Source-Macro Recall (%) |
|:---|---:|---:|---:|---:|
| **Full: $\max(B, \min(O, G))$** | **99.02** | **93.91** | **9.51** | **96.73** |
| Boundary-only ($B$) | 97.28 | 91.63 | 9.51 | 92.58 |
| Operation-only ($O$) | 99.03 | 86.69 | 0.00 | 80.04 |
| Geometry-only ($G$) | 99.68 | 95.85 | 0.00 | 92.42 |
| $\max(B, O)$ (no Geometry gate) | 99.15 | 94.08 | 9.51 | 97.05 |
| Matched independent-state control (no affine transport) | 98.95 | 93.89 | 9.51 | 96.68 |

### Table 3: Latency & Robustness Summary

| Evaluation Setting | Metric / Scope | Observed Result |
|:---|:---|:---|
| Compact detector overhead (`8` D / `24` O atoms, CDF scoring) | Probe overhead / total median latency (`Llama-3.1-8B`, `Qwen2.5-7B`) | `56–65 ms` overhead; `259–284 ms` total prefill + detection (vs `~153 s` for `SkillDetonate`) |
| Balanced $2 \times 2$ declaration $\times$ operation counterfactual (`57` pkgs/cell) | Pairwise ranking of malicious vs benign operation under identical declaration | `94.7%` (`Llama-3.1-8B`) and `100.0%` (`Qwen2.5-7B`); `RouteGuard` ties `100%` of pairs |
| Leave-one-source-out generalization | Mean source-macro F1 / AUROC across `7` backbones | `73.2%` F1 / `80.3%` AUROC (down from `93.9%` / `99.02%` in-distribution) |
| `CompoSkill` (`690` matched attack–clean pairs, `5` backbones) | Standard TPR @ FPR vs permuted-symbol AUROC | `93.0–97.2%` TPR at `3.8–4.3%` FPR; drops to `49.25–53.47%` AUROC under symbol permutation |

## Why Not a Skill?

LatentTriad is a white-box model-internals probing architecture rather than a natural-language subtask procedure that an agent can execute at runtime. Deploying it requires:
1. Direct tensor-level access to prefill hidden activations across 8 intermediate transformer layers (`L3`–`L31` on 32-layer models, `L5`–`L47` on 48-layer models), which is unavailable in closed-API agent runtimes.
2. Offline supervised fitting of a 3-member ensemble of stratum-adjusted operational directions, 32D ridge transport maps ($T_\ell^{DO}, T_\ell^{OB}$), and L2-regularized logistic heads over labeled skill corpora.
3. Strict invariance to a frozen prompt template, tokenizer, and tool-schema contract (`run_shell`); changing the system prompt, tool definitions, or model checkpoint invalidates the trained probe weights.

Consequently, its insights belong in our knowledge base as a **Research Brief** and as empirical evidence strengthening our skill-admission governance rules in `output/rules/skill-system-design.md`.

## Actionable Takeaways

1. **Never rely on single-layer or single-token prefill probes alone for multi-file skills**: Final-token (`Boundary`) readouts achieve only `48.8–53.8%` accuracy on multi-file routing chains (`vs 68.5–75.2%` for multi-state readouts) and miss `4.15` percentage points of recall compared to combining `Boundary` with `Operation` and `Geometry` (`92.58%` vs `96.73%`).
2. **Use prefill hidden-state probing as a fast (`~260 ms`) L1 filter for open-weight runtimes, paired with structural AST/dataflow analysis**: On open-weight agent hosts, LatentTriad provides a `~500x` speedup over sandbox detonation (`259–284 ms` vs `~153 s`) and vastly outperforms static/LLM scanners (`93.9%` vs `27.6–60.5%` source-macro F1), but its collapse to `49.25–53.47%` AUROC under cross-file symbol permutation means it must be paired with symbolic taint/dataflow auditing (see `composite-skill-vulnerability-scanner`).
3. **Always report source-macro metrics when benchmarking skill scanners**: Because benign skill repositories dominate pooled datasets (`89.9%` from a single source in `Large-ID`), pooled FPR (`1.1–1.4%`) severely understates cross-source false alarm rates (`8.0–11.2%` source-macro FPR) and out-of-source degradation (`93.9%` $\to$ `73.2%` F1 under leave-one-source-out).
