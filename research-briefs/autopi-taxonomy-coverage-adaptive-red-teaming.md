# AutoPI: Construction-Taxonomy Coverage vs. ASR in Adaptive Prompt-Injection Red Teaming

> **Source**: [arXiv:2611.24313](https://arxiv.org/abs/2611.24313) — Stavros Damianakis & Konstantinos Psounis (*AutoPI: Taxonomy-Guided Adaptive Red Teaming for Prompt Injection in LLM Agents*, Nov 2026)
> **Praxis Source ID**: `src:2611-24313v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Taxonomy-guided red-teaming and iterative black-box attack loops are already covered by [`taxonomy-driven-red-teaming`](../skills/taxonomy-driven-red-teaming/SKILL.md) (`arXiv:2609.09647`), [`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md) (`CART`, `arXiv:2609.27336`), [`self-improving-red-team`](../skills/self-improving-red-team/SKILL.md) (`SIR`, `arXiv:2608.30207`), and [`agentic-prompt-injection-search`](../skills/agentic-prompt-injection-search/SKILL.md) (`arXiv:2609.04495`), while offensive payload synthesis falls under defensive-brief scoping (`output/AGENTS.md`) and `AutoPI` itself stops at evaluation—explicitly leaving defensive purple-teaming (`§VIII`, covered in [`strategy-diverse-ipi-purple-teaming`](../skills/strategy-diverse-ipi-purple-teaming/SKILL.md)) and automated compositional strategy scheduling (`Ln` for $n > 1$) to future work. Its enduring value for Praxis is its **evaluation-integrity measurement contribution**: proving that adaptive red-teamers ranked solely by scenario-level Attack Success Rate (`ASR`) concentrate almost all successes onto `2–5` narrow construction patterns, skew per-attempt compute by up to **`24×`**, and fail to transfer seed-dependent gains across benchmarks (`rules/agent-evaluation-quality.md`).

---

## Experimental Design & `PIAtlas` Construction Axis (`§III–§V`, `Appendices B–C`)

To separate *how* an indirect prompt injection (`IPI`) is constructed from *where* it is placed or *what* goal it pursues, `AutoPI` builds on a frozen snapshot of the **`PIAtlas`** hierarchical construction taxonomy (`Table I`):

| Class | Name | `# Techniques` | `# Sub-techniques` | Structural Focus |
|:------|:-----|:--------------:|:------------------:|:-----------------|
| **`F1`** | `Instruction Manipulation` | `7` | `26` | Imperative overrides, priority claims, task-step/workflow framing |
| **`F2`** | `Structural Spoofing` | `5` | `14` | Fake delimiters, system/chat/markup boundary mimicry |
| **`F3`** | `Obfuscation` | `8` | `29`* | Encoding, ciphering, character/token splitting |
| **`F4`** | `Social Engineering` | `7` | `32` | Authority personas, urgency, obligation, helpfulness appeals |
| **`F5`** | `Scenario Framing` | `4` | `13` | Hypothetical, testing/audit, roleplay, or policy-simulation wrappers |
| **`F6`** | `Output Coercion` | `3` | `18` | Forced response templates, tool-call format constraints |
| **Total** | **`6` non-overlapping classes** | **`34`** | **`132`** | *(`131` published `PIAtlas` sub-techniques + `1` added leaf under `F3.T6`)* |

- **Two-Stage Training-Free Architecture** (both Generator and Judge run on local FP8 `Qwen3.6-35B` MoE, `35B` total / `~3B` active parameters, thinking disabled):
  - **Stage 1 (`L1` Single-Technique Sweep)**: Sweeps all `132` sub-techniques ($k \le 133$, `1` initial generation/leaf) on scenarios unbroken by static seeds to map per-scenario vulnerability without gradient training.
  - **Stage 2 (`Full` Adaptive Multi-Technique Search, `k = 529` limit)**: Allocates `12` adaptive rounds $\times$ `3` attempts (`36` attempts) per unbroken scenario across `11` curated `L1`/`L2`/`L3` strategy combinations (`Table IV`), using a structured Judge (`compliance` state, `failure mode`, `next adjustment`) over full prior attempt history (`Seed-Exploit` ablation instead allocates `16` rounds $\times$ `3` attempts $\times$ `12` seed variants = `576` attempts, `k = 601` with seeds).
- **Blind Post-Hoc Consensus Labeling (`Appendix C`)**: Because an attacker asked to use technique $X$ frequently drifts into technique $Y$ during refinement, coverage is **never** credited from intended prompt labels. Instead, **`Claude Opus 5.5`** (`temperature = 0`, `3` independent calls per text, `>= 2/3` majority vote at sub-technique level propagated upward) blindly labels all `2,485` distinct successful injection strings (`3,171` broken scenarios across all methods), seeing *only* the raw injection text and full `PIAtlas` codebook. Validation on `100` stratified `L1` texts showed **`0.89` sub-technique precision / `0.87` recall**, **`0.89` technique F1**, **`0.95` class F1**, and **`0.84 / 0.90 / 0.96` inter-call Jaccard** (`384 / 7,455` calls [`5.2%`] triggered provider safety filters, excluding `119` texts [`4.8%`] / `123` scenarios from coverage counts while retaining them in `ASR`).
- **Benchmarks & Targets**:
  1. **`AgentDojo v1.2.2`**: `949` scenario pairs across `workspace` (`560`), `banking`, `slack`, and `travel` (`389` in `3` non-workspace suites; `AutoPI L1`/`Full` ran `946`, `Seed-Exploit` `948`) against local **`Qwen3.6-35B`** and **`Claude Haiku 5.5`** (`97` sampled pairs, `57` in `3` suites).
  2. **`IPI Arena`**: `41` scenarios (`18` tool-use, `15` coding, `8` computer-use; **`21` held-out** outside `PIMiner`'s `20` mined training scenarios) against `Qwen3.6-35B`.

---

## Core Quantitative Findings (`§VI`, `Tables II–V`, `Appendices E–F`)

### 1. Construction Coverage vs. Equal-Compute `ASR@k` (`Table II`)

Total generated-token compute is normalized to `AutoPI Full` (`1.0×` = `147M` generated tokens / `51` GPU-h active work; `96` GPU-h wall-assigned across `8` GPUs at `800` tok/GPU-s), accounting for pre-attack training (`~2` GPU-h mining for `PIMiner`; **`>= 78` GPU-h** 3-stage curriculum RL lower bound for `Climbing the Hill` [`CtH`]; `AutoDojo` untrained, skips `workspace` and runs at `~3×` per-scenario share):

| Method | `AgentDojo` (`Qwen3.6-35B`) Cov `(Cls / Tech / Sub)` | `AgentDojo` (`Haiku 5.5`) Cov `(Cls / Tech / Sub)` | `AgentDojo` (`Qwen`) Equal-Cost `ASR@k` (`All / 3-Suite`) | `AgentDojo` (`Haiku 5.5`) `ASR` (`All / 3-Suite`) | `IPI Arena` (`Qwen`) Equal-Cost `ASR@k` (`All 41 / Held-Out 21`) | Cost / Attempt (Runtime / Incl. Train) |
|:-------|:----------------------------------------------------:|:--------------------------------------------------:|:---------------------------------------------------------:|:-------------------------------------------------:|:----------------------------------------------------------------:|:--------------------------------------:|
| **`Static seeds`** | `3/6, 5/34, 5/132` | `3/6, 5/34, 5/132` | `10.4% / 24.6%` | `4.1% / 7.0%` | `0.0% (0/41) / 0.0%` | — |
| **`PIMiner`** | `6/6, 22/34, 48/132` | `2/6, 4/34, 3/132` | `57.3% / 81.7%` (`k=32`; `65.4%` `@100`) | `5.2% / 8.8%` | `39.0% (16/41) / 42.9% (9/21)` (`k=65`) | `14.4` / **`14.5` GPU-s** (`~11.5k` tok) |
| **`CtH` (Curriculum RL)** | `6/6, 21/34, 38/132` | `4/6, 7/34, 10/132` | **`84.1% / 96.9%`** (`k=41`; `87.4%` `@100`) | `5.2% / 8.8%` | `36.6% (15/41) / 38.1% (8/21)` (`k=100`, `0.9×`) | `1.8` / **`>= 4.7` GPU-s** (`219` words) |
| **`AutoDojo`** | `5/6, 21/34, 38/132` | `1/6, 1/34, 0/132` | `— / 62.2%` (`3`-suite only) | `— / 7.0%` (`4/57`) | — | `2.9` / `2.9` GPU-s (`70` words) |
| **`AutoPI L1`** (`0.3×`) | `6/6, 26/34, 54/132` | `3/6, 6/34, 6/132` | `24.4% / 50.8%` (`k=133`, `230` broken) | `5.2% / 8.8%` | `26.8% / 38.1%` (`k=133`) | **`0.6` / `0.6` GPU-s** (`31` words) |
| **`AutoPI Full`** (`1.0×`) | **`6/6, 31/34, 78/132`** | **`5/6, 9/34, 10/132`** | `42.9% / 73.6%` (`k=529`) | **`6.2%` (`6/97`) / `10.5%`** | `34.1% (14/41)` / **`47.6% (10/21)`** (`k=529`) | **`0.6` / `0.6` GPU-s** |
| **`AutoPI Seed-Exploit`** | `5/6, 20/34, 35/132` (`0.75×`) | `3/6, 5/34, 5/132` | `68.2%` (`67.0%` `@529`) / `86.9%` | **`6.2% / 10.5%`** | `26.8%` (`12/41` `@529`) / `33.3%` (`k=350`, `1.0×`) | **`0.6` / `0.6` GPU-s** |
| **`Union of AutoPI`** | `(6/6, 32/34, 84/132)` (`1.75×`) | `(5/6, 9/34, 10/132)` | `(70.6% [670] / 90.2%)` | `(7.2% / 12.3%)` | `(39.0% [16/41] / 52.4%)` (`2.0×`) | — |

### 2. Severe Technique Concentration Behind High `ASR` (`Fig. 4`, `Table V`, `Appendix E`)

- **`ASR` maximization collapses technique diversity**: Despite `CtH`'s `84.1%` equal-cost `ASR` on `Qwen3.6-35B` (`87.4%` at `k = 100`, matching a `50`-run direct-task upper bound), **`>99%` of its successful injections relied on authority claims and task-step framing** and **`95%` used obligation** (`21/34` techniques, `38/132` sub-techniques). `PIMiner`'s top-3 techniques appeared in **`93%`, `74%`, and `72%`** of successes, and `AutoDojo` used `5` techniques in `>= 76%` of successes. Entire construction classes went untested: **`Scenario Framing (F5)` had `0–1` successes across all three baselines vs. `16` successes across all `4/4` techniques for `AutoPI Full`**.
- **Single-method `AutoPI Full` beats the union of all `3` baselines**: `AutoPI Full` (`31/34` [`91.2%`] techniques, `78/132` sub-techniques) exceeded the combined union of `PIMiner + CtH + AutoDojo` (`28/34` techniques, `63/132` sub-techniques), and already beat every baseline at `0.3×` compute in `AutoPI L1` (`26/34` techniques). Against `Claude Haiku 5.5`, `AutoPI Full` achieved **`25%–400%` higher class coverage (`5/6` vs. `1/6–4/6`)** and **`20%–50%` higher `ASR` (`6.2%` vs. `4.1%–5.2%`)**.
- **Equal-Sample `Cov@k` & Embedding Diversity (`Table V`)**: Subsampling every method to $k = 98$ successful `AgentDojo` scenarios (`1,000` bootstrap draws) confirmed genuine per-sample diversity rather than sample-size inflation: `AutoPI Full` averaged **`5.97` classes / `22.9` techniques** (goal-masked cosine distance $\bar{d} = 0.47$, Vendi Score $\mathrm{VS} = 9.7$, technique-set Jaccard distance $\bar{J} = 0.75$) vs. `PIMiner` (`5.18 / 20.4`, $\bar{d} = 0.45, \mathrm{VS} = 9.7, \bar{J} = 0.60$), `AutoDojo` (`5.00 / 18.9`, $\bar{d} = 0.26, \mathrm{VS} = 3.4, \bar{J} = 0.45$), and `CtH` (`5.12 / 16.5`, $\bar{d} = 0.32, \mathrm{VS} = 5.9, \bar{J} = 0.33$); on seed-unbroken scenarios ($k = 132$), `AutoPI Full` (`26.0`, $\bar{d} = 0.52, \mathrm{VS} = 14.9$) and `L1` (`25.0`) outpaced all baselines (`17.1–20.8`). *(On `IPI Arena` at tiny $k = 8$, `PIMiner`'s `112`-word multi-clause prompts averaged `5.2` co-occurring technique labels/text for `16.9` pooled techniques vs. `8.8` [`1.6` labels/text] for `31`-word `AutoPI Full`, yet `AutoPI Full` led cross-scenario distinctness at $\bar{J} = 0.90$ vs. `0.75/0.76` and $\bar{d} = 0.61$ vs. `0.57/0.52`.)*
- **Seed-Transfer Fragility & System-Defense Replay (`§VI-C`, `§VIII`)**: On `IPI Arena`, where `AgentDojo`'s `important_instructions` seed broke `0/41` scenarios statically, `Seed-Exploit` lost to `AutoPI Full` on **both `ASR` (`12/41` [`26.8%`] vs. `14/41` [`34.1%`]; `47.6%` [`10/21`] held-out vs. `42.9%` `PIMiner` and `38.1%` `CtH`) and coverage (`3/6` vs. `4/6` classes)**. Non-adaptively replaying `351` broken `3`-suite scenarios against system-level defenses (`Progent`, `DRIFT`, `ROPE`) still achieved **`7.7%`, `2.6%`, and `8.3%` `ASR`** while those defenses incurred **`-18` to `-32` points of benign utility loss**.

---

## Relevance to Praxis

- **Rules**: [`rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — `"DO: Report construction-taxonomy coverage alongside ASR at equal total compute in adaptive prompt-injection evaluations"`.
- **Related Artifacts**: [`strategy-diverse-ipi-purple-teaming`](../skills/strategy-diverse-ipi-purple-teaming/SKILL.md) (`PIPETTE`, `arXiv:2611.24362` — resolves this exact coverage-vs-`ASR` pathology during purple-teaming via rolling sparse dictionary learning), [`taxonomy-driven-red-teaming`](../skills/taxonomy-driven-red-teaming/SKILL.md), [`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md), [`owner-authority-ipi-eval-construction`](../skills/owner-authority-ipi-eval-construction/SKILL.md), and [`l2c-workflow-evolution-token-efficient-red-teaming`](l2c-workflow-evolution-token-efficient-red-teaming.md).
