---
name: historical-constraint-restoration
description: >
  Keep user-stated safety constraints in force across long, benign
  agent conversations. Capture each persistable constraint online, at
  the turn it is stated, as a structured rule object (scope, trigger,
  constraint, rule type, compiled target-bound audit rule); reactivate
  matching rules when a task resumes and restate them in the live
  request; then audit every proposed tool call deterministically
  against environment state and execution history, with precedence
  Block > Repair > Allow. Use it when an agent may act many turns after
  a constraint like "back it up before deleting" or "never touch X".
  Derived from "A GHOST in Long-Horizon Agents: Governance Hazard from
  Overlooked Safety Constraints across Turns" (arXiv:2610.02664).
source: https://arxiv.org/abs/2610.02664
---

# Historical Constraint Restoration (STAR-Guard)

Use this skill when a tool-using agent runs long sessions in which the
user states an operational safety constraint early ("create a backup
before deleting", "never delete audit.log") and the agent later
resumes or starts a task that the constraint should govern, without
the user repeating it.

## When to Use

- Long-horizon assistants with persistent sessions (email, filesystem,
  finance, calendar/devices, network requests, script execution).
- Constraints are stated once, in natural language, and the risky
  action comes dozens of turns later.
- The failure you are guarding against is benign forgetting, not an
  attack: no injection, no adversarial user.
- You can intercept tool calls before they reach the environment.

Not a substitute for injection defenses. For untrusted-content attacks
use [`pre-execution-action-auditing`](../pre-execution-action-auditing/SKILL.md)
and the authorization rules in `rules/agent-sandbox-safety.md`.

## Core Insight

The paper names the failure **GHOST**: the agent completes a task
safely when the constraint is restated, but completes the same task
unsafely when the constraint exists only earlier in the history. A
bigger context window does not fix it. Generic fixes that retrieve or
summarize history (reminders, BM25, decompose-and-critique,
summarization, three-tier memory) do not reliably pick out *which*
constraint governs *this* target, and none enforce action order.

Two layers do different jobs:

1. **Restoration** (semantic, probabilistic) reactivates the applicable
   constraint in the live request, so the agent proposes a compliant
   plan more often and task completion is preserved.
2. **Audit** (deterministic, no LLM) checks every proposed action
   against compiled, target-bound rules and blocks or repairs
   violations before they reach the environment.

Restoration alone leaves residual violations. Audit alone gets the
lowest GHOST rate but completes fewer tasks safely. Use both.

**Evidence** (SCARBench: 103 executable scenarios × 4 matched
conditions = 412 instances, 6 domains; benign long contexts of
6,000–6,176 tokens over 56–160 turns; 5 repetitions per model and
condition):

- Strict GHOST rate with no defense ranged from 6.8% (Kimi-K2.6) to
  27.8% (Qwen3.5-4B) across seven models; GPT-5.5 was at 11.5%, with
  Unsafe Completion (UC) rising 11.4 points when the constraint had to
  come from long history.
- STAR-Guard raised Safe Completion (SC) by 7.2–34.2 points and cut UC
  by 8.3–29.2 points across models. GPT-5.5: SC 76.3% → 94.0%, no UC
  or GHOST observed. Qwen3.5-4B: SC 47.0% → 81.2%, UC 31.1% → 1.9%,
  GHOST 27.8% → 1.9%.

Ablation and baselines (all on Qwen3.5-4B, Long Implicit condition):

| Method | SC | UC | GHOST |
|---|---|---|---|
| No defense | 47.0% | 31.1% | 27.8% |
| Restoration only | 76.3% | 4.3% | 3.7% |
| Audit only | — | — | 1.7% |
| VerIFY-Summarize | 56.9% | 35.3% | 27.4% |
| LIGHT Three-Memory | 58.4% | 23.7% | 18.6% |
| **Full STAR-Guard** | **81.2%** | **1.9%** | **1.9%** |

Oracle comparators that were *given* the correct rule did well
(TrustAgent: 5.2% UC; DVR with the benchmark's exact verifier: 0.4%
UC/GHOST). The hard part is capturing the rule online, which
STAR-Guard does without labels or verifier access.

---

## Procedure

### 1. Ingest Every User Message Online

Run one ingestion call on **every** incoming user message, at the turn
it arrives, before later turns exist. Ask a single question: does this
message contain a user-authored operational constraint that should
persist beyond this turn and bound tool-mediated execution? Ordinary
task goals, factual questions, conversational preferences and generic
caution are not constraints.

- If no: return `has_constraint: false` and leave the library alone.
- If yes: in the same call, extract a lifecycle rule object.

Don't extract retrospectively from a long history at resumption time;
that reintroduces the retrieval problem the skill exists to avoid. The
paper ran ingestion at temperature 0.

### 2. Store a Lifecycle Rule Object

Each rule object holds:

| Field | Example (prerequisite) | Example (prohibition) |
|---|---|---|
| source turn | 3 | 7 |
| scope | the file `temp/experiment_data.csv` | the file `audit.log` |
| trigger | deleting that file | deleting that file |
| constraint | back it up before deleting it | must never be deleted |
| rule_type | `prerequisite` | `prohibition` |
| sensitive action | `delete_file(path=temp/experiment_data.csv)` | `delete_file(path=audit.log)` |
| required action | `create_backup(path=temp/experiment_data.csv)`, order `before`, binding `same_target` | none |

Validate generated tool names and arguments against the public tool
schemas before storing; reject anything that doesn't conform.

### 3. Activate on Scope **and** Trigger Match

When a later message starts or resumes an executable task, run a
separate gate over all stored rules. Activate a rule only if both its
scope and its trigger match the task, respecting concrete bindings
(path, account, device, message, transaction, script). Don't activate
a rule just because it belongs to the same broad domain.

### 4. Restore Into the Live Request

Append each activated rule to the current request as an active
execution boundary, for example:

```
[resumed user request]

Restored historical user constraint (active execution boundary):
- Scope: <scope>
- Trigger: <trigger>
- Constraint: <constraint>
```

This makes a compliant plan more likely. It guarantees nothing.

### 5. Audit Every Proposed Action Deterministically

Before a proposed tool call reaches the environment, bind each active
rule to the call's concrete target and evaluate it against the current
environment state plus history facts (prerequisites already met,
confirmations, authorizations). No LLM is involved at this step.
Apply **Block > Repair > Allow**:

1. **Block**: if any target-bound prohibition matches, drop the action.
   No repair can authorize it.
2. **Repair**: if a prerequisite is unmet, execute the same-target
   required action, verify that it succeeded in the environment, then
   re-audit the original action. Every repair action goes through the
   same audit boundary, so a repair can't bypass another rule.
   A backup of a *different* file doesn't authorize the deletion.
3. **Allow**: forward only when every applicable rule holds.

If the required evidence is unavailable or repair fails, block.

### 6. Report the Full Outcome Split

Score runs by task completion, by a trace predicate (was the required
procedure followed?) and by a final-state predicate (is the
environment safe?). Report Safe Completion, Unsafe Completion, Safe
Non-completion, Unsafe Attempt and Execution Failure separately, so a
guard that converts unsafe runs into blocked tasks is visible. Measure
GHOST with matched pairs: the same case with the constraint restated
vs only in long history.

---

## Environment Caveats

- **Conditional guarantee only.** The audit enforces a rule only if
  detection, extraction, activation, target binding, compilation and
  interposition all worked. A missed constraint at ingestion is never
  enforced. This is an action-local property, not end-to-end safety.
- **Two rule types.** The paper implements prerequisites and
  prohibitions with same-target binding. Constraints about rates,
  quantities, recipients by role, or cross-target conditions need new
  compiled predicate types.
- **Benchmark setting.** One user, benign histories of about 6k tokens,
  at most 5 model iterations per task. Behavior with adversarial users,
  conflicting or revoked constraints, and much longer sessions was not
  tested. Plan for rule revocation and conflict explicitly.
- **Cost.** One ingestion call per user message and one gate call per
  task, plus the audit. The paper does not report latency or tokens.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Constraint never captured | Ingestion classifies it as a task goal or generic caution | Log ingestion decisions; spot-check negatives; keep a human-visible rule list |
| Over-activation | Gate matches on broad domain | Require scope **and** trigger match on concrete bindings (step 3) |
| Repair bypasses another rule | Repair action executed directly | Route every repair action through the same audit (step 5) |
| Wrong-target authorization | Prerequisite met on a different object | Same-target binding in the compiled rule (step 2) |
| Hidden over-refusal | Blocks counted as safe | Report SN/UA/EF alongside SC/UC (step 6) |
| Stale rule | User revokes or changes the constraint | Treat revocation as a constraint message; update the rule object, keep the source turn |

## Cross-References

- `rules/agent-sandbox-safety.md`: "DO: Restore earlier-turn safety
  constraints and enforce them at a deterministic action boundary"
  (this skill's rule), "DON'T: Rely on single-turn refusal or initial
  benign turns to evaluate long-horizon safety", "DON'T: Rely on
  structured LLM authorization decisions as the sole safety gate",
  "DO: Confine the LLM to bounded record extraction and authorize
  against a verified, frozen policy".
- [`pre-execution-action-auditing`](../pre-execution-action-auditing/SKILL.md):
  pre-dispatch auditing aimed at injected content rather than forgotten
  user constraints.
- [`dependency-scoped-plan-validation`](../dependency-scoped-plan-validation/SKILL.md):
  checks that a pending action still derives from current state.

> Source: A GHOST in Long-Horizon Agents: Governance Hazard from
> Overlooked Safety Constraints across Turns (arXiv:2610.02664),
> Oct 2026. Praxis source: src:2610-02664
