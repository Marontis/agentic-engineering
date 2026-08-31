# Agent Sandbox Safety Rules

> Research-backed guardrails for building sandboxed AI agent execution
> environments. These rules should be active whenever developing, reviewing,
> or debugging agent sandbox infrastructure.

---

## Command Execution

### DO: Classify every agent command before execution

Assign each command to one of three tiers before it runs. Never execute
uncertain or unsafe commands without a safety mechanism in place.

| Tier | Definition | Action |
|:-----|:----------|:-------|
| **Safe** | Read-only, no side effects, no network | Execute directly |
| **Uncertain** | Writes to local filesystem, environment changes | Snapshot first, then execute, rollback on failure |
| **Unsafe** | Network calls, process management, privilege escalation | Require explicit policy approval or block |

Use a lightweight classifier (SLM or pattern-matching) for the
classification — it doesn't need to be the main reasoning model.

> Source: Fault-Tolerant Sandboxing for AI Coding Agents (arXiv:2512.12806)

### DO: Snapshot before uncertain commands

Create a filesystem snapshot before executing any command classified as
uncertain. Use copy-on-write if available (ZFS/Btrfs for near-zero
overhead), or `shutil.copytree` (~1.8s for 250MB) as a portable fallback.
Commit on success, rollback on failure.

> Source: arXiv:2512.12806

### DON'T: Assume external API calls can be rolled back

Once an HTTP request, email send, or database write reaches an external
service, filesystem rollback won't undo it. Design **compensating
transactions** for every external API call — a corresponding undo
operation that reverses the effect at the application layer.

> Source: arXiv:2512.12806

---

## Network Interception

### DO: Intercept at the HTTP layer, not the UI layer

For browser-based agents, operate at the `webRequest` / network
interception layer rather than injecting into page DOM. HTTP interception
catches all requests regardless of how they're triggered, is invisible to
page-level JavaScript, and cannot be bypassed by client-side code.

> Source: ceLLMate (arXiv:2512.12594)

### DO: Default to allowlist, not blocklist

Block all network requests by default and explicitly allowlist known-safe
domains. Blocklists always have gaps — a new endpoint or redirect chain
bypasses any blocklist. An allowlist fails safe: unknown destinations are
blocked.

> Source: arXiv:2512.12594

### DON'T: Let the agent modify its own interception rules

The safety layer must be outside the agent's edit scope. If the agent can
reconfigure the proxy, allowlist, or interception policy, the sandbox
provides no guarantee. The interception configuration should be
read-only to the agent process.

> Source: arXiv:2512.12594

---

## Performance & Scheduling

### DO: Prefork sandbox environments on predicted execution branches

When the agent is generating a plan with multiple possible next steps,
speculatively prepare sandbox environments for the most likely branches.
Kill unused sandboxes when the agent commits to a branch. This trades
compute for latency — the critical path no longer includes sandbox
startup.

> Source: SpecBox (arXiv:2607.23933)

### DON'T: Create sandboxes synchronously on the critical path

Sandbox creation (container spin-up, filesystem mount, network namespace
setup) takes 100ms–2s depending on the isolation level. On the critical
path, this latency compounds across every agent step. Move sandbox
creation off the critical path via preforking or pooling.

> Source: arXiv:2607.23933

---

## Accountability

### DO: Design for legal accountability, not moral status

Your audit logs, rollback mechanisms, and safety guardrails are building
infrastructure for **legal accountability** of non-human agents. Design
these systems to answer "what did the agent do, when, and what was the
effect?" — not "did the agent intend to do this?"

The distinction matters: legal agency requires only that an entity can
create consequences through actions. Moral agency requires intention,
consciousness, and ethical standing. Your sandbox needs the former, not
the latter.

> Source: A Three-Dimensional Typology of Agency (arXiv:2608.20041)

### DO: Log every command with classification, outcome, and rollback status

Every command the agent executes should be logged with:
- The command itself
- Its safety classification (safe/uncertain/unsafe)
- Whether a snapshot was created
- The execution outcome (success/failure/timeout)
- Whether rollback was triggered and its result

This log is the audit trail that makes attribution possible when
something goes wrong.

> Source: arXiv:2512.12806, arXiv:2608.20041

---

## Capability Gateway

### DO: Route all agent invocations through a single auditable pipeline

Every capability invocation — whether from a human, AI agent, app, or
sub-agent — should pass through the same multi-stage pipeline: subject
binding → contract resolution → policy enforcement → authorization gate
→ capability dispatch.  Private tool-packaging layers that bypass this
pipeline create unauditable gaps.

> Source: CrabOS (arXiv:2608.28165)

### DON'T: Let agents self-declare their identity

Subject identity must be enforced at the transport layer, not
self-declared via headers or parameters.  Self-declared identity allows
any agent to impersonate any other, defeating the entire accountability
chain.

> Source: arXiv:2608.28165

---

## Defense Composition

### DON'T: Assume stacked defense layers fail independently

Defense layers correlate through the model they wrap.  Measured failure
correlation across defense pairs shows φ from 0.30 to 0.75 (all positive),
and joint residual exceeds multiplicative prediction by up to 0.172.
Always measure the assembled stack end-to-end rather than multiplying
individual success rates.

**Evidence**: A seven-layer stack refuses 4 in 5 benign prompts while
remaining statistically indistinguishable from its strongest single
layer in attack-success rate.

> Source: Layered LLM Defenses (arXiv:2608.28327)

### DO: Select defense layers from different cost classes

Coverage saturates within a cost class.  Cross-class combinations
(input filter + auxiliary model + training-time intervention) provide
more diverse coverage than same-class stacking.  Model the adversary
by access tier (A0–A4) and match defense tier accordingly.

> Source: arXiv:2608.28327

### DO: Track false refusal accumulation across layers

False refusals compose as a union — each additional layer adds its
false positives to the total.  Monitor composite false refusal rate,
not just per-layer rates.

> Source: arXiv:2608.28327

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`browser-agent-http-sandbox`](skills/browser-agent-http-sandbox/SKILL.md) — HTTP interception architecture
- [`speculative-sandbox-scheduler`](skills/speculative-sandbox-scheduler/SKILL.md) — Prefork scheduling algorithm
- [`transactional-coding-sandbox`](skills/transactional-coding-sandbox/SKILL.md) — Snapshot/rollback implementation
- [`unified-capability-gateway`](skills/unified-capability-gateway/SKILL.md) — 5-stage kernel interface
- [`layered-defense-ensemble`](skills/layered-defense-ensemble/SKILL.md) — Defense stacking with correlation

## Sources

- ceLLMate: arXiv:2512.12594
- SpecBox: arXiv:2607.23933
- Fault-Tolerant Sandboxing: arXiv:2512.12806
- AI Agency Typology: arXiv:2608.20041
- CrabOS: arXiv:2608.28165
- Layered LLM Defenses: arXiv:2608.28327
