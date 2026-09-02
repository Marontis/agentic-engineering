---
name: requirements-driven-code-generation
description: >
  Systematic requirements engineering and quality assessment for coding
  agents prior to implementation. Decomposes raw tasks into formal contracts,
  evaluates specification quality, and synthesizes requirement-bound tests
  before writing code. Derived from WiseSpec (arXiv:2609.00568).
source: https://arxiv.org/abs/2609.00568
---

# Requirements-Driven Code Generation

Use this skill when tackling complex software engineering tasks, ambiguous
feature requests, or multi-component coding problems where raw user prompts
lack necessary specification details.

## When to Use

- A coding task has ambiguous, incomplete, or high-level requirements
- Complex repository-level issues involving multiple interacting modules
- Preventing agents from hallucinating unintended assumptions or jumping
  prematurely into source code modifications
- High-stakes development where test-driven and contract-driven verification
  is mandatory

## Core Insight

Most coding agent failures stem from **specification defects**, not code
synthesis defects. When given vague instructions like "fix the auth timeout",
agents jump immediately into editing files, hallucinating requirements that
conflict with the broader architecture.

Separating development into an explicit three-stage pipeline—**Requirement
Generation**, **Requirement Quality Assessment**, and **Spec-Driven
Implementation**—significantly boosts pass rates on complex benchmarks by
resolving ambiguities before code is touched.

---

## Procedure

### Step 1: Decompose Raw Task into Structured Specification

Before inspecting or editing source files, translate the user prompt into a
formal requirement specification with four mandatory dimensions:

```markdown
### Requirement Specification: [Feature / Issue Name]

1. **Functional Intent**:
   - Exact expected input/output transformations and behavioral state changes.
2. **Preconditions & Invariants**:
   - System state required before execution; invariants that must hold throughout.
3. **Boundary Conditions & Edge Cases**:
   - Empty collections, network timeouts, invalid payloads, concurrent calls.
4. **Non-Goals / Explicit Constraints**:
   - Unrelated files that must NOT be modified; backward compatibility bounds.
```

### Step 2: Run Requirement Quality Assessment (RQA)

Score the synthesized specification against three quality gates:

| Quality Dimension | Verification Question | Action if Failed |
|:---|:---|:---|
| **Completeness** | Are all input types, return values, and failure paths specified? | Query user or examine codebase type signatures to fill gaps. |
| **Clarity** | Are terms concrete and measurable (e.g., "timeout within 500ms" vs. "fast")? | Replace subjective adjectives with numerical or structural bounds. |
| **Consistency** | Does any requirement contradict existing repository architectural patterns? | Review existing module contracts and reconcile discrepancies. |

If the overall RQA score fails, refine the specification before writing any
code.

### Step 3: Synthesize Requirement-Bound Tests First

Generate automated tests directly from the ratified specification before
authoring the implementation:

1. Write one test case per functional requirement and edge case identified in
   Step 1.
2. Run the newly generated test suite to confirm it **fails for the right
   reason** against the current codebase (proving the test is sensitive to the
   missing feature or bug).

### Step 4: Implement Minimal Targeted Code

Implement the code strictly to satisfy the validated specification and pass
the requirement-bound tests:

1. Keep edits localized to the declared target scope.
2. Verify all requirement tests pass.
3. Run the broader regression test suite to confirm zero regressions in
   adjacent features.

---

## Environment Caveats

- **Legacy or Undocumented Codebases**: When official specifications are
  missing, extract implicit requirements by inspecting existing unit tests and
  type stubs before drafting the new spec.
- **Trivially Simple Edits**: For 1-line syntax fixes or typo corrections,
  skip full formal specification to avoid unnecessary token and latency
  overhead.

## Failure Modes

- **Premature Implementation**: Editing source code immediately without
  clarifying ambiguous requirements, resulting in throwaway work and broken
  invariants.
- **Vague Edge Cases**: Listing "handle errors gracefully" instead of defining
  specific exception types, HTTP status codes, or fallback payloads.
- **Unverified Tests**: Writing tests that pass even on the buggy codebase,
  providing a false sense of security.

## Cross-References

- [`behavior-aware-verification`](../behavior-aware-verification/SKILL.md) —
  Validating behavioral invariants during code generation.
- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) —
  Executing tests in a rollback-capable sandbox environment.

## Sources

- WiseSpec: Requirements-Driven Agents for Code Generation (arXiv:2609.00568)
