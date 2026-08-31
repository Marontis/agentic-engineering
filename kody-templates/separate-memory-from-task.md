---
id: separate-memory-from-task
title: Separate memory quality objective from task completion
severity: warning
category: agent-harness-design
enabled: true
tier: 2
source: "Code with Claude 2026, Talk 18: Memory and dreaming for self-learning agents"
evidence: "Harvey: 6x task completion when dreaming handles memory separately"
---

# Separate Memory Quality from Task Completion

## Detection

Look for agent harness code that asks a task-focused agent to ALSO
manage memory curation, knowledge organization, or learning synthesis
as part of its primary task loop.

### Indicators

```yaml
patterns:
  - Agent prompt contains both "complete the task" AND "update your learnings"
  - Single agent loop handles task execution AND memory deduplication
  - Memory write calls happen inside the task's hot path
  - Agent has competing objectives: performance + memory hygiene
```

### Examples

```python
# ❌ BAD: Task agent also curates memory
async def run_agent(task):
    result = await agent.execute(task)
    await agent.update_memory(result.learnings)  # competing objective
    await agent.deduplicate_memory()              # latency in hot path
    await agent.prune_stale_entries()             # not its job
    return result

# ✅ GOOD: Separate objectives
async def run_agent(task):
    result = await agent.execute(task)
    await agent.append_to_session_log(result)  # cheap, fast append
    return result

async def run_dreaming(session_logs):
    # Separate process, separate objective, out of band
    patterns = await dreaming_agent.analyze(session_logs)
    diff = await dreaming_agent.produce_memory_update(patterns)
    await review_and_apply(diff)
```

## Why This Matters

Asking a task agent to also curate memory creates three problems:

1. **Objective conflict**: The agent optimizes for task completion and
   deprioritizes memory quality under time pressure
2. **Latency penalty**: Memory curation adds time to the task's hot path
3. **Siloed perspective**: A single agent can't see cross-session patterns;
   it only knows its own context

Anthropic's research shows that separating these objectives (task agent
does tasks, dreaming agent does memory) produces dramatically better
outcomes: 6x completion rates, 90% fewer first-pass mistakes.

## Suggested Fix

1. Move memory curation to an out-of-band process
2. Task agents should only do cheap appends (session logs)
3. A separate dreaming/curation process reviews logs and produces diffs
4. Apply diffs to memory after review
