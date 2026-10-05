# Skill System Design Rules

> Research-backed guardrails for building, managing, and deploying skill
> libraries for LLM agents. These rules should be active whenever developing
> skill memory systems, tool registries, or context injection pipelines.

---

## Skill Authoring

### DO: Decompose skills to subtask level

Each skill should capture **one reusable procedure**, not an entire
workflow. A skill about "how to build a complete agent pipeline" is
too broad. A skill about "three-tier command classification" transfers
across multiple different agent architectures.

**The test**: if your skill's description could only match ONE kind of
project, it's too specific. If it could match everything, it's too vague.

**Evidence**: task-level skills harm performance by 1.2–4.1 pts vs
no-memory baseline. Subtask-level skills improve by 0.5–1.9 pts.
Validated across 11 models, 3 benchmarks, all difficulty strata.

> Source: Break It Down, Pass It On (arXiv:2608.20274)

### DO: Write skill bodies as natural-language text, not code

Express skills as workflow notes listing procedures and environment
caveats. Code skills lock in implementation details from the source
context — wrong parameters, namespace conflicts, wrong libraries for
the new task.

**Evidence**: text skills transfer better than code skills at both
task-level and subtask-level induction, on every benchmark, at every
difficulty stratum.

**Exception**: include code when it illustrates a specific algorithm
or data structure that would be ambiguous in prose. But the code should
be illustrative, not executable — the agent should adapt it, not
copy-paste it.

> Source: arXiv:2608.20274

### DO: Audit skills with the utility score before deployment

Compute skill utility = specificity × abstractness before deploying new
skills. This requires only skill descriptions and task descriptions — no
execution needed.

- **Specificity**: does the skill match at least one real task?
- **Abstractness**: does it generalize across multiple tasks?
- **Neither alone predicts transfer** — only the product does.

Flag skills with utility < 0.15 for revision.

> Source: arXiv:2608.20274

---

## Skill Selection (Runtime)

### DO: Score skill SETS, not individual skills

Semantic similarity ranks skills independently. But skill utility depends
on what else is in the set — complementary skills compound, redundant
skills waste tokens.

**Evidence**: adding a redundant skill costs 225 tokens for +1pp gain.
Adding an irrelevant but semantically similar skill **drops** success
by 23pp (paper v1; the revised v2 of 28 Sep 2026 reports 12pp). This is
one controlled single-task example in absolute points; the "up to 21%"
in "DON'T: Assume more skills always helps" is a different measurement
(pass-rate loss as libraries grow).

**Scope:** controlled BigCodeBench-based skill-selection testbed.

> Source: Optimal Skill Selection (arXiv:2608.19993)

### DO: Charge a token penalty for every injected skill document

Every token of injected context has a measurable cost (κ). The selection
objective should be `benefit(S) − κ·tokens(S)`, not just `benefit(S)`.
Compressing skill documents and selecting focused skills over exhaustive
ones both improve execution quality.

> Source: arXiv:2608.19993

### DON'T: Score by semantic relevance alone and pack by top-k

Top-k by relevance reaches the optimal skill set on only 7.5% of
instances. It misses complementarity (loading two skills covering the
same capability), ignores redundancy, and doesn't account for token cost.

Use set-level optimization (BPS algorithm or equivalent) when your
library has 10+ skills with overlapping capabilities and a binding
token budget.

> Source: arXiv:2608.19993

### DO: Prefer structured models over black-box neural regressors

A structured capability model with 281 parameters (supply vectors per
skill, demand vectors per task, one penalty coefficient) outperforms
neural set regressors with 16,000+ parameters for predicting skill
set effectiveness. The submodularity inductive bias does the heavy
lifting.

> Source: arXiv:2608.19993

---

## Skill Library Management

### DON'T: Assume more skills always helps

Selecting the wrong skills cuts pass rates by up to 21% as libraries
grow. On 13/87 benchmark tasks, curated skills pushed success below
the no-skill baseline. A larger library requires better selection, not
just more retrieval.

**Scope:** BigCodeBench-based testbed (87 tasks), paper v1. The 21%
figure measures library growth; the 23pp figure in "DO: Score skill
SETS" is a single controlled example. They are not in conflict.

> Source: arXiv:2608.19993

### DO: Measure transfer density, not just skill count

Track which skills are actually reused across tasks. Cut the task stream
into bins and measure the share of (source_bin, target_bin) pairs that
carry actual transfer. Subtask-level libraries show 1.5–3× higher
transfer density than task-level ones.

> Source: arXiv:2608.20274

---

## Skill Evolution

### DO: Separate persistent knowledge from executable skills

When iteratively refining skills, maintain a knowledge layer that persists
across iterations — even when skill changes are rolled back. The knowledge
layer stores root-cause analyses, failure patterns, and successful
strategies. Skills are compiled from this knowledge and can be reverted
independently.

**Evidence**: adding a persistent knowledge layer between raw traces and
skills adds +15.0pp average benchmark performance. Rolling back a bad skill
update should not discard the analysis that motivated it.

> Source: WikiSkill (arXiv:2608.27454)

### DO: Invest in feedback quality over optimizer complexity

Simple single-lineage instruction revision (revise the prompt, evaluate,
repeat) matches or beats complex multi-candidate search methods — as long
as you provide the revision model with rich rollout traces and rewards,
not just scalar scores. Stronger teacher models further reduce the need
for complex search.

**Evidence**: NPO matches/beats GEPA with fewer rollouts. The advantage
increases with stronger teacher models. Rich rollout feedback is the key
ingredient, not the search strategy.

**Scope:** IFBench/HotpotQA with a Qwen3-8B student, prompt-only
(frozen weights). For when to prefer NPO over ESPO or CASD, see
recursive-improvement.md — "DO: Choose the prompt optimizer by data
regime, then gate the result"; the chosen prompt still passes the
acceptance gate there.

See also: recursive-improvement.md — "DO: Use rich rollout feedback for instruction revision, not just scores".

> Source: Naive Prompt Optimization (arXiv:2608.27266)

### DO: Evolve skills with stronger models, deploy to weaker ones

Skills evolved by a stronger model can outperform skills a weaker model
evolved for itself. Skill discovery and skill execution are distinct
capabilities. Invest evolution compute in your strongest model; deploy the
resulting skills to cheaper models.

**Evidence**: Qwen-27B-evolved skills improve Qwen-9B by +26.2pp on
SpreadSheet, vs. +9.3pp from self-evolved skills. Transfer works across
model families.

**Scope:** WikiSkill benchmarks (e.g. SpreadSheet), Qwen 27B to 9B. Test
on each deployment target before reuse: EvoPathBench found skills
evolved by Qwen3.8-Max gave Qwen3.8-27B +1.96 CEG but same-family
Qwen3.5-9B only +0.03 and Qwen3.5-4B +0.27, so stronger-to-weaker
transfer is receiver-dependent even within a family
(research-briefs/process-level-self-evolution-evaluation.md);
SelfOp found transfer within one
family (GPT-5.4 and GPT-5.4-mini, both directions) but did not test
across families (research-briefs/selfop-security-skill-optimization.md),
and scaffolds can reverse sign on sparse-MoE models
(recursive-improvement.md — "DON'T: Assume multi-agent scaffolding is
universally monotonic across model architectures").

> Source: arXiv:2608.27454

---

## Training Data Quality

### DO: Assess agentic data along Accuracy, Complexity, and Diversity

When generating agent training or evaluation data, apply the ACE lens:

- **Accuracy**: Is the data grounded, internally consistent, and
  executable? Accuracy is a hard constraint — invalid data cannot be
  compensated by complexity or diversity.
- **Complexity**: Is it appropriately challenging for the target learner?
  Complexity should be learner-relative, not fixed.
- **Diversity**: Does the collection cover non-redundant situations and
  behaviors? Volume alone doesn't help — redundant data provides little
  additional learning value.

> Source: ACE Lens (arXiv:2608.27260)

### DO: Distinguish insufficient from conflicting evidence — they need different responses

When a retrieval system returns evidence (or an agent meets an
unsupported claim), classify it as sufficient, insufficient, or
conflicting before generating. Insufficient evidence means "I don't have
enough info" — retry retrieval or acknowledge the gap. Conflicting
evidence means "my sources disagree" — surface the contradiction
explicitly. Collapsing both into a single refusal loses information
critical for downstream handling and trust.

**Scope:** RAG question answering; hidden-state probes need open-weight
access.

**Evidence**: A lightweight linear probe on hidden activations from a
single middle layer achieves 0.91 accuracy for 3-way triage across 16
models, reducing false answer rates by 75% over prompt-based baselines.
The hallucination signal in LLM hidden states is a linearly detectable
mean shift, so simple probes suffice for detection without collapsing
the distinction (arXiv:2608.28930).

(Merged: this entry formerly also appeared as "DON'T: Collapse 'missing
evidence' and 'conflicting evidence' into a single refusal" under
Hallucination Detection.)

> Source: Knowing Before Answering (arXiv:2608.27661); The Hallucination
> Signal Is a Mean Shift (arXiv:2608.28930)

---

## Skill Library Integrity

### DO: Validate skill provenance before adding to library

Every skill entering a library must have verified provenance — traceable
origin, lineage (which parent skills or experiences produced it), and
evidence (which task outcomes justified its creation).  Self-evolving
agent systems are vulnerable to skill injection attacks where adversaries
insert malicious skills that persist across evolution rounds and propagate
to unrelated tasks.  An unprovenanced skill is the primary attack vector.

> Source: EvoSkill Injection (arXiv:2608.30429)

### DON'T: Use a pre-execution skill scanner as the sole admission gate for third-party skills

Scanners that combine static rules with per-file LLM review become the
attacker's optimization signal when they can be queried repeatedly.
Admit skills on provenance, constrain admitted skills with per-task
capability scopes and sandboxed, intercepted execution, rate-limit and
log resubmissions, and test scanner and runtime defense together.

**Scope:** SkillsBench (249 skills) with SkillScan + SkillSonar, four
victim LLMs, Codex harness; NVIDIA SkillSpector v2.2.3 with
qwen3t/glm/gpt-oss backends; attackers with repeated detector access.

**Evidence**: Iteratively revised skills reached 45.28% average attack
success with 0% SkillScan detection, against 97.34–100% detection for
baseline attacks. Scanner acceptance took 3.23 rounds on average (95.18%
by round 10). Against a frozen SkillSpector, evasion reached
96.7%/63.2%/70.5%. The static layer caught 5.6%. When the detector also
adapted, false negatives stayed at 47–78% and false positives rose to
50–62% on gpt-oss.

See also "Validate skill provenance before adding to library" (skill-system-design.md) and "Assume stacked defense layers fail independently" (agent-sandbox-safety.md).

> Source: SkillDRE: Dual-Stage Red-Team Evolution of Agent Skills via Pre-Execution and Runtime Feedback (arXiv:2609.32400); Pretext: Defeating Malicious Skill Detection Frameworks for AI Agents (arXiv:2609.39607)

---

## Prompt Context Assembly & Prefix Invariance

### DO: Maintain byte-identical prefix ordering for static skills and tools

When assembling system prompts and injecting skills, order prompt components into
deterministic tiers:
1. Immutable System Persona (never changes across session)
2. Alphabetically Sorted Tool & Skill Schemas (changes only on dynamic tool load)
3. Compacted Milestone Summaries (evictable)
4. Dynamic Turn Observations & Working Scratchpad (volatile tail)

**DON'T**: Inject dynamic variables (timestamps, request UUIDs, turn counters)
into top-level system prompts. Doing so invalidates the entire provider KV cache,
dropping cache hit rates to 0% and dramatically inflating latency and cost.

> Source: ContextPipe (arXiv:2609.00749)

---

## Persistent Agent Architecture

### DO: Decouple continuity-bearing substrate from execution substrate

Architect long-lived agents by separating the **continuity-bearing substrate**
$\mathcal{P}_t = (I_t, M_t, B_t)$ (Identity, Memory, Software Body) from the
transient **execution substrate** $\mathcal{E}_t = (R_t, H_t, D_t)$ (Reasoner
model, orchestration harness, host server).

Substituting a model or server is a **migration**, not agent creation. Enforce a
quiesce–checkpoint–validate–bind–rehydrate–resume protocol to preserve memory
lineage across transitions.

> Source: Runtime-Independent Persistent Agents (arXiv:2609.00546)

---

## Procedural Skill Organization & Life Cycle

### DO: Consolidate skills into procedural families with frozen global priors and locally regenerated instance details

On heterogeneous long-horizon tasks, single-document prompts collapse into generic platitudes, while flat per-task skill pools inflate and suffer from instance coupling. Organize skills into **procedural families**: clusters of tasks sharing an underlying solving procedure.

**Evidence**: Splitting skills into a frozen de-instantiated global prior and an ephemeral locally regenerated instance layer maintains a library **$3.6\times$ more compact** than flat pools, yields **+17.2 points** across diverse benchmarks, and improves unseen task resolution by +10.0%. Enforce execution-gated commit boundaries before admitting candidate prior updates.

> Source: SkillGLoW: Procedural-Family Skill Consolidation (arXiv:2609.02217)

### DO: Distill operational know-how rather than high-level method descriptions

Knowing a theoretical method does not make it work in execution. Distilling open-source repositories into compact, verified operational skills (environment setup, dependency quirks, error recovery, parameter heuristics) provides the missing operational context for autonomous agents.

**Evidence**: Equipping an agent with verified operational skills distilled across repositories boosts end-to-end autonomous research benchmarks by **+134.3% on MLE-bench**, **+34.4% on PaperBench**, and **+14.0% on PassNet** under identical model and downstream execution budgets.

> Source: Repo-To-Skill: Distilling GitHub Repositories Into AI4AI Skills (arXiv:2609.02749)

### DO: Speculate multi-step action skeletons in isolated sandboxes to reduce sequential turn latency

Sequential tool agent turns spend up to 61% of wall-clock time waiting on tool execution and serial observation parsing. Drafting recurring multi-step action macros on isolated environment snapshots and committing cached steps upon actor prefix verification cuts wall time by **up to 44.9%** with zero accuracy penalty.

Speculate only on side-effect-free steps (reads, queries, computations inside the snapshot). Steps with external or irreversible effects (sends, payments, writes outside the sandbox, deployments) are never pre-executed; they run only after the actor confirms them.

**Scope:** tool-using agent benchmarks with snapshot-able environments; the paper's zero-accuracy-penalty result assumes speculative steps can be discarded without external effects.

See also: agent-sandbox-safety.md — "DO: Prefork sandbox environments on predicted execution branches" (same side-effect constraint).

> Source: Speculative Macro Commit for Faster Tool-Using Agents (arXiv:2609.03236)

### DON'T: Rely on dense semantic embeddings alone for retrieving code or executable skills without execution verification

Dense vector embeddings (e.g., text-embedding-3, Cohere embed-v3, Voyage, BGE) measure semantic and topical similarity, not functional correctness. When near-clone counterfactual variants (such as buggy code containing single-line mutations) exist in the search pool, dense retrievers suffer catastrophic rank-1 functional failure. Always gate retrieved code snippets through an execution oracle, differential test suite, or counterexample repair loop before executing or adopting them into memory.

**Evidence**: Across 23 dense embedding configurations and 939 tasks in ExecRetrieval, top-10 retrieval reached 100% (`exec@10 = 1.00`), but top-1 retrieval plunged to `exec@1 = 0.331`. When rank-1 misses occurred, **91.5% to 99.4% were paired buggy distractors**, and canonical correct implementations scored below buggy distractors in **67% to 78% of queries**.

> Source: ExecRetrieval: Measuring the Functional-Correctness Gap in Code-Embedding Retrieval (arXiv:2609.01865)

### DO: Encapsulate inter-agent tool calls and skill invocations in standardized semantic envelopes

Avoid defining bespoke, ad-hoc JSON payloads for inter-agent communication and tool execution across heterogeneous runtimes. Use a standardized application-layer semantic envelope (such as the NLIP standard) that decouples semantic intent, conversation threading, and context referencing from the underlying transport protocol (HTTP, WebSocket, AMQP).

**Scope:** protocol standard (NLIP, Ecma; arXiv:2609.04135); interoperability design, no benchmark.

**Evidence**: Standardized semantic envelopes provide uniform auditability, context URI referencing, and least-privilege capability claims, bridging tool protocols (like MCP) and agent orchestration frameworks (like A2A) across enterprise boundaries without tight transport coupling.

See also: multi-agent-coordination.md — NLIP semantic envelope entry.

> Source: The Natural Language Interaction Protocol and Standard for AI Agents (arXiv:2609.04135)

---

## Harness Self-Evolution

### DO: Bound the search space of harness self-evolution

Agent harness evolution (automatically improving scaffolding, prompts,
and tools) drifts or overfits if the search is uncontrolled. Limit which
components can evolve simultaneously and bound mutation magnitude per
round. Keep rubrics, verifiers, the model and the evaluator fixed.
Controlled search beats less-controlled search: in RobustSGPO, a periodic
edit-permission schedule (one agent, then existing agents, then
structural edits, repeating) reached a held-out test score of 4.34 (0–5
rubric-judged quality scale) vs 4.06 for fixed maximum permission (3.85
for fixed one-agent scope), and the full controlled method scored 4.30
vs 3.82 for less-controlled SGPO (every arm still had replay admission and safety checks). RRSI's unregularized run scored higher
in-distribution (92.8 vs 90.5) but lower out of distribution (40.3 vs
43.6). Broader permission alone did not help; neither paper shows
unconstrained evolution is worse than *no* evolution.

Acceptance defers to recursive-improvement.md — "DO: Pass every
self-modification through one acceptance gate": accept a change only if
it shows no regression beyond a noise margin δ on previously-correct
cases and held-out tasks, where δ is estimated from repeated runs of the
unchanged baseline; the negative security testbed is always strict
(zero tolerance, no margin). Two-Gate validation (arXiv:2609.08175)
formalizes the same idea: adopt only when the estimated failure-task
gain clears a threshold, the estimated change on previously solved
tasks stays within a limit, and the overall gain's lower bound after
estimation error is positive
(research-briefs/reliable-self-evolution-two-gate.md). Change-specific test selection may be
used during search; at acceptance and deploy, run the full frozen and
security suites.

**Scope:** harness evolution around a frozen model (RobustSGPO: one
AgentX brainstorming workflow, 120 tasks, proposals capped at 120
changed lines and 6,000 added characters; RRSI: agentic-workspace,
coding and design benchmarks); 2609.08175 is theoretical with one
DS-1000 illustration.

Tension with "DO: Make the improvement mechanism part of the agent's
editable source" (recursive-improvement.md): resolved by scope — the
improvement logic may be editable, but only inside a fixed, declared
editable set with bounded per-round change; evaluator, graders, security
tests and permissions stay outside.

> Source: RobustSGPO (arXiv:2609.09646); RRSI (arXiv:2609.24972);
> A Theory of Reliable Self-Evolution for Agent Harnesses (arXiv:2609.08175)

---

## Recursive Self-Improvement Feasibility

### DON'T: Assume recursive self-improvement is unbounded

Recursive self-improvement has theoretical feasibility limits.
An agent cannot improve itself beyond the ceiling imposed by its
optimization substrate, evaluation capability, and the complexity
of the improvement search space.  Design skill evolution loops with
explicit convergence criteria and diminishing-returns detection
rather than assuming open-ended improvement.

**Scope:** a feasibility argument about evaluator, substrate and
search-space limits, not a measured capability ceiling. Evolutionary
Safety of RSI (arXiv:2609.31186) takes no position on ceilings; RRSI's
limitations section (arXiv:2609.24972) says its effectiveness may
depend on the quality of the feedback signal. The Two-Gate theory
(arXiv:2609.08175) derives a ceiling set by verification and evaluation
cost for its validation rule, and shows a different rule can validate
past it at higher evaluation cost.

Tension with "DO: Distinguish systems, data, and algorithmic changes"
(recursive-improvement.md), which says algorithmic change is bounded by
"nothing fundamental": that table refers to hardware/data ceilings; this
entry refers to evaluator quality and diminishing returns. Both hold.

> Source: The Last AI Built by Humans (arXiv:2609.11873); Evolutionary Safety of Recursive Self-Improving AI (arXiv:2609.31186); RRSI (arXiv:2609.24972); A Theory of Reliable Self-Evolution for Agent Harnesses (arXiv:2609.08175)

---

## Context Decoupling & Reasoning Anti-Looping

### DO: Decouple agent context into file ledgers to prevent runaway reasoning loops

When deploying mid-sized dense models (14B–35B) or long-horizon reasoning agents on complex problems, unconstrained single-call generation often degrades into degenerative self-verification loops (e.g., repeating edge-case interrogations thousands of times until hitting token limits). Decouple agent state into a shared filesystem ledger (`plan.md`, `notes.md`, `tasks.json`, `solution.py`), invoke subagents in fresh zero-shot contexts with bounded payloads, and actively prune working notes (<800 words).

**Evidence**: On the 100 latest Hard LiveCodeBench problems, single-call Qwen3.8-27B suffered 35 empty-output failures from runaway deliberation loops (e.g. repeating a verification check 7,743 times). A zero-shot ledger scaffold rescued 25 of these (+5.0 points) and lifted overall Pass@1 from 63.0% to 86.4% (+23.4 points), matching Claude Fable 5 (87.4%). The comparison is asymmetric: Fable 5 was run single-call with no tools and no code execution, while the scaffolded Qwen got up to 10 manager-to-worker rounds with subprocess test execution.

**Exception — sparse MoE / low active parameters**: the same paper found the scaffold hurt Qwen3.6-35B-A3B (3B active): −1.2 points at 16k and −9.0 points at 128k with reasoning off. Benchmark the scaffold per model family before deploying it.

**Scope:** LiveCodeBench Hard (100 latest problems), 128k cap, paper v1 numbers (v2 of 21 Sep 2026 revised them).

See also: recursive-improvement.md — "DON'T: Assume multi-agent scaffolding is universally monotonic across model architectures" (same paper).

> Source: Zero-Shot Self-Orchestration with Ledger-Based Control (arXiv:2608.26480)

---

## Orchestration Boundaries: Graph vs. Collaborative vs. Dynamic

### DO: Keep deterministic steps in code and explicit graph edges; delegate to LLMs only for reasoning

In multi-agent systems, never use prompt-based LLM routing or LLM nodes for tasks that can be modeled as deterministic functions or explicit directed edges.
1. **Pillar 1 (Graph Workflow)**: When execution order is known prior to input arrival, use static workflow graphs with explicit dictionary edges (`edges={router_func: {"key": target_node}}`) and join nodes (`JoinNode(branches=[...])`). Pure function nodes are peer graph nodes that execute with $0$ LLM calls, zero cost, and zero hallucination risk.
2. **Pillar 2 (Collaborative Agents)**: When a known team of specialists exists and the input determines the subset, use a coordinator with `mode="single_turn"` for parallel tool dispatch and synthesis, or `mode="task"` with explicit typed termination schemas (`finish_task(schema)`) for conversational subroutines.
3. **Pillar 3 (Dynamic Workflows)**: When runtime width or depth cannot be predicted statically, bound fan-out via worker nodes (`@node(parallel_worker=True)`) and recursive descent via strict recursion depth checks (`MAX_DEPTH`).

**Scope:** ADK 2 graph, collaborative and dynamic workflows (Google ADK codelab); the 4-to-1 LLM-call figure is a single codelab example, not a controlled benchmark.

**Evidence**: In ADK 2 benchmarked workflows, replacing prompt-based sequential LLM dispatch with an explicit graph router and pure function nodes dropped LLM API calls from 4 to 1 per request while eliminating routing drift and schema translation errors.

See also: adk-workflow-architecture.md — deterministic-steps-first and typed `finish_task` entries; recursive-improvement.md — "DO: Enforce hard depth boundaries and typed terminal schemas on recursive agent invocations".

> Source: Google Cloud Tech & ADK 2 Orchestration Codelab (ADK 2: Graph, Collaborative & Dynamic Workflows)

---

## Context Management & Protocol Preservation

### DO: Enforce protocol-aware context trimming with adaptive budget guardrails

When reducing context in long-horizon agentic workflows, prioritize preserving protocol-critical state (tool schemas, unresolved request/response pairs, causal state mutations, active invariant constraints) over maximizing raw token removal. Avoid uniform aggressive context trimming ($\le 25\%$ retained tokens), which inflates task failure odds by 10.92-fold ($p < 0.001$). Dynamically adapt budget guardrails to workflow complexity classes: retain $\ge 35\%$ for linear tasks, $\ge 50\%$ for branching trees, and $\ge 60\%$ for iterative/cyclic debugging.

**Evidence**: Naive recency, relevance, or summarization trimming drops task success to 66.6%–77.3% and protocol adherence to 85.5%–88.6%. Protocol-aware trimming lifts task success to 92.2% (5.24× odds improvement under aggressive budgets); adaptive guardrails achieve 96.0% task success, 96.3% protocol adherence, and reduce cascading failures to 1.0% with 56.0% mean token savings.

**Scope:** one study of simulated tool-mediated workflows (AgentBench/τ-bench-style) stratified by low/medium/high complexity, not by linear/branching/cyclic shape. The 10.92× figure compares budgets ≤25% with ≥50%. The 35/50/60% floors are this library's conservative heuristic, not values from the paper: its estimated critical thresholds were 20.8/25.4/38.2% for protocol-aware trimming and <15/21.1/29.5% for adaptive guardrails (low/medium/high complexity), versus 45–53% for recency trimming. The floors clear the protocol-aware and guardrail thresholds but not the recency-trimming ones, so they assume protocol-aware trimming. The skill uses the same floors.

> Source: Protocol-Preserving Context Trimming for Agentic Workflows: Benefits, Failure Regimes, and Budget Guardrails (arXiv:2609.16461)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md) — Full skill authoring methodology
- [`capability-aware-skill-selection`](../skills/capability-aware-skill-selection/SKILL.md) — BPS algorithm and capability model
- [`knowledge-compounding-loop`](../skills/knowledge-compounding-loop/SKILL.md) — Persistent knowledge accumulation
- [`iterative-instruction-refinement`](../skills/iterative-instruction-refinement/SKILL.md) — NPO-style revision loop
- [`rag-evidence-triage`](../skills/rag-evidence-triage/SKILL.md) — Three-way evidence classification
- [`skill-evolution-defense`](../skills/skill-evolution-defense/SKILL.md) — Hardening skill evolution loops
- [`hallucination-mean-shift-probe`](../skills/hallucination-mean-shift-probe/SKILL.md) — Linear probe hallucination detection
- [`prefix-preserving-context-assembly`](../skills/prefix-preserving-context-assembly/SKILL.md) — Database-style context assembly
- [`protocol-preserving-context-trimming`](../skills/protocol-preserving-context-trimming/SKILL.md) — Protocol-aware context trimming and budget guardrails
- [`persistent-agent-migration`](../skills/persistent-agent-migration/SKILL.md) — Runtime-independent agent migration
- [`trajectory-aware-eval-pruning`](../skills/trajectory-aware-eval-pruning/SKILL.md) — Trajectory-aware benchmark item selection
- [`procedural-family-skill-consolidation`](../skills/procedural-family-skill-consolidation/SKILL.md) — Hierarchical global/local skill consolidation
- [`speculative-macro-commit`](../skills/speculative-macro-commit/SKILL.md) — Pre-executing multi-step tool action skeletons
- [`counterexample-guided-repair`](../skills/counterexample-guided-repair/SKILL.md) — Multi-turn artifact refinement using counterexample witnesses
- [`nlip-agent-message-envelope`](../skills/nlip-agent-message-envelope/SKILL.md) — Standardized semantic message envelopes and gateway bridging
- [`stable-skill-evolution`](../skills/stable-skill-evolution/SKILL.md) — Adam-style stabilization for skill evolution
- [`graph-of-skills-scaling`](../skills/graph-of-skills-scaling/SKILL.md) — Typed graph structure for skill library scaling
- [`static-dynamic-verification-gap-measurement`](../skills/static-dynamic-verification-gap-measurement/SKILL.md) — Measuring static-pass dynamic-fail gaps
- [`bayesian-backward-disagreement-anchor`](../skills/bayesian-backward-disagreement-anchor/SKILL.md) — Label-free multi-agent disagreement resolution
- [`ledger-orchestrated-coding-loop`](../skills/ledger-orchestrated-coding-loop/SKILL.md) — File-ledger multi-turn loop with test veto
- [`adk2-agent-orchestration-patterns`](../skills/adk2-agent-orchestration-patterns/SKILL.md) — Three pillars of agent orchestration (Graph, Collaborative, Dynamic)

## Sources

- Break It Down, Pass It On: arXiv:2608.20274
- Optimal Skill Selection: arXiv:2608.19993
- WikiSkill: arXiv:2608.27454
- Naive Prompt Optimization: arXiv:2608.27266
- ACE Lens: arXiv:2608.27260
- Knowing Before Answering: arXiv:2608.27661
- EvoSkill Injection: arXiv:2608.30429
- Hallucination Mean Shift: arXiv:2608.28930
- ContextPipe: arXiv:2609.00749
- Runtime-Independent Persistent Agents: arXiv:2609.00546
- Efficient SWE Agent Benchmarking: arXiv:2609.01603
- SkillGLoW: arXiv:2609.02217
- Repo-To-Skill: arXiv:2609.02749
- Speculative Macro Commit: arXiv:2609.03236
- ExecRetrieval: arXiv:2609.01865
- Natural Language Interaction Protocol (NLIP): arXiv:2609.04135
- A Theory of Reliable Self-Evolution for Agent Harnesses: arXiv:2609.08175
- RobustSGPO: arXiv:2609.09646
- RRSI: arXiv:2609.24972
- Evolutionary Safety of Recursive Self-Improving AI: arXiv:2609.31186
- The Last AI Built by Humans: arXiv:2609.11873
- Zero-Shot Self-Orchestration: arXiv:2608.26480
- Google Cloud Tech / ADK 2 Orchestration: Graph, Collaborative & Dynamic Workflows
- Protocol-Preserving Context Trimming: arXiv:2609.16461
- SkillDRE: arXiv:2609.32400
- Pretext: arXiv:2609.39607

