# A Cross-Scenario Survey and Analysis of Self-Evolving Multimodal Agents

> **Source**: [arXiv:2611.14256](https://arxiv.org/abs/2611.14256) — Jingjing Jiang (2026)
> **Praxis Source ID**: `src:2611-14256v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This `419`-reference cross-scenario survey and analytical study constructs a formal taxonomy, a two-ceiling positioning matrix, five cross-cycle degradation pathways, and directed portability rules across four multimodal agent domains (**Multimodal Reasoning [`MR`]**, **Multimodal Generation [`MG`]**, **GUI/Web Navigation [`GW`]**, and **Embodied Manipulation [`EM`]**). Rather than introducing a single executable subtask procedure, its contribution is **structural demarcation and mechanism-portability diagnosis**—explaining why self-evolving mechanisms (`self-play`, `consensus voting`, `refit step verifiers`, `world-model rollouts`, `skill/memory reuse`) succeed in one multimodal regime yet become **redundant**, **conditional**, or **blocked** in another. Its actionable engineering precondition check is extracted as a decision rule for `output/rules/recursive-improvement.md`, while the full cross-scenario synthesis and measurement agenda are preserved here.

---

## 1. Formal Demarcation: Genus Criteria & Self-Reference Differentia

Prior surveys conflate test-time compute, standard RLVR on static datasets, continual learning, and true self-evolution. Jiang formalizes a static multimodal agent as $\mathcal{A} = (\Phi_\theta, \mathcal{M}, \mathcal{T}, \mathcal{I})$ (requiring $\Phi_\theta$ to directly encode or decode at least one non-textual channel without intermediate text conversion—so HTML/accessibility-only web agents count as text-only) and unfolds interaction at two scales:

- **Micro-scale episode loop**: Fixed persistent state $(\Phi_\theta, \mathcal{M}_{\mathrm{long}}, \mathcal{T}, \mathcal{I})$ with only episodic buffer $\mathcal{M}_{\mathrm{short}}$ updating across steps $t \in \{0, \dots, T-1\}$.
- **Macro-scale cycle loop**: $\mathcal{H}_k \xrightarrow{\sigma_\omega} \boldsymbol{g}_k \xrightarrow{p^{\pi_{\mathcal{A}_k}}_{\boldsymbol{g}_k}} \mathcal{D}_k \xrightarrow{V_\nu} V_\nu(\mathcal{D}_k) \xrightarrow{f_\zeta} \mathcal{A}_{k+1}$, governed by three macro meta-operators: **goal sampler** $\sigma_\omega$, **feedback function** $V_\nu$, and **evolution operator** $f_\zeta$.

A system qualifies as a **self-evolving multimodal agent** if and only if its loop passes **four genus criteria** (which define an *autonomous learning loop*) plus **one differentia**:

1. **$\mathcal{C}_1$ Autonomy**: Zero runtime human annotations, verdicts, approvals, or teleoperated actions across $\sigma_\omega$, $V_\nu$, $f_\zeta$, and $\mathcal{D}_k$ for all cycles $k \ge 0$ (bootstrap artifacts fixed before $k = 0$ are permitted; physical human scene resets modify $\mathcal{P}_g$ outside the learning operators and are tracked separately as budget overhead).
2. **$\mathcal{C}_2$ Freshness**: Cycle-$k$ rollouts $\mathcal{D}_k$ depend on the current policy $\pi_{\mathcal{A}_k}$ (on-policy or bounded-lag asynchronous), excluding static offline pools or trajectories cached once under $\mathcal{A}_0$.
3. **$\mathcal{C}_3$ Durability**: $f_\zeta$ alters persistent substrate components ($\Phi_{\theta_k}$, $\mathcal{M}_{\mathrm{long}}$, $\mathcal{T}_k$, or $\mathcal{I}_k$) so $\pi_{\mathcal{A}_{k+1}} \neq \pi_{\mathcal{A}_k}$ on at least one goal—excluding test-time scaling (`Self-Consistency`) and single-episode `Self-Correction` (`Self-Refine`, `CRITIC`) confined to $\mathcal{M}_{\mathrm{short}}$.
4. **$\mathcal{C}_4$ Recurrence**: $\mathcal{A}_k \mapsto \mathcal{A}_{k+1}$ iterates over multiple rounds or online steps where each cycle's output becomes the next cycle's acting agent, excluding one-shot $\mathcal{A}_0 \mapsto \mathcal{A}_1$ pipelines.
5. **Differentia — Self-Reference (`SR`)**: Recorded in a provenance matrix $\boldsymbol{\Gamma}(m) \in \{0, 1\}^{3 \times 4}$ indexing rows $(\sigma_\omega, V_\nu, f_\zeta)$ against provenance columns `(h: runtime human, b: bootstrap, e: environment/task generator, a: agent)`. Autonomy requires $\boldsymbol{\Gamma}(m)\mathbf{e}_h = \mathbf{0}$; self-reference requires **$\boldsymbol{\Gamma}(m)\mathbf{e}_a \neq \mathbf{0}$**—the agent itself (active policy, internally trained role, or shared-lineage snapshot) must realize at least one meta-operator. Autonomous loops with $\boldsymbol{\Gamma}(m)\mathbf{e}_a = \mathbf{0}$ (such as `SimpleVLA-RL`, `ZeroGUI`, `Tülu 3`, or `TextGrad` when an external fixed `GPT-4o` optimizes `GPT-3.5-Turbo`) are **fixed loops**, which serve as structural controls rather than self-evolving agents.

---

## 2. Three-Stage Decomposition & Two-Ceiling Positioning Matrix

Every cycle factors into three scenario-invariant stages, each governed by the product of two diagnostic factors:

| Stage | Meta-Operator | Diagnostic Effectiveness | Governing Factors & Failure Modes |
|:------|:--------------|:-------------------------|:----------------------------------|
| **Stage 1: Experience Generation (`EG`)** | Goal sampler $\sigma_\omega$ + rollout $p^{\pi_{\mathcal{A}_k}}$ | $\mathcal{Q}_k^{\mathrm{EG}} = K_k \cdot \mathbb{E}_{g \sim \sigma_\omega}[I_{\mathcal{A}_k}(g)]$ | **Quantity $K_k$** (per-goal rollouts, capped by $\bar{K} := B / \mathbb{E}_\tau[c(\tau)]$) $\times$ **Quality $\mathbb{E}[I_{\mathcal{A}_k}]$** (outcome variance $\mathrm{Var}[\mathrm{ret}_g(\tau)]$, reducing to $p_g(1 - p_g)$ under binary terminal rewards—vanishing when tasks are mastered [$p_g \to 1$] or unreachable [$p_g \to 0$]). |
| **Stage 2: Feedback Acquisition (`FA`)** | Feedback function $V_\nu$ | $\mathcal{Q}_k^{\mathrm{FA}} = (2F_\nu - 1)\cdot \mathbb{E}_\tau[L_\nu(\tau)]$ | **Fidelity $F_\nu \in [0, 1]$** (pairwise agreement with true return $\mathrm{ret}_g$, Goodman–Kruskal correlation $2F_\nu - 1$, capped by $\bar{F} := \sup_{\nu \in \Xi_V} F_\nu$; optimizes *against* $R$ if $F_\nu < 0.5$) $\times$ **Localization $L_\nu(\tau) \in (0, 1]$** (fraction of environment actions receiving credit; finer $L_\nu$ never rescues a gameable $F_\nu$). |
| **Stage 3: Update Consolidation (`UC`)** | Evolution operator $f_\zeta$ | $\mathcal{Q}_k^{\mathrm{UC}} = S_\zeta \cdot G_\zeta$ | **Retention $S_\zeta \in [0, 1]$** (fraction of cycle-$k$ gain on $\mathcal{G}_k$ surviving $j$ later cycles) $\times$ **Generalization $G_\zeta \in [0, 1]$** ($\mu_{\mathcal{G}}$-measure of out-of-batch goals $\mathcal{G} \setminus \mathcal{G}_k$ with positive gain $\Delta_k(g) > 0$). |

### Four-Quadrant Scenario Positioning (`\bar{K}` vs. `\bar{F}`)

Only $\bar{K}$ (rollout affordability ceiling) and $\bar{F}$ (attainable feedback fidelity ceiling) are both **scenario-exogenous** and **substitution-resistant**, placing the four scenarios into four distinct quadrants:

| Scenario | Ceilings (`\bar{K}`, `\bar{F}`) | Binding Stage Bottlenecks (`EG` / `FA` / `UC`) | Verified Empirical Operating Points |
|:---------|:--------------------------------|:-----------------------------------------------|:------------------------------------|
| **Multimodal Reasoning (`MR`)** | **High $\bar{K}$, High $\bar{F}$** (neither ceiling binds) | `EG`: Quality at saturation (`K_k = 4–10`; `EvoLMM` collapses at `12` samples)<br>`FA`: **Endogenous** realized $F_\nu^{(k)}$ once keys are dropped<br>`UC`: Retention (long-cycle drift) | Program-computed answers (`VQS`) stay `94.4%` accurate on `500` human-audited questions (`5.6%` error), vs. **`24%` wrong** for retained majority-vote labels and **`18%` wrong** for model-judge labels. Pseudo-label accuracy drops `72.0% -> 61.0%` over `3` `VisPlay` rounds (`MM-Vet` drops `48.62 -> 38.07`) and `64.5% -> 37.5%` over `5` `Video-Zero` rounds. |
| **Multimodal Generation (`MG`)** | **High $\bar{K}$, Low $\bar{F}$** (open-ended prompts lack equivalence checks) | `EG`: Quality at edge of checkable pools (`Flow-GRPO` saturates `GenEval` `0.63 -> 0.95`)<br>`FA`: Attainable ceiling $\bar{F}$ (gameable perceptual proxies)<br>`UC`: Retention (compounding reward hacking) | `ManimAgent`'s frozen reviewer correlates negatively with blind human ratings on `37` educational videos (**$r = -0.17$**). `SOLACE` degenerates into textureless images and `IRIS` into meaningless images within hundreds of steps. Execution-verified charts in `RSI in UMMs` reach `59.0%` vs. `46.3%` (`+8.6` pts vs. `+0.5` pts from frozen self-ratings), while vocabulary switch drops prior exact text `72% -> 60%` and erodes `MMBench` by `-2.6` pts. |
| **GUI / Web Navigation (`GW`)** | **Low $\bar{K}$, High $\bar{F}$** (in sandboxed VMs with state scripts; live web drops $\bar{F}$) | `EG`: Quantity ($2.5\text{–}4.0\text{ s/step}$ VM latency; tens-of-minutes episodes; `5–10 min` environment re-init)<br>`FA`: Localization ($L_\nu$ spread over `25–50` steps)<br>`UC`: Cross-platform generalization | Initial success often starts near zero (`11.3%` `SEAgent`, `18.1%` `UI-Genie` on `AndroidLab`). `EvoSkill-GUI`'s same-backbone critic errs on **`28/143` audited failures** (passing `>=4` failures as successes). Reader capability flips memory value: `WebCoach`'s condensed memory **lowers `Qwen2.5-VL-7B` (`32.8% -> 31.1%`)** while **raising `Skywork-r1v3-38B` (`47.3% -> 61.4%`)**. |
| **Embodied Manipulation (`EM`)** | **Low $\bar{K}$, Low $\bar{F}$ on hardware** (simulation shifts toward `GW` cell) | `EG`: Both quantity & quality (`~20 h` per real-robot run with human resets; `6.58%` of `456` autonomous episodes need human scene recovery)<br>`FA`: Both fidelity (`69%–100%` image-judge accuracy; blind to contact/force; `2.6–16.9 s` per judge query) & localization<br>`UC`: Sim-to-real & cross-interface generalization | `SEAR` policies drop from `87.8%` (code) / `73.2%` (VLA) on practiced tasks to `33.3%` / `43.1%` on new tasks and **`28.7%` / `10.2%`** across simulators/interfaces. One `SEAR` run saved a self-built verifier wrong on **`91%` of later rollouts**, finishing at `4.6%` vs. `15.5%` / `23.6%`. In `Scale and Selection`, accepting every harness revision collapses success **`40% -> 0%`** over `20` rounds, whereas champion–challenger gating lifts held-out success **`51% -> 67%`**. |

---

## 3. Cross-Cycle Coupling & Five Degradation Modes

Recurrence ($\mathcal{C}_4$) couples cycles through **two internal edges**—the **agent edge** ($\mathcal{A}_k \to \mathcal{A}_{k+1}$, which extends into $\sigma_\omega$, $V_\nu$, or $f_\zeta$ whenever the agent realizes them) and the **goal edge** ($\mathcal{H}_{k+1} \to \sigma_\omega$ under adaptive curricula)—plus an exogenous **environment path** (live website drift or sim-to-real gap). Under Jiang's **mitigation-locality reading**, where a failure *surfaces* rarely matches where it must be *mitigated*:

1. **Compounding reward hacking**: In-support bias in $V_\nu$ re-amplifies across cycles when $V_\nu$ shares or tracks $\mathcal{A}_k$. *Surfaces at*: `UC`. *Carried by*: Agent edge (into `FA`). *Mitigate upstream at*: `FA` (tighten $F_\nu$ with external/programmatic checks or freeze/decouple the verifier; shrink update step).
2. **Distribution shift**: Improving rollouts leave $V_\nu$'s calibration support (for example, frozen progress heads in `Self-Improving EFMs` encountering out-of-demonstration robot states, or live web DOM drift). *Surfaces at*: `FA`. *Carried by*: Agent edge & environment path. *Mitigate at*: `FA` recalibration or `EG` resampling.
3. **Forgetting and plasticity loss**: Moving goal distributions cause parameter interference in $\Phi_\theta$. *Surfaces at*: `UC`. *Carried by*: Goal edge & environment path. *Mitigate upstream at*: `EG` (trajectory/specification replay, as in `DigiRL`, `MobileRL`, and `RSI in UMMs`) or parameter isolation/reset.
4. **Curriculum collapse**: Adaptive $\sigma_\omega$ contracts goal support toward mastered or trivial tasks (or drops persistently failing tasks, as `MobileRL` risks by design), driving $\mathbb{E}[I_{\mathcal{A}_k}] \to 0$. *Surfaces at*: `EG`. *Carried by*: Goal edge or agent edge into $\sigma_\omega$. *Mitigate at*: `EG` (explicit exploration/diversity bonuses and intermediate-difficulty $p_g(1-p_g)$ targeting).
5. **Model collapse**: Training on self-generated answers, images, or world-model videos erases policy tails under any goal sampler (`World-VLA-Loop` video rollouts degrade past `~300` frames). *Surfaces at*: `EG`. *Carried by*: Agent edge. *Mitigate at*: `EG`/`UC` (accumulate real/external experience rather than replacing it; trust-weight imagined chunks as in `MERL`).

*(Note: **Erroneous non-parametric writes** travel along the agent-edge extension into `UC` whenever the acting model writes and self-approves its own skills/memories without an external online check; writer identity alone can flip transfer sign—in `SEAR` on `RoboLab`, `GPT-5.6-sol` dropped from `46.9%` without a skill library to `42.4%` with its own self-written library, yet rose to `60.6%` when reading a library authored by `Claude Opus 5`.)*

---

## 4. Asymmetric Mechanism Portability Verdicts (`Tables XIII & XIV`)

Portability from source scenario $X$ to target scenario $Y$ is **directionally asymmetric** because verdicts are evaluated in a strict three-tier order over the **target scenario's properties**:

1. **Observability first (`Blocked` `✗`)**: If the target task's true outcome appears neither in the agent's observations nor in any check available to the loop—such as **background-state `GW` goals (`^f`)** invisible on reachable screens without backend scripts, or **contact-rich `EM` assembly (`^e`)** where camera frames omit contact forces (`FailBench` VLM judges cap at `<= 0.60` balanced accuracy vs. `0.77` overall)—every mechanism that checks or judges outcomes (`success-conditioned allocation`, `agent-posed goals`, `record-conditioned goals`, `self-consistency vote`, `self-judgment`) is **blocked**, even model-only judges. `Refit verifiers`, `frozen estimators`, and `memory/skill reuse` drop to **conditional** (retaining only visible step progress or unjudged writes).
2. **Scarcity second (`Redundant`)**: If the factor a mechanism raises is **not scarce** in the target, the mechanism is **redundant**:
   - *Learned world models* (which raise $K_k$ beyond $\bar{K}$ at the cost of $F_\nu$) are **redundant** in `MR` and `MG`, where single-pass rollouts already enjoy high $\bar{K}$.
   - *Votes, self-judgment, and generator-confidence rewards* are **redundant** on `MR` tasks with answer keys/program checks (`^a`) and on `GW` tasks with online outcome scripts (`^b`).
   - *Refit step verifiers and frozen progress estimators* are **redundant** only on keyed/program-checked `MR^a` (where single-step answers fix $L_\nu = 1$), remaining active in `GW` and `EM` where long-horizon localization $L_\nu$ is scarce.
3. **Task-structural resources third (`Portable` vs. `Conditional`)**: When outcomes are observable and the target factor is scarce, portability depends on three task-structural resources—**output equivalence**, **checkable outcomes**, and **resettable rollouts**:
   - Moving **`MR -> MG` or `EM` (hardware)** turns `self-consistency voting`, `success-conditioned allocation`, and `agent-posed goals` **conditional** on sub-families or adaptations (converting generated images into VQA ensembles as in `ASG`, restricting `MG` to program-verified charts/OCR, or adding an audited hardware VLM judge), while **`EM/GW -> MR^a`** renders world models and step estimators **redundant**.
   - **`Episode reuse via memory or skills`** raises $\mathbb{E}[I_{\mathcal{A}_k}]$ and $G_\zeta$ (scarce in all four scenarios) and is **portable** across observable `MR`, `MG`, `GW`, and `EM` targets—provided writes are gated by an **online check outside the writer** rather than reusing the writer's own uncalibrated self-judgment.

---

## 5. Evaluation Audits & Falsifiable Measurement Agenda

Audits of multimodal benchmarks and self-evolving loops reveal four severe measurement confounds that future evaluations must control:

- **Benchmark memorization & reward exploits**: `Sphinx-X-MoE` scores `43.6%` on `MMMU` *without images* (`+17.9` points above its text backbone); VLAs exceeding `90%` on `LIBERO` collapse to **`0.0%`** under `LIBERO-PRO` perturbations; `GenEval` diverges from human judgment by up to `17.7` points; and `BenchJack` achieves near-perfect scores on most of `10` agent benchmarks without solving tasks.
- **Retry and compute confounds**: On `MemGUI-Bench`, `3` retries *without persistent memory* raise `M3A` by **`+14.9` points**, whereas ablating `Agent-S2`'s long-term memory at the same `3`-attempt budget costs `-20.0` points—proving multi-round gains cannot be attributed to self-evolution without a **budget-matched fixed-loop / retry baseline** (counting tokens, environment steps, wall-clock, and human hardware resets).
- **Grader-exposure leakage**: Returning official evaluation verdicts inside the self-evolution loop inflates apparent gains via grader exploitation—on `PhysRSI-eval`, late-round successes drop from **`15/36` with grader access to `5/36` without it**, and embodied gains under exposed simulator predicates vanish under minor predicate perturbations.
- **Autonomy–safety erosion**: Under autonomous updates ($\mathcal{C}_1$), safety degrades along parameter, memory, tool, and workflow channels alike—on `RiOSWorld`, `SEAgent`'s unsafe task completion rate rises from **`39.5%` to `55.3%`**, and benign-only experience accumulation increases downstream attack success on high-risk web and embodied tasks.

---

## Relevance to Praxis

- **Direct theoretical & empirical backing for Praxis's single acceptance gate**: The `Scale and Selection` collapse (`40% -> 0%` un-gated vs. `51% -> 67%` champion–challenger), `SEAR`'s `91%`-wrong self-saved verifier (`4.6%` vs. `23.6%`), and `RiOSWorld`'s `39.5% -> 55.3%` unsafe completion surge reinforce `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../rules/recursive-improvement.md)—confirming that self-written updates must always be gated by an external reference and a strict zero-tolerance security testbed.
- **Cross-scenario mechanism-portability rule**: Contributes a pre-transfer architectural check to [`recursive-improvement.md`](../rules/recursive-improvement.md) (auditing outcome observability, target factor scarcity under $(\bar{K}, \bar{F})$, task-structural resources, writer–reader capability mismatch, and budget-matched fixed-loop baselines before porting self-evolution loops across modalities).
- **Connects directly to sibling skills in this batch**:
  - [`falsification-gated-memory-evolution`](../skills/falsification-gated-memory-evolution/SKILL.md) (`arXiv:2611.14326`) operationalizes the exact online verifier-gated memory-admission and post-commit eviction guard that prevents the erroneous non-parametric writes documented in `Mobile-Agent-E` and `SEAR`.
  - [`certified-task-verifier-harness`](../skills/certified-task-verifier-harness/SKILL.md) (`arXiv:2611.13336`) addresses Stage 2 reference construction under strict generation–scoring separation (`BenchJack` / `PhysRSI-eval` anti-leakage) and state-over-dialogue precedence (`Don't Read the Log`).
- **Extends existing briefs**: Generalizes [`verifier-survey-no-free-checker.md`](verifier-survey-no-free-checker.md), [`criteria-exposure-verifier-overfitting.md`](criteria-exposure-verifier-overfitting.md), and [`flex-rsi-frontier-agent-benchmark.md`](flex-rsi-frontier-agent-benchmark.md) across all four multimodal agent quadrants.
