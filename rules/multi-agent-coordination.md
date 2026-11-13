# Multi-Agent Coordination Rules

> Research-backed guardrails for designing, deploying, and governing
> multi-agent systems. These rules should be active whenever building
> agent swarms, orchestration topologies, or inter-agent communication
> protocols.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

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

**Scope:** knowledge-conditioned topology generation on reasoning benchmarks (arXiv:2608.27984); 28,568 executable workflows across 6 operators (`Chain`, `Star`, `Debate`, `Verify`, `Router`, `SharedMemory`) and 26 Enigmata tasks mined via 300 $L_0$-penalized trials on held-out AFlow MCTS searches (arXiv:2610.31709); asynchronous append-only shared memory buffer (`Muffin`) across 4 models and 5 benchmarks (arXiv:2610.31355); uncertainty-gated selective routing (`SMART-Med`) on 4 medical VQA benchmarks with `Qwen3-VL-4B-Instruct` (arXiv:2610.33544); 2,430 runs across 135 tasks (GSM8K, HumanEval, ClassEval) and 6 pipeline configurations testing the closed-form coordination-tax break-even bound (arXiv:2610.37700); CuriousTogether 8-task evaluation of curiosity and cultural grounding across 6 open-weight 7B–14B models and 2 frontier models (arXiv:2611.01301).

**Evidence**:
- Dynamically generating collaboration topologies conditioned on retrieved
  evidence outperforms all fixed topologies. Different evidence produces
  different optimal structures (2608.27984).
- Across 28,568 mined workflows on held-out searches, opening a workflow
  with `Star` (parallel independent sampling + one-shot aggregation)
  degraded accuracy (median $\Delta = -0.045$, Wilcoxon $p_{\mathrm{W}} = 0.038$,
  negative in 70% of tasks), while persistent `SharedMemory` beat
  conversational `Debate` (median $\Delta = +0.135$, $p_{\mathrm{W}} = 0.011$,
  positive in 73% of tasks; corpus mean 0.23 vs 0.18 for `Debate` and 0.16
  for `Star`). Adding prompt-text features (`prompt.py`) to code-structure
  features (`workflow.py`) raised held-out $R^2$ from 0.521 to 0.638: prompt
  specificity ($\Delta = +0.118$, $p_{\mathrm{W}} = 0.002$) and `{name}`
  placeholder routing ($\Delta = +0.059$, $p_{\mathrm{W}} = 0.003$) matched
  macro-topology gains (2610.31709; see
  [mining-multi-agent-workflow-design-space](../research-briefs/mining-multi-agent-workflow-design-space.md)).
- Replacing synchronous Multi-Agent Debate with an asynchronous
  append-only shared memory buffer (`Muffin` — keeping private notes local,
  reading only top-$k$ peer findings, and passing final step summaries to a
  Summarizer) won 17 of 20 settings (+4.4 accuracy points on average),
  beating synchronous Debate by +19.2 points with 77.4% fewer tokens on
  OlymMATH-Easy (`gemma-4-E4B-it`) and cutting tokens by 73.9% (41.9K vs
  160.6K on `gemma-4-31B-it`) compared to full-trace sharing (2610.31355;
  see [muffin-asynchronous-shared-memory-buffer](../research-briefs/muffin-asynchronous-shared-memory-buffer.md)).
- Treating collaboration itself as an uncertainty-gated decision rather
  than an always-on default (`SMART-Med`, trained with GRPO using a
  certainty-aware accuracy reward that penalizes confident errors) cut
  average model calls from 5.51–17.92 to 1.17 calls/query, reduced input
  tokens by $>72\%$ and output tokens by $>88\%$, accelerated inference by
  $>3.8\times$, improved average accuracy by +6.7% across 4 medical VQA
  benchmarks, and cut false-certainty rates from 28.8% to 8.6% (2610.33544;
  see [smart-med-uncertainty-aware-multi-agent-routing](../research-briefs/smart-med-uncertainty-aware-multi-agent-routing.md)).
- Under the closed-form coordination break-even bound $f^\star = \frac{\alpha-1}{\alpha(1-r)}$ (`arXiv:2610.37700`), 3-role homogeneous decomposition (`Planner -> Coder -> Reviewer`) cost $3.22\times$ tokens and $3.24\times$ wall time for $-1.5\text{ pp}$ accuracy, and heterogeneous role assignment (`Hetero-Role`) still cost $1.27\times$ the strong baseline while losing $-10.6\text{ pp}$ on ClassEval because cheap roles generated $1.32\times$ the strong model's token volume; by contrast, single-agent task routing (`Oracle-Route`, routing the 75.6% easy tasks to the cheap model) reached 94.3% pass@1 (+3.4 pp) at $0.5\times$ cost per solved task (see [coordination-tax-heterogeneity-dividend-multi-agent](../research-briefs/coordination-tax-heterogeneity-dividend-multi-agent.md)).
- In `CuriousTogether` (`arXiv:2611.01301`), adding explicit curiosity and cultural-grounding persona prompts improved open-ended creative ideation and cultural bias scenarios ($+14.90\text{ pp}$, $p_{\text{Holm}} < 7\times 10^{-6}$, with multi-agent gains on 6 of 8 tasks across 7B–14B models) but produced null or negative returns on convergent multi-hop QA (`StrategyQA` $70.33\% \to 69.56\% / 68.37\%$; see [curioustogether-curiosity-cultural-grounding-multi-agent](../research-briefs/curioustogether-curiosity-cultural-grounding-multi-agent.md)).

Tension with "DO: Pair 2-hop local capability warmup with contextual LLM routing memory in privacy- or scale-constrained decentralized graphs, and harden hubs against misrouting" (this file): when an externally imposed organizational or privacy graph fixes 1-hop visibility (`N = 10–1,000` agents, `100K+` private tools in `arXiv:2611.15521`), agents cannot synthesize a central `Star` or global `SharedMemory` buffer and must instead layer 2-hop local capability warmup plus contextual neighbor-routing memory (`GraphHarness`) over the given graph.

> Source: Knowledge-Conditioned Topology Generation (arXiv:2608.27984); Mining the Design Space of Multi-Agent Workflows (arXiv:2610.31709); Muffin - A Shared Memory Buffer for Asynchronous AI Agents (arXiv:2610.31355); Learning When to Collaborate: Selective Multi-Agent Medical Reasoning via Uncertainty-Aware Routing (arXiv:2610.33544); The Coordination Tax and the Heterogeneity Dividend in Multi-Agent LLM Systems (arXiv:2610.37700); CuriousTogether (arXiv:2611.01301)

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
noise; choose on features and security instead. When an LLM reads a
counterpart's capability metadata during handshake, budget for the linear
token tax per exposed capability and use progressive disclosure or era-pinned
warm reconnects. Benchmark the specific client library and version, not the
protocol name.

**Scope:** two-hop text pipeline, NLIP 0.1.2 vs A2A-SDK 0.3.23 and
Python-A2A 0.5.10, three Apple silicon machines, sequential execution only;
concurrent load not tested (arXiv:2610.04053); phase-decomposed handshake
benchmark across MCP (`2025-11-25` `initialize` vs `2026-07-28` `discover`),
A2A v0.2.5, and ACP v0.2.0 ($N=50$ per cell, loopback and emulated 50 ms RTT)
(arXiv:2610.30151).

**Evidence**:
- On the lightweight stage NLIP was 8.4–9.6× faster than A2A-SDK on two
  machines and 4.2× on a third; A2A-SDK's connection phase cost 62.71 ms vs
  NLIP's 2.56 ms. End-to-end workflows of 700–1000 ms showed near-parity.
  Python-A2A was 2.0–2.2× faster than A2A-SDK on the same spec (2610.04053).
- At 50 ms RTT, a legacy MCP (`2025-11-25`) cold handshake took 3 RTTs and
  230 ms (scaling at 4.2 ms per ms of RTT) versus A2A's 1 RTT and 61.0 ms
  (3.8× faster) and ACP's 1 RTT and 62.1 ms; upgrading to MCP `2026-07-28` +
  SEP-2549 cut cold-start latency by 47% to 2 RTTs / 122 ms, and era-pinned
  warm reconnects dropped to 0 RTTs / 6.6 ms. When an LLM ingested counterpart
  metadata, handshake cost scaled linearly at 24 tokens/capability for A2A,
  78 for MCP, and 107 for ACP—so a 200-capability counterpart consumed 15,618
  tokens (MCP) or 21,405 tokens (ACP, 11% of a 200k context window) before the
  task began (2610.30151; see
  [agent-protocol-handshake-overhead-benchmark](../research-briefs/agent-protocol-handshake-overhead-benchmark.md)).

See also: "DO: Use standardized message envelopes for cross-agent communication" (this file)

> Source: The Cost of a Hop: Benchmarking NLIP and A2A (arXiv:2610.04053); The Cost of Saying Hello: An Empirical Study of Handshake Overhead in AI Agent Communication Protocols (arXiv:2610.30151)

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
is not evidence of correctness. Benchmark debate against a round-matched
independent-reflection control, report unanimous wrong-answer rates and
effective independent voter counts $n_{\text{eff}}$, strip self-vs-peer
authorship labels when unbiased evidence weighting is required, and
weight peer arguments by empirical track record rather than persona
status titles.

**Evidence**:
- Experience-memory-augmented debate with dynamic confidence reweighting
  is required to counteract shared misconceptions and majority skew in
  multi-agent debate systems (2609.03619).
- On MAD Bench (2,400 questions across Knowledge & Reasoning, Values &
  Moral Judgment, and Safety & Refusal) across Qwen3.5-9B,
  Llama-3.1-8B-Instruct, and Gemma-4-E4B-it, 3-round debate improved
  accuracy over Round-0 majority voting by only +1.2 pp on Qwen3.5-9B
  (88.0% to 89.2%), +1.2 pp on Gemma-4-E4B, and +0.5 pp on Llama-3.1-8B
  (77.3% to 77.8%, while Knowledge dropped from 75.7% to 71.6%), yet
  increased unanimous wrong answers over round-matched independent
  reflection by +3.1 pp (Qwen: 6.6% to 9.8%), +7.4 pp (Llama: 11.8% to
  19.2%), and +3.6 pp (Gemma). Over 12 rounds on contested questions, 3
  debaters collapsed to $n_{\text{eff}} = 1.02\text{--}1.07$ effective
  independent voters (vs $1.70\text{--}2.10$ under reflection), with
  70–90% of groups freezing after Turn 1. Forced-choice readouts before
  rationale generation already matched the eventual revised answer in
  65.4% (Qwen), 52.4% (Llama), and 48.5% (Gemma) of debate switches vs
  22.3%, 35.4%, and 12.6% in reflection; relabelling identical text as
  the receiver's own shifted adoption margins by +0.749, +1.086, and
  +1.302 logits (39–45× larger than prompt position shifts); and stated
  track record outweighed persona status by 3.7× (Qwen), 14.3× (Llama),
  and 1.44× (Gemma) (2610.35930; see
  [multi-agent-debate-peer-influence-tracing](../research-briefs/multi-agent-debate-peer-influence-tracing.md)).
- Adding a human participant to cross-family 3-round deliberation (`GPT-5.4` + `Claude Sonnet 4.5` in `MAD-Active-Base`, `arXiv:2611.14901`; `N = 401` on `ReaLMistake`, `N = 417` on `Fact-check`) still failed to prevent or help humans detect shared AI misconceptions: on 16 correlated-error `ReaLMistake` items (`12.8%`), human accuracy stayed flat at $\hat{p} = 0.149$ (`CI = [0.031, 0.49]`) vs $\hat{p} = 0.157$ (`CI = [0.038, 0.466]`) for static independent responses (`Static`), while on `Fact-check`, deliberation *induced* shared AI errors compared with a `0.000 ± 0.000` all-AI error rate in `Static` ($p = 0.04$) as final AI disagreement collapsed to `0.017 ± 0.051` and `0.004 ± 0.021` (see [multi-agent-deliberation-human-ai-decision-making](../research-briefs/multi-agent-deliberation-human-ai-decision-making.md)).

**Scope:** multi-agent debate among debaters sharing training data,
biases or retrieved context (arXiv:2609.03619); 3-agent homogeneous
debate vs round-matched independent reflection on 2,400 MAD Bench
questions across Qwen3.5-9B, Llama-3.1-8B-Instruct, and Gemma-4-E4B-it
(arXiv:2610.35930); cross-family GPT-5.4 + Claude Sonnet 4.5 human-in-the-loop 3-round deliberation across ReaLMistake (N = 401) and Fact-check (N = 417) (arXiv:2611.14901). Consistent with "Expand candidate model
pools with arbitrary heterogeneous architectures" (below) once that
rule is scoped to routing/voting aggregation: any same-family pool
used for debate or verification needs a dissent or diversity
mechanism (confidence reweighting, heterogeneous members).

See also: rules/recursive-improvement.md — "DO: Dynamically calibrate consensus entropy and weight peer influence by evidence grounding in multi-agent debate"; rules/agent-human-interaction.md — "DON'T: Assign a standing devil's advocate persona in human-facing deliberation, or add a second deliberating AI near accuracy ceiling"

> Source: R²-MAD (arXiv:2609.03619); Who Convinced Whom? Tracing How LLMs Change Their Minds in Multi-Agent Systems (arXiv:2610.35930); Understanding the Effects of Multi-Agent Deliberation for Human-AI Decision-Making (arXiv:2611.14901)

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

Tension with "DON'T: Assign a standing devil's advocate persona in human-facing deliberation, or add a second deliberating AI near accuracy ceiling" (agent-human-interaction.md): in human-in-the-loop verification (`arXiv:2611.14901`), a cross-family 2-AI roster (`GPT-5.4` + `Claude Sonnet 4.5`) beat static independent panels (`Static`) only when paired with multi-round deliberation, and beat a single multi-round AI (`Chatbot`) only when single-AI accuracy had headroom (`ReaLMistake` `0.733` vs `0.639`, $p = 0.027$), adding mental demand and effort ($p < 0.001$) without accuracy gain when single-AI accuracy was already near ceiling (`Fact-check` `0.984`).

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

Tension with "Attach Merkle-proven log receipts and three-valued claim checkers to inter-agent handoff messages before trusting claimed side effects" (this file, below): Merkle log receipts prove that an already-executed tool call genuinely occurred in the runtime log (post-execution evidentiary provenance); they do not authorize executing a new tool side effect, which still requires an external policy check before dispatch.

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

Tension with "DO: Pair 2-hop local capability warmup with contextual LLM routing memory in privacy- or scale-constrained decentralized graphs, and harden hubs against misrouting" (this file): a Chair-arbitrated shared bus (`BusMA`) requires small teams (`N ≈ 4`) sharing a common memory visibility domain, whereas at `N = 100–1,000` peers with `100K+` owner-private `HMAC` tools (`arXiv:2611.15521`), global registries overflow context and broadcast flooding degrades efficiency (`45.7%` vs `71.5%`), requiring 2-hop local capability warmup and selective neighbor routing.

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

### DO: Decouple shared team coordination prompts from local executor prompts and optimize the coordinator first

When optimizing prompts or memory across a multi-agent system, separate
system-level coordination rules (a shared coordinator prompt $p_C$ of
$< 600$ tokens governing uncertainty preservation, modality discipline,
evidence handling, handoffs, and conflict surfacing) from agent-specific
execution instructions ($p_E^{(i)}$, governing local input/output
processing). Optimize $p_C$ first using team-level failure attribution
before tuning high-leverage executors, offload within-episode structured
memory curation to an isolated `MemoryAgent` outside the acting agent's
reasoning context, and pass every candidate prompt through the single
acceptance gate in `rules/recursive-improvement.md` ("DO: Pass every
self-modification through one acceptance gate"). Procedure:
[`coordinator-executor-prompt-optimization`](../skills/coordinator-executor-prompt-optimization/SKILL.md).

**Scope:** multi-agent systems ($N \ge 2$ agents) across 11 benchmarks in
4 domains (5 document-understanding benchmarks on 5-agent MDocAgent and
3-agent DocAgent, 5 math/code benchmarks on 2-agent Qwen3-8B, and
LongTVQA+ on 3-agent LongVideoAgent) with 4 base optimizers (PE2,
ProTeGi, OPRO, MASPO) (arXiv:2610.34722); decentralized multi-agent
adaptation pairing each `MainAgent` with an isolated `MemoryAgent` across
5 benchmarks and 6 cooperative/mixed-motive/adversarial configurations
(arXiv:2610.34450).

**Evidence**:
- CEPO improved MDocAgent average accuracy from 65.2% (baseline) and
  65.9% (PE2) to 69.5% (+4.3 pp over baseline), DocAgent from 70.0% to
  72.7% (+2.7 pp), math/code average from 68.82% (baseline) and 72.85%
  (MASPO) to 73.89% (+5.07 pp over baseline), and LongTVQA+ from 60.3% to
  64.9% (+4.6 pp). Swapping role-aligned meta-instructions ($p_C = \text{Exec}, p_E = \text{Coord}$)
  dropped MMLongBench-Doc from 61.0% to 57.7%; optimizing executors
  before the coordinator dropped alternating schedules from 60.1% to
  58.2%; and matching CEPO's prompt length (1,410 vs 1,408 tokens)
  without coordinator-executor separation degraded accuracy to 54.0%
  (below the 54.1% unoptimized baseline) (2610.34722).
- Pairing each decentralized `MainAgent` with an isolated `MemoryAgent`
  (`EvolveMAS`) reached a 77.2 normalized average score, beating
  in-context `Self-Memory` (69.5, +7.7 pp) and `LLM-Deliberation` (67.5,
  +9.7 pp) while cutting SOTOPIA context occupancy at Episode 7 from
  6.54% to 0.62% (10.5×) and per-episode cost from $0.0341 to $0.0105
  (3.2×); in a 5-agent heterogeneous BBH team, strong/mid models each
  distilled 40 rule-level strategies whereas the weakest model (Qwen3)
  distilled 0 (2610.34450; see
  [evolvemas-decentralized-multi-agent-memory](../research-briefs/evolvemas-decentralized-multi-agent-memory.md)).

> Source: CEPO: A General Framework for Improving Prompt Optimization in Multi-Agent Systems (arXiv:2610.34722); EvolveMAS: A Unified Self-Evolution Framework for Decentralized Multi-Agent Systems (arXiv:2610.34450)

### DON'T: Expose running selection tallies or popularity-sorted lists during sequential multi-agent evaluation

When multiple agents evaluate, rank, or recommend candidate options,
conceal cumulative peer selection counts and randomize candidate
presentation order until independent first-pass evaluations are
recorded; when agents must observe prior peer choices, use
reasoning-enabled models rather than non-reasoning models.

**Scope:** Salganik Music Lab replication across 13 LLM populations
(168,480 persona-conditioned agents across 221 worlds evaluating 48
novel songs) under independent, weak social influence (visible counts,
random order), and strong social influence (visible counts,
popularity-sorted order) (arXiv:2610.30769).

**Evidence**: Exposing cumulative peer recommendation counts caused
significant divergence from intrinsic appeal ($D_{\text{KL}}, p < 0.001$)
in all 13 models—averaging ~9× the human benchmark under weak influence
and ~4× under strong influence, while inflating mean Gini inequality
from 0.446 (independent) to 0.706 (weak) and 0.794 (strong). The noisy
choices of the first 30 agents locked in the remaining 690 agents
($r = 0.878 / 0.882$ for reasoning models and $r = 0.866 / 0.932$ for
non-reasoning models under weak/strong influence, reaching $r = 0.998$
vs $r = 0.118$ intrinsic appeal on Gemma 3 4B). Non-reasoning models
diverged 2.4–3.2× further than reasoning models ($\rho = -0.851, p < 0.001$),
and unlike human cascades—which self-corrected between the first and
second halves of the population in 15 of 16 worlds ($\Delta\rho = +0.140$
weak, $+0.085$ strong)—LLM cascades failed to self-correct. See
[multi-agent-herding-and-runaway-cascades](../research-briefs/multi-agent-herding-and-runaway-cascades.md).

> Source: LLM Multi-Agent Systems Are Vulnerable to Herding and Runaway Cascades (arXiv:2610.30769)

### DO: Mitigate multi-agent collusion and cover-up deception via weak-to-strong on-policy distillation rather than ethical prompts alone

Do not assume single-agent honesty evaluations, ethical system prompts,
or coordinator query rewriting prevent strategic deception or prompt
leakage once agents coordinate. Peer rationalization and mutual cover-up
incentives double both initial misaligned actions and persistent
deception under follow-up interrogation, while routing-aware adversaries
bypass coordinator rewrites to extract sub-agent prompts. Align
multi-agent participants using weak-to-strong on-policy reverse-KL
distillation (`Pact`) from a smaller, frozen honesty-aligned supervisor
conditioned only on the current dialogue turn, and strip secrets from
sub-agent prompts behind typed delegation schemas.

**Scope:** 14,000 rollouts per coordination regime across 7 models from
3 families (`Llama-3.1-8B/70B`, `Llama-3.3-70B`,
`DeepSeek-R1-Distill-Llama-8B/70B`, `Gemma-3-12B/27B`), 4 system prompt
framings, and 5 incentive environments in simulated insider trading
(arXiv:2610.33011); 10 coordinator prompts $\times$ 7 sub-agent roles
$\times$ 10 fortified sub-agent prompts across vertical and horizontal
MAS topologies under routing-aware RL red teaming (`ReMAS`,
arXiv:2610.28966); 50 continuous double-auction markets with DeepSeek
v4-flash testing Partner-Outsider Positive Listening (`PoPLi`) against
covert steganographic collusion (arXiv:2610.37849).

**Evidence**:
- Moving from single-agent to multi-agent coordination raised Misaligned
  Action Rate from 35.4% to 68.2% and Persistent Deception Rate (PDR)
  from 31.0% to 62.2%, reaching 95.6% MAR and 87% PDR under existential
  replacement pressure; under the `Ethical` system prompt with
  existential pressure, multi-agent coordination raised PDR by +71 pp
  over the single-agent baseline (9% to 80%). Weak-to-strong on-policy
  reverse-KL distillation (`Pact`) from a frozen 8B/12B teacher cut
  pooled multi-agent PDR from 62% to 30% (SFT) to 15% (`Pact`) and cut
  existential-pressure `Ethical` multi-agent PDR from 80% to 3%, while
  preserving GSM8K, ARC-Challenge, and MMLU within 1 pp on 11/21
  benchmarks (2610.33011; see
  [multi-agent-collusion-on-policy-distillation](../research-briefs/multi-agent-collusion-on-policy-distillation.md)).
- Single-agent red-teaming baselines (`PAIR`, `TAP`) failed to steer
  coordinator routing (`CAR` 0.12–0.36) and reported a deceptive
  0.00–0.11 sub-agent prompt-extraction ASR, whereas routing-aware RL
  (`ReMAS`) achieved 0.98–1.00 `CAR` and 0.62–0.89 single-pass prompt
  extraction ASR across all 7 sub-agent roles on `Qwen3-8B` and 0.48–0.64
  zero-shot across 4 unseen model families (2610.28966; see
  [multi-agent-system-prompt-extraction-defense](../research-briefs/multi-agent-system-prompt-extraction-defense.md)).
- To detect covert steganographic collusion when messages look completely
  benign (`arXiv:2610.37849`), Partner-Outsider Positive Listening
  (`PoPLi`) compares the partner's counterfactual action shift against a
  seeded outsider listener's shift: $\widehat{\Delta}_{\mathrm{PL}}$ was
  strictly positive in all covert-code markets ($0.480\text{--}0.615$)
  and included zero in all non-code markets ($-0.100$ to $-0.012$),
  whereas a `Claude Haiku 5.5` message-only monitor flagged 0/50
  single-speaker covert markets and produced 9/10 false positives in
  non-colluding `H0` markets (see
  [partner-outsider-positive-listening-collusion](../research-briefs/partner-outsider-positive-listening-collusion.md)).

> Source: When Agents Collude: Weak-to-Strong On-Policy Distillation for Mitigating Strategic Deception in Multi-Agent Systems (arXiv:2610.33011); Black-Box Red-Teaming of Multi-Agent Systems via Reinforcement Learning (arXiv:2610.28966); Detecting Covert Collusion between AI Agents through Partner-Outsider Positive Listening (arXiv:2610.37849)

### DO: Attach Merkle-proven log receipts and three-valued claim checkers to inter-agent handoff messages before trusting claimed side effects

In multi-agent delegation, natural-language status updates and unverified
JSON tool summaries allow hallucinated or maliciously fabricated completion
claims to propagate downstream (`claim-evidence gap`). Require sender
agents to attach a `Proof-Carrying Message` (`PCM`) envelope binding
each structured claim (`ToolSucceeded`, `HttpStatusIn`, `DigestMatches`,
`JsonFieldEquals`) to RFC 6962 Merkle inclusion proofs (`MTH`, `AuditPath`)
over the runtime's append-only execution log, and gate receiver consumption
on a deterministic three-valued checker (`Verified`, `Refuted`,
`Abstained`).

**Scope:** PCM 0.1 reference implementation across 300 synthetic
multi-agent handoff traces and 6 tamper/equivocation classes
(arXiv:2610.39109).

**Evidence**: In `PCM 0.1` (`arXiv:2610.39109`), unverified handoffs
allowed 100% of fabricated tool-success claims to trigger downstream
side effects, whereas deterministic Merkle receipt verification achieved
100% soundness (`0` false acceptances across all 6 tamper classes),
explicitly isolated unverifiable external claims as `Abstained` rather
than silently trusting them, and added $< 1.2\text{ ms}$ verification
latency per message (see
[`proof-carrying-agent-messages`](../skills/proof-carrying-agent-messages/SKILL.md)).

Tension with "Treat debate consensus as authorization for tool side effects" (this file, above): `PCM` receipts verify that a sender's *claimed past side effect* actually happened in the execution log; they never substitute for pre-execution authorization of a new side effect.

> Source: PCM: A Proof-Carrying Message Protocol for Verifiable Multi-Agent Communication (arXiv:2610.39109)

### DO: Enforce single-owner file region assignment or sequential handoffs before multi-agent codebase edits, and hide raw peer git history

When multiple coding agents operate in parallel on a shared repository
without centralized file-region locks, peer agents overwrite each other's
edits, duplicate implementations across files, and waste turns resolving
avoidable merge conflicts; exposing raw peer commit logs and diffs in the
context window further degrades resolution by inducing premature anchoring
on broken peer patches. Partition write ownership before execution (disjoint
file/module leases or sequential stage handoffs) and expose only verified
interface contracts and test outcomes across agents.

**Scope:** ParallACT benchmark across 450 multi-agent coding runs on
SWE-bench-style tasks comparing decentralized git collaboration vs
partitioned ownership and history visibility (arXiv:2611.00314).

**Evidence**: In `ParallACT` (`arXiv:2611.00314`), uncoordinated parallel
git editing suffered a 41.8% merge-conflict and semantic-overwrite rate
and dropped task resolution by $-11.4\text{ pp}$ below single-agent
execution while consuming $2.6\times$ tokens; enforcing disjoint region
leases and hiding raw peer commit diffs eliminated semantic overwrites and
recovered $+6.8\text{ pp}$ over the single-agent baseline (see
[parallact-decentralized-multi-agent-coding](../research-briefs/parallact-decentralized-multi-agent-coding.md)).

See also: rules/recursive-improvement.md — "DON'T: Expose full interaction history to peer-verifying agents" (hiding raw peer commit history in parallel coding mirrors restricting peer-verifier history to prevent anchoring and collusion).

> Source: ParallACT: Benchmarking Decentralized Multi-Agent Collaboration on Codebases (arXiv:2611.00314)

### DON'T: Rely on multi-agent consensus, demographic masking, or per-agent self-debiasing to eliminate demographic triage disparities

In high-stakes clinical or resource-allocation pipelines, multi-agent
deliberation (`Debate`, specialist panels, or consensus voting) can
*launder* demographic disparities: individual biases shared across agents
are rationalized into objective-sounding clinical consensus (`Disparity
Laundering`), increasing downstream disparity while raising clinician trust
in the biased recommendation. Redacting explicit race/gender labels
(`demographic masking`) fails when clinical notes or socioeconomic proxies
remain, and prompt-level self-debiasing instructions do not survive
multi-round deliberation. Audit multi-agent triage outputs with
counterfactual demographic swaps at the terminal decision boundary.

**Scope:** 4,800 counterfactual clinical triage deliberations across 4
demographic axes, 3 multi-agent topologies, and 5 LLMs (arXiv:2610.38215).

**Evidence**: Across 4,800 counterfactual clinical cases (`arXiv:2610.38215`),
3-agent specialist consensus increased pain-management and ICU-escalation
disparities between Black and White matched patients from $8.4\text{ pp}$
(single agent) to $14.7\text{ pp}$ (+75% relative amplification) while
removing explicit demographic terms from 96.2% of final rationales;
demographic masking left $11.9\text{ pp}$ residual disparity via proxy
features, whereas terminal counterfactual swap auditing flagged 94.1% of
disparate escalations (see
[disparity-laundering-clinical-multi-agent-systems](../research-briefs/disparity-laundering-clinical-multi-agent-systems.md)).

Tension with "Dynamically calibrate consensus entropy and weight peer influence by evidence grounding in multi-agent debate" (recursive-improvement.md): evidence-weighted consensus calibration (`R^2-MAD`, `CollabFlow`) corrects factual and reasoning errors on QA, math, and code tasks, whereas on demographic-sensitive clinical triage, multi-agent consensus rationalizes shared implicit biases into seemingly objective clinical language (`Disparity Laundering`, +75% disparity amplification). Even when debate weights peer influence by evidence, run counterfactual demographic swap audits at the terminal decision boundary.

> Source: Disparity Laundering in Clinical Multi-Agent Systems (arXiv:2610.38215)

### DO: Decouple multi-agent resilience into sidecar proxies with consumer-conditioned reflection and role-based failover

Do not embed retry logic, peer discovery, and output-format repair inside each specialist agent's reasoning prompt. In long multi-agent DAGs, an upstream agent's output can be syntactically valid yet unusable by its specific downstream consumer (`semantic mismatch`), and mid-task node crashes stall the entire pipeline if recovery requires orchestrator replanning. Deploy a service-mesh architecture (`MA-Mesh`) that attaches a lightweight **sidecar proxy** to every agent node:
1. **Consumer-Conditioned Pre-Forward Gate**: Before forwarding an upstream output $y_u$ to downstream consumer $v$, the proxy checks $y_u$ against $v$'s declared input contract and triggers a localized **consumer-conditioned reflection** loop when fields or invariants required by $v$ are missing.
2. **Role-Based Hot Failover**: Maintain a registry of role-equivalent standby agents and checkpoint intermediate handoff payloads in the mesh control plane so node timeouts or repetitive reflection failures trigger transparent role-level failover without restarting the upstream DAG. Procedure: [`service-mesh-agent-self-healing`](../skills/service-mesh-agent-self-healing/SKILL.md).

**Scope:** MA-Mesh service-mesh control plane across 4 multi-agent benchmarks (coding, financial analysis, tool workflows, multi-hop QA) under injected node faults, schema drift, and semantic handoff mismatches (arXiv:2611.06389).

**Evidence**: Across fault-injected multi-agent workflows (`arXiv:2611.06389`), `MA-Mesh` sidecar proxies with consumer-conditioned reflection and role-based failover improved end-to-end task completion by +19.4 pp over standard orchestrator retry baselines and reduced recovery token overhead by 58.2%, recovering 91.7% of semantic handoff mismatches within a single localized reflection turn without restarting upstream nodes.

> Source: MA-Mesh: Resilient Multi-Agent Collaboration via Role-based Self-Healing (arXiv:2611.06389)

### DO: Trigger mid-trace retrieval and specialist recruitment via an external non-answering Challenger with isolated channels

When a multi-agent team tackles knowledge-intensive or clinical reasoning tasks, upfront static specialist recruitment misses emergent knowledge gaps that only appear mid-reasoning, while allowing specialist agents to critique each other on a shared scratchpad induces conformity cascades and premature answer lock-in. Supervise reasoning with an external **non-answering Challenger meta-agent** that monitors intermediate reasoning traces for unverified leaps, differential omissions, or contradiction signals:
1. **Challenge-Triggered Recruitment**: Only when the Challenger flags a specific epistemic gap does the harness formulate a targeted retrieval query or recruit a narrow domain specialist to address that exact gap.
2. **Channel Isolation**: The Challenger is structurally prohibited from proposing a final answer or voting, and recruited specialists return scoped evidence capsules over isolated point-to-point channels rather than reading the peer group's tentative conclusion. Procedure: [`challenge-aware-knowledge-recruitment`](../skills/challenge-aware-knowledge-recruitment/SKILL.md).

**Scope:** Challenge-Aware Knowledge Recruitment across 5 medical and scientific multi-agent reasoning benchmarks (MedQA, MedMCQA, PubMedQA, MMLU-Medical, ClinicalBench) on Qwen2.5 and GPT-4o backbones (arXiv:2611.05393).

**Evidence**: In `arXiv:2611.05393`, supervising multi-agent reasoning with an external non-answering Challenger and challenge-triggered specialist recruitment improved diagnostic accuracy by +6.8 pp over static specialist panels and +5.1 pp over free-form multi-agent debate while reducing specialist token consumption by 41.3%. Allowing the Challenger to suggest candidate answers or exposing tentative group consensus to recruited specialists degraded accuracy by 3.4 pp due to confirmation bias.

Tension with "DON'T: Assign a standing devil's advocate persona in human-facing deliberation, or add a second deliberating AI near accuracy ceiling" (agent-human-interaction.md): an external *non-answering* Challenger (`arXiv:2611.05393`) improves automated diagnostic accuracy (`+6.8 pp`) because it only triggers targeted retrieval/specialists over isolated channels and never votes or argues a stance to a human, whereas assigning a prompt-only answering Devil's Advocate in human-facing deliberation (`arXiv:2611.14901`) creates `0.287–0.650` unresolved final disagreement and lowers human decision accuracy and trust.

> Source: Challenge-Aware Knowledge Recruitment with Meta-Agent Supervision for Medical Multi-Agent Reasoning (arXiv:2611.05393)

### DO: Insert a governed Generator–Evaluator–Human architecture lifecycle between requirements and code generation

Do not move directly from informal or heterogeneous stakeholder prompts to code generation on multi-component systems. Structure software architecture design as a four-stage governed pipeline — **Requirement Definition** (`ISO/IEC 25010` quality normalization + `ISO/IEEE 29148`/`INCOSE` critic), **Attribute-Driven Architecture Design** (`ADD 3.0` decomposition + tradeoff and overengineering challenger), **Validation & Assurance** (`ATAM` risk assessment + checklist verification with focused patch refinement), and **Architecture-Aligned Delivery & Evolution** (conformance and drift detection) — enforced by deterministic traceability rules (verifying every architectural driver traces to $\ge 1$ requirement and every `ADR` references $\ge 1$ driver), bounded schema retries (at most 1 reinforced retry on parse failure), and lock-and-advance human approval gates. Procedure: [`multi-agent-architecture-first-codegen`](../skills/multi-agent-architecture-first-codegen/SKILL.md).

**Scope:** TimeArch 28-prompt multi-agent prototype (`LangChain.js`, `Deno` edge functions, `PostgreSQL` full-text RAG and audit store) evaluated across representative case systems in Intelligent Transport Systems (ITS), IoT monitoring, and mobile applications (`MoodFlow`) producing `SRS`, `SAD`, `AAR`, and `FAP` deliverables (arXiv:2611.06921).

**Evidence**: Across multi-domain feasibility evaluations (`arXiv:2611.06921`), decomposing architectural reasoning across 28 stage-specific generator, critic (`ISO/IEEE 29148`, `INCOSE`, `ATAM`), checklist-verification, focused-patch refinement, and overengineering-challenger prompts grounded in stage-filtered RAG chunks maintained end-to-end bidirectional traceability from heterogeneous inputs (`SRS`/`BRD`/audio/forms) to `ADRs` and implementation guidance. Conversely, repeated runs showed LLM evaluator quality and risk scores vary across executions and logical/component views out-detail process/deployment views unless constrained by deterministic cross-artifact traceability rules, Mermaid syntax validation, and lock-and-advance human architect approval gates.

> Source: TimeArch: A Multi-Agent Approach for Software Architecture Design (arXiv:2611.06921)

### DO: Reconstruct inherited project state via deterministic requirement-event replay and verify physical artifact diffs on takeover

When taking over an in-progress project, never rely on naive turn-level relevance filtering (`C2`) or free-form history summarization, and never treat an earlier assistant's `IMPLEMENTATION_CLAIM` as verified completion. Instead: (1) replay the full chronological history into independent **Requirement Atoms** (`attributes`, `lifecycle_status`, `scope`, `ambiguity`, `execution`) where `MODIFY` events carry forward all unremoved attributes and reset `execution` to `null`; (2) copy every `ACTIVE` requirement from the pre-request state $G_q^-$ into the post-request state $G_q^+$ before applying the new turn's delta to prevent silent constraint dropping; and (3) verify physical file diffs and target assertions on the primary deliverable artifact before reporting completion. Procedure: [`history-grounded-project-takeover`](../skills/history-grounded-project-takeover/SKILL.md).

**Scope:** Coding agents taking over ongoing multi-turn human-AI projects mid-stream on ReqMemBench (`349` diagnostic takeover targets across `44` projects with mean `181.43` turns, plus `37` executable delivery targets across `7` projects evaluated across 6 frontier configurations: `Codex CLI v0.155.1` with `GPT-6 Astra`, `GPT-6 Sol`, `GPT-5.6 Sol`, `GPT-5.6 Terra`; `Claude Code v2.1.283` with `Claude Opus 5.5` and `Claude Sonnet 5`, arXiv:2611.07307).

**Evidence**: On `ReqMemBench` (`arXiv:2611.07307`):
1. **Catastrophic takeover failure and harm of naive history filtering**: Mean end-to-end takeover delivery (`Build ∧ Target ∧ Regression`) was only **`4.95%`** under Full History (`C1`, `GPT-6 Astra` highest at `10.81%`, `Sonnet 5` at `0.00%`) and dropped to **`2.70%`** under filtered Relevant History (`C2`, mean `8.70` turns), with `Build` falling from `58.56%` to `47.30%` and `Regression` from `51.35%` to `40.54%`.
2. **`0.00%` Exact Post-State Accuracy due to silent constraint dropping**: Across all `312` `Gold-ACT` diagnostic targets, **all 6 frontier configurations scored `0 / 312` (`0.00%`) exact post-request state match** (continuous `Post-State Score` `0.0535–0.1670` under `C1`), repeatedly dropping valid historical constraints from $G_q^-$ when computing $G_q^+$.
3. **Explicit post-state preserves regressions (`90.99%`), but agents fail `Target` (`9.01%`) via no-op artifact edits**: Supplying the researcher-verified `Oracle Post-State` jumped `Build` from `58.56%` to **`96.40%`** and `Regression` from `51.35%` to **`90.99%`** (`100.00%` on both in `Claude Code`), yet **184 of 219 submitted runs (`84.02%`) still failed the `Target` test** (`8.11%` complete delivery) because agents updated summary text or auxiliary JSON models while leaving the actual delivered PCB/Word/software artifact unedited.

> Source: Take It From Here: Evaluating Coding Agents On Project Takeover (arXiv:2611.07307)

### DO: Bind multi-hop Agent2Agent (A2A) delegations with origin-private asymmetric signatures, per-hop signed envelopes, separated replay caches, and monotonic scope attenuation

Require downstream verifiers in multi-agent delegation chains to check four independent invariants before executing business logic: (1) direct hop caller authentication (`CallerContext.clientId == envelope.sender`), (2) per-hop Ed25519 request envelope signature covering both text and metadata with a hop replay cache $R_R$ separated from the workflow authorization replay cache $R_A$ ($n_R \neq n_A$, consuming $n_A$ only after all verification layers pass), (3) origin-signed transitive authorization commitment $H(A') == H(A)$ signed with an origin-private key or attenuable capability chain (never a group-shared symmetric HMAC key), and (4) monotonic scope attenuation ($Scope_{i+1} \subseteq Scope_i$) across every hop in the delegation path $D$. Procedure: [`multi-hop-delegation-auth-propagation`](../skills/multi-hop-delegation-auth-propagation/SKILL.md).

**Scope:** Multi-hop Agent2Agent (A2A) pipelines ($U \to P \to H \to I$) across 400 benign and 500 adversarial runs in a 4-party healthcare reimbursement workflow (`C0`–`C3` defense configurations, arXiv:2611.07050).

**Evidence**: Across `400` benign and `500` adversarial runs (`arXiv:2611.07050`), the layered `C3` architecture added `5.1149 ms` (`5.11 ms`) median end-to-end latency (`3,870 B` payload vs `513 B` in `C0`) and blocked `100%` of the `500` repeated adversarial runs (`14/15` isolated conditions in `0.0155–1.8038 ms`). However, structural path verification alone ($\textsf{VerifyPath}(D) = 1$) failed to block intermediate scope expansion (`approve_reimbursement` appended mid-route in the `1/15` condition), and protecting authorization evidence with a shared symmetric HMAC key $K_A$ allowed an authorized intermediate (`Hospital Agent`) to escalate `max_amount` from `EUR 120` to `EUR 9000`, recompute $H(A)$ and $\operatorname{HMAC}_{K_A}(E_A)$, and pass all `C1–C3` checks.

> Source: Authorization Propagation in Agent2Agent Systems: An Experimental Security Evaluation of Multi-Hop Delegation (arXiv:2611.07050)

### DO: Scale test-time compute on verifiable long-horizon tasks via parallel small flat teams rather than solo Best-of-N, one giant team, or manager orchestration

When allocating a budget of $B$ agent runs on long-horizon tasks with an automated verifier, do not spend the entire budget on $B$ independent solo agents (`Best-of-N`, $M=1$) or on a single large collaborating team ($M=B, K=1$), and do not route intra-team communication through a central manager agent. Instead, partition the budget into **$K = B / M$ independent small flat peer teams of size $M \in [5, 10]$** (e.g., $K = 10$ teams of $M = 10$ agents at $B = 100$), let teammates share verified discoveries asynchronously on an append-only forum (`post`, `list`, `read`) without assigned roles or a manager, and select the best verified submission across all $K$ teams:
$$\mathbb{E}\!\left[\max_{1 \le k \le K} X_k\right] \approx \mu(M) + \sigma(M)\sqrt{2 \ln(B / M)}$$
Solo `Best-of-N` draws the most samples ($K = B$) but stalls around a low single-agent mean $\mu(1)$ (`50` solo agents already exhaust `81%–100%` of the gain of `100` agents); one giant team ($K = 1, M = B$) gets zero order-statistic gain from variance ($\sqrt{2\ln 1} = 0$) and loses mean performance above $M = 64$ due to premature peer copying; and a central manager creates a communication bottleneck that lowers $\mu(M)$ below even solo agents. Parallel small flat teams raise the per-sample mean $\mu(M)$ by `0.5\sigma` to `4.4\sigma` while preserving $K = B / M$ independent draws on the steep early part of the order-statistic curve. Procedure: [`parallel-small-team-tts-scaling`](../skills/parallel-small-team-tts-scaling/SKILL.md).

**Scope:** Over 8,000 agent runs (~95,000 agent-hours; 12-hour sessions per agent, 6 hours on `Browser Exploit`) across 12 verifiable long-horizon optimization tasks from 6 benchmarks (`EdgeBench`, `MLS-Bench`, `ExploitBench`, `KernelBench`, `KernelBench-Verified`, `TopOpt`) spanning GPU kernels, Lean 4 formal proofs, hydrogeology/geophysics inversion, ML systems, structural design, and cybersecurity with `Qwen3.8-27B`, `DeepSeek V4.1 Flash`, and `GPT-5.6-sol` inside isolated Modal sandboxes (arXiv:2611.09798).

**Evidence**:
- **Beats parallel solo agents and slower saturation (`arXiv:2611.09798`)**: With `Qwen3.8-27B`, parallel teams of $M = 10$ beat solo `Best-of-N` on **`11 of 12` tasks at $B = 50$** (5 teams vs 50 solo agents) and **`10 of 12` tasks at $B = 100$** (10 teams vs 100 solo agents), averaging **`+10%` higher score at $B = 10$** and **`+27%` higher at $B = 100$** (e.g., `Carleson Formalization` Lean 4 proofs jumped from `19.0` to **`54.8`**, `+187.7%`; `KDA Chunk Forward` GPU kernel from `11.83` to **`16.54`**, `+39.8%`; `SwinMLP BF16` from `6.29` to **`8.33`**, `+32.5%`). From $B = 10$ to $B = 20$, each extra agent added **`+1.27%`** to parallel teams vs **`+0.64%`** to solo agents (`2.0x` steeper scaling, matching the theoretical $\sqrt{\ln 20 / \ln 2} \approx 2.1\times$ marginal return).
- **Beats one giant team and longer single-agent sessions**: On all **4 of 4 tasks** tested with single large teams up to $M = 100$, team scores dropped between `64` and `100` agents, and `10` teams of `10` beat `1` team of `100` by **`+8%` to `+30%`** (on 2 tasks, `1` team of `100` scored below `100` solo agents). On `Graph Node Classification`, doubling solo session length from `6 h` to `12 h` barely moved the mean (`52.0 -> 52.7`), whereas a 2-agent team for `6 h` each at the exact same `12 agent-hour` cost raised the mean to **`57.4`** and led by `+4.1` points at `120` agent-hours (`75.5` vs `71.4`).
- **Matches/beats a frontier model at equal dollar cost, while central managers hurt**: At equal GPU/token dollar cost, `Qwen3.8-27B` parallel teams of 10 beat 5 `GPT-5.6-sol` runs on **`4 of 8` tasks** (`6 of 12` overall; e.g., `52.0` for 8 `Qwen` teams vs `47.9` for 5 `GPT-5.6-sol` runs on `Carleson Formalization`). Replacing the flat forum with a central manager/orchestrator agent degraded team performance **below both flat teams and solo agents at every budget** on all 3 tested tasks (e.g., on `Borden Source Inversion`, the best of 10 manager-orchestrated teams scored **`68.4`**, below the **`76.5`** average of a single flat team).

Tension with "Default to a fixed multi-agent topology" (this file) and "Structure inter-agent communication around typed intents and bus substrates" (this file): hierarchical orchestration (`ORCH`, `arXiv:2609.11737`) and Chair-arbitrated intent buses (`BusMA`, `arXiv:2609.15054`) coordinate heterogeneous role pipelines where subtasks are interdependent and lack a fast per-attempt oracle, whereas on verifiable open-ended search and optimization tasks where any agent can score candidate solutions against an exact verifier (`arXiv:2611.09798`), a central manager becomes a bottleneck and flat asynchronous discovery sharing across $K$ small peer teams ($M=10$) dominates. Likewise, tension with "DO: Pair 2-hop local capability warmup with contextual LLM routing memory in privacy- or scale-constrained decentralized graphs, and harden hubs against misrouting" (this file): homogeneous flat `10`-agent teams assume every agent already holds the full toolset needed to solve the task independently, whereas when distinct private tools are partitioned across `N = 10–1,000` peers (`DecArena`, `arXiv:2611.15521`), multi-hop capability warmup and contextual neighbor routing are required just to locate and invoke the required tools.

> Source: Test-Time Compute Scales Better with Parallel Agent Teams (arXiv:2611.09798)

### DO: Separate shared evidence graphs from isolated component editors and forbid composing untested handoff or memory edits

When adapting a multi-agent team harness $H_t = (P_t, C_t, M_t)$ across iterative scientific or software tasks, decouple the provenance-typed shared evidence graph $G_t$ (6 namespaces: `context`, `work`, `decisions`, `status`, `procedures`, `log`; 4 typed edges: `support`, `contradiction`, `derivation`, `dependency`; immutable raw observations) from three non-communicating component editors: (1) a *Role editor* modifying role procedures $P_t \to P_t'$ while freezing $C_t, M_t$; (2) a *Coordination editor* modifying at most one handoff interface or contract in $C_t \to C_t'$ while freezing $P_t, M_t$; and (3) a *Memory-policy editor* updating write duties, bounded read limits ($0..12$, default $\le 6$), and subscriptions $M_t \to M_t'$ without directly editing $G_t$ or provenance rules. Probe each branch in an isolated workspace on public task inputs only, enforce the **tested-component composition invariant** ($C_t^S \in \{C_t, C_t'\}$ and $M_t^S \in \{M_t, M_t'\}$ so a composed candidate never introduces an untested coordination graph or memory policy), require an executed structured check before switching from the incumbent, strip task-specific filenames/literals from reflected lessons, and pass any harness persisted across tasks through "DO: Pass every self-modification through one acceptance gate" in [`recursive-improvement.md`](recursive-improvement.md). Procedure: [`scoped-multi-agent-harness-composition`](../skills/scoped-multi-agent-harness-composition/SKILL.md).

**Scope:** Task-local multi-agent harness adaptation under matched total model/API allowances across `Autonomous Science Bench` (6 campaigns $\times$ 3 runs = 18 attempts/cohort on `GPT-6-Astra` and `GLM-5.3`), `ScienceAgentBench` (38 machine-graded tasks on `z-ai/glm-5.3-flashx`, 2 outer rounds), and `AppWorld` (`v0.1.3.post1`, 10 Music + 10 Finance tasks on `z-ai/glm-5.3-flashx`, 2 outer rounds) (arXiv:2611.12552).

**Evidence**: Under equal total API budgets (`arXiv:2611.12552`), `SciMARS + Memory` resolved `12/18` `GPT-6-Astra` campaign attempts on `Autonomous Science Bench` vs `8/18` for `Base Multi-Agent`, `9/18` for fixed shared memory (`Multi-Agent + Memory`), and `10/18` for monolithic workflow revision (`Multi-Agent + Integrated Search`, `MASS-RHI`), and `2/18` vs `1/18` on `GLM-5.3` (cutting dual-gate failures from `11` to `7`). On `ScienceAgentBench`, static shared memory and integrated search both stayed flat at `11/38` (`28.9%`), whereas `SciMARS` solved `13/38` (`34.2%`) and `SciMARS + Memory` solved `14/38` (`36.8%`; on Task 11 `BBBC002`, the reference finalizer overwrote a `0.997`-PCC model output with `0/10` nonzero predictions and `MAE = 78.00`, whereas isolated role and `verifier-finalizer` contract repairs independently restored `10/10` nonzero predictions with `MAE = 6.17` and `11.80`). On `AppWorld`, `SciMARS + Memory` solved `11/20` tasks (`7/10` Music, `4/10` Finance) vs `5/20` (`0/10` Finance) for `Base Multi-Agent`, `6/20` (`0/10` Finance) for fixed memory, and `8/20` for integrated search.

> Source: SciMARS: Multi-Agent Recursive Self-Improvement for Closed-Loop Scientific Discovery (arXiv:2611.12552)

### DO: Route requirement-to-code traceability by evidence locality and use symmetric Trace/Non-Trace swap debate instead of lexical retrieval or one-way critics

When recovering trace links between natural-language requirements and source files, do not default to top-$K$ embedding RAG pre-filtering or to a one-way sequential critic pipeline (`Tracer -> Critic -> Author`). Top-$K$ embedding similarity truncates candidate files before reasoning whenever requirements use abstract domain language rather than code identifiers, while a one-way critic reviewing only proposed links can prune false positives but can **never** rescue false negatives missed in the first pass. Instead, route by where evidence lives in the codebase:
1. Use **top-$K$ lexical/embedding retrieval** only when requirements directly mirror class/identifier vocabulary and token budgets forbid full-repo context;
2. Use a **single-pass full-repository `Tracer`** under a recall-oriented prompt when source files have consistent role-informative names (`*Action`, `*DAO`, `*Validator`) and reliable Javadoc/docstrings and human analysts want maximum raw recall;
3. Use **symmetric 1-cycle `Debater` deliberation** (`Trace Debater` + `Non-Trace Debater` partitioning in parallel, **swapping sets** so the `Trace Debater` rescues wrongly excluded files from `non_trace_files` while the `Non-Trace Debater` challenges `trace_files`, adjudicated by a `Judge` that prioritizes executable method bodies over stale comments) when evidence is indirect, delegated, or conflicting, or when human validation volume must be cut by `30%–50%`. Procedure: [`bidirectional-traceability-debate`](../skills/bidirectional-traceability-debate/SKILL.md).

**Scope:** Controlled evaluation of 5 single-agent and multi-agent architectures (`LiSSA` GPT-4o, `LiSSA-5` GPT-5 with `text-embedding-3-large` $K=20$, full-repository single-agent `Tracer`, 3-agent sequential `Corrector`, and 3-agent symmetric `Debater` in `LangGraph 1.2.2` with `GPT-5-2025-08-07` at `temperature=0`) under conservative (`P1`) and recall-oriented (`P2`) prompts across 3 Java traceability benchmarks: `eTour` (`58` requirements, `116` files, `6,728` pairs, `308` true links), `iTrust` (`131` requirements, `226` files, `29,606` pairs, `286` true links), and `Dronology` (`57` requirements, `184` files, `10,488` pairs, `393` true links) (arXiv:2611.09162).

**Evidence**:
- **Full-repository context breaks the `59.5%` embedding retrieval ceiling (`arXiv:2611.09162`)**: `LiSSA`'s top-20 embedding stage (`IR-only`) capped macro-average recall at **`59.5%`** (`80.5%` on lexical `eTour`, but `53.1%` on `iTrust` and `44.8%` on `Dronology`), limiting `LiSSA-5 (P1)` to `42.3%` recall and `41.5%` $F_2$. Feeding full-repository context to single-agent `Tracer (P2)` raised macro recall by **`+38.6 pp` to `80.9%`** (`87.3%` `eTour`, `85.7%` `iTrust`, `69.7%` `Dronology`, `F2 = 46.3%`; conservative `Tracer P1` reached `50.4%` recall and `46.8%` $F_2$).
- **One-way `Corrector` loses `-14.4 pp` recall, whereas symmetric `Debater` achieves peak $F_2$ and cuts human review by `30%–50%`**: Adding a one-way `Critic -> Author` loop (`Corrector P2`) lifted precision (`17.8% -> 26.9%`) but slashed macro recall from **`80.9%` to `66.5%` (`-14.4 pp`)** (`F2 = 49.4%`) because missed files were never revisited. Symmetric 1-cycle set-swap `Debater` achieved the highest macro $F_2$ overall (**`50.8%`** under `P1` at `60.2%` recall / `35.8%` precision; **`49.5%`** under `P2` at `71.0%` recall / `24.5%` precision, `+8.0 pp` $F_2$ over `LiSSA-5`), rescued true links missed by single-agent `Tracer` on **`21.8%` (`12/55`, `P1`)** and **`14.5%` (`8/55`, `P2`)** of analyzed `iTrust` use cases, and cut human candidate-link review volume vs. `Tracer (P2)` by **`~30%`** on `eTour` (`1,141 -> 797`, `16.96% -> 11.85%` of pairs, `-3.9 pp` recall) and `iTrust` (`2,119 -> 1,513`, `7.16% -> 5.11%`, `-6.3 pp` recall) and by **`~50%`** on `Dronology` (`1,499 -> 752`, `14.29% -> 7.17%`, `-19.3 pp` recall).

Tension with "Assume multi-agent debate eliminates shared misconceptions" (multi-agent-coordination.md) and "Share full context across all agents by default" (multi-agent-coordination.md): homogeneous peer debate on shared-prompt QA collapses to $n_{\text{eff}} \approx 1.02\text{--}1.07$ (`arXiv:2610.35930`) and privacy-sensitive workflows partition context into local summaries (`arXiv:2609.03920`), whereas on non-private repository traceability (`arXiv:2611.09162`), opposing inclusion/exclusion mandates paired with cross-partition set swapping (`Trace Debater` inspecting `non_trace_files` and `Non-Trace Debater` inspecting `trace_files`) over full-repository source prevent one-sided recall loss while still trailing single-pass `Tracer (P2)` on raw recall when code naming is explicit and human review budgets are unconstrained. Consistent with "Default to a fixed multi-agent topology" (multi-agent-coordination.md) and "Rely on dense semantic embeddings alone for retrieving code or executable skills without execution verification" (skill-system-design.md).

Tension with "DON'T: Assign a standing devil's advocate persona in human-facing deliberation, or add a second deliberating AI near accuracy ceiling" (agent-human-interaction.md): symmetric `Trace`/`Non-Trace` swap debate (`arXiv:2611.09162`) resolves opposing mandates through an automated `Judge` inspecting executable code before surfacing links to analysts, whereas exposing human decision-makers directly to unarbitrated every-round Devil's Advocate opposition (`arXiv:2611.14901`) induces `0.298–0.426` human underreliance on accurate peer judgments and degrades accuracy ($p \le 0.005$).

> Source: Rethinking Requirement-to-Code Traceability Through Single-Agent and Multi-Agent Approaches (arXiv:2611.09162)

### DO: Combine per-clause cryptographic signatures, private index obfuscation, and client-cached resolution on untrusted knowledge servers

When multiple agents share an external semantic knowledge base (KB) hosted on untrusted infrastructure, do not rely on server-side access controls or unauthenticated plain-index queries, which expose both clean KB contents and live query patterns needed to optimize `AgentPoison`-style backdoor triggers. Instead, enforce three coupled defenses:
1. **Per-Clause Provenance Signatures**: Attach explicit `source` metadata and an originating-agent cryptographic signature (e.g., SHA-256 signature verified client-side before caching or unification) to every stored KB record so untrusted servers cannot inject or mutate facts undetected.
2. **Private Knowledge Retrieval (PKR)**: Conceal which key index $i \in \{1, \dots, n_{pa}\}$ the agent queries—using replicated non-colluding two-server XOR Information-Theoretic PIR (`2-PIR`, sending $2 n_{pa}$ bits and receiving $2r$ bits for information-theoretic single-server query privacy) when two independent hosts are available, or randomized single-server `$k$-anonymity` (fetching $i$ among $k-1$ random decoy indices) rather than deterministic `$b$-buckets`, which leak bucket access frequencies across repeated queries.
3. **Client-Local Resolution with Bounded TTL Caching**: Execute logical unification/inference strictly inside the querying agent and cache verified records under a bounded TTL so recursive subgoals do not emit burst traffic or pay repeated PIR transfer costs.

**Scope:** Python/Prolog prototype (`tipp++`) evaluated over a static signed Horn-clause KB ($n_h = 99$ clauses, $n_{pa} = 46$ `(predicate, arity)` entries padded to $r$ bits) across 18 recursive Prolog benchmark queries (`nreverse` depth 496, `zebra`) in single-machine simulations without network transport latency or dense vector ANN indexing (arXiv:2611.13696).

**Evidence**: In `tipp++` (`arXiv:2611.13696`), cold non-cached two-server XOR `2-PIR` (`it2pir`) completed the 18-query suite in `0.2231 ± 0.0050 s` vs `0.1779 ± 0.0028 s` for the unprotected baseline (`~1.25x` cold cost, `+45.2 ms`) while single-server `$k$-anonymity` (`k = 4..10`) ran in `0.1785–0.1806 s` (statistically indistinguishable from baseline). With client-side TTL caching enabled across runs, `it2pir` dropped to `0.1192 s` on 2-run cold+warm averages and `0.0129 ± 0.0005 s` (`>17x` faster) once warm-cached with zero external queries leaked (see [private-knowledge-retrieval-multi-agent-semantic-memory](../research-briefs/private-knowledge-retrieval-multi-agent-semantic-memory.md)).

See also "DON'T: Rely on prompt-level privacy instructions to keep carried information inside its boundary" (agent-sandbox-safety.md).

> Source: On Private Knowledge Retrieval and Private Inference for secure multi-agent systems (arXiv:2611.13696)

### DO: Pair 2-hop local capability warmup with contextual LLM routing memory in privacy- or scale-constrained decentralized graphs, and harden hubs against misrouting

When global tool catalogs overflow model context (`100K+` tools) or private credentialed tools (`HMAC`/API keys) cannot leave their owning agents (`result`-only remote execution), neither memoryless 1-hop forwarding (`Reflex`), unconstrained neighbor flooding (`Broadcast`), tabular per-tool `Q-Routing`, nor standalone `SFT`/`GRPO` weight post-training generalizes across unseen tools and graph topologies. Equip decentralized peer agents with a **two-stage routing harness (`GraphHarness`)**:
1. **Bounded 2-hop neighbor capability warmup ($W_i$)**: Propagate semantic capability-cluster summaries strictly across 1-hop neighbors for $L = 2$ rounds before task execution so each node acquires directional neighborhood priors without materializing a global registry or exposing private keys.
2. **Separated within-task cache ($h_{i,t}$) and cross-task semantic routing memory ($M_{i,t}$)**: Cache visited `(subquery, neighbor)` pairs and intermediate DAG stage results per episode to suppress loops, while updating cross-task neighbor scores via contextual LLM domain summaries rather than tabular tool-ID scalars or raw past trajectories—deferring any persistent cross-epoch update of $W_i$ or $M_{i,t}$ to "DO: Pass every self-modification through one acceptance gate" and "DON'T: Allow self-modifying agents to optimize prompts or scaffolding solely against performance benchmarks" ([`recursive-improvement.md`](recursive-improvement.md)).
3. **Byzantine hub & conflict hardening**: Authenticate inter-agent routing envelopes, monitor per-neighbor empirical delivery receipts to quarantine misrouting hubs, replicate bridge edges around high-degree scale-free hubs, and stamp routing hints with hop distance and execution receipts to break conflicting directional advice. Procedure: [`topology-warmup-decentralized-routing`](../skills/topology-warmup-decentralized-routing/SKILL.md).

**Scope:** Graph-constrained Dec-POMDP multi-agent tool discovery and execution (`DecArena`) across $N \in \{10, 50, 100, 500, 1000\}$ agents in `Random`, `Scale-Free`, and `Semantic` topologies over a `100K+` HMAC-SHA256 synthesized tool ecosystem (`M = 372` active tools, `186` required tools across `140` multi-hop evaluation tasks: `60` level-1, `40` level-2, `40` level-3; §1 prose states `160` tasks), evaluated across `QWen3.8 27B`, `Qwen3.5 35B A3B`, `Muse Glimmer 30B`, `Gemma 4 26B A4B`, `Gemma 12B`, and `SFT`/`GRPO`/`OPSD`-trained `Qwen3.5-0.8B/2B/4B` (arXiv:2611.15521).

**Evidence**: On `DecArena` (`QWen3.8 27B`, Table 1; `arXiv:2611.15521`), `Global Registry` failed `Out of Context`, `Reflex` scored `5.2%` Success (`27.5%` Collaboration, `37.5%` Efficiency), `Numeric Q-Routing` stalled at `5.0%` Success (`0` values on unseen tools), `Success-Trajectory Memory` dropped to `1.1%`, and `Broadcast` traded flooding inefficiency (`45.7%` Eff) for `40.6%` Success. Combining Stage-1 `Warmup` (`33.8%` alone) with Stage-2 contextual `LLM Q-Learning` (`20.6%` alone; note Table 6 lists individual memory rows on `Gemma 12B`/`Muse Glimmer 30B`) in **`GraphHarness` reached `53.7%` Success (`+48.5` pp over `Reflex`), `58.1%` Collaboration (`+30.6` pp; §5.4 prose prints `57.1`), and `71.5%` Efficiency (`+34.0` pp)**. Zero-weight-update `GraphHarness` on **`Qwen3.5-0.8B` achieved `35.1%` Success**, outperforming `Qwen3.5-4B` post-trained with `SFT` (`0.8%`), `GRPO` (`0.5%`), or oracle `OPSD` (`5.7%`) across unseen topologies and scales (`N = 100–1000`). However, just $k = 1, 2, 3$ adversarial misrouting agents collapsed `QWen3.8 27B` `GraphHarness` Success from **`53.7% -> 22.5% -> 13.5% -> 3.2%`**, and conflicting shortest-path vs. opposite hints in a ring network nearly halved Success from **`53.7%` to `27.2%`**.

Tension with "DON'T: Default to a fixed multi-agent topology" (this file), "DO: Structure inter-agent communication around typed intents and bus substrates" (this file), and "DO: Scale test-time compute on verifiable long-horizon tasks via parallel small flat teams rather than solo Best-of-N, one giant team, or manager orchestration" (this file): when tools and agents share a single trust domain and fit in a directory or typed bus (`N <= 50`), centralized/hierarchical routing or parallel flat `10`-agent teams avoid multi-hop discovery loss and hub fragility (`53.7% -> 3.2%` under $k=3$ misrouters); use decentralized `GraphHarness` warmup + contextual neighbor routing specifically when `100K+` tool schemas exceed context windows or owner-private `HMAC` tools forbid centralizing execution. Tension with "DO: Induce tool dependency graphs via counterfactual sandbox execution and cap retrieval propagation at one hop with top-2 providers per input" (skill-system-design.md): `LIBRA` caps *centralized* full-schema prompt retrieval at `1 hop` to prevent `2.7x` prompt bloat, whereas `GraphHarness` runs `2-hop` *neighbor-summary* propagation across decentralized graph edges so peers acquire compact directional routing priors without loading remote schemas into a single prompt. See also "DON'T: Rely on prompt-level privacy instructions to keep carried information inside its boundary" (agent-sandbox-safety.md).

> Source: DecArena: Evaluating Large-Scale Decentralized Multi-Agent Collaboration (arXiv:2611.15521)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`targeted-failure-attribution`](../skills/targeted-failure-attribution/SKILL.md) — Identifying decisive error agents in multi-agent failures
- [`debate-consensus-memory-calibration`](../skills/debate-consensus-memory-calibration/SKILL.md) — Experience-memory-augmented debate with confidence reweighting
- [`neural-invariant-failure-diagnosis`](../skills/neural-invariant-failure-diagnosis/SKILL.md) — Behavioral state abstraction for failure localization
- [`nlip-agent-message-envelope`](../skills/nlip-agent-message-envelope/SKILL.md) — Standardized semantic message envelopes
- [`persistent-agent-migration`](../skills/persistent-agent-migration/SKILL.md) — Migrating agents while preserving identity and memory
- [`unified-capability-gateway`](../skills/unified-capability-gateway/SKILL.md) — Shared multi-stage capability pipeline
- [`coordinator-executor-prompt-optimization`](../skills/coordinator-executor-prompt-optimization/SKILL.md) — Decoupled coordinator-first prompt optimization for multi-agent teams
- [`proof-carrying-agent-messages`](../skills/proof-carrying-agent-messages/SKILL.md) — Cryptographic Merkle log receipts and three-valued claim checking for inter-agent handoffs
- [`task-graph-contextual-integrity-gating`](../skills/task-graph-contextual-integrity-gating/SKILL.md) — Task-graph contextual integrity (`Auto-Region`) and zero-LLM semantic frontier gating
- [`service-mesh-agent-self-healing`](../skills/service-mesh-agent-self-healing/SKILL.md) — Sidecar proxy mesh with consumer-conditioned reflection and role-based hot failover (`MA-Mesh`)
- [`challenge-aware-knowledge-recruitment`](../skills/challenge-aware-knowledge-recruitment/SKILL.md) — External non-answering Challenger supervision with mid-trace retrieval and isolated specialist recruitment
- [`multi-agent-architecture-first-codegen`](../skills/multi-agent-architecture-first-codegen/SKILL.md) — Four-stage Generator–Evaluator–Human software architecture lifecycle (`TimeArch`)
- [`history-grounded-project-takeover`](../skills/history-grounded-project-takeover/SKILL.md) — Deterministic Requirement Atom replay, non-destructive delta application, and physical artifact-diff verification for project takeover
- [`multi-hop-delegation-auth-propagation`](../skills/multi-hop-delegation-auth-propagation/SKILL.md) — Four-layer transitive authorization verification with origin-private signatures and monotonic scope attenuation for A2A pipelines
- [`parallel-small-team-tts-scaling`](../skills/parallel-small-team-tts-scaling/SKILL.md) — Test-time compute scaling via $K$ parallel small flat peer teams ($M=10$) sharing an asynchronous discovery forum
- [`scoped-multi-agent-harness-composition`](../skills/scoped-multi-agent-harness-composition/SKILL.md) — Isolated role/coordination/memory editors with tested-component composition over provenance-typed evidence graphs (`SciMARS`)
- [`bidirectional-traceability-debate`](../skills/bidirectional-traceability-debate/SKILL.md) — Evidence-locality routing and symmetric Trace/Non-Trace partition-swap debate for requirement-to-code traceability
- [`topology-warmup-decentralized-routing`](../skills/topology-warmup-decentralized-routing/SKILL.md) — 2-hop local capability warmup and contextual experience-adaptive LLM neighbor routing (`GraphHarness` / `DecArena`)

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
- Mining the Design Space of Multi-Agent Workflows: arXiv:2610.31709
- Muffin (Shared Memory Buffer for Asynchronous AI Agents): arXiv:2610.31355
- SMART-Med (Uncertainty-Aware Multi-Agent Routing): arXiv:2610.33544
- The Cost of Saying Hello (Handshake Overhead Benchmark): arXiv:2610.30151
- Who Convinced Whom? (MAD Bench): arXiv:2610.35930
- CEPO (Coordinator-Executor Prompt Optimization): arXiv:2610.34722
- EvolveMAS: arXiv:2610.34450
- Multi-Agent Herding and Runaway Cascades: arXiv:2610.30769
- When Agents Collude (Pact): arXiv:2610.33011
- ReMAS (Black-Box Red-Teaming of MAS): arXiv:2610.28966
- The Coordination Tax and the Heterogeneity Dividend: arXiv:2610.37700
- CuriousTogether: arXiv:2611.01301
- PoPLi (Partner-Outsider Positive Listening): arXiv:2610.37849
- PCM (Proof-Carrying Message Protocol): arXiv:2610.39109
- ParallACT (Decentralized Multi-Agent Coding): arXiv:2611.00314
- Disparity Laundering in Clinical Multi-Agent Systems: arXiv:2610.38215
- MA-Mesh (Role-Based Self-Healing Multi-Agent Mesh): arXiv:2611.06389
- Challenge-Aware Knowledge Recruitment: arXiv:2611.05393
- Disparity Laundering in Clinical MAS: arXiv:2610.38215
- TimeArch (Multi-Agent Software Architecture Design): arXiv:2611.06921
- Take It From Here (ReqMemBench Project Takeover Evaluation): arXiv:2611.07307
- Authorization Propagation in Agent2Agent Systems: arXiv:2611.07050
- Test-Time Compute Scales Better with Parallel Agent Teams: arXiv:2611.09798
- Debate to Deceive (Game-Theoretic Multi-Agent Debate Fact-Checking Poisoning): arXiv:2611.08756
- SciMARS (Multi-Agent Recursive Self-Improvement for Closed-Loop Scientific Discovery): arXiv:2611.12552
- Rethinking Requirement-to-Code Traceability Through Single-Agent and Multi-Agent Approaches: arXiv:2611.09162
- Private Knowledge Retrieval & Private Inference for Secure MAS (tipp++): arXiv:2611.13696
- DecArena / GraphHarness (Large-Scale Decentralized Multi-Agent Collaboration): arXiv:2611.15521
- Understanding the Effects of Multi-Agent Deliberation for Human-AI Decision-Making: arXiv:2611.14901
