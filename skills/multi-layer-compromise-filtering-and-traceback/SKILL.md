---
name: multi-layer-compromise-filtering-and-traceback
description: >-
  Detect persistent latent compromise across multi-agent memory, logic, and
  infrastructure layers using a zero-LLM event-triggered factored Kalman
  filter, multi-trigger conformal early warning, 2-hop RTS backward trace-back,
  and staged credible-set remediation. Derived from Swarm Shepherd
  (arXiv:2611.18693).
source: https://arxiv.org/abs/2611.18693
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Multi-Layer Compromise Filtering and Traceback

> **Source**: [Swarm Shepherd: Securing Multi-Agent Ecosystems Against Persistent Latent Compromise](https://arxiv.org/abs/2611.18693) (Zhang & Pei, 2026) | Praxis: `src:2611-18693v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Operating persistent multi-agent ecosystems (`LangGraph`, `CrewAI`, `AutoGen`, or custom orchestrators) that retain cross-session vector stores/checkpointers, editable prompts/skills/routing logic, or shared tool/container workspaces.
- Adding a zero-LLM, millisecond-latency CPU monitoring sidecar (`<= 3.1 ms` median per event at `N = 20–50`, `\$0.02`/agent/day) that warns multiple sessions before visible alignment failure without inserting an LLM judge on every turn.
- Remediating multi-agent compromises where restarting or quarantining only the visibly failing agent leaves upstream poisoned memory, modified prompts, or altered runtime packages intact to re-infect peers.

## Overview

Single-turn input filters, stateful single-session monitors, and per-call tool-privilege gates miss **persistent cross-layer compromises** whose individual steps stay within benign action envelopes while accumulating across three coupled substrates: **Memory (`L1`)**, **Agent Logic (`L2`)**, and **Infrastructure (`L3`)**. Across `LangGraph` (`v0.2+`), `CrewAI` (`v0.100+`), and `AutoGen` (`v0.4+`) over `4` topologies and `4` LLM backbones (`1,000` trials/cell), Zhang & Pei show that latent multi-layer propagation accelerates behavioural drift (`ASI < 0.7`) **`2.7–8.9x` faster** (`13.2–26.9` sessions vs. `73` natural-drift interactions), achieves uncontrolled reproduction **`R_0 > 1` on `8/9` framework-topology pairs** (`2.81–4.18` on `LangGraph`, `1.57–2.68` on `CrewAI`, `1.12–1.39` on `AutoGen` star/mesh, and `2.31` across a shared-ChromaDB `LangGraph`+`CrewAI` deployment), and evades `Prompt Guard 2` (`91.6%`), `Llama Guard 4` (`88.8%` in per-detector `Table 13`; `88.9%` aggregate evasion in `Table 1`), `Lakera Guard` (`88.1%`), `NeMo Guardrails` (`86.3%`), stateful `DeepContext` (`83.6%`), and runtime policy guards (`Progent` default `6.6%` detection, oracle ceiling `64.8 ± 2.9%`; multi-session `DRIFT` `31.6%` prevention; session-persistent `CaMeL` `38.4%` prevention).

**Swarm Shepherd** closes this gap with a pure-CPU statistical sidecar combining:
1. **Event-triggered 6D factored Kalman filtering + split-conformal warning**, firing **`3.2–3.9` sessions before visible `ASI` failure** (`AUROC 0.881–0.918`; `2.6 [2.1, 3.1]` sessions lead even when scored solely against an external task grader with `ASI` removed).
2. **Local `2`-hop Rauch–Tung–Striebel (`RTS`) backward smoothing**, localizing the initial patient-zero entry node and substrate at **`0.69 ± 0.02` top-1**, **`0.87 ± 0.01` top-3**, and **`0.72 ± 0.02` layer macro-F1** across `24` propagation variants.
3. **Staged top-3 credible-set substrate remediation**, driving live measured post-intervention reproduction below criticality (**`R_c = 0.81 [0.64, 0.97]`** on `LangGraph star` and **`0.62 [0.47, 0.81]`** on `AutoGen mesh`), whereas removing only the visibly failed node leaves **`R_c = 2.83 [2.44, 3.23]`** (`2.5` post-restart recurrences).

---

## Step-by-Step Implementation Procedure

### Step 1: Instrument the Dual-View Cross-Layer Telemetry Graph

1. **Maintain Persistent Substrate Nodes Alongside Agent Nodes**:
   - Represent the ecosystem as $\mathcal{E} = (\mathcal{A}, \mathcal{M}, \mathcal{L}, \mathcal{I})$ covering executing agents ($\mathcal{A}$), memory stores/collections ($\mathcal{M}$), mutable prompt/skill/workflow artifacts ($\mathcal{L}$), and tool/package/container environments ($\mathcal{I}$).
2. **Capture All `11` Typed Cross-Layer Edges via OTel + Kernel/FS Watchers**:
   - **Memory (`L1`)**: `read`, `write`, `retrieve` (via OpenTelemetry framework hooks on vector stores, checkpointers, and SQLite/Redis state).
   - **Agent Logic (`L2`)**: `invoke`, `return`, `modify`, `handoff` (inter-agent messages, delegation transfers, and writes to prompt/skill/config files).
   - **Infrastructure (`L3`)**: `grant`, `install`, `execute`, `egress` (capability grants, package installations, subprocess execs, and outbound network sockets via container eBPF or auditd).
3. **Extract Six Per-Node Proxy Coordinates ($d = 6$)**:
   - Anchor three coordinates to observable physical telemetry: **contamination ($c$)** (rolling retrieval rate of unverified-provenance or anomalous artifacts), **authority ($a$)** (empirical routing share and retrieval rank), and **capability exposure ($x$)** (active tool permissions and reachable resource count).
   - Pair them with three behavioural subscales: **susceptibility ($s$)**, **persistence ($p$)**, and **behavioural deviation ($d$)** (rolling tool-sequence, output-distribution, and constraint-adherence drift).

---

### Step 2: Calibrate Cold-Start Parameters Safely with Shadow-Mode Guards

1. **Fit Linear-Gaussian Dynamics Over `W ≈ 50` Benign Sessions**:
   - Estimate transition/emission matrices $(A_v, B_\tau, H_v, Q_v, R_v)$ via Expectation-Maximization (`EM`) once **`W ≈ 50` clean sessions** accumulate (`<10 min` CPU; false-positive rate drops from `21.8%` at `W = 0` to the `5.2%` elbow at `W = 50`).
   - When switching LLM backbones without full recalibration (which otherwise degrades detection `15%–50%` across model families), re-fit at minimum the diagonal emission adapter $H_m$ on benign traces from the new model to recover roughly half of the cross-backbone transfer loss.
2. **Enforce Shadow Mode and Taint Screening During Cold Start**:
   - While session count `< W`, suppress uncalibrated statistical drift (`T1`) interventions, **but keep deterministic policy (`T2`) and cryptographic hash/integrity (`T3`) triggers active** on every `modify`, `grant`, and `install` edge.
   - Screen the `W` calibration window for pre-existing compromise using an innovation-covariance whiteness check (`AUC = 0.79` at `5%` startup taint); reject or purge calibration windows whose estimated taint approaches or exceeds **`8%`**.

---

### Step 3: Run Event-Triggered Factored Filtering and Multi-Trigger Warning

1. **Update Only Active Nodes Per Event ($O(d^3 + |E_t(v)|d^2)$)**:
   - On each event touching active node set $\mathcal{A}_t$, run the `6x6` Kalman predict-update step only on $v \in \mathcal{A}_t$ and its incident active edges (`3.41x` faster than dense graph filtering; `2.3–3.1 ms` median at `N = 20–50` and `3.3 ms` p50 / `9.1 ms` p95 with `143 MB` RSS at `N = 5,000` on one CPU core).
2. **Compute Split-Conformal Early Warning Scores**:
   - Score each updated node's posterior contamination/deviation trajectory against held-out benign calibration nonconformity quantiles at target miscoverage $\alpha = 0.10$ (adding an explicit safety margin on decentralized `AutoGen` meshes where exchangeability shifts empirical coverage to `0.876`).
3. **Fuse Four Trigger Channels (`T1 ∨ T2 ∨ T3 ∨ T4`) Against Null-Space Evasion**:
   - Never gate alarms on `T1` Kalman innovation/drift alone: an adaptive adversary shaping emissions toward the observation null space $\ker(H)$ reduces `T1`-only detection to **`0.42 ± 0.031`** (`+34.5%` delay).
   - Always OR `T1` with **`T2` policy-boundary violations** (`modify`/`grant`), **`T3` file/skill/package hash integrity mismatches** (`install`/`modify`), and **`T4` external task-outcome/grader failures**. Multi-trigger fusion raises patient-zero top-1 attribution to `0.73` (`L1`), `0.81` (`L2`), and `0.86` (`L3`).

---

### Step 4: Execute `2`-Hop RTS Backward Trace-Back and Staged Credible-Set Remediation

When any trigger fires on node $v^*$ at event $t$, **do not simply restart or evict $v^*$**:

1. **Run Local `2`-Hop Rauch–Tung–Striebel (`RTS`) Smoothing**:
   - Extract the causal `2`-hop incoming subgraph $\mathcal{N}_2(v^*; \mathcal{G}^{\mathrm{obs}}_{\le t})$ over the historical event log and run backward RTS smoothing to compute posterior entry probabilities $P(\text{entry} = u, \text{layer} = \ell, t_0 \mid y_{1:t})$.
   - Weight candidate origins using three structural cross-layer invariants:
     - **`I1` (`L1` Memory)**: an anomalous/unverified `write` to $\mathcal{M}$ preceding downstream `retrieve` edges into drifting agents.
     - **`I2` (`L2` Logic)**: a `modify` edge on $\mathcal{L}$ (system prompt, skill file, or routing rule) without an authorized deployment change.
     - **`I3` (`L3` Infrastructure)**: an `install`, `modify`, or `grant` edge on $\mathcal{I}$ accompanied by a capability-exposure ($x$) jump.
2. **Remediate the Top-3 Credible Set in Three Reversibility Stages**:
   - Select the **top-3 posterior candidate origins** (`0.87 ± 0.01` true-origin coverage vs. `0.69` for top-1, cutting post-remediation recurrence from `0.31` to **`0.13`** at only `4.1%` utility cost):
     - **Stage 1 (Reversible Containment)**: Pause routing/delegation through the top-3 candidate agents and quarantine memory records written to incident $\mathcal{M}$ nodes inside the estimated entry window $[\hat{t}_0, t]$ from retrieval results without deleting them.
     - **Stage 2 (Corroboration)**: Run targeted provenance audits on quarantined `L1` entries, diff `L2` prompt/skill hashes against signed baselines, and inspect `L3` container/package diffs; release uncorroborated candidates cleanly.
     - **Stage 3 (Irreversible Substrate Sanitization)**: Only upon `T2`/`T3` or provenance corroboration, purge confirmed poisoned `L1` records, roll back mutated `L2` prompt/skill files (including compact `<= 40`-token prompt deltas where `T1` attribution drops to `0.41` without `T4`/`T3`), and rebuild affected `L3` tool/container images from clean manifests before resuming traffic and verifying $R_c < 1$.

---

### Step 5: Balance Per-Node History Depth Against Ecosystem Node Coverage

Allocate telemetry retention and instrumentation budgets along the two-scale operating boundary **`n_0(N) ≈ 8.3 N`** (empirical fit `C_emp = 8.31`, `95% CI [7.42, 9.18]`, e.g., `~170` retained events per node for an `N = 20` ecosystem):
- **Inference-Limited Regime (`n < 8.3 N`)**: Estimation error is dominated by per-node filter variance ($\propto 1/\sqrt{n}$). Increase per-node event retention and session history before instrumenting additional low-centrality peripheral nodes.
- **Coverage-Limited Regime (`n > 8.3 N`)**: Estimation error is dominated by unobserved subgraph hops ($\propto 1/\sqrt{N}$). Expand OTel and `L1`/`L3` edge instrumentation to unmonitored memory stores, shared checkpointers, and sub-agents rather than lengthening history windows further.

---

## Environment Caveats

- **Framework-Specific Amplification Paths**: `LangGraph` cyclic state graphs compound per-pass drift multiplicatively ($d_0(1+\delta)^{\lfloor m/k \rfloor}$, `R_0 = 2.81–4.18`)—harden shared state channels with schema/provenance checks. `CrewAI` concentrates blast radius in its single hierarchical Manager and shared `SQLite3` memory (`R_0 = 1.57–2.68`). `AutoGen` (`v0.4+`) Docker code-executor defaults keep `pipeline-3` subcritical (`R_0 = 0.82`), but `star-5` (`1.12`) and `mesh-7` (`1.39`) still cross criticality via conversational propagation.
- **Provenance Metadata Sensitivity**: Removing ground-truth memory provenance tags reduces overall early-warning `AUROC` modestly (`0.901 -> 0.871`, `3.3` sessions lead, `8.4%` clean FPR), but degrades `L1` memory-entry detection more sharply (`0.924 -> 0.848`); attach writer-agent IDs and source hashes at write time whenever possible.

## Failure Modes to Avoid

- **Evicting Only the Visibly Misbehaving Agent**: Leaving `L1` vector/SQLite residue, `L2` edited skill files, or `L3` modified packages untouched leaves live `R_c = 2.83` on `LangGraph star` (`79.1%` residual ASR) and guarantees re-compromise after restart.
- **Running `T1` Statistical Drift Monitoring Without `T2`/`T3`/`T4` Fusion**: Exposes the Kalman filter to observation null-space ($\ker(H)$) evasion and misses minimal (`~40`-token) system-prompt edits (`0.41` top-1 without `T3`/`T4`).
- **Calibrating `EM` Priors on Unverified Production Logs**: Fitting baseline matrices on startup traffic with `>= 8%` pre-existing taint teaches the filter to treat compromised latent dynamics as normal.

---

## Related Artifacts

- **Rule**: [Multi-Agent Coordination](../../rules/multi-agent-coordination.md)
- **Rule**: [Agent Sandbox Safety](../../rules/agent-sandbox-safety.md)
- **Spec**: [Agent Sandbox Spec](../../specs/agent-sandbox.spec.md)
- **Skill**: [State-Anchored Trajectory Auditing](../state-anchored-trajectory-auditing/SKILL.md)
- **Skill**: [Targeted Failure Attribution](../targeted-failure-attribution/SKILL.md)
- **Skill**: [Sealed Replayable Agent Audit Log](../sealed-replayable-agent-audit-log/SKILL.md)
