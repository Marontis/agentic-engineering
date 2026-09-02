---
name: persistent-agent-migration
description: >
  Protocol for migrating long-lived AI agents across reasoning models,
  harnesses, host servers, and interaction surfaces while preserving
  architectural identity, private memory, and software body lineage.
  Derived from Enoch (arXiv:2609.00546).
source: https://arxiv.org/abs/2609.00546
---

# Persistent Agent Migration

Use this skill when designing, executing, or verifying migrations of
long-lived, stateful AI agents across models, orchestration frameworks,
or cloud hosts.

## When to Use

- Upgrading the underlying LLM (e.g., from GPT-4o to Claude 3.7 or an open
  weights model) without losing agent identity or task memory
- Migrating an agent between runtimes (e.g., from a local CLI to a cloud daemon
  or web service)
- Resuming complex multi-day workflows across process restarts or machine
  failures
- Ensuring verifiable continuity and authorized lineage for enterprise agents

## Core Insight

An agent should not be conflated with the model or harness that happens to
execute its current turn. A robust architecture separates the agent into two
distinct layers:

1. **Continuity-Bearing Substrate** $\mathcal{P}_t = (I_t, M_t, B_t)$:
   - **Identity** ($I_t$): Architectural persona, persistent goals, access
     credentials, public key certificates.
   - **Memory** ($M_t$): Private episodic memory, working knowledge base,
     active task boards.
   - **Body** ($B_t$): Versioned executable code lineage, installed skills,
     and tool plugins.
2. **Replaceable Execution Substrate** $\mathcal{E}_t = (R_t, H_t, D_t)$:
   - **Reasoner** ($R_t$): The specific model API or weight snapshot.
   - **Harness** ($H_t$): Orchestration runtime (LangGraph, AutoGen, custom).
   - **Host** ($D_t$): Infrastructure/hardware environment (laptop, VM, pod).

Changing the execution substrate $\mathcal{E}_t$ is a **migration**, not the
birth of a new agent, provided an authorized continuity protocol is followed.

---

## The Six-Stage Migration Protocol

To migrate an active agent without state corruption or behavioral divergence,
execute the **Quiesce–Checkpoint–Validate–Bind–Rehydrate–Resume** loop:

```
[ Active Running ]
       │
       ▼ (Trigger: model upgrade, host rebalance, maintenance)
  1. Quiesce
       │  (Drain in-flight tool calls, complete current turn, reject new tasks)
       ▼
  2. Checkpoint
       │  (Snapshot episodic memory, task graph, and git body commit)
       ▼
  3. Validate
       │  (Assert 6 continuity invariants against checkpoint package)
       ▼
  4. Bind
       │  (Attach new Reasoner, Harness, and Host configuration)
       ▼
  5. Rehydrate
       │  (Restore memory stores, verify tool connectivity, test reasoner ping)
       ▼
  6. Resume
       │  (Publish continuation certificate, open interaction surfaces)
       ▼
[ Restored Running ]
```

---

## Procedure

### Step 1: Quiesce In-Flight Execution

Do not kill or checkpoint an agent mid-turn:
1. Signal the harness to complete the current reasoning/tool turn.
2. Temporarily pause inbound message queues and webhook triggers.
3. Verify that all filesystem workspace locks and database transactions are
   either committed or cleanly rolled back.

### Step 2: Assemble the Continuity Package

Bundle the persistent substrate $\mathcal{P}_t$:
- **Identity Manifest**: Unique Agent UUID, cryptographic public key,
  authorized delegation scopes.
- **Durable Memory Snapshot**: Vector database export, episodic memory SQLite
  dump, and current task-board state.
- **Body Hash**: Git commit SHA of the agent's software body, installed skills,
  and rule configs.

### Step 3: Validate Continuity Invariants

Before releasing the old host, verify the checkpoint satisfies 6 core
invariants:
1. **Attribution**: Memory items trace back to verified user/agent turns.
2. **Completeness**: No open dangling transactions or unacknowledged tool
   responses.
3. **Identity Preservation**: Agent public key and core invariants remain
   unmodified.
4. **Lineage Hash Chain**: New checkpoint cryptographically references the prior
   checkpoint hash.
5. **Schema Compatibility**: Memory stores match the schema expected by the
   target harness.
6. **Authorization Bound**: Continuation authority has not expired or been
   revoked.

### Step 4: Bind and Rehydrate on Target Substrate

On the new execution host:
1. Spin up the new execution environment (new Reasoner endpoint, new harness).
2. Mount the private memory stores and verify database integrity (`PRAGMA
   integrity_check`).
3. Verify all declared tools and skills are reachable in the new environment.
4. Issue a synthetic "self-identity probe" turn to verify the new reasoner
   correctly reads its role and task context from the rehydrated state.

### Step 5: Resume and Audit Lineage

1. Unpause inbound task queues and interaction surfaces.
2. Log the migration event to the immutable audit ledger with:
   - Source: `(Reasoner_A, Host_A, Timestamp_A)`
   - Destination: `(Reasoner_B, Host_B, Timestamp_B)`
   - Checkpoint Digest: `sha256(...)`

---

## Environment Caveats

- **Model Context Window Disparities**: Migrating from a 200k-token model to
  a 32k-token model requires running an active memory compaction pass during
  the rehydration phase.
- **Tool Calling Format Differences**: Different reasoning models (e.g.,
  OpenAI vs. Anthropic vs. local GGUF) require different tool call schemas.
  The harness translation layer must normalize tool signatures without
  altering tool semantics.

## Failure Modes

- **Split-Brain Continuation**: The old host resumes execution after the
  new host starts, causing divergent, conflicting memories and double-actions.
  Enforce strict mutual exclusion via leased distributed locks.
- **Silent Context Amnesia**: Checkpointing only recent conversation tokens
  while forgetting long-term memory databases, reducing the agent to a blank
  slate on migration.
- **Unverified Reasoner Substitution**: Upgrading to a model that fails to
  follow structured tool output schemas, causing repeated validation crashes
  on resume.

## Cross-References

- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) —
  Filesystem checkpointing and rollback mechanisms.
- [`agent-sandbox-safety`](../../rules/agent-sandbox-safety.md) — Security
  rules for authorized agent execution and network boundaries.

## Sources

- Runtime-Independent Persistent Agents: Architectural Identity, Memory, and
  Migration (arXiv:2609.00546)
- Enoch Reference Implementation: https://github.com/our-ark/enoch
