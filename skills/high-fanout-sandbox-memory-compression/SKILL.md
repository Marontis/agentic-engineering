---
name: high-fanout-sandbox-memory-compression
description: >
  Compress KV-cache and context state for agents running many
  parallel sandbox instances.  Covers shared-prefix deduplication,
  per-instance delta encoding, and memory-budget-aware eviction.
  Derived from "Memory Compression for High-Fanout Agent Sandboxes"
  (arXiv:2609.11294).
---

# High-Fanout Sandbox Memory Compression

Use this skill when running an agent across many parallel sandbox
instances and memory consumption is the bottleneck.

## When to Use

- Your agent spawns 10+ parallel sandbox instances (e.g., for
  test-time search, speculative execution, or A/B evaluation)
- GPU/CPU memory is the scaling bottleneck, not compute
- Multiple instances share a common prefix (system prompt,
  task description) but diverge on execution paths
- You need to fit more concurrent instances in fixed memory

## Core Insight

When an agent runs N parallel sandboxes, naive replication stores
N full copies of context and KV-cache.  But most instances share
a common prefix (system prompt + task).  **Shared-prefix
deduplication** stores the common prefix once and only the
per-instance deltas, reducing memory from O(N × L) to
O(L + N × Δ) where Δ is the average divergence length.

## Procedure

### Step 1: Identify the shared prefix

Determine the longest common prefix across all sandbox instances:

- System prompt → always shared
- Task description → usually shared
- Initial tool results → shared if deterministic tools
- Agent reasoning → diverges after first decision point

The prefix boundary is the first token where any instance diverges.

### Step 2: Deduplicate KV-cache prefix

Store the KV-cache for the shared prefix exactly once:

1. Run the forward pass for the shared prefix once
2. Store the resulting KV-cache tensors in shared memory
3. Each sandbox instance references the shared KV-cache
   for prefix tokens and maintains its own KV-cache only
   for post-divergence tokens
4. On read: concatenate shared prefix KV + instance delta KV

### Step 3: Delta-encode per-instance state

For each sandbox instance, store only:

- The delta tokens (post-divergence)
- The delta KV-cache entries
- Instance-specific tool state (file system changes, etc.)

### Step 4: Memory-budget-aware eviction

When total memory approaches the budget:

1. **Priority ranking**: Rank instances by promise (e.g.,
   partial reward, depth reached, diversity from other instances)
2. **Evict lowest-priority**: Kill and free the lowest-ranked
   instance's delta memory
3. **Checkpoint before eviction**: If the instance might be
   needed later, checkpoint its delta to disk
4. **Lazy restoration**: If a checkpointed instance is needed,
   restore only its delta on top of the (still-live) shared prefix

### Step 5: Monitor compression ratio

Track the effective compression:

```
compression_ratio = (N × full_context_size) / 
                    (shared_prefix_size + N × avg_delta_size)
```

Typical ratios: 3–8× for coding tasks, 2–4× for open-ended tasks.
If ratio drops below 2×, the instances have diverged too much
for prefix sharing to help — consider reducing fanout.

## Environment Caveats

- **Dynamic prefixes**: If the task description includes
  retrieved context that changes per query, the shared prefix
  is shorter.  Measure actual sharing before committing to
  this optimization.
- **Model architecture**: Prefix sharing requires the serving
  framework to support shared KV-cache (vLLM, SGLang do;
  some frameworks don't).
- **Instance lifetime**: Short-lived instances may not justify
  the overhead of delta management.  Best for instances that
  run 100+ tokens.

## Failure Modes

- **False sharing**: Assuming tokens are shared when they
  aren't (e.g., due to non-deterministic sampling) corrupts
  KV-cache.  Validate prefix identity at the token level.
- **Eviction regret**: Evicting an instance that turns out
  to be the best path.  Use checkpointing to make eviction
  reversible.
- **Memory fragmentation**: Frequent allocation/deallocation
  of delta buffers fragments GPU memory.  Use a slab allocator
  or pre-allocated pool.

## Cross-References

- [`prefix-preserving-context-assembly`](../prefix-preserving-context-assembly/SKILL.md) —
  ContextPipe preserves byte-identical prefixes for KV-cache reuse;
  this skill extends the principle to high-fanout scenarios
- [`speculative-sandbox-scheduler`](../speculative-sandbox-scheduler/SKILL.md) —
  SpecBox pre-allocates sandboxes; memory compression determines
  how many can fit in memory

## Sources

- Memory Compression for High-Fanout Agent Sandboxes (arXiv:2609.11294)
