---
name: service-mesh-agent-self-healing
description: >-
  Wrap multi-agent workflows in a decoupled service-mesh architecture with per-agent
  Resilient Proxies (data plane) and a Meta-Agent (control plane). Combines
  consumer-conditioned Cross-Agent Reflection with threshold-gated Role-Based
  Failover to heal from agent crashes, corrupted prompts, noisy tools, and
  adversarial outputs without global re-orchestration. Derived from MA-Mesh
  (arXiv:2611.06389).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Service-Mesh Agent Self-Healing

> **Source**: [arXiv:2611.06389](https://arxiv.org/abs/2611.06389) — *MA-Mesh: Resilient Multi-Agent Collaboration via Role-based Self-Healing* (`src:2611-06389v1`)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Use this skill when designing or hardening multi-agent systems (sequential chains, parallel-and-merge fan-outs, iterative refinement loops, multi-agent debates, or static role frameworks such as `MetaGPT` and `RTADev`) that must remain reliable under runtime faults:

1. **Mixed structural and semantic failures**: Agents may terminate unexpectedly or time out (`Agent Chaos`), suffer corrupted or underspecified role/task instructions (`Prompt Chaos`), emit malformed or hallucinated artifacts (`I/O Chaos`), encounter failing/noisy external tools, or face targeted adversarial prompt/output injection.
2. **Static inspector/challenger bottlenecks**: Adding centralized or pairwise inspector agents (`Challenger + Inspector`) inflates prompt token overhead by more than `2x` while still collapsing under compound faults (`0.00%–1.59%` on `Web Dev.` and `GUI Dev.`) because inspectors evaluate outputs in isolation without knowing how downstream consumers will use them, and cannot replace a terminated or persistently broken agent role.
3. **Retrofitting existing multi-agent frameworks without rewriting business logic**: You need to add fault detection, critique, and role replacement transparently around existing worker agents, similar to how a cloud-native service mesh (`Istio` / `Linkerd`) attaches sidecar proxies to microservices.

---

## Architecture Overview: Control Plane and Data Plane

Decouple multi-agent workflow execution from resilience management by separating the system into two planes governed by a shared **Resilience-Aware System Specification**:

- **Control Plane (`Meta-Agent` + `System Specification`)**: Defines the collaboration topology (chain, parallel & merge, refine, debate), role definitions, inter-agent dependency edges, timeout budgets, reflection retry limits, and role-specific acceptance criteria. When a role exhausts its local repair budget or crashes, the `Meta-Agent` provisions a replacement agent with a refined role specification while preserving the surrounding workflow graph.
- **Data Plane (Worker Agents + sidecar `Resilient Proxies`)**: Every worker agent $a_i$ is paired 1-to-1 with a lightweight **Resilient Proxy** $p_i$. All task inputs, upstream artifacts, peer critiques, and outbound responses pass through $p_i$. Worker agents never communicate directly with one another; they interact solely with their local proxy.

---

## Step-by-Step Procedure

### Phase 1: Compile the Resilience-Aware System Specification

Before launching the workflow, have the `Meta-Agent` compile the task into a structured **System Specification** containing four mandatory sections for each role $r_i$:

1. **Role & Interface Contract**: The role's responsibility, expected input artifacts from upstream dependencies $\mathrm{Pred}(r_i)$, and required output schema/deliverables for downstream consumers $\mathrm{Succ}(r_i)$.
2. **Collaboration Pattern**: The local routing primitive governing $r_i$ (`Chain`, `Parallel & Merge`, `Refine`, or `Debate`). Using `Parallel & Merge` for independent sub-roles reduces end-to-end wall-clock latency (`4.53 min` for `MA-Mesh` vs. `8.26 min` for `C+I` and `16.26 min` for `RTADev`, with `23%` of generated structures utilizing parallel fan-out).
3. **Consumer-Conditioned Validation Criteria**: Explicit functional and structural invariants that $r_i$'s output must satisfy *specifically so that each downstream consumer $r_j \in \mathrm{Succ}(r_i)$ can execute its own role without error*.
4. **Self-Healing Thresholds**:
   - Execution timeout budget $\tau_{\mathrm{exec}}$ (to catch silent hangs, infinite tool loops, or pod crashes).
   - Maximum local reflection retries $K_{\mathrm{reflect}}$ before escalating to control-plane failover.

### Phase 2: Intercept Execution via Sidecar Resilient Proxies (Data Plane)

For every active role $r_i$, attach a sidecar `Resilient Proxy` $p_i$ that mediates the worker agent's lifecycle:

1. **Pre-execution input gating**: Proxy $p_i$ collects validated outputs from all upstream proxies $\{p_u \mid r_u \in \mathrm{Pred}(r_i)\}$, assembles the role prompt and task context from the System Specification, and dispatches the invocation to worker agent $a_i$.
2. **Liveness and timeout monitoring**: While $a_i$ executes (including external tool calls), $p_i$ monitors heartbeat/completion within $\tau_{\mathrm{exec}}$. If $a_i$ crashes, raises an unhandled tool exception, or exceeds $\tau_{\mathrm{exec}}$, $p_i$ immediately flags a **Liveness Fault** (`Agent Chaos` detection recall `1.00` across all four benchmarks) and escalates to Phase 4 (`Role-Based Failover`).
3. **Output capture and syntactic sanity check**: When $a_i$ returns candidate output $y_i^{(t)}$, $p_i$ intercepts $y_i^{(t)}$ before releasing it to the workflow and initiates Phase 3 (`Cross-Agent Reflection`).

### Phase 3: Consumer-Conditioned Cross-Agent Reflection

Instead of evaluating $y_i^{(t)}$ with a generic standalone judge, validate it through the proxies of its **dependent downstream consumers** $\mathrm{Succ}(r_i)$:

1. **Request downstream consumer critique**: Proxy $p_i$ forwards candidate output $y_i^{(t)}$ to the proxies $\{p_j \mid r_j \in \mathrm{Succ}(r_i)\}$ (or evaluates against their downstream role specifications if $r_i$ is a terminal node).
2. **Evaluate consumer usability**: Each downstream proxy $p_j$ checks whether $y_i^{(t)}$ contains the exact interfaces, code units, data fields, or reasoning steps required by role $r_j$'s specification, returning a binary verdict (`ACCEPT` / `REJECT`) and actionable diagnostic feedback $f_{i \leftarrow j}^{(t)}$ identifying missing or inconsistent elements.
3. **Iterative local repair**:
   - If all downstream proxies return `ACCEPT`, $p_i$ commits $y_i^{(t)}$ and forwards it to $\mathrm{Succ}(r_i)$.
   - If any downstream proxy returns `REJECT` and the retry counter $t < K_{\mathrm{reflect}}$, $p_i$ aggregates the feedback $\{f_{i \leftarrow j}^{(t)}\}$ and prompts worker $a_i$ to revise its output without involving the `Meta-Agent`.
   - If $t \ge K_{\mathrm{reflect}}$ and the output still fails verification (indicating a corrupted role/task prompt, persistent hallucination, or compromised agent instance), $p_i$ triggers a **Quality Exhaustion Fault** and escalates to Phase 4.

### Phase 4: Threshold-Gated Role-Based Failover (Control Plane)

When proxy $p_i$ escalates either a **Liveness Fault** or a **Quality Exhaustion Fault** to the control plane, heal the failed role locally without restarting or re-orchestrating the entire multi-agent graph:

1. **Diagnose failure trace**: The `Meta-Agent` inspects the failed role specification $r_i$, the upstream inputs, any partial/rejected outputs $\{y_i^{(1)}, \dots, y_i^{(t)}\}$, and the accumulated downstream critique log $\{f_{i \leftarrow j}\}$.
2. **Synthesize a refined role specification $r'_i$**:
   - If $a_i$ failed due to liveness/crash, instantiate a clean replacement worker bound to the original role specification $r_i$ (or a fallback compute pod).
   - If $a_i$ failed due to repeated reflection rejections (e.g., `Prompt Chaos`, `I/O Chaos`, or adversarial injection), rewrite and harden the role prompt $r'_i$ from scratch using the clean System Specification and explicit guardrails derived from the failure trace—discarding the corrupted in-context state of the failed worker.
3. **Hot-swap worker behind proxy $p_i$**: Bind the new worker instance $a'_i$ (with refined specification $r'_i$) behind the existing proxy $p_i$ and resume execution from $p_i$'s cached upstream inputs. Upstream roles $\mathrm{Pred}(r_i)$ do not re-execute, and downstream roles $\mathrm{Succ}(r_i)$ remain unaware of the failover.

### Phase 5: Selective Proxy Model Scaling (Optional Cost-Resilience Knob)

Because the data-plane workers and sidecar `Resilient Proxies` are decoupled, you can upgrade *only* the LLM powering the `Resilient Proxies` while keeping cheap worker models (`gpt-4.1-mini`):

- Upgrading only the proxy model on `GUI Dev.` from `gpt-4.1-mini` (`65.30%` Prompt Chaos / `67.87%` I/O Chaos, `$0.186` per task) to `gemini-3-flash` boosts accuracy to **`69.50%` / `85.81%`** at `$0.370` per task; upgrading the proxy to `gpt-5.4` reaches **`75.27%`** with `1.00` detection recall (`$1.616` per task).

---

## Quantitative Summary

All primary benchmarks use `gpt-4.1-mini-0414` (`temperature = 0.0`, 3 trials) across `GUI Dev.` (21 tasks, 15,880 avg length), `Web Dev.` (20 tasks, 8,793 avg length), `GAIA`, and `GPQA-Diamond`. Chaos settings inject `30%` random termination (`Agent Chaos`), `20%` prompt corruption (`Prompt Chaos`), `20%` output corruption (`I/O Chaos`), or all three simultaneously at `20%` each (`Compound Chaos`).

| Benchmark / Scenario | Strongest Baseline (`C+I`: Challenger + Inspector) | `MA-Mesh` Result | Gain / Key Metric |
|:---|:---|:---|:---|
| **Average across all 4 benchmarks** | Vanilla: `52.14%`<br>All Chaos avg: `23.62%`<br>Compound Chaos avg: `5.41%` | Vanilla: **`58.85%`**<br>All Chaos avg: **`56.13%`**<br>Compound Chaos avg: **`50.33%`** | **`+6.71 pp`** Vanilla<br>**`+32.51 pp`** Chaos avg<br>**`+44.92 pp`** Compound Chaos (`+0.36` avg DR) |
| **`GUI Dev.`** (Vanilla / Agent / Prompt / I/O / Compound) | `68.05%` / `4.46%` / `19.30%` / `47.37%` / `1.59%` (Compound DR `0.30`) | **`75.29%` / `71.05%` / `65.30%` / `67.87%` / `65.66%`** (Compound DR **`0.90`**) | **`+64.07 pp`** under Compound Chaos; `1.00` DR under Agent Chaos |
| **`Web Dev.`** (Vanilla / Agent / Prompt / I/O / Compound) | `45.25%` / `5.72%` / `12.47%` / `14.03%` / `0.00%` (Compound DR `0.25`) | **`59.68%` / `53.98%` / `53.11%` / `54.12%` / `49.76%`** (Compound DR **`0.91`**) | **`+49.76 pp`** under Compound Chaos |
| **`GAIA`** & **`GPQA-Diamond`** (Compound Chaos) | `GAIA`: `3.70%` (DR `0.72`)<br>`GPQA-D`: `16.33%` (DR `0.66`) | `GAIA`: **`24.44%`** (DR **`0.94`**)<br>`GPQA-D`: **`61.45%`** (DR **`0.96`**) | **`+20.74 pp`** on `GAIA`; **`+45.12 pp`** on `GPQA-Diamond` |
| **Adversarial Attacks** (`20%` targeted Role / Task / Output attacks on `GUI Dev.` & `Web Dev.`) | `GUI`: `6.80%` / `8.52%` / `4.44%`<br>`Web`: `15.14%` / `6.11%` / `4.13%` | `GUI`: **`63.95%` / `52.98%` / `52.14%`**<br>`Web`: **`48.00%` / `53.77%` / `44.39%`** | **`+45.02 pp`** average accuracy gain over `C+I` |
| **Noisy Tools on `GAIA`** (`20%` Execution Failure / Noisy Response) | `22.42%` (DR `0.50`) / `23.64%` (DR `0.49`) | **`27.88%`** (DR **`0.99`**) / **`27.27%`** (DR **`0.89`**) | **`+4.55 pp`** average accuracy gain; near-perfect fault detection |
| **Retrofitting Static Frameworks** (`GUI Dev.` across 3 Chaos types) | Native `MetaGPT`: `17.21%` avg<br>Native `RTADev`: `31.80%` avg | `MetaGPT + MA-Mesh`: **`60.95%`** avg<br>`RTADev + MA-Mesh`: **`61.22%`** avg | **`+43.74 pp`** gain on `MetaGPT`<br>**`+29.42 pp`** gain on `RTADev` |
| **Ablation Study** (`Web Dev.` Vanilla / Compound Chaos) | `- Cross-agent Reflection`: `49.89%` / `17.57%` (DR `0.57`)<br>`- Role-based Failover`: `52.50%` / `4.13%` (DR `0.35`)<br>`- Resilient Proxy`: `46.06%` / `0.00%` (DR `0.00`) | Full `MA-Mesh`: **`59.68%` / `49.76%`** (DR **`0.91`**) | Both reflection (`+32.19 pp`) and failover (`+45.63 pp`) are essential under Compound Chaos |
| **Cloud-Native Kubernetes Testbed** (`AIOpsLab` + `Chaos Mesh` at `20%` pod fault rate: Stress / Disk I/O / Network) | `C+I`: `47.98%` / `34.34%` / `43.94%`<br>`LLM-Debate`: `38.89%` / `31.82%` / `37.37%` | **`55.56%` / `60.61%` / `56.06%`** (`1.00` DR across all 3 fault types) | Up to **`+26.27 pp`** over `C+I` under Disk I/O Chaos |
| **API Cost & Latency** (`Web Dev.` per task) | `C+I`: `$0.204` (`$0.155` resilient proxy, `344,844` prompt tokens), `8.26 min`<br>`RTADev`: `$0.180`, `16.26 min` | **`$0.170`** (`$0.114` agent + **`$0.055` resilient proxy**, `125,210` proxy prompt tokens), **`4.53 min`** | Resilience layer costs **`<50%`** of `C+I` (`$0.055` vs. `$0.155`) and runs **`1.8x–3.6x` faster** |

---

## Anti-Patterns to Avoid

1. **Relying on reflection without role failover (or vice versa)**: Removing `Role-based Failover` causes Compound Chaos accuracy on `Web Dev.` to collapse from `49.76%` to `4.13%` because an agent with a corrupted role prompt or dead process cannot self-correct through critique alone; conversely, removing `Cross-agent Reflection` drops accuracy to `17.57%` (DR `0.57`) because subtle semantic corruptions pass undetected to downstream nodes.
2. **Using consumer-agnostic standalone inspectors**: Pairwise `Challenger + Inspector` pipelines spend `$0.155` per task (`344,844` prompt tokens) checking outputs in isolation—nearly `3x` the proxy cost of `MA-Mesh` (`$0.055`, `125,210` prompt tokens)—yet achieve only `0.25–0.30` detection recall under Compound Chaos on software development tasks. Always condition output verification on the concrete specification of the downstream consumer roles $\mathrm{Succ}(r_i)$.
3. **Triggering global re-orchestration on single-agent failure**: Re-planning and restarting the entire multi-agent workflow when a mid-pipeline agent fails wastes all upstream compute and risks cascading instability. Isolate recovery to the failed role behind its `Resilient Proxy` using cached upstream artifacts.
