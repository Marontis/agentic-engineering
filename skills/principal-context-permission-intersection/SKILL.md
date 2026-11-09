---
name: principal-context-permission-intersection
description: >
  System-level privilege-escalation defense for multi-principal LLM agents via
  the ITES provenance kernel and Conflux architecture. Tracks all influencing
  principals in an immutable Principal Context, intersects their existing
  access-control permissions at the effect boundary outside model judgment,
  plans read/action ordering to bound authority attenuation, and verifies finite
  defense models with black-box (SLED) and white-box IR (SLED-V) evaluators.
  Derived from Conflux (arXiv:2611.08768).
source: https://arxiv.org/abs/2611.08768
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Principal-Context Permission Intersection (Conflux / ITES)

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when designing, hardening, or verifying tool-using LLM agents
that consume data from multiple principals (users, retrieved documents, APIs,
other agents) and execute externally visible actions against an organization's
access-control system (ACS).

## When to Use

- An agent combines instructions or data from multiple users, documents, tool
  outputs, or sub-agents before invoking effect-bearing tools
- You need a deterministic, system-level guarantee against **privilege
  escalation (`PE`)** that holds even under arbitrary or worst-case LLM
  behavior (prompt injection, confused deputy, data-dependent arguments)
- Unlike control-flow lock-in systems (`CaMeL`) that reject data-dependent
  arguments, your workflow requires legitimate data-dependent values (e.g.,
  User `Ava` asks the agent to update a record using a remediation status
  authored by `Ben`) while confining the resulting action to principals
  authorized by the existing ACS
- You want to order or branch untrusted reads (**Exposure Planning**) so early
  low-privilege reads do not unnecessarily block high-privilege actions
- You need to verify your authorization mediator using bounded exhaustive state
  exploration (`SLED`) or solver-backed plan Intermediate Representation (`IR`)
  checking (`SLED-V`)

## Core Insight

Model-level defenses (structured queries, spotlighting, preference tuning,
injection classifiers) decide based only on token histories and user requests.
By **Proposition 1 (System-Level Necessity)**, under worst-case model behavior,
*no deterministic defense whose admission decision depends only on model-level
information and the user request can guarantee that an unauthorized action is
never admitted*: two executions with identical token text—one authored by an
authorized principal $u$, one by an unauthorized adversary $v$—are
indistinguishable to the model. Conversely, by **Proposition 2 (Model-Level
Utility)**, system-level provenance and ACS state alone cannot choose which of
several authorized actions $a_1, a_2$ completes the user's semantic goal.
Therefore (**Corollary 1**), a sound architecture requires a **mixed-level
decomposition**: the LLM acts purely as an untrusted proposal generator, while
an external kernel (**`ITES`** — *Influence Tracking with Extrapolated
Security*) enforces authority confinement at the effect boundary.

**Key Properties (`arXiv:2611.08768`)**:
- **Privilege Escalation (`Definition 1`)**: An action event $(e, a, t)$
  escalates privilege iff there exists a semantically influencing principal
  $u \in \mathrm{I}_{\mathrm{sem}}(e, a)$ such that $\neg P_t(u, a)$ under the
  effective ACS relation $P_t$ at dispatch time $t$.
- **Pointwise Intersection & Monotonicity (`Proposition 3`)**: Consuming
  information from an additional principal can only preserve or shrink effective
  authority ($X \subseteq Y \implies \mathrm{Permitted}_P(Y) \subseteq
  \mathrm{Permitted}_P(X)$), acting as a principal-sensitive readers-lattice
  meet analogous to Biba's low-water-mark integrity rule without inventing a
  separate policy language.
- **Context-Relative Maximality (`Proposition 4`)**: Among sound rules that
  observe only the recorded Decision Context $\mathrm{DC}(e, a)$ and ACS
  relation $P$, `ITES` is maximal—it admits every action that all principals in
  $\mathrm{DC}(e, a)$ permit.

---

## Conditional Authority-Confinement Assumptions (`Theorem 1`)

Before deploying the `ITES` kernel, verify that your runtime satisfies all five
explicit assumptions required for the authority-confinement invariant:

| ID | Assumption | Operational Requirement |
|:---|:---|:---|
| **`A1`** | **Complete Mediation** | Every externally effectful action $a$ is mediated by `ITES` and executes only if the authorization kernel *and* all independent policy ports (`read`, `visibility`, `consent`, `argument-policy`) return `permit`. |
| **`A2`** | **Influence Completeness & No-Laundering** | Semantic influence is contained in the decision context ($\mathrm{I}_{\mathrm{sem}}(e, a) \subseteq \mathrm{DC}(e, a)$), and for every data object $d$ with direct sources $\mathrm{Src}(d)$, $\bigcup_{d' \in \mathrm{Src}(d)} A(d') \subseteq A(d)$ so copying untrusted text into a new document cannot strip prior authors. |
| **`A3`** | **Rule Conformance** | The runtime's authorization decision implements the exact `ITES` intersection predicate over $\mathrm{DC}(e, a)$. |
| **`A4`** | **Action Binding & Atomic Recheck** | Immediately before dispatch, the mediator re-derives the decision for $\mathrm{DC}(e, a)$ and verifies an immutable certificate binding the action fingerprint, context fingerprint, branch ID, and policy version. Recheck and dispatch are atomic with respect to policy changes, or fail closed. |
| **`A5`** | **Known, Non-Empty Context** | $\mathrm{DC}(e, a) \subseteq U \cup \{\bot\}$ is non-empty and contains no unknown provenance ($\bot \notin \mathrm{DC}(e, a)$, where $\bot$ is absorbing under context merge $\bigsqcup$). |

---

## Procedure

### Step 1: Track No-Laundering Principal Contexts Across Reads and Proposals

Maintain an immutable **Principal Context** $\mathrm{PC}(e)$ outside the LLM
for every execution branch $e$:

1. **Assign Authorship & Absorbing Unknowns**: For every ingested data object
   $d \in D$ (user prompt, document, database row, API response), resolve its
   author set from the provenance store $W \subseteq D \times U$:
   $$\mathrm{PC}(e) = \bigsqcup_{d \in ds} A(d), \qquad A(d) = \begin{cases} \{u \in U \mid W(d, u)\} & \text{if } d \text{ has a recorded author,} \\ \{\bot\} & \text{otherwise.} \end{cases}$$
   If *any* input has unknown authorship, $\bot$ propagates and absorbs the
   entire context ($\bot \in \mathrm{PC}(e)$), causing `ITES` to fail closed.
2. **Enforce No-Laundering Provenance (`A2`)**: Whenever an agent or user
   creates a derived object $d$ from source objects $\mathrm{Src}(d)$, set
   $A(d) \supseteq \bigcup_{d' \in \mathrm{Src}(d)} A(d') \cup \mathrm{PC}(e)$.
   Never allow summarization, file writing, or trusted-user copying to reset
   provenance to the latest writer alone.

### Step 2: Intersect Permissions Across Independent Policy Ports at the Effect Boundary

When the untrusted LLM proposes an action $a$ with arguments, evaluate the
proposal in a pure, deterministic mediator (`Conflux` request path):

```python
from dataclasses import dataclass
from typing import FrozenSet, Mapping, Callable

UNKNOWN = "<UNKNOWN_PRINCIPAL>"

@dataclass(frozen=True)
class DecisionCertificate:
    action_fp: str
    context_fp: FrozenSet[str]
    branch_id: str
    policy_version: int

def authorize_ites_conflux(
    pc_exec: FrozenSet[str],
    arg_provenance: FrozenSet[str],
    action_kind: str,
    arg_selectors: Mapping[str, str],
    branch_id: str,
    policy_version: int,
    acs_permits: Callable[[str, str, int], bool],
    arg_policy_permits: Callable[[str, str, str, int], bool],
    read_port_ok: bool,
    visibility_port_ok: bool,
    consent_port_ok: bool,
    action_fp: str,
) -> DecisionCertificate:
    # 1. Merge Execution Principal Context with Argument Provenance
    dc = pc_exec | arg_provenance

    # 2. Enforce A5: Known and Non-Empty Decision Context (fail-closed)
    if not dc or UNKNOWN in dc:
        raise PermissionError("DENY [A5]: Empty or unknown principal in Decision Context")

    # 3. Enforce Independent Policy Ports (Conjunction; none can widen authority)
    if not (read_port_ok and visibility_port_ok and consent_port_ok):
        raise PermissionError("DENY [Port]: Independent read/visibility/consent port denied")

    # 4. Enforce A3: Pointwise ACS Permission Intersection over all u in DC(e, a)
    for u in dc:
        if not acs_permits(u, action_kind, policy_version):
            raise PermissionError(f"DENY [ITES]: Principal '{u}' lacks ACS permission for '{action_kind}'")
        # Argument-aware selector checks per authority-bearing argument
        for role, val in arg_selectors.items():
            if not arg_policy_permits(u, role, val, policy_version):
                raise PermissionError(f"DENY [ArgPolicy]: Principal '{u}' unauthorized for {role}={val}")

    return DecisionCertificate(
        action_fp=action_fp,
        context_fp=dc,
        branch_id=branch_id,
        policy_version=policy_version,
    )
```

- **Keep Policy Ports Orthogonal**: Evaluate `authorisation`, `argument-aware
  selector policy`, `read access`, `visibility` (deterministic audience-specific
  field redaction), and `consent` as separate ports whose decisions are
  conjoined. User consent is an independent port—**consent can never supply or
  widen missing ACS authority** for another principal in $\mathrm{DC}(e, a)$.
- **Enforce Atomic Recheck at Dispatch (`A4`)**: Immediately before the effect
  sink executes $a$, re-verify that `certificate.branch_id == current_branch`,
  `certificate.policy_version == current_acs_version`, and
  `certificate.action_fp == hash(a, args)`. Reject sibling-branch certificates
  or stale policy versions fail-closed.

### Step 3: Apply Exposure Planning to Preserve Utility Under Monotonicity

Because reading an untrusted document $d_B$ authored by principal $B$
monotonically shrinks permitted actions to $\mathrm{Permitted}_P(\{A, B\})$,
naively reading all inputs upfront causes **authority contamination** (false
denials). Use **Exposure Planning** over the finite planning domain
$(S, s_0, G, \mathcal{O}, c)$ with operators $\mathrm{read}(d)$ and
$\mathrm{act}(a)$:

1. **Order Effectful Actions Before Low-Privilege Reads**: If task goal $G$
   requires action $a_1$ (permitted only for $A$, needing only $d_A$) and
   action $a_2$ (permitted only for $B$, needing only $d_B$), schedule
   $\mathrm{read}(d_A) \to \mathrm{act}(a_1)$ before $\mathrm{read}(d_B)$—or
   spawn an isolated child branch for $d_B \to \mathrm{act}(a_2)$ that does not
   merge $B$ into the parent's Principal Context.
2. **Minimize Exposure Cost**: Rank candidate admissible plans by a cost
   function $c$ counting newly acquired principals, sensitive reads,
   irreversible effects, and branch count, with a deterministic tie-breaker.
3. **Combine with Operation Alphabet Restriction**: Restrict the planner to a
   task-declared operation alphabet so untrusted data cannot introduce new tool
   types into the proposal space.

### Step 4: Verify the Mediator with System-Level Evaluators (`SLED` & `SLED-V`)

Never rely solely on LLM prompt-injection benchmarks (`AgentDojo`, `InjecAgent`)
to certify authority confinement—a model benchmark tests whether a specific LLM
resists a fixed attack suite, and read-only or low-capability runs can report
`0` security violations simply because no effect call was ever attempted (in
`Conflux`'s retained `AgentDojo` runs, `66/66` attacked `14B` cells and
`198/198` complete `0.5B` floor cells reported no security violation because no
effect tool was executed, with utility `19/132` and `0/204` respectively;
`Tables 6–7`). Instead, run two complementary system-level checks:

1. **Black-Box Finite-Model Exploration (`SLED`)**:
   - Declare a finite model of your defense (principals, ACS state, objects,
     tools, transition relation, depth bound) and treat the LLM as an
     adversarial, nondeterministic proposal source that emits *any* well-typed
     proposal at each step.
   - Run breadth-first search up to the bound to verify that no admitted trace
     reaches a privilege-escalating state, and check the **projection/lifting
     condition** (every trace projects to a task sequence, every admitted task
     sequence lifts to a trace, and projection preserves goal/action labels).
2. **White-Box Plan IR Verification & Mutation Falsifiability (`SLED-V`)**:
   - Serialize plan and transition models into a finite-domain or node-bounded
     plan IR and check security/provenance invariants using predicate
     abstraction with `CEGAR` refinement and `SMT`-based induction (or `IC3/PDR`
     on finite-domain fragments), cross-checking solver verdicts against a
     direct reference interpreter.
   - **Audit Mutation Falsifiability**: Mutate single rule guards in your
     declared mutation alphabet and classify each invariant as:
     - `checked`: holds at baseline *and* at least one single-rule guard
       weakening falsifies it at a reachable state (verify the baseline rule's
       guard is actually reachable so the check is non-vacuous).
     - `checked_by_construction`: holds at baseline, but no single-rule mutation
       falsifies it—**do not claim this as defense enforcement**, as the
       property is merely entailed by the encoding.
     - `violated_at_baseline`: fails before mutation.

---

## Environment Caveats

- **Value Influence vs. Control Influence (`Section 3.3`)**: `ITES` Theorem 1
  covers the **value-influence fragment** (where influencing data reaches $a$ or
  its tracked authority-bearing arguments $\mathrm{Prov}_{\mathrm{arg}}(a)$).
  If an untrusted input influences *control flow*—such as which tool, branch,
  recipient, or plan step the LLM selects—while all value arguments come from a
  trusted source, `A2` does not automatically capture that control dependency
  unless the branch/step provenance is explicitly merged into $\mathrm{PC}(e)$.
- **Argument Schema Completeness**: Argument-aware authorization only checks
  arguments marked as authority-bearing in the tool schema. Any tool parameter
  omitted from selector annotations bypasses argument-level policy.
- **Safety-Only Guarantee (No Liveness or Noninterference)**: `Conflux` is
  fail-closed and safety-only. It does not guarantee task completion (liveness)
  and does not prevent timing, latency, or output-ordering side channels
  (authorized-read safety is not information-flow noninterference).

## Failure Modes

- **Provenance Laundering via Intermediate Writes**: Allowing an agent to read
  an untrusted email from `External`, write a summary note attributed solely to
  the current user `Ava`, and then read that summary in a fresh step strips
  `External` from $\mathrm{DC}(e, a)$, violating `A2`.
- **Treating User Consent as Authority Elevation**: Allowing `Ava`'s interactive
  approval ("Yes, run this") to override a missing ACS permission for another
  influencing principal `Ben` in $\mathrm{DC}(e, a)$ turns the user into a
  confused deputy. Consent must remain a conjunctive port that can only deny.
- **TOCTOU Race Between Certificate Check and Dispatch**: Checking ACS
  permissions during planning without atomic re-verification of the policy
  version and action fingerprint at the effect sink (`A4`) allows stale
  grants or mutated arguments to slip through.
- **Vacuous Benchmark Assurance**: Claiming `100%` attack defense from
  `AgentDojo` runs where the adapter only exposed read paths or where a small
  model (`0.5B`) achieved `0%` task utility, or claiming formal verification
  from `checked_by_construction` IR invariants that cannot be falsified by guard
  mutations.

## Cross-References

- [`agent-sandbox-safety`](../../rules/agent-sandbox-safety.md) — Capability
  gateways, pre-execution action auditing, and fail-closed containment rules.
- [`unified-capability-gateway`](../unified-capability-gateway/SKILL.md) —
  Single-pipeline capability routing (`CrabOS`).
- [`provenance-capability-grants`](../provenance-capability-grants/SKILL.md) —
  Provenance-scoped capability enforcement (`ToolFence`).
- [`multi-hop-delegation-auth-propagation`](../multi-hop-delegation-auth-propagation/SKILL.md) —
  Attenuated authorization propagation across multi-agent delegation chains.
- [`pre-execution-action-auditing`](../pre-execution-action-auditing/SKILL.md) —
  Pre-execution effect-boundary checks (`ActGuard`).

## Sources

- Buckley & Schroeder de Witt, *Conflux: Preventing Privilege Escalation with
  Principal Contexts and System-Level Evaluation* (arXiv:2611.08768, November
  2026)
