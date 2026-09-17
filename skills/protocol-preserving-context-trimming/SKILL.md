---
name: protocol-preserving-context-trimming
description: >
  Protocol-preserving context trimming and adaptive budget guardrails for multi-step
  agentic workflows. Prevents catastrophic task failure and protocol violations caused
  by naive token trimming (recency, relevance, summarization) by protecting dependency
  chains, tool states, and protocol invariants. Derived from Gaggar (arXiv:2609.16461).
source: https://arxiv.org/abs/2609.16461
---

# Protocol-Preserving Context Trimming

Use this skill when managing context windows in long-horizon, multi-step agentic workflows where uncontrolled context expansion causes latency or cost issues, but naive truncation threatens workflow failure.

## When to Use

- Long-horizon tool-using agents (multi-turn coding, API orchestration, SWE workflows) approaching token limits.
- Agents experiencing sudden cascading tool failures, forgotten prerequisites, or dropped protocol contracts after context compression.
- Replacing heuristic recency-based (FIFO) truncation, semantic similarity filtering, or naive text summarization with formal reliability guardrails.
- Systems requiring sustained high token savings (~55-60%) without sacrificing task completion rates.

## Core Insight

Conventional context reduction techniques—such as recency-based sliding windows, relevance-based retrieval filtering, or naive history summarization—achieve ~60% token savings but severely degrade reliability:
- Task success drops to **66.6%–77.3%**
- Protocol adherence falls to **85.5%–88.6%**
- Aggressive context budgets ($\le 25\%$ retained context) cause a **10.92-fold increase in failure odds** ($p < 0.001$) compared to budgets $\ge 50\%$.

The primary cause of failure is not loss of semantic context, but the silent destruction of **protocol-critical state**: unresolved tool calls, intermediate schema definitions, authorization tokens, causal dependency chains, and active execution invariants.

By contrast, **protocol-aware trimming** ensures that protocol-critical spans are pinned and never pruned, boosting task success to **92.2%** (a 5.24-fold improvement under aggressive budgets). Combining protocol preservation with **adaptive budget guardrails**—which dynamically scale context retention based on workflow complexity—achieves **96.0% task success**, **96.3% protocol adherence**, and reduces cascading failures to **1.0%** while preserving **56.0% mean token savings**.

---

## Procedure

```
Trajectory Context
       │
       ▼
[1. Protocol State Classification]
  ├── Identify Protocol-Critical Anchors (Schemas, Invariants, Unresolved IDs)
  └── Identify Prunable Dynamic Payload (Redundant observations, verbose stdout)
       │
       ▼
[2. Complexity Class Estimation]
  ├── Assess Graph Depth, Branching Factor & Dependency Density
  └── Determine Dynamic Budget Floor (Guardrail Threshold: 35% - 60%)
       │
       ▼
[3. Protocol-Aware Trimming & Anchor Preservation]
  ├── Pin Protocol Anchors & Dependency Ancestors
  └── Prune Intermediate Non-Critical Turns & Payload Bodies
       │
       ▼
[4. Boundary Verification & Invariant Audit]
  └── Verify Reference Integrity (No Dangling Tool IDs or Broken Contracts)
```

### Step 1: Classify Context Spans into Protocol Anchors vs. Prunable Payload

Before removing any tokens, parse the raw execution trace into semantic protocol blocks:

1. **Pin Protocol-Critical Anchors (Non-Evictable)**:
   - **Active Schema & Invariants**: Tool function signatures, return schemas, global environment constraints.
   - **Unresolved Dependencies**: Pending tool calls, open transaction IDs, promises, or async tasks waiting for fulfillment.
   - **Causal State Transitions**: Tool invocations that established persistent state changes (e.g., file creation, directory change, branch checkout, environment variables).
   - **Root Task Contract**: Initial user objective, acceptance criteria, and explicit negative constraints.

2. **Mark Prunable Payload (Evictable)**:
   - **Verbose Tool Observations**: Raw stdout/stderr logs from successful intermediate commands where only exit code or key entity names matter.
   - **Exploration Dead Ends**: Rejected candidate attempts or failed grep searches whose negative findings have already been incorporated into current plans.
   - **Transient Conversational Pleasantries**: Acknowledgments, filler reasoning, and duplicate confirmation turns.

### Step 2: Calculate Workflow Complexity & Set Adaptive Budget Guardrails

Do **not** apply a uniform fixed retention ratio across all tasks. Classify the workflow complexity class and apply the corresponding minimum retained budget floor:

| Complexity Class | Structural Characteristics | Minimum Retained Budget Floor ($\theta$) |
|:---|:---|:---|
| **Class A (Linear)** | Single tool chain, depth $\le 3$, no branching | 30% - 35% |
| **Class B (Tree / Branching)** | Subagents, parallel searches, depth 4–7 | 45% - 50% |
| **Class C (Cyclic / Iterative)** | Debugging loops, refactoring, depth $\ge 8$, cross-module dependencies | 55% - 65% |

**Guardrail Invariant**: If projected context reduction would push retained tokens below threshold $\theta$, trigger **spill-over summarization** into an external persistent ledger rather than dropping tokens below the critical threshold.

### Step 3: Execute Protocol-Aware Trimming

When trimming context to meet the budget:

1. **Preserve Causal Chains**: Trace backward from all currently active variables and files to their introducing tool turn. Pin those turns regardless of age.
2. **Compress Observations into Receipts**: Replace verbose command outputs with structured receipts:
   ```json
   {
     "tool": "run_command",
     "call_id": "call_123",
     "status": "success",
     "exit_code": 0,
     "summary": "Created 12 test fixtures in tests/fixtures/",
     "persisted_entities": ["tests/fixtures/test_user.json", "tests/fixtures/test_org.json"]
   }
   ```
3. **Trim Intermediates in Chronological Batches**: Evict non-anchor turns starting from the oldest non-essential steps, keeping the immediate working tail ($N=3..5$ turns) completely uncompressed.

### Step 4: Verify Protocol Integrity and Dangling References

Execute a post-trim validation pass prior to dispatching the next model prompt:

1. **Dangling Call Audit**: Assert that every `tool_call_id` referenced in assistant/tool messages has both the call and response retained.
2. **Schema Coverage Audit**: Confirm all tools invoked in the working tail have their JSON schemas intact in the prefix.
3. **State Consistency Audit**: Ensure no active file path referenced in the current instruction has had its generation lineage pruned without an explicit entity summary.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Quantitative Impact | Concrete Mitigation |
|:-------------|:--------|:-------------------|:-------------------|
| **Aggressive Budget Collapse** | Setting retained context $\le 25\%$ to minimize token costs | 10.92× increase in task failure odds ($p < 0.001$) | Enforce strict adaptive budget guardrail: never trim below 35% for linear and 55% for cyclic tasks. |
| **Dangling Tool-Call Violation** | Trimming assistant tool call while retaining tool output, or vice versa | Provider API 400 Bad Request error; session crash | Atomic pruning: treat `(tool_call, tool_result)` pairs as indivisible units. |
| **Pruned Causal Prerequisite** | Dropping an early turn that modified working directory or installed dependencies | Cascading tool failure (missing file/command) | Pin state-mutating tool executions in a persistent scratchpad/ledger before trimming history. |
| **Schema Amnesia** | Pruning capability descriptions during multi-turn exploration | Model generates hallucinated tool signatures | Keep capability schemas in an immutable Zone 2 prefix separate from message history. |

## Cross-References

- [`prefix-preserving-context-assembly`](../prefix-preserving-context-assembly/SKILL.md) — Structural layout of immutable prefix and evictable memory zones.
- [`dependency-scoped-plan-validation`](../dependency-scoped-plan-validation/SKILL.md) — Ensuring pending actions match active memory dependencies.
- [`ledger-orchestrated-coding-loop`](../ledger-orchestrated-coding-loop/SKILL.md) — Externalizing milestone receipts into durable filesystem ledgers.
