---
name: knowledge-compounding-loop
description: >
  How to consolidate raw agent execution traces into persistent structured
  knowledge that compounds across iterations, survives skill rollbacks, and
  informs future skill proposals. Covers the three-layer workspace pattern
  (raw/knowledge/skill), the wiki maintainer consolidation procedure, gated
  rollback with knowledge persistence, and cross-model skill transfer.
  Derived from WikiSkill (arXiv:2608.27454).
source: https://arxiv.org/pdf/2608.27454
related_skills:
  - skill-design-methodology
  - agent-self-improvement-loop
  - iterative-instruction-refinement
---

# Knowledge Compounding Loop

How to accumulate durable, structured knowledge from agent execution
experience — so that skill evolution builds on an increasingly well-supported
foundation rather than reinventing insights from scratch each iteration.

## The Problem

When agents iteratively improve their skills (instructions, workflows,
procedures), the insights that guide improvements typically stay scattered
across optimization histories — old proposals, rejected diffs, rollback
logs. Each new iteration starts from the same shallow understanding because
the intermediate knowledge was never consolidated.

This leads to three failure modes:

1. **Repeated proposals**: the system re-proposes changes that were already
   tried and rejected, because there's no record of why they failed
2. **Shallow diagnosis**: failure analysis starts from raw traces every
   time instead of building on prior root-cause analysis
3. **Lost context on rollback**: when a bad skill update is rolled back,
   the knowledge that motivated it is also lost — even when the knowledge
   itself was correct and only the skill implementation was wrong

**The evidence**: adding a persistent knowledge layer (wiki) between raw
traces and skills improves average benchmark performance by +15.0pp over
the same system without it. The ablation is clean — same model, same
traces, same skill format, only difference is whether accumulated knowledge
is available to the skill proposer.

> Source: WikiSkill (Tang et al., 2026), Table 3 ablation, Gemini 3.5 Flash

---

## The Three-Layer Workspace

Organize the agent workspace into three distinct layers with different
lifecycle guarantees:

### Layer 1: Raw Layer (immutable)

Stores execution traces exactly as they happened. Never edited, never
deleted. Each trace captures the agent's complete step-by-step interaction:
reasoning, tool calls, tool outputs, and final results.

**Lifecycle**: write-once, read-many. Traces are permanent records of
what actually happened.

**Purpose**: ground truth for analysis. The wiki maintainer and skill
proposer both read these to diagnose failures and extract strategies.

### Layer 2: Knowledge Layer (compounding, never reset)

Stores structured observations extracted from raw traces — failure
patterns, successful strategies, root-cause analyses, evolution logs.
Organized as individual pattern documents plus an index.

**Lifecycle**: append-and-update, never reset. Even when a skill update
is rolled back, the knowledge layer persists. It compounds monotonically
across all iterations.

**Contents**:
- **Pattern catalog** (`patterns/`): individual documents describing
  specific failure modes or successful strategies, with actionable
  workarounds. Created and updated by the wiki maintainer.
- **Index** (`index.md`): navigable catalog of all patterns, updated
  whenever patterns are modified.
- **Evolution log** (`logs.md`): chronological record of each iteration's
  findings, decisions, and outcomes. Provides historical awareness.
- **Impact tracker** (`skill-impact.md`): records every skill proposal's
  metadata, the diff, its validation score, and whether it was accepted
  or rejected. Written programmatically by the gating mechanism.

**Critical design choice**: the knowledge layer is NOT accessible to the
inference agent during task execution. Ablation shows that giving the
executing agent access to both skills and wiki degrades final skill
quality by −2.8pp average, because task-solving knowledge gets obtained
directly from the wiki rather than being properly compiled into skills.

### Layer 3: Skill Layer (gated, reversible)

Stores the active set of procedural skills that the agent uses during
task execution. Skills are the *output* — the compiled, validated
procedures that have earned their place through the gating process.

**Lifecycle**: propose → validate → accept/rollback. Skills are the
only layer that can be rolled back.

**Linkage**: each skill contains a purpose document that maps it back
to the knowledge-layer patterns that motivated its creation or
modification. This provenance link is critical for debugging why a
skill exists and whether the underlying knowledge has been updated.

---

## The Wiki Maintainer Procedure

After each batch of agent executions, consolidate observations into the
knowledge layer using this procedure:

### Input

- The existing knowledge layer (patterns, index, logs)
- A sample of execution traces from the latest iteration, stratified
  by outcome (include both successes and failures)

### Steps

1. **Root-cause analysis on failures**: for each failing trace, diagnose
   *why* it failed. Don't just note that it failed — identify the
   specific decision, assumption, or missing knowledge that caused it.

2. **Strategy extraction from successes**: for each passing trace,
   identify what worked and *why*. Look for strategies that are
   generalizable beyond the specific task.

3. **Pattern matching against existing knowledge**: check whether the
   diagnosed failures or extracted strategies match existing patterns.
   If yes, update the existing pattern with new evidence or refined
   solutions. If no, create a new pattern document.

4. **Incremental updates**: apply changes as patches — append, replace,
   or insert text spans within existing pattern documents. Don't
   rewrite entire documents unless the understanding has fundamentally
   changed.

5. **Update the index and log**: revise `index.md` to reflect any new
   or modified patterns. Append a summary of this iteration's findings
   to `logs.md`.

### What NOT to do

- Don't dump raw traces into the knowledge layer. The whole point is
  *consolidation* — structured, actionable observations, not raw data.
- Don't limit the number of patterns created per iteration. The
  maintainer should create as many or as few as the traces warrant.
- Don't give the wiki maintainer access to the skill layer. It
  should analyze what happened (traces) and what's known (knowledge),
  not what the current skills say. This avoids circular reasoning.

---

## Gated Rollback with Knowledge Persistence

When evaluating a proposed skill change:

1. **Apply the proposal** to produce a candidate skill set
2. **Evaluate** the candidate on a validation split
3. **Accept** if validation score exceeds the current best threshold
4. **Reject and rollback** the skill set if validation score doesn't
   improve — revert to the last accepted configuration

**Critical rule**: the knowledge layer is NEVER rolled back. Regardless
of whether the skill proposal was accepted:
- The knowledge patterns that motivated it persist
- The evolution log records the attempt
- The impact tracker records the proposal, its diff, the validation
  score, and whether it was accepted or rejected

This means the skill proposer in the next iteration can see:
- What was tried before
- Whether it worked or not
- The root-cause analysis that motivated it
- And avoid re-proposing the same failed change

---

## Cross-Model Skill Transfer

Skills evolved through this process transfer effectively across models:

- Skills evolved by one model can outperform self-evolved skills on
  another model (Qwen-27B skills improve Qwen-9B by +26.2pp on
  SpreadSheet, vs. +9.3pp from self-evolved skills)
- Transfer works across model families, not just sizes (Qwen-evolved
  skills improve Gemma, and vice versa)
- Stronger models generally extract more value from the same transferred
  skills

**When transfer fails**: skills that encode low-level workarounds specific
to one model's failure modes (e.g., "always use single-line Python
commands") can actively harm stronger models that would benefit from
more capable approaches. The skill-design-methodology's text-over-code
rule and subtask-level decomposition both reduce this risk.

**Implication for multi-model deployments**: consider evolving skills on
a stronger model and deploying them to weaker models. The skill
discovery capability of the stronger model may outweigh the weaker
model's self-evolved skills.

---

## When to Use This

### Use the knowledge compounding loop when:

- Your system iteratively refines agent behavior over multiple cycles
- You observe the same failure patterns recurring across iterations
- Skill rollbacks discard insights that were correct but badly
  implemented
- You need an audit trail of what was tried and why

### Use simpler approaches when:

- You're doing one-shot skill authoring (no iteration loop)
- Your execution trace volume is too low to warrant consolidation
- The skill proposer already has access to full execution history
  and the context window isn't a constraint

---

## Connection to Other Skills

| Skill | Relationship |
|:------|:------------|
| `skill-design-methodology` | Governs *how* the skill layer is authored. This skill governs the knowledge layer that *informs* skill authoring. |
| `agent-self-improvement-loop` | The WCF pattern (report → triage → validate → review) is complementary. WCF handles *issue detection*; this skill handles *knowledge consolidation*. |
| `iterative-instruction-refinement` | NPO-style revision is the mechanism for updating skill text. This skill provides the structured knowledge context that makes the revision informed. |
| `capability-aware-skill-selection` | Selection operates at runtime. This skill operates at evolution time. But the knowledge layer can inform capability model fitting by providing richer execution records. |

---

## Evidence Summary

| Finding | Source | Scale |
|:--------|:------|:------|
| Wiki layer adds +15.0pp average over no-wiki | Tang et al. 2026, Tab. 3 | 4 benchmarks, Gemini 3.5 Flash |
| Wiki access for inference agent degrades quality (−2.8pp) | Tang et al. 2026, Tab. 3 | 4 benchmarks |
| WikiSkill outperforms EvoSkill, SkillOpt, Trace2Skill | Tang et al. 2026, Tab. 1 | 5 benchmarks × 5 models |
| Benefits increase with model scale (+12.3 to +23.9pp) | Tang et al. 2026, Tab. 1 | Qwen 4B/9B/27B |
| Cross-model transfer: source ≠ self can outperform | Tang et al. 2026, Tab. 2 | 5 models × 5 benchmarks |
| Smaller model + skills > larger model without (+8.0pp) | Tang et al. 2026, §4.2.1 | Qwen-9B vs Qwen-27B |

## References

- **Paper**: [WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution](https://arxiv.org/abs/2608.27454) — Tang, Rashtchian, Ferng, Tomkins, Juan, Vu (Google Research / Virginia Tech)
- **Praxis source**: `src:2608-27454`
