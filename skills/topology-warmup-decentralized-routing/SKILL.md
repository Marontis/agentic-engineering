---
name: topology-warmup-decentralized-routing
description: >
  Two-stage topology-aware multi-hop capability warmup and contextual
  experience-adaptive LLM neighbor routing (GraphHarness) for large-scale
  decentralized multi-agent collaboration where global tool registries
  overflow context or privacy boundaries forbid centralizing keyed tools.
  Derived from "DecArena: Evaluating Large-Scale Decentralized Multi-Agent
  Collaboration" (arXiv:2611.15521).
source: https://arxiv.org/abs/2611.15521
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Topology-Warmup Decentralized Routing (`GraphHarness`)

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when designing multi-agent collaboration across **decentralized, graph-constrained peer networks** (`N = 10` to `1,000+` agents, `10K–100K+` specialized tools, federated cross-organization A2A meshes, or privacy-isolated service domains) where **no central orchestrator or global tool directory can be materialized**—either because the global tool catalog overflows model context (`Out of Context` at `100K+` tools) or because tools bind private owner credentials (`HMAC`/API keys) that cannot leave their host agent.

> **When NOT to Use**: If all agents and tools belong to one trust domain and the active tool/agent directory fits cleanly in an orchestrator or typed bus registry (`N <= 50`, centralized visibility permitted), prefer simpler centralized/hierarchical orchestration or small parallel flat teams per [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md). Decentralized multi-hop routing pays message-hop overhead and introduces hub/routing-conflict attack surfaces that are only justified by hard context-scale or privacy-isolation boundaries.

## Core Insight: Why Reactive Forwarding, Tabular Q-Routing, and Standalone RL Fail

In a graph-constrained Dec-POMDP (`DecArena`, `arXiv:2611.15521`), each agent $A_i$ observes only its private toolset $\mathcal{T}_i$, its 1-hop neighbor list $\mathcal{N}_i$, and local message history $h_{i,t}$. Across `QWen3.8 27B` and 5 additional open-weight backbones (`Qwen3.5-0.8B` up to `Qwen3.5 35B A3B`, `Muse Glimmer 30B`, `Gemma 4 26B A4B`, `Gemma 12B`):

1. **Myopic 1-hop forwarding (`Reflex`, `5.2%` Success) & flooding (`Broadcast`, `40.6%` Success / `45.7%` Efficiency)** fail in complementary ways: memoryless 1-hop forwarding wanders in cycles, while flooding every request to all neighbors ($F_{i,t} = \mathcal{N}_i$) explodes message cost as graph size $N$ scales.
2. **Tabular `Numeric Q-Routing` (`5.0%` Success) & `Success-Trajectory Memory` (`1.1%` Success) fail to generalize across large tool catalogs**: When test tasks require unseen tools from a `100K+` catalog (`M = 372` active tools, `186` distinct required tools across `140` multi-hop evaluation tasks; *note: §1 line 145 states `160` tasks while §3.2 and Appendix A.2 specify `140` evaluation tasks: `60` level-1, `40` level-2, `40` level-3*), per-tool scalar $Q(t, j)$ entries stay zero on unvisited tool IDs and raw episodic trajectories inject misleading path priors.
3. **Standalone weight post-training (`SFT` `0.8%`, `GRPO` `0.5%`, `OPSD` `5.7%` on `Qwen3.5-4B`) fails to transfer across unseen graph topologies and scales**: Policies fine-tuned on small random/scale-free graphs ($N \in \{10, 50\}$) collapse when deployed on held-out tasks, larger graphs ($N \in \{100, 500, 1000\}$), or unseen semantic topologies. By contrast, equipping an **unmodified `Qwen3.5-0.8B`** model with the two-stage **`GraphHarness`** (`Warmup 2 Hop + LLM Q-Learning`) lifts Success from **`1.5%` (`Reflex`) / `0.2%` (`GRPO`) to `35.1%`**, and lifts `QWen3.8 27B` from **`5.2%` to `53.7%` Success** (`+48.5` pp), **`58.1%` Collaboration** (`+30.6` pp; *§5.4 prose prints `57.1` while Tables 1, 2, 3, and 6 report `58.1`*), and **`71.5%` Efficiency** (`+34.0` pp).

---

## Procedure

### Step 1: Separate Remote Execution (`result`) from Portable Artifact Transfer (`content`)

Before routing across owner boundaries, enforce strict execution-mode typing on every capability in $\mathcal{T}_i$:
- **`result`-mode (Private / Keyed Capabilities)**: Tools bound to owner-private secrets, HMAC keys, proprietary databases, or privileged sandboxes **never serialize code or credentials across edges**. Peers send typed execution requests `(subquery k, input args)` along graph edges; the owning agent executes the tool locally, verifies output constraints, and returns only the bounded output artifact along the reverse path.
- **`content`-mode (Portable Public Schemas/Specs)**: Only pure, credential-free specifications or intermediate task data may traverse peers directly.

### Step 2: Run Bounded Multi-Hop Local Topology Warmup ($L = 2$ Hops)

Before serving live user tasks (and after major topology/membership changes), execute $L$ synchronous rounds ($L = 2$ hops is the empirically validated sweet spot in `DecArena` Table 6) of **neighbor-only capability summary propagation**:

1. **Round $0$ Initialization**: Each agent $A_i$ summarizes its own local tool domains and capability tags into a compact semantic descriptor $W_i^{(0)}$ (abstracting `10s–100s` of local tools into domain/subdomain capability clusters, e.g., hierarchical topic categories rather than raw source code or private keys).
2. **Rounds $\ell = 0, \dots, L-1$ Exchange**: Each agent exchanges current summaries **strictly with direct neighbors $A_j \in \mathcal{N}_i$** and aggregates directional reachability priors:
   $$W_i^{(\ell+1)} = \Phi\!\left(W_i^{(\ell)},\; \operatorname{AGG}\!\left\{\Psi(W_i^{(\ell)}, W_j^{(\ell)}) : A_j \in \mathcal{N}_i\right\}\right)$$
   where $\Psi$ tags *which direct neighbor $A_j$* advertises or reaches a given semantic capability cluster at hop distance $\ell + 1$, and $\Phi / \operatorname{AGG}$ deduplicate redundant capability tags so $W_i = W_i^{(L)}$ stays bounded in token length regardless of network size $N$.
3. **Optional Disjoint Auxiliary Probes**: Where advertised metadata is coarse, run a small set of synthetic warmup queries disjoint from held-out evaluation tasks to verify end-to-end neighbor responsiveness before freezing $W_i$ for deployment. *(Implementation note: `arXiv:2611.15521` defines $\Phi, \Psi, \operatorname{AGG}$ at the operator level; instantiate them with deterministic JSON schema merging or structured LLM summarization capped per neighbor.)*

### Step 3: Maintain Two Orthogonal Runtime Memory Tiers (`Within-Task` vs. `Cross-Task`)

Never mix ephemeral multi-hop traversal state with persistent cross-task routing beliefs. Maintain two separate stores per agent $A_i$:

| Memory Tier | Scope & Lifetime | Exact Contents | Purpose |
|:------------|:-----------------|:---------------|:--------|
| **1. Within-Task Cache (`h_{i,t}`)** | Single task episode (cleared on task completion) | Visited `(subquery_id, neighbor_id)` pairs, hop budget remaining, discovered tool owner locations for the active DAG, and cached intermediate stage outputs | Prevents ping-pong routing loops (`RepeatRate`), enforces DAG stage dependencies (`level-2`/`level-3` sequential & parallel compositions), and avoids re-querying already-resolved sub-results |
| **2. Contextual Routing Memory (`M_{i,t}`)** | Cross-task local store (bounded LRU / summarized domain table) | Natural-language / structured semantic routing entries linking **capability domain & failure/success outcomes** to specific neighbors $A_j \in \mathcal{N}_i$ | Enables zero-shot semantic generalization: learning that neighbor $A_j$ resolved a *vascular pharmacology* tool lets $f_{\text{LLM}}$ route a novel *cardiology* tool request toward $A_j$ even when the exact tool ID was never seen |

### Step 4: Score Candidate Neighbors Contextually & Update Experience Selectively

When agent $A_i$ receives subquery $k$ at step $t$:
1. **Local Execution Check**: If the required capability is in $\mathcal{T}_i$ (and predecessor DAG stage outputs are satisfied), execute locally and return the verified result toward the requester.
2. **Contextual Neighbor Scoring**: Otherwise, score unvisited candidate neighbors $A_j \in \mathcal{N}_i \setminus \text{Visited}(k)$ by conditioning the routing LLM jointly on the frozen 2-hop warmup map $W_i$, cross-task semantic routing memory $M_{i,t}$, and within-task trace $h_{i,t}$:
   $$s_i(k, A_j, t) = f_{\text{LLM}}(k, A_j, W_i, M_{i,t}, h_{i,t})$$
   Forward to the top-scoring neighbor (or a bounded top-$b$ fan-out, never unconstrained `Broadcast`), attaching a monotonic hop-TTL counter.
3. **Post-Episode Experience Update & Acceptance Gating**: When downstream feedback $(r_i, o_{i,t+1})$ returns (tool found + valid output vs. dead-end / timeout / invalid HMAC receipt):
   $$M_{i,t+1} = \operatorname{Update}_{\text{LLM}}(M_{i,t}, k, A_j, r_i, o_{i,t+1})$$
   - Record **semantic capability-level routing lessons** (e.g., *"Neighbor $A_4$ reaches clinical trial & pharmacology tools within 2 hops; Neighbor $A_2$ dead-ended on genomics"*), **never raw successful trajectories** (`Success-Trajectory Memory` drops `QWen3.8 27B` Success to `1.1%`).
   - **Mandatory Self-Modification Gate**: Whenever persisting updated routing memories $M_{i,t+1}$ or refreshed warmup states $W_i$ across production epochs, **defer to `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md)**—evaluating the updated routing state on a frozen canary suite (with noise margin $\delta$ and strict security checks) so poisoned or drifted routing updates can be rolled back atomically.

### Step 5: Harden Against Hub Misrouting, Conflicting Hints, and Topology Churn

`DecArena` (`§5.4`, Tables 2–3 & Appendix C.4) exposes two severe structural fragilities in decentralized LLM routing that **must** be mitigated in production meshes:

1. **Byzantine / Adversarial Misrouting Collapses Success (`53.7% -> 3.2%`)**: Introducing just $k = 1, 2, 3$ adversarial agents that intentionally forward queries to the *least*-promising neighbor drops `GraphHarness` Success on `QWen3.8 27B` from **`53.7%` -> `22.5%` ($k=1$) -> `13.5%` ($k=2$) -> `3.2%` ($k=3$)** (`Collaboration`: `58.1% -> 40.9% -> 33.4% -> 25.7%`; `Efficiency`: `71.5% -> 53.7% -> 46.8% -> 33.8%`), with scale-free hubs (degrees up to `95` at $N=1000$) acting as single points of routing failure.
   - **Mitigation**: Authenticate inter-agent envelopes per [`multi-hop-delegation-auth-propagation`](../multi-hop-delegation-auth-propagation/SKILL.md), track per-neighbor empirical delivery success rates to quarantine neighbors whose forwarded queries repeatedly time out or fail deterministic output verification, and replicate bridge edges across scale-free hubs so alternate disjoint paths exist.
2. **Conflicting Local Routing Hints Halve Success (`53.7% -> 27.2%`)**: In ring topologies where two local information sources give opposite directional advice (one along the shortest path, one opposite), `GraphHarness` Success drops from **`53.7%` to `27.2%`** (`Collaboration` `58.1% -> 35.1%`, `Efficiency` `71.5% -> 30.8%`).
   - **Mitigation**: Stamp warmup and routing entries with **hop-distance counts, epoch timestamps, and verified execution receipts** (preferring empirically verified tool-execution receipts over unverified peer claims, and triggering bounded 2-direction parallel probe splits when hop-cost estimates tie or conflict).
3. **Dynamic Edge & Tool-Ownership Churn**: Under edge additions/removals or tool migration across owners, attach a staleness TTL to $M_{i,t}$ entries and re-run lightweight 2-hop delta warmup on affected neighborhoods whenever consecutive routing misses occur.

---

## Ablation & Baseline Reference (`DecArena`, `arXiv:2611.15521`)

| Method (`QWen3.8 27B`, Table 1) | Success (%) ↑ | Collaboration (%) ↑ | Efficiency (%) ↑ | Key Diagnostic |
|:--------------------------------|:-------------:|:-------------------:|:----------------:|:---------------|
| `Global Registry` (centralized) | `Out of Context` | `Out of Context` | `Out of Context` | `100K+` tool schemas exceed context window |
| `Reflex` (1-hop memoryless) | `5.2` | `27.5` | `37.5` | Blind local forwarding loops |
| `Broadcast` (flood all $\mathcal{N}_i$) | `40.6` | `68.7` | `45.7` | High recall via flooding; message explosion at scale |
| `Numeric Q-Routing` (tabular) | `5.0` | `22.0` | `80.1` | Zero generalization to unseen tool IDs |
| `Success-Trajectory Memory` | `1.1` | `22.3` | `62.5` | Raw past paths mislead new task routing |
| `Warmup` only (Stage 1 alone) | `33.8` | `37.2` | `58.2` | Strong structural prior (`+28.6` pp over `Reflex`), static at runtime |
| `LLM Q-Learning` only (Stage 2 alone) | `20.6` | `37.7` | `56.8` | Cold-start exploration tax without topology warmup |
| **`GraphHarness` (Warmup + LLM Q-Learning)** | **`53.7`** | **`58.1`** | **`71.5`** | **Synergistic `+19.9` pp over Warmup alone, `+33.1` pp over LLM Q-Learning alone** |

*(Data-integrity note on `arXiv:2611.15521`: In Appendix Table 6, the exact rows `(5.0, 22.0, 80.1)`, `(1.1, 22.3, 62.5)`, and `(3.6, 36.1, 56.8)` appear under `Gemma 12B` and `(20.6, 37.7, 56.8)` appears under `Muse Glimmer 30B`, whereas main-text Table 1 summarizes them under `QWen3.8 27B`. On consistent per-model rows in Table 6, `Warmup 2 Hop + LLM Q-Learning` achieves the top decentralized non-flooding Success on every evaluated model: `53.7%` on `QWen3.8 27B`, `45.4%` on `Qwen3.5 35B A3B`, `38.9%` on `Muse Glimmer 30B`, `35.1%` on `Qwen3.5-0.8B` [vs `0.2%` `GRPO` / `3.3%` `OPSD`], `30.6%` on `Gemma 4 26B A4B`, and `28.1%` on `Gemma 12B`.)*

## Cross-References

- [`multi-hop-delegation-auth-propagation`](../multi-hop-delegation-auth-propagation/SKILL.md) — Cryptographic origin signatures and monotonic scope attenuation across multi-hop A2A delegations
- [`parallel-small-team-tts-scaling`](../parallel-small-team-tts-scaling/SKILL.md) — Preferred alternative when full tool visibility IS available and test-time compute scales via parallel flat peer teams ($M=10$)
- [`recursive-improvement.md`](../../rules/recursive-improvement.md) — Mandatory `"DO: Pass every self-modification through one acceptance gate"` governing persistent cross-task routing memory updates
- [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md) — Topology selection rules separating centralized/bus coordination from privacy- and scale-constrained decentralized graphs

## Sources

- [DecArena: Evaluating Large-Scale Decentralized Multi-Agent Collaboration](https://arxiv.org/abs/2611.15521) (`arXiv:2611.15521`, `src:2611-15521v1`)
