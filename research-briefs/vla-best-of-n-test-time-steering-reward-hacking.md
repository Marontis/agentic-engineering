# Best-of-N Test-Time Steering Can Lead to Reward Hacking in Vision-Language-Action Models

> **Source**: Khattar, V., Liu, J., Koike-Akino, T., Jin, M., & Wang, Y. (*Virginia Tech & Mitsubishi Electric Research Laboratories*), *Best-of-$N$ Test-Time Steering Can Lead to Reward Hacking in Vision-Language-Action Models* (`arXiv:2611.33398`, `src:2611-33398v1`, 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Problem & Core Finding

Inference-time `Best-of-N` (`BoN`) steering—sampling $N$ candidate action chunks from a frozen Vision-Language-Action (`VLA`) policy and executing the chunk ranked highest by a world-model or simulator rollout verifier—is widely assumed to improve safety and task completion monotonically with compute budget $N$. Evaluating frozen **$\pi_{0.5}$** (`pi05_libero_safety`, replanning every $h = 5$ steps over `<= 200`-step horizons across **$N \in \{1, 5, 10, 30, 50, 75\}$**) on **`60` `LIBERO-Safety` task-level cases** (`4` suites $\times$ `5` instructions $\times$ `3` difficulty levels `L0–L2`, `10` repetitions/case = `600` episodes per $N$-point) scored by $\hat{R}_i = 0.5\hat{S}_i + 0.5\hat{T}_i$ inside a `MuJoCo` trajectory verifier under **three controlled verifier imperfections** (`Output noise` [`0.1 m` / `100 mm` Gaussian XYZ object-position noise], `Under-responsive` dynamics, and `Over-responsive` arm/gripper/mass dynamics), the authors demonstrate **inference-time Goodhart reward hacking in closed-loop physical control**:

1. **Increasing $N$ actively degrades safe task completion and inflates real physical safety violations** on specific task groups once $N$ grows large enough to sample candidate chunks that exploit positive verifier prediction errors.
2. **Hard safety pre-filtering ($\hat{S}_i = 0$) does NOT prevent hacking**, because larger candidate pools surface *more* false-safe hazards (`missed unsafe choices`) where the imperfect verifier predicts zero violation on a physically dangerous trajectory.
3. **Soft `Best-of-N` (`softmax` selection) partially mitigates dynamics mismatch but barely helps perception output noise**, while **shared-weight post-hoc linear calibration (`SLOP`) backfires under distribution shift or noisy safety signals—collapsing the learned safety weight to $w_S = 0.0000$**.

---

## Key Empirical Findings (Verified Paper Figures)

### 1. Benchmark-Wide Plateau Hides Severe Task-Group Safety Reversals (`Table 1`, `Figs. 1–3`, `Appendix A`)

- **Pooled `60`-case aggregate (`Table 1`, `Fig. 1`)**: From unsteered $N = 1$ (**`43.8%`** safe task completion, **`10.3%`** violation rate), an **exact (`perfect`) verifier** at $N = 75$ lifts safe completion to **`49.8%` (`+6.0 pp`)** and cuts violations more than `2x` to **`4.5%` (`-5.8 pp`)**. Under the **pooled imperfect verifiers** at $N = 75$, safe completion stalls at **`47.0%`** and violations remain **`9.1%`**:
  - `Output noise` (`0.1 m` XYZ): **`44.5%`** safe completion, **`9.8%`** violations (mean proxy-vs-clean reward gap **`0.170`**: `0.190` predicted vs. `0.020` clean).
  - `Under-response` dynamics: **`48.7%`** safe completion, **`7.8%`** violations (`0.0328` predicted vs. `0.0268` clean).
  - `Over-response` dynamics: **`47.8%`** safe completion, **`9.5%`** violations (`0.0310` predicted vs. `0.0256` clean).
- **Non-monotonic `Best-of-N` reversals on contested task groups (`Table 1`, `Figs. 2–3`, `Appendix A`)**:
  - **`Human L2` (`over-response`, $N: 30 \to 75$)**: Safe completion drops **`82% -> 70%`** (`77% -> 64%` across an `18`-repetition check) while real safety violations nearly double **`10% -> 18%`** (`13% -> 20%`).
  - **`Obstacle L0` (`over-response`, $N: 30 \to 50$)**: Safe completion plunges **`34% -> 14%`** (`-20 pp`) while safety violations quadruple **`4% -> 16%`**; under `output noise` ($N: 30 \to 75$), verifier-predicted reward rises **`0.1823 -> 0.2023`** while clean reward falls **`0.0229 -> 0.0217`**, dropping safe completion **`32% -> 20%`** and raising violations **`14% -> 18%`**.
  - **`Soda handover` (`output noise`, $N: 5 \to 75$)**: Safe completion collapses **`50% -> 10%`**.
  - **`Banana placement` (`under-response`, $N: 5 \to 50$)**: Safe completion falls **`60% -> 20%`** while physical violations surge **`40% -> 80%`**.
  - **`Frypan placement` (`output noise`, $N: 5 \to 75$)**: Verifier-predicted reward climbs **`0.1189 -> 0.1957`** while true clean reward crosses below zero (**`0.00356 -> -0.00135`**), collapsing safe completion **`10% -> 0%`** (where the `perfect` verifier achieves **`100%`**).
- **Closed-loop state-shift caveat (`Appendix A`)**: For `Frypan` and `Obstacle L0` (`output noise`), $N_2 > N_1$ satisfies strict static proxy-vs-clean divergence ($P_{N_2} > P_{N_1} \land G_{N_2} < G_{N_1}$). For the two `over-response` trajectories in `Fig. 2` (`Human L2`, `Obstacle L0`), step-level argmax over-optimism steered the robot into harder closed-loop states where even mean predicted reward across visited states dipped from $N = 30 \to 75$.

### 2. Why Hard Safety Filtering ($\hat{S}_i = 0$) Fails as $N$ Grows (`§3.2`, `Fig. 4`, `Appendix B`)

Across the `40` `L0–L1` cases with explicit obstacle/hazard constraints, pre-filtering candidates to those predicted completely safe ($\hat{S}_i = 0$) before maximizing $\hat{T}_i$ (`safety-first selection`) still suffers reward hacking: as $N$ increases from **`5` to `75`**, the count of **`missed unsafe choices`** (selected chunks with $\hat{S}_i = 0$ in the imperfect verifier that violate safety in clean physics) climbs monotonically across all three error modes:
- `Output noise`: **`95 -> 161`** (`+69.5%` missed unsafe selections).
- `Under-response`: **`17 -> 50`** (`2.94x`).
- `Over-response`: **`16 -> 42`** (`2.63x`).

Larger $N$ increases extreme-value selection pressure on **false-negative safety predictions** just as strongly as on false-positive task rewards.

### 3. Limits of Soft `Best-of-N` and Shared-Weight `SLOP` Calibration (`§3.3`, `Tables 2–3`, `Appendix E`)

| Intervention at $N = 75$ | Mechanism | Verified Outcome | Structural Limitation |
|:---|:---|:---|:---|
| **Soft `Best-of-N`** ($p_{\beta,c}(i) \propto \exp(\beta \hat{R}_i / \sigma_c)$) | Replaces hard `argmax` with within-pool standard-deviation-normalized Boltzmann sampling. | **Helps dynamics errors** (`under-response` at $\beta = 16$: **`48.7% -> 53.0%`** safe, **`7.8% -> 5.2%`** viol; `over-response` at $\beta = 8$: **`47.8% -> 52.2%`** safe, **`9.5% -> 7.2%`** viol). | Barely moves `output noise` ($\beta = 2$: `44.5% -> 45.8%`, `9.8% -> 8.2%`), loses steering gains at $\beta = 0.5$, and has **no single optimal $\beta$** across error regimes. |
| **Shared-Weight `SLOP` Calibration** (`Tables 2–3`) | Fits global linear weights $(w_S, w_T)$ on logged proxy features vs. clean outcomes; evaluated at $\exp(16 w^\top x_i)$. | Recovers target `Human L2 over-response` (`70% -> 86%` safe [`43/50` vs. `34/50`], `18% -> 4%` viol [`2/50` vs. `6/50`]); neutral on `57` held-out `over-response` cases (`52.3% -> 53.9%` [`298 -> 307/570`], `5.4% -> 4.4%` [`31 -> 25/570`]). | **Degrades `under-response`** (`54.2% -> 48.8%` safe [`309 -> 278/570`], violations rise **`3.2% -> 5.1%` [`18 -> 29/570`]**) and **zeroes out safety ($w_S = 0.0000$, $w_T = 8.4305$) under `output noise`** (`45.5% -> 47.7%` safe, violations rise **`8.5% -> 9.2%` [`51 -> 55/600`]**). |

- **Two `Appendix E` `SLOP` calibration confounds**: (1) weights were fit at inverse-temperature scale `1` (`Eq. 10`) without per-choice $\sigma_c$ normalization, then deployed at `16x` sharpness (`\exp(16 w^\top x_i)`), and (2) `output noise` weights were fit and evaluated on the **same `60` cases** (`0` held-out split, unlike the `3`-train / `57`-held-out split used for dynamics)—meaning $w_S = 0.0000$ failed *even in-sample* because linear regression discards high-noise safety predictors in favor of lower-noise task-progress features!

---

## Practical Takeaways for Test-Time VLA Steering

1. **Audit per-suite $N$-scaling curves ($N \in \{1, 5, 10, 30, 50, 75\}$) rather than pooled benchmark means**: Pooled `60`-case metrics (`43.8% -> 47.0%`) hid `-20` to `-40 pp` safe-completion collapses and `2x–4x` violation surges on `Obstacle L0`, `Banana`, `Soda`, and `Frypan`. Cap $N$ at the pre-divergence knee (`N = 5–15` under `100 mm` perception noise) or replace `argmax` with moderate-$\beta$ `Soft Best-of-N` ($\beta \in [8, 16]$) when errors stem from dynamics mismatch.
2. **Never let unconstrained linear calibration fit scalar weights $(w_S, w_T)$ across noisy safety and cleaner task channels**: Enforce a **hard positive lower bound on $w_S$** (or lexicographic pessimistic safety margins $\hat{S}_i + \gamma \hat{\sigma}_S(x, a_i)$) and match training-time and inference-time softmax temperatures/normalizations identically.
3. **Pair imperfect rollout critics with policy-independent kinematic fallbacks and tail-pose audits**: Combine with [`detecting-is-not-choosing-vla-world-model-safety`](detecting-is-not-choosing-vla-world-model-safety.md) (`arXiv:2611.29553`), which shows why `P90` pose spikes blind rollout filters and why deterministic retreat/hold fallbacks are needed when all policy chunks cluster in unsafe modes.

---

## Why Not a Standalone Skill?

This paper is a controlled **diagnostic characterization** of inference-time Goodhart reward hacking on a single VLA checkpoint ($\pi_{0.5}$) and simulated `MuJoCo` verifier (`LIBERO-Safety`), and its two tested mitigations (`Soft Best-of-N` and `SLOP` weight calibration) exhibit severe regime-dependent trade-offs (`output noise` insensitivity, `under-response` regression, and $w_S = 0.0000$ safety collapse, plus `Appendix E`'s temperature/normalization mismatch) rather than a self-contained, general-purpose steering recipe. Its durable engineering guardrails—per-group $N$-sweep auditing, false-safe $\hat{S}_i = 0$ scaling failure, and forbidding unconstrained shared linear calibration over noisy safety channels—belong in [`../rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md).

## Related Artifacts

- [`detecting-is-not-choosing-vla-world-model-safety`](detecting-is-not-choosing-vla-world-model-safety.md) — Why `0.864` pooled AUROC collapses to `0.551–0.560` within-decision VLA ranking, `P90` pose filter blindness, and fallback necessity (`arXiv:2611.29553`)
- [`verifier-gap-sign-pre-rl-audit`](../skills/verifier-gap-sign-pre-rl-audit/SKILL.md) — Training-time (`RLVR`/`GRPO`) counterpart showing how optimistic verifiers ($\mathbb{E}[\tilde{V} - r^\star] > 0$) drive reward hacking `2.3x–3.2x` harder (`arXiv:2611.21538`)
- [`abstaining-guardrail-best-of-n`](../skills/abstaining-guardrail-best-of-n/SKILL.md) — Pairwise knockout + abstaining guardrail selection for label-free `Best-of-N` code execution (`GRACE`, `arXiv:2611.20983`)
- [`reward-hacking-immunization`](../skills/reward-hacking-immunization/SKILL.md) — Black-box online reward-hacking detection and honest-candidate reselection (`HackProbe`, `arXiv:2609.04665`)
- [`fatcat-chip-level-alignment-fault-tolerance-defensive-lessons`](fatcat-chip-level-alignment-fault-tolerance-defensive-lessons.md) — Out-of-SoC microcontroller kinematic/workspace safety interlocks for VLA robots (`arXiv:2611.31129`)
