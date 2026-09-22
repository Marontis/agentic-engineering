---
name: attribution-guided-skill-graph-update
description: >
  Route observed agent failures to specific editable locations in a
  skill graph via abductive attribution, apply targeted local repairs,
  and screen changes through two-level validation gates before
  committing. Prevents unscoped skill edits and regression from
  unvalidated updates.
  Derived from "SkillAA: Attribution-Guided Skill-Graph Updating with
  Targeted Validation and Rollback" (arXiv:2609.20455).
source: https://arxiv.org/abs/2609.20455
---

# Attribution-Guided Skill-Graph Updating (SkillAA)

Use this skill when maintaining a skill graph for a frozen LLM agent
and you need to repair skills from failed execution traces without
breaking working skills or making unscoped edits.

## When to Use

- Agent fails on a task and you need to identify WHICH skill (or skill
  component) to fix, not just THAT it failed
- Skill graph has grown large enough that editing the wrong node causes
  cascading regressions
- You want structured commit gates (not just "did accuracy go up?")
  before accepting skill changes
- Upgrading from flat skill lists to graph-structured skill management

## Core Insight

Existing skill evolution methods edit skills directly from failed
rollouts without structured routing from the failure to an editable
location. SkillAA introduces **abductive attribution**: contrast
successful and failed executions on the same task to isolate which
graph object (skill node, edge, or composition) diverged, then route
the repair to that specific object. Two validation gates — **Local
Gate** (graph-scoped retesting) and **Big Gate** (epoch-level commit)
— screen changes before they become permanent.

**Evidence**: With gpt-5.6-sol, SkillAA reaches 81.5% (SearchQA),
66.7% (LiveMath), and 91.2% (DocVQA) — highest observed mean in every
main setting. Attribution routing and two-level gating each contribute
independently (ablation-confirmed).

---

## Procedure

### 1. Represent Skills as a Structured Graph

Organize skills with three node types in a unified graph:

- **Applicability nodes**: conditions under which a skill activates
  (semantic boundaries, input type guards)
- **Execution nodes**: the procedural content of the skill (step
  sequences, tool calls, prompts)
- **Composition nodes**: how skills chain or delegate (dependencies,
  ordering constraints, data flow)

Edges encode **topological dependencies** and **object addresses** so
that retrieval, attribution, and update all operate on the same
structure.

### 2. Execute and Collect Traces with Usage Records

For each task epoch:

1. Retrieve relevant skills via **semantic activation** (match task
   description against applicability nodes)
2. Execute the task with the selected skills, recording a full
   **usage trace**: which nodes were activated, what outputs they
   produced, which composition edges were traversed
3. Record the outcome: success or failure, with error details

### 3. Attribute Failures via Abductive Contrast

When a task fails:

1. Find a **successful execution** of the same or closely similar task
   (same skill activation pattern, different outcome)
2. **Contrast** the two traces to identify the divergence point — the
   specific graph object where the failed trace deviated
3. Route the candidate repair to **that specific object**, not to the
   entire skill or a random location
4. If no successful contrast is available, fall back to error-message
   attribution (less precise but still scoped)

### 4. Apply Targeted Local Repair

1. Generate a candidate patch for the attributed graph object only
2. Allowed edits: modify execution content, adjust applicability
   conditions, update composition edges
3. **Deterministic merge validation**: verify the patch is structurally
   valid and doesn't create cycles or orphaned nodes
4. Do NOT edit objects outside the attribution scope

### 5. Screen Through Local Gate

Before committing the patch to the graph:

1. **Re-execute** the failed task with the patched graph — it must now
   succeed
2. **Re-execute** all tasks that used the same graph object in the
   current epoch — none must regress
3. Use **paired execution** with decision stability checks (run twice,
   confirm same outcome)
4. If the Local Gate fails → **rollback** the patch and try a
   different repair or attribution

### 6. Screen Through Big Gate (Epoch Commit)

At the end of each epoch (batch of tasks):

1. Run the full epoch task set against the candidate graph
2. Compare aggregate performance against the pre-epoch baseline
3. If epoch-level performance regresses → **restore** the pre-epoch
   graph state entirely
4. If it passes → commit all accumulated patches as the new baseline

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Wrong attribution target | Contrast traces diverge at multiple points | Use topological shortest-path to the first divergence; prefer structural over semantic matches |
| Patch passes Local Gate but breaks distant skill | Changed node has implicit dependency not in graph | Big Gate catches epoch-level regression; rollback restores pre-epoch state |
| No successful contrast available | Novel task type with no prior success | Fall back to error-message attribution; flag as lower-confidence repair |
| Graph bloat from accumulated patches | Too many fine-grained nodes slow retrieval | Periodically merge semantically equivalent nodes; prune unused applicability conditions |
| Overfitting to specific task instances | Patch is too narrow to generalize | Local Gate retests across ALL tasks using the same node, not just the failed one |

> Source: Shang et al., "SkillAA: Attribution-Guided Skill-Graph
> Updating with Targeted Validation and Rollback" (arXiv:2609.20455),
> Sep 2026.
