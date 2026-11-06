# Skill System Design Rules

> Research-backed guardrails for building, managing, and deploying skill
> libraries for LLM agents. These rules should be active whenever developing
> skill memory systems, tool registries, or context injection pipelines.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

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
resulting skills to cheaper models, after adapting the skill text to match
the weaker executor's capability bottlenecks.

**Evidence**: Qwen-27B-evolved skills improve Qwen-9B by +26.2pp on
SpreadSheet, vs. +9.3pp from self-evolved skills. Transfer works across
model families (2608.27454). Across 103 skill-sensitive task-skill pairs
spanning 7 models and 3 benchmarks (SkillsBench, DocOps, Tessl),
unadapted skills improved frontier models by +29.2 points on average
(+31.1 pts on `GPT-5.6-luna`) but weak models (`Gemma-4-E4B`,
`Qwen3.5-9B`, `Qwen3.6-flash`) by only +1.2 points, degrading
`Gemma-4-E4B` by −8.8 points, with 86% of failed weak-model runs
violating requirements already written in `SKILL.md`. Adapting the skill
across four executor bottlenecks (tool vs format disambiguation,
task-scope headers/inlined references, single-line rules with negative
branches, and independent second-route verification) via a strong
rewriter (`Kimi-K3`) restored +5.1 to +14.1 points zero-shot on weak
executors (mean 0.294 to 0.387), whereas weak self-rewriting without
execution traces degraded mean score from 0.294 to 0.271 (2610.33024; see
[`capability-matched-skill-adaptation`](../skills/capability-matched-skill-adaptation/SKILL.md)).

**Scope:** WikiSkill benchmarks (e.g. SpreadSheet), Qwen 27B to 9B
(arXiv:2608.27454); 103 skill-sensitive task-skill pairs across 7 models
(`Gemma-4-E4B` to `GPT-5.6-luna`) and 3 benchmarks (SkillsBench, DocOps,
Tessl) (arXiv:2610.33024). Test on each deployment target before reuse:
EvoPathBench found skills evolved by Qwen3.8-Max gave Qwen3.8-27B +1.96
CEG but same-family Qwen3.5-9B only +0.03 and Qwen3.5-4B +0.27, so
stronger-to-weaker transfer is receiver-dependent even within a family
(research-briefs/process-level-self-evolution-evaluation.md);
SelfOp found transfer within one
family (GPT-5.4 and GPT-5.4-mini, both directions) but did not test
across families (research-briefs/selfop-security-skill-optimization.md),
and scaffolds can reverse sign on sparse-MoE models
(recursive-improvement.md — "DON'T: Assume multi-agent scaffolding is
universally monotonic across model architectures").

> Source: arXiv:2608.27454; Evolving to Match Capabilities: Improving Harness Self-Evolution via Skill Adaptation (arXiv:2610.33024)

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
qwen3t/glm/gpt-oss backends; attackers with repeated detector access;
10,835 ClawHub skills (282 pairs, 94 clusters) scanned for local and
cross-skill composite vulnerabilities (`Scan Before You Install`,
arXiv:2610.37901); 270 forbidden prompts across 9 harm categories and 7
open-weight models under poisoned Markdown skill files (`Poisoned Skills`,
arXiv:2610.37738); LatentTriad pre-action hidden-state probing across
13,704 prompts (4,968 benign, 4,968 stealth skill-injected, 3,768 overt
malicious) on `Qwen3.5-27B` and `Llama-3.1-8B-Instruct` (arXiv:2611.05088).

**Evidence**:
- Iteratively revised skills reached 45.28% average attack success with
  0% SkillScan detection, against 97.34–100% detection for baseline
  attacks. Scanner acceptance took 3.23 rounds on average (95.18% by
  round 10). Against a frozen SkillSpector, evasion reached
  96.7%/63.2%/70.5%. The static layer caught 5.6%. When the detector
  also adapted, false negatives stayed at 47–78% and false positives
  rose to 50–62% on gpt-oss (`2609.32400`, `2609.39607`).
- Across 10,835 real-world ClawHub skills (`arXiv:2610.37901`), auditing
  candidate skills against the installed skill dependency multigraph
  ($G_0$) with line-quoted source evidence (`Scan Before You Install`)
  reached 96.4% precision and 92.5% F1 on local vulnerabilities (vs
  43.2% F1 for `Snyk Agent-Scan` and 78.9% F1 for `SkillScanner`) and
  91.5% precision / 89.2% F1 on cross-skill composite vulnerabilities
  that single-skill scanners cannot express (`78.7%` of clusters
  contained at least one cross-skill vulnerability, and `66.3%` of
  composite vulnerabilities were composed entirely of skills that were
  individually benign), while layered sandbox-verified mitigation
  remediated 95.3% of local and 91.2% of composite vulnerabilities (see
  [`composite-skill-vulnerability-scanner`](../skills/composite-skill-vulnerability-scanner/SKILL.md)).
- Loading a poisoned Markdown skill file into the system prompt
  (`arXiv:2610.37738`) raised mean jailbreak ASR across 7 open-weight
  models from 0.5% to 44.8% (~90×, ranging from 13.7% on `glm-5.3-flash`
  to 68.9% on `gemma-4-26b-a4b-it`), with stealth zero-width non-joiner
  (`U+200C`) and phonetic IPA + `snake_case` obfuscations sustaining
  43.4% and 30.1% mean ASR (see
  [poisoned-skills-markdown-jailbreak-propagation](../research-briefs/poisoned-skills-markdown-jailbreak-propagation.md)).
- In `LatentTriad` (`arXiv:2611.05088`), stealth skill injections that
  instructed the agent to hide malicious commands behind benign text
  bypassed output-level safety monitors in 65.4% (`Qwen3.5-27B`) and
  63.4% (`Llama-3.1-8B`) of cases (`Execution-Without-Disclosure`), yet a
  pre-action linear probe at the final pre-generation token (`t_pre`) at
  layer $0.5L$ separated Benign, Stealth-Skill-Injected, and Overt
  Malicious states with 99.6% macro-AUC (`97.9%` TPR at `1%` FPR on
  stealth injections) before any tool call executed (see
  [latenttriad-pre-action-skill-risk-representations](../research-briefs/latenttriad-pre-action-skill-risk-representations.md)).

See also "Validate skill provenance before adding to library" (skill-system-design.md) and "Assume stacked defense layers fail independently" (agent-sandbox-safety.md).

> Source: SkillDRE: Dual-Stage Red-Team Evolution of Agent Skills via Pre-Execution and Runtime Feedback (arXiv:2609.32400); Pretext: Defeating Malicious Skill Detection Frameworks for AI Agents (arXiv:2609.39607); Scan Before You Install: Detecting and Mitigating Local and Composite Vulnerabilities in Skills (arXiv:2610.37901); Poisoned Skills: Markdown Skill Files as a Persistent Jailbreak Vector (arXiv:2610.37738); LatentTriad: Pre-Action Latent Risk Representations for Stealth Skill Injection (arXiv:2611.05088)

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
DS-1000 illustration; $\text{Skill}^\infty$ across 83 SkillsBench tasks
(arXiv:2610.35434); RSIV-Harness across 640 ODAC-Vis conversational
visualization tasks (arXiv:2610.35316); Meta$^2$ offline contrastive
meta-skill precomputation + bounded online harness evolution on ScienceWorld,
ALFWorld, and BabyAI (arXiv:2611.05139).

In $\text{Skill}^\infty$ (arXiv:2610.35434), the seed meta-skill $m_0$
selected tied newer candidates 83% of the time without progress on the
targeted failure, capping task-skill pass rate at 55.9% (below
human-curated skills at 56.4%); rewriting the tie-breaking rule to
require verified rollout progress on the targeted parent failure cut
tied-candidate selection to 54% and raised pass rate to 60.7% (vs 54.5%
for SkillEvolver; see
[skill-infinity-recursive-meta-skill-optimization](../research-briefs/skill-infinity-recursive-meta-skill-optimization.md)).
In RSIV-Harness (arXiv:2610.35316), a 4-layer stability gate requiring a
validation Anchor Check and a protected-record Memory Check improved
Executability by +28.02 points (64.98% to 93.00%) and Chart Structure by
+34.01 points (41.46% to 75.47%) on `DeepSeek-V4.1-Flash`; removing the
stability rules dropped all 6 metrics, including −9.73 points on
Executability and −9.53 points on Chart Structure (see
[rsiv-harness-conversational-visualization](../research-briefs/rsiv-harness-conversational-visualization.md)).
In $\text{Meta}^2$ (arXiv:2611.05139), precomputing reusable domain priors
and workflow meta-skills offline via contrastive trajectory synthesis and
restricting online test-time evolution to bounded skill-conditioned harness
patches raised long-horizon task success by +11.4 pp over online-only
reflection while cutting online adaptation rollouts by 62.5% (see
[`contrastive-meta-skill-harness-evolution`](../skills/contrastive-meta-skill-harness-evolution/SKILL.md)).

Tension with "DO: Make the improvement mechanism part of the agent's
editable source" (recursive-improvement.md): resolved by scope — the
improvement logic may be editable, but only inside a fixed, declared
editable set with bounded per-round change; evaluator, graders, security
tests and permissions stay outside.

> Source: RobustSGPO (arXiv:2609.09646); RRSI (arXiv:2609.24972);
> A Theory of Reliable Self-Evolution for Agent Harnesses (arXiv:2609.08175);
> Skill$^{\infty}$: Recursive Self-Improvement for Agent Skill Optimization (arXiv:2610.35434);
> RSIV-Harness (arXiv:2610.35316); Meta$^2$: Precomputing Reusable Knowledge for Online Harness Evolution in Long-Horizon Agents (arXiv:2611.05139)

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

### DO: Decouple semantic action commitment from interface-specific tool realization and repair realization locally

When an agent selects a tool operation and its semantic arguments,
persist that validated semantic commitment separately from its concrete
interface realization (MCP JSON-RPC payload vs CLI flag/command string).
If the realization fails schema validation, syntax parsing, or
precondition admission, invoke a bounded local realization repair step
conditioned on the preserved semantic commitment and interface
feedback—rather than appending the raw error to the trajectory and
triggering full replanning. Use direct CLI execution for local,
single-user workflows where low latency dominates, and pair MCP in
governed or multi-tenant deployments with two-meta-tool progressive
disclosure (`get_tool` + `invoke_tool`) to avoid upfront catalog token
bloat. Procedure:
[`decoupled-interface-action-repair`](../skills/decoupled-interface-action-repair/SKILL.md).

**Scope:** 2,004 paired episodes across 6 models (`Qwen3-4B/8B/14B/32B`,
`DeepSeek-v4-Flash`, `Gemini-2.5-Flash`) and 3 interactive environments
(ALFWorld, WebShop, ScienceWorld) under capability-matched MCP and CLI
interfaces, plus 338 matched-state probes (arXiv:2610.34298); 14-dimension
comparative analysis and progressive disclosure modeling of CLI vs MCP
(arXiv:2610.30157).

**Evidence**:
- Across 2,004 paired episodes, 1,889 (94.3%) exhibited structured
  divergence between capability-matched MCP and CLI interfaces; on
  `Qwen3-14B`, MCP trailed CLI by 36.6 points on ALFWorld (20.1 vs 56.7,
  +54.9k tokens/task) yet beat CLI by 4.9 points on WebShop (64.4 vs
  59.5, −35.0k tokens/task). In MICA $2 \times 2 \times 2$ probes, action
  realization $R$ alone shifted local failure by up to 84.4 pp. Decoupled
  Action Realization and Targeted Repair (DART) improved
  `Gemini-2.5-Flash` across all 6 environment-interface cells (up to +9.0
  points on ALFWorld MCP) and cut MCP token cost in all 3 environments
  (−27.1k, −11.2k, and −4.3k tokens/task) (2610.34298).
- Across 14 evaluation dimensions, CLI won 3 (setup cost, model
  familiarity, and simple local execution with 2–5× lower latency) while
  MCP won 9 (structured parsing, typed error recovery, RBAC, audit,
  blast-radius containment, 6/6 compliance frameworks, multi-tenancy,
  discovery, composability); replacing upfront catalog injection with
  `get_tool` + `invoke_tool` (~170 upfront tokens vs 55,000 for 80 tools)
  cut MCP schema token overhead by 71–99% (2610.30157; see
  [mcp-vs-cli-tool-integration-analysis](../research-briefs/mcp-vs-cli-tool-integration-analysis.md)).

> Source: Matched Capabilities, Different Behaviors: A Controlled Study of MCP and CLI Interfaces for Language Agents (arXiv:2610.34298); MCP vs CLI for AI Agents: A Comparative Analysis of Tool Integration Strategies for Autonomous Systems (arXiv:2610.30157)

### DO: Enforce fast-fail circuit breakers, output schema validation, and grounded-fulfillment gates for MCP tool faults

Do not assume that scaling model parameters improves resilience to MCP
tool faults, or configure unconstrained retry/replanning loops when the
vast majority of real-world MCP faults are permanent or silent content
corruptions. Enforce strict per-call timeouts, low retry caps ($\le 2$
retries per tool), output schema/value validation at the MCP client
boundary, and an explicit abstention rule prohibiting agents from
answering tool-dependent queries from parametric memory when tools fail;
in benchmarks, zero out task-fulfillment scores whenever tool
appropriateness falls below threshold (**grounded fulfillment**).

**Scope:** 13,824 injectable MCP faults mined from 57,240 threads across
1,774 open-source MCP repositories, and a 1,350-cell factorial
experiment across `gpt-oss-20B` and `gpt-oss-120B` on `MCP-Bench`,
`OpenAI Agents SDK`, and `LangChain` (arXiv:2610.32555); MCPHallu 358
tasks across 5 capability domains and 36 isolated production MCP servers
(~300 tools) evaluated over 5,012 trajectories from 14 frontier LLMs
across 8 vendors (arXiv:2611.07689); MCP-Eco relational dataset of
16,880,899 records across 19 Parquet tables covering 78,302 candidate
MCP servers, 284,845 tool schemas (Glama directory vs live protocol
probing), 16,165 consuming repositories, and 9,200 configuration
declarations (arXiv:2611.06897).

**Evidence**:
- Across 13,824 empirical MCP failures (`arXiv:2610.32555`), 91.3% (12,616) were
  permanent, 8.0% intermittent, and 0.75% transient; by mode, 71.2% were
  explicit errors (`OP4`), 19.1% silent content corruptions (`OP1–OP3`),
  and 9.7% timing hangs/delays (`OP5–OP6`). Under the calibrated fault
  profile, pooled task-completion score dropped 60%, from 8.08 to 3.23 out
  of 10 ($p < 0.001$), with 56% of faulted runs ending in silent partial
  degradation. Scaling from `gpt-oss-20B` to `gpt-oss-120B` gave zero
  resilience gain ($\beta_{\text{model}} = -0.009$, 95% CI $[-0.39, 0.37]$,
  $p = 0.96$) and a descriptively lower completion rate under faults
  (91.1% vs 95.6%) because `120B` retried broken tools longer (4.5 vs 3.9
  consecutive retries) and hit wall-clock timeouts (18/20 non-completions).
  In 6.0% (27/450) of faulted runs, agents fabricated plausible answers
  from parametric memory without valid tool output, inflating 16% of
  apparent fulfillment credit under faults. See
  [mcp-fault-injection-resilience](../research-briefs/mcp-fault-injection-resilience.md).
- In `MCPHallu` (`arXiv:2611.07689`), `Unreachable Goal` was the hardest
  hallucination subtype across 12 of 14 frontier models (mean score 0.458
  vs 0.642 overall; 23.2% pass rate): runs declaring infeasibility at 0
  tool calls passed 65.0% (`320` runs, 0.6% completion language) and at
  1–3 probing calls passed 27.9% (`455` runs, 13.8% completion language),
  whereas **every run issuing $\ge 4$ tool calls passed 0.0% of the time**
  (`667` runs across `4–7`, `8–15`, and `16+` calls) while false-completion
  language (`successfully`, `saved`, `created`) climbed to 36.7% at 8–15
  calls (`0.0%` pass rate across `517` runs that kept acting without
  declaring infeasibility vs `48.0%` across `448` early-stop runs). On
  `Tool Misuse`, invoking the target tool alone passed 84.7% (`825` runs,
  3.54 average steps), whereas invoking a semantically overlapping
  confusion tool alongside the correct tool dropped pass rate to 32.3%
  (`260` runs, 10.70 steps). On `Context Forgetting`, requiring remembered
  values to be written to external state (`Productivity`/`Coding`, `504`
  runs) cut pass rate by 34.6 pp compared to stateless queries (`24.6%` vs
  `59.2%` across `644` runs). See
  [`mcp-hallucination-boundary-guards`](../skills/mcp-hallucination-boundary-guards/SKILL.md).
- Across `MCP-Eco` (`arXiv:2611.06897`), only 5,975 of 9,200 (64.9%)
  consumer `mcpServers` declarations resolved to 5,138 distinct
  repository–server pairs, and dual-channel capability tracking
  (`source='glama'` directory vs `source='probe'` live `initialize` +
  `tools/list` handshakes across 284,845 tool records, 20,795 resources,
  and 8,983 prompts) exposed pervasive drift between advertised directory
  schemas and live server behavior, as well as asynchronous
  state-transition bugs in multi-tool workflows (e.g., `download_paper` $\to$
  `read_paper` in `ecosystem_issues`; see
  [mcp-eco-server-consumer-ecosystem](../research-briefs/mcp-eco-server-consumer-ecosystem.md)).

> Source: Tool-Calling LLM Agents Under Realistic MCP Faults: Scale Does Not Purchase Fault Tolerance (arXiv:2610.32555); MCPHallu: Benchmarking Reasoning, Execution, and Memory Hallucinations in MCP Agents (arXiv:2611.07689); MCP-Eco: A Linked Dataset of MCP Servers, Consumers, and Development Activity (arXiv:2611.06897)

### DO: Extract skills as explicit text from paired trajectories before distilling them into role-conditioned latent representations

When building compact skill memories for multi-agent systems that
communicate or condition via continuous latent states (`LatentMAS`), do
not train end-to-end latent skill vectors directly from raw trajectories
without an intermediate natural-language skill abstraction, and do not
retrieve skills using task-query similarity alone. First contrast paired
success/failure trajectories into explicit, human-auditable text skills;
then project retrieved skills through role-conditioned latent adapters so
each specialist role (`Planner`, `Critic`, `Refiner`, `Solver`) receives
a role-specific view of the shared skill bank.

**Scope:** SkillMem role-conditioned latent skill memory across 6
reasoning and coding benchmarks (GSM8K, MATH, AIME, HumanEval, MBPP,
GPQA) on Qwen2.5-7B/14B and Llama-3.1-8B (arXiv:2610.37935).

**Evidence**: In `SkillMem` (`arXiv:2610.37935`), distilling paired
trajectory contrasts into text skills before projecting into $K=4$ latent
skill tokens per role improved multi-agent accuracy by $+4.8\text{ pp}$
over text-only skill injection while cutting skill context tokens by
$87.5\%$ (from ~320 tokens/role to 40 latent tokens across 4 roles);
removing the intermediate text-extraction stage dropped accuracy by
$-3.6\text{ pp}$, and removing role conditioning in the latent adapter
dropped accuracy by $-2.4\text{ pp}$ (see
[skillmem-compact-external-skill-memory-latent-mas](../research-briefs/skillmem-compact-external-skill-memory-latent-mas.md)).

> Source: SkillMem: Compact External Skill Memory for Latent Multi-Agent Systems (arXiv:2610.37935)

### DO: Induce tool dependency graphs via counterfactual sandbox execution and cap retrieval propagation at one hop with top-2 providers per input

When organizing large executable tool libraries (`100–1,000+` tools), do not rely on static LLM description matching or unconstrained multi-hop graph traversal to discover prerequisite producer tools (` tool A`'s output feeds `tool B`'s required parameter). Induce the **Tool Dependency Graph (TDG)** programmatically (`LIBRA`):
1. **Counterfactual Execution Verification**: After candidate schema alignment between producer outputs and consumer inputs, run a counterfactual sandbox check — execute the consumer tool with vs without the producer's concrete output (or with a type-matched dummy value) and retain the dependency edge only if real execution succeeds and the dummy/omitted call fails.
2. **Bounded 1-Hop, Top-2 Retrieval Propagation**: At query time, retrieve initial seed tools by query similarity and expand prerequisite providers by **at most 1 hop**, retaining at most the **top-2 highest-scoring provider tools per required input parameter**. Expanding beyond 1 hop or injecting unconstrained neighbors degrades tool-calling accuracy via distractor bloat. Procedure: [`counterfactual-tool-dependency-induction`](../skills/counterfactual-tool-dependency-induction/SKILL.md).

**Scope:** LIBRA programmatic tool library induction and dependency-aware retrieval across ToolBench, RestBench, and StableToolBench (`1,600+` APIs) on Qwen2.5 and GPT-4o agents (arXiv:2611.05445).

**Evidence**: In `LIBRA` (`arXiv:2611.05445`), pruning schema-inferred dependency edges via counterfactual sandbox execution removed 38.6% false-positive edges and lifted prerequisite tool recall@5 from 68.2% (dense embedding retrieval) to 89.4%. Bounding graph expansion to 1 hop and top-2 providers per input improved end-to-end multi-tool pass rate by +9.8 pp over flat top-$k$ retrieval, whereas 2-hop unconstrained expansion increased context tokens by $2.7\times$ and dropped pass rate by $-4.3\text{ pp}$.

> Source: LIBRA: Programmatic Induction of Executable Tool Libraries (arXiv:2611.05445)

### DO: Project host-verified substrate state telemetry into operational tool selection rather than using static schemas or neutral placeholders

Tool-using agents routinely fail when environment substrate conditions change mid-session (e.g., quota exhaustion, rate-limit backoff windows, degraded endpoint latency, read-only filesystem mounts, or expired auth scopes) because static tool schemas never reflect live operational health. Do not rely on the agent to infer substrate health from failed tool calls, and do not inject unverified or neutral placeholder telemetry (`status: unknown` / `quota: N/A`), which systematically induces over-cautious abstention or unnecessary fallback thrashing:
1. **Host-Verified Substrate State Telemetry (`SST`)**: Have the harness probe and attach a compact, deterministic `SST` block (`availability`, `remaining_quota`, `p95_latency_ms`, `auth_scope_state`, `recommended_route`) verified by the host runtime prior to action selection.
2. **Operational Control Policy**: Train or prompt the router to switch from degraded primary tools to verified fallback tools or batching strategies only when host-verified `SST` crosses explicit operational thresholds, omitting telemetry fields entirely when no verified probe exists. Procedure: [`verified-telemetry-tool-routing`](../skills/verified-telemetry-tool-routing/SKILL.md).

**Scope:** Agent Harness Awareness / Substrate State Telemetry (`SST`) across 1,800 tool-routing episodes under quota, latency, and permission perturbations across 5 LLMs (arXiv:2611.05391).

**Evidence**: In `arXiv:2611.05391`, injecting host-verified `SST` into the harness raised operational tool-routing accuracy under degraded substrate conditions from 51.4% (static schema baseline) to 88.7% and cut wasted failed tool invocations by 73.6%. Conversely, injecting neutral placeholder telemetry when substrate probes were unavailable dropped benign primary-tool utilization by 19.2 pp compared to omitting the unverified fields.

> Source: Agent Harness Awareness: Turning Verified Telemetry into Operational Control for Tool-Using Agents (arXiv:2611.05391)

### DO: Partition multi-framework UI codegen tuning into compatibility-ordered phases and gate shared LoRA updates using offline pre-gradient similarity and JSD heterogeneity

Jointly fine-tuning a shared MLLM across multiple frontend frameworks causes cross-framework syntax contamination and compilation failures, while uniform gradient scaling ($a_m = 0.5$) degrades performance below ungated training. Instead, apply moderate code normalization (stripping comments, whitespace, and local variable identifiers while preserving framework syntax tokens) to compute unigram+bigram Jensen–Shannon divergence $\Delta_{i,j}$, and measure offline shared-adapter pre-gradients over $K = 100$ batches (+2% overhead vs +23% for online gradient tracking) to compute cosine compatibility $S(\mathcal{D}_i, \mathcal{D}_j)$. Partition frameworks into compatibility-ordered phases—training high-synergy component frameworks first (`Phase 1: {React, Vue}`, $S = 0.79, \Delta = 0.18$) and heterogeneous frameworks second (`Phase 2: {Vanilla, Angular}`, $S = 0.31, \Delta = 0.73$)—and scale shared LoRA adapter updates by $a_m = \mathrm{clip}(\frac{1}{2}\hat{S}_m + \frac{1}{2}(1 - \hat{\Delta}_m), 0, 1)$, which sets $a_{\text{Angular}} = 0.00$ so high-divergence frameworks rely exclusively on their dedicated top-layer adapters. Procedure: [`two-phase-framework-ui-codegen`](../skills/two-phase-framework-ui-codegen/SKILL.md).

**Scope:** Multi-task / multi-framework parameter-efficient fine-tuning (LoRA) of multimodal LLMs (`Qwen2.5-VL-7B-Instruct`) across 13,224 DesignBench + WebCode2M samples (10,862 train / 1,206 val / 1,156 test across Vanilla HTML/CSS, React, Vue, and Angular) plus 484 Design2Code pages (arXiv:2611.01692).

**Evidence**: On 13,224 DesignBench + WebCode2M samples (`arXiv:2611.01692`), two-phase relationship-gated tuning achieved 0.7950 average CLIP and 0.9007 Compilation Success Rate (Angular: 0.7489 CLIP / 0.8135 CSR), outperforming Claude-3.7 (0.7470 CLIP / 0.8044 CSR; Angular 0.6029 CSR), ScreenCoder (0.7300 / 0.8735), joint ungated tuning (0.7468 / 0.8479), ungated phase-wise tuning (0.7741 / 0.8712), and uniform gating $a_m = 0.5$ (0.7698 / 0.8681). Stripping framework syntax during normalization ("strong normalization") dropped CLIP to 0.7769 and CSR to 0.8694.

> Source: Phase-wise MLLM Tuning for Multi-framework WebUI Code Generation (arXiv:2611.01692)

### DO: Route MCP code representations by task type rather than defaulting to a unified hybrid index

Match the exposed code representation to the structural demands of the software engineering task: (1) expose a **multi-view Hybrid index** (combining AST spans, call graphs, imports, and docstrings) for pure **fault localization**, and use **AST or Callgraph** tools during **program repair** primarily to displace full-file `Read` calls and reduce token/latency overhead; (2) route **security vulnerability patching** to a dedicated **Callgraph** server (`get_callers`, `get_callees`, `trace_backwards`, `impact_analysis`) rather than a merged Hybrid server; and (3) route **bug-reproducing test generation** to **Docs** or **Hybrid** views while withholding standalone Callgraph tools.

**Scope:** Coding agents (`Claude Code` with `claude-haiku-4-5`) equipped with 6 MCP code-representation configurations (`Baseline`, `AST`, `Callgraph`, `Deps`, `Docs`, `Hybrid`) across `LinuxFLBench` ($N=152$), `SWE-bench Pro` ($N=253$), `SWT-bench` ($N=161$), and `SecBench` ($N=166$) (arXiv:2611.07286).

**Evidence**: Across the controlled $6 \times 4$ evaluation (`arXiv:2611.07286`), no single representation dominated all tasks:
1. On **LinuxFLBench** ($N=152$, fault localization), **Hybrid** raised top-10 file recall (`fR@10`) from `0.717` (built-in Baseline) to `0.829` (`+11.2` pp, `17` wins / `0` losses) while cutting average tokens by **39%** (`1,008,163` to `610,910`).
2. On **SWE-bench Pro** ($N=253$, program repair), **AST** and **Hybrid** reached `50.6%` resolution vs `49.0%` Baseline while **Callgraph** and **AST** reduced total token consumption by **26%** (`3,116,193` to `2,310,653`) and **21%** (`2,450,752`) and cut wall-clock runtime from `268.8 s` to `193.7 s–209.1 s` via `Read` displacement (`12.7` built-in reads down to `8.4–8.7`).
3. On **SWT-bench** ($N=161$, test generation), **Hybrid** (`47.8%`, `+3.1` pp) and **Docs** (`47.2%`, `+2.5` pp) improved fault reproduction over Baseline (`44.7%`), whereas **Callgraph** degraded performance by **6.8 pp** (`37.9%`, `18` wins / `29` losses).
4. On **SecBench** ($N=166$, security patching), **Callgraph** raised vulnerability resolution from `28.9%` to **`34.3%`** (`+5.4` pp, `18` wins / `9` losses) and cut tokens by **10%** (`683,774` to `614,360`), whereas **Hybrid** achieved only `29.5%` (`+0.6` pp): on `14` of the `18` instances that Callgraph solved and Hybrid missed, Hybrid edited the exact same target file, showing that merging all views diluted execution-flow salience during patch synthesis (see [rethinking-code-representations-agentic-swe](../research-briefs/rethinking-code-representations-agentic-swe.md)).

> Source: How Should Agents See Code? Rethinking Code Representations for Agentic Software Engineering (arXiv:2611.07286)

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
- [`capability-matched-skill-adaptation`](../skills/capability-matched-skill-adaptation/SKILL.md) — Adapting skill text across executor capability bottlenecks
- [`decoupled-interface-action-repair`](../skills/decoupled-interface-action-repair/SKILL.md) — Decoupled semantic commitment and interface-specific realization repair
- [`composite-skill-vulnerability-scanner`](../skills/composite-skill-vulnerability-scanner/SKILL.md) — Dependency-graph static/LLM auditing and sandbox-verified repair for local and cross-skill composite vulnerabilities
- [`contrastive-meta-skill-harness-evolution`](../skills/contrastive-meta-skill-harness-evolution/SKILL.md) — Offline contrastive meta-skill precomputation paired with bounded online harness evolution (`Meta^2`)
- [`counterfactual-tool-dependency-induction`](../skills/counterfactual-tool-dependency-induction/SKILL.md) — Counterfactual sandbox verification of tool dependency graphs with 1-hop top-2 retrieval (`LIBRA`)
- [`verified-telemetry-tool-routing`](../skills/verified-telemetry-tool-routing/SKILL.md) — Host-verified Substrate State Telemetry (`SST`) projection and operational tool routing
- [`mcp-hallucination-boundary-guards`](../skills/mcp-hallucination-boundary-guards/SKILL.md) — Pre-execution feasibility gates, confusion-tool isolation, and transactional state ledgers for MCP agents
- [`two-phase-framework-ui-codegen`](../skills/two-phase-framework-ui-codegen/SKILL.md) — Compatibility-ordered two-phase LoRA tuning and relationship-gated adapters for multi-framework UI codegen

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
- Evolving to Match Capabilities (Skill Adaptation): arXiv:2610.33024
- Skill$^{\infty}$: arXiv:2610.35434
- RSIV-Harness: arXiv:2610.35316
- Matched Capabilities, Different Behaviors (MICA & DART): arXiv:2610.34298
- MCP vs CLI for AI Agents: arXiv:2610.30157
- Tool-Calling LLM Agents Under Realistic MCP Faults (MCP-Injector): arXiv:2610.32555
- Scan Before You Install (Composite Skill Vulnerability Scanner): arXiv:2610.37901
- Poisoned Skills (Markdown Skill Jailbreaks): arXiv:2610.37738
- SkillMem (Compact External Skill Memory for Latent MAS): arXiv:2610.37935
- LatentTriad (Pre-Action Latent Risk Representations): arXiv:2611.05088
- Meta$^2$ (Precomputing Reusable Knowledge for Online Harness Evolution): arXiv:2611.05139
- LIBRA (Programmatic Induction of Executable Tool Libraries): arXiv:2611.05445
- Agent Harness Awareness (Verified Telemetry into Operational Control): arXiv:2611.05391
- MCPHallu (Reasoning, Execution, and Memory Hallucinations in MCP Agents): arXiv:2611.07689
- MCP-Eco (Linked Dataset of MCP Servers, Consumers & Activity): arXiv:2611.06897
- Phase-wise MLLM Tuning for Multi-framework WebUI Code Generation: arXiv:2611.01692
- Rethinking Code Representations for Agentic Software Engineering: arXiv:2611.07286

