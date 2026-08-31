---
name: speculative-sandbox-scheduler
description: >
  Patterns for speculative sandbox preallocation and scheduling in LLM agent
  serving runtimes. Derived from SpecBox (arXiv:2607.23933). Covers intent-aware
  prewarming, stochastic prefetching via Markov SDG, semantic result caching,
  and zero-copy shared-memory artifact transport.
source: https://arxiv.org/pdf/2607.23933
---

# Speculative Sandbox Scheduler

Skill for building runtime systems that overlap sandbox environment preparation
with LLM inference, eliminating cold-start latency in multi-tenant, multi-turn
agent serving pipelines.

## Core Problem

Modern LLM agents invoke external tools (code execution, web automation, DB
queries) inside isolated sandbox containers accessed via MCP or similar
protocols. Two deployment extremes both fail at scale:

| Strategy | Problem |
|:---------|:--------|
| **Reserved** (always-on containers) | Memory explodes: 80+ GiB at moderate concurrency; economically unsustainable with thousands of MCP tools |
| **On-demand** (cold-start per call) | Tail latency explodes: 2–20s cold-start per sandbox, compounding across multi-turn sessions |

## Key Insight

The bottleneck is not sandbox initialization time itself — it's the **sequential
reactive execution model**. Vanilla agent runtimes (AgentScope, AutoGen,
LangGraph) wait until the LLM finishes generating the full tool call before
beginning sandbox preparation. This leaves GPU and CPU resources idle in
alternating phases.

The fix: **infer tool intent mid-token-generation** and start sandbox
bootstrapping while the LLM is still producing tokens.

## Latency Model

Each agent step decomposes as:

```
T_step = T_context + T_generation + T_env_prep + T_data_io + T_sandbox_exec
         ├── LLM inference ──┤  ├──── Runtime optimization target ─────┤
```

SpecBox targets the three runtime components without modifying the LLM
inference stack.

## Architecture: Three Synergetic Mechanisms

```
┌─────────────────────────────────────────────────────────────┐
│ C1: Intent-Aware Sandbox Prewarming (within current step)   │
│                                                             │
│   Token Stream ──→ Keyword Router (fast, may false-positive)│
│                ──→ Semantic Router (precise, slower)         │
│                                                             │
│   Union Assembly: S_trigger = S_key ∪ S_semantic            │
│   First credible signal → start sandbox immediately         │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ C2: Stochastic Sandbox Prefetching (across steps)           │
│                                                             │
│   Sandbox Dependency Graph (SDG):                           │
│   P(S_next = v_j | S_curr = v_i) = (C_ij + α) / Σ(C_ik + α)│
│                                                             │
│   Filter: L_j ≥ λ (cold-start cost threshold)              │
│   Filter: P_ij ≥ τ (confidence threshold)                  │
│   Select: top-B candidates under budget constraint          │
│                                                             │
│   Prewarm during current sandbox execution                  │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ C3: Reuse-Aware Data Transmission                           │
│                                                             │
│   Semantic Cache:                                           │
│   hit(x) = ∃i s.t. tool(x)=tool(x_i) ∧ sim(φ(x),φ(x_i))≥τ_c│
│   Cache hit → skip sandbox init AND execution entirely      │
│                                                             │
│   Out-of-Band Transport:                                    │
│   Control plane: tool directives, errors, 64-bit token_id   │
│   Data plane: shared-memory mmap, zero-copy artifact reads  │
└─────────────────────────────────────────────────────────────┘
```

## C1: Intent-Aware Sandbox Prewarming

### Dual-Router Design

**Keyword Router**: scans the streaming token output against tool-specific
keyword profiles. Can emit a candidate within microseconds of a distinctive
token. Operates with a threshold γ on the number of matched keywords.

- Strength: extremely fast, enables early overlap
- Weakness: common terms like `search`, `read`, `get` cause false positives
- Tuned parameter: **γ = 2** (require 2+ matching keywords before triggering)

**Semantic Router**: compares the accumulated context (prompt + plan + partial
generation) against tool-intent embeddings using sparse retrieval.

- Strength: captures implicit intent even when no single keyword matches
- Weakness: needs a longer prefix before producing a reliable signal
- Tradeoff: by the time it decides, the cold-start window may be partially lost

### Union Assembly

Rather than requiring both routers to agree (intersection — which delays to the
slower router), SpecBox uses union:

```
S_trigger = S_keyword ∪ S_semantic
```

Each router independently manages its own false-positive rate. The first
credible signal from either starts preparation. This maximizes the overlap
window while maintaining precision through complementary coverage.

## C2: Stochastic Sandbox Prefetching

Within a single step, prewarming can only use the remaining decoding window. For
heavyweight sandboxes (10–20s cold-start), this isn't enough. SpecBox extends
the prewarming horizon across steps.

### Sandbox Dependency Graph (SDG)

A directed graph where nodes are sandbox types and edges are observed transitions
with counts. After each completed invocation, the graph updates:

```
C_ij ← C_ij + 1   when   S(n) = v_i, S(n+1) = v_j
```

### First-Order Markov Model with Laplace Smoothing

```
P(S(n+1) = v_j | S(n) = v_i) = (C_ij + α) / Σ_k(C_ik + α)
```

where α = 1 prevents zero-probability for unseen transitions.

### Budgeted Prefetch Selection

Given current state v_i:

1. **Cost filter**: only consider sandboxes with non-trivial cold-start:
   `K_i = { v_j ∈ V \ {v_i} | L_j ≥ λ }`

2. **Confidence filter**: retain high-probability successors:
   `C_i = { v_j ∈ K_i | P_ij ≥ τ }`

3. **Budget cap**: select top-B sandboxes by probability:
   `A_i = top-B(C_i, P_ij)`

Tuned parameters: **λ = 5s**, **τ = 0.6**, **B = 1** (prewarm at most 1
next-step sandbox)

### Online Adaptation

The SDG updates asynchronously in a background prefetch worker after each
completed sandbox invocation. The predictor continuously adapts to evolving
multi-turn workflows without blocking foreground agent execution.

## C3: Reuse-Aware Data Transmission

### Semantic Result Cache

Multi-turn agents frequently re-access unchanged documents, submit semantically
equivalent queries with different wording, or re-run deterministic computations.

Cache lookup:
```
hit(x) = ∃i s.t. tool(x) = tool(x_i) ∧ sim(φ(x), φ(x_i)) ≥ τ_c
```

- `tool(x) = tool(x_i)`: tool identity must match exactly
- `φ(·)`: normalizes invocation arguments (removes superficial variations)
- `sim(·,·)`: semantic similarity measure
- **τ_c = 0.8**: conservative threshold — only reuse when highly similar

On a cache hit, **both** `T_env_prep` and `T_sandbox_exec` are eliminated.
On a miss, the result is computed and appended to the cache.

### Out-of-Band Shared-Memory Transport

Standard MCP/RPC transports serialize large artifacts (files, images, dataframes)
into request–response messages. This makes `T_data_io` proportional to payload
size.

SpecBox decouples the planes:

| Plane | Carries | Transport |
|:------|:--------|:----------|
| **Control** (in-band) | Tool directives, completions, errors, compact metadata, 64-bit `token_id` references | Standard MCP/RPC |
| **Data** (out-of-band) | Large artifacts (logs, files, images, structured outputs) | Host-managed mmap'd shared-memory region, zero-copy reads |

The sandbox writes large results into a shared-memory region and returns only a
`token_id`. The agent engine reads the artifact directly from shared memory.
Transmission latency becomes effectively insensitive to payload size.

## Quantitative Results

| Metric | On-demand Baseline | SpecBox | Improvement |
|:-------|:-------------------|:--------|:------------|
| P99 E2E latency (QPS=20) | 257.2s | 88.7s | **2.9×** reduction |
| Cumulative provisioning latency | — | — | **4.53×** reduction |
| Peak memory (vs Reserved) | — | 49.4 GiB vs 80.6 GiB | **45.9%** reduction |
| Peak CPU (high QPS) | 15.8 cores | 12.2 cores | **22.8%** reduction |
| Gap vs Reserved (latency) | — | — | Within **10.6%** |

Evaluated on 200 multi-turn trajectories, 32 MCP-compatible tool servers
(Playwright, Jupyter, Neo4j, etc.), 5–8 steps per session average.

## Implementation Notes

- Built on AgentScope framework but is framework-agnostic
- Sandboxes are Docker containers
- Control plane subscribes to the LLM token stream
- Background prefetch worker runs outside the LLM generation critical path
- Predictive preparation does not execute side-effecting work — unused warmups
  are discarded
- Cache reuse limited to deterministic, compatible tool requests
- Shared-memory bridge operates within one trusted host boundary

## When to Use This Skill

- Building or optimizing an LLM agent serving runtime
- Reducing cold-start latency in MCP server deployments
- Designing multi-tenant agent infrastructure with container isolation
- Implementing speculative execution for tool-calling agents
- Adding semantic caching to agent tool invocation pipelines
- Optimizing data transfer between agent engines and tool sandboxes

## Design Patterns to Extract

1. **Dual-router intent detection**: combine fast keyword matching with slower
   semantic matching via union assembly for early-as-possible signal
2. **Markov-based prefetching**: model tool transitions as a first-order Markov
   chain; budget-constrained top-B selection prevents resource waste
3. **Semantic deduplication**: cache deterministic tool results with tool-identity
   + similarity-threshold guard to safely skip redundant execution
4. **Control/data plane separation**: keep RPC-compatible control messages small;
   move bulk artifacts to shared-memory for zero-copy access

## References

- **Paper**: [SpecBox: Speculative Sandbox Scheduling for Efficient LLM Agent Serving](https://arxiv.org/abs/2607.23933) — Zhang et al. (Beihang University, University of Leeds, University of Sydney)
- **Praxis source**: `src:specbox-speculative-sandbox-scheduling-for-efficient-llm-agent-serving`
