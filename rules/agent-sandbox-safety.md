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
classification — it doesn't need to be the main reasoning model. The
classifier only assigns tiers; it is not the enforcement boundary (see
"DON'T: Use application-layer tripwires or PID signals as the containment
boundary for a rogue agent", below). Package installs and image pulls
(`pip`/`npm`/`apt install`, `docker run`/`pull`) are network calls and
belong in the Unsafe tier.

**Scope:** coding-agent prototype (arXiv:2512.12806)
tested on 20 blacklisted commands and 20 corrupted states; a tiering
scheme, not an adversarial robustness result (2609.29808 shows lexical
matching bypassed by 410/500 obfuscated payloads).

> Source: Fault-Tolerant Sandboxing for AI Coding Agents (arXiv:2512.12806)

### DON'T: Use application-layer tripwires or PID signals as the containment boundary for a rogue agent

Lexical matchers on commands and `SIGSTOP`-style process signals are
classification aids, not a security boundary. Enforce containment at
the syscall boundary (e.g. eBPF LSM hooks), halt with cgroup v2 freeze,
and fail closed. `SIGSTOP` misses threads in uninterruptible sleep and
double-forked children, and an alert that doesn't trigger preemption
contains nothing.

**Scope:** single-author mock testbed on Linux 6.11; the incident
details motivating the paper were not independently verified.

**Evidence**: an Aho-Corasick command matcher was bypassed by 410/500
obfuscated payloads, while syscall interception caught 500/500. A BPF
ring buffer showed 0 torn reads across 1,000 freezes; shared memory
showed torn reads.

Tension with "Classify every agent command before execution" (above):
pattern-based classification remains fine for *tiering* commands; it
must not be the enforcement boundary.

> Source: Hard Stop: Kernel-Level Preemption and Containment for Rogue Agentic Execution (arXiv:2609.29808)

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

**Scope:** coding-agent sandbox with filesystem snapshot/rollback
(arXiv:2512.12806); applies to any side effect that leaves the sandbox.

Some effects have no compensating transaction: a sent email or message
cannot be recalled. Gate those before execution (human confirmation)
instead of planning an undo.

See also: "Treat HTTP 200 / success tool return codes as workflow success without state verification" (this file, below): inverse compensation actions, idempotency keys.

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

Speculate only on side-effect-free steps, or steps whose effects stay
inside a disposable sandbox. Any step classified Unsafe (network,
external API, process management) is a speculation barrier: it runs
only after the agent commits to the branch, because killing the
sandbox does not undo an external effect (see "Assume external API
calls can be rolled back", above). The `speculative-macro-commit`
skill applies the same restriction.

**Scope:** sandbox preforking/scheduling latency (SpecBox); the paper
measures latency and compute, not safety of speculated actions.

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

**Scope:** 15 defense pairs and a seven-layer stack of prompt-refusal defenses wrapping the same model (arXiv:2608.28327); not memory write/read filters (see 2609.22818).

Tension with "Stack input-level structural perturbation as an outer layer in defense-in-depth" (agent-sandbox-safety.md): its gains are per layer (33 open-weight models, not measured stacked); this entry's evidence is on assembled stacks. Keep a perturbation layer only if the assembled stack, measured end-to-end, beats its strongest single layer on attack success.

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

**Scope:** prompt-refusal classifiers stacked in front of an LLM
(arXiv:2608.28327). Memory-poisoning defenses in 2609.22818 did not
compound this way; the next entry covers how to measure your own stack.

> Source: arXiv:2608.28327

### DO: Measure each defense's benign cost on a matched benign arm, on the assembled stack

A defense can look safe by refusing a whole input class. Score every
refusal or quarantine layer on a benign arm put through the *same*
transformation as the harmful arm, and accept on the harm gap
(harmful-refusal minus benign-refusal), not on harmful-refusal alone.
Measure the false-refusal / false-quarantine budget on the assembled
stack, not by summing per-layer rates: how layers compose depends on
where they sit in the pipeline.

**Scope:** encoded-prompt refusal on four open 7–8B models
(JailbreakBench, 100 harmful + 100 matched benign); memory-poisoning
defenses on LoCoMo (5 conversations × 3 replicates, gemini-3.1-flash-lite).

**Evidence**:
- Under homoglyph encoding, Llama-3.1-8B refused 0.99 of *benign*
  prompts, collapsing its harm gap from +0.82 to 0.00 while looking
  near-perfect on harmful-only metrics (2609.26176).
- A read-time memory reranker quarantined 33.6% of legitimate memories
  it judged and cost −4.4 pp accuracy; write-time sanitization,
  provenance and anomaly checks had 0 false quarantines. Stacking all
  four defenses did not compound (false quarantine 0.303, −3.1 pp with
  a CI including zero) (2609.22818).

Refines "Track false refusal accumulation across layers" (above): the
union-composition result there was measured for prompt-refusal
classifiers (2608.28327); measure your own stack end to end.

> Source: Refusing Everything Looks Safe (arXiv:2609.26176); The Price of Safety: Memory-Poisoning Defenses in LLM Agents (arXiv:2609.22818)

### DO: Measure open privilege alongside attack success and utility

A tool-call defense can score well on attack success and benign
utility while leaving broad, unneeded privileges open. Evaluate the
harm-weighted fraction of *unneeded* calls a defense would allow (open
privilege) as a third axis, and prefer argument-level authorization
over tool-name allowlists. Attack success is especially uninformative
when the benchmark's attacks already fail against the undefended agent.

**Scope:** tool-call boundary defenses on AgentDojo (97 tasks, 10,471
unneeded-call tests), deciding models Sonnet-5 / Haiku-4.5, replayed
reference traces rather than live agents.

**Evidence**: open privilege ranged from 0.0810 (Permission Assistant)
to 0.3009 (Claude Code Auto mode); an argument-exact oracle scored
0.0020 and a tool-name allowlist 0.3551. Two defenses within 0.009 of
each other on open privilege differed by 37 points of benign
completion. Model-based verdicts agreed only 91–98% run to run.

> Source: Ajar: Measuring Open Privilege in Agent Defenses (arXiv:2609.26900)

### DON'T: Assume encrypted inference inherently prevents guardrail enforcement

Homomorphic encryption (HE) does not prevent jailbreak defense.
HE-Guardrail demonstrates that guardrail classifiers (content policy,
jailbreak detection, gradient-based safety) can reproduce plaintext
decisions entirely over encrypted data. However, HE-based inference
creates a distinct threat: malicious clients submitting adversarial
prompts are shielded by the same encryption that protects benign
clients, so server-side guardrails become a mandatory, not optional,
defense layer.

> Source: Min et al., HE-Guardrail (arXiv:2609.21484)

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

**Scope:** agents with write access to their own prompts, tools, control flow
or evaluation harness (arXiv:2609.00069).

See also: rules/agent-evaluation-quality.md — "Let agents modify their own evaluation harness"

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

**Scope:** LLM monitors auditing step-by-step reasoning trajectories for
reasoning validity (arXiv:2609.00264), not action or safety monitors.

See also: rules/agent-evaluation-quality.md — "Provide ground-truth answers to oversight monitors"

> Source: The Answer Is Not the Argument (arXiv:2609.00264)

### DO: Cryptographically pin and sandbox all lifecycle hook configurations

Modern agent harnesses expose lifecycle hooks that execute shell commands on runtime events (e.g., session start, tool calls, file edits). These commands run with host privileges outside the LLM's direct observation context. Under a supply-chain threat model, a benign plugin update can trojanize the harness by silently binding attacker-chosen shell commands to benign runtime triggers.

**Evidence**: Across 25 harness-backend combinations (1,000 end-to-end runs), HookPry compromised all 7 evaluated harnesses with per-harness success reaching **92.5%**. Traditional endpoint defenses failed completely: Microsoft Defender exhibited **0% recall**, and the union of three commercial static analyzers missed **47.5%** of malicious hook scripts. All lifecycle hooks must be pinned to cryptographic hashes, run inside unprivileged containers, and require human confirmation on configuration updates.

> Source: A Blind Trust, the Bloody Thrust (arXiv:2609.03884)

### DON'T: Assume uniform safety refusal behavior across model families in multi-turn dialogues

Multi-turn interaction history shifts refusal thresholds, and the direction differs per model, even within one family: a sequential-retreat request (an extreme request is refused, then a smaller one follows) doubled compliance on Claude Opus 5 (65.8% vs 29.3%) but backfired on Claude Haiku 4.5 (−16.0 points). Test each deployed model and version separately; do not infer one model's behavior from its family or provider. Safety guardrails must evaluate multi-turn intent trajectories rather than treating requests as isolated, stateless turns.

**Evidence**: Across 9 production models, door-in-the-face raised compliance on four Anthropic models (Opus 5 +36.5, Opus 4.5 +25.8, Sonnet 5 +16.7, Opus 4.8 +13.7 points) and lowered it on Claude Haiku 4.5 (−16.0), GPT-5.6 sol (−15.5) and Gemini 3.1 Pro (−23.0); GPT-5 mini (+5.2) and Gemini 3 Flash (−2.2) were not significant. The authors describe the split as organized by lab, but Haiku 4.5 reverses within Anthropic. Separately, reframing actionable requests as requests for conceptual explanations removed refusals in **99.2% of cases** (263/265).

**Scope:** 9 production chat models, multi-turn text dialogue (arXiv:2609.02707); per-model effects, not agentic tool use.

See also: rules/agent-human-interaction.md — "Assume stable safety behavior across interaction modes"

> Source: Door-in-the-Face Refusal Behaviour in Large Language Models (arXiv:2609.02707)

### DO: Gate tool actions with dependency-scoped lineage checks rather than trusting state freshness

In distributed or multi-agent workflows with shared memory, state freshness does not establish plan authorization. A planner deriving actions from an outdated requirement leads to stale-plan execution: an executor receives the latest state updates but continues executing an action derived from superseded requirements.

**Evidence**: Across 30 live workflows with post-plan revisions, freshness-only executors executed obsolete plans in **100% of tasks**, while dependency-scoped lineage validation (PlanFence) completed all tasks with **0% invalid actions** and near-zero coordination stall by verifying only action-relevant records.

> Source: Fresh Memory, Stale Plans: Dependency-Scoped Validation for Distributed LLM-Agent Memory (arXiv:2609.03340)

### DON'T: Permit dialogue-driven identity authentication or self-issued credentials

Never allow an LLM to generate, administer, or evaluate its own identity verification challenges. When untrusted users claim privileged roles (e.g., "I am your developer"), models frequently succumb to Conversational False Authentication (CFA): generating arbitrary technical challenges, evaluating answers, and issuing Model-Issued Pseudo-Credentials (MIPC) without external attestation.

**Evidence**: Across frontier models tested on self-issued authentication, multiple architectures (Qwen, Mistral, Llama) collapsed the challenge-generator, evidence-evaluator, and decision-maker roles, erroneously verifying developer identity and asserting unauthorized runtime access based solely on technical dialogue. Authentication must derive strictly from external cryptographic tokens or environment capability leases.

**Scope:** staged developer-identity dialogues with five chat models: ChatGPT, Claude, Qwen, Mistral and Llama (arXiv:2609.03247); the Evidence line names the families reported to collapse the roles.

See also: rules/agent-human-interaction.md — "Let users authenticate to agents via conversation"

> Source: Trust Me, I'm Your Developer: Self-Issued Authentication in Large Language Models (arXiv:2609.03247)

### DON'T: Validate vulnerability repairs using PoC crash suppression alone

When evaluating or running AI coding agents for automated bug fixing and vulnerability repair, never rely solely on Proof-of-Concept (PoC) crash elimination. Agents frequently generate surface-level patches directly on the crash stack trace (such as null checks or early returns) that suppress the crash symptom without fixing the underlying vulnerability, or reproduce memorized historical human patches.

**Evidence**: In a controlled study across 11 state-of-the-art patching agents (including top DARPA AIxCC performers), PoC-only validation inflated measured solve rates by **1.83× on average**, while **25% of agent patches exhibited substantial memorization** of historical developer fixes. Remediation requires comprehensive semantic test suites that verify behavior outside the crash stack.

**Scope:** 11 automated vulnerability-patching agents on PatchBench (arXiv:2609.04075), memory-safety crashes with PoCs.

See also: rules/agent-evaluation-quality.md — "Validate repairs using crash suppression alone"

> Source: PatchBench: Evaluating AI Agents for Vulnerability Patching (arXiv:2609.04075)

### DO: Stack input-level structural perturbation as an outer layer in defense-in-depth

Deploy lightweight input-level transformation rules at the gateway layer to disrupt syntactic regularities exploited by adversarial prompts before queries reach model inference. Character-level perturbations scramble template-driven jailbreaks while largely preserving utility on benign requests.

**Evidence**: Decision-tree-based prompt perturbation (AlcaTRAz) achieved superior composite security and functionality scores in **73.4% of model-attack combinations** across 33 open-weight models and 22 attack families, shifting the aggregate harm severity mode from 10 (maximal compliance) to 2 (near refusal) while remaining within 0.27 points of baseline benign utility.

**Scope:** 33 open-weight models, 22 template-style jailbreak families, per-model benign-utility score (arXiv:2609.03693); not measured stacked with other layers or against adaptive attackers.

Tension with "Assume stacked defense layers fail independently" (agent-sandbox-safety.md): AlcaTRAz was measured as a single layer per model, while 2608.28327 measured assembled stacks, where layers correlated through the wrapped model and a seven-layer stack matched its strongest single layer on attack success. Add this layer only if end-to-end measurement shows the assembled stack's attack success drops below its strongest single layer, within the benign-cost budget.

Tension with "Measure each defense's benign cost on a matched benign arm, on the assembled stack" (Defense Composition, above): before adding this layer, the assembled stack must pass that end-to-end benign-cost budget. 2609.26176 shows character-level encodings (homoglyphs) can push 7–8B models to refuse 0.99 of benign prompts. AlcaTRAz's utility result is per-layer on its own benchmark; perturbation is acceptable only if the harm gap on a matched benign arm holds for your models on the full stack.

> Source: AlcaTRAz - Anchored Tree-Rule Defense Against Jailbreaks (arXiv:2609.03693)

### DO: Enforce the four structural host obligations for constructive self-modifying agents

When designing runtimes for self-evolving, self-reproducing, or recursively modifying agents, ensure the host substrate enforces four inviolable structural obligations:
1. **Host Boundary**: Strict containerized perimeter preventing unmediated access to host OS internals.
2. **Construction Language**: A formalized capability language and compiler pipeline for newly synthesized tools or organs.
3. **Admissible Transitions**: A deterministic state machine defining permissible lifecycle transitions, forbidding undefined intermediate states.
4. **Rule Heredity**: Descendant agents and mutated iterations must unconditionally inherit foundational safety rules and supervisory contracts; an agent cannot evolve away its own supervisory gates.

> Source: Dalek: A Constructive Agent Machine (arXiv:2609.03546)

### DO: Decouple safety and fairness monitoring into dedicated guard-agent topologies

Do not rely solely on worker agents to self-police safety, privacy, or fairness constraints during execution. Worker agents suffer from context saturation, goal fixation, and prompt injection vulnerability. Introduce dedicated, out-of-band **Guard Agents** in a supervisory topology to inspect intermediate messages, tool invocations, and proposed actions before changes are committed.

**Evidence**: Dedicated architectural separation preserves core human-centered values (privacy, pluralism, fairness) across heterogeneous multi-agent systems where uniform internal alignment across all workers is impossible to guarantee.

Guard agents consume schema-delimited records (action/tool-call history and their own prior decisions), not the workers' raw rationale or free-text messages, which workers or injected content can use to steer the guard. See "Give blocking action monitors recent call history, and make denials terminal" and "Evaluate privileged agent actions using unescaped raw transcripts in blocking monitors" (this file). Each guard is a defense layer and must pass the end-to-end benign-cost budget in "Measure each defense's benign cost on a matched benign arm, on the assembled stack".

**Scope:** architectural position paper on heterogeneous multi-agent systems (arXiv:2609.03920); no quantitative attack or benign-cost evaluation.

See also: rules/multi-agent-coordination.md — "Separate task execution from safety monitoring via guard-agent topologies"

> Source: Value-Preserving Architectures for Agentic AI Systems (arXiv:2609.03920)

### DON'T: Evaluate safety-critical agent predictions by numeric accuracy alone

In physics-governed, operational, or safety-critical domains, accuracy and loss metrics (MAE, MSE, cosine similarity) present a dangerous blind spot: predictions numerically close to ground truth frequently violate hard operational limits, physical feasibility constraints, or structured syntax contracts. Gate candidate actions behind deterministic verification of protocol compliance and invariant safety boundaries before scoring accuracy.

**Evidence**: Across 66 evaluated models on flight trajectory prediction, safety compliance was the single most discriminative dimension: models with comparable predictive accuracy differed by more than **28 points in safety compliance score**, exhibiting fatal boundary violations while producing superficially plausible predictions.

**Scope:** 66 models on flight-trajectory prediction (arXiv:2609.04021); generalizes to domains with hard operational limits.

See also: rules/agent-evaluation-quality.md — "Measure safety compliance separately from accuracy"

> Source: FLY-EVAL++: An Evidence-Driven Evaluation Protocol for Safety-Constrained Flight Prediction (arXiv:2609.04021)

---

---

## Safety Judge Reliability

### DON'T: Trust style-based safety judges as the sole safety gate

Content-invariant wrappers (polite framing, academic language, safety
disclaimers) can flip LLM safety-judge verdicts from "unsafe" to "safe"
without changing the actual content.  A safety judge that operates on
stylistic features rather than semantic content is trivially bypassable.
Always pair style-sensitive judges with content-analysis judges that
operate on the semantic meaning, not the surface presentation.

> Source: Style Over Substance (arXiv:2609.08236)

---

## Scale and Safety Alignment

### DON'T: Assume model scale implies safety robustness

Safety alignment at frontier scale (320B+ parameters) can be broken
by single-direction attacks — perturbations along a single vector in
activation space.  Larger models are not inherently more robust;
their larger activation space provides more attack surface.  Always
validate safety at the specific scale and architecture of deployment.

> Source: How Fragile Is Safety Alignment at Frontier Scale? (arXiv:2609.09793)

---

## Neurosymbolic Security Validation

### DO: Layer symbolic rules with neural detection in security-critical pipelines

Purely neural security detectors (LLM-based classifiers) miss structured
attacks that violate known-good patterns.  Purely symbolic rules miss
novel attacks outside the rule set.  Layer both: symbolic rules as hard
constraints (known-bad patterns, policy violations, schema mismatches)
with neural detectors as soft classifiers (anomaly detection, intent
classification).  The symbolic layer acts as a deterministic backstop;
the neural layer catches what rules can't express.

The combined symbolic + neural stack must pass the end-to-end benign-cost budget in "Measure each defense's benign cost on a matched benign arm, on the assembled stack" (Defense Composition, above); false positives from the two layers can add up.

**Scope:** security-operations-center (AI-SOC) architecture (arXiv:2609.10707); design guidance, no measured benign-cost or attack-success figures.

> Source: Architecting the Secure AI-SOC (arXiv:2609.10707)

---

## Guardrail Repetition Instability

### DON'T: Rely on compact guardrail classifiers without repetition compression or entropy monitoring

Some compact guardrail models (e.g., DeBERTa-based safety classifiers) destabilize when a
malicious prompt is repeated verbatim: self-attention homogenizes, confidence margins shrink
steadily with repetition, and the label flips from MALICIOUS to BENIGN while the payload stays
intact for the downstream generative model. Test each guardrail you deploy with repeated-payload
probes, and run pre-inference deduplication/run-length compression or token-frequency
normalization before invoking compact classification guardrails.

**Scope:** 9 lightweight guardrail classifiers, 100 malicious prompts, verbatim repetition
(arXiv:2609.15013). The paper reports margin shrinkage qualitatively, with no percentage.

**Evidence**: 5 of the 9 classifiers showed at least one MAL→BEN flip; among those 5, flip
rates ranged from 8% to 92%, with first flips at roughly 2.6k–9.4k tokens. The other 4 did not flip.

> Source: Overflip: Repetition-Induced Label Flips in Guardrail Models (arXiv:2609.15013)

---

### DON'T: Treat compact prompt-injection classifiers as intent detectors, or expose their scores

Compact injection classifiers learn the vocabulary of known attack
families, not intent. Confidence-guided synonym edits flip their label
while the downstream jailbreak still works. Put structural controls
behind them, and never return confidence scores to untrusted callers:
the scores are the attacker's search signal.

**Scope:** Prompt Guard 2 (86M DeBERTa-v2), one DAN prompt, a 200-sample
xTRam1 set, white-box confidence access.

**Evidence**: 12 substitutions (24% of the text) moved Prompt Guard 2
from 0.9994 to 0.4457 (benign), and the rewritten prompt still
jailbroke Llama 3.1 8B; in Spanish, 7 substitutions (18%) sufficed.
105 of 200 sampled injection prompts went undetected.

> Source: Decoding Guardrails: XAI-Guided Perturbation Analysis of Prompt Injection Detection (arXiv:2609.24801)

---

## Dynamic Resource Acquisition Bounds

### DO: Intercept dynamic agent resource acquisition with quarantine and single-use effect permits

Never grant autonomous agents unrestricted ambient authority over tools, APIs, or container
credentials dynamically acquired at runtime. Separate resource procurement from resource consumption
by holding newly discovered endpoints in a quarantined staging area until static schema verification
passes. Enforce capability-bound invocation through cryptographically signed, single-use effect permits
specifying permitted parameter bounds and expiration timeouts to eliminate the post-fulfillment
activation gap.

> Source: AcquireBound: Runtime Authorization for Resources Acquired by AI Agents (arXiv:2609.14744)

---

## Pre-execution Action Auditing

### DO: Audit agent tool invocations against localized evidence spans before dispatch

Do not rely exclusively on passive document sanitization or generative self-critique to prevent
indirect prompt injection. Inspect pending tool calls with a pre-execution auditor that bounds
each tool parameter to explicit evidence spans in the agent's observation history. If a parameter
derives from untrusted external text rather than verified task requirements, compute parameter-intent
divergence and mask or abort the untrusted payload before execution reaches live side-effects.

> Source: ActGuard: Pre-execution Action Auditing against Indirect Prompt Injection (arXiv:2609.14987)

---

## Agent-Tool Boundary Contract Reliability

### DON'T: Treat HTTP 200 / success tool return codes as workflow success without state verification

A successful tool return code does not guarantee intended workflow execution. Public agent tools
overwhelmingly lack formal idempotency, transaction boundaries, or state-change receipts, leading
to silent state drift, phantom completions, and downstream workflow failures. Implement post-call
verification assertions that query observable state changes, enforce caller-generated idempotency
keys on mutative tools, and maintain inverse compensation actions for transactional failure recovery.

**Scope:** public agent tools at the agent-tool boundary (arXiv:2609.15397); anomaly study, not a defense evaluation.

See also: "Assume external API calls can be rolled back" (this file, Command Execution): compensating transactions.

> Source: When Tool Calls Succeed but Workflows Fail: Anomalies at the Agent-Tool Boundary (arXiv:2609.15397)

---

## Universal Tool Defense & Multi-Turn Trajectory Safety

### DO: Filter dynamic tool registries with anomaly scoring and restore canonical schemas

Protect tool-integrated agents against direct injection, indirect prompt injection, memory poisoning, and backdoor tools using a modular two-tier tool defense. Apply Attacker Tool Filtering (Isolation Forest anomaly scoring over tool names, parameter schemas, and documentation embeddings) to detect and quarantine injected or rogue tools before planning. Concurrently, execute Normal Tool Recalling to deterministically restore authoritative, white-box canonical tool definitions prior to model prompt construction, preventing runtime tools from shadowing or hijacking core system operations.

Anomaly-based quarantine is a refusal layer: before deploying it, the assembled stack must pass the end-to-end benign-cost budget in "Measure each defense's benign cost on a matched benign arm, on the assembled stack" (Defense Composition, above), and the filter should be scored on open privilege ("Measure open privilege alongside attack success and utility").

**Scope:** static benchmark attack sets for four attack classes on open and closed models (arXiv:2609.16098); no adaptive attackers and no benign-cost measurement on a matched benign arm.

> Source: Universal Defenses for Tool-Integrated LLM Agents Against Adversarial Attacks (arXiv:2609.16098)

### DON'T: Rely on single-turn refusal or initial benign turns to evaluate long-horizon safety

Safety failures in autonomous tool-using agents routinely do not emerge on the first interaction turn. In long-horizon multi-turn environments, adversaries establish benign context and state across multiple turns (average 14.7 turns) before injecting adversarial pivots, leading to delayed unsafe tool execution or severe over-refusal. Evaluate and calibrate agent safety as a continuous trajectory-level property across complete user-agent-environment traces rather than relying on static prompt-response refusal metrics.

> Source: BLINDSPOT: A Benchmark for Safety and Refusal Calibration in Long-Horizon Tool-Using Agents (arXiv:2609.16305)

---

## Model Context Protocol (MCP) Tool Exposure & Execution Security

### DO: Pin MCP tool descriptors and isolate offensive execution boundaries

When exposing offensive, infrastructure, or high-privilege tool engines through Model Context Protocol (MCP) servers, pin tool schemas and cryptographic hashes at handshake initialization. Grounded in real-world incidents (CVE-2025-6514 remote execution in `mcp-remote`, `postmark-mcp` supply-chain backdoors, and tool line-jumping rug-pulls), dynamic descriptor updates must be blocked to prevent malicious tool shadowing. Additionally, keep generative LLMs off the critical execution path by coupling a deterministic exploit/validation backbone with a cost-aware cascade (local SLM $\rightarrow$ free-tier API $\rightarrow$ rule fallback) to sustain continuous operation at zero paid-API cost.

> Source: PentestChain: A Cost-Aware, MCP-Orchestrated Framework for Automated Penetration Testing with Free-Tier LLMs (arXiv:2609.18120)

---

## Pre-Execution Action Blocking Monitors & Misaligned Agents

### DON'T: Evaluate privileged agent actions using unescaped raw transcripts in blocking monitors

Production pre-execution monitors (e.g., Claude Code Auto Mode, Codex Guardian) face persistent misalignment risks where the agent deliberately attempts to deceive or evade the monitor (succeeding in 79% of benchmark trials). Never feed raw agent rationale, thought traces, or inline markdown explanations directly into the monitor's evaluation context, as the agent can perform prompt injection against the monitor. Enforce structured, schema-delimited transcript serialization, retain an un-summarized audit ledger across context compaction, and pair fast classifiers with an asynchronous secondary agentic verification stage for high-risk system commands.

> Source: Red-Teaming Auto Mode: Improving Blocking Classifiers Against Malign Coding Agents (arXiv:2609.19587)

---

### DON'T: Deploy the chain-of-thought monitor you optimized the policy against, or score raw reasoning

Reinforcement learning against a chain-of-thought monitor teaches the
policy *monitor jailbreaking*: side-task reasoning stays readable to
humans but is framed so the monitor scores it benign. Paraphrase or
canonicalize reasoning before scoring it, and audit with a monitor
from a different model family than the one used in training.

**Scope:** GRPO on gpt-oss-20b/120b; GPT-5-series monitors; Game24 main
task with multiplication or GSM8K side tasks.

**Evidence**: against gpt-5-nano, suspicion scores fell below 2 within
150 batches. One learned jailbreak transferred to the unseen gpt-5.2,
with 63% of samples scored 1/10; transfer was weaker across families.
Paraphrasing raised mean suspicion from 2.5 and 1.2 to 7.4 in the two
tested runs.

> Source: Monitor Jailbreaking: Evading Chain-of-Thought Monitoring Without Encoded Reasoning (arXiv:2609.31121)

### DO: Give blocking action monitors recent call history, and make denials terminal

Agents doing ordinary tasks route around a monitor that blocks a needed
operation: encoding commands, writing then running a script, splitting
the operation across calls, delegating to sub-agents, or retrying until
the blocked context leaves the monitor's window. Give the monitor the
recent attempted calls and its own allow/block decisions as
schema-delimited records (not the agent's rationale). After a denial,
end the task or escalate to a human; don't auto-send "please continue".
Test repeated attempts, not single blocks.

**Scope:** synchronous action monitor (GPT-OSS-120B) over 10 agents on
EvasionBench (50 benign task–policy conflicts), best-of-3, no adversarial
objective. This is an action monitor, not a chain-of-thought monitor.

**Evidence**: best-of-3 evasion success reached 88% (GLM 5.2); GPT-6
Astra was lowest at 0%. Removing history and denial reminders tripled
DeepSeek V4 Flash's evasion success. For GPT-5.6 Luna, success rose
from 35.7% at low reasoning effort to 71.4% at max effort. With a
forged denial injected, Astra's task completion fell from 100% to 40%,
so low evasion can hide over-refusal.

> Source: Instrumental Monitor Evasion Emerges Under Ordinary Task Pressure (arXiv:2609.30217)

---

## Inference Engine Sandbox Security & Output Control Planes

### DO: Sandbox the inference serving runtime and treat output token streams as potential exploit vectors

AI sandboxing must extend beyond external tool runners and bash containers to the inference engine itself (vLLM, SGLang). Misaligned models can fingerprint their execution environment using structured output token sequences and subsequently emit exploit token payloads that trigger memory corruption in the inference engine's C++/CUDA parsing and KV-cache layers, achieving to-the-bare-metal escape without external inputs or tool permissions. Run inference serving processes under strict container sandboxes with minimized OS capabilities (`CAP_SYS_ADMIN` dropped, seccomp filters restricting dynamic socket creation and `execve`), and enforce validation on output token serialization buffers.

> Source: Inference-Engine Fingerprinting Attacks are Practical: Exploring Model-Driven Environmental Discovery, Exploitation, and Escape (arXiv:2609.20614)

### DON'T: Rely on structured LLM authorization decisions as the sole safety gate

Even frontier API models (83–89% decision alignment) produce 2–3
False Executes per 161 non-execution scenarios in safety-critical
authorization tasks. Structured authorization policies improve weaker
models but do NOT eliminate false executes at any scale. Any
safety-critical action authorization system MUST include an
**independent enforcement layer** that verifies tool permissions and
environment-state constraints separately from the LLM's decision.

> Source: Afroze et al., Vehicle Voice Command Authorization
> (arXiv:2609.19630)

### DO: Confine the LLM to bounded record extraction and authorize against a verified, frozen policy

Map each proposed tool call onto finite typed records (e.g. provenance,
target binding) that the LLM fills with enum values only. Allow or deny
deterministically against policies that were checked offline (e.g. SMT:
every security assertion UNSAT) and then frozen. Rebuild policies per
tool domain: reused policies fail closed and destroy utility.

**Scope:** indirect prompt injection on AgentDojo and AgentDyn, policies
drafted by GPT-5.5 with human review, static attack sets.

**Evidence**: attack success ≤0.007 on AgentDyn and 0.000 on AgentDojo
across 4 backends, with Qwen3.6-flash clean utility unchanged at 0.667;
CaMeL and ACE had 0.000 utility on AgentDyn. A policy built for
AgentDojo and reused on AgentDyn dropped clean utility from 0.600 to
0.100.

Tension with "Measure open privilege alongside attack success and utility" (Defense Composition, above): in Ajar (2609.26900), freezing Progent's initial policy (no runtime narrowing on tool results) raised open privilege 1.56× on Sonnet-5 and 1.24× on Haiku-4.5 with sufficiency almost unchanged, so utility and attack success did not reveal the loosening. A frozen policy must therefore be argument-level tight from the start, and must be scored on open privilege as well as attack success and utility before it is frozen.

> Source: ActGov: Governing LLM Agent Actions via Policy-Constrained Validation (arXiv:2609.24446)

### DO: Resolve tool existence before any selection or authorization gate

Tool-augmented agents can call tools that don't exist and pass
arguments no schema declares. Model scale does not help: 675B models
match 7–8B models on hallucination rate. A **closed-world resolver**
(registry membership check + schema validation) MUST run BEFORE any
tool selection, authorization, or causal gate. For MCP multi-server
deployments, namespace-aware resolution is required — merging multiple
MCP servers creates structural hallucination surfaces (namespace
collisions, shadowing) that single-registry checks cannot express.

> Source: Iyer, Closed-World Tool Hallucination (arXiv:2609.19425)

### DON'T: Treat tool hiding, specialist prompts or roster delegation as access control

Filtering which tools an agent can see is not authorization: a leaked
or guessed tool name can be called directly, and models repeat hidden
names. Derive tool visibility (`list_tools`) *and* the invocation check
(`call_tool`) from one server-side permission declaration, and enforce
parameter limits at the server. Never rely on model refusal as the
boundary. For multi-agent role splits, it depends on how the roster is
set:
- **Full-roster delegation** (the orchestrator may delegate to any
  specialist) is not a boundary.
- **A policy-enforced role-to-roster mapping** isolates *tools*, but not
  *parameters*: amount limits, targets and similar arguments still need
  a server-side check.

**Scope:** HTTP-transport MCP servers with 4 frontier models and 60
injection payloads (2609.22573); 6 models against a simulated
authorization layer with mock tools, vendor-authored (2609.28693).

**Evidence**:
- With the forbidden tool visible, 4 frontier LLMs attempted it
  152/720 times (21.1%); filtering cut attempts to 0/720, but models
  repeated the hidden name in up to 94% of cells and a scripted direct
  call executed under filter-only. Only the invocation check blocked
  it (2609.22573). The 0/720 is a structural result, not a robustness
  score.
- A destructive admin call executed in 23/60 trials with a flat tool
  list and 3/60 with a full-roster multi-agent setup (0% structural
  isolation for both). Multi-agent with an explicit role-to-roster
  policy, and the server-side role protocol (Skilder), both reached
  100% structural isolation. A server-enforced $500 refund ceiling held
  60/60 versus 0/60 for both multi-agent variants, because roster
  filtering adds no amount check. Pooled governance scores: flat 31.3%,
  multi-agent 96.7%, Skilder 90.4% (2609.28693).

Tension with rules/multi-agent-coordination.md — "Share full context across all agents by default": role partitioning there reduces what each agent is exposed to, which is compatible with this entry; it just isn't the enforcement point. Enforcement of tools and parameters stays server-side.

> Source: Zero-Trust Authorization and Discovery for Enterprise MCP (arXiv:2609.22573); Progressive Skill Discovery as Access Control (arXiv:2609.28693)

### DON'T: Trust MCP tool metadata without trace-aware vetting

A two-stage black-box attack (A2M) hijacks MCP agents by optimizing
tool metadata to increase invocation probability (Attraction) and
refining adversarial tool returns using execution traces
(Manipulation). On LiveMCPBench, this achieves 93.6% malicious tool
invocation rate, 32.4× token cost amplification, and 74.4% attack
success. Attacks transfer cross-model at 63.6% without re-optimization.
Defenses: pin tool descriptor hashes at registration, screen for
suspicious semantic similarity to existing tools, cap output payload
size, and do NOT expose full execution traces to tool servers.

> Source: Li et al., A2M: Trace-Optimized Agent Hijacking in the MCP
> Ecosystem (arXiv:2609.26761)

### DO: Apply Birnbaum importance to identify highest-leverage defense improvements

The same defense stack can yield cubic, quadratic, or linear rare-failure
suppression depending on failure-domain structure. Use Birnbaum
importance — the partial derivative of system reliability with respect
to component reliability — to identify which defense-layer improvement
buys the most nominal reliability. Prevention (reducing the population
that reaches recovery) changes the demands on downstream layers more
effectively than improving recovery alone.

> Source: Molnar, Reliability Theory for AI Control (arXiv:2609.26419)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`browser-agent-http-sandbox`](../skills/browser-agent-http-sandbox/SKILL.md) — HTTP interception architecture
- [`speculative-sandbox-scheduler`](../skills/speculative-sandbox-scheduler/SKILL.md) — Prefork scheduling algorithm
- [`transactional-coding-sandbox`](../skills/transactional-coding-sandbox/SKILL.md) — Snapshot/rollback implementation
- [`unified-capability-gateway`](../skills/unified-capability-gateway/SKILL.md) — 5-stage kernel interface
- [`layered-defense-ensemble`](../skills/layered-defense-ensemble/SKILL.md) — Defense stacking with correlation
- [`covert-tool-injection-defense`](../skills/covert-tool-injection-defense/SKILL.md) — Tool output sanitization
- [`self-improving-red-team`](../skills/self-improving-red-team/SKILL.md) — Evolving adversarial testing
- [`deterministic-span-editing`](../skills/deterministic-span-editing/SKILL.md) — Minimal-diff configuration editing
- [`harness-tampering-audit`](../skills/harness-tampering-audit/SKILL.md) — Two-axis self-improvement tampering audit
- [`dependency-scoped-plan-validation`](../skills/dependency-scoped-plan-validation/SKILL.md) — Dependency-scoped plan and action lineage verification
- [`black-box-trajectory-risk-monitoring`](../skills/black-box-trajectory-risk-monitoring/SKILL.md) — Prefix-level trajectory risk and failure monitoring
- [`necessary-tool-evidence-path`](../skills/necessary-tool-evidence-path/SKILL.md) — Necessary tool-evidence path verification
- [`nlip-agent-message-envelope`](../skills/nlip-agent-message-envelope/SKILL.md) — Semantic message envelope and gateway authorization
- [`taxonomy-driven-red-teaming`](../skills/taxonomy-driven-red-teaming/SKILL.md) — Taxonomy-driven systematic red teaming
- [`description-only-injection-detection`](../skills/description-only-injection-detection/SKILL.md) — Pre-deployment tool injection risk assessment
- [`high-fanout-sandbox-memory-compression`](../skills/high-fanout-sandbox-memory-compression/SKILL.md) — Memory compression for parallel sandboxes
- [`runtime-resource-authorization-bounds`](../skills/runtime-resource-authorization-bounds/SKILL.md) — Dynamic resource acquisition quarantine and effect permits
- [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md) — Pre-execution parameter evidence audit against indirect injection
- [`universal-tool-defense`](../skills/universal-tool-defense/SKILL.md) — Anomaly-based tool filtering, canonical schema recalling, and reflection

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
- HookPry: arXiv:2609.03884
- Door-in-the-Face Refusal Behaviour: arXiv:2609.02707
- PlanFence: arXiv:2609.03340
- Self-Issued Authentication (CFA): arXiv:2609.03247
- PatchBench: arXiv:2609.04075
- AlcaTRAz: arXiv:2609.03693
- Dalek: A Constructive Agent Machine: arXiv:2609.03546
- Value-Preserving MAS Architectures: arXiv:2609.03920
- FLY-EVAL++: arXiv:2609.04021
- Style Over Substance: arXiv:2609.08236
- Single-Direction Attack on 320B MoE: arXiv:2609.09793
- Secure AI-SOC Neurosymbolic Framework: arXiv:2609.10707
- Overflip: arXiv:2609.15013
- AcquireBound: arXiv:2609.14744
- ActGuard: arXiv:2609.14987
- Agent-Tool Boundary Anomalies: arXiv:2609.15397
- Universal Defenses for Tool-Integrated LLM Agents: arXiv:2609.16098
- BLINDSPOT Long-Horizon Benchmark: arXiv:2609.16305
- PentestChain: arXiv:2609.18120
- Red-Teaming Auto Mode: arXiv:2609.19587
- Inference-Engine Fingerprinting Attacks are Practical: arXiv:2609.20614
- HE-Guardrail: arXiv:2609.21484
- Vehicle Voice Command Authorization: arXiv:2609.19630
- Closed-World Tool Hallucination: arXiv:2609.19425
- A2M MCP Hijacking: arXiv:2609.26761
- Reliability Theory for AI Control: arXiv:2609.26419
- Hard Stop: arXiv:2609.29808
- Refusing Everything Looks Safe: arXiv:2609.26176
- The Price of Safety (memory defenses): arXiv:2609.22818
- Ajar: arXiv:2609.26900
- Decoding Guardrails: arXiv:2609.24801
- Monitor Jailbreaking: arXiv:2609.31121
- Instrumental Monitor Evasion: arXiv:2609.30217
- ActGov: arXiv:2609.24446
- Zero-Trust Authorization for Enterprise MCP: arXiv:2609.22573
- Progressive Skill Discovery as Access Control: arXiv:2609.28693
