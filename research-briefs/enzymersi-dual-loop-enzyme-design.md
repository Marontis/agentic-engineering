# EnzymeRSI: A Dual-Loop Recursive Self-Improvement System for Enzyme Design

> **Source**: [arXiv:2611.06321](https://arxiv.org/abs/2611.06321) | `src:2611-06321`
> **Authors**: Genoria AI Team, Yuejie Hou, Lixiang Yang, Yisi Liu, Weiting Tang, Yueyuxiao Yang, Meng Yang (Genoria AI)
> **Date**: November 2026
> **Categories**: cs.AI, q-bio.BM, cs.LG
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Summary

`EnzymeRSI` is a dual-loop recursive self-improvement (`RSI`) system (`ProtoPilot` + `Operon-S1`) that couples computational dry-lab evolution with prospective wet-lab enzyme engineering across three enzymes (`RLuc` Renilla luciferase, `A3A` APOBEC3A cytidine deaminase, and `KOD-E` archaeal DNA polymerase). Built on a locked coding-agent substrate (`QwenCode v0.26.5`), `EnzymeRSI` separates an **outer harness loop**—which evolves prompts, pipelines, skills, MCP tool access, and subagents while keeping model weights frozen—from an **inner algorithm loop** that searches over representations, surrogate objectives, and candidate acquisition rules under strict host-enforced evaluation budgets (`20` formal evaluations, `48 h` wall-clock limit, `96 GiB` memory).

Beyond its wet-lab discoveries (such as a `31.1`-fold catalytic efficiency gain in `KOD-E` and a `+40.44` percentage-point preference reversal in `A3A` when the boundary condition shifts), the paper provides an unusually rigorous post-mortem of **evaluation pitfalls in recursive self-improvement**: affine-invariant metric gaming, duplicate prediction submission, benchmark family over-representation reversing strategy rankings, and the sharp divergence between *pool nomination* and *within-pool ranking* ($\rho = 0.175$) when dry-lab surrogates meet noisy physical assays.

---

## Key Findings

1. **Outer-loop harness RSI requires paired falsification and strict adoption gates**: Across `196` outer-loop rounds and `142` paired comparisons on `5` human protein assays from `ProteinGym`, only `12` candidate harness bundles (`8.5%`) passed the adoption gate (`spearman_macro` improvement $\ge 0.001$ with no catastrophic assay regression). Those `12` adoptions raised mean dev-set Spearman correlation by `+0.044`, propelling `EnzymeRSI` to 1st place among `97` official `ProteinGym` models on `CD19` (`0.335` vs. `0.314` starting baseline and `0.316` for leading baseline `MIF`, achieved via `2` adoptions over `39` rounds) and `OPSD` (`0.683`, where `0.680` came from the initial tool combination and `44` rounds added `+0.003`).
2. **Host-side pre-checks prevent evaluation quota waste and metric gaming in inner-loop RSI**: Under a `20`-evaluation budget on `ThermoMPNN` (`215,731` training records across `239` proteins; `27,328` dev records across `31` proteins), `EnzymeRSI` reached a dev Pearson correlation (`PCC`) of `0.849` (`0.849462` in `2.54 h`, `19` valid evaluations) by introducing `ESM2` embeddings, beating `10` reference RSI frameworks (`OpenRSI` `0.834438`, `AReaL-RSI` `0.831964`, `AgenticEvolve` `0.823430`, `ShinkaEvolve` `0.813336`, `MLEvolve` `0.812658`, `RD-Agent` `0.811239`, `OpenEvolve` `0.807043`, `TusoAI` `0.806553`, `AI-Scientist-v3` `0.806209`, `ERA` `0.804358`). Crucially, the host-side audit caught baseline agents submitting positive affine transforms of the starting predictions—which leave Pearson correlation bitwise identical (`0.804358`) while appearing to modify outputs—and instituted zero-quota pre-checks for repeated predictions and malformed delivery manifests.
3. **Statistical unit choice reverses RSI benchmark rankings**: In `evolution-replay-v1` (`2,325` dev replays across `93` dev+val environments $\times 5$ strategies $\times 5$ seeds), `64` of the `93` environments come from a single dense stability dataset (`Tsuboyama`). Weighting equally by environment ranked `Linear ridge` 2nd (`0.7235`), whereas weighting equally across the `21` related protein groups dropped `Linear ridge` to 4th (`0.6063`), behind `GP-BO` (`0.6308`), `FolDE-style` (`0.6235`), and `Static ESM2` (`0.6082`).
4. **Dry-lab surrogates succeed at pool nomination but fail at within-pool ranking**: In prospective wet-lab testing on `RLuc` (`40` single substitutions across `31` positions, `32` non-pre-specified), `16/32` non-pre-specified variants exceeded wild-type (`WT`) luminescence and `10/32` reached $\ge 2\times$ `WT` on retest (`22/40` and `13/40` overall; inference-only variants `M185I`, `S287I`, `S287M` reached retest integrals of `2.30`, `1.98`, `2.43` $\times$ `WT`). Yet the Spearman correlation between dry-lab design rank and wet-lab retest rank inside the nominated `40`-variant pool was only $\rho = 0.175$, and `WT` reference-well coefficient of variation (`CV`) jumped from `16.8%` in batch 1 to `87.6%` in batch 2 (where dropping a single reference well scaled fold-change by `0.77` to `2.01`).
5. **Researcher boundary conditions must be compiled into constrained selection rules, not static scalar scores**: On `A3A` (`75` variants paired in `CG` and `CT` contexts), compiling a minimax selection rule ($\max(\text{C}_{\text{CG}}, \text{C}_{\text{CT}}) \le \text{limit}$, rank by $\min(\text{5mC}_{\text{CG}}, \text{5mC}_{\text{CT}})$) revealed `6` discrete top choices and `5` switches across the constraint frontier: at a `50%` bystander `C` limit (`18` eligible), `Y130Q` is optimal (`46.51%` weaker-context `5mC` vs. `4.55%` runner-up `F66K`, a `+40.44 pp` reversal over `WT`'s `34.81% C` / `11.43% 5mC` in `CT`), whereas at a `60%` limit (`24` eligible), `K47T` jumps to 1st (`64.61%` min `5mC`). On `KOD-E` (`189` valid variants, `125` single-step parent–descendant pairs), sign epistasis reversed mutation direction in `8/18` multi-background substitutions and caused rank reversal in `7/21` four-construct sets (all involving positions `676` and `680` at `3.9–4.0 Å`, up to a `7.4`-unit swing), while combining cooperative positions `451` and `485` (`14.4–16.7 Å` apart) yielded `31.1`-fold `WT` catalytic efficiency.

---

## Quantitative Summary

### Dry-Lab Inner & Outer Loop Results

| Task / Benchmark | Metric | Baseline / Reference | `EnzymeRSI` Result | Key Audit / Ablation Finding |
|:---|:---|:---|:---|:---|
| `ProteinGym` Outer Loop (`5` human assays, `196` rounds) | Mean Dev Spearman $\Delta$ | Starting harness | **`+0.044`** (`12/142` paired comparisons adopted, `8.5%`) | `CD19`: `0.314` $\to$ **`0.335`** (#1 of `97` official models); `OPSD`: `0.680` $\to$ **`0.683`** (#1 of `97`) |
| `ThermoMPNN` Inner Loop (`239` train / `31` dev proteins, `20` eval budget) | Dev Pearson (`PCC`) | Official `0.804358`; `OpenRSI` `0.834438`; Unmodified `QwenCode` `0.839677` (`1.60 h`) | **`0.849462`** (`2.54 h`, `19` valid evals) | Beat all `10` RSI baselines; exposed affine-transform no-op submissions scoring `0.804358` |
| `TadA-Bench` Inner Loop (`31` PANCE rounds, `28` C-terminal positions) | Dev Spearman | Unmodified `QwenCode` `0.300716` (`2.24 h`) | **`0.306826`** (`1.13 h`, `20/20` evals) | Switched continuous regression to ordinal activity-bin modeling under distribution shift (median `0.025` $\to$ `1.03`) |
| `evolution-replay-v1` (`93` dev+val envs, `2,325` replays) | Final Cumulative Top-1 | Equal-env: `Linear ridge` #2 (`0.7235`) | Equal-group (`21` groups): `GP-BO` #1 (`0.6308`), `FolDE` #2 (`0.6235`) | `64/93` envs from `Tsuboyama` skewed per-env mean; group weighting dropped `Linear ridge` to #4 (`0.6063`) |

### Wet-Lab Prospective Validation Across 3 Enzymes

| Enzyme System | Variants Assayed | Primary Wet-Lab Outcome | Diagnostic / Epistatic Finding |
|:---|:---:|:---|:---|
| `RLuc` (Renilla luciferase) | `40` (`8` RLuc8 + `32` novel across `31` sites) | `16/32` novel $>$ `WT`; `10/32` $\ge 2\times$ `WT` on retest (`M185I` `2.30x`, `S287I` `1.98x`, `S287M` `2.43x` integral) | Design rank vs. retest rank Spearman $\rho = 0.175$; `WT` reference CV `16.8%` (batch 1) vs. `87.6%` (batch 2) |
| `A3A` (APOBEC3A deaminase) | `78` in `CG`, `75` paired in `CG` & `CT` | At `50%` `C` limit: `Y130Q` #1 (`46.51%` min `5mC` vs `4.55%` runner-up `F66K`); at `60%` limit: `K47T` #1 (`64.61%`) | `6` optimal variants and `5` discrete switches across boundary frontier; `Tyr130` $C\varepsilon 2$ sits `3.664 Å` from target `C5` |
| `KOD-E` (Archaeal DNA polymerase) | `189` valid variants (`125` parent–child pairs) | `E485I` (`2.9x`) + `S451L` $\to$ **`31.1x`** `WT` $k_{\text{cat}}/K_m$ (vs. `+R484G` $\to$ `1.2x`) | `8/18` multi-background mutations reversed sign; `7/21` four-construct sets reversed rank (positions `676`/`680`, `7.4`-unit swing) |

---

## Why Not a Skill?

1. **Domain-coupled wet-lab/dry-lab architecture**: The concrete workflows (`ESM2` + `ProteinMPNN` + `Boltz` structure priors, `PANCE` phage-evolution ordinal binning, plate-level luminescence normalization, and Cy3-dATP incorporation kinetics) are specialized for protein and enzyme engineering rather than general software or agent tasks.
2. **Core RSI governance patterns belong in rules and existing skills**: The generalizable lessons—host-side pre-checks against duplicate/affine-transformed predictions, hierarchical group-weighted aggregation, and separating outer harness evolution from inner task optimization—directly reinforce [`recursive-improvement.md`](../rules/recursive-improvement.md) and [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md).

---

## Actionable Takeaways

- **Enforce zero-quota host pre-checks for duplicate and affine-transformed predictions**: When evaluating RSI agents on correlation or ranking metrics (`Pearson`, `Spearman`, `ROC-AUC`), reject prediction vectors that are identical or positive affine transformations ($a \cdot \hat{y} + b, a > 0$) of the baseline before consuming evaluation quota.
- **Weight benchmark aggregation by independent family/group rather than raw task count**: When a single source dataset contributes the majority of tasks (`64/93` environments in `evolution-replay-v1`), ungrouped means invert strategy rankings. Always aggregate within related task groups first.
- **Treat surrogate scores as pool nominators, not fine-grained rankers, under noisy oracles**: When design-to-retest rank correlation inside a nominated top-$K$ pool is near zero ($\rho = 0.175$), allocate budget to diversity and boundary-condition coverage across the nominated pool rather than over-optimizing top-1 surrogate scores.

---

## Related Artifacts

- **Rules**: [`recursive-improvement.md`](../rules/recursive-improvement.md) — Falsification gates, outer-vs-inner loop separation, and non-regression invariants.
- **Rules**: [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Evaluation integrity, metric invariance traps, and stratified group aggregation.
- **Skill**: [`mcts-full-harness-optimization`](../skills/mcts-full-harness-optimization/SKILL.md) — Tree-structured search over agent harnesses under a fixed evaluation budget.
