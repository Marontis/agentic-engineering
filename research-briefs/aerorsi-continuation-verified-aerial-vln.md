# AeroRSI: Recursive Self-Improvement for Aerial Vision-Language Navigation

> **Source**: [arXiv:2611.24077](https://arxiv.org/abs/2611.24077) — Shiwei Wu, Yuwen Pan, Zhi Li, Yaowen Li, Yan Zhou, Xuemiao Xu, Yu Liu (Tsinghua Shenzhen International Graduate School, Foshan University, South China University of Technology, Tsinghua University, November 2026)
> **Praxis Source ID**: `src:2611-24077v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`AeroRSI` is an **embodied UAV Vision-Language-Action (`VLA`) simulator training pipeline** (`Qwen3-VL-2B` with rank-`64` LoRA + visual merger trained on `Unreal Engine` / `AirSim` `TravelUAV` trajectories using `384×768` front+downward RGB mosaics, discretized `99^3` 3D motion bins, and depth-map potential-field / altitude-climb action proposals). Because its anchor replay and geometric obstacle-clearance proposals depend on deterministic physics-simulator state resets and onboard depth maps, it is not a general software-agent workflow skill. However, its **self-continuation verification gate**, **renewed failure-frontier anchoring**, and **retentive positive cross-entropy distillation** isolate general principles for closed-loop sequential agent repair, which we distill into [`recursive-improvement.md`](../rules/recursive-improvement.md).

---

## Core Mechanism: Continuation-Verified Closed-Loop Failure Repair

In long-horizon sequential control, imitating a local heuristic fix at a pre-failure state (`DAgger`) often steers the policy into an out-of-distribution state where its own subsequent actions stall or collide (`arXiv:2611.24077`). `AeroRSI` closes a `3`-round simulator-verified RSI loop (`~100` GPU hours/round, zero new human demonstrations, zero test-time search overhead):

1. **Pre-Failure Anchor Rollback**: Roll out current policy $\pi_k$ across training routes (`7,611` routes in `11` scenes; `1/5` route groups held out for mechanism audits), record terminal collisions/timeouts, and rewind $\delta \in \{3, 6\}$ steps before failure to establish reproducible pre-failure anchors (in Round 1, `1,450` of `2,390` anchors had reproducible failures; `1,048` [`43.8%`] yielded verified repairs: `837` training-split + `211` held-out route-group audit repairs).
2. **Dual Proposal Generation + Greedy Self-Continuation Verification**:
   - Pool stochastic policy samples from $\pi_k$ with lightweight depth-map geometric rule proposals (repulsive potential-field lateral avoidance and vertical climb).
   - **Self-continuation gate**: Execute candidate action $a$ at the anchor and require **$\pi_k$ itself to fly greedily for $H = \max(8, \delta + 4) \le 20$ subsequent steps** without collision while making net target progress. Local clearance without $H$-step policy continuation fails/stalls at nearly `25%` of repairable anchors.
3. **Best-Candidate Cross-Entropy + `20%` Self-Retention (`\lambda_n = 0.2`)**:
   - Distill only the **single best continuation-verified repair** per anchor via standard supervised cross-entropy (`CE`), mixed with **`\lambda_n = 0.2` current-policy self-retention** (`1,990` normal states) so local obstacle-turn updates do not shift global straight-flight action priors, then re-collect fresh failure anchors from $\pi_{k+1}$.

---

## Key Empirical Results (`TravelUAV`, `3,005` Test Routes)

### 1. Multi-Round Scaling from `SFT` and `AeroDPO` Initializations (`Tables 1–3`)

Evaluated across `1,418` `Seen`, `629` `Unseen Object` (`UO`), and `958` `Unseen Map` (`UM`) routes:

| Policy Checkpoint | Overall `SR` (`%`) | Collision Rate `CR` (`%`) | `Seen SR` (`%`) | `Unseen Obj SR` (`%`) | `Unseen Map SR` (`%`) |
|:---|:---:|:---:|:---:|:---:|:---:|
| `AerialVLA` baseline `[9]` | `45.32` | — | — | — | `37.58` |
| **Round 0 (`SFT init.`)** | `46.39` | `38.64` | `51.83` | `53.26` | `36.85` |
| **`AeroRSI` Round 1 ($\pi_1$)** | `57.60` | `29.48` | — | — | — |
| **`AeroRSI` Round 2 ($\pi_2$)** | `66.02` | `21.26` | — | — | — |
| **`AeroRSI` Round 3 ($\pi_3$, from `SFT`)** | **`67.49`** (**`+21.10 pp`**, $z = 18.5$) | **`19.10`** (`-19.54 pp`) | **`75.32`** | **`82.19`** | **`46.24`** (`+9.39 pp` vs. `SFT`) |
| **Prior SOTA `AeroDPO` (`DPO init.`)** | `56.87` | `29.15` | `60.01` | `66.45` | `45.93` |
| **`AeroRSI` Round 3 (from `AeroDPO`)** | **`69.85`** (**`+12.98 pp`**, $z = 12.7$) | **`17.90`** | `75.88` | `83.62` | **`53.55`** (`+7.62 pp`) |

- **Outperforming `AeroDPO` from identical `SFT` weights**: From the same `46.39%` `SFT` checkpoint, `3` rounds of `AeroRSI` beat `AeroDPO` by **`+10.62 pp` (`67.49%` vs. `56.87%`, McNemar $z = 10.2$, winning `649` vs. `330` discordant routes)** while halving collision rate (`38.64% -> 19.10%`). Under a strict `15 m` altitude-climb cap on `999` test routes (`Appendix C.4`), $\pi_3$ retained **`13.21` of its `16.22` percentage-point gain** (`36.44% -> 49.65%` capped vs. `50.15% -> 66.37%` uncapped), confirming genuine lateral obstacle negotiation rather than fly-over gaming.

### 2. Diagnostic Ablations: Why Unverified `DAgger`, Short Lookahead, Stale Anchors, and `DPO`/`GRPO` Fail (`Table 4`, `Tables S3–S9`)

- **Unverified heuristic imitation (`DAgger`) hurts the base policy (`-6.64 pp`)**: Directly imitating repulsive potential-field avoidance without continuation verification **dropped test `SR` from `46.39%` to `39.75%` ($z = -6.2$)**, and unverified rule proposals reached only `49.23%`. Adding the $H$-step greedy self-continuation gate jumped rule-only `SR` by **`+12.37 pp` (`49.23% -> 61.59%`, $z = 11.5$)**; truncating verification to a `2`-step lookahead left **`+4.23 pp` more collisions (`33.72%` vs. `29.48%`, $z = 4.2$)**.
- **Rule-to-network internalization & `40.2 m` failure-frontier shift**: At the `21.0%` of Round-1 reproducible anchors where stochastic policy sampling failed completely and *only* geometric rule proposals found a valid continuation, the updated policy's own single-sample `Pass@1` rose from **`11.0%` ($\pi_0$) to `62.1%` ($\pi_1$) and `76.7%` ($\pi_3$)** (`13.7% -> 57.7% -> 76.2%` on `42` held-out route-group anchors). Because fixing early collisions pushed consecutive failure locations **`40.2 m` ($\pi_0 \to \pi_1$) and `28.0 m` ($\pi_1 \to \pi_2$)** further down-route (vs. `12.7 m` same-policy jitter; shifting residual failures from collisions `38.6% -> 19.1%` toward long-range timeouts `1.2% -> 6.8%`), fresh per-round anchoring (`66.02%` R2) beat `Stale labels` (`60.30%`, `-5.73 pp`, $z = -5.5$) and single-round `2x anchors` (`62.98%`, `-3.06 pp`, $z = -3.2$).
- **Best-candidate `CE` + retention vs. `DPO` (`0.1%`) and `GRPO` (`-3.70 pp`)**: Training on anchor pairs with pure `DPO` collapsed `SR` to **`0.1%`**, `GRPO` advantage weighting across all qualifying continuations trailed best-candidate `CE` by **`-3.70 pp` (`53.93%` vs. `57.60%`, $z = -3.7$)**, and removing `\lambda_n = 0.2` normal-state retention inflated turn actions (`15.8% -> 19.6%` toward the `30%` repair-set turn rate) and raised collisions by **`+2.53 pp` (`32.01%` vs. `29.48%`, $z = 2.6$)**.

---

## Related Artifacts

- **Rules**: [`recursive-improvement.md`](../rules/recursive-improvement.md) (`"DO: Verify trajectory failure recovery via greedy policy continuations across renewed pre-failure anchors with best-candidate distillation and on-policy retention"`)
- **Research Briefs**: [`roboace-adversarial-curriculum-execution-coevolution`](./roboace-adversarial-curriculum-execution-coevolution.md) (`RoboACE`, `arXiv:2611.13034`), [`self-evolving-multimodal-agents-cross-scenario-survey`](./self-evolving-multimodal-agents-cross-scenario-survey.md) (`arXiv:2611.14256`)
