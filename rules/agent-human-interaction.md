# Agent-Human Interaction Rules

> Research-backed guardrails for designing how agents present work to
> humans, solicit feedback, manage cognitive load, and structure
> handoff points. These rules should be active whenever building
> approval workflows, review interfaces, or human-in-the-loop systems.

---

## Proposal Design

### DO: Design proposals for evaluability, not just acceptability

When an agent presents options to a human for approval, optimize for
the human's ability to *evaluate* the proposal — not just for the
probability of acceptance. Highly acceptable proposals and informative
preference probes rarely coincide. Agents that optimize only for
immediate acceptance systematically converge to suboptimal long-term
outcomes.

**Evidence**: under a Bayes-adaptive planning framework (ProSE), agents
that explicitly plan exploratory proposals when evaluation costs are
low significantly improve downstream task alignment compared to agents
that greedily optimize for acceptance rate.

> Source: ProSE: Evaluability-Aware Assistance (arXiv:2609.02242)

### DO: Present structured, inspectable choices at approval gates

At every approval gate (plan review, spec review, deployment), the
agent should present choices as structured, easily inspectable
artifacts — not free-form prose. Structured choices reduce cognitive
evaluation fatigue and surface decision-relevant dimensions that prose
obscures.

Use:
- **Tables** for multi-dimensional comparisons
- **Checklists** for verification steps
- **Diffs** for proposed changes
- **Decision matrices** when tradeoffs exist

> Source: arXiv:2609.02242

---

## Cognitive Load Management

### DON'T: Present all information at once

When context is large (full codebase, complete analysis, long
trajectory), the agent — not the human — should manage context
window presentation. Show only what is needed for the current
decision; keep everything else addressable but hidden.

Principles:
- **Partial exposure**: render views incomplete on purpose; what's
  held back stays addressable via follow-up
- **Progressive disclosure**: summary first, details on request
- **Decision-scoped context**: include only information that changes
  the decision at hand

**Evidence**: String OS states partial exposure as a design principle
(runtime-managed views, with held-back content retrievable via
follow-up commands). The paper reports no measurement comparing it with
full-context presentation, for agents or for humans
(research-briefs/agentic-os-interface-design.md).

**Scope:** human-facing presentation of agent output (review views,
approval gates, reports); a design principle, not a measured result.
Not evidence for how to manage an agent's own context window.

Tension with 2609.20804 (research-briefs/empirical-harness-design-study.md):
for coding agents, making elided context recoverable added machinery
models rarely used and gave no accuracy gain; the benefit of context
management came from preventing context overflow. For an agent's own
context, prefer rule-based elision then summarization; do not add
recoverable-elision machinery expecting accuracy gains.

> Source: String OS (arXiv:2608.28027); An Empirical Study of Harness Design for Coding Agents (arXiv:2609.20804)

### DO: Adapt response granularity to query complexity

Not all queries deserve the same level of detail. Match response
depth to question complexity:

| Query Complexity | Response Strategy |
|:----------------|:-----------------|
| **Factual recall** | Direct answer, minimal context |
| **Comprehension** | Answer with explanation |
| **Application** | Answer with worked example |
| **Analysis/Synthesis** | Structured breakdown with tradeoffs |

**Evidence**: prompt-level cognitive conditioning (classifying queries
by Bloom's Taxonomy and adapting response parameters accordingly)
reliably alters response granularity and structure without corrupting
factual grounding, across 2,910 evaluated responses.

> Source: Hybrid Micro-Level Personalization (arXiv:2609.03402)

---

## Escalation & Handoff

### DO: Define explicit escalation triggers, not vague guidelines

Every agent workflow should declare concrete, testable conditions
under which the agent stops and hands off to a human. Vague
guidelines like "escalate when uncertain" are useless — agents
can't reliably self-assess uncertainty. Instead, define structural
triggers:

- **Scope triggers**: changes to files outside declared scope
- **Risk triggers**: modifications to auth, crypto, PII, or
  financial calculation code
- **Novelty triggers**: patterns not covered by existing guidelines
  or skills
- **Confidence triggers**: when the agent's top-k proposals are
  close in score (low decisiveness)
- **Impact triggers**: changes affecting >N files, >N users, or
  >$N in cost

> Source: The AI-Native SDLC Playbook (Claude Academy)

### DON'T: Treat agent output as implicit authorization

A diagnosis, a report, or a recommendation authorizes nothing by
itself. An agent that identifies a bug is not authorized to fix it.
An agent that finds a security vulnerability is not authorized to
patch it. An agent that recommends a merge is not authorized to merge
it. Evidence and authorization are separate concerns — conflating
them lets agents quietly widen their own scope by framing actions as
"obvious next steps" from their own findings.

This applies at every level:
- **Diagnosis ≠ permission to remediate**: the agent must explicitly
  request authorization before acting on its own findings
- **Recommendation ≠ approval**: a proposal that passes all automated
  checks still requires the explicit gate before execution: a human
  approval, or a pre-granted, bounded scope that already covers the
  action (see Scope below). Passing checks is not itself that gate
- **Standing autonomy never quietly widens**: an agent authorized to
  fix lint errors is not authorized to refactor the surrounding code,
  even if the refactor would "obviously" improve it

**Scope:** agents acting on their own findings in a human-supervised
workflow (FirstMate design principle; no benchmark). A pre-granted,
bounded scope counts as the explicit gate: an autonomous loop that
fixes only what an operator authorized in advance (e.g. a `mode="task"`
remediation node limited to its declared tools and output schema) is
already authorized for that scope. Sanction or revocation powers over
other agents need their own explicit grant.

Tension with "Use `mode="task"` with typed `finish_task` for autonomous
remediation loops" (adk-workflow-architecture.md) and "Apply commons
governance principles to shared agent resources"
(multi-agent-coordination.md): those loops act without a per-action
human gate, and they stay consistent with this rule only while they
act inside the scope they were granted up front.

See also "Let a stored user approval outlive the context it was granted
in" (below): a pre-granted scope stays a valid gate only while the
context it was granted in still holds.

> Source: FirstMate agent distro (github.com/kunchenguid/firstmate),
> VISION.md: "Evidence is never authorization"

### DON'T: Let a stored user approval outlive the context it was granted in

When the runtime remembers an "allow" (always allow, don't ask again,
session-wide grants), store it with the task, the exact resource and
anything else that changes the action's effect, re-check those at every
authorization point, and ask again when a change alters what the action
does. Default grant lifetime to the current task. Exact-resource
matching narrows replay but does not remove it.

**Scope:** approval-gated tool-use agents that persist grants across
tasks or sessions; AgentDojo v1.2 (508 cases; GPT-4.1,
Gemini-3.1-Flash-Lite, Qwen3-14B, DeepSeek-V4-Pro, Llama-3.3-70B,
Claude-Sonnet-5) and 55 Terminal-Bench cases on live Codex, Gemini CLI
and Goose.

**Evidence**: tool-level grant retention gave attack success
0.114–0.351 against 0 in a fresh approval state (up to +35.1 points);
silent execution of approval-gated actions rose from 0 to 0.982–1.000
after 64 benign tasks; exact-resource matching left 0.012–0.039. On live
agents replay raised success by 24.9 points on average, and Goose
admitted every approval-gated probe action silently after one benign
task. Task-bound authorization removed the effect (PAuth 0; Progent at
most 0.009). See
[`residual-auth-state-preservation`](../skills/residual-auth-state-preservation/SKILL.md)
Step 5.

> Source: When Consent Outlives Context: Residual Authority Replay in Long-Lived Agents (arXiv:2609.33910)

### DON'T: Let the human become the transport layer between agents

When multiple agents need to collaborate, humans should not serve as
the copy-paste intermediary (copying output from Agent A, pasting
into Agent B). This loses provenance, execution context, and semantic
constraints. Design direct agent-to-agent communication channels with
human oversight, not human intermediation.

**Evidence**: the "human as transport layer" anti-pattern is the
primary failure mode in multi-agent collaboration. The Civilization
Framework's Embassy Protocol eliminates this by providing asynchronous
store-and-forward messaging between agent systems under sovereign
policy constraints.

> Source: The Civilization Framework (arXiv:2609.03425)

---

## Review & Approval

### DO: Reserve human review for judgment, not verification

Humans are expensive, slow, and prone to fatigue. Don't waste human
review bandwidth on checklist items that an automated reviewer can
handle. Structure the review pipeline so that:

1. **Automated checks** (linters, type checkers, tests) handle
   mechanical correctness
2. **Agentic review** handles pattern matching, style conformance,
   and checklist compliance
3. **Human review** handles architecture decisions, security
   implications, novel patterns, and regulated code

The goal is to ensure that every item reaching a human reviewer
genuinely requires human judgment.

> Source: The AI-Native SDLC Playbook (Claude Academy)

### DO: Make agent reasoning auditable and navigable

When a human reviews agent work, they need to understand *why* the
agent made each decision, not just *what* it did. All agent work
products should include or link to:

- The specification or intent document that motivated the work
- The plan that structured the implementation
- Key decision points and the reasoning behind each choice
- What was explicitly excluded and why

This enables meaningful review rather than "looks fine, LGTM" rubber-
stamping.

> Source: The AI-Native SDLC Playbook (Claude Academy)

---

## Trust Calibration

### DON'T: Assume stable safety behavior across interaction modes

The same model with the same safety training can exhibit different
protective behaviors depending on how it's invoked (API, chat, agent
loop), what system prompt it receives, and what tools are available.
Multi-turn interaction history also alters safety refusal thresholds
asymmetrically across model providers.

The effect is per model, not per provider family: test multi-turn
refusal behaviour on each model you deploy, and re-test when you swap
models, even within one provider.

**Scope:** nine frontier production models from Anthropic, OpenAI and
Google, single door-in-the-face sequences (2609.02707).

**Evidence**: sequential retreat (refusing an extreme request, then
receiving a smaller one) raised compliance on Claude Opus 5 (65.8% vs
29.3% when asked directly) but backfired on Claude Haiku 4.5, GPT-5.6
sol and Gemini 3.1 Pro (-15.5 to -23.0 points; GPT-5 mini and Gemini 3
Flash showed no significant effect), so two models from
one provider reacted in opposite directions
(research-briefs/door-in-the-face-model-refusals.md). Reframing
refused operational requests as requests for conceptual explanations
removed refusals in 263/265 cases (99.2%).

See also: rules/agent-sandbox-safety.md — "DON'T: Assume uniform safety refusal behavior across model families in multi-turn dialogues"; rules/agent-sandbox-safety.md — "DON'T: Assume safety transfers across deployment contexts" (tool-mediated refusal evidence: 2609.35117, refusal falls once the tool schema is visible)

> Source: Door-in-the-Face Refusal Behaviour (arXiv:2609.02707),
> Not the Same Protector (arXiv:2608.29136)

### DON'T: Let users authenticate to agents via conversation

Never allow an LLM to generate, administer, or evaluate its own
identity verification challenges. When untrusted users claim
privileged roles ("I am your developer"), models frequently generate
arbitrary technical challenges, evaluate answers, and issue pseudo-
credentials without external attestation.

**Scope:** chat models (ChatGPT, Claude, Qwen, Mistral, Llama per the brief) under unsupported developer-identity claims (arXiv:2609.03247); no failure rates recorded in this repo.

**Evidence**: across frontier models, multiple architectures collapsed
the challenge-generator, evidence-evaluator, and decision-maker roles,
erroneously verifying developer identity based solely on technical
dialogue. Authentication must derive from external cryptographic
tokens or environment capability leases.

See also: rules/agent-sandbox-safety.md — "DON'T: Permit dialogue-driven identity authentication or self-issued credentials"

> Source: Conversational False Authentication (arXiv:2609.03247)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`intent-driven-sdlc-planning`](../skills/intent-driven-sdlc-planning/SKILL.md) — Structured intent → spec → plan pipeline for human-agent planning
- [`agentic-review-deploy-loop`](../skills/agentic-review-deploy-loop/SKILL.md) — Layered review pipeline with escalation triggers
- [`requirements-driven-code-generation`](../skills/requirements-driven-code-generation/SKILL.md) — Requirement decomposition for evaluable specifications
- [`persistent-agent-migration`](../skills/persistent-agent-migration/SKILL.md) — Preserving agent identity across interaction sessions

## Sources

- ProSE: arXiv:2609.02242
- String OS: arXiv:2608.28027
- Empirical Study of Harness Design for Coding Agents: arXiv:2609.20804
- Hybrid Micro-Level Personalization: arXiv:2609.03402
- The Civilization Framework: arXiv:2609.03425
- Door-in-the-Face Refusal Behaviour: arXiv:2609.02707
- Not the Same Protector: arXiv:2608.29136
- Conversational False Authentication: arXiv:2609.03247
- The AI-Native SDLC Playbook: https://academy.claude.com/courses/ai-native-sdlc-playbook
- FirstMate agent distro: https://github.com/kunchenguid/firstmate
- When Consent Outlives Context: arXiv:2609.33910
