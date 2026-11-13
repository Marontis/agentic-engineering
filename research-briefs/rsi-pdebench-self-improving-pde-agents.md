# RSI-PDEbench: A Benchmark for Self-Improving Agents in PDE Solving

> **Source**: [arXiv:2611.14949](https://arxiv.org/abs/2611.14949) — Binghang Lu, Lang Cao, Changhong Mou, Yige Sun, Cindy Xiangrui Kong, Zheyuan Deng, Tian Yuan, Bing Hu, Runyu Zhang, Na Lu, Guang Lin (2026)
> **Praxis Source ID**: `src:2611-14949v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Under [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md), `RSI-PDEbench` and its accompanying harness `RSI-PDE` are best captured as a research brief plus rule/evidence guidance in [`recursive-improvement.md`](../rules/recursive-improvement.md) for three reasons:
1. **Domain-Specific Equation Library**: Stage I (`Section 4.2`) ranks candidate differential operators $\mathcal{N}_{k,\theta}[u](x,t) = f(x,t)$ across a finite `42`-template PDE/FPDE library from `256` space-time samples—a physics-specific formulation rather than a subtask procedure transferable across `3+` general engineering project types.
2. **Existing Acceptance-Gate Coverage**: Stage II's frozen supervisor updating `(solver P, policy \pi, memory M)` under validation non-regression rules instantiates [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md) and defers directly to `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../rules/recursive-improvement.md).
3. **Unisolated Residual Shortlisting (`Sections 4.2, 5.2, 5.5, 6`)**: The authors explicitly note that the benchmark runs do *not* include an isolated ablation of residual `Top-5` shortlisting, its wall-clock savings, its top-5 recall, or parameter-recovery accuracy, and post-hoc true-equation residual medians are non-monotonic with aggregate relative $L^2$ error across harnesses.

---

## Benchmark Design & Evaluation Protocol (`Section 3`, `Appendices B–D`)

`RSI-PDEbench` releases **`1,001` PDE and fractional PDE (FPDE) problem instances** across **`42` templates** (`20` classical and Caputo/variable-order $\alpha(t), \alpha(x,t)$ fractional templates; `10` nonlinear and multiphysics templates including chaotic Kuramoto–Sivashinsky, 2D Navier–Stokes, spinodal Cahn–Hilliard, and Maxwell/curl–curl; and `12` data-driven and 2D templates including `5` input-field templates adapted from `DiffusionPDE`).

- **Information Boundary**: For each case, the entrant sees only the public view—spatial/temporal domain, callable forcing and initial/boundary data, grid specifications, candidate equation library $\mathcal{K}$, and **`256` spatiotemporal solution samples**—while the true template identity, true parameters $\theta^\star$, noise realization, and high-resolution reference solution $u_{\mathrm{ref}}$ remain hidden inside an isolated evaluator.
- **Pass Criterion**: A submitted solver program passes a case iff execution succeeds within runtime/memory limits, initial/boundary mismatch satisfies $\le 10^{-10}$, and *both* space-time ($E_{\mathrm{st}}$) and final-time ($E_T$) relative $L^2$ errors against $u_{\mathrm{ref}}$ satisfy $\le \tau = 2 \times 10^{-3}$ ($\tau = 5 \times 10^{-2}$ for Elliptic template `28`).
- **Matched Compute & Query Budget**: Development splits templates into `3` parallel solver-library sub-runs (`classical/fractional`, `nonlinear/multiphysics`, `data-driven/2D`), each capped at `2 h` wall-clock, `400` model requests, `40M` prompt tokens, `1.5M` output tokens, and `30` validation submissions on `1 CPU + 1 NVIDIA H100 GPU` (**`1,200` calls, `120M` prompt tokens, `4.5M` output tokens, and `90` validation submissions** total per setting).

| Setting | Templates | Train | Val | Hidden Test | Observation Noise | Evaluation Focus |
|:---|:---:|:---:|:---:|:---:|:---|:---|
| **`Full`** (`full0`) | `42` | `42` | `42` | `210` (`5`/template) | `0%` (noise-free) | Broad coverage across all classical, fractional, nonlinear, and 2D families |
| **`Noisy`** | `24` | `22` | `18` | `160` (from `200` calibrated) | `50%` RMS Gaussian | Parameter estimation & equation identification under heavy corruption |
| **`Hard-OOD`** | `39` (`20` seen + `19` unseen) | `20` | `20` | `278` (`188` unseen + `90` shifted) | `1%` RMS (hidden) | Transfer to `19` held-out equation families & out-of-range coefficients |

---

## The `RSI-PDE` Harness (`Section 4`)

`RSI-PDE` keeps both foundation model weights and the executable supervisor (`src/pde_rsi/code_agents.py`) frozen while evolving three explicit state objects across validation rounds: the solver library $P_r$, a structured JSON instruction policy $\pi_r$, and a bounded lesson memory $M_r$:

1. **Stage I — Residual-Guided Hypothesis Shortlisting (`Section 4.2`)**: Sandbox routines fit candidate families $k \in \mathcal{K}$ against the `256` samples via differential-operator residual loss $\mathcal{L}_{\mathrm{res}}(k, \theta) = \frac{1}{|\mathcal{X}_{\mathrm{id}}|} \sum r_{\mathrm{id}}(x, t; k, \theta)^2$ plus IC/BC checks, retaining up to $K = \min(5, |\mathcal{K}|)$ families before full numerical forward integration.
2. **Stage II — Quantitative Error Feedback & Bounded Proposal Rounds (`Sections 4.3–4.4`)**: Each round requires at least one training-split experiment before proposing edits and caps exploration at $\le 2$ diagnostic analyses and $\le 3$ proposal attempts.
   - **Standard Reference-Error Gate**: Accepts a candidate update when macro validation relative $L^2$ error drops by $> 0.5\%$, no PDE class average rises by $> 5\%$, no class loses passes, and no individual validation case increases $E_{\mathrm{st}}$ or $E_T$ by $> 25\%$.
   - **Public-Pass Fallback Gate**: When only public pass/error records are compared, requires $\ge 1$ gained pass, `0` lost passes, no new execution/constraint/resource failure, and $\le 25\%$ error increase on already-passing cases (with a 1-round waiver of the all-training self-test guard after `2` consecutive blocked rounds).

---

## Quantitative Benchmark Results (`Section 5`, `Tables 3–4`, `Appendices E–F`)

Four frontier models (`Opus 5.5`, `GPT-5.5`, `GPT-6.1`, `Sonnet 5.5`) were evaluated across three entrants: a non-iterative **Single run** (`3–4` model calls, `0` validation rounds), the model's **Native coding harness** (`Claude Code` for Anthropic models, `Codex` for OpenAI models) under the exact same split/budget contract, and **`RSI-PDE`**.

### 1. Hidden-Test Pass Counts & Resource Calls (`Tables 3–4`, `Table 6`)

| Model | `Full` (`/210`): Single / Native / `RSI-PDE` | `Noisy` (`/160`): Single / Native / `RSI-PDE` | `Hard-OOD` (`/278` = `/188` Unseen + `/90` Shifted): Single / Native / `RSI-PDE` | Recorded Model Calls (`Full` / `Noisy` / `Hard-OOD`): Native $\to$ `RSI-PDE` |
|:---|:---:|:---:|:---:|:---:|
| **`Opus 5.5`** | `66` (`31.4%`) / `193` (`91.9%`, 3-run `187–198`) / **`196` (`93.3%`)** | `37` (`23.1%`) / `76` (`47.5%`) / **`120` (`75.0%`)** | `133` (`47.8%`) / `245` (`161+84`, `88.1%`) / **`254` (`165+89`, `91.4%`)** | `240→88` / `187→278` / `240→81` |
| **`GPT-5.5`** | `38` (`18.1%`) / `95` (`45.2%`) / **`104` (`49.5%`)** | `51` (`31.9%`) / `83` (`51.9%`) / **`93` (`58.1%`)** | `42` (`15.1%`) / `81` (`44+37`, `29.1%`) / **`102` (`57+45`, `36.7%`)** | `482→88` / `332→104` / `374→91` |
| **`GPT-6.1`** | `77` (`36.7%`) / `189` (`90.0%`) / **`193` (`91.9%`)** | `45` (`28.1%`) / `90` (`56.2%`) / **`97` (`60.6%`)** | `135` (`48.6%`) / **`261` (`175+86`, `93.9%`)** / **`261` (`173+88`, `93.9%`)** | `548→146` / `140→539` / `643→111` |
| **`Sonnet 5.5`** | `59` (`28.1%`) / `183` (`87.1%`) / **`187` (`89.0%`)** | `36` (`22.5%`) / `92` (`57.5%`) / **`98` (`61.2%`)** | `104` (`37.4%`) / `224` (`134+90`, `80.6%`) / **`238` (`148+90`, `85.6%`)** | `148→95` / `117→138` / `96→125` |
| **4-Model Mean** | `28.7%` / `78.6%` / **`81.0%`** (`+181.9%` vs. Single, `+3.0%` rel. / `+2.4 pp` vs. Native) | `26.5%` / `53.3%` / **`63.8%`** (`+140.2%` vs. Single, `+19.6%` rel. / `+10.5 pp` vs. Native) | `37.2%` / `72.9%` / **`76.9%`** (`+106.5%` vs. Single, `+5.4%` rel. / `+4.0 pp` vs. Native) | Total across `12` pairs: `3,547` $\to$ **`1,884` (`-46.9%`)** |

### 2. Critical Methodological & Diagnostic Findings (`Sections 5.2–5.5`)

- **Iteration Dominates Single-Pass Codegen, While Structured Harness Gains Concentrate Under Noise (`Section 5.2`)**: Moving from single-run synthesis to iterative validation-guided coding accounts for the bulk of total gains (`28.7% → 78.6%` on `Full`, `37.2% → 72.9%` on `Hard-OOD`). `RSI-PDE` beats or ties native coding agents across all `12` model–setting pairs (`11` wins, `1` tie on `GPT-6.1 Hard-OOD` where `Codex` leads unseen templates `175` vs. `173` and `RSI-PDE` leads shifted coefficients `88` vs. `86`), with the largest margin under `50%` observation noise (`+10.5 pp` mean; **`+44` cases** [`76 → 120`] on `Opus 5.5`). Conversely, on `Full`, `Opus 5.5`'s `+3`-case edge (`196` vs. `193`) lies well inside native `Claude Code`'s 3-run range (`187–198`, `11` cases).
- **Call Reduction vs. Noise-Induced Search Expansion & Cost Provenance (`Section 5.4`, `Table 6`)**: Across all `12` pairs, `RSI-PDE` cut total model calls by **`46.9%`** (`3,547 → 1,884`), reducing calls in `8/12` pairs (e.g., `GPT-5.5 Full` `482 → 88` with measured API cost dropping **`-21.9%`** from `\$40.97` to `\$32.01`; `GPT-6.1 Hard-OOD` `643 → 111`), **but increased calls in `4/12` pairs**—including `3 of 4` `Noisy` runs (`Opus 5.5` `187 → 278`, `GPT-6.1` `140 → 539`, `Sonnet 5.5` `117 → 138`) plus `Sonnet 5.5 Hard-OOD` (`96 → 125`). The authors explicitly warn that dollar figures marked `*` in `Table 6` (such as `Opus 5.5 Full` `\$30.47*` vs. `\$16.74` native and `Noisy` `\$67.10*` vs. `\$13.90` native) are *retrospective stop-rule replay costs* paired with full-budget pass counts rather than fresh stopped runs.
- **Evaluator Residuals Correlate Within Runs ($\rho = 0.60\text{--}0.96$) Yet Do Not Rank Harnesses Monotonically (`Section 5.5`, `Tables 7–9`)**: Post-hoc true-equation PDE residuals separate passed from failed cases within each run (e.g., `Opus 5.5 Noisy RSI-PDE` median $L^2$ drops from `2.8e-3` native to `3.2e-6` and median residual from `2.0e-3` to `8.4e-5`, Spearman $\rho = 0.89$), yet lower aggregate $L^2$ error does *not* guarantee lower true-equation residual across harnesses (`Opus 5.5 Full`: `RSI-PDE` improves median $L^2$ from `4.5e-4` to `4.3e-4` while median true-equation residual rises from `3.9e-4` to `4.6e-4`; `GPT-6.1 Noisy`: median $L^2$ `2.5e-10` vs. `5.7e-7` native while median residual is `2.1e-3` vs. `2.8e-4`) because coarse interpolation, boundary mismatch, wrong equation family, and parameter error remain distinct failure modes.

---

## Relevance to Praxis

- **Constructive Quantitative Feedback & Non-Regression Gating ([`recursive-improvement.md`](../rules/recursive-improvement.md))**: Reinforces [flex-rsi-frontier-agent-benchmark](flex-rsi-frontier-agent-benchmark.md) (`arXiv:2611.08946`) on constructive scientific coding—iterative solver repair with continuous $L^2$ error feedback more than doubles single-shot pass rates, while structured policy/memory gating with per-class and per-case (`<= 25%`) non-regression guards yields its largest advantage (`+10.5 pp` mean, up to `+27.5 pp` on `Opus 5.5`) when `50%` observation noise destabilizes free-form coding agents.
- **Auditability of Resource & Diagnostic Claims ([`self-improving-agent.spec.md`](../specs/self-improving-agent.spec.md))**: Demonstrates why self-improving agent benchmarks must report multi-seed baseline variance (`187–198` on `Claude Code Full`), separate full-budget call counts from retrospective early-stop cost replays, and avoid conflating equation-residual diagnostics with ground-truth forward solution error.

---

## Key Citations

- Takamoto et al. (2022) — *PDEBench: An Extensive Benchmark for Scientific Machine Learning* (NeurIPS Datasets & Benchmarks)
- Raissi, Perdikaris & Karniadakis (2019) — *Physics-Informed Neural Networks* (J. Comput. Phys.)
- Rudy et al. (2017) — *Data-Driven Discovery of Partial Differential Equations (`PDE-FIND`)* (Sci. Adv.)
- Li et al. (2026a) — *CodePDE: Inference-Time Solver Generation and Refinement for PDEs*
- Shojaee et al. (2025) — *LLM-SR: Scientific Equation Discovery via Programming with Large Language Models* (ICLR)
- Tian et al. (2026a) — *Harness Evolution Hits a Ceiling: When Weight Training Should Begin* (`arXiv:2610.11655`)
