---
name: intent-ltl-mcp-orchestration
description: >
  Compile natural-language orchestration intents into atomic goals, generate
  Linear Temporal Logic (LTL)-style specifications, ground propositions into
  discovered MCP tools and resources via two-stage role-aware matching and
  numeric enrichment, resolve temporal operators into reactive rules, and
  enforce two-phase SMT-backed guardrails before executing single-action
  consequents. Derived from SafeOrchestrate (arXiv:2611.09364).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Intent-to-LTL Runtime-Checked MCP Orchestration

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when building or hardening LLM-driven tool orchestration over
Model Context Protocol (MCP) servers, Web of Things (WoT) Thing Descriptions
(TDs), or cyber-physical system (CPS) actuator/sensor interfaces where
unconstrained LLM tool calling risks skipping preconditions, misordering
multi-device workflows, confusing read queries with state-mutating actions, or
violating cross-rule and deployment safety constraints.

## When to Use

- Orchestrating heterogeneous sensors, actuators, controllers, or services exposed as MCP tools ($\mathcal{T}_t$) and resources ($\mathcal{R}_t$) from natural-language (NL) operator intents
- Event-triggered, ordered, or multi-device workflows where direct LLM-to-MCP tool use suffers from skipped preconditions, wrong tool selection, or extra unsafe actions
- Environments with standard capability schemas (e.g., W3C WoT Thing Descriptions, OpenAPI, URDF) that lack hand-authored planning domain annotations (`affects`, `isAffectedBy`) or pre-authored Hoare contracts
- Systems requiring deterministic pre-execution verification against both live runtime state snapshots and global safety constraints (e.g., emergency-stop invariants)

## Core Insight

Direct LLM-to-MCP tool invocation treats multi-device coordination, trigger
checking, and safety enforcement as an unconstrained reactive generation loop.
As tasks move from simple property reads to event-triggered, sequential, or
multi-device workflows, unconstrained tool calling degrades sharply—omitting
precondition checks, confusing read-only state queries with actuator commands,
and firing actions when triggers are absent. Compiling NL intent through an
explicit pipeline—atomic goal decomposition ($D_{am}$), LTL-style formula
generation ($G_f$), role-aware affordance grounding ($G_m$), temporal
resolution ($T_r$), and two-phase SMT-backed guardrail verification ($V_g$)—separates
specification synthesis from runtime execution and fails closed whenever any
stage cannot validate its output.

**Evidence**: Evaluated across 8 simulated smart home, greenhouse, and
industrial automation tasks (10 runs per atomic goal at temperature 0),
SafeOrchestrate achieves **100% required-action accuracy on all 8 tasks** and
**100% MCP Execution Similarity (MCP-ES) on 7 of 8 tasks** (scoring **92%
MCP-ES** on *Coming/Leaving Home* due to a single non-oracle lighting action).
By contrast, the direct LLM-to-MCP baseline (`VanillaOrchestrate`, capped at 3
reactive steps) matches 100% on simple property-triggered tasks (*Presence
Control*, *AC Control*) but degrades to **80% accuracy / 75% MCP-ES** on *Robot
Workflow*, **83% accuracy / 87% MCP-ES** on *Greenhouse Automation*, **50%
accuracy / 50% MCP-ES** on *Washing Machine Event*, **25% accuracy / 25%
MCP-ES** on *Alarm Ringing*, **80% accuracy / 17% MCP-ES** on *Coming/Leaving
Home*, and **17% accuracy / 13% MCP-ES** on *Doorbell Workflow*
(arXiv:2611.09364).

## Procedure

Implement the seven-component pipeline
$\mathcal{A} = \langle B_{mcp}, D_{am}, G_f, G_m, T_r, V_g, O_r \rangle$
sequentially for each atomic goal. If any stage fails to produce valid input
for the next, halt processing for that goal (fail closed) so $O_r$ performs no
action.

### Step 1: Expose capability descriptions via the MCP Bridge ($B_{mcp}$)

Transform device or service capability descriptions (such as W3C WoT Thing
Descriptions registered in a Thing Description Directory) into discoverable MCP
affordances at time $t$:

1. Map **properties** (state reads/writes) and **actions** (executable
   commands) to MCP tools $\mathcal{T}_t = \{t_1, \dots, t_n\}$ in explicit mode,
   distinguishing read-only query tools (e.g., `get_*`) from state-mutating
   actuator tools.
2. Map asynchronous **events** and observable sensor streams to MCP resources
   $\mathcal{R}_t = \{r_1, \dots, r_m\}$.

### Step 2: Decompose compound intent into ordered atomic goals ($D_{am}$)

Given a compound NL intent $g$, apply lexical decomposition $D_{am}(g) = \{am_1, \dots, am_k\}$:

1. Split $g$ at sentence boundaries and trigger cues while strictly preserving
   textual mention order so sequential workflows execute in the intended sequence.
2. Structure each atomic goal $am_i$ as an indivisible trigger–response pair:
   - **Precondition (trigger)**: an observable condition over properties,
     sensor readings, events, or status checks (e.g., $\text{humidity} > 60 \land \text{temp} > 25$).
   - **Action (response)**: one or more executable effects (tool invocations or
     property writes). Classify the response as either a **single-action
     consequent** ($|act| = 1$) or a **multi-action consequent** ($|act| > 1$,
     such as "turn on all ZigBee lamps").
3. Tag each fragment with its syntactic role $r \in \{\text{precondition}, \text{action}\}$
   so imperative command symbols are never misread as state predicates downstream.

### Step 3: Generate LTL-style symbolic specifications ($G_f$)

For each atomic goal $am_i$, invoke an NL-to-LTL translator ($G_f(am_i) \leadsto \phi_i$)
with role-consistent prompting and domain-agnostic few-shot examples:

1. Emit an LTL-style formula $\phi_i$ over symbolic propositions $\text{Prop}(\phi_i)$
   using boolean connectives ($\lnot, \land, \lor, \rightarrow, \leftrightarrow$)
   and temporal operators ($\mathbf{G}, \mathbf{F}, \mathbf{X}, \mathbf{U}$).
2. Normalize trigger placement so equivalent phrasings ("turn on the lamp if
   someone is present" and "if someone is present, turn on the lamp") produce
   the identical implication $\phi_i$.
3. Validate formula syntax deterministically (e.g., via a Lark grammar parser);
   if malformed, fail closed and abort the goal.

### Step 4: Ground symbolic propositions to MCP affordances ($G_m$)

Map every symbolic proposition $p \in \text{Prop}(\phi_i)$ with inherited role
$r \in \{\text{precondition}, \text{action}\}$ to live MCP affordances
$\Gamma_i(p, r) \subseteq \mathcal{T}_t \cup \mathcal{R}_t$ in two stages:

1. **Stage 1: Role-Aware Matching**:
   - Use semantic matching (LLM at temperature 0) constrained by role $r$:
     - If $r = \text{precondition}$, restrict candidates to **observable
       affordances** (MCP resources $\mathcal{R}_t$ or read-only query tools
       such as `get_holdingObject` or `get_temperature`).
     - If $r = \text{action}$, restrict candidates to **executable actuator
       tools** in $\mathcal{T}_t$ (such as `startBeltForward`). If $p$ denotes
       a device group, return the conjunction of matching actuator tools.
   - Apply a deterministic role-aware filter that drops any mapping whose
     antecedent is not observable or whose consequent is not executable.
2. **Stage 2: Numeric Enrichment**:
   - Inspect the NL fragment that produced $p$ for numeric literals and
     comparison cues (e.g., "exceeds 26", "below 18").
   - Attach the extracted relational operator and threshold to the grounded
     affordance ID:
     $$\text{proposition} \xrightarrow{\Gamma_i} \text{tool\_id} \oplus \text{comparison}$$
     (e.g., "temperature exceeds 26" $\mapsto$ `get_temperature > 26`).
3. **Whole-Formula Substitution**:
   - Recursively apply $\Gamma_i^*$ across $\phi_i$ without altering logical
     structure ($\Gamma_i^*(\varphi \odot \psi) = \Gamma_i^*(\varphi) \odot \Gamma_i^*(\psi)$)
     to yield the grounded formula $\phi_g = \Gamma_i^*(\phi_i)$.

### Step 5: Resolve temporal formulas into reactive rules ($T_r$)

Transform the grounded formula $\phi_g$ into reactive precondition–action pairs
$T_r(\phi_g) = \{(pre_1, act_1), \dots, (pre_k, act_k)\}$:

1. Parse $\phi_g$ into an abstract syntax tree and strip outer temporal
   modalities ($\mathbf{G}, \mathbf{F}, \mathbf{X}, \mathbf{U}$) so rules can be
   evaluated against a single state snapshot $s_t$.
2. Extract reactive pairs from top-level implications and biconditionals:
   - Top-level implication $(A \rightarrow B)$ yields $\{(A, B)\}$.
   - Top-level biconditional $(A \leftrightarrow B)$ yields both $\{(A, B), (B, A)\}$.
   - Preserve boolean structure ($\land, \lor, \lnot$) inside $A$ and $B$.
   - If $\phi_g$ has no top-level implication or biconditional, return $\emptyset$
     (no action can be triggered).

### Step 6: Verify candidate actions with the two-phase Guardrail Verifier ($V_g$)

Before executing any candidate action $t_i \in \mathcal{T}_t$ from a
single-action consequent ($|act| = 1$), run two verification phases over the
sampled runtime state $s_t$:

1. **Phase 1: Precondition Evaluation**:
   - Evaluate $\text{eval}(pre_i, s_t) \in \{\text{true}, \text{false}\}$ directly
     against the current state snapshot $s_t$.
   - If $\text{false}$, reject $act_i$ immediately without invoking the SMT solver.
2. **Phase 2: SMT-Based Cross-Rule and Safety Consistency Check**:
   - Alias grounded tool and resource IDs to typed SMT variables (`Bool` or
     `Real` in Z3) via a shunting-yard infix-to-prefix pass, and encode the
     observed runtime state values as assignment assertions $\widehat{s_t}$.
   - Conjoin the complete grounded specification $\phi_g$, optional deployment
     safety invariants $C$ (e.g., $C = \lnot\texttt{get\_emergencyStop}$),
     the runtime state assignments $\widehat{s_t}$, and the candidate action
     assertion $(t_i = \text{true})$:
     $$V_g(\phi_g, s_t, t_i) = \text{SAT}\!\left(\phi_g \land C \land \widehat{s_t} \land (t_i = \text{true})\right)$$
   - Permit execution if and only if the solver returns `sat`. Because the check
     ranges over all of $\phi_g \land C$, it blocks actions whose local
     precondition holds but that violate a coupled rule (e.g.,
     $\texttt{get\_obstacleDetected} \rightarrow \lnot\texttt{startBeltForward}$
     or the reverse branch of a biconditional) or a global safety invariant $C$.

### Step 7: Coordinate execution in the Runtime Orchestrator ($O_r$)

Process each atomic goal $am_i \in D_{am}(g)$ once in textual order:

1. **State Sampling**: Read all observable affordances referenced in $\phi_g$
   into a single consistent snapshot $s_t$ reused across all checks for that
   goal pass.
2. **Candidate Selection & Guarded Dispatch**: Compute the authorized tool set
   $\mathcal{T}_e \subseteq \mathcal{T}_t$:
   $$\mathcal{T}_e = \left\{\, t \in \mathcal{T}_t \;\middle|\; \exists (pre, act) \in T_r(\phi_g) : t \in act \land \text{eval}(pre, s_t) \land \big(|act| = 1 \Rightarrow V_g(\phi_g, s_t, t)\big) \,\right\}$$
   - Single-action consequents ($|act| = 1$) require both Phase 1 and Phase 2
     ($V_g$).
   - Multi-action consequents ($|act| > 1$) execute sequentially and mutate
     state between steps, so single-snapshot SMT checking does not soundly
     apply; admit them on their satisfied Phase 1 precondition ($\text{eval}(pre, s_t)$) alone.
3. **Trace Fidelity Auditing (Optional Evaluation)**: To audit orchestration
   fidelity against an oracle sequence $E$, filter out read-only state queries
   (`get_*`) and internal guardrail checks to retain state-changing actions $A$,
   then compute normalized Levenshtein similarity:
   $$\text{MCP-ES} = 1 - \frac{D_{\text{edit}}(E, A)}{\max(|E|, |A|)}$$

## Environment Caveats

- **Single-snapshot temporal scope**: $T_r$ strips temporal operators and $V_g$
  checks a single state snapshot $s_t$ per atomic goal pass rather than
  reasoning over multi-step traces or concurrent interleavings. Duration
  requirements are supported only when they map directly to an executable
  affordance parameter.
- **No inter-goal state dependency**: Because $O_r$ samples $s_t$ per goal and
  does not search over execution orders, proportional control, continuous
  closed-loop monitoring, or rule sets whose later conditions depend on the
  physical effects of earlier actions require external event re-triggering or
  per-pair state resampling.
- **Pre-execution verification only**: $V_g$ gates tool calls before dispatch;
  it does not inspect post-execution physical actuation results or recover from
  hardware faults during execution.

## Failure Modes

- **Role-correct but semantically wrong grounding**: If Stage 1 maps a
  precondition to the wrong read-only sensor or maps an action to the wrong
  actuator of the same type, the deterministic role filter will not catch the
  mismatch. Require human review or domain-specific schema constraints in
  high-consequence deployments.
- **Applying single-snapshot SMT to multi-action consequents**: Conjoining
  multiple sequential state-mutating actions into a single static snapshot query
  can produce unsound rejections or admissions because intermediate actions
  change the state before subsequent actions run.
- **Unhandled NL trigger phrasings**: Because $D_{am}$ and Stage 2 numeric
  enrichment rely on lexical cue lists and regex threshold patterns, phrasings
  outside the recognized cue set fail closed rather than degrading into
  unconstrained tool execution.

## Cross-References

- [`mcp-hallucination-boundary-guards`](../mcp-hallucination-boundary-guards/SKILL.md) — Boundary guards for MCP tool schemas and hallucinated invocations
- [`temporal-workflow-graph-compilation`](../temporal-workflow-graph-compilation/SKILL.md) — Compiling workflow constraints into verifiable execution graphs
- [`pre-execution-action-auditing`](../pre-execution-action-auditing/SKILL.md) — Pre-execution action verification before committing external tool effects
- [`unified-capability-gateway`](../unified-capability-gateway/SKILL.md) — Routing agent capability invocations through a centralized policy gateway
- [`rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — Always-active rules on pre-execution tool gating and sandbox enforcement
- [`rules/adk-workflow-architecture.md`](../../rules/adk-workflow-architecture.md) — Workflow decomposition and structured orchestration patterns

## Sources

- SafeOrchestrate: Ashfaq et al., *SafeOrchestrate: Runtime Checked Intent-Driven Orchestration for Cyber-Physical Systems* (arXiv:2611.09364)
