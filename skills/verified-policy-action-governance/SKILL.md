---
name: verified-policy-action-governance
description: >
  Authorize every LLM-proposed tool call deterministically against a
  policy bundle that was generated offline and checked with an SMT solver.
  The LLM is confined to filling a finite set of typed context records
  (such as argument provenance), and a deterministic interpreter makes the
  allow/deny decision. Use against indirect prompt injection in
  long-horizon, dynamically branching tool workflows where fixed plans
  are too brittle.
  Derived from "ActGov: Governing LLM Agent Actions via Policy-Constrained
  Validation" (arXiv:2609.24446).
source: https://arxiv.org/abs/2609.24446
---

# Verified Policy Action Governance

Use this skill when an agent must adapt its plan to tool outputs (so you
cannot pre-commit a plan), yet untrusted tool content must never be able to
authorize an action the user did not ask for.

## When to Use

- Tool-calling agents that read untrusted content (email, web, shared
  documents) and can take side-effecting actions (send, pay, delete, share)
- Workflows where action targets must be resolved from runtime observations,
  so plan-locking defenses (CaMeL- or ACE-style) destroy utility
- You need a policy set that is auditable and machine-checked before it is
  deployed, not a judge prompt that decides at runtime
- The tool catalog grows over time and hand-written policies no longer keep up

## Core Insight

Split action *proposal* from execution *authority*. The agent may propose
any call. A monitor between the agent and the tools maps the call and its
context onto a **finite record space**, and permits the call only if it
falls inside the task-scoped permission boundary and violates no policy.
The LLM is used only to fill bounded record values (for example, "is this
argument from an untrusted source?") and to draft policies offline. It never
makes the allow/deny decision.

**Evidence**: The policy bundle was built with GPT-5.5 over 10 refinement
rounds with human review and evaluated on held-out splits.

- **AgentDyn**: ASR at most 0.007 across four agent backends (Qwen3.6-flash,
  MiniMax-M2.5, DeepSeek-v4-pro, GPT-4o mini). Qwen3.6-flash kept clean and
  attacked utility at 0.667 and 0.586, versus 0.667 and 0.650 undefended.
- **AgentDojo**: ASR 0.000 on all four backends.
- **Baselines on AgentDyn**: CaMeL and ACE reached 0.000 ASR but also 0.000
  utility. Progent's clean utility fell to 0.033–0.217.

---

## Procedure

### 1. Define the Finite Record Schema

Enumerate the authorization-relevant facts about any tool call as typed
records with finite value domains. Classify each record on two axes.

**Formation level** (how the value is produced):

| Level | Produced by | Example |
|:--|:--|:--|
| L1 Deterministic | Structured system state, no NLP | `tool_allowed`, `is_high_risk`, `pending_obligation` |
| L2 Bounded semantic | LLM maps text to a predefined enum or boolean | `arg_provenance` ∈ {user, trusted_tool, untrusted_tool} |
| L3 Composed | Boolean combination of L1/L2 | `binding_valid` |

**Semantic scope** (what the value describes): action, permission,
parameter, history, binding, external, domain.

Keep the value domains small. Whatever the schema cannot represent, the
policies cannot constrain, and the solver cannot check.

### 2. Write the Three Policy Layers

- **Task-Permission**: from the trusted user prompt only, derive the
  minimum tool and resource set (`perm`). Any action outside `perm` is
  denied.
- **Hard-Invariants**: global properties that hold regardless of task. For
  example, no outbound action whose destination or payload has
  `arg_provenance = untrusted_tool`.
- **Procedural-Obligations**: conditional prerequisites for ambiguous
  cases, such as weak target binding or uncertain provenance. Examples:
  "require user confirmation first" or "require a lookup that binds the
  target".

### 3. Generate and Refine Policies Offline, Gated by an SMT Check

Loop until no counterexamples remain (the paper used 10 rounds with human
review, or 5 rounds fully automated):

1. An LLM proposes or edits rules using three inputs: tool specifications
   (capability and risk), benign task traces (to find over-restrictive
   rules), and observed attack traces (to find missing conditions).
2. Encode the bundle and each security assertion `A_sec` in Z3. Query
   `∃ r, v : Domain(r) ∧ P_sem(r, v) ∧ ¬A_sec(r, v)`.
3. **SAT** means a counterexample: a policy gap or conflict. Feed it back
   to step 1.
4. **All UNSAT** means the bundle preserves every assertion over the
   modeled record domain. Present it to an administrator, then **freeze**
   it.

No update may reach the runtime monitor without passing this check.

### 4. Enforce at Runtime (No Solver Online)

For each proposed call `c_i`:

1. Resolve `perm` for the task.
2. Populate the record set `r_i = α(task, perm, history, c_i)`. Compute L1
   records from state. Ask the LLM only for L2 values, each with a
   constrained output. Compute L3 records.
3. Evaluate the frozen bundle deterministically. Execute the tool **iff**
   the call is within `perm` and no policy is violated. Otherwise return a
   denial, or the pending obligation, to the agent.
4. Append the records, the verdict, and the rule that fired to the
   execution history. Later `History` records depend on this, for example
   an unresolved approval.

### 5. Measure Utility Alongside ASR

A defense that blocks everything scores ASR 0. Always report clean utility,
attacked utility, and ASR together on a held-out split. Add utility loss to
your end-to-end false-refusal budget (see `rules/agent-sandbox-safety.md`,
"DO: Track false refusal accumulation across layers").

---

## Environment Caveats

- **The guarantee holds only inside the modeled domain.** UNSAT proves the
  assertions hold for all assignments of the *records*. It says nothing
  about whether the L2 extractor labeled provenance correctly.
- **Policies are domain-specific.** Bundles trained on one benchmark
  collapsed utility on the other. Evaluated on DeepSeek-v4-pro, an
  AgentDojo-trained bundle on AgentDyn gave clean utility **0.100**,
  against 0.600 in-domain and 0.767 undefended. ASR stayed 0.000, so the
  failure mode is over-blocking, not leakage. Rebuild policies for each new
  tool domain.
- **The policy-generating model matters.** With the same 50% training
  data, bundles drafted by Qwen3.6-flash or MiniMax-M2.5 gave clean utility
  0.317 and 0.283. Bundles drafted by DeepSeek-v4-pro gave 0.533. ASR was
  ≤ 0.007 in all three cases. Halving training data further (50% to 25%)
  cost little (0.533 to 0.500).
- The threat model assumes the attacker cannot modify the user task, tool
  specifications, or deployed policies, and that every side effect passes
  through the monitor.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:--|:--|:--|
| Over-blocking in a new domain | Policy bundle reused on unseen tools or tasks | Re-run step 3 with benign traces from the new domain; track clean utility |
| Provenance mislabeling | L2 extractor fooled by injected text | Keep L2 outputs enum-constrained; make L1 records carry as much as possible (for example, taint tags on tool outputs) |
| Silent policy drift | Hand edits to the deployed bundle | Freeze the bundle; any change re-enters the SMT loop |
| Assertion set too weak | Solver proves only what you asserted | Review `A_sec` with red-team traces; add assertions for each new attack class |
| Static-benchmark overconfidence | ASR 0.000 on AgentDojo taken as robustness | Add adaptive attacks (`skills/self-improving-red-team/SKILL.md`), per deconfliction item M14 |

---

## Cross-References

- `skills/unified-capability-gateway/SKILL.md`: the single pipeline this
  monitor plugs into as the policy stage
- `skills/pre-execution-action-auditing/SKILL.md`: evidence-span auditing
  of arguments, complementary to provenance records
- `skills/runtime-resource-authorization-bounds/SKILL.md`: provenance-bounded
  activation of dynamically acquired resources
- `skills/auto-formalization-safety-guarantee/SKILL.md`: same
  verify-before-deploy idea applied to generated code
- `rules/agent-sandbox-safety.md`: "DON'T: Rely on structured LLM
  authorization decisions as the sole safety gate"
- `rules/adk-workflow-architecture.md`: "DO: Evaluate deterministic policy
  checks BEFORE invoking generative models"

## Sources

> Zhang, Peng, Jiang et al., "ActGov: Governing LLM Agent Actions via
> Policy-Constrained Validation" (arXiv:2609.24446), Sep 2026.
