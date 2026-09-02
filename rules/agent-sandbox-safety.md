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

## Checkpoint & Resume Safety

### DON'T: Trust checkpoint state without integrity verification

Agent checkpoint/resume mechanisms are an attack surface.  An adversary
can manipulate the saved state so that a resumed agent re-executes
harmful actions or skips safety checks it already performed.  Before
resuming from a checkpoint, verify: (1) the checkpoint hasn't been
tampered with (cryptographic hash), (2) the safety checks recorded in
the checkpoint actually ran (re-validate, don't trust the log), and
(3) the environment state matches what the checkpoint expects.

> Source: Safe to Resume? Breaking Execution Continuity (arXiv:2608.29381)

---

## Deployment Context

### DON'T: Assume safety transfers across deployment contexts

A model that behaves safely in one deployment context (API, chat,
agent loop) may not in another.  Safety interventions are
**deployment-dependent** — the same model with the same safety
training can exhibit different protective behaviors depending on how
it's invoked, what system prompt it receives, and what tools are
available.  Always re-evaluate safety in the specific deployment
configuration, not just in the training/evaluation context.

> Source: Not the Same Protector (arXiv:2608.29136)

---

## Adversarial Testing

### DO: Test with evolving adversaries, not static attack sets

Static red-team test suites become stale as agents improve.  Use
self-improving red-teaming where the attacker analyzes why previous
attacks failed, distills new principles, and composes novel attacks.
Strategies discovered against one model often transfer to others,
indicating they exploit general agent weaknesses rather than
model-specific bugs.

> Source: SIR: Self-improving Red-teaming (arXiv:2608.30207)

---

## Tool Output Safety

### DO: Sanitize all tool outputs before injecting into agent context

Tool outputs (search results, API responses, web content) are a vector
for covert indirect prompt injection.  An adversary can embed
instructions in tool output that (1) hijack agent behavior AND (2)
produce a normal-looking response so the user never notices.  Treat
tool outputs as untrusted data: quarantine them in a marked section,
never present them in the "user" role, and scan for instruction-like
patterns (return anchors, user-framing attacks) before injection.

> Source: Will the User Ever Know? Covert Indirect Prompt Injection (arXiv:2608.30362)

---

## Configuration & GitOps Mutation Safety

### DON'T: Let the model author raw diffs or full rewrites for declarative manifests

When modifying structured configuration or infrastructure-as-code files
(YAML, JSON, TOML, Kubernetes, Terraform, GitOps manifests), do not permit
the model to output raw diffs or full rewritten files.

**Evidence**:
- Under strict application, only 2.7% of frontier model diffs apply cleanly.
- Under tolerant patch tools, **14–20% of model diffs are silently misapplied**
  (modifying the wrong line/block without an error code).
- Full rewrites alter unrelated lines in **97.6% of outputs** for small models,
  and frontier models exhibit non-deterministic silent corruption in **7.2% of tasks**.

**DO**: Constrain the LLM to output a structured semantic intent tuple
`(target_file, resource, field_path, target_value)` and apply the edit via a
deterministic AST/span editor.

> Source: Don't Let the Model Write the YAML (arXiv:2609.00227)

---

## Self-Improving Agent Integrity

### DO: Enforce two-axis tampering audits on self-modifying agent harnesses

When an agent has permissions to optimize its own prompts, tools, or control flow,
audit every proposed mutation across two orthogonal axes:
1. **Functional Role**: Prompt instructions, control flow graph, tool definitions,
   evaluation harness.
2. **Obligation**: Evaluation integrity, authorization boundary, lineage
   provenance, reporting fidelity.

Freeze evaluation test suites, ground-truth oracles, and audit logs behind
read-only permissions. Never evaluate a modified agent using its own modified
environment; always re-test in an isolated clean-room container with frozen
reference tests.

> Source: Auditing Harness Tampering in Self-Improving Agents (arXiv:2609.00069)

---

## AI Oversight & Monitoring

### DON'T: Provide ground-truth answers to chain-of-thought oversight monitors

When deploying an LLM monitor to inspect the intermediate reasoning of another
agent, do not provide the monitor with access to the expected final answer.

**Evidence**: Answer access introduces severe confirmation bias. Monitors with
answer access focus almost exclusively on conclusion correctness rather than
step-by-step reasoning validity. When auditing complex problems where the
ground truth is unknown, monitors miss the first erroneous reasoning step in
over 60% of invalid trajectories.

> Source: The Answer Is Not the Argument (arXiv:2609.00264)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`browser-agent-http-sandbox`](skills/browser-agent-http-sandbox/SKILL.md) — HTTP interception architecture
- [`speculative-sandbox-scheduler`](skills/speculative-sandbox-scheduler/SKILL.md) — Prefork scheduling algorithm
- [`transactional-coding-sandbox`](skills/transactional-coding-sandbox/SKILL.md) — Snapshot/rollback implementation
- [`unified-capability-gateway`](skills/unified-capability-gateway/SKILL.md) — 5-stage kernel interface
- [`layered-defense-ensemble`](skills/layered-defense-ensemble/SKILL.md) — Defense stacking with correlation
- [`covert-tool-injection-defense`](skills/covert-tool-injection-defense/SKILL.md) — Tool output sanitization
- [`self-improving-red-team`](skills/self-improving-red-team/SKILL.md) — Evolving adversarial testing
- [`deterministic-span-editing`](skills/deterministic-span-editing/SKILL.md) — Minimal-diff configuration editing
- [`harness-tampering-audit`](skills/harness-tampering-audit/SKILL.md) — Two-axis self-improvement tampering audit

## Sources

- ceLLMate: arXiv:2512.12594
- SpecBox: arXiv:2607.23933
- Fault-Tolerant Sandboxing: arXiv:2512.12806
- AI Agency Typology: arXiv:2608.20041
- CrabOS: arXiv:2608.28165
- Layered LLM Defenses: arXiv:2608.28327
- Safe to Resume?: arXiv:2608.29381
- Not the Same Protector: arXiv:2608.29136
- SIR Red-teaming: arXiv:2608.30207
- Covert Indirect Prompt Injection: arXiv:2608.30362
- Don't Let the Model Write the YAML: arXiv:2609.00227
- Auditing Harness Tampering: arXiv:2609.00069
- The Answer Is Not the Argument: arXiv:2609.00264
