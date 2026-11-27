---
name: reciprocal-p2h-h2p-coevolution
description: >-
  Co-evolve a deliberative coding-agent harness (programmatic skill library,
  execution memory, and task router) with a trainable low-latency neural
  executor via parallel 3-route Policy-to-Harness (Code, Code+ICL, Code+Policy)
  failure repair and state-matched Counterfactual Preference Distillation (CPD)
  with asymmetric anchor proximity and EWC retention. Derived from RoboEvo^2
  (arXiv:2611.34675).
source: "arXiv:2611.34675"
repository: "https://github.com/Marontis/agentic-engineering"
license: CC-BY-4.0
---

<!-- Licensed under CC BY 4.0 | Source: Marontis/agentic-engineering | Origin: arXiv:2611.34675 -->

# Reciprocal Policy-to-Harness and Harness-to-Policy Co-Evolution

## When to Use

Use this procedure when building **two-tier agentic control systems** that pair a **frozen, deliberative LLM/VLM coding-agent harness** $H_r = (L_r, M_r, \rho_r)$ (`L_r` = reusable programmatic skills, `M_r` = operational experience memory, `\rho_r` = task-to-route dispatcher) with a **distinct, parameter-trainable fast neural executor** $\pi_{\theta_r}$ (such as a flow-matching/diffusion Vision-Language-Action [`VLA`] or World-Action Model [`WAM`], a low-latency GUI/game action controller, or a compact continuous/discrete policy adapter) inside a simulator or resettable physical testbed with binary/programmatic task verification:

- **Embodied and bimanual robotic manipulation**: Bootstrapping high-success standalone and hybrid policies from weak base VLA checkpoints (`11.0% -> 84.1%` standalone / `90.5%` hybrid on `LIBERO-PRO`; `46.0% -> 77.5%` standalone / `87.4%` hybrid on `50`-task `RoboTwin C2R`; `85.0%` standalone / `95.0%` hybrid on physical `Unitree G1-D` with `120` autonomous demos vs. `80.0%` from `200` human teleop demos in `arXiv:2611.34675`) while amortizing slow LLM coding-agent API calls (`-77.0%` and `-55.0%` per-round spend).
- **Autonomous multi-task skill acquisition without human teleoperation**: Acquiring new manipulation, navigation, or interactive GUI/game behaviors from task instructions + `<= 1` cross-scene reference demonstration (`57.0%` standalone / `65.8%` hybrid on `40`-task `MolmoSpaces` vs. `38.0%` `RATs` and `21.0%` `CaP-Agent0`).
- **Amortizing System-2 code-synthesis harnesses into System-1 weights**: Distilling multi-route deliberative repairs into $\pi_{\theta}$ so deployment can run either **standalone** (`0` LLM calls at test time) or **hybrid** (invoking $H_r$ only on residual failures).

**When NOT to use**:
- **Single-LLM API, FHIR, or SQL agents where `Improver` and `Solver` share one text-generation architecture**: Co-training a **single shared-weight LoRA adapter** across both roles via case-balanced `GRPO` beats frozen frontier proposers by `+33.5 pp` (`85.1%` vs. `51.6%`); use [`dual-role-model-harness-coevolution`](../dual-role-model-harness-coevolution/SKILL.md) (`MedicalRSI`, `arXiv:2611.26806`) instead.
- **Strictly frozen executor weights (closed APIs or read-only edge binaries)**: When $\pi_\theta$ cannot be fine-tuned (`P2H-only` ceiling `46.1%` vs. `68.3%` co-evolved at Round 3 in `arXiv:2611.34675`), use asynchronous `state`/`proc`/`wm` harness evolution ([`asynchronous-system1-harness-evolution`](../asynchronous-system1-harness-evolution/SKILL.md)), dual-granularity intra-episode working memory ([`embodied-harness-dual-agent-manipulation-self-improvement`](../../research-briefs/embodied-harness-dual-agent-manipulation-self-improvement.md)), or curriculum–execution harness alternation ([`roboace-adversarial-curriculum-execution-coevolution`](../../research-briefs/roboace-adversarial-curriculum-execution-coevolution.md)).
- **Environments without reliable task-completion verification or safe resets**: Where outcome observability is blocked (`FailBench` contact-rich VLM detectors cap at `<= 0.60` balanced accuracy; `../../rules/recursive-improvement.md`), unverified harness rollouts inject false-positive supervision into `H2P` distillation.

---

## Core Insight

In heterogeneous System-2 / System-1 architectures, evolving only the coding harness against a frozen neural policy (`P2H only`) stalls because pure code skills struggle with contact-rich local compliance (`46.1%` Round-3 hybrid success on `LIBERO-PRO`), while fine-tuning the policy on rollouts from a fixed Round-0 harness (`H2P only`) starves as soon as early harness heuristics saturate (`33.6%` standalone / `49.0%` hybrid vs. **`52.3%` standalone / `68.3%` hybrid** under reciprocal co-evolution in `Table 3` of `arXiv:2611.34675`). Furthermore, naively distilling harness repairs via supervised imitation (`\mathcal{L}_{\mathrm{sup}}` alone: `20.1%` Round-1 policy SR) ignores what the current policy actually did wrong, while unanchored preference losses (`DPO`) collapse continuous/VLA action priors (`0.1%` SR in `AeroRSI`, `arXiv:2611.24077`).

**RoboEvo$^2$** (`arXiv:2611.34675`) closes a reciprocal two-stage loop in each round $r$:
1. **`Policy-to-Harness (P2H)` Parallel 3-Route Repair**: Evaluates $\pi_{\theta_r}$ to isolate failure cases $\mathcal{F}_r$, dispatches three isolated coding-agent repair routes in parallel—**`Code`** (pure programmatic primitives), **`Code+ICL`** (abstracting strategy sequence from `1` cross-scene demonstration without copying coordinates), and **`Code+Policy`** (code staging + invoking $\pi_{\theta_r}$ itself as a bounded local skill)—and keeps the verified repair minimizing kinematic jerk $J(\tau)$ (`All Routes` reaches `49.1%` Round-1 hybrid SR and lifts Round-1 policy SR to `32.1%`, outperforming any single route: `Code` `29.4%`/`21.0%`, `Code+ICL` `44.9%`/`28.6%`, `Code+Policy` `45.6%`/`29.0%`, `Table 4`).
2. **`Harness-to-Policy (H2P)` Asymmetric-Proximity Counterfactual Preference Distillation (`CPD`) + `EWC`**: Aligns each failed policy rollout segment $y^-$ with its **state-matched** verified harness repair $y^+$ from identical start state $x = (o, g)$, and optimizes supervised imitation plus a margin-bounded preference gap **anchored to frozen round-start weights $\bar{\theta}_r$ via asymmetric proximity regularization** ($\mathcal{L}_{\mathrm{prox}}$)—lifting Round-1 policy SR from `20.1%` (`\mathcal{L}_{\mathrm{sup}}`) to `29.9%` (`+ \mathcal{L}_{\mathrm{gap}}`) and **`32.1%` (`Full CPD`, `+12.0 pp`, `Table 5`)**, while `EWC` prevents source-domain forgetting (**`92.5%` vs. `72.0%`** original `LIBERO` retention, `Table 20`). As $\pi_{\theta_r}$ absorbs repaired skills, fewer tasks enter $\mathcal{F}_r$ (`LIBERO-PRO` per-round coding-agent cost drops **`77.0%` from `$430.63` to `$98.92`**; `RoboTwin C2R` drops **`55.0%` from `$719.05` to `$323.84`**), and the stronger $\pi_{\theta_{r+1}}$ makes `Code+Policy` strictly stronger in round $r+1$.

---

## Step-by-Step Procedure

### Step 1: Isolate Policy Failures and Run Parallel 3-Route `P2H` Repair

At round $r$ with current neural executor $\pi_{\theta_r}$ and harness $H_r = (L_r, M_r, \rho_r)$:

1. **Failure-focused rollout screen**: Roll out $\pi_{\theta_r}$ (and routed hybrid $H_r$) across the training task pool. Partition episodes into direct policy successes $\mathcal{S}_r$ and failure cases $\mathcal{F}_r$ (recording failure video/state traces, terminal state summaries, and step indices). Spend deliberative coding-agent budget **exclusively on $\mathcal{F}_r$**.
2. **Spawn three isolated workspace branches per failed task cluster**:
   - **Route A — `Code` (Programmatic Skill Synthesis)**: Synthesize parameterized perception-to-control Python primitives (`grasp_handle`, `align_axis`, `guarded_lift`) using current library $L_r$ and experience notes $M_r$.
   - **Route B — `Code+ICL` (Cross-Scene Strategy Abstraction)**: Provide **at most `1` cross-scene demonstration** summarized into phase transitions, relative spatial offsets, and gripper events—instructing the coding agent to extract the **high-level subgoal sequence and failure guards** while **explicitly forbidding raw coordinate or joint-trajectory copying**.
   - **Route C — `Code+Policy` (Compositional Neural-Programmatic Staging)**: Expose $\pi_{\theta_r}$ as a callable tool primitive `run_policy_chunk(goal, max_steps)` inside the code harness so programmatic skills handle coarse long-horizon transport/alignment while $\pi_{\theta_r}$ executes fine contact-rich local phases (or vice versa).
3. **Select smoothness-optimal verified repairs**: Keep only branches that pass the environment's binary/programmatic task verifier (`V(\tau) = 1`, with verifier internal source hidden from the coding agent per `"DON'T: Expose benchmark verifier code or unstated rubric predicates to the skill-library learner"`). When multiple routes succeed on the same failure instance, select the trajectory minimizing normalized kinematic jerk / action oscillation $J(\tau)$ so downstream policy targets remain smooth and learnable.
4. **Non-regressing harness consolidation (`H_r -> H_{r+1}`)**: Merge newly verified reusable primitives into $L_{r+1}$, distil concise precondition/pitfall notes into $M_{r+1}$, and update router $\rho_{r+1}$ to map each task signature to its winning route—**requiring zero regression on previously solved skill-dependent tasks** before updating $H_{r+1}$.

### Step 2: Build Failure-Balanced, State-Matched Counterfactual Pairs

Construct the round-$r$ distillation dataset for $\pi_\theta$ from two aligned sources:

1. **`50/50` uniform + failure-weighted task sampling**: Sample `50%` of training episodes uniformly across all tasks (preserving broad multi-task coverage) and `50%` proportional to $(1 - \hat{s}_{r,k})^\gamma$ ($\gamma > 0$, where $\hat{s}_{r,k}$ is task $k$'s current standalone policy success rate) so persistent bottlenecks receive concentrated gradient budget.
2. **Exact same-state counterfactual pairing `(x, y^+, y^-)`**: For every repaired failure state $x = (o_t, g)$ where $\pi_{\theta_r}$ diverged or stalled, pair:
   - **$y^-$ (Negative continuation)**: $\pi_{\theta_r}$'s own failed action chunk / trajectory segment starting from $x$, and
   - **$y^+$ (Positive counterfactual repair)**: The verified, jerk-filtered harness action chunk starting from the **exact same observation and goal state $x$** (resetting or branching from identical simulator state $x$, or matching verified recovery anchors on physical resets).

### Step 3: Update Executor Weights via Asymmetric-Proximity `CPD` + `EWC` (`H2P`)

Freeze a reference copy of the round-start executor weights $\bar{\theta}_r \leftarrow \theta_r$. Let $\ell_\theta(y \mid x)$ denote the executor's per-chunk action loss (e.g., flow-matching velocity MSE or negative log-likelihood; **lower $\ell_\theta$ = higher likelihood**), and define reference-anchored loss shifts:

$$\delta^+ = \ell_\theta(y^+ \mid x) - \ell_{\bar{\theta}_r}(y^+ \mid x), \qquad \delta^- = \ell_\theta(y^- \mid x) - \ell_{\bar{\theta}_r}(y^- \mid x), \qquad \Delta = \delta^+ - \delta^-$$

Optimize $\theta$ via the four-term `H2P` objective:

$$\mathcal{L}_{\mathrm{update}}(\theta) = \mathcal{L}_{\mathrm{sup}}(\theta) + \lambda_{\mathrm{pref}}\!\left(\mathcal{L}_{\mathrm{gap}}(\theta) + \lambda_{\mathrm{prox}}\mathcal{L}_{\mathrm{prox}}(\theta)\right) + \lambda_{\mathrm{EWC}}\mathcal{L}_{\mathrm{EWC}}(\theta)$$

1. **Supervised anchor (`\mathcal{L}_{\mathrm{sup}}`)**: Standard imitation loss $\mathbb{E}_{(x, y^+)}[\ell_\theta(y^+ \mid x)]$ over verified successful trajectories (clean anchors + verified harness repairs; e.g., `2.5K` clean + `5K` autonomous reaches `77.5%` on `RoboTwin C2R`, matching `27.5K` random-rollout data at **`27.3%` of the sample budget**).
2. **Squared margin gap (`\mathcal{L}_{\mathrm{gap}}`)**: $\mathbb{E}[(\max\{\Delta, -m\} + m)^2]$ ($m > 0$), driving $\delta^+ - \delta^- \le -m$ smoothly up to margin $m$ without unbounded log-sigmoid gradients once separated.
3. **Asymmetric anchor proximity (`\mathcal{L}_{\mathrm{prox}}`, critical anti-collapse guard)**:
   $$\mathcal{L}_{\mathrm{prox}}(\theta) = \mathbb{E}\!\left[\,[\delta^+]_+^2 + [\delta^- - \kappa]_+^2\,\right] \qquad ([u]_+ = \max(u, 0),\ \kappa > 0)$$
   - `$[\delta^+]_+^2$` forbids satisfying the margin purely by letting $y^+$'s loss *worsen* relative to $\bar{\theta}_r$ while pushing $y^-$ up faster;
   - `$[\delta^- - \kappa]_+^2$` caps how far $\ell_\theta(y^- \mid x)$ may rise above $\bar{\theta}_r$ (`\kappa` ceiling), preventing negative-sample gradient explosion in continuous flow-matching/diffusion action spaces (`+2.2 pp` additional Round-1 lift on top of `+\mathcal{L}_{\mathrm{gap}}`'s `+9.8 pp`, `Table 5`).
4. **Elastic Weight Consolidation (`\mathcal{L}_{\mathrm{EWC}}`)**: Penalize parameter drift weighted by the diagonal Fisher matrix on base/source capabilities (`92.5%` original `LIBERO` retention with `EWC` vs. **`72.0%` [`-20.5 pp` forgetting]** at $\lambda_{\mathrm{EWC}} = 0$, `Table 20`).

### Step 4: Gate Persistent Promotion and Optionally Chain Online RL

1. **Single Acceptance Gate**: Before promoting $(\theta_{r+1}, H_{r+1})$ as the new persistent incumbent, evaluate both standalone $\pi_{\theta_{r+1}}$ and hybrid $(H_{r+1}, \pi_{\theta_{r+1}})$ through `"DO: Pass every self-modification through one acceptance gate"` in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md): verify no regression beyond baseline noise margin $\delta$ (estimated across $\ge 3$ baseline runs) on protected source tasks and held-out OOD suites, and enforce strict zero tolerance on negative safety testbeds.
2. **Track API amortization & stopping**: Monitor per-round coding-agent cost and $|\mathcal{F}_r|$; stop co-evolution once standalone/hybrid held-out gains plateau within $\delta$ (`5–8` rounds in `arXiv:2611.34675`).
3. **Optional post-co-evolution online RL (`+ PPO`)**: Once `CPD` lifts standalone policy competence into the high-variance reward regime (`~84%` SR, avoiding `0`-variance outcome starvation), chaining online `PPO` further refines contact precision (`84.1% -> 94.8%` standalone and `90.5% -> 96.8%` hybrid on `LIBERO-PRO`, `Table 21`).

---

## Environment Caveats

- **Articulated/constrained kinematics still benefit from hybrid fallback at deployment**: On `40`-task `MolmoSpaces` (`Table 6`), standalone policy distillation reached `57.0%` overall (`65.8%` hybrid), but articulated `Open` tasks dropped to **`9.0%` standalone vs. `32.0%` hybrid**—keep $\rho_r$ hybrid fallback enabled in deployment for constrained Revolute/Prismatic joint tasks until tactile/force sensing or online RL closes the gap.
- **Cross-embodiment transfer of $H_r$**: Because $L_r$ and $M_r$ express geometry in task/object-relative frames rather than joint-space constants, a frozen harness evolved on `ALOHA AgileX` (`45.8%`) transferred zero-shot to unseen dual-arm `ARX-X5` (**`42.5%`**) and `Franka-Panda` (**`41.0%`**, `Table 7`) to bootstrap data collection on new robot morphologies without human teleoperation.
- **Open-weight vs. frontier coding-agent harnesses**: Replacing `GPT-6 Astra` (`84.1%` standalone / `90.5%` hybrid on `LIBERO-PRO`) with open-weight `Qwen3.8-27B` still achieved **`76.0%` standalone / `82.5%` hybrid** (`Table 19`), and swapping the executor from $\pi_{0.5}$ (`LoRA 512/512`) to `FastWAM` reached **`75.5%` standalone / `82.9%` hybrid**.
- **Manuscript figure/table notes (`arXiv:2611.34675`)**: `Fig. 3b` plots `RoboTwin C2R` Round-0 hybrid SR at two decimals (`48.84%`, rounded to `48.8%` in `Table 16` and prose); in `Table 4`, `All Routes` shows a `+13.5 pp` within-round repair delta (`35.6% -> 49.1%`) vs. `Code+Policy`'s `+14.8 pp` (`30.8% -> 45.6%`) solely because `All Routes` starts `+4.8 pp` higher before repair (`35.6%` vs. `30.8%`) and achieves the highest final hybrid (`49.1%`) and post-`H2P` policy (`32.1%`) accuracy.

---

## Failure Modes

- **Omitting asymmetric proximity $\mathcal{L}_{\mathrm{prox}}$ in preference distillation**: Unbounded negative-action pushing ($\delta^- \to \infty$) or unpenalized positive-loss drift ($\delta^+ > 0$) destabilizes continuous flow-matching/diffusion policies (dropping Round-1 `CPD` by `-2.2 pp` in `Table 5`, and collapsing pure anchor `DPO` to `0.1%` in `AeroRSI`).
- **Allowing `Code+ICL` to copy raw demo coordinates**: Hardcoding demonstration XYZ waypoints breaks immediately under object-pose or camera perturbations (`LIBERO-PRO` / `RoboTwin C2R`); enforce symbolic phase + object-relative offset extraction.
- **Omitting `EWC` (`\lambda_{\mathrm{EWC}} = 0`) during multi-round `H2P` updates**: Adapted `LIBERO-PRO` accuracy looks intact (`84.3%` vs. `84.1%`), **hiding a `-20.5 pp` catastrophic forgetting drop (`92.5% -> 72.0%`) on original `LIBERO` tasks** (`Table 20`).
- **Running single-direction `P2H-only` or `H2P-only`**: Leaves `-22.2 pp` (`46.1%` vs. `68.3%` hybrid) or `-18.7 pp` (`33.6%` vs. `52.3%` standalone) on the table by Round 3 (`Table 3`).

---

## Cross-References

- **Rules**:
  - [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Alternate model weight updates and harness search"`, `"DO: Verify trajectory failure recovery via greedy policy continuations across renewed pre-failure anchors with best-candidate distillation and on-policy retention"`, `"DO: Co-evolve shared-weight Improver and Solver roles via case-balanced counterfactual harness advantage rather than freezing either role"`, and `"DO: Pass every self-modification through one acceptance gate"`
- **Spec Templates**: [`../../specs/self-improving-agent.spec.md`](../../specs/self-improving-agent.spec.md) and [`../../specs/skill-library.spec.md`](../../specs/skill-library.spec.md)
- **Related Skills & Briefs**:
  - [`dual-role-model-harness-coevolution`](../dual-role-model-harness-coevolution/SKILL.md) — Shared-weight single-adapter `Improver`+`Solver` `GRPO` co-evolution for API/SQL agents (`MedicalRSI`, `arXiv:2611.26806`)
  - [`asynchronous-system1-harness-evolution`](../asynchronous-system1-harness-evolution/SKILL.md) — Asynchronous `state`/`proc`/`wm` System-2 synthesis for frozen System-1 action scorers (`JevRSI`, `arXiv:2611.22432`)
  - [`verifier-gap-sign-pre-rl-audit`](../verifier-gap-sign-pre-rl-audit/SKILL.md) — Auditing verifier gap sign and group variance ($u$) before chaining post-`CPD` RL (`arXiv:2611.21538`)
  - [`embodied-harness-dual-agent-manipulation-self-improvement`](../../research-briefs/embodied-harness-dual-agent-manipulation-self-improvement.md) — Frozen-VLM dual-granularity intra-episode working memory vs. cross-episode reflection (`Embodied-Harness`, `arXiv:2611.27689`)
  - [`aerorsi-continuation-verified-aerial-vln`](../../research-briefs/aerorsi-continuation-verified-aerial-vln.md) — Why unanchored anchor `DPO` collapses (`0.1%`) on aerial VLA recovery (`AeroRSI`, `arXiv:2611.24077`)
  - [`roboace-adversarial-curriculum-execution-coevolution`](../../research-briefs/roboace-adversarial-curriculum-execution-coevolution.md) — Alternating curriculum and execution harnesses when VLA weights are frozen (`RoboACE`, `arXiv:2611.13034`)
  - [`system-one-rsi-guided-practice-muscle-memory`](../../research-briefs/system-one-rsi-guided-practice-muscle-memory.md) — Offline visual `LoRA` consolidation paired with explicit Python `OODA` behaviour trees (`System-One RSI`, `arXiv:2611.26007`)
  - [`coevo-policy-aware-context-evolution`](../../research-briefs/coevo-policy-aware-context-evolution.md) — Alternating prompt edits and `GRPO` weight updates on math/code reasoning (`COEVO`, `arXiv:2609.33398`)

---

## Sources

- Liu, C., Lin, J., et al. (2026). *RoboEvo$^2$: Recursive Robot Self-Improvement via Harness-Policy Co-Evolution*. `arXiv:2611.34675` (`src:2611-34675v1`).
