---
name: agentic-requirements-reverse-engineering
description: >
  Recover a business requirements document (user journeys, business rules
  with provenance, gap analysis, Given/When/Then acceptance criteria, risk
  register) from undocumented code, tests, configuration, and docs. Uses
  a pipeline of narrow agents that extract with static analysis first,
  corroborate each finding across at least two sources, resolve conflicts
  by a fixed evidence precedence, and escalate to humans only through
  structured decision packages. Use before migrating, extending, or
  auditing a legacy or undocumented service.
  Derived from "From Code to Requirements: Agentic Reverse Engineering of
  Business Rules at Enterprise Scale" (arXiv:2609.22719).
source: https://arxiv.org/abs/2609.22719
---

# Agentic Requirements Reverse Engineering

Use this skill when a service's behavior lives only in its code, tests,
and configuration, and you need a traceable requirements baseline before
you change or migrate it.

## When to Use

- Legacy migration where undiscovered edge cases stall the programme
- Modern microservices whose "spec" is the working code
- Compliance or audit requests for the business rules a system enforces
- Producing a machine-readable behavioral baseline that downstream coding
  and testing agents can consume (see
  `skills/requirements-driven-code-generation/SKILL.md`)

## Core Insight

A single prompt over a whole component fills gaps with plausible invention.
Instead, split the work into narrow agents, each with a deterministic tool
belt and an output contract. Let static analysis (AST queries, pattern
rules, schema diffs, test mining) do the extraction. Reserve the LLM for
translation into plain language, conflict resolution, and synthesis over
curated inputs. Resolve conflicts with a fixed precedence (**test evidence
over business rule over journey**) so the document can be locked
deterministically.

**Evidence** (one enterprise Java programme; 14 instrumented services):

- 280 journeys and 1,612 rules extracted, with 327 test cases mapped
- Average generation time 8.78 minutes per service, about 47,694 tokens per
  service (about $0.07 at Haiku pricing)
- 115 distinct extracted rules each matched a rule that developers had
  independently cited in production-defect triage notes (over 100 defects
  across 5 services)
- The claimed >98% cost reduction compares against a *modeled* manual
  baseline, and the authors call it an order-of-magnitude indication, not a
  controlled measurement

---

## Procedure

### 1. Human-Defined Scope (Discovery Agent)

A human maps the named service to its candidate repositories and sources
(code, tests, configuration, API specifications, tickets, wiki pages). The
discovery agent catalogs the artifacts and scores each for freshness and
authority. It maps upstream and downstream dependencies and flags anything
that looks out of scope. **An ambiguous boundary pauses the pipeline for a
human decision.** Scope is never silently expanded.

### 2. Journeys and Rules in Parallel

Run both agents from the scope document only. Neither reads the other's
output.

- **Journey agent**: find endpoints and routes by static scan, trace logic
  by AST, parse docs, and **mine the test suite**. Regression tests encode
  the edge and error paths teams actually validated. Extract actors from
  authorization checks, not assumptions. Output: a typed journey inventory
  (happy, alternate, error, and edge paths per actor and channel) and a
  test-to-journey coverage matrix.
- **Rules agent**: run AST and Semgrep-style patterns for conditionals,
  validation guards, eligibility checks, and threshold constants. Return
  each with its file location and context. The LLM then states the rule as
  actor, condition, and outcome. Flag PII, financial, and regulatory logic.

Every rule is emitted with provenance, for example:

```json
{ "rule_id": "R-014",
  "statement": "Requests from an unsupported region are rejected before pricing runs",
  "source": ["EligibilityService.java:118", "regions.yaml"],
  "corroborated_by": ["RegionValidatorTest"],
  "confidence": "HIGH", "regulatory_flag": false,
  "journeys": ["J-02", "J-05"], "assumptions": [] }
```

House rule: **accept a finding only when at least two independent sources
support it.** Otherwise record it as an assumption with lowered confidence.

### 3. Gap Analysis Against the Target

If a target-state specification or schema exists, diff the legacy data
model and behavior against it. Classify each item as *clean map*,
*transform needed*, *missing*, or *deferred*, and risk-score it by business
impact and customer exposure. If no target specification exists, report
only the baseline and flag the absence. Blocking gaps escalate.

### 4. Synthesis and Lock (Quality Gate)

One agent cross-examines all upstream outputs for conflicts, coverage holes,
confidence-chain violations, and assumption chains. Resolve in this order:

1. Knowledge-layer precedent and evidence weighing
2. Fixed precedence: **test evidence ≻ business rule ≻ journey** (amend the
   journey, keep the rule, add the exception branch)
3. Human escalation, only for business judgment. Send a decision package
   containing the conflict statement, the evidence on each side, a
   recommendation, and **one answerable question**

Log every resolution with its rationale, sources, and confidence. Then lock
the document in two forms: human-readable and machine-readable JSON.

### 5. Acceptance Criteria and Risk (Parallel, After Lock)

- Build each criterion from the intersection **Rule (Given) + Journey step
  (When) + Test or gap closure (Then)**, emitted as Gherkin. A behavior
  counts as expected only where all three meet. Compare against the
  existing regression suite and propose the missing tests.
- Build a risk register from dependencies and regulatory flags, scored by
  likelihood and impact.

### 6. Validate Against Independent Evidence

Test-to-journey mapping shows only internal consistency, because the
journey agent already read the tests. For an independent check, sample
production-defect triage notes (written by engineers for another purpose)
and match the rule each defect cites against the extracted catalog.
Escalate unmatched cases to a human. Report the corroborated count, and
where possible the uncorroborated count as well.

### 7. Keep State Auditable

Use a two-layer store. The first layer is a rolling summary that every
agent reads on activation. The second is an append-only event log (finding,
decision, tool call, and conflict, with agent, timestamp, sources, and
confidence). Later agents fetch named artifacts **by key, not by similarity
search**. On re-runs, retrieve prior rules and decisions so that only the
changed code is reprocessed.

---

## Environment Caveats

- Static-first extraction under-represents behavior resolved at runtime
  (dependency injection, reflection, dynamic proxies) and logic outside the
  application (stored procedures, triggers, message routing). Coverage
  counts do not prove completeness.
- Without a usable test suite, cap the confidence of affected findings and
  report the missing suite as a risk.
- The paper's evidence is a single Java programme plus one legacy pilot.
  There are no precision or recall figures, and defect corroboration used
  an LLM judge.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:--|:--|:--|
| Fluent but ungrounded rules | LLM given raw repository content | Static extraction first; two-source corroboration (step 2) |
| Silent conflict resolution | Synthesis picks one source quietly | Fixed precedence plus a logged rationale (step 4) |
| Scope creep | Agent pulls in adjacent services | Human-defined scope; boundary escalation (step 1) |
| Circular validation | Test-to-journey mapping reported as accuracy | Independent defect corroboration (step 6) |
| Context overflow | Orchestrator threads all state | Keyed artifact reads from the store (step 7) |
| Escalation fatigue | Vague human questions | One-question decision packages (step 4) |

---

## Cross-References

- `skills/requirements-driven-code-generation/SKILL.md`: the forward
  direction, turning requirements into contracts and tests
- `skills/intent-driven-sdlc-planning/SKILL.md`: intent, spec, and plan
  artifacts that a locked requirements document can seed
- `skills/governed-knowledge-graph/SKILL.md`: provenance-carrying knowledge
  layer for cross-run reuse
- `rules/adk-workflow-architecture.md`: "DO: Evaluate deterministic policy
  checks BEFORE invoking generative models"
- `rules/skill-system-design.md`: "DO: Keep deterministic steps in code and
  explicit graph edges; delegate to LLMs only for reasoning"
- `rules/agent-human-interaction.md`: "DO: Present structured, inspectable
  choices at approval gates"

## Sources

> Agrawal, Das, L et al., "From Code to Requirements: Agentic Reverse
> Engineering of Business Rules at Enterprise Scale" (arXiv:2609.22719),
> Sep 2026.
