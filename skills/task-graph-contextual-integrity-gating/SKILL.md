---
name: task-graph-contextual-integrity-gating
description: >-
  Prevent multi-hop privacy leakage and compositional mosaic disclosure in
  multi-agent workflows using Task-Graph Contextual Integrity (TG-CI),
  maximal admissible propagation subtrees (Auto-Region), and zero-LLM semantic
  frontier gates. Derived from Wu et al. (arXiv:2610.39532).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Task-Graph Contextual Integrity (TG-CI) Gating

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when orchestrating multi-agent workflows (`Chain`, `Tree`, `Branching` DAGs) where agents retrieve records from a shared or private persistent memory store (e.g., `Mem0`, vector DBs) and pass synthesized messages downstream. Traditional Contextual Integrity (`Local-History CI`) checks only whether the *requesting* agent is allowed to see a record — ignoring that the record will propagate along downstream task-graph edges to unauthorized terminal recipients or colluding peers, or combine with earlier facts to violate compositional privacy rules.

---

## When to Use

- Multi-agent pipelines operating over sensitive domains (`Healthcare`, `Finance`, `Corporate HR`, `Personal/Lifestyle` assistants) with shared or per-agent memory stores.
- Workflows where an upstream planner/analyst needs a sensitive attribute to make a local decision, but downstream customer-facing or external agents must not receive the raw attribute.
- Policies that include **compositional (mosaic) constraints** where disclosing `fact_A` and `fact_B` to the same recipient is forbidden even when each fact is individually benign.

---

## Core Concepts

1. **Multi-Agent Task Graph (`MATG`)**: Directed acyclic workflow graph $G = (V, E)$ where vertices $V$ are role-specialized agents and edges $(u, v) \in E$ are planned communication channels. $\text{Reach}(u)$ is the set of all downstream nodes reachable from $u$ (including $u$).
2. **Conservative Disclosure Footprint ($\overline{D}_t(v)$)**: An upper-bound set of memory item IDs that agent $v$ may have learned up to time $t$, updated whenever a memory release or message path reaches $v$.
3. **Admissible Propagation Region ($P_i^\star$)**: The maximal connected subtree rooted at requesting agent $u$ within which memory item $m_i$ can circulate without violating any node's individual or compositional privacy policy.
4. **Frontier Gate ($\partial P_i^\star$)**: A lightweight, non-LLM semantic filter placed on every outgoing edge $(x, y) \in E$ where $x \in P_i^\star$ and $y \notin P_i^\star$.

---

## Step-by-Step Procedure

### Step 1: Compile the Workflow into an Explicit `MATG` and Initialize Footprints

Before task execution begins:
1. Extract the directed communication graph $G = (V, E)$ from the orchestrator plan, associating each node $v \in V$ with its role specification, clearance scope, and subtask description.
2. Precompute reachability sets $\text{Reach}(u)$ for every agent $u \in V$.
3. Initialize the conservative disclosure footprint $\overline{D}_0(v) = \emptyset$ for every $v \in V$.

### Step 2: Authorize Memory Retrieval Over Downstream Propagation Regions (`Auto-Region`)

When agent $u$ queries persistent memory and retrieves candidate items $\{m_1, \dots, m_k\}$ at step $t$:

1. **Evaluate Node-Level Admissibility across $\text{Reach}(u)$**:
   For each candidate item $m_i$ and each reachable node $v \in \text{Reach}(u)$, check two conditions in a single batched CI policy evaluation:
   - *Role & Subtask Necessity*: Does $v$'s subtask and role clearance permit receiving $m_i$?
   - *Compositional Mosaic Safety*: Would adding $m_i$ to $v$'s current footprint $\overline{D}_t(v) \cup \{m_i\}$ trigger any forbidden fact-pair/mosaic combination $\mathcal{F}_{\text{mosaic}}$?
2. **Compute the Maximal Admissible Subtree ($P_i^\star$, `Auto-Region`)**:
   - If $m_i$ is inadmissible at the requesting node $u$ itself, **block $m_i$ at retrieval** ($P_i^\star = \emptyset$).
   - Otherwise, define $P_i^\star \subseteq \text{Reach}(u)$ as the maximal connected subgraph rooted at $u$ containing only nodes $v$ for which $m_i$ passed both checks.
   - *Why `Auto-Region` over `Full-Scope`*: `Full-Scope` blocks $m_i$ at $u$ whenever *any* downstream node in $\text{Reach}(u)$ is unauthorized (`P_i^\star == Reach(u)` required). `Auto-Region` releases $m_i$ to $u$ so $u$ can complete its local reasoning, and bounds propagation at the boundary $\partial P_i^\star$.
3. **Update Conservative Footprints**:
   For every $v \in P_i^\star$, update $\overline{D}_{t+1}(v) \leftarrow \overline{D}_t(v) \cup \{m_i\}$.

### Step 3: Install Zero-LLM Semantic Frontier Gates on $\partial P_i^\star$

Identify the **cut edges** leaving the admissible region:
$$\partial P_i^\star = \{ (x, y) \in E \mid x \in P_i^\star \;\land\; y \notin P_i^\star \}$$

- **Inside $P_i^\star$ ($x \in P_i^\star, y \in P_i^\star$)**: Allow messages to pass directly with **zero inspection overhead**.
- **Across $\partial P_i^\star$ ($x \in P_i^\star, y \notin P_i^\star$)**: Attach a local restriction watch for item $m_i$ on edge $(x, y)$.

When agent $x$ emits an outbound message $M_{x \to y}$ across a watched frontier edge $(x, y) \in \partial P_i^\star$, run a 3-stage local semantic gate against every restricted item $m_i$ watched on $(x, y)$:

1. **Stage 1 — Lexical & Entity Value Overlap**: For each message span, check for exact or normalized lexical entity and value overlap against `restricted_item`. If present, block the span immediately (`True`).
2. **Stage 2 — Dense Embedding Recall Filter**: Compute dense embedding cosine similarity (e.g., `all-MiniLM-L6-v2`) between the span and `restricted_item`. If similarity is below `0.35`, pass the span; if `>= 0.35`, advance to Stage 3.
3. **Stage 3 — Bidirectional NLI Entailment Check**: Compute bidirectional Natural Language Inference entailment probabilities (e.g., `nli-deberta-v3-base`) in both directions (`span -> restricted_item` and `restricted_item -> span`). If the maximum entailment probability is `>= 0.70`, block the span (`True`); otherwise allow (`False`).

### Step 4: Redact or Rewrite Blocked Frontier Spans Without Leaking Footprints

If `frontier_gate_blocks(M_{x->y}, m_i)` returns `True`:
1. Strip or replace the offending span in $M_{x \to y}$ with a task-safe abstract summary before delivering the message to $y$.
2. Because $m_i$ was blocked at $\partial P_i^\star$, **do not** add $m_i$ to $\overline{D}(y)$ or any node downstream of $y$ — preserving their ability to receive other mosaic-paired facts safely.
3. If an unexpected off-graph edge $(x, z) \notin E$ is requested dynamically at runtime, treat it as an unverified frontier edge and run the Step 2 CI check before delivery.

---

## Quantitative Reference (`MAPLE-Bench`, `arXiv:2610.39532`)

Evaluated across `144` multi-agent cases (`4` domains $\times$ `3` topologies, `720` task MCQs, `288` compositional fact-pair rules, single and colluding compromised agents):

| Metric (`Haiku–Luna` Primary Pairing) | `No Protection` | `Local-History CI` | `Online Atomic CI` | `TG-CI (Auto-Region)` | `TG-CI (Full-Scope)` |
|:--------------------------------------|:---------------:|:------------------:|:------------------:|:---------------------:|:--------------------:|
| **Unauthorized Disclosures / Case** | `15.84` | `10.47` | `6.11` | **`1.49` (`-85.8%`)** | **`0.62` (`-94.1%`)** |
| **Compromised-Agent Exposures / Case** | `2.90` | `1.58` | `0.99` | **`0.35` (`-77.8%`)** | **`0.16` (`-89.9%`)** |
| **Task Utility (`Haiku–Luna` MCQ %)** | `80.97%` | `83.26%` | `80.69%` | **`80.00%`** | `77.92%` |
| **Task Utility (`Haiku–Haiku` MCQ %)** | `81.04%` | `78.06%` | `74.04%` | **`68.40%`** | `62.22%` |
| **Task Utility (`Luna–Luna` MCQ %)** | `94.72%` | `96.11%` | `88.47%` | **`92.22%`** | `88.06%` |
| **Judge Token Spend (`Haiku–Luna`)** | `0` | — | — | **`133.1K`** | `144.5K` |
