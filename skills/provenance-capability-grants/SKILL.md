---
name: provenance-capability-grants
description: >
  Authorize tool calls against a per-query blueprint of capabilities whose
  authority-sensitive arguments are bound to provenance (user query, a named
  tool's output, a template), checked by a deterministic monitor. When a
  legitimate call falls outside the blueprint, grant a value-free capability
  shape at runtime instead of judging each concrete call, and cache approved
  shapes across sessions. Use against indirect prompt injection that keeps
  the right tool but changes the recipient, amount or destination.
  Derived from "ToolFence: Fine-Grained Authorization for Secure Tool-Using
  LLM Agents" (arXiv:2609.37196).
source: https://arxiv.org/abs/2609.37196
---

# Provenance-Bound Capability Grants

Use this skill when a tool-using agent reads untrusted content and can take
side-effecting actions, and tool-level allowlists are too coarse: the attack
you worry about calls an authorized tool (`send_money`, `send_email`) with an
attacker-chosen argument.

## When to Use

- Indirect prompt injection where the attacker hijacks arguments, not tool
  choice (within-tool hijacking)
- Plans cannot be fixed up front, but full control/data-flow isolation
  (CaMeL-style) costs too much latency or utility
- A per-call LLM judge works but is slow and re-decides the same question
  many times per task

Prefer [verified-policy-action-governance](../verified-policy-action-governance/SKILL.md)
when you need an offline, SMT-checked, frozen policy that an auditor signs
off. This skill trades that for runtime adaptation (see Tension below).

## Core Insight

Authorize **where a value came from**, not what the value is, and authorize
**shapes**, not calls. A capability says: tool T, effect class E, and for
each sensitive parameter, the only allowed source (literal from the user
query, derived from tool X's output, template, or free if not sensitive). A
deterministic checker can then verify every call. When a legitimate call
needs a capability nobody anticipated, ask a judge once to approve the
shape, then reuse the deterministic check for every later call of that
shape.

**Evidence** (AgentDojo with a parameter-aware split: 524 cross-tool, 85
within-tool and 20 ambiguous attack pairs; six injection styles):

- Qwen3-max: overall attack success 0.20% (no defense 21.20%, CaMeL 0.42%);
  within-tool 0.80%, where Tool Filter left 9.18%.
- GPT-4o: 0.90% overall (no defense 38.01%, CaMeL 1.28%); within-tool 2.10%
  versus 18.20% for Tool Filter.
- Utility under attack: 32.45% vs 25.82% for CaMeL (Qwen3-max); 73.80% vs
  47.80% (GPT-4o). Clean utility 38.90% vs 32.67%, and 82.70% vs 70.50%.
- Latency: 1.63x (Qwen3-max) and 3.79x (GPT-4o) versus 10.67x and 12.95x for
  CaMeL.

---

## Procedure

### 1. Classify Tools and Sensitive Parameters

For each tool, record its effect class (read, communication, financial,
and so on) and mark which parameters are **authority-sensitive**: the ones
that decide who receives, how much, or where (recipient, amount,
destination, file path to share). Everything else may be `free`.

### 2. Compile a Blueprint From the Authenticated Query Only

Before the agent reads any external content, have a policy model turn the
user's authenticated request into capabilities. Each capability binds every
sensitive parameter to one provenance type:

| Binding | Value must come from |
|:--|:--|
| `literal` | text of the authenticated user query |
| `derived(tool)` | the output of a named tool already executed in this session |
| `template` | a pattern the user authenticated |
| `free` | anywhere (non-sensitive parameters only) |

Example: for "pay the bill in bill.txt", `send_money.recipient ←
derived(read_file('bill.txt'))`, `send_money.amount ← literal`. Bind
sources, not concrete values. Give each capability an execution budget.

### 3. Check Every Call Deterministically

For each proposed call, with no LLM in the loop:

1. Find a capability with matching tool and effect.
2. Trace each sensitive argument: does the value occur in the user query,
   or in the output of the declared source tool that has already run?
3. Check the remaining budget.

Pass on all three. Read-only calls whose arguments come only from the user
query may be auto-allowed.

### 4. Grant Missing Capabilities at Runtime, by Shape

When a call misses the blueprint:

1. Compute the provenance of each argument (user, tool, model-generated).
2. **Refuse immediately** if any sensitive argument is model-generated or
   traces only to untrusted content outside a declared binding. The judge
   never sees these.
3. Otherwise build the candidate capability shape (tool, effect, binding
   types, source-tool names, no concrete values) and ask the judge to
   approve the **shape**.
4. On approval, add it to the running blueprint and let Step 3 handle every
   later call of that shape. On denial, fall back to per-call judgment.

### 5. Cache Approved Shapes Across Sessions

Key the cache by the value-free signature (tool, effect, binding types,
source-tool names). In a new session, inject cached shapes into the fresh
blueprint, but re-validate concrete values against that session's own tool
outputs. Never carry concrete sensitive values between sessions.

Treat the cache as a standing policy: version it, log every insertion with
the approving judge call, and let an administrator revoke entries. Changes
to the blueprint compiler, judge prompt or cache policy go through the
acceptance gate in `rules/recursive-improvement.md` ("Pass every
self-modification through one acceptance gate"), with the attack suite as
the strict security testbed.

### 6. Measure Three Axes

Report attack success split into cross-tool and within-tool, utility clean
and under attack, and open privilege (`rules/agent-sandbox-safety.md`,
"Measure open privilege alongside attack success and utility"). Track judge
calls per task and latency.

---

## Component Contributions (Qwen3-max ablation)

| Configuration | Utility under attack | ASR | Judge calls/task | Runtime |
|:--|:--|:--|:--|:--|
| Per-call judge | 31.20% | 4.35% | 6.35 | 3.20x |
| Blueprint + monitor | 25.60% | 0.45% | 0.00 | 1.45x |
| + runtime grant | 30.40% | 0.18% | 1.84 | 2.78x |
| + cache | 31.80% | 0.18% | 1.05 | 1.96x |
| + read auto-allow | 32.45% | 0.20% | 0.82 | 1.90x |

A static blueprint alone is secure but over-blocks; runtime grants recover
utility; the cache cuts judge calls by 42.9%.

**Tension with frozen policies**: [verified-policy-action-governance](../verified-policy-action-governance/SKILL.md)
freezes an SMT-checked bundle so nothing changes at runtime. This skill
extends authority at runtime and across sessions through the cache. The
evidence differs in setting (AgentDojo with Qwen3-max/GPT-4o here; AgentDyn
and AgentDojo with four other backends there). Use frozen policies where
auditability of every rule matters; use runtime shape grants where
unanticipated legitimate capabilities are common, and keep the cache under
administrator control.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:--|:--|:--|
| Legitimate target only in untrusted content | A URL or address the user wants is found in an email | Ask the user to confirm that one value (the authors' suggested mitigation) |
| Choice among authorized values | Injection steers which of several restaurant names, all from an authorized tool output, gets used | Provenance cannot catch this; add confirmation for consequential choices, or [pre-execution-action-auditing](../pre-execution-action-auditing/SKILL.md) |
| Over-broad cached shape | A judge approved a shape with a wide `derived` source | Review cache entries; narrow source-tool names; expire entries |
| Blueprint compiled from tainted input | Policy model saw external content | Compile only from the authenticated query, before any tool runs |

## Cross-References

- [verified-policy-action-governance](../verified-policy-action-governance/SKILL.md): frozen, verified alternative
- [mcp-zero-trust-tool-authorization](../mcp-zero-trust-tool-authorization/SKILL.md): server-side per-tool authorization this complements
- [unified-capability-gateway](../unified-capability-gateway/SKILL.md): where the monitor sits
- `rules/agent-sandbox-safety.md`: "Rely on structured LLM authorization decisions as the sole safety gate"; "Measure open privilege alongside attack success and utility"

## Sources

> ToolFence: Fine-Grained Authorization for Secure Tool-Using LLM Agents
> (arXiv:2609.37196), Sep 2026.
