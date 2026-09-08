---
name: intent-driven-sdlc-planning
description: >
  Structure upstream planning for agentic software development as a
  three-artifact pipeline: intent.md → spec.md → plan.md. Each artifact
  gates the next stage, is version-controlled, and is produced through
  a prompted AI-assisted session. Derived from the AI-Native SDLC Playbook
  (Claude Academy, Anthropic Applied AI).
source: https://academy.claude.com/courses/ai-native-sdlc-playbook
---

# Intent-Driven SDLC Planning

Use this skill when a raw idea, feature request, or initiative needs to be
structured before an agentic coding tool begins writing code. The pipeline
produces three versioned artifacts that progressively sharpen intent into
an implementable plan.

## When to Use

- A non-technical stakeholder describes a desired outcome but hasn't
  specified constraints, scope, or acceptance criteria
- An engineering lead wants to decompose a large initiative into
  agent-ready work units before launching parallel coding sessions
- The team needs an audit trail showing *why* code was written, not just
  *what* was changed
- Requirements are ambiguous enough that an agent would hallucinate scope
  if given the raw prompt directly

## Core Insight

When agentic tools can write code faster than humans can review it, **the
bottleneck shifts upstream**: planning, scoping, and design become the
limiting factor. Organizations that restructure their SDLC to produce
machine-readable planning artifacts *before* code generation see dramatic
throughput improvements because agents receive precise, constrained
instructions rather than vague feature descriptions.

The key is treating planning artifacts as first-class version-controlled
deliverables with explicit progression gates — a merged `intent.md` is the
signal to begin design, a merged `spec.md` is the signal to begin planning,
and a merged `plan.md` is the signal to begin implementation.

---

## Procedure

### Step 1: Capture Intent as `intent.md`

When a new idea arrives (from a user, stakeholder, or incident), create an
`intent.md` file using the following template. This is a *proto-spec* — it
captures what is wanted and why, without prescribing how.

```markdown
# Intent: [Short Title]

## Problem
What is broken, missing, or suboptimal? Be specific about observable symptoms.

## Proposed Outcome
What should be true when this is done? State acceptance criteria as
observable, testable conditions.

## Affected Users / Systems
Who or what is impacted? List user roles, services, or components.

## Constraints
- Budget / timeline boundaries
- Regulatory or compliance requirements
- Systems that must NOT be modified
- Backward compatibility requirements

## Open Questions
List anything that must be answered before design can begin.
```

**Key principle**: The originator fills in what they know. An AI assistant
can brainstorm with them to surface missing constraints and sharpen vague
language, but the originator owns the intent.

### Step 2: Convert Intent to `spec.md`

In a single prompted design session, convert `intent.md` into a detailed
specification. Feed the intent plus any relevant organizational context
(architecture docs, existing skills, `CLAUDE.md` or equivalent) to the AI
assistant and prompt it to produce:

```markdown
# Spec: [Feature Name]

## Overview
One-paragraph summary of what this feature does.

## Functional Requirements
Numbered list of specific, testable requirements.

## Non-Functional Requirements
Performance targets, security constraints, observability needs.

## Architecture
Which components are affected, how they interact, what changes.

## API Contract (if applicable)
Endpoints, request/response schemas, error codes.

## Data Model Changes (if applicable)
Schema changes, migration strategy, backward compatibility.

## Security Considerations
Auth, authorization, data handling, PII exposure.

## Test Strategy
What kinds of tests validate this spec (unit, integration, e2e).

## Out of Scope
Explicit list of things this feature does NOT do.
```

**Gate**: `spec.md` is reviewed (by human or agentic reviewer) and merged.
The merge signals that design is ratified and planning can begin.

### Step 3: Generate `plan.md` from Spec

Use the AI assistant's planning mode to generate an implementation plan
from the ratified spec. The plan should be concrete enough for an agent to
execute without further clarification:

```markdown
# Plan: [Feature Name]

## Files to Create
- path/to/new/file.ts — purpose

## Files to Modify
- path/to/existing/file.ts — what changes and why

## Order of Work
1. Step description — rationale
2. Step description — rationale
3. ...

## Risks
- Risk description — mitigation strategy

## Verification
- How to confirm the implementation satisfies the spec
- Specific test commands to run
```

**Gate**: `plan.md` is reviewed and merged. The merge signals that
implementation can begin. The agent receives `plan.md` as its primary
instruction document.

### Step 4: Maintain the Knowledge Base

After implementation completes, update organizational context documents
with any new patterns, decisions, or conventions that emerged. This closes
the loop — future `spec.md` sessions benefit from accumulated institutional
knowledge.

---

## Environment Caveats

- **Small changes**: For trivial fixes (typos, 1-line bugs), skip the full
  pipeline. The overhead isn't justified when scope is self-evident.
- **Existing spec systems**: If the team already uses Jira, Linear, or
  similar, `intent.md` can be generated *from* those tickets rather than
  replacing them. The value is in the structured format, not the specific tool.
- **Regulated environments**: In regulated industries, `intent.md` and
  `spec.md` may need to satisfy compliance documentation requirements.
  Treat them as formal records, not informal notes.

## Failure Modes

- **Skipping intent capture**: Jumping straight to spec or plan means the
  agent hallucinates the "why." This leads to technically correct code that
  solves the wrong problem.
- **Over-specifying intent**: Writing implementation details in `intent.md`
  constrains the design space prematurely. Intent should describe outcomes,
  not solutions.
- **Stale specs**: If `spec.md` isn't updated when requirements change
  mid-implementation, the plan diverges from reality. Treat spec changes
  as new intent → spec → plan cycles.
- **Ungated progression**: Skipping the merge-gate between stages removes
  the review checkpoint. An agent that plans from an unreviewed spec
  compounds errors.

## Cross-References

- [`requirements-driven-code-generation`](../requirements-driven-code-generation/SKILL.md) —
  Complements this skill at the implementation stage: once `plan.md` is
  approved, use WiseSpec's requirement decomposition to structure the
  actual coding work.
- [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) —
  Step 4's knowledge base maintenance aligns with WikiSkill's three-layer
  workspace pattern for persisting institutional knowledge.

## Sources

- The AI-Native SDLC Playbook, Claude Academy (Anthropic Applied AI)
  https://academy.claude.com/courses/ai-native-sdlc-playbook
