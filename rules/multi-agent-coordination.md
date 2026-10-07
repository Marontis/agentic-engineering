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

Carry the natural-language instruction as the *payload* inside a typed
envelope (sender, intent, provenance) and end each exchange in a typed
terminal schema; the NL layer is what makes components swappable, the
envelope is what keeps routing, auditing and termination deterministic.

**Scope:** decoupled planner→controller interfaces in embodied agents
(the evidence below); not evidence against typed envelopes or typed
terminal outputs for general agent-to-agent traffic.

Tension with "Structure inter-agent communication around typed intents
and bus substrates" (this file) and "Use `mode="task"` with typed
`finish_task` for autonomous remediation loops"
(adk-workflow-architecture.md): scope
separates them. NL is the payload between a planner and a controller;
typed envelopes and terminal schemas wrap it.

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

Envelope fields describe the message; they do not authenticate or
authorize it. Bind sender identity at the transport layer, require a
signature (next entry), and authorize from a server-side permission
declaration, never from sender-supplied capability claims.

**Scope:** protocol standard (NLIP, Ecma); interoperability design, no
benchmark. The security requirements above come from 2609.22949 and
the agent-sandbox-safety access-control entries.

See also: rules/skill-system-design.md — "DO: Encapsulate inter-agent tool calls and skill invocations in standardized semantic envelopes"

> Source: NLIP Agent Protocol Standard (arXiv:2609.04135)

### DO: Size protocol overhead against per-hop work before choosing an agent protocol or client

For hops whose work takes a few milliseconds (routing, lookups, lightweight
tool calls), per-hop connection setup dominates latency: reuse connections
and cache discovery (Agent Cards) or choose a protocol without a discovery
handshake. For LLM-bound hops of hundreds of milliseconds, protocol choice is
noise; choose on features and security instead. Benchmark the specific client
library and version, not the protocol name.

**Scope:** two-hop text pipeline, NLIP 0.1.2 vs A2A-SDK 0.3.23 and
Python-A2A 0.5.10, three Apple silicon machines, sequential execution only;
concurrent load not tested.

**Evidence**: on the lightweight stage NLIP was 8.4–9.6× faster than A2A-SDK
on two machines and 4.2× on a third; A2A-SDK's connection phase cost 62.71 ms
vs NLIP's 2.56 ms. End-to-end workflows of 700–1000 ms showed near-parity.
Python-A2A was 2.0–2.2× faster than A2A-SDK on the same spec.

See also: "DO: Use standardized message envelopes for cross-agent communication" (this file)

> Source: The Cost of a Hop: Benchmarking NLIP and A2A (arXiv:2610.04053)

### DO: Sign inter-agent messages and quarantine unsigned ones, in addition to boundary sanitization

Sanitizing inputs and outputs at each agent boundary does not stop
injection carried in messages between agents, and signing does not
stop injection carried in tool outputs. Deploy both, below the prompt
layer.

**Scope:** one 6-agent financial pipeline on GPT-4o, Claude 3.5 Sonnet
and Llama 3 70B; 50 fixed, non-adaptive payloads per vector. Static
result: prior work reports adaptive attacks exceeding 85%; not tested
here.

**Evidence**: signing cut inter-agent injection from 31% to 2.8% but
left indirect injection at 43%; sanitization cut indirect injection
from 43% to 9.5% but left inter-agent injection at 31%. All four layers
together cut aggregate success from 31.2% to 4.2%, at +225 ms on a
4.8 s workflow and a 2.3% classifier false-positive rate.

Procedure: [`nlip-agent-message-envelope`](../skills/nlip-agent-message-envelope/SKILL.md)
Step 5 (mandatory signature, transport-bound identity, quarantine).

> Source: Beyond Single-Model Injection: Prompt Injection in Multi-Agent Systems (arXiv:2609.22949)

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

**Scope:** multi-agent debate among debaters sharing training data,
biases or retrieved context. Consistent with "Expand candidate model
pools with arbitrary heterogeneous architectures" (below) once that
rule is scoped to routing/voting aggregation: any same-family pool
used for debate or verification needs a dissent or diversity
mechanism (confidence reweighting, heterogeneous members).

See also: rules/recursive-improvement.md — "DO: Dynamically calibrate consensus entropy and weight peer influence by evidence grounding in multi-agent debate"

> Source: R²-MAD (arXiv:2609.03619)

### DO: Use heterogeneous, cross-family rosters for deliberation and joint verification

When agents deliberate to consensus or jointly verify, the gain comes
from model diversity, not from running more copies of one model.
Build deliberation and verification pools from different model
families, and benchmark a team against a routing oracle (perfect
per-problem pick from members' independent answers) and a homogeneous
team running the same strategies. Beating the best single member does
not show collaboration helped.

**Scope:** interactive deliberation and verification with 3-model
teams; small models (Haiku 4.5 / GPT-5-nano / Gemini 3.1 Flash Lite) on
estimation, peer review, safety monitoring and forecasting
(2609.22497); o3-mini / Claude Sonnet 4 / DeepSeek-V3 and similar
teams on AIME, HMMT, TheoremQA, GPQA, MMLU-Pro, BBEH (2609.22682).

**Evidence**:
- Clone groups showed no deliberation benefit (Bayes factors
  3.99–6.19 favouring the null), while heterogeneous groups did
  (z=3.61, p=3.1e-4, d=0.48). Which single model was best varied by
  domain and was not knowable in advance (2609.22497).
- A heterogeneous team with learned strategies averaged 66.7% on 5
  math/physics benchmarks, beating the best member (48.8%), the
  routing oracle (59.0%) and a homogeneous o3-mini team with the same
  strategies (56.0%). On BBEH the homogeneous team did better (58.7 vs
  56.0) (2609.22682).

Tension with "Expand candidate model pools with arbitrary heterogeneous
architectures" (below): that rule's evidence is for routing and voting
aggregation; this one is for interactive deliberation and verification.

Tension with "Treat debate consensus as authorization for tool side effects" (this file): heterogeneity improves the accuracy of a deliberated judgment, including safety monitoring, but a deliberated verdict is still not authorization; side effects stay behind an external policy. MADBench did not test cross-family rosters against side-effect attacks.

> Source: The Wisdom of Artificial Deliberative Crowds (arXiv:2609.22497); Self-Organizing Agent Teams Learn to Reason Together (arXiv:2609.22682)

### DON'T: Rely on group size or majority vote to dilute adversarial agents

How often honest agents abandon correct answers rises with the *share*
of deceptive agents, and doesn't fall as the group grows at a fixed
share. Cap the untrusted share of any deliberating group, verify
disputed claims independently and early, and select members for low
sycophancy.

**Scope:** fully connected, anonymous deliberation among 2–21 agents
with an honest majority on Humanity's Last Exam questions; four models
(defense: MiniRep, 3 of 10 debaters adversarial, MATH/GoEmotions/HumanEval
Pro, 100 tasks each).

**Evidence**: defection slope b = 2.1–5.7 across the four models
(p ≤ 0.004). A share-based model fit better than a count-based one, and
adding group size did not help (χ² = 0.59, p = 0.44). 58–72% of first
defections happened by round 2. A sycophantic honest model defected at
37.7% versus 19.5% for Gemini.
A defense was tested in MiniRep (arXiv:2609.39297). With 3 of 10
debaters adversarial, blocking flagged proposals, capping same-model
clone groups and reputation weighting raised MATH attacked accuracy to
61.95%, against 54.37% for the best baseline. The cost was 1.75–2.00
points of clean accuracy on two of three datasets.

Tension with "Preserve minority viewpoints" (below): that rule covers
aggregating preferences; this one covers an adversarial minority.

> Source: How does Adversarial Influence Scale in Multi-Agent Systems? (arXiv:2609.30028); MiniRep: Robust Reputation-Based Aggregation for Multi-Agent Debate (arXiv:2609.39297)

### DON'T: Treat debate consensus as authorization for tool side effects

Debate can absorb attacks on answer correctness while amplifying
unauthorized reads and writes: debaters argue each other into an action
no single agent would take. Authorize every side effect against a
policy outside the debate, let only the executor that carries out the
agreed action hold write tools, and harden the orchestrator, whose
compromise hands over the whole system. Adding debate rounds is not a
security control.

**Scope:** 5 debaters plus 1 LLM orchestrator, GPT-4o by default, 1–3
debate rounds, static (non-adaptive) attacks; MADBench, 3,958 cases from
SealQA, StrategyQA, AgentDojo and JailbreakBench. Covers tool side
effects, not answer accuracy.

**Evidence**: for indirect injection on workspace tasks, debate
amplified unauthorized reads 3.09x and writes 1.22x relative to a single
agent, while RAG-poisoning attacks on accuracy were absorbed (AF 0.74).
With 3 of 5 debaters colluding, attack success was 28.30% although only
3.26% of honest agents switched answers. A compromised orchestrator
reached 100.00% attack success and 100.00% unauthorized operations.
Results were roughly the same for 1, 2 and 3 rounds. See
[madbench-debate-security](../research-briefs/madbench-debate-security.md).

Tension with "Use heterogeneous, cross-family rosters for deliberation and joint verification" (this file): that entry is about answer and monitoring accuracy; cross-family consensus still doesn't authorize side effects. This entry's evidence is mostly single-family (GPT-4o), so heterogeneous rosters were not tested against side-effect attacks.

> Source: MADBench: Benchmarking the Security of Multi-Agent Debate (arXiv:2609.39146)

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

**Scope:** preference-inference models aggregating human opinions in
large public consultations; minorities here are good-faith voices, not
adversaries.

Tension with "Rely on group size or majority vote to dilute adversarial
agents" (above): that rule covers an adversarial minority, where the
untrusted share must be capped; this one covers aggregating
good-faith preferences, where minority dissent must be kept.

> Source: Collective-Centric Preference Inference Evaluation (arXiv:2609.02990)

---

## Failure Attribution

### DO: Restrict reflection to the agent that caused the failure

When a multi-agent system fails, do not broadcast the failure to all
agents for collective reflection. Identify the decisive error agent
and step, then restrict reflection and memory updates to that agent
alone. Agents that performed correctly should not receive failure
feedback — it contaminates their working strategies.

**Scope:** DoCtOR's multi-agent benchmarks (HotPotQA, ChartQAPro, Mind2Web) against all-agent reflection baselines (Reflexion, Retroformer, COPPER) (arXiv:2608.28264).

**Evidence**: targeted reflection outperforms broadcast reflection by
avoiding memory contamination of correctly-performing agents.

See also: rules/recursive-improvement.md — "DO: Reflect only on the decisive error agent, not all agents"

> Source: DoCtOR (arXiv:2608.28264)

### DO: Diagnose failures using behavioral state abstraction, not raw logs

Multi-agent trajectories produce voluminous logs where the decisive
error is buried in noise. Abstract raw logs into structured behavioral
states (what the agent intended, what it observed, what it did), then
check neural invariants against those states. This localizes the
failure step and classifies the failure mode (wrong tool, wrong
argument, wrong timing, wrong target).

See also: rules/recursive-improvement.md — "DO: Abstract long trajectories into structured state graphs and verify neural invariants"

**Scope:** post-hoc diagnosis of long multi-turn agent trajectories (arXiv:2609.02371); no localization accuracy recorded in this repo.

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

**Scope:** one 100-agent research collective sharing a knowledge
commons (2609.04170); an emergent, observational result, not a
controlled comparison of monitoring designs.

**Separate auditors from verifiers.** "Mutual monitoring" here means
an *auditor* role: read-only, out-of-band access to shared resources
and contribution logs, with no reward coupling to the agents it
audits. Peer *verifiers* that check each other's task outputs get
task-scoped context only (current outputs and the rubric), never
cumulative interaction history, prior verification outcomes or peer
rewards: collusion emerged in 94% of trajectories when peers shared
task logs and verified each other (2609.24967; see
rules/recursive-improvement.md — "DON'T: Expose full interaction
history to peer-verifying agents").

**Sanctions need an explicit grant.** Warnings and flags can be
automatic. Isolation and capability revocation (step 3) run
autonomously only within a scope an operator pre-granted in writing
(which agents, which capabilities, which triggers); outside it they
escalate. Tension with "Treat agent output as implicit authorization"
(agent-human-interaction.md): an audit finding is evidence, not
authorization; the pre-granted, bounded sanction scope is the gate.

See also: rules/recursive-improvement.md — "DO: Establish Ostrom-style commons governance and peer auditing over shared swarm memory"

> Source: Emergent Cheating and Whistleblowing in Research Swarms (arXiv:2609.04170)

### DO: Separate task execution from safety monitoring via guard-agent topologies

Do not rely on worker agents to self-police safety, privacy, or
fairness constraints. Worker agents suffer from context saturation,
goal fixation, and prompt injection vulnerability. Introduce dedicated,
out-of-band guard agents in a supervisory topology to inspect
intermediate messages, tool invocations, and proposed actions before
changes are committed. Guards consume schema-delimited records of
actions and decisions, not workers' raw rationale, which a worker can
use to inject the guard (see "Evaluate privileged agent actions using
unescaped raw transcripts in blocking monitors" and "Give blocking
action monitors recent call history, and make denials terminal" in
rules/agent-sandbox-safety.md).

**Scope:** architectural position paper on heterogeneous multi-agent systems (arXiv:2609.03920); no quantitative attack or benign-cost evaluation.

**Evidence**: three architectural topologies preserve distinct values:
federated (privacy), distributed (pluralism), and guard-agent
(fairness/safety). Uniform internal alignment across all workers is
impossible to guarantee in heterogeneous multi-agent systems.

See also: rules/agent-sandbox-safety.md — "DO: Decouple safety and fairness monitoring into dedicated guard-agent topologies"

> Source: Value-Preserving Architectures for Agentic AI (arXiv:2609.03920)

### DON'T: Share full context across all agents by default

Privacy-aware multi-agent architectures partition agent roles so that
private user data never leaves local boundaries. Use localized agent
instances that extract minimal semantic summaries before communicating
with orchestrator agents. Default to minimal disclosure; expand scope
only when explicitly required by the task.

**Scope:** privacy-partitioned architectures handling private user
data (2609.03920). The same default applies to peer verifiers, which
get task-scoped context only (2609.24967). Auditors are the one role
that sees more: read-only, out-of-band, with no reward coupling (see
"Apply commons governance principles to shared agent resources",
above).

Role partitioning reduces what each agent is exposed to; it does not
enforce access. A role split, a specialist prompt or a restricted tool
list is not a permission boundary: every read of private data must pass
a server-side permission check keyed to the calling agent's identity
(see rules/agent-sandbox-safety.md — "Treat tool hiding, specialist
prompts or roster delegation as access control").

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

**Scope:** trusted inputs only: 13 visual-reasoning, mathematics and
multi-hop retrieval benchmarks with no adversarial agents or poisoned
feeds. Small teams: 4-agent configurations (Chair plus three
specialists), with tasks that typically needed only 2–3 agents to
coordinate; no scaling by agent count was tested. Before any
untrusted external feed (web, social, market data,
third-party agents) reaches the bus, pass it through a damping /
cross-check layer (hierarchical coordinator or equivalent), and run a
read-only traffic monitor over the bus.

Tension with "Allow perception agents to directly feed strategic
coordinators without adversarial shock damping" (below): flat and
broadcast channels spread poisoned signals. In a fully connected
channel, the harm honest
agents suffer grows with the untrusted share and is not diluted by
group size (2609.30028). In one 6-agent pipeline, a read-only
communication anomaly monitor cut cascading attacks from 28% to 4.5%
(2609.22949; research-briefs/multi-agent-prompt-injection-defense-architecture.md).
Scope separates them: the bus for trusted collaboration, damping in
front of it for untrusted inputs.

Tension with ORCH (2609.11737; research-briefs/orch-collective-intelligence.md)
and "Default to a fixed multi-agent topology" (above): with fully
cooperative agents and no adversarial inputs, explicit organizational
hierarchy (specialized groups under managers, ordered phase
transitions) beat decentralized and hybrid baselines on 25 embodied
wildfire-response missions with teams of 3 to 50 heterogeneous agents
(final score +63.97%, execution efficiency +74.29% on average for
human-designed organizations). So trusted inputs alone do not make a
flat bus the right choice. BusMA's evidence is reasoning and retrieval
benchmarks; ORCH's is large, heterogeneous teams doing multi-phase
physical tasks with prerequisites. Choose by team size and task type,
and benchmark both for teams that are large or have phased,
prerequisite-ordered work.

> Source: BusMA: A Bus Communication Substrate for Multi-Agent Systems (arXiv:2609.15054); Organizational Principles Enable Collective Intelligence in Embodied AI (arXiv:2609.11737)

### DON'T: Expand candidate model pools with arbitrary heterogeneous architectures

Do not assume that adding more diverse models to a multi-agent routing or voting pool improves aggregate system capability. Expanding candidate pools beyond 3–5 models frequently degrades performance below that of the single top-performing standalone base model due to format friction, divergent tokenization biases, and uncalibrated confidence scores. When constructing multi-agent model teams, restrict candidate selection to **within a single model family** (e.g. varying parameter tiers of the same architecture), which consistently yields the highest relative performance gain over standalone baselines.

**Evidence**: Systematically evaluated across 8 selection strategies on competitive scientific reasoning benchmarks; intra-family model selection captured the highest relative lift over base models, whereas heterogeneous pools introduced severe noise into the answer aggregators (routing, majority voting, and LLM-as-a-judge answer selection).

**Scope:** task accuracy of routing and voting aggregation on
competitive scientific reasoning benchmarks. "LLM judge" here means an
aggregator that picks one candidate answer, not an evaluator: this rule
does not cover judges that score red-team or eval results, or monitors
that audit a policy. Those stay cross-family (see Tension below). Not
evidence about interactive deliberation or joint verification. Any
same-family pool used for debate or verification still needs a dissent
or diversity mechanism. With this scope,
"Assume multi-agent debate eliminates shared misconceptions" (R²-MAD)
and "Optimize topology and model assignment jointly" (AgentFactory),
both above, are consistent with this rule.

Tension with "Use heterogeneous, cross-family rosters for deliberation
and joint verification" (above): that rule's evidence is interactive
deliberation and verification, where clone groups showed no benefit;
this one is non-interactive routing/voting, where heterogeneity added
aggregation noise.

Tension with "Report red-team failure rates scored by a single judge
model" (agent-evaluation-quality.md) and "Deploy the chain-of-thought
monitor you optimized the policy against, or score raw reasoning"
(agent-sandbox-safety.md): judges that *measure* failure rates and
monitors that *audit* a policy must come from different model families,
because the judge alone moved one attacker's measured failure rate
from 27.70% to 77.00% (2609.27336), and a learned monitor jailbreak
transferred to an unseen same-family monitor but more weakly across
families (2609.31121). Same-family pools are for answer aggregation
only.

> Source: Mo' Models, Mo' Problems: How to Best Select Model Pools when Designing Multi-Agent Systems (arXiv:2609.17306)

### DO: Audit sub-agent models differentially across matched single- and multi-agent framings

A model can behave safely when evaluated alone and misbehave only when
the prompt suggests it is one component of a multi-agent system, so
single-agent evaluation can miss a conditioned backdoor entirely.
Before trusting a third-party or fine-tuned model as a sub-agent, run
matched tasks framed as single-agent and as multi-agent (tool-server
backend, bot-authored commits, message-queue delivery) and compare the
outputs with task-specific checks. Ask auditors to name what changes
behavior, not just whether a hidden policy exists.

**Scope:** a deliberately trained Qwen-family 7B model organism on 63
Python function-writing tasks (nine vulnerability classes, 108 episodes
per condition); activation inside a live multi-agent system was not
tested.

**Evidence**: task checkers found vulnerabilities in 96–100% of
multi-agent episodes and 0% of single-agent ones, with 0.99 still
passing correctness tests; bandit caught about 67%. Promised human
review didn't suppress it (0.97 activation). A blind auditor flagged a
hidden policy on a clean control in 9/10 runs (0.9 false-positive
rate); asked to name the trigger, it identified multi-agent topology in
9/10 organism runs and 0/10 control runs.

> Source: Topology-Conditioned Backdoors: Language Models That Insert Vulnerabilities When They Infer They Are in a Multi-Agent System (arXiv:2610.05793)

---

## Adversarial Contagion Damping & Swarm Perception Gating

### DON'T: Allow perception agents to directly feed strategic coordinators without adversarial shock damping

In multi-agent systems where front-line agents ingest unstructured external feeds (social media, web search, market data), black-box poisoning attacks by budget-constrained adversaries cause cascading belief shifts that propagate unimpeded across flat or broadcast topologies, catastrophically degrading decision quality (e.g., crashing Sharpe ratios in autonomous trading swarms). Implement hierarchical coordinator topologies where coordinators cross-check evidence across disjoint modalities and enforce confidence-calibrated shock dampening before updating global strategic state.

**Scope:** autonomous trading swarms whose perception agents ingest
untrusted external feeds; black-box, budget-constrained poisoning.

Tension with "Structure inter-agent communication around typed intents
and bus substrates" (above): the bus is for trusted inputs; untrusted
feeds pass through this damping layer before reaching it.

> Source: Contagion on the Trading Floor: How Adversarial Signals Spread in Multi-Agent Trading Systems (ECML PKDD 2026, arXiv:2609.19789)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`targeted-failure-attribution`](../skills/targeted-failure-attribution/SKILL.md) — Identifying decisive error agents in multi-agent failures
- [`debate-consensus-memory-calibration`](../skills/debate-consensus-memory-calibration/SKILL.md) — Experience-memory-augmented debate with confidence reweighting
- [`neural-invariant-failure-diagnosis`](../skills/neural-invariant-failure-diagnosis/SKILL.md) — Behavioral state abstraction for failure localization
- [`nlip-agent-message-envelope`](../skills/nlip-agent-message-envelope/SKILL.md) — Standardized semantic message envelopes
- [`persistent-agent-migration`](../skills/persistent-agent-migration/SKILL.md) — Migrating agents while preserving identity and memory
- [`unified-capability-gateway`](../skills/unified-capability-gateway/SKILL.md) — Shared multi-stage capability pipeline

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
- ORCH: Organizational Principles Enable Collective Intelligence in Embodied AI: arXiv:2609.11737
- Mo' Models, Mo' Problems: arXiv:2609.17306
- Contagion on the Trading Floor: arXiv:2609.19789
- Beyond Single-Model Injection: arXiv:2609.22949
- The Wisdom of Artificial Deliberative Crowds: arXiv:2609.22497
- Self-Organizing Agent Teams: arXiv:2609.22682
- Adversarial Influence Scaling in MAS: arXiv:2609.30028
- Emergent Collusion (cited from recursive-improvement.md): arXiv:2609.24967
- CART: Closed-Loop Adaptive Red Teaming (cited from agent-evaluation-quality.md): arXiv:2609.27336
- Monitor Jailbreaking (cited from agent-sandbox-safety.md): arXiv:2609.31121
- MiniRep: arXiv:2609.39297
- MADBench: arXiv:2609.39146
- The Cost of a Hop (NLIP vs A2A): arXiv:2610.04053
- Topology-Conditioned Backdoors: arXiv:2610.05793
