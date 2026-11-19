---
name: asynchronous-system1-harness-evolution
description: >
  Decouple sub-second System-1 decision-model action selection from
  asynchronous System-2 LLM harness synthesis by assembling past (executable
  state-graph compaction), present (precondition-action rules), and future
  (counterfactual world-model lookahead) modules, quarantining failing modules
  after consecutive episode losses, and gating background updates via trajectory
  replay and prediction-accuracy checks. Derived from "Think Once, Act Fast:
  Cost-Effective Recursive Self-Improvement for Decision Model Harness"
  (JevRSI, arXiv:2611.22432).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Asynchronous System-1 Harness Evolution

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Use this skill when building **low-latency, cost-effective interactive decision agents** (such as multi-step CLI/workspace executors, game/simulation controllers, interactive troubleshooting bots, or discrete action-selection agents) where:

- A lightweight **System-1 decision model** (`9B–27B` or compact action scorer) must select actions from candidate sets $\mathcal{A}_t$ in **sub-second wall-clock latency (`0.08–0.58 s`)**, making per-step frontier LLM calls (`2.14–15.58 s`) or synchronous confidence-takeover cascades prohibitively slow and expensive.
- Long-horizon partial observability, unstated action prerequisites, and multi-step lookahead traps cause vanilla small models—and static one-shot LLM-generated harnesses—to fail or collapse out of distribution.
- You can run an **asynchronous System-2 LLM harness developer** off the critical execution path to synthesize, revise, and replay-verify reusable context modules (`state`, `proc`, `wm`) whose cost amortizes toward zero as library coverage matures.

Do **not** use this skill for **millisecond-hard (`< 5 ms`) continuous kinematic control** over fixed numeric state vectors (use the variable-indexed closed-form dynamics pattern in [`reins-real-time-trajectory-planning-harness`](../../research-briefs/reins-real-time-trajectory-planning-harness.md) instead), or when open-ended free-form code generation rather than discrete candidate action scoring is the primary per-turn output (use [`regularized-harness-evolution`](../regularized-harness-evolution/SKILL.md) or [`mcts-full-harness-optimization`](../mcts-full-harness-optimization/SKILL.md)).

## Overview

Static one-shot harness generation (`JevHarness`) and synchronous LLM takeover (`JevAgentHarness`, invoking an LLM whenever System-1 confidence $c_t < 0.8$) both fail to scale across interactive environments: in `JevRSI` (`arXiv:2611.22432`), static `JevHarness` (`StartLux-27B + DeepSeek-V4.1-Flash`) collapses from `36.00% / 40.00%` to `20.00% / 21.33%` on `BabyAI` and from `100.0% / 62.66%` to `52.66% / 1.33%` on `TextCraft`, while synchronous `JevAgentHarness` still collapses to `4.00%` OOD on `TextCraft` and pays full LLM latency on uncertain steps.

`JevRSI` ("Think Once, Act Fast") keeps a frozen System-1 executor on the synchronous control path (`0.08–0.58 s` per step) while a background System-2 LLM (`4` asynchronous workers) synthesizes and replay-gates three typed harness module classes covering **past, present, and future** decision context:

- **Large accuracy gains beating standalone LLMs at System-1 speed**: Pairing `StartLux-27B` with asynchronous `DeepSeek-V4.1-Flash` lifts `ALFWorld` ID/OOD success from `45.71% / 45.52%` to **`86.42% / 85.82%`** (`+89.06% / +88.53%` relative—surpassing standalone `DeepSeek-V4.1-Flash` LLM-agent execution at `80.71% / 82.83%`), lifts `BabyAI` to **`65.33% / 68.66%`**, and reaches **`100.0% / 64.00%`** on `TextCraft` (`70.66%` OOD with `Qwen3.8-27B`, vs. `55.33%` standalone `Qwen3.8-27B`), while cutting `TextCraft` ID inference cost by **`~93%` (`$0.36` vs. `$5.38` for `GPT-6.1 Sol`)** at `100%` `SR@1`.
- **Self-amortizing System-2 interventions**: Comparing the first vs. second half of `200`-episode training, background System-2 triggers drop from **`22 -> 3` (`ALFWorld`)**, **`126 -> 75` (`BabyAI`)**, and **`6 -> 0` (`TextCraft`)** as validated modules accumulate.

---

## Step-by-Step Procedure

### Step 1: Assemble Past, Present, and Future Context Around a Fast System-1 Executor

Keep the System-1 decision model $c_\theta$ strictly synchronous and non-blocking: at each step $t$, retain the `8` most recent `(action, observation)` pairs alongside a structured context tuple $x_t = F_{M_t}\bigl(q_t, c_t^{\mathrm{past}}, c_t^{\mathrm{now}}, c_t^{\mathrm{future}}\bigr)$ built from three typed module classes, then execute $a_t = \arg\max_{a \in \mathcal{A}_t} c_\theta(a \mid x_t, \mathcal{A}_t)$:

1. **Past state-compaction module (`state` $\to c_t^{\mathrm{past}}$)**: Execute a sandboxed Python state-abstraction function $\sigma_m$ (`<= 6,000` chars, capped at `50 ms` wall time and `20,000` executed Python lines per call) that parses raw step observations to update a **framework-managed** directed transition graph $G_t = (N_t, E_t)$ (keeping persistent graph state outside generated module code so faulty scripts cannot corrupt historical memory). Render a compact summary (`<= 1,200` chars: at most `12` recent state nodes and `12` outgoing transitions). *(Removing `state` drops `ALFWorld` ID/OOD by `-15.7` / `-17.9 pp`.)*
2. **Present procedural-rule modules (`proc` $\to c_t^{\mathrm{now}}$)**: Inject up to $K = 3$ concise textual precondition-to-action rules $b_m = \langle s_m \to \hat{a}_m \rangle$ specifying immediate action prerequisites and ordering invariants relevant to the current goal and state. *(Removing `proc` drops `BabyAI` ID by `-17.3 pp`.)*
3. **Future counterfactual world-model module (`wm` $\to c_t^{\mathrm{future}}$)**: Execute a sandboxed one-step transition predictor $\omega_m(s_t, G_t, \mathcal{A}_t)$ (`<= 20,000` chars, capped at `300 ms` and `500,000` executed Python lines per call) that predicts next abstract state $s_{t+1}^a$, step reward $R(s_t \mid a)$, and terminal flag $\textsc{DONE}_{t+1}^{(s_t \mid a)}$ (`<= 160` chars per candidate action $a \in \mathcal{A}_t$) so System-1 sees immediate action consequences without multi-turn LLM rollouts. *(Removing `wm` collapses `BabyAI` ID from `64.0%` to `37.3%`, a `-26.7 pp` drop.)*

### Step 2: Route Modules via Scope Tags, Empirical Utility, and Consecutive-Failure Quarantine

Never inject the entire module library or rank executable modules by embedding similarity alone:

1. **Filter `state` and `proc` by scope relevance and failure quarantine**: Restrict active candidates to
   $$\mathcal{C}_t = \bigl\{m \in \widehat{M}_t : \operatorname{Rel}(q_t, \operatorname{tag}(m)) > 0 \;\land\; f_t(m) < L\bigr\}$$
   where $f_t(m)$ counts consecutive failed episodes in which module $m$ was active (default quarantine threshold $L = 3$). **Quarantine any `state` or `proc` module reaching $f_t(m) \ge 3$ immediately**—removing it from System-1 retrieval until System-2 diagnoses and revises it.
2. **Rank active candidates by empirical episode utility**: Select `1` `state` module at episode start and up to $K = 3$ `proc` modules at each step using empirical utility $u_t(m) = n_t^*(m) / n_t(m)$ (successful episodes over total active episodes, with Laplace/optimistic tie-breaking for newly admitted modules).
3. **Route `wm` by Laplace-smoothed prediction accuracy**: Track each world-model module's one-step state/termination prediction accuracy independently of episode win/loss using Laplace smoothing (`+1` prior success and `+1` prior failure), selecting the highest-accuracy scope-matched predictor.

### Step 3: Buffer Low-Confidence Steps and Prediction Mismatches Off the Critical Path

Never block an in-progress episode waiting for System-2 synthesis. Instead, feed two lightweight asynchronous triggers into bounded background queues:

1. **Confidence-drop trigger for `state` and `proc` synthesis**: Whenever System-1's top-action confidence falls below threshold $\eta$ ($c_t < \eta$, default $\eta = 0.5$), record a local failure window containing step $e_t$ plus the next `3` trajectory steps, and flush buffered windows at episode end into a bounded FIFO queue (capacity `64` items) served asynchronously by System-2 worker threads (default `4` workers, `temperature = 0`, `8,192` diagnosis / `16,384` code-development max output tokens).
2. **Counterfactual mismatch trigger for `wm` synthesis**: At episode end, compare `wm`'s predicted one-step outcomes $\widehat{Y}_{t+1}$ against observed compacted states $s_{t+1}$. Whenever observed transitions contradict $\widehat{Y}_{t+1}$ (or no `wm` exists yet for the task scope), dispatch a background `wm` synthesis/revision job containing at most `8` prediction-error examples and `30` observed graph transitions.

### Step 4: Gate Candidate Modules on Historical Trajectory Replay Before Library Publish

System-2 diagnoses whether a buffered failure stems from missing history (`state`), missing action prerequisites (`proc`), or wrong lookahead (`wm`), and proposes a targeted module addition or revision. Enforce deterministic sandbox admission gates before publishing to active library $\widehat{M}_t$:

1. **`state` replay gate**: Compile $\sigma_m$ and replay it across every step of the recorded episode inside an isolated sandbox (`50 ms` / `20,000`-line limit). Require **zero runtime exceptions and valid non-empty graph state output**, allowing **at most `1` automated repair attempt** (`proc` syntax/schema checks likewise allow at most `1` repair).
2. **`wm` historical transition gate**: Replay candidate $\omega_m$ across a stratified buffer of `~150` historical transitions (`>= 5` transitions per task, retaining up to `400` transitions per task and `200` recent prediction records) plus current-episode transitions (`300 ms` / `500,000`-line limit):
   - Require **zero execution errors** and checkable non-trivial predictions on **`>= 50%`** of transitions.
   - For **new `wm` modules**, require **`>= 60%`** exact one-step prediction accuracy.
   - For **`wm` revisions**, require accuracy on the identical replay slice to **drop by at most `2` percentage points** relative to the incumbent module while resolving the triggering mismatch (allowing **at most `2` repair attempts**).

### Step 5: Monitor System-2 Trigger Volume and Gate Persistent Library Releases

1. **Audit System-2 trigger frequency when swapping developer models**: Do **not** assume a stronger standalone frontier LLM automatically makes a better System-2 harness developer. In `JevRSI` (`Table 2` & `§4.3`), pairing `StartLux-27B` with `GPT-6.1 Sol` initiated **only `10` System-2 development episodes on `BabyAI`**—compared to `67` with `Qwen3.8-27B` and `49` with `DeepSeek-V4.1-Flash`—leaving the harness library under-populated and **underperforming by `-13.33` to `-14.67 pp` ID and `-6.67` to `-13.33 pp` OOD** (`50.66% / 55.33%` vs. `64.00% / 62.00%` and `65.33% / 68.66%`). Log cumulative System-2 trigger and admission counts per `50` episodes; if trigger volume stalls while System-1 failure rate remains high, recalibrate $\eta$ or decouple trigger detection from the developer LLM's self-confidence.
2. **Pass persistent library snapshots through the single acceptance gate**: Replay-verified background admission governs online search-time module availability; before promoting an evolved harness library $\mathcal{M}$ as a persistent production release or freezing it for deployment, pass it through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md): verify zero regression beyond baseline noise margin $\delta$ (estimated from at least `3` unchanged baseline runs) on protected previously-correct cases and held-out OOD splits, and enforce **strict zero tolerance** on the immutable negative security testbed (including sandbox escape and resource-cap checks on executable `state` and `wm` Python modules).

---

## Environment Caveats

- **Discrete vs. unconstrained action spaces**: `JevRSI` assumes System-1 scores a discrete or candidate-enumerated action set $\mathcal{A}_t$ at each step (`ALFWorld`, `BabyAI`, `TextCraft`). When actions are unconstrained shell scripts or multi-file patches, generate top-$k$ candidate actions first or apply [`selective-step-verification`](../selective-step-verification/SKILL.md) (`SWE-VERIFIER`) on low-confidence steps.
- **Cold-start amortization horizon**: During the first `10–30` episodes in a novel environment, System-1 runs near its vanilla baseline while asynchronous System-2 workers populate initial `state`, `proc`, and `wm` modules. Warm-start from `50–200` offline practice episodes when zero-episode cold-start errors carry high user cost.
- **Strict sandbox isolation for `state` and `wm` code**: Because `state` and `wm` are LLM-synthesized Python functions executed on every System-1 step, enforce hard AST/import whitelists, read-only copies of $G_t$ inside `wm`, and strict per-call instruction/wall-clock quotas (`50 ms` / `300 ms`) so synthesized code can neither hang the fast path nor mutate external state.

## Failure Modes

- **Synchronous confidence-takeover cascades**: Handing live control to System-2 whenever $c_t < 0.8$ (`JevAgentHarness`) couples user-facing latency to multi-second LLM generation (`2.14–15.58 s`) and still collapses to `4.00%` OOD on compositional `TextCraft` tasks because insights are never compiled into reusable System-1 state/world-model abstractions.
- **Letting `state` scripts own raw persistent memory**: Allowing synthesized $\sigma_m$ code to overwrite the persistent episode graph directly causes a single buggy revision to corrupt downstream `wm` predictions; always keep $G_t = (N_t, E_t)$ framework-managed and validate $\sigma_m$ outputs before commit.
- **Omitting consecutive-failure quarantine ($L = 3$)**: Without $f_t(m) < L$, an over-general `proc` rule or brittle `state` parser that passed single-episode replay continues to match `tag(m)` on OOD variants, repeatedly dragging System-1 below baseline.
- **Unmonitored developer under-triggering**: Swapping in a high-cost frontier System-2 model that abstains from module synthesis (`10` dev steps vs. `49–67`) starves the harness library while giving the false impression of low maintenance overhead.

## Cross-References

- Acceptance governance: [`recursive-improvement.md`](../../rules/recursive-improvement.md) (`"DO: Pass every self-modification through one acceptance gate"`)
- Millisecond kinematic trajectory planning with variable-indexed rules: [`reins-real-time-trajectory-planning-harness`](../../research-briefs/reins-real-time-trajectory-planning-harness.md)
- Low-confidence step verification on unconstrained coding trajectories: [`selective-step-verification`](../selective-step-verification/SKILL.md)
- Offline contrastive meta-skill precomputation + bounded online harness patches: [`contrastive-meta-skill-harness-evolution`](../contrastive-meta-skill-harness-evolution/SKILL.md)
- Regularized single-component harness search: [`regularized-harness-evolution`](../regularized-harness-evolution/SKILL.md)
- Continual reference-free text playbook gating under drift: [`regret-guided-continual-harness-evolution`](../regret-guided-continual-harness-evolution/SKILL.md)
