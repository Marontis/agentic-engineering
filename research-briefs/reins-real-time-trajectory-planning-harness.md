# REINS: A Self-Evolving Agent Harness for Real-Time Trajectory Planning

> **Source**: [arXiv:2611.10748](https://arxiv.org/abs/2611.10748) — Zhihong Cui, Hengyu Liu, Haoran Tang, Shijun Liu, Amir Taherkordi, Tor Skeie (2026)
> **Praxis Source ID**: `src:2611-10748v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`REINS` demonstrates how to close a verification-and-consolidation harness loop under **millisecond-level real-time control constraints**, but its concrete state representation (44 factored kinematic/traffic variables across `Env`, `Traffic`, `Ego`, `Action`, and `Outcome`, such as `TTC`, `THW`, and `DHW`), 5 discrete driving meta-actions, and all six experimental benchmarks (`highway-env` simulation plus `highD` and `rounD` drone trajectory replay) are specialized to **autonomous-driving tactical trajectory planning** (as noted in Section 6 & Appendix D.1 of the paper). Rather than extracting driving-specific predicate templates as a general coding skill, we record `REINS`'s quantitative architecture and latency/evolution findings here — complementing [`planner-controller-decoupling`](planner-controller-decoupling.md) — and link its generalizable verification/consolidation evidence to [`recursive-improvement.md`](../rules/recursive-improvement.md).

---

## Core Architecture: Three LLM–Planner Couplings Off the Real-Time Critical Path

Existing LLM trajectory planners face a structural dilemma: keeping the LLM in the synchronous control loop violates millisecond latency budgets (`4.36–10.93 ms`+ or full API round-trips), whereas compiling static rules offline (`PDDL`, `DriReg`) leaves the runtime planner unable to adapt to novel scenes and still wastes `3.71 ms` of `4.95 ms` per step re-grounding unindexed preconditions. `REINS` couples a frozen LLM (`GPT-4o`, `temp=0`, zero weight updates) to a real-time tactical planner via three mechanisms:

1. **Variable-Level Dynamics Grounding**: Maps raw observations into 44 typed domain variables and learns a sparse parent graph ($K = 5$ parents, lag $L = 6$) via LLM-prior-guided ridge regression ($\alpha = 0.6, \rho = 2.0, \lambda_0 = 0.1$) paired with a lightweight 2-layer Transformer dynamics model trained on `50k` episodes for closed-form multi-step rollout.
2. **Calibrated Predicate & Rollout Verification**: Compiles LLM-proposed rules into 7 typed rule templates calibrated against trajectory statistics (z-score with $\zeta = 1.5$, quantile, or absolute physical bounds) and filters every candidate rule through schema validation plus forward dynamics rollout before admission.
3. **$O(\log |\mathcal{R}|)$ Variable-Indexed Rule Consolidation (`Neo4j 5.12`)**: Stores verified, $\kappa$-hash-deduplicated rules in a variable-indexed property graph (`1,023` post-deployment rules across all 6 scenarios).
   - **Synchronous control path (`1.89–4.58 ms`)**: Queries the active state's variables in `<1 ms` (`0.41 ms` at `1,023` rules; `0.79 ms` even when inflated to `100,000` synthetic rules), activates only `2–3` matching rules per step, and scores the 5 meta-actions via closed-form rollout.
   - **Asynchronous miss-acquisition path (`1.59 s` mean, `2.96 s` p95)**: On a memory miss, the real-time loop immediately executes a **`2.6 ms` verified fallback** (`3.9 ms` p95) on the control thread while dispatching background LLM rule generation (`1.58 s` mean `GPT-4o` API time), rollout verification, and graph write-back so future similar scenes become fast memory hits.

---

## Key Empirical Findings

### 1. Real-Time Compliance, Collision Reduction, and Latency Across 6 Benchmarks

Evaluated across 4 `highway-env` scenarios (`Highway`, `Merge`, `Roundabout`, `Intersection`) and 2 naturalistic drone datasets (`highD` 4,237 vehicles; `rounD` 2,156 vehicles) over 5 seeds against 8 classical, runtime-LLM, RL, and symbolic baselines (Table 1):

| Scenario | Best Baseline (`Plan-R1`) Compl. / CR / PE | Runtime LLM (`DriveSpeak`) CR / PE | Unindexed Symbolic (`PDDL`) Compl. / CR / PE | `REINS` Compl. $\uparrow$ / CR $\downarrow$ / PE $\downarrow$ |
|:---------|:------------------------------------------:|:----------------------------------:|:--------------------------------------------:|:-------------------------------------------------------------:|
| **`Highway`** | `0.9717` / `12.83%` / `3.74 ms` | `38.28%` / `5.89 ms` | `0.9123` / `25.93%` / `4.95 ms` | **`0.9956` / `5.67%` / `2.50 ms`** |
| **`Merge`** | `0.9641` / `14.78%` / `2.24 ms` | `35.62%` / `5.21 ms` | `0.9011` / `21.52%` / `3.85 ms` | **`0.9924` / `6.86%` / `1.89 ms`** |
| **`Roundabout`** | `0.9568` / `18.57%` / `4.86 ms` | `39.19%` / `8.27 ms` | `0.8838` / `23.84%` / `5.38 ms` | **`0.9925` / `9.01%` / `3.62 ms`** |
| **`Intersection`** | `0.9553` / `20.37%` / `5.57 ms` | `44.27%` / `10.93 ms` | `0.8789` / `32.12%` / `6.77 ms` | **`0.9838` / `9.08%` / `4.58 ms`** |
| **`highD` (real)** | `0.9612` / `12.78%` / `3.89 ms` | `35.21%` / `6.12 ms` | `0.9078` / `23.12%` / `5.12 ms` | **`0.9867` / `6.12%` / `2.62 ms`** |
| **`rounD` (real)** | `0.9534` / `18.47%` / `4.56 ms` | `41.23%` / `8.56 ms` | `0.8956` / `26.78%` / `5.62 ms` | **`0.9856` / `9.45%` / `3.89 ms`** |

`REINS` achieves **`0.9838–0.9956` rule compliance**, cuts **collision rate (`CR`) by `49%–56%` below `Plan-R1`** (`5.67%–9.45%` vs `12.78%–20.37%`), and runs **`15%–33%` faster than `Plan-R1`** and **up to `58%` faster than runtime LLM baselines**.

### 2. Component Ablations: Every Coupling Is Load-Bearing

Across all 4 simulated scenarios (Table 2; `Highway` `Full`: `0.9956` Compl., `5.67%` CR, `2.50 ms` PE):
- **`w/o World Model` (constant-velocity propagation)**: Largest safety regression — CR jumps **`+49%` on `Highway` (`8.47%`)** and **`+48%` on `Intersection` (`13.45%`)**.
- **`w/o LLM Prior` (purely data-driven ridge structure)**: CR rises **`31%–46%`** (`8.26%` on `Highway`, `12.23%` on `Intersection`), confirming semantic priors regularize spurious trajectory correlations.
- **`w/o Rule Generation` (hand-crafted rules)**: Drops compliance to `0.9312` (`Highway`) and `0.8923` (`Intersection`) and nearly doubles CR (`11.23%` and `17.56%`), though the verification+indexing harness still keeps hand-crafted rules safer than matched no-harness `PDDL` (`21.37%`) and `DriReg` (`18.92%`).
- **`w/o Retrieval` (uniform activation of all rules)**: Raises CR by **`22%–43%`** (`8.12%` on `Highway`) *and* slows latency (`PE`) by **`34%–58%`** (`3.89 ms` on `Highway`, `6.12 ms` on `Intersection`) due to constraint conflicts across irrelevantly activated rules.

### 3. Online Self-Evolution Dynamics & Proposal Audit (`1,000` Episodes)

Deploying on `Highway` from an offline seed memory $|\mathcal{R}_0| = 88$ over `1,000` episodes (Table 3):
- **Monotonic LLM offloading + safety improvement**: Rule memory grows from `88` $\to$ `113` (ep. 250) $\to$ `127` (ep. 500) $\to$ `138` (ep. 750) $\to$ **`145` (ep. 1000)**; runtime **LLM call (miss) rate drops `5.5×` from `70.0%` $\to$ `48.44%` $\to$ `25.0%` $\to$ `12.81%`**, while compliance rises `0.9885` $\to$ **`0.9956`** and CR falls `7.05%` $\to$ **`5.67%`**. Against a **`Frozen R_0` control** (`0.9800` Compl., `9.63%` CR), online evolution adds **`+0.0156` compliance** and removes **`3.96` CR percentage points**.
- **Verification funnel (`~39,000` logged LLM proposals)**: `2.1%` failed schema validation, **`18.0%` failed forward rollout verification**, and the remaining `79.9%` collapsed under $\kappa$-hash deduplication to **`57` unique new rules** (`54/57` judged consistent with domain guidelines in manual audit; `3` over-specific rules never fired again).
- **Cross-LLM & domain-shift robustness**: Swapping `GPT-4o` for `Claude Sonnet 4.5` or `Qwen2.5-72B-Instruct` holds `Highway` CR at `5.89%` and `6.24%`. Under zero-shot transfer from `highD`/`rounD` to `highway-env`, call rate starts at **`86.2%`** (`11.84%` CR at ep. 250) because compiled thresholds are environment-specific, but online acquisition recovers CR to **`6.21%` by ep. 1000** (within `0.54` points of native memory, whereas frozen transferred memory stagnates at `11.20%` CR).

---

## Takeaways for Latency-Critical Agent Harnesses

1. **Move LLM synthesis off the synchronous control path behind a verified fast fallback**: Decoupling a `2.6 ms` indexed-rule/fallback control loop from a `1.59 s` asynchronous LLM rule-acquisition worker lets an agent self-evolve without ever blocking real-time actuation.
2. **Index consolidated rules by state-variable triggers rather than evaluating flat rule lists**: Uniformly applying all learned rules (`w/o Retrieval`) simultaneously hurt safety (`+22%–43%` collisions from conflicting constraints) and latency (`+34%–58%`), echoing selective skill/rule routing in [`policy-centroid-routing`](../skills/policy-centroid-routing/SKILL.md).
3. **Never transfer compiled numerical predicates zero-shot across shifted dynamics without online re-acquisition**: Domain shift spiked miss rate to `86.2%` (`11.84%` CR frozen vs `6.21%` with online verification+consolidation).

## Related Artifacts

- [`planner-controller-decoupling`](planner-controller-decoupling.md) — Architectural separation of slow LLM deliberation from fast real-time control loops
- [`policy-centroid-routing`](../skills/policy-centroid-routing/SKILL.md) — Selective context-conditioned rule activation to prevent rule-bloat interference (`arXiv:2608.30757`)
- [`world-model-trust-gating`](../skills/world-model-trust-gating/SKILL.md) — Gating planner rollouts against learned dynamics models (`arXiv:2609.26293`)
- [`recursive-improvement.md`](../rules/recursive-improvement.md) — Guardrails on rollout/oracle verification before rule registration
