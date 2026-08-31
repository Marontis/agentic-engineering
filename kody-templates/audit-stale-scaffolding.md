---
id: audit-stale-scaffolding
title: Audit agent scaffolding for stale or counterproductive rules
severity: suggestion
category: agent-harness-design
enabled: true
tier: 1
source: "Code with Claude 2026, Talk 10: The capability curve (Alex Albert, Anthropic)"
evidence: "SWE-bench verified: 62% → 87% in 12 months; complex scaffolding that helped Sonnet 3.7 hurts Opus 4.7"
---

# Audit Agent Scaffolding for Stale Rules

## Detection

Look for agent scaffolding (prompts, skills, tool configurations, workflow
orchestrations) that was designed for an older model generation and has
not been re-evaluated since the model was upgraded.

### Indicators

```yaml
patterns:
  - Multi-step workflow orchestration that could be a single agent call
  - System prompts with model-specific workarounds (e.g. "do not loop")
  - Instructions that constrain planning ("think step by step" for models
    that already do adaptive thinking)
  - Accumulated prompt rules without clear rationale comments
  - Context-window management hacks (chunking, summarization) for models
    that sustain attention over 1M tokens
  - Forced tool-call sequences that prevent model from choosing its own order
```

### Examples

```python
# ❌ STALE: Workaround for old doom-loop behavior
SYSTEM_PROMPT = """
If you encounter an error, DO NOT try the same approach again.
Instead, stop and ask the user for guidance.
IMPORTANT: Never attempt more than 3 retries.
"""
# Newer models backtrack and try different approaches naturally.
# This instruction now prevents useful exploration.

# ❌ STALE: Multi-step orchestration from weaker-model era
async def run_task(task):
    plan = await agent.plan(task)        # Step 1: force planning
    review = await agent.review(plan)    # Step 2: force review
    code = await agent.implement(plan)   # Step 3: force coding
    test = await agent.test(code)        # Step 4: force testing
    return test
# Newer models do plan→implement→test naturally in one run,
# and forced steps add latency + token cost.

# ✅ GOOD: Let the model work
async def run_task(task):
    return await agent.execute(task, effort="extra_high")
# Adaptive thinking handles planning, error recovery, and
# verification internally.
```

## Why This Matters

Anthropic's capability curve data shows:

1. **Planning**: Models now think before acting. Forcing explicit planning
   steps is redundant and adds latency.
2. **Error recovery**: Models backtrack instead of doom-looping. Anti-loop
   instructions now prevent useful exploration.
3. **Long attention**: Models sustain focus over 1M+ tokens. Context-window
   hacks are unnecessary overhead.

> "Often, you can actually boost your performance by REMOVING instead
> of adding things onto your scaffolding." — Alex Albert, Anthropic

## Suggested Fix

With every model upgrade:

1. **Audit prompts**: Remove model-specific workarounds. Cut rules without
   clear rationale. Shorter prompts = better performance + fewer tokens.
2. **Simplify workflows**: Try collapsing multi-step orchestrations into
   single agent calls. Measure if performance improves.
3. **Remove babysitting**: Stop chunking work, stop summarizing context,
   stop forcing tool-call order. Let the model choose.
4. **Test with evals**: Don't guess — measure. Swap the new model in with
   the simplified scaffolding and run evals on YOUR task distribution
   (not generic benchmarks).

## Eval Hygiene

- Build evals that mirror your actual product use cases
- Ensure evals are not saturated (if the model scores 100%, the eval
  is useless for detecting regressions)
- Grow eval difficulty alongside model capability
- The best optimization is sometimes just swapping in the latest model
