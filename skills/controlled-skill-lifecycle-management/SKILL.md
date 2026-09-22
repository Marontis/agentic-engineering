---
name: controlled-skill-lifecycle-management
description: >
  Govern post-deployment agent skill evolution through typed failure
  diagnosis, scoped skill patches with targeted validation, regression
  checks, negative controls, and versioned replacement or retirement.
  Prevents uncontrolled behavioral drift from unchecked skill updates.
  Derived from "FINSKILLOPS: A Self-Evolving Multi-Agent System for
  SEC Filing QA" (arXiv:2609.19680).
source: https://arxiv.org/abs/2609.19680
---

# Controlled Skill Lifecycle Management (FINSKILLOPS)

Use this skill when managing a registry of reusable agent skills that
evolve post-deployment, and you need admission gates to prevent skill
updates from introducing regressions or uncontrolled behavioral drift.

## When to Use

- Agent system has recurring failures that should become reusable
  skill patches
- Skill registry is growing and you need governance over what gets
  promoted vs. rejected
- Prior skill updates have introduced regressions in previously
  correct behavior
- You want to implement a principled skill lifecycle: propose →
  validate → promote → version → retire

## Core Insight

Post-deployment improvement should be framed as **controlled
behavioral maintenance**, not unchecked self-modification. Recurring
failures should become **scoped skill patches**, and each patch must
earn deployment through explicit admission gates without introducing
regressions. The key finding: in a 12-round operational study, **only
6 of 33 proposed skills were promoted** — the 82% rejection rate is
a feature, not a bug, as it prevented regression while the monitoring
non-correct rate fell from 20.0% to 12.5%.

**Evidence**: A single frozen skill registry achieves highest
verdict-weighted correctness and reference consistency across six
benchmarks. Evolved skills raise correctness from 3.70 to 4.55.

---

## Procedure

### 1. Diagnose Failures with Typed Classification

When an agent fails on a task:

1. Classify the failure into a **typed category**: period error,
   entity error, evidence-use error, calculation error, or
   domain-specific types
2. Ground the diagnosis in **evidence** — what specific input or
   reasoning step triggered the failure?
3. Check whether the failure type matches an **existing skill** that
   should have prevented it (skill gap vs. skill failure)

### 2. Derive Scoped Skill Patches

For each diagnosed failure pattern:

1. Write a **skill patch** that addresses the specific failure type
2. Define the patch's **scope** — what input patterns it applies to,
   what behavior it modifies
3. Scope must be **narrow enough** that it doesn't alter behavior on
   unrelated inputs
4. Derive the patch from the evidence-grounded diagnosis, not from
   ad-hoc observation

### 3. Run Targeted Validation

Before promotion, each proposed skill must pass:

1. **Targeted validation**: the skill correctly handles the failure
   cases that motivated it
2. **Protected-case regression checks**: previously correct answers
   remain correct after applying the skill
3. **Negative controls**: confirm the skill does NOT trigger on inputs
   outside its intended scope
4. All three gates must pass — failure on any gate blocks promotion

### 4. Promote, Version, or Reject

Based on validation results:

- **Promote**: all gates pass → add skill to the frozen registry with
  a version number
- **Reject**: any gate fails → log the failure, discard the skill,
  optionally flag for redesign
- **Version replacement**: new skill replaces an existing one → the
  old version is retired but preserved in version history
- **Retirement**: skill no longer triggers on current workload →
  mark inactive but keep in history for rollback

### 5. Freeze and Monitor

1. After promotion, the registry is **frozen** until the next
   evaluation cycle
2. Monitor the non-correct rate on incoming tasks
3. If the non-correct rate increases after a promotion cycle →
   investigate which newly promoted skill is responsible
4. Rollback to the previous frozen registry if regression is confirmed

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Over-scoped skill patch | Skill triggers on unrelated inputs | Negative controls (Step 3.3) catch out-of-scope activation |
| Under-scoped skill patch | Skill is too narrow to generalize | Targeted validation uses diverse examples of the failure pattern |
| Regression from new skill | New skill breaks previously correct behavior | Protected-case regression checks (Step 3.2) block promotion |
| Skill accumulation bloat | Registry grows with rarely-used skills | Retirement policy: mark inactive when skill hasn't triggered in N cycles |
| False confidence from frozen registry | New failure types not covered by existing skills | Continuous monitoring of non-correct rate; trigger new diagnosis cycles |

> Source: Ma et al., "FINSKILLOPS: A Self-Evolving Multi-Agent System
> for SEC Filing QA" (arXiv:2609.19680), Sep 2026.
