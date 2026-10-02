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

This rule flags scaffolding for **re-evaluation on each deployment
target**, not for removal. Whether a piece of scaffolding helps is
model-specific: planning scaffolds helped a weak model and mostly saved
cost on stronger ones (arXiv:2609.20804), and a ledger scaffold that
lifted dense models cost a sparse-MoE model up to 9 points
(arXiv:2608.26480). Only per-target evals decide.

### Never flag (exempt)

These are safety and correctness controls, not capability workarounds.
They stay regardless of model generation:

- Safety scaffolding: sandbox/permission checks, command classification,
  security tests, policy and allowlist enforcement
- Independent testers and verifiers (the author is never the sole
  certifier; see `rules/recursive-improvement.md` "DO: Enforce
  independent tester role separation")
- Loop guards: retry caps, token/turn caps, repetition detectors,
  recursion depth limits
- Terminal denials: refusals or hard stops after a denied action (the
  agent must not route around a denial)
- Acceptance gates and negative security testbeds

### Indicators

```yaml
patterns:
  - Multi-step workflow orchestration that could be a single agent call
    (excluding independent test/verify steps)
  - System prompts with model-specific *prompting* workarounds (not
    loop guards, denials or safety instructions)
  - Instructions that constrain planning ("think step by step" for models
    that already do adaptive thinking)
  - Accumulated prompt rules without clear rationale comments
  - Context-window management hacks (chunking, summarization) for models
    that sustain attention over 1M tokens
  - Forced tool-call sequences that prevent model from choosing its own order
```

### Examples

```python
# ⚠️ RE-EVALUATE: prompting workaround from an older model
SYSTEM_PROMPT = """
Think step by step. Before answering, write out a numbered plan.
Restate the question in your own words first.
"""
# Models with adaptive thinking may not need this. Run your evals on
# the new target with and without it; remove it only if the eval says so.

# ⚠️ RE-EVALUATE: forced planning/review steps from a weaker-model era
async def run_task(task):
    plan = await agent.plan(task)        # forced planning
    review = await agent.review(plan)    # forced self-review
    code = await agent.implement(plan)
    return await tester.verify(code)     # independent tester: KEEP
# The forced plan/review may be redundant on a stronger model.
# The independent tester is exempt and stays.

# ✅ GOOD: simplified after a per-target eval, controls kept
async def run_task(task):
    result = await agent.execute(
        task,
        effort="extra_high",
        max_turns=MAX_TURNS,             # loop guard: KEEP
        token_budget=TOKEN_BUDGET,       # loop guard: KEEP
    )
    return await tester.verify(result)   # independent tester: KEEP
# Planning scaffolding removed because evals on THIS model showed no
# loss; sandbox, permissions and denials are unchanged.
```

## Why This Matters

Anthropic's capability curve data shows:

1. **Planning**: Models now think before acting. Forcing explicit planning
   steps is redundant and adds latency.
2. **Error recovery**: Frontier models backtrack more often instead of
   doom-looping, so prompt-level "don't retry" advice may now block
   useful exploration. Hard loop guards (turn/token caps, repetition
   detectors) are still required: mid-sized models can spend the whole
   budget in runaway self-verification (arXiv:2608.26480).
3. **Long attention**: Models sustain focus over long contexts, so some
   context-window hacks may be overhead, but only on the models and
   budgets where your evals show it.

> "Often, you can actually boost your performance by REMOVING instead
> of adding things onto your scaffolding." — Alex Albert, Anthropic

## Suggested Fix

With every model upgrade:

1. **Audit prompts**: Re-evaluate model-specific workarounds. Cut rules without
   clear rationale. Shorter prompts = better performance + fewer tokens.
2. **Simplify workflows**: Try collapsing multi-step orchestrations into
   single agent calls. Measure if performance improves.
3. **Reduce babysitting only where evals allow**: chunking, context
   summarization and forced tool-call order are candidates, but context
   management still matters under tight context budgets
   (arXiv:2609.20804). Never remove the exempt controls above.
4. **Test with evals per deployment target**: Don't guess — measure.
   Run the simplified scaffolding on each target model against YOUR task
   distribution (not generic benchmarks). Keep a removal only if it
   passes `rules/recursive-improvement.md` "DO: Pass every
   self-modification through one acceptance gate" (no regression beyond
   a noise margin δ; security testbed strict).

## Eval Hygiene

- Build evals that mirror your actual product use cases
- Ensure evals are not saturated (if the model scores 100%, the eval
  is useless for detecting regressions)
- Grow eval difficulty alongside model capability
- The best optimization is sometimes just swapping in the latest model
