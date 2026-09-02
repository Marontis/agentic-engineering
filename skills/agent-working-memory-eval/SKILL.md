---
name: agent-working-memory-eval
description: >
  How to evaluate and manage coding agent working memory (context window
  utilization).  Covers object-type heterogeneity, content accounting,
  object-aware compression, and retrieval-based memory management.
  Derived from "Measure Before You Manage" (arXiv:2608.31057).
---

# Agent Working Memory Evaluation

Use this skill when evaluating or improving how coding agents
manage the code and context loaded into their context window.

## When to Use

- Your coding agent runs out of context or performs poorly on
  long tasks
- You want to measure how effectively your agent uses its
  context window
- You're comparing memory management strategies (compression,
  retrieval, pruning)
- You're building a context management layer for a coding agent

## Core Insight

Coding agents load different types of objects into their context
(source files, error messages, tool outputs, conversation history),
and these types differ dramatically in volume, residency time, and
representation behavior.  The "pooled average" across all objects
is misleading — **you must account for heterogeneity**.

**Key findings**:
- Nominal context budgets (the stated limit) don't reflect effective
  budgets (what's actually used)
- Different object types need different management strategies
- Memory management overhead (compression, retrieval) is itself
  a cost that must be included in comparisons

## Procedure

### Step 1: Identify object types in working memory

Categorize everything the agent loads into context:

| Object Type | Example | Typical Properties |
|:-----------|:--------|:------------------|
| **Source code** | File contents | Large, high residency |
| **Tool output** | Test results, grep output | Variable size, transient |
| **Error messages** | Stack traces, lint output | Small, high value |
| **Conversation** | User messages, agent reasoning | Growing, partly stale |
| **Plans/state** | Task lists, progress notes | Small, persistent |

### Step 2: Measure per-type metrics

For each object type, measure:

- **Volume**: How many tokens does this type contribute on average?
- **Residency**: How long does this type stay in context?
- **Contribution**: Does this type's presence correlate with
  task success?
- **Redundancy**: How much of this type is duplicated or stale?

### Step 3: Object-aware compression

Apply different compression strategies per object type:

| Object Type | Strategy |
|:-----------|:---------|
| **Source code** | Keep signatures + docstrings; elide function bodies unless actively editing |
| **Tool output** | Summarize; keep only relevant lines from long outputs |
| **Error messages** | Keep full; these are high-signal-per-token |
| **Conversation** | Summarize old turns; keep recent turns verbatim |
| **Plans/state** | Keep full; small and persistent |

### Step 4: Retrieval-based memory management

For objects too large to keep in context:

1. **Index**: Store all loaded objects in a retrievable index
2. **Evict**: Remove objects from active context when not
   immediately needed
3. **Recall**: Retrieve evicted objects when they become relevant
   again (triggered by tool calls, errors, or explicit requests)

### Step 5: Evaluate management strategies

When comparing memory management approaches:

- **Include management overhead**: The tokens spent on compression,
  retrieval queries, and re-loading count against the budget
- **Measure effective budget**: The actual tokens available for
  useful content after management overhead
- **Control for object composition**: Two tasks with different
  object-type distributions need different management strategies;
  don't average across them

## Environment Caveats

- **Large context windows** (100k+ tokens): Management overhead
  may exceed savings for short tasks.  Only apply management for
  tasks that would exceed the window.
- **Streaming agents**: Agents that stream tool outputs need
  real-time decisions about what to keep vs. evict.
- **Multi-file edits**: Tasks that touch many files simultaneously
  have high source-code residency requirements.  Prioritize
  keeping edited files in context.

## Failure Modes

- **Uniform compression**: Applying the same compression to all
  object types loses high-value content (error messages) while
  barely compressing low-value content (stale conversation).
- **Over-eviction**: Removing too much context forces expensive
  re-retrieval.  The cost of re-loading a file may exceed the
  cost of keeping it.
- **Ignoring management cost**: A clever management strategy
  that costs 10k tokens of overhead to save 8k tokens of
  content is a net loss.

## Cross-References

- [`cost-effective-repo-exploration`](../cost-effective-repo-exploration/SKILL.md) —
  Exploration determines what to load; this skill manages what's
  loaded after it arrives

## Sources

- Measure Before You Manage: Evaluating Agent Working Memory in Coding Agents (arXiv:2608.31057)
