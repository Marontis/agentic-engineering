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

## Related Skills

For implementation details on the procedures behind these rules:
- [`skill-design-methodology`](skills/skill-design-methodology/SKILL.md) — Full skill authoring methodology
- [`capability-aware-skill-selection`](skills/capability-aware-skill-selection/SKILL.md) — BPS algorithm and capability model
- [`knowledge-compounding-loop`](skills/knowledge-compounding-loop/SKILL.md) — Persistent knowledge accumulation
- [`iterative-instruction-refinement`](skills/iterative-instruction-refinement/SKILL.md) — NPO-style revision loop
- [`rag-evidence-triage`](skills/rag-evidence-triage/SKILL.md) — Three-way evidence classification

## Sources

- Break It Down, Pass It On: arXiv:2608.20274
- Optimal Skill Selection: arXiv:2608.19993
- WikiSkill: arXiv:2608.27454
- Naive Prompt Optimization: arXiv:2608.27266
- ACE Lens: arXiv:2608.27260
- Knowing Before Answering: arXiv:2608.27661
