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
by 23pp.

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

> Source: Naive Prompt Optimization (arXiv:2608.27266)

### DO: Evolve skills with stronger models, deploy to weaker ones

Skills evolved by a stronger model can outperform skills a weaker model
evolved for itself. Skill discovery and skill execution are distinct
capabilities. Invest evolution compute in your strongest model; deploy the
resulting skills to cheaper models.

**Evidence**: Qwen-27B-evolved skills improve Qwen-9B by +26.2pp on
SpreadSheet, vs. +9.3pp from self-evolved skills. Transfer works across
model families.

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

When a retrieval system returns evidence, classify it as sufficient,
insufficient, or conflicting before generating.  Insufficient evidence
means "I don't have enough info" — retry retrieval or acknowledge the
gap.  Conflicting evidence means "my sources disagree" — surface the
contradiction.  Collapsing both into "don't answer" loses information
critical for downstream handling and trust.

**Evidence**: A lightweight linear probe on hidden activations from a
single middle layer achieves 0.91 accuracy for 3-way triage across 16
models, reducing false answer rates by 75% over prompt-based baselines.

> Source: Knowing Before Answering (arXiv:2608.27661)

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

---

## Hallucination Detection

### DON'T: Collapse "missing evidence" and "conflicting evidence" into a single refusal

When an agent encounters unsupported claims, distinguish between
*insufficient* evidence (not enough information) and *conflicting*
evidence (contradictory sources).  These require different downstream
actions: insufficient evidence should trigger additional retrieval,
while conflicting evidence should surface the contradiction explicitly.
The hallucination signal in LLM hidden states is a linearly detectable
mean shift — simple probes suffice for detection without collapsing
the distinction.

> Source: The Hallucination Signal Is a Mean Shift (arXiv:2608.28930)

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

> Source: Speculative Macro Commit for Faster Tool-Using Agents (arXiv:2609.03236)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`skill-design-methodology`](skills/skill-design-methodology/SKILL.md) — Full skill authoring methodology
- [`capability-aware-skill-selection`](skills/capability-aware-skill-selection/SKILL.md) — BPS algorithm and capability model
- [`knowledge-compounding-loop`](skills/knowledge-compounding-loop/SKILL.md) — Persistent knowledge accumulation
- [`iterative-instruction-refinement`](skills/iterative-instruction-refinement/SKILL.md) — NPO-style revision loop
- [`rag-evidence-triage`](skills/rag-evidence-triage/SKILL.md) — Three-way evidence classification
- [`skill-evolution-defense`](skills/skill-evolution-defense/SKILL.md) — Hardening skill evolution loops
- [`hallucination-mean-shift-probe`](skills/hallucination-mean-shift-probe/SKILL.md) — Linear probe hallucination detection
- [`prefix-preserving-context-assembly`](skills/prefix-preserving-context-assembly/SKILL.md) — Database-style context assembly
- [`persistent-agent-migration`](skills/persistent-agent-migration/SKILL.md) — Runtime-independent agent migration
- [`trajectory-aware-eval-pruning`](skills/trajectory-aware-eval-pruning/SKILL.md) — Trajectory-aware benchmark item selection
- [`procedural-family-skill-consolidation`](skills/procedural-family-skill-consolidation/SKILL.md) — Hierarchical global/local skill consolidation
- [`speculative-macro-commit`](skills/speculative-macro-commit/SKILL.md) — Pre-executing multi-step tool action skeletons

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
