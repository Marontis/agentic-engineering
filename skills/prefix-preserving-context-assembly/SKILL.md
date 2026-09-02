---
name: prefix-preserving-context-assembly
description: >
  Database-inspired prompt context assembly and compaction for long-horizon
  agents. Preserves byte-identical KV-cache prefixes, optimizes token costs,
  and avoids ad-hoc history truncation through execution plans and cost models.
  Derived from ContextPipe (arXiv:2609.00749).
source: https://arxiv.org/abs/2609.00749
---

# Prefix-Preserving Context Assembly

Use this skill when designing or configuring runtime context assembly,
prompt templating, or history compaction in long-horizon LLM agents.

## When to Use

- Agents running long trajectories (10+ turns, multi-file codebases, SWE tasks)
- High API latency or costs caused by prompt cache invalidation
- Context windows hitting hard token limits during multi-tool execution
- Replacing ad-hoc string concatenation and regex truncation with a formal
  pipeline

## Core Insight

Modern LLM providers (Anthropic, OpenAI, Google) implement **byte-sensitive
prefix prompt caching**: any single character change early in the prompt
invalidates the entire KV cache downstream.

In unoptimized agent runtimes, dynamic values (timestamps, turn counters,
changing scratchpad notes) inserted near the top of the prompt invalidate
cache hits on every turn. Treating context assembly as a **database query
execution plan**—with static prefix guarantees, cost modeling, and
tiered eviction—preserves cache reuse rates (>90%) while strictly respecting
token budgets.

---

## Procedure

### Step 1: Segment Context into Tiered Prefix Zones

Partition every prompt into four strictly ordered, non-interleaved zones:

```
[ Zone 1: Immutable Static Prefix ]
  ├── System persona & immutable behavioral rules
  ├── Core safety guardrails
  └── (Cache-pinned; never changes across the entire session)

[ Zone 2: Semi-Static Capability Declarations ]
  ├── Tool definitions and JSON schemas (sorted deterministically by name)
  ├── Static skill workflow documentation
  └── (Changes only when tools/skills are dynamically loaded)

[ Zone 3: Long-Horizon Evictable Memory ]
  ├── Compacted milestone summaries
  ├── Retrieved repository map / index summaries
  └── Eviction target: structured FIFO or LRU summaries

[ Zone 4: Dynamic Working Tail ]
  ├── Recent uncompressed dialogue turns (sliding window of N=3..5 turns)
  ├── Current step observation / tool execution output
  └── Active workspace scratchpad / transient thoughts
```

### Step 2: Enforce Byte-Level Prefix Invariance

Eliminate dynamic variables from Zones 1 and 2:
- **Timestamp handling**: Do **not** inject `Current time: 2026-09-02T19:40:00`
  into the system prompt. Inject timestamps into the latest user turn or
  tool response in Zone 4.
- **Deterministic ordering**: Sort tool schemas alphabetically by name rather
  than insertion order to prevent cache churn across restarts.
- **Exact whitespace**: Avoid string template formatting engines that reflow
  indentation or change trailing linebreaks.

### Step 3: Cost-Modeled History Compaction

When total tokens approach `Budget - SafetyMargin` (e.g., 85% of window):

1. **Do not truncate from the beginning**: Truncating Zone 1 or Zone 2
   destroys cache prefixing.
2. **Execute a compaction pass on Zone 3**:
   - Collapse completed subtask turns into a single structured milestone block:
     `{"milestone": "auth_setup", "status": "verified", "touched": ["src/auth.py"]}`.
   - Strip verbose raw stdout from older tool calls while preserving exit codes
     and concise error summaries.
3. **Keep the head of Zone 4 intact**: Retain the last 2 full turn cycles verbatim
   to prevent reasoning degeneration on recent context.

### Step 4: Verify Cache Hit Ratio

Monitor provider metrics for prompt token utilization:
- `cache_read_input_tokens` / `total_input_tokens` should consistently exceed
  80–95% on turns $T \ge 3$.
- If cache hit drops to 0% mid-session, identify which zone broke byte
  invariance.

---

## Environment Caveats

- **Minimum cache block requirements**: Providers often require prefix
  blocks to exceed minimum thresholds (e.g., 1024 or 2048 tokens) before
  caching activates. Ensure Zones 1 + 2 exceed this threshold.
- **Multi-tenant model routing**: If your architecture routes turns across
  different model providers or model sizes, prompt caches are not shared.
  Pin consistent subtasks to the same model endpoint.

## Failure Modes

- **Timestamp Cache Invalidation**: Placing dynamic timestamps or UUIDs on
  line 2 of the system prompt, causing 100% cache misses on every single turn.
- **Volatile Tool Registration**: Loading tools or skills in random dict order,
  altering prompt hash signatures.
- **Ad-hoc Regex Truncation**: Cutting off raw tokens without updating
  closing tags or message boundaries, resulting in malformed JSON or prompt
  syntax errors.

## Cross-References

- [`agent-working-memory-eval`](../agent-working-memory-eval/SKILL.md) — Measuring
  object-type token residency and heterogeneity.
- [`cost-effective-repo-exploration`](../cost-effective-repo-exploration/SKILL.md) —
  Strategies for loading minimal repository context.

## Sources

- ContextPipe: Database-Inspired Context Assembly for Long-Horizon Agents
  (arXiv:2609.00749)
