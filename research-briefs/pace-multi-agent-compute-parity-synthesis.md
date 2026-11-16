# More Agents, More Samples, or More Thinking? Parity-Aware Compute Synthesis (`PACE`) Across 516 Multi-Agent Configurations

> **Source**: [arXiv:2611.17610](https://arxiv.org/abs/2611.17610) — Seyed Mahmoud Sajjadi Mohammadabadi (University of Nevada, Reno, 2026) | **Code**: `https://github.com/mahmoudsajjadi/pace`
> **Praxis Source ID**: `src:2611-17610v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is a **quantitative evidence synthesis (meta-analysis)** across `9` primary empirical studies and **`516` unique multi-agent configurations** (`531` raw extracted rows), paired with stylized information/conformity bounds and a 6-item conference reporting standard (**Parity-Aware Compute Evaluation, `PACE`**). Rather than introducing a runtime agent execution algorithm—and to avoid overlapping with [`parallel-small-team-tts-scaling`](../skills/parallel-small-team-tts-scaling/SKILL.md) (`arXiv:2611.09798`, inference-time team sizing under a verifier) or [`learned-teamwork-strategy-bank`](../skills/learned-teamwork-strategy-bank/SKILL.md) (`arXiv:2609.22682`, offline strategy-bank learning)—its baseline ladder, 6D resource vector $\mathbf{R}$, and positive-return preconditions belong as **always-active evaluation and coordination rules** in [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) and [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md) plus kickoff checklists in [`specs/`](../specs/adk-agentic-workflow.spec.md).

---

## Conceptual Framework: Baseline Ladder, 6D Resource Vector $\mathbf{R}$, and Analytical Bounds (`Sections 3–4`, `Appendix A`)

### 1. The Four-Category Single-Agent Baseline Ladder & Accounting Identity

Comparing an $N$-agent, $T$-round communicating system (`MAS`, budget $\mathcal{B}_A$) against a greedy single pass (`SAS`, $B_0$ with $\mathcal{B}_0 \prec \mathcal{B}_A$) confounds two distinct quantities (`Eqs. 4–5`):
$$p_A - p_{B_0} = \underbrace{\big[p_A - f(\mathcal{B}_A)\big]}_{\text{Coordination Effect}} + \underbrace{\big[f(\mathcal{B}_A) - p_{B_0}\big]}_{\text{Compute Scaling Effect}}, \qquad \Delta_{\text{gap}} \triangleq (p_A - p_{\text{sampled}}) - (p_A - p_{B_0}) = p_{B_0} - p_{\text{sampled}}.$$

- **`Category A` (Greedy Single Pass, $N=1, T=1$)**: Uncontrolled compute; confounds coordination with sample multiplicity and token budget.
- **`Category B` (Sample-Matched Baseline, $k = N$)**: Independent draws without communication (e.g., $k$-sample `CoT-SC` / majority voting); isolates gains beyond variance reduction, though token/dollar spend may still diverge.
- **`Category C` (Resource-Matched Baseline)**: Holds a declared dimension of $\mathbf{R}$ equal within tolerance $\epsilon \in [0, 0.10]$: $(1-\epsilon)\mathcal{B} \preceq \mathbb{E}[\mathbf{R}(\pi)] \preceq \mathcal{B}$.
- **`Category D` (Pareto Frontier Sweep)**: Sweeps compute budgets to trace empirical accuracy–cost or accuracy–latency frontiers (`A \succ_{\text{Pareto}} B` iff $p_A \ge p_B \land \mathbf{R}_A \le \mathbf{R}_B$ with strict improvement on $\ge 1$ coordinate).

### 2. The Six-Dimensional Resource Vector $\mathbf{R}$ (`PACE` Protocol)

Every `MAS` vs. `SAS` comparison must classify each of six resource dimensions as **`Strictly Controlled`**, **`Approximately Matched`**, **`Unmatched (Measured)`**, or **`Unreported (Omitted)`**:
$$\mathbf{R} = \langle R_{\text{reason}},\, R_{\text{token}},\, R_{\text{cost}},\, R_{\text{lat}},\, R_{\text{sample}},\, R_{\text{sys}} \rangle$$
covering **(1) `R_reason`** (internal reasoning/scratchpad tokens), **(2) `R_token`** (total prompt + completion + echoed scaffold tokens), **(3) `R_cost`** (USD API spend or normalized FLOPs), **(4) `R_lat`** (serialized wall-clock latency across rounds—controlled by **`0 of 9`** synthesized studies), **(5) `R_sample`** (total forward passes), and **(6) `R_sys`** (external compilers, search engines, bash tools, and verifiers).

### 3. Four Stylized Propositions & Three Routes to Positive Coordination Returns

- **Proposition 3.1 (No Information Gain Under Contextual Redundancy)**: If agents share identical evidence $I(Y; X_1, \dots, X_M \mid X_{\text{shared}}) = 0$, the Data Processing Inequality implies $I(Y; \mathcal{H}^{(T)} \mid X_{\text{shared}}) = 0$ for every $T$-round transcript $\mathcal{H}^{(T)}$.
- **Proposition 3.2 (Category A Bias, Correlated Votes & Quadratic Scaffold Dilution)**:
  1. For independent binary accuracy $p_1 > 1/2$ and odd $K \ge 3$, plurality vote satisfies $p_{\text{SC}}(K) \ge 1 - \exp(-2K(p_1 - 1/2)^2) > p_1$ (sign reverses for $p_1 < 1/2$).
  2. Pairwise peer correlation $\rho_{\text{peer}} \in [0, 1]$ shrinks effective sample size to $K_{\text{eff}} = K / [1 + (K-1)\rho_{\text{peer}}]$ (e.g., $K = 5, \rho_{\text{peer}} = 0.50 \implies K_{\text{eff}} = 1.67$).
  3. Full-history echoing across $K$ agents and $T$ rounds consumes $C_{\text{tot}}(K,T) = KTc_0 + \frac{1}{2}K^2 T(T-1)\bar{\ell}$ scaffold tokens, shrinking per-call thinking allowance to $b(K,T) = B/(KT) - c_0 - \frac{1}{2}K(T-1)\bar{\ell}$.
- **Proposition 3.3 (Conformity-to-Truth Threshold) & Three Positive-Return Routes**: Under constant per-round transition rates $\tau_{i \to c}$ (`wrong -> right`) and $\tau_{c \to i}$ (`right -> wrong`) with $\kappa = \tau_{i \to c}/\tau_{c \to i}$, communication lowers expected per-agent accuracy ($\Delta_{\text{round}}(p_1) < 0$) iff $p_1 > p^* = \frac{\kappa}{1+\kappa} = \frac{\tau_{i\to c}}{\tau_{i\to c} + \tau_{c\to i}}$ (e.g., $\kappa \approx 0.82 \implies p^* \approx 0.45$). Positive returns require:
  - **Route I — Information Partitioning**: $I(Y; X_j \mid X_{\text{shared}}, X_i) > 0$ (testable via Stasser–Titus hidden-profile tasks, `pace hidden-profile`).
  - **Route II — Asymmetric External Verification**: A verifier accepting valid changes w.p. $1 - \epsilon_{\text{FN}}$ and invalid changes w.p. $\epsilon_{\text{FP}} < \kappa \frac{1-p_1}{p_1}(1 - \epsilon_{\text{FN}})$, driving $p^* \to 1$ as $\epsilon_{\text{FP}} \to 0$ (counted in $R_{\text{sys}}$).
  - **Route III — Cross-Model Error Decorrelation**: Heterogeneous panels with $\rho_{\text{het}} < \rho_{\text{hom}}$, raising $K_{\text{eff}}$ at aggregation.
- **Proposition A.1 (Shared-Baseline Variance Deflation)**: When $m_b \ge 2$ `MAS` configurations share one baseline estimate of variance $v_b$, diagonal covariance understates variance of the mean contrast by Kish's design effect $\mathrm{DEff}(m_b, \rho_{\text{base}}) = 1 + (m_b - 1)\rho_{\text{base}}$ where $\rho_{\text{base}} = v_b / (v_a + v_b)$.

---

## Quantitative Synthesis Across 9 Studies (`516` Unique Configurations, `Section 5`, `Appendices B–E`)

Five initial studies (`237` unique `MAS` configs from `252` raw rows after excluding `14` majority-vote rows in `Choi et al.` and `1` `SC` row in `Wunderlich et al.`) plus `4` of `7` screened candidate studies (`279` configs; `40/531` stratified spot-check audit + `336/336` `Tran & Kiela` cell checks with `0` discrepancies) yield **`516` unique `MAS` configurations**:

### 1. Headline Accuracy Differences & Three-Level REML Estimates (`Tables 1–3, 5`)

| Baseline Category | Subset | Studies / Contrasts | Contrast Mean $\bar{\Delta}$ | Study Mean $\bar{\Delta}$ | Share `MAS > SAS` | 3-Level REML Log-Odds $\hat{\beta}$ (`CR2 95% CI`, $\varphi=0.50$) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **`Cat. A` (Greedy 1-pass)** | With `Zhang et al.` | `5 / 358` | `-0.032` | `-0.010` | `0.37` | `-0.071` (`[-0.299, +0.158]`, $\nu=4.7$, $I^2=90/9$) |
| **`Cat. A` (Greedy 1-pass)** | Without `Zhang et al.` | `4 / 178` | `-0.005` | `+0.003` | `0.48` | — |
| **`Cat. B` (Sample-matched)** | With `Zhang et al.` | `6 / 360` | **`-0.051`** | **`-0.043`** | **`0.24`** | **`-0.235`** (`[-0.380, -0.090]`, $\nu=5.2$, $I^2=95/4$) |
| **`Cat. B` (Sample-matched)** | Without `Zhang et al.` | `5 / 220` | `-0.038` | `-0.037` | `0.27` | — |
| **`Cat. C` (Budget-matched)** | `Tran & Kiela` + `Kim et al.` | `2 / 114` | `-0.012` | `-0.024` | `0.32` | *(kept descriptive: 2 studies)* |
| **`Cat. B/C` (Combined)** | **All comparable (`B9`)** | **`8 / 474`** | **`-0.042`** | **`-0.038`** | **`0.26`** *(`74%` $\le 0$)* | **`-0.195`** (`[-0.320, -0.070]`, $p=0.0076, \nu=7.2$) |
| **`Cat. B/C` (Combined)** | Without `Zhang` (`B9-Z`) | `7 / 334` | `-0.029` | `-0.033` | `0.29` | **`-0.145`** (`[-0.242, -0.049]`, $\nu=5.8$, $I^2=86/4$) |
| **`Cat. D` (Pareto front)** | `Wunderlich et al.` (`MMLU-Pro`) | `1 / 2` | `+0.020` | `+0.020` | `1.00` | *(sole positive study: `+0.013` debate, `+0.027` MoA vs 10-SC)* |
| **Sampling Gap ($\Delta_{\text{gap}}$)** | `5` dual-baseline studies (`D`) | `5 / 318` | `-0.028` | **`-0.038`** (`-0.043` no `Zhang`) | `0/5` studies $>0$ | **`-0.169`** (`[-0.288, -0.049]`, $\nu=4.9$, $I^2=72/21$) |

- **Robustness (`Table 5`)**: `B9` stays between `-0.195` and `-0.194` across $\varphi \in [0.00, 0.90]$, stays negative across all `8` leave-one-study-out fits (`-0.233` without `Tran` to `-0.145` without `Zhang`; `-0.190`, `CR2 [-0.341, -0.039]` without `Jwalapuram`), and keeps `CR2` upper bounds `< 0` under CHE block covariance up to $\rho = 0.80$ within `112` shared-baseline blocks (`-0.054`) and `37` shared-benchmark blocks (`-0.044`), crossing zero (`+0.002` to `+0.053`) only under an adversarial uniform correlation across disjoint benchmarks inside a study.

### 2. Study-Level Disaggregations, Cost Multipliers & Threshold Audit (`Tables 6–8, 11–13`)

- **Voting vs. Debate (`Choi et al.`, `m = 14`)**: `5`-agent, `2`-round decentralized debate (`0.715`) beat single-pass greedy decoding (`0.670`) by `+0.045`, but `5`-sample majority voting without communication reached **`0.747` (`+0.076`)**, leaving debate at **`-0.031`** (`100%` of `14` pairs had $\Delta_{\text{gap}} < 0$).
- **Cost & Tooling Audit (`Jwalapuram et al.`, `m = 107`, `Tables 7–8`)**: Automated `MAS` frameworks (`DyLAN`, `MAS-Zero`, `AFlow`, `MaAS`, `ADAS`, `MAS-Orchestra`) cost a median **`8.1x`** (`27.1x` mean, up to `225x`) vs. greedy `CoT` for `\bar{\Delta}_{\text{CoT}} = -0.007` (`42%` ahead), and trailed `5`-sample `CoT-SC` by **`\bar{\Delta}_{\text{SC}} = -0.041`** (`1.6x` median cost, `25%` ahead; note `CoT-SC` rows report maxima across entries). On `SWE-bench Lite` (`m=17`), `BrowseComp-Plus` (`m=23`), `SWE-bench Verified` (`m=9`), and `Terminal-Bench` (`m=9`), `MAS` trailed across all software/agentic suites (`-0.017` to `-0.111`). On `SMFR` (`GPT-5`, $N = 588$), automated `MAS` scored `20.2%` (`ADAS`) to `63.0%` (`MAS-Orchestra`) at `$427–$9,239` vs. `48.5%` `CoT` and `57.0%` `CoT-SC`, whereas human-engineered domain tooling (**`Expert MAS`**, `m = 3`) reached **`96.51%` at `$555`** (`+0.226` vs. `CoT`, `+0.167` vs. `CoT-SC`).
- **Refuting a Universal `~45%` Capability Ceiling (`Section 5.6`, `Appendix E`, `Tables 11–13`)**:
  - Splitting `m = 235` initial contrasts at $p_{\text{SAS}} = 0.45$ and fitting a study-fixed-effects segmented log-odds regression showed **no break** (slope difference **`+0.03`, `HC3 SE = 0.17`**; `+0.13 (0.11)` in `Tran & Kiela`, `-0.13 (0.20)` in `Jwalapuram`, `+1.44 (0.73)` in `Kim et al.`, `n = 20`/cell).
  - Under matched thinking tokens (`Tran & Kiela`, `FRAMES` $N=824$, `MuSiQue` 4-hop $N=405$; `-0.007` across `96` Debate/Sequential contrasts and **`-0.017` across all `240` 5-arm contrasts** in `Table 11`), single agents outperformed `MAS` from **`500` to `10,000` thinking tokens** (`-0.012` at `500`, `-0.023` to `-0.035` at `1k–10k`) regardless of baseline accuracy (`-0.004` $<.45$ vs. `-0.014` $\ge .45$), while the `+0.077` gap at `100` tokens reflected truncated reasoning chains.

---

## The `PACE` Reviewer Checklist & Evaluation Card (`Section 6.3`, `Table 4`)

1. **6D Resource Vector $\mathbf{R}$**: Disclose verification status (`Strictly Controlled`, `Approximately Matched`, `Unmatched`, `Unreported`) for all six components ($R_{\text{reason}}, R_{\text{token}}, R_{\text{cost}}, R_{\text{lat}}, R_{\text{sample}}, R_{\text{sys}}$).
2. **Equal-Compute Single-Agent Baselines**: Include `Category B` (`CoT-SC` / `Best-of-N`) and/or `Category C` (matched thinking/total tokens or cost within $\epsilon \le 0.10$), never `Category A` greedy alone.
3. **Scaffold Accounting**: Deduct system prompts, role headers, echoed dialogue histories, and router calls from effective reasoning budgets (`prompt + completion` tokens logged for every call, including reused/cached calls).
4. **Dispersion, Sample Size & Paired Variance**: Report $N_{\text{items}}$, seeds, and per-item binary outcomes or paired bootstrap intervals (`95%` CI on the `Frontier Gap` against the `SC` token frontier), modeling shared-baseline correlation ($\mathrm{DEff}$).
5. **Task Decomposability & Tool Parity**: Test whether a single agent equipped with identical external tools/verifiers ($R_{\text{sys}}$) achieves the same gain, and state which positive-return route (partitioned evidence, external verifier, or cross-model heterogeneity) applies.
6. **Architecture Search Cost Disclosure**: Report cumulative compute spent on prompt/graph search and negative topology trials.

## Related Artifacts

- [`rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Benchmark design, `PACE` baseline parity, and verifier soundness guardrails
- [`rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md) — `"DON'T: Default to a fixed multi-agent topology"`, `"DON'T: Assume multi-agent debate eliminates shared misconceptions"`, `"DO: Use heterogeneous, cross-family rosters for deliberation and joint verification"`, and `"DO: Scale test-time compute on verifiable long-horizon tasks via parallel small flat teams rather than solo Best-of-N, one giant team, or manager orchestration"`
- [`skills/parallel-small-team-tts-scaling/SKILL.md`](../skills/parallel-small-team-tts-scaling/SKILL.md) — Realizing Route II (external verifier) on long-horizon optimization tasks (`arXiv:2611.09798`)
- [`skills/learned-teamwork-strategy-bank/SKILL.md`](../skills/learned-teamwork-strategy-bank/SKILL.md) — Realizing Route III (cross-model heterogeneity) with compute-matched and routing-oracle baselines (`arXiv:2609.22682`)
- [`coordination-tax-heterogeneity-dividend-multi-agent.md`](coordination-tax-heterogeneity-dividend-multi-agent.md) — Closed-form token/cost/latency feasibility bounds ($\alpha < 1/r$, $f > f^\star$) for multi-stage decomposition (`arXiv:2610.37700`)
