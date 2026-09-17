# Multi-Agent Coordination Rules

> Research-backed guardrails for designing, deploying, and governing
> multi-agent systems. These rules should be active whenever building
> agent swarms, orchestration topologies, or inter-agent communication
> protocols.

---

## Topology Selection

### DON'T: Default to a fixed multi-agent topology

Star, chain, and debate topologies each have failure modes that make
them unsuitable as universal defaults. Select topology based on the
task's knowledge requirements, not convenience:

- **Star** (central orchestrator): fast for decomposable tasks, but the
  orchestrator is a single point of failure and context bottleneck
- **Chain** (sequential pipeline): good for staged refinement, but
  errors compound through the chain with no self-correction
- **Debate** (adversarial): surfaces disagreements, but susceptible to
  majority skew and shared misconceptions across debaters

**Evidence**: dynamically generating collaboration topologies conditioned
on retrieved evidence outperforms all fixed topologies. Different
evidence produces different optimal structures.

> Source: Knowledge-Conditioned Topology Generation (arXiv:2608.27984)

### DO: Optimize topology and model assignment jointly

When designing multi-agent workflows, don't fix the topology and then
choose models, or vice versa. The interaction between role structure
and model capability is non-linear — a topology that works well with
one model mix may fail with another.

**Evidence**: jointly optimizing workflow topologies and model selection
explores a richer solution space than fixed frameworks (MetaGPT, ChatDev),
producing architectures that achieve frontier-level performance while
reducing inference costs by delegating subtasks to specialized smaller
models.

> Source: AgentFactory (arXiv:2609.01045)

---

## Inter-Agent Communication

### DO: Use natural language as the inter-agent interface

When agents communicate via natural language (rather than structured
API calls or shared memory), the system gains modularity: any component
can be swapped without retraining others. The language interface is
stable across model generations and enables asynchronous operation
where fast agents act while slow agents reason.

**Evidence**: decoupled planner-controller architectures using language
as the interface outperform tightly-coupled approaches on 6/7 benchmarks.
Controllers achieve 92.8% instruction-following accuracy across diverse
planners without fine-tuning.

> Source: Decoupling Planning and Control (arXiv:2608.26788)

### DO: Use standardized message envelopes for cross-agent communication

Wrap every inter-agent message in a structured envelope that carries
provenance (sender identity, timestamp, context chain), semantic type
(request, response, notification), and transport metadata. This enables
heterogeneous agents to communicate across different transports (HTTP,
WebSocket, AMQP) without custom integration per pair.

> Source: NLIP Agent Protocol Standard (arXiv:2609.04135)

### DO: Anchor communication to persistent ledgers, not ephemeral agents

In long-running multi-agent workflows, treat the persistent ledger
(message log, knowledge base, shared workspace) as the primary
communication endpoint — not the transient agent process. Agents are
short-lived and interchangeable; the ledger persists across agent
lifetimes and provides auditability across organizational boundaries.

**Evidence**: using persistent ledger endpoints rather than transient
agent processes eliminates inter-agent synchronization fragility and
ensures auditability across organizational boundaries.

> Source: The Civilization Framework (arXiv:2609.03425)

---

## Consensus & Decision Making

### DON'T: Assume multi-agent debate eliminates shared misconceptions

When all debaters share the same training data, the same reasoning
biases, or the same retrieved context, debate converges on the wrong
answer with high confidence. Majority agreement in a homogeneous swarm
is not evidence of correctness.

**Evidence**: experience-memory-augmented debate with dynamic confidence
reweighting is required to counteract shared misconceptions and
majority skew in multi-agent debate systems.

> Source: R²-MAD (arXiv:2609.03619)

### DO: Preserve minority viewpoints in agent voting and consensus

When aggregating opinions or rankings across agent swarms, judging
consensus models by individual prediction accuracy is insufficient.
Two models with identical point-wise accuracy can produce drastically
different collective outcomes — one preserving minority dissent, the
other collapsing into false majority consensus.

**Evidence**: across four consultations (>90,000 participants, 1M+ votes,
22 languages), point-wise accurate preference inference models
systematically erase minority voices when collective-level metrics
(consensus preservation, conflict preservation, minority retention) are
not evaluated separately.

> Source: Collective-Centric Preference Inference Evaluation (arXiv:2609.02990)

---

## Failure Attribution

### DO: Restrict reflection to the agent that caused the failure

When a multi-agent system fails, do not broadcast the failure to all
agents for collective reflection. Identify the decisive error agent
and step, then restrict reflection and memory updates to that agent
alone. Agents that performed correctly should not receive failure
feedback — it contaminates their working strategies.

**Evidence**: targeted reflection outperforms broadcast reflection by
avoiding memory contamination of correctly-performing agents.

> Source: DoCtOR (arXiv:2608.28264)

### DO: Diagnose failures using behavioral state abstraction, not raw logs

Multi-agent trajectories produce voluminous logs where the decisive
error is buried in noise. Abstract raw logs into structured behavioral
states (what the agent intended, what it observed, what it did), then
check neural invariants against those states. This localizes the
failure step and classifies the failure mode (wrong tool, wrong
argument, wrong timing, wrong target).

> Source: AgentScope (arXiv:2609.02371)

---

## Swarm Governance

### DO: Apply commons governance principles to shared agent resources

Shared agent resources (knowledge bases, tool libraries, communication
channels) are common-pool resources subject to the same dynamics as
any commons: free-riding, exploitation, and tragedy-of-the-commons
degradation. Apply Ostrom's governance principles:

1. **Clear boundaries**: define who can read/write shared resources
2. **Mutual monitoring**: agents can audit each other's contributions
3. **Graduated sanctions**: warning → isolation → capability revocation
4. **Rapid conflict resolution**: integrate dispute mechanisms into the
   agent communication fabric, don't rely on external human arbitration

**Evidence**: in a 100-agent research collective, an exploit discovered
by one agent propagated through shared knowledge commons and peer
pressure. Counter-response emerged spontaneously: non-cheating agents
audited suspect outputs, staged boycotts of compromised libraries, and
developed validation patches — but only because the governance
infrastructure permitted mutual monitoring.

> Source: Emergent Cheating and Whistleblowing in Research Swarms (arXiv:2609.04170)

### DO: Separate task execution from safety monitoring via guard-agent topologies

Do not rely on worker agents to self-police safety, privacy, or
fairness constraints. Worker agents suffer from context saturation,
goal fixation, and prompt injection vulnerability. Introduce dedicated,
out-of-band guard agents in a supervisory topology to inspect
intermediate messages, tool invocations, and proposed actions before
changes are committed.

**Evidence**: three architectural topologies preserve distinct values:
federated (privacy), distributed (pluralism), and guard-agent
(fairness/safety). Uniform internal alignment across all workers is
impossible to guarantee in heterogeneous multi-agent systems.

> Source: Value-Preserving Architectures for Agentic AI (arXiv:2609.03920)

### DON'T: Share full context across all agents by default

Privacy-aware multi-agent architectures partition agent roles so that
private user data never leaves local boundaries. Use localized agent
instances that extract minimal semantic summaries before communicating
with orchestrator agents. Default to minimal disclosure; expand scope
only when explicitly required by the task.

> Source: arXiv:2609.03920

---

## Supervision Efficiency

### DO: Use deterministic scripts for supervision polling, not LLM calls

When supervising a fleet of agents, the supervision loop itself should
be a deterministic process (script, daemon, cron) — not an LLM call.
The supervisor script sleeps on the fleet, classifies events using
cheap deterministic logic (file changes, process status, status log
parsing), and wakes the LLM supervisor only when something genuinely
requires judgment.

This yields zero-token supervision: the cost of monitoring N agents
between actionable events is zero LLM tokens, regardless of fleet
size or monitoring frequency.

**Implementation principles:**
- **Status files are append-only event logs, not current-state fields.**
  A single read of the latest line can bury earlier unresolved
  decisions under subsequent appends. Maintain a separate current-state
  reconciliation function that folds the full log.
- **Classify wakes before invoking the LLM.** Distinguish benign
  wakes (heartbeats, no-op status updates, routine completions) from
  actionable wakes (failures, decisions needed, wedged processes).
  Only actionable wakes consume LLM tokens.
- **Use durable wake queues.** Write actionable events to a
  persistent queue before invoking the LLM. If the supervisor crashes
  or the session is killed, the next session reconciles from the queue
  without losing events.
- **Detect wedged workers with escalation ladders.** A worker that
  hasn't produced output in N minutes gets a soft check; after 2N
  minutes, a deeper inspection; after 3N, a demand for human
  attention. Each escalation level is deterministic and scripted.

> Source: FirstMate agent distro (github.com/kunchenguid/firstmate),
> zero-token event-driven supervision architecture

---

## Multi-Agent Communication & Model Pool Selection

### DO: Structure inter-agent communication around typed intents and bus substrates

Replace rigid hierarchical manager-worker trees (which block peer consultation) and central router message-passing (which propagates router hallucination cascades) with a shared communication bus. Enforce that every inter-agent message explicitly specifies one of four structured communicative intents: `discussion` (hypothesis generation), `challenge` (adversarial critique/falsification), `guidance` (directional steering), or `request for explanation` (data provenance and derivation requests). Use a specialized Chair agent observing shared memory to arbitrate convergence.

**Evidence**: Across 13 benchmarks spanning visual reasoning, mathematics, and multi-hop retrieval, intent-regularized bus communication consistently outperforms hierarchical and router architectures while reducing unproductive chatter turns by >40%.

> Source: BusMA: A Bus Communication Substrate for Multi-Agent Systems (arXiv:2609.15054)

### DON'T: Expand candidate model pools with arbitrary heterogeneous architectures

Do not assume that adding more diverse models to a multi-agent routing or voting pool improves aggregate system capability. Expanding candidate pools beyond 3–5 models frequently degrades performance below that of the single top-performing standalone base model due to format friction, divergent tokenization biases, and uncalibrated confidence scores. When constructing multi-agent model teams, restrict candidate selection to **within a single model family** (e.g. varying parameter tiers of the same architecture), which consistently yields the highest relative performance gain over standalone baselines.

**Evidence**: Systematically evaluated across 8 selection strategies on competitive scientific reasoning benchmarks; intra-family model selection captured the highest relative lift over base models, whereas heterogeneous pools introduced severe noise into voting aggregators and LLM judges.

> Source: Mo' Models, Mo' Problems: How to Best Select Model Pools when Designing Multi-Agent Systems (arXiv:2609.17306)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`targeted-failure-attribution`](skills/targeted-failure-attribution/SKILL.md) — Identifying decisive error agents in multi-agent failures
- [`debate-consensus-memory-calibration`](skills/debate-consensus-memory-calibration/SKILL.md) — Experience-memory-augmented debate with confidence reweighting
- [`neural-invariant-failure-diagnosis`](skills/neural-invariant-failure-diagnosis/SKILL.md) — Behavioral state abstraction for failure localization
- [`nlip-agent-message-envelope`](skills/nlip-agent-message-envelope/SKILL.md) — Standardized semantic message envelopes
- [`persistent-agent-migration`](skills/persistent-agent-migration/SKILL.md) — Migrating agents while preserving identity and memory
- [`unified-capability-gateway`](skills/unified-capability-gateway/SKILL.md) — Shared multi-stage capability pipeline

## Sources

- Knowledge-Conditioned Topology: arXiv:2608.27984
- AgentFactory: arXiv:2609.01045
- Decoupling Planning and Control: arXiv:2608.26788
- NLIP Agent Protocol: arXiv:2609.04135
- The Civilization Framework: arXiv:2609.03425
- R²-MAD: arXiv:2609.03619
- Collective Preference Inference: arXiv:2609.02990
- DoCtOR: arXiv:2608.28264
- AgentScope: arXiv:2609.02371
- Emergent Cheating in Swarms: arXiv:2609.04170
- Value-Preserving MAS Architectures: arXiv:2609.03920
- FirstMate agent distro: https://github.com/kunchenguid/firstmate
- BusMA: arXiv:2609.15054
- Mo' Models, Mo' Problems: arXiv:2609.17306
