# Agent-Human Interaction Rules

> Research-backed guardrails for designing how agents present work to
> humans, solicit feedback, manage cognitive load, and structure
> handoff points. These rules should be active whenever building
> approval workflows, review interfaces, or human-in-the-loop systems.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

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

### DO: Ground SAST finding explanations in fired SARIF rule definitions and repository data-flow endpoints with demand-tiered disclosure

When integrating LLM agents into Static Application Security Testing (`SAST`), linter, or policy-compliance workflows, keep finding detection inside deterministic, auditable `SARIF` analysers (`Semgrep`, `CodeQL`, `Qodana`), deterministically pre-enrich CWE metadata and taint-trace step roles (`source`, `propagator`, `call`, `sanitizer`, `sink`) outside the model, and restrict the agent to a **read-only** repository and rule-inspection toolkit that verifies both the **fired rule definition** (`lookup_sast_rule`) and the **surrounding codebase endpoints** (`read_code`) before emitting a single structured response tiered by on-demand progressive disclosure rather than self-reported `beginner`/`intermediate`/`advanced` labels. Keep verbatim `SARIF` rule messages inspectable, pre-warm and cache explanations asynchronously, and leave true/false-positive judgment and patch application strictly with the human developer. Procedure: [`code-grounded-sast-finding-explanations`](../skills/code-grounded-sast-finding-explanations/SKILL.md).

**Scope:** Developer-facing IDE and PR explanation of already-emitted static-analysis findings; controlled AB/BA crossover user study (`N = 24` participants; `124` triage decisions, `64` blind-coded true-positive remediation proposals with $\kappa = 0.79$, and `24` closing interviews) plus two formative studies (`20`-participant survey and `19`-practitioner World Cafe workshop) evaluating `SAFE` (`Semgrep v1.160.0` across `CWE-23`, `CWE-78`, `CWE-79`, `CWE-89`, `CWE-918` on `Health-Doc-Exchange` with prewarmed cache, arXiv:2611.13041).

**Evidence**: Replacing a single-prompt audience-selector baseline (`SAFE-Blue`) with a demand-tiered UI backed by a 6-tool read-only repository and rule-lookup agent (`SAFE-Red`) more than doubled `correct` remediation proposals on true positives from 19% to 41% (participant-clustered cumulative-link odds ratio 2.6, 95% CI [0.93, 7.09], $p = .069$; 2.8, $p = .064$ with period and finding-set covariates), increased System Usability Scale (`SUS`) from 77.3 to 85.0 ($z = -2.55$, $p = .011$, $r = 0.62$), and raised perceived remediation actionability by +0.67 on a 5-point scale ($z = -2.53$, raw $p = .011$, Holm $p = .057$, $r = 0.73$), while perceived trust remained flat (+0.04)—showing that code-and-rule grounding improves comprehension and localization rather than uncritical belief. In closing interviews, 20 of 24 participants explicitly insisted that the developer, not the agent, judge findings and apply fixes.

Tension with "DO: Combine deterministic SAST with unrestricted AI security agents rather than substituting one for the other or pre-filtering vulnerability classes in the harness" (agent-sandbox-safety.md): that rule governs vulnerability *discovery* audits (running an unrestricted AI security agent alongside SAST to catch cross-file business-logic bugs SAST misses and verifying the union via PoCs); once a specific `SARIF` warning is surfaced to a developer for triage, constrain the *explanation* agent to the fired rule and read-only repo context without inventing verdicts or auto-applying patches.

See also: "DON'T: Treat agent output as implicit authorization" (above); "DON'T: Present all information at once" (above); "DO: Restrict architecture-documentation agents to read-only drift auditing and factual scaffolding while requiring humans to author rationale" (below).

> Source: Code-Grounded Agentic Explanations for Static Analysis Vulnerability Findings (arXiv:2611.13041)

### DON'T: Assign a standing devil's advocate persona in human-facing deliberation, or add a second deliberating AI near accuracy ceiling

When designing Multi-Agent Deliberation (`MAD`) interfaces to support human decision-makers, do not default to prompt-based every-round Devil's Advocate (`DA`) or uncalibrated `Expert` personas, do not present static multi-AI panels without inter-agent deliberation, and do not force two-AI active deliberation on easy or evidence-saturated items where a single multi-round AI is already near ceiling:
1. **Use multi-round deliberation over static multi-AI panels, and add a second cross-family AI only when single-AI accuracy has headroom**: Let agents deliberate across rounds (stopping early once consensus forms, since Round 1 captures the vast majority of human accuracy gains) rather than showing independent one-shot AI opinions (`Static`), and add a second heterogeneous model only when single-AI multi-round accuracy leaves room to improve.
2. **Avoid standing every-round `DA` prompts for general human decision accuracy**: Instructing one AI to oppose the other AI in every round creates persistent final-round disagreement and severe human underreliance on the accurate non-DA agent while increasing user frustration, perceived complexity, and confusion and lowering trust. Reserve adversarial counterargument mechanisms for selective triggers or domains prioritizing correlated-error auditing over overall accuracy.
3. **Escalate human engagement adaptively (`Static` $\to$ `MAD-Passive-Base` $\to$ `MAD-Active-Base`) and never rely on human-in-the-loop `MAD` alone to catch shared AI errors**: Active human participation improves human accuracy on harder tasks under information symmetry but raises user frustration across tasks and NASA-TLX mental demand/effort on evidence-dense tasks, while standard `MAD` leaves shared AI misconceptions unreduced (and can even induce new shared errors over independent panels).

**Scope:** Two randomized between-subjects Prolific studies of human-AI verification across 8 treatments (`Chatbot-R1`, `Chatbot`, `Static`, and $3 \times 2$ [`Base`, `Expert`, `DA`] $\times$ [`MAD-Active`, `MAD-Passive`]) using cross-family `GPT-5.4` + `Claude Sonnet 4.5` (`temperature = 1.0, top_p = 0.9`, 3 rounds, 200-word cap): `ReaLMistake` (`N = 401`, 6 items/user from 125 LLM-response verification items) and `Fact-check` (`N = 417`, 8 items/user from 48 PolitiFact/Snopes claims Jan 2025–Apr 2026 with Tavily web search) (arXiv:2611.14901).

**Evidence**:
- **Multi-round driver & single-AI ceiling (`RQ1`, `arXiv:2611.14901`)**: `MAD-Active-Base` beat `Chatbot-R1` (`0.733 ± 0.203` vs `0.605 ± 0.200`, $p = 0.007$), 3-round single-AI `Chatbot` (`0.639 ± 0.205`, $p = 0.027$), and 2-AI `Static` (`0.620 ± 0.223`, $p = 0.019$) on `ReaLMistake`, and beat `Chatbot-R1` (`0.948 ± 0.075` vs `0.849 ± 0.170`, $p < 0.001$) and `Static` (`0.748 ± 0.228`, $p < 0.001$) on `Fact-check`, but gave no accuracy advantage over `Chatbot` on `Fact-check` where single-AI accuracy was already near ceiling (`0.984 ± 0.042`) while raising mental demand ($p < 0.001$) and effort ($p < 0.001$). Round 1 delivered almost all human accuracy gains (`+0.156` vs `+0.021` after Round 1 on `ReaLMistake`, $p < 0.001$; `+0.227` vs `+0.057` on `Fact-check`, $p < 0.001$).
- **Standing `DA` harms accuracy and UX, while `MAD` misses shared errors (`RQ1–RQ3`)**: `DA` significantly lowered overall human accuracy on `ReaLMistake` (`0.577 ± 0.208` vs `0.678 ± 0.191` `Base` and `0.721 ± 0.185` `Expert`, $F(2,292) = 14.959, p < 0.001$) and `Fact-check` (`0.875 ± 0.145` vs `0.929 ± 0.104` `Expert`, $F(2,353) = 5.452, p = 0.005$) due to unresolved final disagreement (`0.587 / 0.650` and `0.287 / 0.415`) and `0.298–0.426` human underreliance on the accurate non-DA AI, while raising frustration ($p < 0.001$), complexity ($p = 0.002, p = 0.033$), and confusion ($p < 0.001, p = 0.017$) and lowering trust ($p = 0.007, p = 0.032$) vs `Base` (`Expert` gave no overall accuracy gain over `Base` and worsened frustration $p = 0.013$, confusion $p = 0.008$, and complexity $p = 0.006$). Although `DA` lowered all-AI error rate on `ReaLMistake` ($p = 0.005$) and helped users spot shared errors when the non-DA AI visibly flipped (`94.4%–100%` of cases, $p = 0.008$), standard `MAD-Active-Base` failed to reduce shared errors (`ReaLMistake` correlated-error accuracy $\hat{p} = 0.149$ vs `0.157` `Static`) and induced shared errors on `Fact-check` vs `0.000 ± 0.000` in `Static` ($p = 0.04$). Active engagement (`MAD-Active` vs `MAD-Passive`) improved accuracy on `ReaLMistake` (`0.698 ± 0.214` vs `0.619 ± 0.186`, $F(1,292) = 12.849, p < 0.001$) but not `Fact-check`, while raising frustration on both tasks ($p = 0.007, p = 0.003$; see [multi-agent-deliberation-human-ai-decision-making](../research-briefs/multi-agent-deliberation-human-ai-decision-making.md)).

Tension with "DO: Use heterogeneous, cross-family rosters for deliberation and joint verification" (multi-agent-coordination.md): cross-family rosters (`GPT-5.4` + `Claude Sonnet 4.5`) outperform static independent panels (`Static`) once multi-round interaction is enabled (`arXiv:2611.14901`), but relative to a single AI already deliberating across rounds (`Chatbot`), adding a second cross-family AI improves human accuracy only when single-AI accuracy leaves headroom (`ReaLMistake` `0.733` vs `0.639`, $p = 0.027$), adding cognitive load without accuracy gain near ceiling (`Fact-check` single-AI `0.984`).

Tension with "DO: Trigger mid-trace retrieval and specialist recruitment via an external non-answering Challenger with isolated channels" (multi-agent-coordination.md) and "DO: Route requirement-to-code traceability by evidence locality and use symmetric Trace/Non-Trace swap debate instead of lexical retrieval or one-way critics" (multi-agent-coordination.md): channel-isolated non-answering Challengers (`arXiv:2611.05393`) and judge-adjudicated `Trace`/`Non-Trace` partition-swap debates (`arXiv:2611.09162`) improve automated reasoning and traceability because dissent is resolved or scoped before final output, whereas exposing a human decision-maker directly to a prompt-only every-round Devil's Advocate (`arXiv:2611.14901`) leaves `0.287–0.650` unresolved Round-3 disagreement, causing human underreliance on the accurate peer AI and lower decision accuracy and trust.

Tension with "DO: Dynamically calibrate consensus entropy and weight peer influence by evidence grounding in multi-agent debate" (recursive-improvement.md): `R^2-MAD` and `CollabFlow` (`arXiv:2609.03619`, `arXiv:2609.38662`) inject verified counter-evidence dynamically when consensus entropy collapses, whereas an unconditional every-round `DA` persona (`arXiv:2611.14901`) opposes accurate answers indiscriminately—helping users detect rare shared AI errors ($p = 0.008$) only at the cost of lower overall human accuracy ($p \le 0.005$) and higher frustration.

See also: "DON'T: Assume multi-agent debate eliminates shared misconceptions" (multi-agent-coordination.md); "DON'T: Present all information at once" (this file); "DO: Reserve human review for judgment, not verification" (this file).

> Source: Understanding the Effects of Multi-Agent Deliberation for Human-AI Decision-Making (arXiv:2611.14901)

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

## Accessible UI Hierarchy, Generative Diagrams & CUA Overlays

### DO: Group flat mobile accessibility trees into shallow spatial-functional hierarchies and refine multi-granularity labels in a single LLM request

Raw mobile accessibility trees flatten composite visual cards and toolbars into long linear focus sequences (averaging $18.7 \pm 16.5$ swipes to reach a target across 50 commercial Android pages, with 34.0% of pages suffering functional-unit focus interruptions and 28.8% of focus stops carrying non-informative labels). Reconstruct a 3-level hierarchy (Page Root $\rightarrow$ Functional Units $\rightarrow$ Atomic Elements) by combining spatial bounding-box containment, XML shared parenthood, and row/column alignment, then enforce three shallow-hierarchy simplification rules: (1) strip unlabelled containers covering $\ge 80\%$ of the screen, (2) cap XML sibling grouping at 2 rounds, and (3) flatten units with $< 3$ children. Finally, pass the entire simplified page tree in a single structured LLM call to generate a 3-area page summary, functional unit labels with 1–2 decision attributes (e.g., product name + price), and context-repaired leaf labels, while preserving a flat-traversal bypass for simple or familiar screens. Procedure: [`mobile-spatial-accessibility-grouping`](../skills/mobile-spatial-accessibility-grouping/SKILL.md).

**Scope:** Mobile screen-reader transformation (`SeeR`), BLV accessibility interfaces ($N=10$ BLV users, 37 paired task attempts), and GUI perception across 50 commercial Android pages (10 apps, 1,858 focus stops, 1,324 semantic actions, arXiv:2611.02410).

**Evidence**: Across 50 Android pages (`arXiv:2611.02410`), `SeeR` constructed hierarchies in 5.8 ms median latency (0.996 pairwise precision, 0.711 recall, 0.769 F1), cut non-informative focus stops by 82.1% (from 28.8% [535/1,858] to 5.1% [82 stops]) in a single `deepseek-v4-flash` pass (median 3.4 s, 2,535.4 prompt + 273.8 completion tokens), and reduced target navigation distance by 52.7% ($18.7 \pm 16.5$ to $8.8 \pm 6.2$ steps, $p < .001$). In a within-subjects study with 10 BLV users (37 paired task attempts), `SeeR` reduced visited nodes by 45.8% (17.9 to 9.7, $p = .004$) and task completion time by 34.2% (58.2 s to 38.3 s, $p = .014$).

> Source: Spatial Organization Is Accessibility Structure: Hierarchical Screen Reading of Mobile UIs (arXiv:2611.02410)

### DO: Decouple editable diagram generation into Semantic-Style-Layout specs and use bottom-up geometric text sizing before top-down coordinate layout

One-shot prompting of an LLM to emit complete canvas JSON simultaneously entangles entity extraction, styling, and 2D coordinate math, resulting in severe node overlaps and text overflow. Decouple the diagram into a Semantic Graph $G = (\mathcal{V}, \mathcal{E})$ (built entity-first, relation-last), a closed Style Schema $S$ (mapped strictly to discrete canvas enums), and a Layout Configuration $L$. Have specialized agents emit strategy specifications ($\tilde{G}, \tilde{S}, \tilde{L}$) first, invoke a deterministic font-aware Geometric Size Estimator tool bottom-up to calculate collision-free leaf and container dimensions before assigning top-down recursive $(x, y)$ coordinates, and refine rendered snapshots via surgical VLM tool calls rather than full-canvas regeneration. Procedure: [`editable-semantic-diagram-generation`](../skills/editable-semantic-diagram-generation/SKILL.md).

**Scope:** Automated generation of object-level editable diagrams (`tldraw`) across CanvasBench (`2,260` validated diagrams across `21` diagram types and `30` domains; `210`-sample test set evaluated on `GPT-5.2`, `Gemini-3-Pro`, and `Qwen3-VL-Plus`, arXiv:2604.09568).

**Evidence**: On `CanvasBench` (`arXiv:2604.09568`), `EvoDiagram` improved Visual Space Balance ($V_{\text{SB}}$) over one-shot schema prompting from 1.782 to 2.705 (+51.8%) on `GPT-5.2`, from 2.312 to 3.010 on `Gemini-3-Pro`, and from 1.705 to 2.695 on `Qwen3-VL-Plus`, while boosting Cognitive Comprehension Accuracy ($G_{\text{CA}}$) from 3.146 to 3.419 (`GPT-5.2`) and 2.224 to 3.018 (`Qwen3-VL-Plus`). Removing the multi-agent decomposition collapsed Space Balance back to 1.891 (`GPT-5.2`), 2.435 (`Gemini-3-Pro`), and 1.884 (`Qwen3-VL-Plus`).

> Source: EvoDiagram: Agentic Editable Diagram Creation via Design Expertise Evolution (arXiv:2604.09568)

### DO: Restrict architecture-documentation agents to read-only drift auditing and factual scaffolding while requiring humans to author rationale

To prevent **cognitive debt** (erosion of a team's shared mental model of how the system works) and **intent debt** (loss of design rationale, constraints, and discarded alternatives), never allow coding agents to autonomously author or overwrite architectural rationale and narrative walkthroughs. Restrict documentation-maintenance skills to **read-only staleness/drift audits** (reporting one finding at a time against git history) and **factual graph scaffolding** (proposing only `label`, `type`, `file path`, `edges`, and candidate stop orders paired with Socratic questions), preserving **productive friction** by requiring human developers to articulate the "why" and docent commentary in their own words.

**Scope:** Six-month longitudinal deployment of Cognitive Tours (`59` socio-technical waypoints, `73` named relationships, `5` curated narrative tours, and 4 read-only Claude Code skills: `/audit-waypoints`, `/audit-tours`, `/suggest-waypoint`, `/suggest-tour`) in an AI-assisted software development project (arXiv:2611.08456).

**Evidence**: In `Cognitive Tours` (`arXiv:2611.08456`), auditing the repository after a high-velocity AI coding session (`28` commits since the prior checkpoint, including `>20` commits in a single evening) via `/suggest-waypoint` surfaced and ranked `#1` an unrecorded architectural shift (*"One site and database per team"*) that directly contradicted an existing `Accepted` Architecture Decision Record (`ADR 007`). Withholding AI-generated rationale and prompting the human author with Socratic questions forced explicit reconciliation of the contradicted ADR and prevented silent intent drift (see [cognitive-tours-understanding-deliverable-swe](../research-briefs/cognitive-tours-understanding-deliverable-swe.md)).

> Source: Cognitive Tours: Making Understanding a Deliverable in AI-Assisted Development (arXiv:2611.08456)

### DO: Separate build-time CUA visual grounding from runtime pixel template matching when overlaying Generative UI patches on desktop applications

Confine expensive Vision-Language Model (VLM) screen exploration (`OmniParser v2`, coordinate-grounding VLMs) to an isolated build-time phase that exports a declarative `JSON` binding manifest (coordinates, glyph templates, shortcuts) decoupled from `TypeScript` UI logic. At runtime, synchronize application state using lightweight local luminance text tags and zero-mean normalized cross-correlation (ZNCC) glyph template matching, and inject synthetic actions via background PID-targeted OS events (`CGEvent.postToPid`) rather than hijacking the user's foreground cursor.

**Scope:** Interface Quilt desktop GUI modification and Generative UI overlay architecture evaluated across 5 macOS `26.5.2` applications (`PowerPoint`, `Affinity`, `Fusion`, `Slack`, `Overleaf`) using `OmniParser v2`, `Apple Vision OCR`, and `Holo2-8B-bf16` (arXiv:2611.01891).

**Evidence**: In `Interface Quilt` (`arXiv:2611.01891`), decoupling `TypeScript` patch logic from `JSON` bindings allowed interactive overlays (such as radial *Marking Menus*) to port directly from `PowerPoint` to `Overleaf` by regenerating only the `JSON` binding file, while runtime ZNCC glyph matching and `CGEvent.postToPid` enabled real-time reactive state binding and background cross-app actuation (`PowerPoint` driving `Affinity`) without VLM critical-path latency or focus stealing (see [interface-quilt-cua-generative-ui](../research-briefs/interface-quilt-cua-generative-ui.md)).

> Source: Interface Quilt: Modifying Applications with Computer Use Agents and Generative UI (arXiv:2611.01891)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`intent-driven-sdlc-planning`](../skills/intent-driven-sdlc-planning/SKILL.md) — Structured intent → spec → plan pipeline for human-agent planning
- [`agentic-review-deploy-loop`](../skills/agentic-review-deploy-loop/SKILL.md) — Layered review pipeline with escalation triggers
- [`requirements-driven-code-generation`](../skills/requirements-driven-code-generation/SKILL.md) — Requirement decomposition for evaluable specifications
- [`persistent-agent-migration`](../skills/persistent-agent-migration/SKILL.md) — Preserving agent identity across interaction sessions
- [`mobile-spatial-accessibility-grouping`](../skills/mobile-spatial-accessibility-grouping/SKILL.md) — Spatial-functional hierarchy reconstruction and single-pass multi-granularity LLM labeling for mobile screen readers (`SeeR`)
- [`editable-semantic-diagram-generation`](../skills/editable-semantic-diagram-generation/SKILL.md) — Decoupled Semantic-Style-Layout specification and bottom-up geometric text sizing for editable vector diagrams (`EvoDiagram`)
- [`code-grounded-sast-finding-explanations`](../skills/code-grounded-sast-finding-explanations/SKILL.md) — Read-only repository & SARIF rule-grounded explanations with demand-tiered disclosure (`SAFE`)

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
- SeeR (Spatial Organization Is Accessibility Structure): arXiv:2611.02410
- EvoDiagram (Agentic Editable Diagram Creation via Design Expertise Evolution): arXiv:2604.09568
- Cognitive Tours (Making Understanding a Deliverable in AI-Assisted Development): arXiv:2611.08456
- Interface Quilt (Modifying Applications with CUAs and Generative UI): arXiv:2611.01891
- SAFE (Code-Grounded Agentic Explanations for SAST Findings): arXiv:2611.13041
- Understanding the Effects of Multi-Agent Deliberation for Human-AI Decision-Making: arXiv:2611.14901
