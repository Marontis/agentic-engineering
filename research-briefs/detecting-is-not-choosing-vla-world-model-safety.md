# Detecting Is Not Choosing: What a World Model Needs to Keep a VLA Policy Safe

> **Source**: [arXiv:2611.29553](https://arxiv.org/abs/2611.29553) (`src:2611-29553v1`)
> **Category**: Embodied VLA Safety Filtering, World-Model Evaluation & Runtime Verification
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Summary

Vision-language-action (`VLA`) manipulation policies (`\pi_{0.5}`, `\pi_0-FAST`, `SmolVLA`) achieve high task completion (`88.0%–98.5%` on `LIBERO`) yet routinely violate physical safety constraints—knocking adjacent non-target objects (`> 5 mm`), applying excessive contact force (`> 200 N`), colliding with themselves, or tilting carried vessels (`> 15°–30°`)—on **`13%–37%` of nominal rollouts** (`Table 1`). This study asks what a runtime world model actually needs to filter unsafe `VLA` action chunks via short-horizon (`H = 10` steps = `0.5 s`) counterfactual rollout selection over $K = 16$ sampled policy chunks plus `2` vertical-lift fallback primitives.

Using an exact `MuJoCo` state-cloning oracle to establish the upper bound (`+11.5` to `+30.8` percentage points higher episode safety across `8` policy–benchmark pairs), the authors uncover **three sharp empirical disconnects** that invalidate standard safety-critic and pose-estimator benchmarks:
1. **Pooled unsafe detection $\neq$ within-decision candidate ranking**: Five action-conditioned neural critics reach **`0.778–0.864` pooled dataset AUROC**—matched by a **state-only critic (`0.864`) that never sees the candidate action**—yet collapse to **`0.551–0.560` within-decision AUROC** on contested states where safe and unsafe chunks coexist, alongside learned MLP dynamics (`0.571`), `DINOv2` latent world models (`0.45–0.46`), and `Cosmos Policy` video/value selection (`0.42` safe-pick vs. `0.34` chance; `-1.0 pp` episode safety).
2. **Median state error fails to predict in-loop safety-filter degradation**: Even with exact `MuJoCo` physics, displacement selection hits half-advantage at **$\epsilon_{1/2} = 1.57\text{ mm}$** on `LIBERO-Spatial` (**`0.21 mm`** across all four constraints), and in-loop `3.18 mm` Gaussian error erases **`70%`** of safety gains. Worse, **upper-tail (`P90`) pose errors** blind the filter by making safe states appear *already in violation*: a pixel reader with `0.56 mm` non-target median error (`3.4 mm` P90; `19.5 mm` task-object P90) loses **`6.5 pp` (`95% CI [-11.0, -2.5]`)** more safety gain than `0.53 mm` median Gaussian noise because **`25%` of decisions** falsely appear pre-violated, and `FoundationPose` (`1.17 / 1.27 mm` medians `< \epsilon_{1/2}`, `468 mm` P90 on moved `LIBERO-10` objects) retains only **`0.31`** (`LIBERO-Spatial`) and **`0.69`** (`LIBERO-10`) of exact-pose rescues.
3. **Policy candidate sampling hits a `43%–44%` infeasibility ceiling without independent fallbacks**: At **`43%` (`LIBERO-Spatial`) and `44%` (`LIBERO-10`)** of unsafe-nominal decisions, **zero of `64` sampled policy chunks are safe** (`K = 16 -> 64` removes only `25%` of infeasible states); stripping the `2` lift fallbacks loses `5.8 pp` and `9.5 pp` of safety, whereas **nominal-vs-`2`-lift-fallbacks alone** recovers within **`0.8 pp` and `3.5 pp`** of full `16`-chunk lookahead.

---

## Why Not a Skill?

This paper is an **explicitly negative feasibility and diagnostic boundary study** rather than a deployable positive world-model procedure (`§3.1–3.2, §5 Limitations`):
- Every tested learned replacement for the simulator—action-conditioned safety critics, pairwise ranking-loss critics, MLP state-space dynamics, `DINOv2` latent predictors, and `Cosmos Policy` future-frame/value predictors—scored near random chance (`0.45–0.571` within-decision AUROC) on fine-grained `5 mm` / `15°` / `200 N` counterfactual selection.
- The positive upper-bound oracle (`MuJoCo` exact state cloning + `K = 16 + 2` rollouts) requires noiseless internal simulator state (`qpos`, `qvel`, contacts, equality constraints), failed to port cleanly to GPU `PhysX` (`ManiSkill3` / `SimplerEnv` state-restoration instability, `§5`), and takes **`5–8 s` per decision (`max 12.4 s`)** vs. a **`0.25 s`** real-time execution window (`20x–32x` slower than real-time).

Instead, its findings directly sharpen evaluation and safety-architecture rules in [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) and [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md), complementing [`world-model-trust-gating`](../skills/world-model-trust-gating/SKILL.md).

---

## Key Empirical Findings

### 1. Exact Simulator Lookahead Upper Bound (`SafeVLA-Bench`, `Table 1`)

Evaluating `0.5 s` (`H = 10` steps at `20 Hz`, re-evaluating every `5` executed steps) exact `MuJoCo` rollouts over $K = 16$ policy chunks + `2` vertical-lift fallbacks (`+2.5 cm` and `+5.0 cm` over `0.5 s`, holding gripper state) across four constraints (`> 5 mm` non-target displacement, `> 200 N` contact force, self-collision, `> 15°` [`30°` on `LIBERO-10`] carried-object tilt):

| Policy & Benchmark | Nominal Safe (`%`) | Lookahead Safe (`%`) | Safety Gain | Task Success (Nom $\to$ Look) | Safe & Successful (Nom $\to$ Look) |
|:---|:---:|:---:|:---:|:---:|:---:|
| `\pi_{0.5}` on `LIBERO-Spatial` (`200` eps) | `86.8%` | **`98.3%`** | **`+11.5 pp`** | `98.5% -> 98.0%` | `85.5% -> 96.5%` |
| `\pi_{0.5}` on `LIBERO-10` (`200` eps) | `70.5%` | **`94.0%`** | **`+23.5 pp`** | `88.0% -> 83.0%` | `62.0% -> 81.5%` |
| `\pi_{0.5}` on `LIBERO-Plus-Spatial` (`70` perturbed eps) | `78.6%` | **`94.3%`** | **`+15.7 pp`** | `95.7% -> 94.3%` | `75.7% -> 88.6%` |
| `\pi_{0.5}` on `LIBERO-Plus-10` (`70` perturbed eps) | `65.7%` | **`91.4%`** | **`+25.7 pp`** | `72.9% -> 71.4%` | `47.1% -> 65.7%` |
| `\pi_{0.5}` on `RoboCasa` (`107` matched kitchen pairs) | `62.6%` | **`93.5%`** | **`+30.8 pp`** | `51.4% -> 53.3%` | `30.8% -> 49.5%` *(driven largely by `CoffeeSetupMug` `+51.1 pp`)* |
| `\pi_0-FAST` on `LIBERO-Spatial` / `LIBERO-10` | `84.7%` / `66.5%` | **`97.3%` / `89.5%`** | **`+12.6` / `+23.0 pp`** | `96.0% -> 95.3%` / `82.5% -> 79.0%` | `81.3% -> 92.7%` / `55.5% -> 71.0%` |
| `SmolVLA` (`450M`) on `LIBERO-Spatial` | `79.2%` | **`94.0%`** | **`+14.8 pp`** | `85.0% -> 83.3%` | `67.5% -> 78.3%` |

### 2. Why Pooled AUROC Is an Illusion for Action Selection (`§3.1`, `Figure 1b`)

- **Cross-state separability dominates pooled AUROC**: Across `46,202` `\pi_{0.5}` decisions (`739,232` chunk rollouts), almost all decisions are either trivially all-safe (arm in free space) or uniformly dangerous (already grazing an obstacle); only **`1,641` decisions (`3.6%`)** are *contested* (containing both safe and unsafe policy chunks).
- **State-only baseline exposes zero action discrimination**: Five action-conditioned critics (concatenated MLP, FiLM-conditioned MLP, cross-attention transformer, ensemble, and pairwise ranking-loss critic) scored **`0.778–0.864` pooled AUROC**, yet a **state-only MLP that completely ignores the candidate action scored `0.864` pooled AUROC**.
- **Collapse on contested decisions**: Evaluated within each of `289` held-out contested states, all five action-conditioned critics scored **`0.551–0.560` within-decision AUROC** (upper `95%` bootstrap CI $\le 0.591$; pairwise ranking loss $\Delta = -0.007$; safe-pick rate `0.56` vs. `0.39` random chance).
- **Learned dynamics, latent WMs, and video WMs fail for the same reason**:
  - Multi-step learned state-space MLP dynamics reached **`0.571`** within-decision AUROC (`0.56` safe-pick vs. `0.39` chance), because step-wise prediction error (`~3–6 mm` over `10` steps) exceeds the `5 mm` displacement margin.
  - `DINO-WM` (`DINOv2` patch-latent rollout + safety probe) scored **`0.46` (`LIBERO-Spatial`) and `0.45` (`LIBERO-10`)** within-decision AUROC—slightly below chance (`14 px` patch stride $\approx 5\text{--}10\text{ mm}$ spatial quantization).
  - Fine-tuned `Cosmos Policy` (`Predict2-2B` video/action/value model on `LIBERO-10`) had **`6.5 mm`** object-position error on predicted future frames vs. **`5.8 mm` for a zero-motion copy-input baseline**; decoding constraints on predicted frames gave **`0.42` safe-pick rate** (vs. `0.34` chance and `0.65` on ground-truth future frames), and filtering `K = 8` chunks with `Cosmos Policy`'s learned value head **lowered episode safety by `-1.0 pp`**.

### 3. Sub-Millimeter Half-Advantage Scales & Tail-Error Filter Blindness (`§3.2`, `Appendix A`)

- **Detection tolerates noise that destroys selection**: Injecting `2.35 mm` median object-pose error on `LIBERO-Spatial` leaves binary unsafe detection at **`0.95` AUROC** while collapsing candidate safe-selection accuracy from **`1.00` to `0.61`** (chance `0.28`). Offline half-advantage pose-error thresholds $\epsilon_{1/2}$ are **`1.57 mm`** (`LIBERO-Spatial` displacement), **`0.21 mm`** (`LIBERO-Spatial` all four constraints; even `0.01 mm` drops all-constraint selection from `1.00` to `0.82` via contact discontinuities), and **`3.27 mm`** (`LIBERO-10` displacement). Unmodeled `±10%` friction error on `LIBERO-10` drops selection accuracy to **`0.64–0.69`**, worse than `9.42 mm` position noise (`0.82`).
- **Upper-tail (`P90`) errors silence the filter (`already-violated` blindness)**:
  - On `LIBERO-Spatial`, a trained convolutional pixel reader achieved **`0.56 mm` median error** on non-target objects (`< 1.57 mm` $\epsilon_{1/2}$, `3.4 mm` P90) and `2.85 mm` median on the manipulated object (`19.5 mm` P90), yet lost **`6.5 pp` (`95% CI [-11.0, -2.5]`)** more episode safety than `0.53 mm` median isotropic Gaussian noise: at **`25%` of decisions**, tail pose spikes exceeded `5 mm` or `15°` before rollout began, making *every* candidate appear unsafe and disabling selection.
  - `FoundationPose` (`RGB-D` + ground-truth CAD meshes) achieved **`1.17 mm` (`LIBERO-Spatial`) and `1.27 mm` (`LIBERO-10`) median errors** (both below $\epsilon_{1/2}$), yet occlusion/symmetry outliers (**`468 mm` P90** on moved `LIBERO-10` objects) restricted rescue retention to **`0.31` (`LIBERO-Spatial`)** and **`0.69` (`LIBERO-10`)** of exact-pose gains.

### 4. Policy Sampling Ceiling & Fallback Necessity (`§5`, `Appendix B`)

- At **`43%` (`LIBERO-Spatial`) and `44%` (`LIBERO-10`)** of decisions where the nominal policy chunk is unsafe, **none of `64` sampled policy chunks is safe** (`K = 16 -> 64` resolves only `25%` of infeasible `K = 16` states because flow-matching/autoregressive VLA modes concentrate tightly around the unsafe trajectory).
- Removing the `2` vertical-lift fallback primitives from the `K = 16` filter drops episode safety by **`-5.8 pp` (`LIBERO-Spatial`) and `-9.5 pp` (`LIBERO-10`)**, whereas evaluating **only `{nominal chunk, +2.5 cm lift, +5.0 cm lift}` (`3` rollouts instead of `18`)** recovers within **`0.8 pp` and `3.5 pp`** of full `16`-chunk selection—demonstrating that **detecting nominal hazard + switching to a policy-independent safe fallback** is far more tractable than ranking clustered policy samples.

---

## Practical Takeaways for Agentic & Embodied Engineering

1. **Always benchmark action-ranking critics and world models on within-decision contested-state AUROC alongside a state-only baseline**: Never accept pooled dataset AUROC (`0.864`) as evidence that a critic or world model can choose between candidate actions at a single state.
2. **Gate state/pose estimators on `P90`/`P99` tail error and pre-rollout false-violation rates, not median error**: Check how often state estimation noise trips safety thresholds at $t = 0$ before counterfactual rollouts even start (`25%` filter-blindness rate).
3. **Pair candidate-sampling filters with policy-independent safe fallback primitives**: Because `43%–44%` of unsafe VLA states contain zero safe samples even at $K = 64$, always include synthesized geometric/kinematic retreat or hold actions (`+2.5/+5 cm` lift, stop, Certified Hold) in the candidate pool.

---

## Related Artifacts

- **Skills**:
  - [`world-model-trust-gating`](../skills/world-model-trust-gating/SKILL.md) — Action-outcome trust calibration for deciding when a world model's predictions are reliable enough to gate actions (`arXiv:2609.26293`)
  - [`asymmetric-knowledge-contingent-execution`](../skills/asymmetric-knowledge-contingent-execution/SKILL.md) — Symbolic three-valued precondition gating and Certified Holds above continuous robot controllers (`AKR`, `arXiv:2611.30179`)
- **Research Briefs**:
  - [`embodied-agent-guardrail-benchmark`](embodied-agent-guardrail-benchmark.md) — High-level symbolic/VLM jailbreak guardrail latency and accuracy tradeoffs in embodied agents (`arXiv:2610.06122`)
  - [`fatcat-chip-level-alignment-fault-tolerance-defensive-lessons`](fatcat-chip-level-alignment-fault-tolerance-defensive-lessons.md) — Hardware-level kinematic/servo envelope interlocks independent of VLA policy outputs (`arXiv:2611.31129`)
- **Rules**:
  - [`output/rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — `"DO: Measure safety compliance separately from accuracy"` and within-decision contested-state critic evaluation
  - [`output/rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — `"DON'T: Evaluate safety-critical agent predictions by numeric accuracy alone"`
