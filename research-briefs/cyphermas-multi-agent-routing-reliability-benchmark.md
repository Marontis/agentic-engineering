<!-- License: CC BY 4.0 | Repository: https://github.com/Marontis/agentic-engineering -->

# CypherMAS: Benchmarking Routing Reliability, Graph Diameter & Parallel Tool Batching in Multi-Agent Systems

**Paper**: *CypherMAS: Benchmarking Routing Reliability in LLM-Based Multi-Agent Systems* (`arXiv:2611.33242`)  
**Authors**: Daniil Kostromin, Andrey Sakhovskiy, & Semen Budennyy (Sber AI, RTU MIREA, AIRI)  
**Category**: `cs.AI` / `cs.CL` / `cs.MA` (2026-11-26)  
**Triage**: **Research Brief** (synthetic diagnostic benchmark isolating multi-agent message routing, graph diameter scaling, parallel tool-call batching, and typed-vs-prose protocol trade-offs across `4B–753B` open-weight models)  
**Code / Benchmark**: `https://github.com/Andoree/CypherMAS`

---

## Why Not a Standalone Skill?

`CypherMAS` (`arXiv:2611.33242`) introduces a controlled synthetic benchmark (`N = 3..25` agents, main suite at `N = 25`) where every agent holds a Caesar-ciphered payload (`shift = 7` over `10` alphanumeric characters) whose unique `decrypt_for_agent` tool resides on a remote peer placed at **maximum shortest-path distance** via a Hungarian-algorithm derangement $\pi^*$. By stripping away open-domain knowledge and reasoning confounds, `CypherMAS` cleanly isolates **pure message-routing reliability, loop suppression, and parallel `send_message` tool batching** with exact closed-form optimal message bounds (`Chain = 624`, `Ring = 600`, `Star = 96`, `Bipartite = 100` at $N = 25$). Because the paper contributes a **diagnostic benchmark and empirical scaling/failure laws** rather than a new runtime routing algorithm beyond existing Praxis topology and envelope rules (such as `GraphHarness` in [`topology-warmup-decentralized-routing`](../skills/topology-warmup-decentralized-routing/SKILL.md)), it belongs as a **Research Brief** paired with quantitative routing-readiness criteria in our coordination and evaluation rules.

---

## 1. Benchmark Architecture & Manuscript Verification Notes

At $N = 25$ agents (`2,048`-message global cap, `3` seeds per configuration plus a `10`-seed stability sweep in `Appendix F`), agents see **only their immediate 1-hop neighbors** and must route `25` concurrent request–response round-trips across four undirected topologies:
- **Linear-diameter topologies ($O(N)$ hops)**: `Chain` (`624` minimum `send_message` transmissions) and `Ring` (`600` minimum transmissions, $d_i = \lfloor N/2 \rfloor = 12$ hops).
- **Constant-diameter topologies ($2$ hops)**: `Star` (`96` minimum transmissions; central hub bridges `24` leaves) and balanced `Bipartite` (`100` minimum transmissions).
- **Communication modes**: `Strict Mode` (typed `send_message` payloads) vs. `Free Text Mode` (unconstrained natural-language `content`).

**Verified Internal Manuscript Discrepancies (HTML + PDF cross-checked)**:
1. **`3` vs. `5` `Strict Mode` message types**: `§3.2` and `Appendix C` (`Figure 9`) state that `Strict Mode` restricts `message_type` to `3` actions (`decrypt_request`, `decrypt_response`, `forward`), whereas the full `Strict Mode` system prompt in `Appendix B` (`Figure 8`) explicitly defines **`5` message types** (`route_query`, `route_response`, `decrypt_request`, `decrypt_response`, `forward`).
2. **`Qwen3.8-27B` `Chain` Success Rate & `DeepSeek-V4-Flash` SD**: Under `Strict Mode` on `Chain` ($N = 25$), `Table 1` reports `Qwen3.8-27B` `SR = 0.55 ± 0.08`, whereas the stage-outcome breakdown in `Table 3` (`Completed` column, identical definition) prints **`0.57 ± 0.08`** (`DeepSeek-V4-Flash` SD prints `0.87 ± 0.06` in `Table 1` vs. `0.87 ± 0.07` in `Table 3`).
3. **Apparent sub-optimal `LLM Calls` (`549–581 < 624`) & `2,049–2,074 > 2,048` cap overshoots in `Table 1`**: `Table 1`'s `LLM Calls` column counts **total `send_message` transmissions** (not model forward passes—e.g., `Star` logs `96` `LLM Calls` across `124.0` actual model invocations in `Appendix G` `Table 11`). Mid/large models log `549–581 < 624` transmissions on `Chain` because `SR < 1.0` leaves dropped requests' return hops unexecuted; conversely, looping small models log `2,049–2,074` transmissions because the `2,048` cap is checked only at round boundaries after all concurrent active agents emit their round messages.

---

## 2. Four Core Empirical Findings (`11` Open-Weight Models, `4B–753B`)

### Finding 1: Active Parameter Count (`~27B` Dense Threshold)—Not Total MoE Capacity—Governs Multi-Hop State Tracking
- **Sub-`10B` dense collapse & `>80%` duplicate flooding**: `Qwen3.5-4B` (`SR = 0.00–0.12` `Strict`) and `Qwen3.5-9B` (`SR = 0.00–0.04` `Strict`) fail even on `2`-hop `Star`/`Bipartite`. On `Chain` and `Ring`, `Qwen3.5-4B` emits **`83.08%` (`1,702.3/2,049.0`) and `82.16%` duplicate messages** (`Table 12`), exhausting the `2,048` cap and burning **`77.0M` input tokens** (`117.6M` input tokens for `Qwen3.6-35B-A3B` on `Ring Free Text`, `Table 9`).
- **Sparse-MoE active-parameter cliff (`Qwen3.6-35B-A3B` vs. dense `Qwen3.6-27B`)**: Despite `35B` total parameters, `Qwen3.6-35B-A3B` (**`3B` active parameters**) drops below `0.30` SR by $N = 10$ and collapses at $N = 25$ (`0.07` `Chain`, `0.00` `Ring`, losing `65%` of messages in `Transit to Dec`, `Table 3`), whereas smaller-total dense **`Qwen3.6-27B` (`27B` active)** reaches **`1.00` `Star` / `0.99` `Bipartite` / `0.36` `Chain` / `0.57` `Ring`** (`Strict`). However, at larger active MoE scales (`DeepSeek-V4-Flash` `284B` total / `13B` active: `0.87–1.00` SR; `GLM-5.2` `753B` total / `40B` active: `0.83–1.00` SR), routing reliability recovers fully.

### Finding 2: Parallel Tool-Call Batching Is a Hard Prerequisite for Hub & Mesh Relays (`gpt-oss-20b` / `120b`)
- Both `gpt-oss-20b` (`21B` total / `3.6B` active) and `gpt-oss-120b` (`117B` total / `5.1B` active) score near-zero everywhere (`SR = 0.00–0.09` `Strict`, `0.00–0.04` `Free Text`)—failing *even on `2`-hop `Star` (`0.08` / `0.09`)* where `27B+` peers score `1.00`.
- **Root cause (`Table 3`, `Appendix E` `Table 7`)**: When a `Star` hub receives `24` simultaneous neighbor requests in Round 1, it must emit **multiple parallel `send_message` tool calls in a single turn** (or maintain an uncorrupted multi-turn backlog). `gpt-oss-20b` and `gpt-oss-120b` emit only `1` tool call per turn and immediately drop the rest, leaving **`92.21%` (`gpt-oss-20b`) and `75.28%` (`gpt-oss-120b`)** of messages stranded in `Transit to Dec` on `Star` (`85.71%` and `66.00%` on `Bipartite`) and prematurely halting the simulation—making their raw run cost look deceptively cheap (`$0.005–$0.178`, `Table 10`) solely because `>90%` of work was abandoned!

### Finding 3: Graph Diameter Dominates Both Global Completion Rate (`GCR`) and Inference Cost (`10x–55x`)
- **Per-agent `SR` hides system-wide `GCR` failure (`Table 2`)**: Capable models (`Qwen3.6-27B`, `Qwen3.8-27B`, `Gemma4-31B`, `DeepSeek-V4-Flash`, `GLM-5.2`) achieve **`0.99–1.00` per-agent SR and `1.00` Global Completion Rate (`GCR`, all `25/25` agents resolved)** on `2`-hop `Star` and `Bipartite` (`0.67` `GCR` for `Qwen3.6-27B` `Bipartite`) at the **exact theoretical minimum `96` (`Star`) and `99–120` (`Bipartite`) transmissions**. On linear-diameter `Chain` and `Ring` (`Strict`), **`10 of 11` models score `0.00` `GCR`** (only `GLM-5.2` reaches `0.33` `GCR` on `Chain` and `Ring`!), because per-hop drop/loop probabilities compound exponentially across `12–24` relay hops.
- **Topology outweighs model unit price by an order of magnitude (`Table 10`)**: Running frontier `753B` `GLM-5.2` on `Star` (**`$0.386`**, `SR = 1.00`, `GCR = 1.00`) is **`3x` cheaper** than running `9B` `Qwen3.5-9B` on `Chain` (**`$1.164`**, `SR = 0.04`, `GCR = 0.00`—which itself costs **`55x` more** on `Chain` `$1.164` than on `Star` `$0.021`). Even among reliable models, `Chain`/`Ring` inflate cost **`10x–33x`** over `Star`/`Bipartite` (`GLM-5.2`: `$0.386` `Star` vs. `$12.801` `Chain`; `Gemma4-31B`: `$0.056` `Star` vs. `$1.097` `Chain`).

### Finding 4: `Strict` Typed Schemas vs. `Free Text` Prose Exhibit Opposite Redundancy Failure Modes Across Model Families
Switching from `Strict Mode` to `Free Text Mode` (`Tables 4–5`, `Appendix G` `Tables 11–13`) improves mean `SR` for **`7 of 11` models** on long-diameter graphs (`Qwen3.8-27B` `Chain`: **`0.55 -> 0.96`**, `GCR 0.00 -> 0.33`; `DeepSeek-V4-Flash` `Ring`: **`0.69 -> 0.99`**, `GCR 0.00 -> 0.67`) because agents batch multiple pending requests inside a single prose message or self-recover from rigid enum mistakes. However, **cost and redundancy flip sign depending on post-training**:
- **Conversational over-confirmation in `Free Text` (`Qwen` / `DeepSeek` / `Gemma`)**: `Qwen3.6-27B` doubles `Chain` calls from `549 -> 1,156` (`$2.899 -> $12.668`, `4.4x` cost) and `DeepSeek-V4-Flash` jumps `581 -> 1,139` (`$1.201 -> $3.551`) because agents emit polite `"Thank you / Confirmed received"` acknowledgement loops after task completion.
- **Schema-duplicate Retry Loops in `Strict Mode` (`GLM-5.2`)**: Conversely, `GLM-5.2` **cuts `Chain` calls in half under `Free Text` (`1,248 -> 573`, `$12.801 -> $2.451`, `-80.9%` cost while `SR` rises `0.83 -> 0.95`)**, because in `Strict Mode` **`45.03%` (`562.3/1,248.7`)** of its `Chain` messages (`37.41%` on `Ring`) are exact schema duplicates!

---

## 3. Practical Implications for Multi-Agent Engineering

1. **Keep inter-agent routing diameter `<= 2` hops (`Star`, `Bipartite`, or hierarchical `2`-tier hubs)**: Never chain `N >= 10` LLM peers sequentially when an orchestrator hub, directory lookup, or `2`-hop capability index (`GraphHarness`) is permissible; linear-diameter relays turn `99%` per-hop models into `0%` global-completion systems at `10x–33x` higher cost.
2. **Gate router/hub checkpoints on parallel multi-tool batching and active-parameter floors**: Before assigning a model to a hub or peer-relay role, run a `1`-round fan-in preflight (`>= 10` simultaneous inbound requests) verifying that the checkpoint emits all `10` outbound tool calls without dropping queued items (`catching gpt-oss-20b/120b`'s `75%–92%` single-hop drop) and meets active-parameter floors (`>= 13B–27B` active; avoid `<= 4B`-active dense/MoE routers).
3. **Pair natural-language payloads inside typed envelopes with deterministic deduplication and `NO_ACK` termination**: Combine the routing flexibility of `Free Text` (`0.96–0.99` `Chain`/`Ring` SR) with envelope-level `(request_id, hop_ttl)` deduplication (eliminating `GLM-5.2`'s `45%` `Strict` duplicates) and explicit terminal state flags that suppress conversational `"thank you"` loops (`saving 2x–4.4x` cost on `Qwen`/`DeepSeek`).
4. **Never report raw mean run cost without completion-adjusted cost (`Cost / SR` or `Cost / GCR`)**: Early-deadlocking models (`gpt-oss-20b` at `$0.005` for `SR = 0.00`) dominate raw cost tables purely by abandoning messages on hop 1.

---

## Cross-References

- **Rules**:
  - [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md) — `"DON'T: Default to a fixed multi-agent topology"`, `"DO: Use natural language as the inter-agent interface"`, `"DO: Structure inter-agent communication around typed intents and bus substrates"`, and `"DO: Pair 2-hop local capability warmup with contextual LLM routing memory in privacy- or scale-constrained decentralized graphs, and harden hubs against misrouting"`
  - [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — `"DON'T: Claim coordination gains over greedy decoding without sample-parity and compute-parity baselines and 6D PACE accounting"` and `"DO: Replay frozen plan-task-arrival schedules across serving substrates and report submitted-job Effective Quality alongside survivor-matched intersection P95"`
  - [`skill-system-design.md`](../rules/skill-system-design.md) — `"DO: Decouple agent context into file ledgers to prevent runaway reasoning loops"` (confirming the `Qwen3.6-35B-A3B` `3B`-active MoE cliff)
- **Spec Templates**:
  - [`adk-multi-agent-a2a.spec.md`](../specs/adk-multi-agent-a2a.spec.md) — Multi-agent topology selection, hop budgets, and envelope deduplication
  - [`adk-eval-quality-gate.spec.md`](../specs/adk-eval-quality-gate.spec.md) — Multi-agent `GCR`, parallel tool-call preflights, and completion-normalized cost metrics
- **Related Skills**:
  - [`topology-warmup-decentralized-routing`](../skills/topology-warmup-decentralized-routing/SKILL.md) — `2`-hop capability warmup + loop-suppressing `h_{i,t}` caches when decentralized graphs are mandatory (`DecArena`)
  - [`paired-serving-substrate-mas-benchmarking`](../skills/paired-serving-substrate-mas-benchmarking/SKILL.md) — Separating whole-job `Q_eff` (`GCR` analogue) from survivor-only `Q_eval` (`MASSys`)
  - [`nlip-agent-message-envelope`](../skills/nlip-agent-message-envelope/SKILL.md) — Wrapping flexible natural-language payloads inside typed, deduplicated envelopes
- **Research Briefs**:
  - [`pace-multi-agent-compute-parity-synthesis.md`](pace-multi-agent-compute-parity-synthesis.md) — `6D` compute-cost accounting across multi-agent topologies (`arXiv:2611.17610`)
  - [`mining-multi-agent-workflow-design-space.md`](mining-multi-agent-workflow-design-space.md) — Macro-topology vs. prompt-placeholder routing effects (`arXiv:2610.31709`)
  - [`coordination-tax-heterogeneity-dividend-multi-agent.md`](coordination-tax-heterogeneity-dividend-multi-agent.md) — Closed-form multi-agent coordination-tax break-even bounds (`arXiv:2610.37700`)
  - [`agent-protocol-handshake-overhead-benchmark.md`](agent-protocol-handshake-overhead-benchmark.md) — Per-hop protocol overhead across `MCP`, `A2A`, and `NLIP` (`arXiv:2610.30151`)

## Sources

- Kostromin, D., Sakhovskiy, A., & Budennyy, S. (2026). *CypherMAS: Benchmarking Routing Reliability in LLM-Based Multi-Agent Systems*. `arXiv:2611.33242`. Code: `https://github.com/Andoree/CypherMAS`.
