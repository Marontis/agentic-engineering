# Muffin: A Shared Memory Buffer for Asynchronous AI Agents

> Source: `src:2610-31355` — "Muffin - A Shared Memory Buffer for Asynchronous AI Agents" (arXiv:2610.31355, 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Classification: Research Brief (Contextual Knowledge)

This paper is classified as a **research brief** because its core contribution is an inference-time multi-agent coordination topology (**Muffin**: Memory bUFFer INference) whose actionable design constraints—replacing synchronous all-to-all round barriers and full-trajectory broadcasting with an append-only shared memory buffer of compact intermediate findings—directly reinforce and quantify existing multi-agent coordination rules in `rules/multi-agent-coordination.md` and `rules/agent-working-memory.md`.

---

## Problem & Motivation

Synchronous multi-agent frameworks such as Multi-Agent Debate (MAD) force every agent to wait at global round barriers and broadcast full reasoning traces to all peers at every round. This creates two compounding bottlenecks:
1. **Context bloat and quadratic token growth**: Passing complete chain-of-thought trajectories across $N$ agents over multiple rounds floods each agent's working memory with verbose, partially redundant reasoning.
2. **Synchronization stalls and conformity skew**: Agents cannot progress at their own step cadence, and full-trace exposure in synchronous rounds can overwrite correct minority reasoning or amplify noisy peer rationales.

---

## Architecture: Two-Stage Routing and Asynchronous Shared Memory Buffer

Muffin structures multi-agent inference into three lightweight components without inter-agent round barriers:

1. **Stage 1 — Complexity-Based Orchestrator**:
   - Given a query $x$, an orchestrator decides whether to route the task to `direct` (a single-agent call for straightforward queries) or `multi` (instantiating $N = 3$ agents with specialized roles $r_i$, non-overlapping subtasks $\tau_i$, and a collaboration protocol $\rho$).
2. **Stage 2 — Asynchronous Execution with a Shared Memory Buffer ($B$)**:
   - Each agent $a_i$ runs asynchronously over $T = 5$ local reasoning steps.
   - At step $t$, agent $a_i$ reads only the **$k$ most recent peer findings** $R_k(B, i)$ from an append-only shared buffer $B$ (filtering out its own prior entries).
   - The agent produces three distinct outputs: a compact step summary $m_i^{(t)}$, private scratchpad notes $n_i^{(t)}$ (kept strictly in its local history $h_i^{(t+1)}$ and never shared), and an optional compact shared finding $s_i^{(t)}$ appended to $B$ only when useful to peers.
3. **Final Summarizer**:
   - Once agents finish, a summarizer synthesizes the final answer from only the query $x$, the role assignments $\alpha_i$, and each agent's final step summary $m_i^{(T_i)}$—never reading the raw multi-step trajectories or private notes.

---

## Key Empirical Findings

Muffin was evaluated across **4 models** (`gemma-4-E4B-it`, `gemma-4-31B-it`, `Qwen3.5-4B`, `Qwen3.8-27B`) and **5 benchmarks** (Chess Move Validity [100], GPQA-Diamond [198], MMLU-Pro [100], OlymMATH-Easy [100], and OlymMATH-Hard [100] = 20 model–benchmark settings, averaged over 3 runs) against Single-Agent, Majority Vote, and synchronous Multi-Agent Debate (MAD):

| Evaluation Dimension | Empirical Result |
| :--- | :--- |
| **Overall benchmark wins** | **17 of 20 settings** (and second-best in the remaining 3), beating the strongest baseline by **+4.4 accuracy points on average** across all benchmarks (**+11.8 points** on OlymMATH-Easy, **+2.6 points** on OlymMATH-Hard) |
| **Step-wise quality vs. token cost (OlymMATH-Easy, `gemma-4-E4B-it`, 10 steps)** | Outperforms synchronous Multi-Agent Debate by **+19.2 accuracy points** while consuming **77.4% fewer tokens**; final Summarizer lifts accuracy from **44.9% to 59.2%** |
| **Compact finding sharing vs. full-trace sharing (OlymMATH-Easy, `gemma-4-31B-it`)** | Full-trace sharing reaches 87.3% vs. Muffin's 85.0% (+2.3 pp), but Muffin cuts per-problem token usage from **160.6K to 41.9K tokens (73.9% fewer tokens)** |
| **Agent count scaling ($N \in \{2, 3, 4, 5\}$ on OlymMATH-Easy, `gemma-4-E4B-it`)** | Scaling $N=2 \to N=3$ raises accuracy from **50.6% to 59.3%** (+8.7 pp); $N=4$ (**59.7%**) and $N=5$ (**58.7%**) plateau while token cost scales linearly |
| **Buffer retrieval window $k$ (`gemma-4-E4B-it` vs. `gemma-4-31B-it`)** | Smaller model peaks at **$k = 10$** (+5.0 pp over $k = 5$) and degrades at larger $k$ due to stale/noisy early findings; larger 31B model varies by only 2.0 pp across $k$ |
| **Peer steering dynamics (Chess, `gemma-4-31B-it`)** | **20.5%** of shared findings alter a peer's tentative answer, decaying from **43.2%** at step 1 to **15.8%** at the final step; in early steps, **51.6%** of peer-induced flips convert wrong $\to$ correct vs. **14.2%** correct $\to$ wrong |
| **Summarizer net value (across Gemma-4 runs)** | Summarizer diverges from the last agent output on **11.14%** of examples, flipping **32.05%** from wrong $\to$ correct vs. **21.20%** from correct $\to$ wrong (**+10.85 pp net gain**; 5.24% of queries routed via `direct`) |

---

## Why Not a Skill?

Muffin is a general multi-agent inference topology rather than a multi-step human-invoked diagnostic or verification procedure. Its key operational takeaways—**separating private scratchpad reasoning from compact shared findings**, **capping peer retrieval windows ($k \approx 10$) for smaller models**, **stopping agent scaling at $N = 3$ complementary roles**, and **passing only final agent summaries to the aggregator**—are concise quantitative decision rules that belong in `rules/multi-agent-coordination.md` and `rules/agent-working-memory.md`.

---

## Connections to Praxis

- **Multi-Agent Coordination (`rules/multi-agent-coordination.md`)**: Provides direct quantitative evidence against synchronous all-to-all full-trace debate (+19.2 accuracy points at 77.4% lower token cost; 73.9% token reduction vs. full-trace sharing).
- **Working Memory Management (`rules/agent-working-memory.md`)**: Demonstrates that bounding cross-agent context via a sliding window ($k = 10$) of distilled findings prevents smaller models from degrading on stale intermediate reasoning.
- **Related Skill**: Complements [debate-consensus-memory-calibration](../skills/debate-consensus-memory-calibration/SKILL.md) by showing how asynchronous buffer communication avoids synchronous majority conformity pressure in early reasoning steps.
