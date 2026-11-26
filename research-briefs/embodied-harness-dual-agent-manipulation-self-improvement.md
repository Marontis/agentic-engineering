# Embodied-Harness: Dual-Agent Working-Memory vs. Experiential Self-Improvement in Robotic Manipulation

> **Source**: [arXiv:2611.27689](https://arxiv.org/abs/2611.27689) (`src:2611-27689v1`, v2 manuscript)
> **Category**: Embodied Manipulation Harnesses, Working vs. Experiential Memory & Backbone Scaling
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Summary

End-to-end Vision-Language-Action (`VLA`) policies (`\pi_{0.5}`, `GigaBrain-0.7`, `PrismWAM`) struggle on long-horizon, spatially perturbed, and non-Markovian robotic manipulation tasks (`10.4%` for `\pi_{0.5}` on memory-dependent `RMBench`), while open-loop LLM code-as-policy wrappers (`RoboDawn`) lack structured intra-episode state tracking and cross-episode failure consolidation (`41.4%` on `RoboSPA-Long`, `53.2%` zero-shot on `RoboTwin 2.0`). *Embodied-Harness* (`arXiv:2611.27689`) wraps a frozen frontier VLM (`GPT-6 Astra` at medium reasoning effort by default, capped at `45` interaction rounds) over `5` high-level spatial/end-effector primitives (`{move, rotate, point, gripper, home}`) inside a dual-agent harness:
1. **Online `Actor` with Dual-Granularity Short-Term Working Memory (`STWM`)**: Conditioned on `3` RGB views (`head`, `left_wrist`, `right_wrist`), end-effector poses, active `Skill Guidance` ($H_k$), and retrieved `Experiential Memory` ($E_k$), the `Actor` updates two synchronized intra-episode buffers at every round—a **`Condensed Progress` ledger** (completed subgoals, active constraints, key historical events) and a **`Detailed Execution` window** (recent primitive commands, contact outcomes, and local state deltas).
2. **Post-Episode `Reflector` with Evidence-Grounded Diagnosis & Long-Term Consolidation**: After each rollout trajectory $\tau_k$, a separate `Reflector` grounds failure attribution in concrete visual/pose evidence across `5` embodied failure categories, distills reusable `Experiential Memory` ($E_k$), and rewrites task `Skill Guidance` via $H_{k+1} = \mathrm{Update}(H_k, \Delta G_k, E_k)$ over `4` iterative refinement rounds.

Across `4` simulation suites and physical robot evaluation (`Tables 1–5`), `Embodied-Harness` reaches **`82.4%`** zero-shot success on `RoboTwin 2.0 C2R` (`50` tasks $\times$ `10` eps, `+29.2 pp` over `0`-shot `RoboDawn` `53.2%` and `+6.9 pp` over full-set trained `PrismWAM*` `75.5%`), **`94.0%`** on `RoboSPA-Spatial (L5)` (`24` tasks, `+28.4 pp` over `RoboDawn` `65.6%`), **`59.5%` SR / `74.9%` PS** on `RoboSPA-Long (L5)` (`32` tasks, `+18.1 pp` SR over `RoboDawn` `41.4%`), **`94.4%`** on non-Markovian `RMBench` (`9` tasks $\times$ `20` eps vs. `83.3%` `MaP-WAM` and `10.4%` `\pi_{0.5}`), and **`96.7%`** across `3` real-world `Piper`-arm tasks (`30` trials vs. `40.0%` `\pi_{0.5}`).

*(Manuscript discrepancy notes: [1] The abstract and `Figure 1c` report **`76.7%`** overall on `RoboSPA`, which is the rounded unweighted mean `(94.0% + 59.5%) / 2 = 76.75%` of `Table 2` [`RoboSPA-Spatial` `94.0%`, `24` tasks] and `Table 3` [`RoboSPA-Long` `59.5%`, `32` tasks; similarly `RoboDawn` `(65.6% + 41.4%) / 2 = 53.5%` matches `Figure 1c`]; [2] the HTML text line `1795` mislabels the real-world table reference as `Table 6`, which is corrected to `Table 5` in the PDF version.)*

---

## Why Not a Skill?

Under [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md) (*"Don't create one skill per paper"*), `Embodied-Harness` is a domain-specific manipulation wrapper whose transferable architectural components are already covered—with stronger statistical acceptance and anti-forgetting guarantees—by existing Praxis skills:
- **Three-layer trace $\to$ experiential knowledge $\to$ skill consolidation**: [`knowledge-compounding-loop`](../skills/knowledge-compounding-loop/SKILL.md) (`WikiSkill`) and [`falsification-gated-memory-evolution`](../skills/falsification-gated-memory-evolution/SKILL.md) (`FGSE`).
- **Evidence-localized post-episode failure attribution**: [`targeted-failure-attribution`](../skills/targeted-failure-attribution/SKILL.md) (`DoCtOR`) and [`neural-invariant-failure-diagnosis`](../skills/neural-invariant-failure-diagnosis/SKILL.md).
- **Continual harness/playbook revision without regression**: [`regret-guided-continual-harness-evolution`](../skills/regret-guided-continual-harness-evolution/SKILL.md) (`GUARD`) and [`roboace-adversarial-curriculum-execution-coevolution`](roboace-adversarial-curriculum-execution-coevolution.md) (`RoboACE`). Notably, `Embodied-Harness`'s prompt-driven `Update(H_k, \Delta G_k, E_k)` (`Eq. 11`) applies skill-guidance rewrites directly across `4` rounds without a held-out statistical non-regression gate; any production deployment must route persistent `H_{k+1}` and `E_k` commits through `"DO: Pass every self-modification through one acceptance gate"` in [`output/rules/recursive-improvement.md`](../rules/recursive-improvement.md).

Instead, `Embodied-Harness` contributes two high-signal **empirical ablations and scaling boundaries** for [`output/rules/recursive-improvement.md`](../rules/recursive-improvement.md) and [`output/specs/self-improving-agent.spec.md`](../specs/self-improving-agent.spec.md).

---

## Key Empirical Findings

### 1. Intra-Episode Dual-Granularity Working Memory Outweighs Cross-Episode Reflection (`Table 6`)

On `32` `RoboSPA-Long (L5)` long-horizon tasks (`Success Rate` / `Progress Score`), ablating harness components one at a time reveals a clear hierarchy of leverage:

| Configuration (`RoboSPA-Long L5`, `Table 6`) | Success Rate (`SR`) | Progress Score (`PS`) | $\Delta$ `SR` vs. Full |
|:---|:---:|:---:|:---:|
| **Full `Embodied-Harness` (`GPT-6 Astra`, Med)** | **`59.5%`** | **`74.9%`** | — |
| `w/o Evidence Grounding` (unanchored reflection) | `52.3%` | `67.9%` | `-7.2 pp` |
| `w/o Long-Term Experiential Memory` ($E_k$) | `48.5%` | `65.6%` | `-11.0 pp` |
| `w/o Reflector` (round-0 frozen harness, `Fig. 5b`) | `43.0%` | `61.2%` | `-16.5 pp` |
| **`w/o Short-Term Working Memory` (`Condensed` + `Detailed`)** | **`32.1%`** | **`49.5%`** | **`-27.4 pp`** |

- **Design lesson**: Before investing in cross-episode self-improvement loops on long-horizon (`20–45` round) embodied or multi-step agents, build **dual-granularity intra-episode working memory** (`Condensed Progress` subgoal/constraint ledger + `Detailed Execution` recent action-outcome window): stripping working memory cost **`1.66x` more success (`-27.4 pp`)** than removing the entire cross-episode `Reflector` (`-16.5 pp`).
- **4-Round Iterative Gains (`Figure 5b`)**: Across rounds `0 -> 4`, iterative reflection lifted `RoboTwin 2.0` from `59.2% -> 82.4%` (`+23.2 pp`), `RoboSPA-Spatial` from `78.2% -> 94.0%` (`+15.8 pp`), `RoboSPA-Long` from `43.0% -> 59.5%` (`+16.5 pp`), and `RMBench` from `71.7% -> 94.4%` (`+22.7 pp`), with steep gains on spatial/memory edge cases (`CVR` `24.0% -> 98.0%`, `MIP` `16.0% -> 80.0%`).

### 2. Backbone Perceptual Grounding Dominates Test-Time Reasoning Effort (`Figure 5a`)

Evaluating `RoboSPA-Long (L5)` across `GPT-6 Astra` reasoning budgets (`Low`, `Medium`, `High`) and `7` closed/open VLM backbones exposes a sharp contrast with symbolic/code RSI:

| Model Backbone (`Figure 5a`, `RoboSPA-Long`) | Reasoning Effort | Success Rate (`SR`) | Progress Score (`PS`) |
|:---|:---:|:---:|:---:|
| **`GPT-6 Astra`** | **Low** | **`61.1%`** | `75.2%` |
| **`GPT-6 Astra`** (default) | **Medium** | `59.5%` | `74.9%` |
| **`GPT-6 Astra`** | **High** | `61.0%` | **`75.5%`** |
| `Claude-Opus-5.5` | Medium | `36.4%` | `60.1%` |
| `Gemini-4-Argon` | Medium | `32.7%` | `51.3%` |
| `Qwen3.8-Max` (strongest open-weight) | Medium | `29.0%` | `50.4%` |
| `Kimi-K3.1-Pro` | High | `27.2%` | `47.5%` |
| `GLM-5.3-Flash` | High | `14.6%` | `33.5%` |
| `DeepSeek-V4.1-Flash` | High | `12.2%` | `32.6%` |

- **Sharp boundary on reasoning-effort scaling**: Unlike ML-code self-improvement (`AI4AI-Bench`, `arXiv:2608.20318`, where raising reasoning effort lifted learning-side attempts from `8%` to `64%`), scaling `GPT-6 Astra` from `Low` to `High` reasoning effort on embodied primitive control yielded **`0.0 pp` net gain (`61.1%` vs. `61.0%` SR)** while model-backbone visual/spatial grounding created a **`47.3–48.9 pp` spread** (`61.1%` `GPT-6 Astra` Low vs. `12.2%` `DeepSeek-V4.1-Flash` High). Extra thinking tokens cannot compensate for 3D visual-spatial misgrounding in `{move, rotate, point}` primitives.

### 3. Five-Category Embodied Failure Taxonomy (`Figure 6`)

Across diagnosed manipulation failures, **`79.0%`** stem from physical actuation and protocol semantics rather than initial object detection:
1. **`Contact & Pose Control` (`34.5%`)** — grasp slip, gripper orientation misalignment, premature/late release.
2. **`Motion & Coordination` (`22.7%`)** — bimanual collision, approach-waypoint sweeps knocking nearby items.
3. **`Task Protocol & Completion` (`21.8%`)** — incomplete terminal placement, skipped ordering constraints.
4. **`State Tracking & Recovery` (`10.9%`)** — losing count/history on occluded or identical objects (`RMBench`).
5. **`Spatial Grounding` (`10.1%`)** — initial 2D/3D target localization offset.

---

## Related Artifacts

- **Skills**:
  - [`knowledge-compounding-loop`](../skills/knowledge-compounding-loop/SKILL.md) — Three-layer (`raw / knowledge / skill`) consolidation with gated rollback
  - [`falsification-gated-memory-evolution`](../skills/falsification-gated-memory-evolution/SKILL.md) — Counterfactual falsification and regression-archive gating for persistent experiential memory (`FGSE`)
  - [`regret-guided-continual-harness-evolution`](../skills/regret-guided-continual-harness-evolution/SKILL.md) — Paired directional regret and `Soft-HURT` scope guards for continual playbook updates (`GUARD`)
  - [`targeted-failure-attribution`](../skills/targeted-failure-attribution/SKILL.md) — Isolating decisive failure steps before reflection (`DoCtOR`)
- **Research Briefs**:
  - [`roboace-adversarial-curriculum-execution-coevolution`](roboace-adversarial-curriculum-execution-coevolution.md) — Alternating curriculum-harness and execution-harness co-evolution in robotics (`RoboACE`, `arXiv:2611.13034`)
  - [`criteria-exposure-verifier-overfitting`](criteria-exposure-verifier-overfitting.md) — Preventing embodied `GPT-6 Astra` skill-library learners from overfitting to hidden benchmark verifier predicates (`arXiv:2611.08318`)
  - [`reglos-two-timescale-memory-harness-evolution`](reglos-two-timescale-memory-harness-evolution.md) — Two-timescale memory harness evolution gated across disjoint splits and readers (`arXiv:2611.06049`)
- **Rules**:
  - [`output/rules/recursive-improvement.md`](../rules/recursive-improvement.md) — `"DON'T: Conflate reasoning effort with algorithmic ability"`, `"DO: Audit outcome observability, rollout scarcity, and structural preconditions before porting iterative multimodal improvement mechanisms, and subtract stateless retry baselines"`, `"DON'T: Expose benchmark verifier code or unstated rubric predicates to the skill-library learner"`, and `"DO: Pass every self-modification through one acceptance gate"`
