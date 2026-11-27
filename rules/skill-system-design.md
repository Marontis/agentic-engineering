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

Tension with "DON'T: Equate in-domain SLM trace distillation or exact-reward RL gains with transferable search judgment without cross-schema minimality checks" (recursive-improvement.md): deploying explicit natural-language `SKILL.md` rules evolved/adapted by stronger models transfers decision criteria to weaker executors (`arXiv:2608.27454`, `arXiv:2610.33024`), whereas fine-tuning a `4B` student directly on exact-filtered frontier action traces (`Frontier-148`, `53.1%`) underperformed clean algorithmic traces (`Alg-148`, `84.4%` mean) in-domain and still failed to transfer cross-schema stopping judgment (`Alg-2000` `47.9%` OOD vs. `100%` [`47/47`] on `Claude Haiku 4.5` with a `1`-sentence instruction; `arXiv:2611.21529`).

Tension with "DO: Pair sub-second System-1 action scorers with past-present-future harness modules, consecutive-loss quarantine, and audited asynchronous System-2 synthesis volume" (recursive-improvement.md): unconditional offline skill distillation benefits from stronger writer models (`arXiv:2608.27454`, `arXiv:2610.33024`), whereas in event-triggered System-1/System-2 harness development (`JevRSI`, `arXiv:2611.22432`), replacing `Qwen3.8-27B` or `DeepSeek-V4.1-Flash` with stronger standalone `GPT-6.1 Sol` cut triggered `BabyAI` development episodes `5–7x` (`10` vs. `49–67`) and lowered System-1 `SR@1` by `-13.33` to `-14.67 pp` ID (`50.66%` vs. `64.00%` / `65.33%`)—audit trigger volume whenever swapping in a stronger developer model.

Tension with "DO: Co-evolve shared-weight Improver and Solver roles via case-balanced counterfactual harness advantage rather than freezing either role" (recursive-improvement.md): when parameter-efficient RL is available (`MedicalRSI`, `arXiv:2611.26806`), co-training a single `9B` shared-weight adapter across both `Improver` and `Solver` roles beat a frozen `GPT-6.1-Sol` skill proposer by `+33.5 pp` (`85.1%` vs. `51.6%` on `MedAgentBench`) and transferred `9B`-authored workflow harnesses *upward* to lift `7` frozen `26B–284B`/frontier solvers by `+16.8` to `+32.3` points (`Claude Sonnet 5` `61% -> 85%`).

> Source: arXiv:2608.27454; Evolving to Match Capabilities: Improving Harness Self-Evolution via Skill Adaptation (arXiv:2610.33024)

### DO: Ground unverified skill revisions in AST-indexed script contracts aligned with trace gaps while freezing bundled code

When evolving a tool-bearing skill package `S = (P, M)` (`P` = helper scripts/CLI wrappers, `M` = `SKILL.md` guidance) on unlabeled tasks without task-specific test verifiers, neither ungrounded trace self-refinement nor raw source-code dumping works reliably: trace-only revision hallucinates unsupported flags or overwrites working instructions, while pasting raw script files into the reviser degrades accuracy below structured alignment by `-18.89 pp`. Structure verifier-free skill revision around four deterministic invariants:
1. **Freeze `P` read-only and extract line-verified operational records (`K`)**: Index `P` via Python/source AST + line numbers (`SHA-256` verified) to extract `<= 12` workflow-level operational contracts `k = (cap, cond, steps, limits, src)`, rejecting any record whose inclusive line span does not match `P`.
2. **Align `K` against `M` on the execution trace (`A` -> `F`)**: Classify each task-relevant contract (`COVERED`, `ADD_OPERATION`, `ADD_FALLBACK`, `CORRECT_OPERATION`, `UNKNOWN`) against trace `\tau` and emit `<= 12` quote-anchored `MISSING_GUIDANCE` or `CONFLICTING_GUIDANCE` items citing exact `request_quotes` and `skill_quotes`.
3. **Apply bounded substring patches (`<= 4` non-overlapping edits) or `KEEP`**: Restrict `M -> M'` to local exact-substring replacements (`<= 8,000` chars each, preserving non-blank baseline structure) or explicit `KEEP` when `F` is empty, and pass any persistent skill update through "DO: Pass every self-modification through one acceptance gate" (`recursive-improvement.md`). Procedure: [`tool-implementation-grounded-skill-revision`](../skills/tool-implementation-grounded-skill-revision/SKILL.md).

**Scope:** `VISE` evaluation (`gpt-5.5`, `temp = 0`) across `SkillsBench` (`81–82/84` complete-score tasks + `233` `P1`/`P2`/`P3` perturbations) and `SkillLearnBench` (`96–97/99` tasks; `177–179/183` total) over `4` evolution methods (`Self-Refine`, `TraceEvo`, `SkillLearn`, `SkillRevise`) and `60`-task component ablations (arXiv:2611.32480). When a skill has no inspectable local implementation (remote closed APIs) or when rich task-specific unit-test reports exist on scriptless software tasks (`SkillLearnBench` `Software Engineering`, where `Report` gained `+5.9%` to `+21.6%` vs. `VISE` `-3.9%` to `+3.9%`), pair with external test reports or Turn-0 checklist gating (`GUARD`, `arXiv:2611.23476`).

**Evidence**:
- **Gains over no-verifier and task-verifier baselines (`arXiv:2611.32480`, `Tables 1–2, 4–7`)**: Across all `4` evolution methods (`Self-Refine` `49.91%`, `TraceEvo` `52.51%`, `SkillLearn` `51.04%`, `SkillRevise` `51.40%` `P@1`), `VISE` lifted `P@1` by **`+9.14` to `+13.35` pp**, `P@3` by **`+4.59` to `+7.93` pp**, and strict `3/3` consistency (`Hit^3`) by **`+12.36` to `+18.29` pp** over `No-verifier` (where `Binary` verifier feedback actually hurt `Self-Refine` `P@1` `39.16% -> 37.34%`, and `CoEvoSkills` dropped mean reward `49.44 -> 36.60`), beat the strongest task-specific verifier (`Binary`/`Report`/`Diagnostic`) by **`+0.76` to `+9.16` pp `P@1`** and **`+3.62` to `+16.10` pp `Hit^3`** (`67.0%` vs. `40.4%` `3/3` consistency on `SkillLearn` at tied `61.58%` `P@3`), and raised transfer across `233` `SkillsBench` variants from `46.35%–49.36%` to **`61.37%–66.52%`**.
- **Stage-by-stage `60`-task ablation (`Tables 3, 9–10`)**: Relative to `Full VISE` (**`57.78%` `P@1` / `76.67%` `P@3` / `30.00%` `Hit^3`**, `41.62k–44.79k` input tokens, `57.97–82.27 s`), pasting raw scripts (`Raw-Source Revision`) collapsed `P@1 / P@3 / Hit^3` by **`-18.89 / -13.33 / -16.67` pp**, omitting quote-anchored feedback (`w/o Structured Feedback`) dropped **`-13.89 / -16.67 / -5.00` pp**, omitting trace alignment (`w/o Workflow Alignment`) dropped **`-10.56 / -5.00 / -1.67` pp**, and unbounded rewrites (`w/o Workflow Revision`) dropped **`-8.33 / 0.00 / -5.00` pp** (see [`tool-implementation-grounded-skill-revision`](../skills/tool-implementation-grounded-skill-revision/SKILL.md)).

Tension with "DON'T: Expose benchmark verifier code or unstated rubric predicates to the skill-library learner" (recursive-improvement.md): `Criteria Exposure` (`arXiv:2611.08318`) forbids showing hidden *benchmark evaluation code or unstated grading predicates* to the skill learner (`-25.9 pp` collapse under instruction-faithful re-judging), whereas `VISE` (`arXiv:2611.32480`) inspects *the skill package's own deployment-resident helper scripts `P`* while keeping benchmark verifiers completely unseen (`+15.0` to `+17.2 pp` transfer lift across `233` perturbed tasks).

Tension with "DON'T: Promote bundled text-space skill edits on aggregate clean validation accuracy alone" (recursive-improvement.md): `VISE` (`arXiv:2611.32480`) permits up to `4` non-overlapping substring edits grounded in `SHA-256`-verified script spans under benign unlabeled traces, whereas when task requests or reference traces may be adversarially poisoned (`SkillOpt`, `arXiv:2611.09348`), multi-edit patches (`2–4` edits) must also pass leave-one-edit-out (`LOEO`) marginal validation and literal-abstraction filtering so a trigger-bound clause cannot ride on a clean operational fix.

Tension with "DO: Prioritize paired directional regret and filter continual playbook revisions with sandbox-anchored checklists and Soft-HURT scope guards when answer keys are absent" (recursive-improvement.md): use `VISE` (`arXiv:2611.32480`) when local tool/script source `P` is inspectable, and combine or fall back to `GUARD` (`arXiv:2611.23476`) `Turn-0` checklists + `Soft-HURT` when tools are opaque remote endpoints or on scriptless general software tasks.

See also "DON'T: Rely on dense semantic embeddings alone for retrieving code or executable skills without execution verification" (this file) and "DO: Pass every self-modification through one acceptance gate" (recursive-improvement.md).

> Source: VISE: Verifier-Independent Skill Self-Evolution with Feedback from Tool Implementations (arXiv:2611.32480)

### DO: Anchor sparse-feedback memory distillation on evaluator verdicts and pre-inject generalized API names while serving pitfalls on demand

When distilling reusable `L1` patterns/pitfalls and `L2` skills from multi-turn coding sandboxes where the external harness returns only a sparse binary pass/fail verdict, naive write-side reflection contaminates memory with false-verified recipes and already-fixed tracebacks, while naive Turn-0 retrieval leaks concrete call sequences and distracts the agent with irrelevant pitfall warnings. Enforce asymmetric write-side and read-side guards:
1. **Write-side verdict anchoring & contradiction separation**: Override agent self-reported success with the external pass/fail verdict (`50%` of failed traces self-report success after weak self-tests), and split `FAIL` traces into a **terminal-error path** (unresolved final exception) vs. a **silent-contradiction path** (self-test passed + hidden eval failed, stripping intermediate solved tracebacks so resolved syntax errors are not stored as pitfalls).
2. **Read-side docstring generalization, names-only upfront hints, and on-demand pitfalls**: Rewrite problem docstrings into instance-agnostic functional intents before indexing, pre-inject retrieved `solution_pattern` entries at Turn 0 as **canonical API names only** (stripping call order and parameter literals), and withhold `pitfall` entries from Turn 0—serving them **on demand only when a matching runtime exception or zero-false-positive AST static-checker warning fires**, gating multi-round retention via held-out rollback and "DO: Pass every self-modification through one acceptance gate" (`recursive-improvement.md`). Procedure: [`anti-leakage-sparse-feedback-memory-distillation`](../skills/anti-leakage-sparse-feedback-memory-distillation/SKILL.md).

**Scope:** `ZhuLong-SE` self-evolution and harness evaluation across `5` models (`DeepSeek-V4-Pro-Preview`, `GLM-5.2`, `Kimi-K2.6`, `DeepSeek-V4-Flash-Preview`, `Doubao-Seed-2.0-pro`) on `EDA-Eval-PyAether` (`158` tasks total; challenge split `98` train / `20` val / `40` instance-disjoint test, `5` runs per eval split) over C++/SWIG EDA scripting bindings (arXiv:2611.26912). Note that single-batch runs cannot exercise cross-batch disconfirmation pruning (`>= 2` batches required), and `54.1%` of residual failures remain semantic `AssertionError`s that cause over-accumulation by Round 3 without held-out rollback.

**Evidence**:
- **Self-evolution beyond human-crafted skills & Round-3 rollback (`arXiv:2611.26912`, `Tables I–III`)**: Starting from `Bare` **`66.0% ± 7.2%`** on `40` unseen test tasks (`DeepSeek-V4-Pro-Preview`), `ZhuLong-SE` reached **`80.0% ± 3.1%` test (`+14.0 pp`) and `88.0% ± 2.7%` val** at Round 2 (`334` patterns, `20` skills)—beating the `4`-skill human-crafted expert baseline (`77.5% ± 5.3%`) by **`+2.5 pp`**—while its held-out rollback gate caught Round-3 over-accumulation (`386` patterns, `25` skills: val **`88.0% -> 80.0%`, `-8.0 pp`**, test `75.5% ± 6.7%`) and rolled back `52` entries; with self-evolution off, the AST static checker (`0/158` reference false flags, `+6.3 pp`), identifier-aware keyword+BM25 (`+1.3 pp`), and skills (`+3.8 pp`) lifted full-benchmark pass rates by **`+5.7` to `+16.4 pp`** across all `5` models (`92.4%` on `DeepSeek-V4-Pro-Preview`).
- **Write-side & read-side gate ablations (`Tables IV–V`)**: On `24` failed traces, disabling `Ground-Truth Anchoring` admitted falsely `verified` entries from **`12/24` (`50%`)** of failed traces (`37 -> 48` L1 entries), and disabling `Contradiction Path` injected **`+17` stale solved-error entries** (`37 -> 54`); on frozen Round-2 knowledge (`88.0% ± 2.7%` val), Turn-0 `Pitfall Pre-Injection` dropped **`-8.0 pp` (`80.0% ± 5.0%`)**, `Docstring Generalization Off` dropped **`-6.3 pp` (`81.7% ± 5.8%`)**, and `Full-Sequence Injection` dropped **`-4.7 pp` (`83.3% ± 5.8%`)** (see [`anti-leakage-sparse-feedback-memory-distillation`](../skills/anti-leakage-sparse-feedback-memory-distillation/SKILL.md)).

Tension with "DO: Gate step-level action verification on low-confidence steps and keep the verifier transparent to the policy" (recursive-improvement.md): subgoal-conditioned pitfall anticipation (`PAWM`, `arXiv:2610.29139`) improves interactive navigation when selective `<pass>` warnings are conditioned on the *live subgoal state*, whereas Turn-0 pre-injection of historical API `pitfall` memories matched only against a static task docstring (`ZhuLong-SE`, `arXiv:2611.26912`) drops validation pass rate by `-8.0 pp` (`88.0% -> 80.0%`) because task descriptions do not predict which API will be misused—serve API pitfalls strictly on demand upon runtime errors or static-checker triggers.

See also "DO: Distill operational know-how rather than high-level method descriptions" (this file) and "DO: Pass every self-modification through one acceptance gate" (recursive-improvement.md).

> Source: Self-Evolving Beyond Human-Crafted Experience for EDA Scripting (arXiv:2611.26912)

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

Tension with "Pair static skill checks with safety-constrained sandbox dry-runs and provenance-weighted evidence rather than alert-count thresholds" (skill-system-design.md), "Assume clean-fitted hidden-state probes outrank token-entropy uncertainty on system-override hijackings" (agent-sandbox-safety.md), and "Score collusion probes post-vote or omit decliner and instruction-stripping ablations" (agent-evaluation-quality.md): provenance-weighted sandbox dry-runs cut pre-admission scanner FPR from `0.67` to `0.08` (`F1 = 0.89`, `Recall = 0.85`, `arXiv:2611.10830`) and supervised exposure-contrast probes (`LatentTriad`) reach `99.6%` macro-AUC when the injected skill is in context, whereas `15%` of malicious skills still evade dry-runs, benign-only pre-action error probes collapse to `0.431` AUROC under `system-override` (`arXiv:2611.11172`), and prompt-trained collusion probes drop from `1.00` to `0.61` AUROC when secret briefs are stripped (`arXiv:2611.10620`) — so provenance attestation, rate-limited resubmissions, and runtime sandboxing remain mandatory.

Tension with "DO: Screen external A2A Agent Cards before orchestrator ingestion via schema gates, deterministic NLP rules, and an isolated read-only semantic judge" (adk-security-and-evaluation.md): pre-invocation Agent Card validation (`SecCARD`, `arXiv:2611.18887`) screens remote discovery metadata (`97.0%` perturbation recall at `1.7%` seed FPR with `GPT-5.5`) before an orchestrator reads it, but just like pre-admission skill scanning it cannot guarantee post-admission runtime honesty or prevent remote metadata `rug pulls`—pair discovery screening with content-digest pinning, per-hop A2A authorization envelopes, and runtime invocation sandboxing.

> Source: SkillDRE: Dual-Stage Red-Team Evolution of Agent Skills via Pre-Execution and Runtime Feedback (arXiv:2609.32400); Pretext: Defeating Malicious Skill Detection Frameworks for AI Agents (arXiv:2609.39607); Scan Before You Install: Detecting and Mitigating Local and Composite Vulnerabilities in Skills (arXiv:2610.37901); Poisoned Skills: Markdown Skill Files as a Persistent Jailbreak Vector (arXiv:2610.37738); LatentTriad: Pre-Action Latent Risk Representations for Stealth Skill Injection (arXiv:2611.05088)

### DO: Pair static skill checks with safety-constrained sandbox dry-runs and provenance-weighted evidence rather than alert-count thresholds

Do not gate third-party or agent-authored Markdown skill packages (`SKILL.md` + helper scripts) on static regex/YARA alert totals or static-only LLM review. Benign developer and administrative skills legitimately reference `curl`, shell pipelines, and API keys—producing higher mean static alert counts than malicious skills—while passing static hits alone to an LLM adjudicator collapses recall because stealth prose instructions trigger few high-severity signatures. Instead, retain static findings with file/line provenance (`Low`/`Medium`/`High` severity), execute the candidate skill inside an isolated **safety-constrained dry-run container** (`appuser`, `300 s` cap, capturing `strace`, `tcpdump`, and filesystem diffs while intentionally blocking and logging credential reads, exfiltration, persistence, security-control bypasses, and unverified remote script execution), weight behavioral indicators by source-to-trace provenance multipliers (`0.45` ungrounded narrative vs. `0.85` source-grounded blocked primitive vs. `1.00–1.15` executed/corroborated), and adjudicate via bounded threat-grounded retrieval (`<= 3` rounds) emitting line-cited `SARIF 2.1.0` reports. Procedure: [`hybrid-sandbox-skill-intent-audit`](../skills/hybrid-sandbox-skill-intent-audit/SKILL.md).

**Scope:** Pre-admission security auditing of `700` SHA-256 deduplicated AI agent skill bundles (`400` malicious, `300` benign across `MalSkillBench`, `Datadog AI-Skills`, and `VoltAgent Awesome Agent Skills`; `560` dev, `140` held-out test: `80` malicious, `60` benign) comparing `OSS-Detect-Backdoor`, `YARA`, `Cisco Skill Scanner` (`+/- Qwen3:8B`), and a 3-layer static + Docker sandbox (`Claude Opus 4.8`) + agentic (`Qwen3.5 122B` / `Qwen3:8B` + `Qdrant`) pipeline (arXiv:2611.10830).

**Evidence**: On the `140`-skill held-out test set (`arXiv:2611.10830`), raw static alert counts inverted—benign skills triggered higher mean alerts than malicious skills on both `OSS-Detect-Backdoor` (`11.70` vs. `6.34`, test `F1 = 0.42`, `Recall = 0.33`, `FPR = 0.28`) and `YARA` (`105.78` vs. `60.05`, test `F1 = 0.72`, `FPR = 0.82`), while `Cisco Skill Scanner` reached `FPR = 0.55` (`33/60` FP) and `Cisco Skill Scanner + LLM` reached `FPR = 0.67` (`40/60` FP, `Recall = 0.85`, `F1 = 0.72`). In within-system evidence ablations using the identical agentic backend, `Skill content only` achieved `F1 = 0.70` (`Recall = 0.68`, `21` FP, `319.95 s` median latency), adding `+ Static evidence` alone collapsed recall to `0.35` (`F1 = 0.50`, `52/80` FN), `+ Dynamic sandbox evidence` raised `F1` to `0.85` (`Recall = 0.79`, `5` FP, `89.45 s` median latency), and the `Full Hybrid Pipeline` (`Static + Dynamic + Agentic`) achieved `F1 = 0.89`, `Precision = 0.93`, `Recall = 0.85` (`68/80`), and `FPR = 0.08` (`5/60` FP—cutting false positives by `87.5%` relative to `Cisco Skill Scanner + LLM`, at `109.35 s` median agentic latency plus `<= 300 s` sandbox execution).

Tension with "Use a pre-execution skill scanner as the sole admission gate for third-party skills" (skill-system-design.md): resolved by defense-in-depth — this rule specifies how to replace high-FPR static/LLM pre-execution scanners with provenance-weighted sandbox dry-runs (`FPR 0.67 -> 0.08`, `F1 = 0.89`), while `12/80` (`15%`) malicious skills still evade pre-admission dry-runs (`Recall = 0.85`), so provenance attestation, rate-limited resubmission, and runtime per-task sandboxing remain mandatory.

Tension with "Poll global backend quiescence to close a session or screen status endpoints only on idle backends" (agent-sandbox-safety.md): isolated sandbox dry-runs on quiescent mock backends catch overt malicious skill behavior (`F1 = 0.89`, `FPR = 0.08`), but `OverServe` (`arXiv:2611.14808`) passes quiescent dry-runs cleanly (`1.25x–1.50x` calls, `<= 2` status polls, `0/22` static scanner alerts) while amplifying calls `10.30x–93.88x` when paired with an ordinary user completion clause under concurrent workspace `churn`; dry-run harnesses for status/verification tools must inject non-converging state-churn profiles.

> Source: The Devil Wears Markdown: Detecting Malicious Intent Hidden in AI Agent Skill Instructions through Hybrid Static, Dynamic, and Agentic Analysis (arXiv:2611.10830)

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

**Scope:** 23 dense embedding configurations across 939 code-retrieval tasks paired with single-line buggy distractors in ExecRetrieval (arXiv:2609.01865).

**Evidence**: Across 23 dense embedding configurations and 939 tasks in ExecRetrieval, top-10 retrieval reached 100% (`exec@10 = 1.00`), but top-1 retrieval plunged to `exec@1 = 0.331`. When rank-1 misses occurred, **91.5% to 99.4% were paired buggy distractors**, and canonical correct implementations scored below buggy distractors in **67% to 78% of queries**.

Tension with "DO: Isolate backend coordinates and asset IDs behind canonical state adapters and factor spatial-layout skills from semantic-content skills" (this file): declarative, asset-ID-free `Layout` and `Content` design skills (`SceneAgent`, `arXiv:2611.17821`) and entity-first `InfoNCE` asset proposals (`search_modules`) do not execute arbitrary code directly, yet injecting `50` vs `0` skills still dropped 3D `Spatial Plausibility` below parity (`46.2%`), confirming that even declarative semantic retrieval requires candidate metadata/thumbnail inspection and deterministic geometry checks (`check_bbox_collision`) before commit.

> Source: ExecRetrieval: Measuring the Functional-Correctness Gap in Code-Embedding Retrieval (arXiv:2609.01865)

### DO: Encapsulate inter-agent tool calls and skill invocations in standardized semantic envelopes

Avoid defining bespoke, ad-hoc JSON payloads for inter-agent communication and tool execution across heterogeneous runtimes. Use a standardized application-layer semantic envelope (such as the NLIP standard) that decouples semantic intent, conversation threading, and context referencing from the underlying transport protocol (HTTP, WebSocket, AMQP).

**Scope:** protocol standard (NLIP, Ecma; arXiv:2609.04135); interoperability design, no benchmark.

**Evidence**: Standardized semantic envelopes provide uniform auditability, context URI referencing, and least-privilege capability claims, bridging tool protocols (like MCP) and agent orchestration frameworks (like A2A) across enterprise boundaries without tight transport coupling.

See also: multi-agent-coordination.md — NLIP semantic envelope entry.

> Source: The Natural Language Interaction Protocol and Standard for AI Agents (arXiv:2609.04135)

### DO: Isolate backend coordinates and asset IDs behind canonical state adapters and factor spatial-layout skills from semantic-content skills

When building multi-agent constructive systems that must port across target execution engines, rendering runtimes, or asset catalogs without rewriting prompts or retraining, an interoperable output export format alone is insufficient because raw transcripts and distilled trajectories still entangle domain logic with native coordinates, APIs, and concrete asset identifiers. Enforce a three-part construction-portability boundary:
1. **Canonical world state + Orchestrator-only backend adapters**: Have fresh task-local `Builder` sessions read and mutate a shared canonical state (`SceneContext`: canonical axes, bounding boxes, occupancy index, and subtask provenance) through backend-neutral tools, passing only compact completion reports (`status`, `summary`, `residual_issues`, `actor_count_delta`) across subtasks rather than raw tool-call transcripts, while hiding low-level serialization (`export_json`) behind an `Orchestrator`-invoked adapter that translates coordinate/unit/rotation conventions and resolves backend-specific catalog bindings.
2. **Asset-ID-free `Layout` vs. `Content` skill factorization with `Thin Recipes`**: Gate trace extraction behind human quality review aided by automated geometry diagnostics (storing rejected traces separately as failure evidence), and factor approved traces into concrete-ID-free **Layout skills** (spatial topology, routes, circulation corridors), backend-neutral **Content skills** (semantic object roles, palettes, and missing-asset **substitution rules**), and scene-specific **Thin recipes**, enforcing schema validation, deduplication, and "DO: Pass every self-modification through one acceptance gate" ([`recursive-improvement.md`](recursive-improvement.md)) before library updates.
3. **Budget for multi-agent orchestration latency and pair text skills with deterministic geometry checks**: Fresh-session multi-agent handoffs and injected skill libraries primarily improve prompt alignment and content completeness at a substantial runtime cost while leaving fine-grained spatial plausibility near or slightly below parity—pair semantic skill retrieval with deterministic bounding-box/support validators rather than relying on text skills to enforce physical geometry.

**Scope:** `SceneAgent` (`Orchestrator` $\le 30$ rounds, `Planner` $\le 50$ rounds / $\le 40$ tool calls, fresh `Builder` $\le 40$ rounds; `DeepSeek-V4-Flash` `204.8k` context, plus `Gemini 3.5 Flash`, `Hy3`, and `Qwen3.6-35B-A3B`) evaluated on `GameSceneBench` (`69` prompts: `56` outdoor, `13` indoor $\times$ `3` runs $\times$ `5` views) against `5` adapted 3D scene-generation baselines (`AutoUE†`, `Holodeck`, `ImperativeScene`, `Reason-3D`, `SceneWeaver`) via `CLIP ViT-L/14`, blinded pairwise `gpt-4o-2024-11-20` VLM preferences, and `1,860` blinded human judgments (`51` qualified participants), plus a qualitative second-engine (`Engine B`) retargeting study; the skill-library ablation tests `0` vs `20` vs `50` frozen skills rather than isolating `Layout–Content` factorization against unfactored skill text (arXiv:2611.17821).

**Evidence**:
- **Baseline & cross-backend comparisons (`arXiv:2611.17821`, `Tables 2 & 8`, `§6.2–6.3`)**: Across `1,860` blinded human judgments on `Engine A`, `SceneAgent` achieved **`83.3%` overall tie-adjusted preference** (`76.9%` wins, `12.7%` ties, `10.3%` losses; **`78.2%–89.4%`** across all `5` baselines), **`72.5%–86.7%`** aggregate VLM preference across all `3` dimensions, and the highest `CLIPScore` (`0.216 ± 0.034` vs `0.185–0.214`) at `203.2 ± 97.8 s` per scene (`16.3–60.7 s` for non-reflective baselines, `226.4 s` for `SceneWeaver`). Retargeting all `69` prompts from `Engine A` (actor array, string IDs, cm, quaternions) to `Engine B` (`PCGGenerate` wrapper, numeric IDs, meters, fixed-precision strings) required replacing only the adapter, asset catalog, and native wrappers while keeping the protocol, `SceneContext`, core tools, and `50`-skill library unchanged (qualitative retargeting only). Replacing `DeepSeek-V4-Flash` with `Gemini 3.5 Flash` yielded near-parity VLM preference (`51.2%` vs `48.9%`, `0.220` vs `0.216` CLIP) while increasing runtime `1.84x` (`374.8 s` vs `203.2 s`).
- **Completeness/alignment gains vs. runtime and spatial-plausibility limits (`Tables 3–4`, `§6.4–6.5`)**: Expanding the frozen human-approved library (`0 -> 20 -> 50` skills) lifted `CLIPScore` (`0.211 -> 0.214 -> 0.216`) and beat `0` skills on VLM `Alignment` (**`59.7%`**) and `Completeness` (**`63.8%`**), but scored **`46.2%` on `Spatial Plausibility`** (below `50%` parity, `56.6%` 3-axis aggregate; `52.1%` over `20` skills) while raising runtime from `173.3 ± 56.4 s` to `203.2 ± 97.8 s`. Similarly, multi-agent `SceneAgent` beat a monolithic single-agent transcript baseline (`CLIPScore` `0.210 -> 0.216`, `57.0%` overall VLM preference) via **`62.4%` `Completeness`** (`vs 37.7%`) and **`57.5%` `Alignment`** (`vs 42.5%`), while `Spatial Plausibility` stayed near parity (**`51.0%` vs `49.0%`**) and wall-clock runtime rose **`5.17x` (`39.3 ± 24.2 s -> 203.2 ± 97.8 s`**; see [sceneagent-portable-game-scene-generation](../research-briefs/sceneagent-portable-game-scene-generation.md)).

Tension with "DON'T: Rely on dense semantic embeddings alone for retrieving code or executable skills without execution verification" (this file): `ExecRetrieval` (`arXiv:2609.01865`) shows dense vector retrieval fails at rank-1 (`exec@1 = 0.331`) when selecting *executable code* among buggy near-clones without an execution oracle, whereas `SceneAgent` (`arXiv:2611.17821`) retrieves declarative, asset-ID-free `Layout` and `Content` design guidance and uses entity-first `InfoNCE` hard-negative training (`search_modules`) only to propose top-$K$ candidate 3D assets—yet even declarative skill injection dropped `Spatial Plausibility` to `46.2%` vs `0` skills, so retrieved guidance and candidate assets must still pass metadata/thumbnail inspection and deterministic geometry checks (`check_bbox_collision`).

Tension with "DON'T: Default to a fixed multi-agent topology" (multi-agent-coordination.md): `3`-role sequential decomposition on self-contained coding benchmarks cost `3.22x` tokens and `3.24x` wall time for `-1.5 pp` accuracy (`arXiv:2610.37700`), whereas on multi-region `5–10`-subtask 3D world construction (`arXiv:2611.17821`), `Orchestrator -> Planner -> fresh Builder` canonical-state handoffs cost **`5.17x` wall-clock runtime (`203.2 s` vs `39.3 s`)** in exchange for higher `Completeness` (`62.4%` vs `37.7%`) and `Alignment` (`57.5%` vs `42.5%`) with flat `Plausibility` (`51.0%`)—reserve multi-session `Builder` decomposition for multi-region constructive workflows where single-transcript context drops required subsystems and latency budgets permit. See also "DO: Decouple continuity-bearing substrate from execution substrate" (this file), "DO: Consolidate skills into procedural families with frozen global priors and locally regenerated instance details" (this file), "DO: Decouple semantic action commitment from interface-specific tool realization and repair realization locally" (this file), and "DO: Decouple editable diagram generation into Semantic-Style-Layout specs and use bottom-up geometric text sizing before top-down coordinate layout" (agent-human-interaction.md).

> Source: SceneAgent: A Multi-Agent Framework for Portable Game Scene Generation (arXiv:2611.17821)

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
ALFWorld, and BabyAI (arXiv:2611.05139); `60`-issue `SWE-bench Lite` ablation (`sympy/sympy` Dev `N=12`, Val `N=8`, ID `N=20`; `django/django` cross-repo OOD `N=20`; `142`-line seed $h_0$ across `context_mgr.py`, `control.py`, `action_aci.py`, `verify.py` with $B_{\mathrm{tok}} = 110.0\text{k}$) on frozen `Gemini 3.8 Flash` plus zero-shot transfer to `Gemini 4 Argon` (arXiv:2611.22299).

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
In `arXiv:2611.22299` (`Table IV`), single-module token-budgeted evolution (`1` module/step, $B_{\mathrm{tok}} = 110.0\text{k}$) lifted `Gemini 3.8 Flash` combined ID+OOD resolve rate `8×` from `5.0%` (`2/40`, `114.8k` avg tok/task, `15.0%` unverified OOD exits) to **`40.0%` (`16/40`: `40.0%` ID, `40.0%` OOD)** at **`46.7k` avg tok/task** (`116.8k` tok/solved, **`0.0%` unverified OOD exits**, `< 100`-query evolution payback) and transferred zero-shot (`0` re-evolution rollouts) to `Gemini 4 Argon` at **`37.5%` (`15/40`) and `64.8k` tok/task**—outperforming `Unconstrained Full-Harness Rewrite` on transfer (`30.0%` [`12/40`] at `284.7k` tok/task, after unconstrained rewrite raised turn limits `12 -> 28` and inflated `Flash` cost `~10×` to **`451.6k` avg tok/task** with a `>2.8M`-token rollout, whereas Stage 3 rejected `control.py`'s `12 -> 18` cap increase), while `Prompt-Only Reflection` (`RULES.md` text only) fell to `2.5%` (`1/40`) and **doubled unverified OOD exits from `15.0%` to `30.0%`** despite an explicit opening rule forbidding untested `finish` calls (see [self-improving-agent-harnesses-framework](../research-briefs/self-improving-agent-harnesses-framework.md)).

Tension with "DO: Make the improvement mechanism part of the agent's
editable source" (recursive-improvement.md): resolved by scope — the
improvement logic may be editable, but only inside a fixed, declared
editable set with bounded per-round change; evaluator, graders, security
tests and permissions stay outside.

> Source: RobustSGPO (arXiv:2609.09646); RRSI (arXiv:2609.24972);
> A Theory of Reliable Self-Evolution for Agent Harnesses (arXiv:2609.08175);
> Skill$^{\infty}$: Recursive Self-Improvement for Agent Skill Optimization (arXiv:2610.35434);
> RSIV-Harness (arXiv:2610.35316); Meta$^2$: Precomputing Reusable Knowledge for Online Harness Evolution in Long-Horizon Agents (arXiv:2611.05139);
> Harnesses That Improve Themselves: A Unifying Framework for Self-Improving Agent Harnesses (arXiv:2611.22299)

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

**Evidence (Governance & Alignment Boundaries)**: Even if recursive takeoff crosses human-supervised ceilings across three capability regimes — supercharged digital AI, physical-world robotics/lab agency, and conceptual alienation where human-in-the-loop oversight fails semantically — delegating safety to a fully autonomous alignment researcher with no subsequent human oversight reduces inductively to solving full alignment at the final human-supervised handoff (`arXiv:2611.10261`). Moreover, in a symmetric two-actor RSI initiation game with private benefit `1` and catastrophic risk $r$, replacing additive harm (`2r` joint loss, which yields a Prisoner's Dilemma at $r = 3/4$ and dominant restraint at $r = 3/2$) with non-additive existential harm (`r` joint loss) transforms $r = 3/2$ into a Stag Hunt ("Flammable Duplex House", payoffs `(0, 0)` vs `(-1/2, -1/2)`), where mutual restraint `(no RSI, no RSI)` is already a pure-strategy Nash equilibrium threatened primarily by gradual capability habituation rather than unilateral defection incentives (see [is-recursive-self-improvement-safe](../research-briefs/is-recursive-self-improvement-safe.md)).

See also "DO: Constrain recursive model-authored weight-edit programs with low-rank Frobenius bounds, fresh-screen prefiltering, and binary acceptance feedback" (recursive-improvement.md): in `SelfWrite` (`arXiv:2611.29513`), recursive gradient-free weight-edit programming on `Qwen3.8-27B` monotonically improved `DAPO-Math` gate `avg@4` for `4` generations (`+1.20, +0.50, +0.10, +0.70`) before stalling at `0` accepted candidates in Generation `5`.

> Source: The Last AI Built by Humans (arXiv:2609.11873); Evolutionary Safety of Recursive Self-Improving AI (arXiv:2609.31186); RRSI (arXiv:2609.24972); A Theory of Reliable Self-Evolution for Agent Harnesses (arXiv:2609.08175); Is Recursive Self-Improvement Safe? (arXiv:2611.10261)

---

## Context Decoupling & Reasoning Anti-Looping

### DO: Decouple agent context into file ledgers to prevent runaway reasoning loops

When deploying mid-sized dense models (14B–35B) or long-horizon reasoning agents on complex problems, unconstrained single-call generation often degrades into degenerative self-verification loops (e.g., repeating edge-case interrogations thousands of times until hitting token limits). Decouple agent state into a shared filesystem ledger (`plan.md`, `notes.md`, `tasks.json`, `solution.py`), invoke subagents in fresh zero-shot contexts with bounded payloads, and actively prune working notes (<800 words).

**Evidence**: On the 100 latest Hard LiveCodeBench problems, single-call Qwen3.8-27B suffered 35 empty-output failures from runaway deliberation loops (e.g. repeating a verification check 7,743 times). A zero-shot ledger scaffold rescued 25 of these (+5.0 points) and lifted overall Pass@1 from 63.0% to 86.4% (+23.4 points), matching Claude Fable 5 (87.4%). The comparison is asymmetric: Fable 5 was run single-call with no tools and no code execution, while the scaffolded Qwen got up to 10 manager-to-worker rounds with subprocess test execution.

**Exception — sparse MoE / low active parameters**: the same paper found the scaffold hurt Qwen3.6-35B-A3B (3B active): −1.2 points at 16k and −9.0 points at 128k with reasoning off. Benchmark the scaffold per model family before deploying it.

**Scope:** LiveCodeBench Hard (100 latest problems), 128k cap, paper v1 numbers (v2 of 21 Sep 2026 revised them).

See also: recursive-improvement.md — "DON'T: Assume multi-agent scaffolding is universally monotonic across model architectures" (same paper).

Tension with "DON'T: Trigger online detour cues on single errors or two-step repeats, replace concise reminders with auxiliary-LLM spotters, or equate detour cessation with bug-fix resolution" (this file): zero-shot file-ledger context decoupling rescues single-call empty-output deliberation loops (`+23.4` pts Pass@1 on `LiveCodeBench Hard`, `arXiv:2608.26480`), whereas injecting online natural-language detour cues into an ongoing `SWE-agent` transcript (`ToolPulse`, `arXiv:2611.19275`) yields `61.6%–90.9%` local detour cessation without raising aggregate repository bug-fix pass rates (`101/270` baseline vs `99–105/270` assisted).

> Source: Zero-Shot Self-Orchestration with Ledger-Based Control (arXiv:2608.26480)

### DON'T: Trigger online detour cues on single errors or two-step repeats, replace concise reminders with auxiliary-LLM spotters, or equate detour cessation with bug-fix resolution

When adding online behavioral monitoring to tool-using coding agents (`ToolPulse`), avoid over-eager triggers and heavy runtime advice generators, and never treat local behavioral adjustment as proof of higher task pass rates:
1. **Delay repetition and error triggers to preserve autonomous self-recovery**: Wait for **`>= 3` consecutive identical `(tool, args)` calls** (`Calling Repetition`) rather than `2`, gate error reminders on **repeated identical error signatures within an `8`-step window with zero intervening state-changing edits/installs** (`Failure Inertia`) rather than firing on first-time or diagnostic errors, and keep broad-retrieval (`Wandering Flood`) auditing offline so task-justified repository exploration is not interrupted.
2. **Default to concise factual reminders over auxiliary-LLM spotters**: Use brief `Reminder-Only` notices for open-ended strategic detours (`Strategic Fixation`, `Functional Cycle`), add fixed prescriptive guidance **only** for concrete invariant preconditions (such as inspecting a file in `V_{t-1}` before editing it in `Blind Command`), and avoid per-trigger auxiliary-LLM advice (`Tactile Spotting`), which lowers aggregate substantive correction while inducing severe consecutive re-trigger storms.
3. **Audit paired `(Newly Passed / Regressed)` task outcomes alongside process cessation**: Because breaking a tool-use detour does not supply missing root-cause defect diagnosis—and trajectory perturbations regress previously solved instances—evaluate runtime interventions on paired net task resolution and protected-case regressions, not local detour cessation alone.

**Scope:** `ToolPulse` pre/post-execution online monitoring middleware integrated into `SWE-agent` (`T = 0`), evaluated across a `240`-run Python pilot (`30` tasks $\times$ `2` models $\times$ `4` sequence detectors) and **`1,350` main trajectories** (`90` complexity-stratified `OmniCode` bug-fix tasks across Python, C++, and Java $\times$ `3` backbones: `DeepSeek-V4-Pro`, `Qwen3-Coder-Plus`, `Qwen3.6-27B` $\times$ `5` conditions: `Baseline` + `Reminder-Only`, `Guided Verbal`, `Visual JSON`, and `Qwen3.7-Flash` `Tactile Spotting`), with `Kimi-K3` step-window detour judging (`87%–98%` `100`-sample expert agreement; `arXiv:2611.19275`).

**Evidence**:
- **Premature triggers & auxiliary-LLM spotter backfire (`arXiv:2611.19275`, `Tables 4, 6–9`, `§3.2 & §5.3–5.4`)**: In the pilot, `DeepSeek-V4-Pro` escaped `2`-step duplicate calls autonomously **`100.00%` (`3/3`, `0%` recurrence)** vs `58.33%–88.89%` under `2`-step prompts, generic `Failed Action` prompts derailed normal dependency fixes (`missing-pytest`), and only `799/3,191` (`25.0%`) `>95th`-percentile Retrieve steps across `400/1,350` (`29.6%`) runs were genuine `Wandering Floods`. Across `1,080` main assisted runs, **`Reminder-Only` achieved the highest pooled substantive-response rate (`67.8%`, `158/233`; `69.8%` on `Strategic Fixation`)**, outperforming `Guided Verbal` (`59.2%` overall, though `Guided` led concrete `Blind Command` at **`78.6%` [`11/14`] vs `56.3%` [`9/16`]**), `Visual JSON` (`52.6%`), and `Qwen3.7-Flash` `Tactile Spotting` (`56.1%`, `27.5%` on `Blind Command`)—which inflated `Strategic Fixation` trigger density **`4.74x` (`6.40` vs `1.35` per `100` actions)** via consecutive re-trigger runs (`107/144` affected trajectories, `974/1,124` [`86.7%`] triggers, max run length `30`, vs `0` runs across all three static cueing arms).
- **Process adjustment without aggregate repair gain (`Tables 6 & 10`, `§5.5`)**: Despite **`90.9%` (`100/110`)**, **`65.5%` (`19/29`)**, and **`61.6%` (`699/1,134`)** substantive detour responses on `Failure Inertia`, `Functional Cycle`, and `Strategic Fixation`, total passing bug-fix patches across all `270` paired model–task instances stayed nearly unchanged from **`101` (`Baseline`, `37.4%`)** at **`105` (`Reminder-Only`), `104` (`Guided`), `99` (`Visual`), and `103` (`Tactile Spotting`)** (`<= ±2` in all `36` language-model cells, with gains offset by regressions such as `4` newly passed / `3` regressed on `Qwen3.6-27B` Java, while most token-change 95% CIs included zero; see [toolpulse-runtime-cueing-vs-task-outcomes](../research-briefs/toolpulse-runtime-cueing-vs-task-outcomes.md)).

Tension with "DO: Decouple agent context into file ledgers to prevent runaway reasoning loops" (this file) and "DO: Enforce fast-fail circuit breakers, output schema validation, and grounded-fulfillment gates for MCP tool faults" (this file): zero-shot file-ledger decoupling rescues single-call empty-output deliberation loops (`+23.4` pts on `LiveCodeBench Hard`, `arXiv:2608.26480`) and permanent `MCP` server faults (`91.3%` permanent in `arXiv:2610.32555`) or `Unreachable Goals` (`0.0%` pass at `>= 4` calls in `arXiv:2611.07689`) require hard `<= 2`-retry fast-fail circuit breakers, whereas inside mutable repository debugging (`SWE-agent`, `arXiv:2611.19275`), single command errors and `2`-step repeats reflect normal test reproduction or autonomous self-recovery (`100%` [`3/3`] baseline `2`-step escape), and even `61.6%–90.9%` online detour cessation leaves aggregate repository bug-fix pass rates flat (`101/270` vs `99–105/270`).

Tension with "DO: Gate step-level action verification on low-confidence steps and keep the verifier transparent to the policy" (recursive-improvement.md): trained low-confidence step verifiers (`SWE-VERIFIER`, `<4%` steps, `arXiv:2610.30284`) and subgoal pitfall predictors (`PAWM`, `arXiv:2610.29139`) lift end-to-end resolution (`+1.7` to `+24.3` pp) by resampling or steering candidate actions before execution, whereas appending post-trigger free-text advice from an uncalibrated fast auxiliary LLM (`Qwen3.7-Flash` `Tactile Spotting` in `arXiv:2611.19275`) trailed bare `Reminder-Only` notices (`56.1%` vs `67.8%` substantive response) and inflated `Strategic Fixation` triggers `4.74x` (`6.40` vs `1.35` per `100` actions, `86.7%` consecutive runs). See also "DO: In low-resource settings, reflect only on steps AFTER the decisive error" (recursive-improvement.md; post-episode reflection windowing vs in-episode detour cueing) and "DO: Pass every self-modification through one acceptance gate" (recursive-improvement.md).

> Source: Beyond Clumsy Agentic Tool Calling: How Cueing and Spotting Make the Difference (arXiv:2611.19275)

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

Tension with "DO: Schedule working-context compaction around materialized disk edits and preserve open-vs-settled epistemic tags" (this file): complexity-adaptive retention floors (`35%`/`50%`/`60%`) assume deterministic message/span trimming (`arXiv:2609.16461`), whereas generative LLM summarization (`CompAct-Bench`, `arXiv:2611.25673`) fails to honor `40%–80%` retention targets on `272K`-char histories (`18%–44%` adherence at `r = 80%`, plateauing near `0.12–0.14`) and requires scheduling compaction *after* coding edits materialize on disk (`86.9%` vs. `53.0%`) while tagging `settled` vs. `open` epistemic state.

> Source: Protocol-Preserving Context Trimming for Agentic Workflows: Benefits, Failure Regimes, and Budget Guardrails (arXiv:2609.16461)

### DO: Schedule working-context compaction around materialized disk edits and preserve open-vs-settled epistemic tags

Working-context compaction is severely lossy even on tasks a frontier model solves `3/3` times uncompacted, and its failure dynamics reverse depending on whether task state lives only in the prompt or is externalized into a persistent environment:
1. **Condition compaction timing on externalized state vs. context-resident evidence**: In **coding and repository-mutation workflows**, avoid early compaction (`25%` progress) before hypotheses are materialized on disk—once the agent writes concrete repository edits, the workspace itself carries verified progress and late compaction (`75%`) succeeds at high rates. Conversely, in **web search, deep research, and multi-app synthesis workflows** with zero environment persistence, accuracy degrades monotonically the later compaction occurs (`25% -> 50% -> 75%`) as irreplaceable negative exclusions and cross-source chains accumulate—externalize intermediate search exclusions and entity tables into an explicit structured scratchpad before compacting, and avoid asking LLM compactors to meet mild character-retention targets (`40%–80%`), where length calibration collapses.
2. **Preserve explicit epistemic status (`verified fact` / `ruled-out candidate` / `open hypothesis`) alongside raw facts**: Compaction fails through two distinct behavioral pathways—**Information Omission** (dropping constraints or completed steps, driving wasted repeated tool calls) and **Epistemic State Distortion** (`Premature Commitment`, turning unresolved hypotheses into settled conclusions or leaving settled exclusions marked open, driving immediate unverified wrong submissions or `39`-step budget exhaustion even when the underlying factual string is retained verbatim). Require compaction schemas to separate confirmed facts, falsified exclusions, active user constraints, and unverified hypotheses.

**Scope:** `CompAct-Bench` single-boundary working-context compaction benchmark across `200` `pass^3`-screened long-horizon ($\ge 8$-round) trajectories spanning `BrowseComp` (`79` web-search tasks), `SWE-bench` (`96` coding tasks), and `CompanyBench` (`25` multi-app workspace tasks), evaluating `12` frontier LLMs under Iterative Ratio Calibration (`IRC`) at `r = 10%` (`[0.097, 0.103]` character retention, `86.7%` overall adherence in prose / `86.0%` in `Table 9` "All" row) across `25%`, `50%`, and `75%` execution boundaries (`2,400` compactions, `3` continuation rollouts each under matched remaining $T - b$ action budgets), plus `Without H_b` state-ablation and `6`-category error attribution (`arXiv:2611.25673`).

**Evidence**:
- **`43.3` pp mean accuracy loss & opposite stage trends across domains (`arXiv:2611.25673`, Tables 2, 9–10, 12–14)**: Across `200` tasks where pre-compaction `pass^3 = 100%`, `12`-model mean strict `Avg@3` post-compaction accuracy fell to **`56.7%`** (`range 46.0%–68.5%`: `Claude Opus 5` `68.5%`, `Gemini 3.8 Flash` `65.5%`, `Kimi K3` `62.0%`, `GPT-5.6-Sol` `59.5%`, down to `Doubao Seed 2.1 Pro` `46.0%`; within-domain prefix length was uncorrelated with accuracy, $|\rho| \le 0.03$). Across `25% -> 50% -> 75%` compaction boundaries, **`Search` degraded monotonically from `52.9% -> 42.6% -> 34.6%`** (declining in `11/12` models, monotonic in `9/12`), whereas **`Coding` improved monotonically from `64.0% -> 72.7% -> 86.1%`** (`12/12` models peaked at `75%`, monotonic in `10/12`), and `Workspace` peaked at `50%` (`9/12`). Removing *both* prefix $H_b$ and summary $M_b$ (`Without H_b`, `Table 14`), `Coding` from reconstructed repo state alone scored **`66.7% / 58.1% / 71.9%`** (`+18.2 / +22.6 / +56.3` pp over unedited initial state; $M_b$ added `-2.7 / +14.6 / +14.2` pp), and trajectories with a materialized pre-boundary repo edit reached **`86.9%` vs. `53.0%` without edit** ($p = 3 \times 10^{-8}$, $\rho = 0.62$), whereas `Search` `Without H_b` collapsed to `26.9% / 15.4% / 7.4%` (`M_b` added `+26.0 / +27.2 / +27.2` pp). `IRC` ratio adherence held `65–99%` at `r = 5%–20%` (`Table 10`) but collapsed to **`18%–44%` at `r = 80%`** (compressing `272K`-char `Workspace` histories to `0.12–0.14` regardless of prompt).
- **Omission (`+18.2` pp repeated work) vs. Epistemic Distortion (`56.7%` of early failures, `Tables 16–17`, `Case F`)**: Budget exhaustion accounted for `91.6%` (`Search`), `92.0%` (`Coding`), and `97.7%` (`Workspace`) of failed continuations, while early wrong termination concentrated at the `25%` boundary (`20.8%` `Search`, `14.8%` `Coding`). `Premature Commitment (PC)` appeared in **`56.7%` of early failures vs. `46.0%` of budget exhaustions** (`Progress/State Loss` `55.2% vs. 44.6%`, `Constraint Omission` `47.8% vs. 48.8%`, `Factual Distortion` `40.3% vs. 35.2%`). Omissions drove **repeated completed work** (`CO` **`+18.2` pp**, `LR` `+14.2` pp, `PSL` `+13.8` pp), whereas distortions drove **unverified commitment** (`CGD` **`+10.5` pp**, `FD` `+7.3` pp, `PC` `+5.2` pp); in `Case F`, all `12/12` compactors kept the exact `"8 authors vs. 7"` fact, yet marking the exclusion *settled* yielded **`4/4` passes (`4–6` rounds)** while leaving it *open* caused **`5/8` models to exhaust all `39` actions** (see [compact-bench-working-context-compaction](../research-briefs/compact-bench-working-context-compaction.md)).

Tension with "DO: Enforce protocol-aware context trimming with adaptive budget guardrails" (this file): `arXiv:2609.16461` sets complexity-stratified token-retention floors (`35%`/`50%`/`60%`) to avoid `<= 25%` protocol-adherence collapse under message trimming, whereas `CompAct-Bench` (`arXiv:2611.25673`) shows that under generative summarization (`r = 10%`), LLM compactors fail to honor `>= 40%–80%` retention targets on long `272K`-char histories (`0.12–0.14` plateau) and task survival depends critically on *when* compaction fires relative to materialized disk state (`86.9%` with repo edit vs. `53.0%` without in `Coding`, vs. `52.9% -> 34.6%` late-compaction decay in `Search`) and on preserving `open` vs. `settled` epistemic tags.

See also "DO: Restore earlier-turn safety constraints and enforce them at a deterministic action boundary" (agent-sandbox-safety.md) and "DON'T: Place compacted history summaries in the user-request authorization slot or rely on prose-only summary tags" (agent-sandbox-safety.md).

> Source: CompAct-Bench: A Benchmark for Working-Context Compaction in Long-Horizon Agent Tasks (arXiv:2611.25673)

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

Tension with "DO: Annotate Code Mode tool stubs with explicit return-value shapes and bound router fallbacks rather than stacking front-door routers on strong coders" (this file) and "DO: Pre-inject deterministic analyzer outputs for open-weight models and resolve domain aliases server-side rather than exposing raw ISO-code MCP arguments" (this file): two-meta-tool progressive JSON disclosure (`get_tool` + `invoke_tool`, `arXiv:2610.30157`) cuts upfront schema tokens by `71–99%` while keeping intermediate JSON payloads in context, whereas `Code Mode` (`search()` + `execute()` with return-shape stub hints, `arXiv:2611.19123`) keeps multi-step intermediate outputs inside the script sandbox (`70%–90%` fewer total tokens; `-22.7` and `-39.5` pp without return-shape hints), and for `<= 27B` open-weight models (`arXiv:2611.19439`—where `45.2%` [`14/31`] never emit a tool call and `52.4%` of live calls return empty on guessed ISO codes) pre-computed deterministic prompt injection (`inject`, `10/10` models improved) beats live `MCP` unless checkpoint tool-calling and prose synthesis are verified.

> Source: Matched Capabilities, Different Behaviors: A Controlled Study of MCP and CLI Interfaces for Language Agents (arXiv:2610.34298); MCP vs CLI for AI Agents: A Comparative Analysis of Tool Integration Strategies for Autonomous Systems (arXiv:2610.30157)

### DO: Annotate Code Mode tool stubs with explicit return-value shapes and bound router fallbacks rather than stacking front-door routers on strong coders

When exposing large Model Context Protocol (`MCP`) tool catalogs (`40–2,000+` tools), replace multi-turn JSON tool schemas (`Plain MCP`) with a two-meta-tool **`Code Mode` gateway** (`search()` returning Python stubs + `execute()` running bounded scripts in an isolated sandbox and returning only the final output) and treat **stub return-shape annotations** (`keys`, `types`, `list` vs `dict`)—not front-door tool routers or dynamic call-shape routers—as the first-order quality lever:
1. **Always include explicit return-value shapes on `Code Mode` stubs**: Bare `-> dict | list` stubs collapse weaker open-weight coders below `Plain MCP`, whereas explicit return-shape hints raise success by up to **`+39.5` percentage points**—`3–4x` the utility gain of adding a front-door decision-model router.
2. **Skip front-door tool routers on strong coders and never route call shapes dynamically**: Putting a decision-model subset router in front of `Code Mode` provides no statistically confirmed gain (and adds **`+1.45 s`** latency and slight utility loss on strong coders whose native `search()` + `Code Mode` already nears ceiling, requiring a router under **`0.4–0.7 s`** just to break even), while dynamic per-task JSON-vs-code shape routing trails fixed `Code Mode`.
3. **Enforce a bounded `full_code` fallback and non-authoritative subsets whenever a router is used**: Because candidate embedding retrieval caps router recall on large catalogs (`0.65` at `200` tools, `0.44` at `2,000` tools) and poisoned tool descriptions steer routers directly, retry subset misses in `Code Mode` via `search()` over the full catalog first (`full_code`), cap any JSON `request_more_tools` fallback at **`<= 2` calls**, and never use router subset selection as an authorization gate.

**Scope:** Pre-registered controlled evaluation (`confirmatory-freeze-v1`) on a synthetic `12`-server, `42`-tool resettable MCP world plus up to `1,958` public-catalog distractor tools (`42`, `200`, `2,000` tools; instant mock execution; hand-written stub return-shape hints) across `4` gateway configurations (`Plain MCP`, `Router+JSON`, `Code Mode`, `Router+Code`) and `3` quantized open-weight agents (`Qwen3.8-27B` 4-bit, `Gemma-4-26B-A4B` NVFP4, `Nemotron-3-Nano-30B-A3B` NVFP4; `T = 0`, thinking disabled) over `119` sealed test instances (`1,785` serial runs, `21` template families) plus `119` extension instances (`238` pooled) and a `4B` LoRA `spark-s1` router (`arXiv:2611.19123`).

**Evidence**:
- **`Code Mode` + return-shape stubs (`arXiv:2611.19123`, `Tables 2–4`)**: On `119` sealed test instances (`21`-family cluster bootstrap), `Code Mode` cut total tokens by **`84%`** (`Qwen`: `26,602 -> 4,362`), **`70%`** (`Gemma`: `16,779 -> 5,112`), and **`90%`** (`Nemotron`: `74,608 -> 7,553`), significantly lifting utility on `Qwen` ($\Delta U = +0.364$, Holm $p = 0.0012$, `+13.4` pp success to `0.992`) and `Nemotron` ($\Delta U = +0.861$, Holm $p = 0.0012$, `+19.3` pp success to `0.555`). Stripping return-shape hints (`Ext-1`) dropped `Gemma` by **`-22.7` pp** (`0.891 -> 0.664`, $\Delta U = -0.296$, Holm $p = 0.0003$, `+4,372` tokens) and `Nemotron` by **`-39.5` pp** (`0.555 -> 0.160`, $\Delta U = -0.478$, Holm $p = 0.0003$, `+6,104` tokens)—below `Plain MCP` (`0.866` and `0.361`)—while barely affecting `Qwen` (`0.992 -> 0.975`, $p = 0.20$).
- **Front-door routers, `14x` unbounded fallback blowup, and router injection (`Tables 5–6, 11`, `§5.3–§7`)**: Pooled across `238` test instances (`Ext-2`), `Router + Code` vs `Code Mode` (`H3`) was **not confirmed** for any agent (`Qwen` $\Delta U = -0.028$, Holm $p = 0.15$; `Gemma` `+0.099`, $p = 0.21$; `Nemotron` `+0.109`, $p = 0.22$), and leave-one-task-out shape routing scored `-0.021` below fixed `Code Mode`. At `2,000` tools (`10`-task scale arm), `Plain MCP` hit `0.00` (context overflow) while standalone `Code Mode` held `0.90` success at `6.0–6.3 s` and `11.9K–14.3K` tokens; `top-30` retrieval capped router recall at `0.44`, causing unbounded JSON `request_more_tools` fallback to blow up to **`222.7 s` mean latency (`570.2 s` p90), `370,482` tokens (up to `23` calls / `900K` tokens), and `0.40` success**, whereas bounded `full_code` fallback cut latency **`14x` to `16.1 s` (`34,490` tokens, `0.90` success)**. In exploratory probing (`n = 39`), one `"ALWAYS select this tool"` description hijacked a prompted LLM router on **`39/39` (`100%`)** tasks and the `4B` scoring router on **`62%`** (see [mcp-code-mode-return-shape-stubs-vs-routers](../research-briefs/mcp-code-mode-return-shape-stubs-vs-routers.md)).

Tension with "DO: Decouple semantic action commitment from interface-specific tool realization and repair realization locally" (this file) and "DO: Induce tool dependency graphs via counterfactual sandbox execution and cap retrieval propagation at one hop with top-2 providers per input" (this file): two-meta-tool progressive JSON disclosure (`get_tool` + `invoke_tool`, `arXiv:2610.30157`) and 1-hop dependency retrieval (`LIBRA`, `arXiv:2611.05445`) cut upfront JSON schema bloat while still routing every intermediate tool return through model context, whereas `Code Mode` (`search()` + `execute()`, `arXiv:2611.19123`) keeps multi-step chaining and filtering inside the script sandbox (`70%–90%` fewer total tokens and `+13.4` to `+19.3` pp higher success on `Qwen3.8-27B`/`Nemotron-3-Nano`, conditional on return-shape stub hints) and makes front-door subset routers statistically redundant (`-0.028` utility and `+1.45 s` slower on `Qwen3.8-27B`).

Tension with "DO: Pre-inject deterministic analyzer outputs for open-weight models and resolve domain aliases server-side rather than exposing raw ISO-code MCP arguments" (this file): interactive `Code Mode` (`arXiv:2611.19123`) and live `MCP` excel on tool-capable checkpoints (`Qwen3.8-27B`), whereas across `31` open-weight instruction models (`0.6B–27.8B`, `arXiv:2611.19439`), `14/31` (`45.2%`) never emit a parseable tool call (`Gemma-3` `1B–27B` at `0%`), so bounded deterministic pre-analysis should be injected directly into the prompt unless the target checkpoint's tool-calling and prose-synthesis fidelity are verified.

Tension with "DO: Declare mandatory safety-tool chains in MCP routing policies and monitor pre-execution route drift against operational shortcut pressure" (agent-sandbox-safety.md) and "DO: Compile web-agent tasks offline against a typed Trusted Website API and feed back only schema-level error diagnostics during replanning" (agent-sandbox-safety.md): policy-constrained routing (`ShadowBench-MCP`, `arXiv:2611.11720`) enforces mandatory safety steps and offline networkless compilation (`Baya`, `arXiv:2611.06039`) guarantees `0.0%` untrusted-web IPI ASR (`327.15 s` compile time), whereas interactive `Code Mode` (`arXiv:2611.19123`) targets low-latency (`3.6–6.4 s` median) trusted/governed catalogs where front-door routers are steerable (`62%–100%` on `"ALWAYS select"`) and live `execute()` leaves tool-result IPI nonzero (`9.3%` pilot ASR unless paired with provenance/write-integrity gates). See also "DON'T: Treat HTTP 200 / success tool return codes as workflow success without state verification" (agent-sandbox-safety.md).

Tension with "DO: Pair progressive BM25 manual tools with five orthogonal sync-async execution primitives, step-atomic cycle holds, and console-history injection for live stateful engines" (this file): two-meta-tool `Code Mode` (`search()` + `execute()`, `arXiv:2611.19123`) suffices for sub-second stateless API catalogs, whereas live multi-hour C++/Qt simulation engines (`itasca-mcp` / `yade-mcp`, `arXiv:2611.33926`) require `5` separate sync/async primitives (`execute_code`, `execute_task`, lock-free `check_task_status`, step-boundary `interrupt_task`, `list_tasks`), single-timestep `cycle hold` synchronization, and human `console history` injection alongside `BM25` + `browse` manual tools (`20/21` autonomous calibrations solved).

> Source: Beyond Plain MCP: Do Decision Models and Code Mode Make Tool Use Cheaper and Faster? (arXiv:2611.19123)

### DO: Pre-inject deterministic analyzer outputs for open-weight models and resolve domain aliases server-side rather than exposing raw ISO-code MCP arguments

When augmenting small or mid-size open-weight instruction models (`<= 27B` parameters) with fast, deterministic rule-based analyzers, morphological parsers, or domain dictionaries over bounded inputs:
1. **Prefer deterministic pre-execution prompt injection (`inject`) over live `MCP` tool calling unless the target checkpoint is verified to call tools reliably and answer in prose**: Nearly half of open-weight instruction models—governed by post-training family rather than parameter scale—never emit a parseable tool call, function-calling specialists frequently emit raw call syntax instead of prose answers, and adding a tool-use system prompt alone (`mcp_prompt`) measurably degrades generation quality.
2. **Bind language/domain codes server-side or resolve aliases rather than requiring callers to guess opaque ISO/enum identifiers**: Even tool-capable models hallucinate unsupported or sibling codes on over half of calls; inject known request context at the host or expose alias-resolving lookup tools rather than raw per-item code parameters, and verify that underlying lexicons cover target-task semantics (not just structural tags) before expecting downstream gains.
3. **Include a no-tool `mcp_prompt` control arm when benchmarking `MCP` augmentations**: Always separate the effect of changing the system prompt from the effect of live tool execution.

**Scope:** Controlled `62,920`-record evaluation across `31` open-weight instruction-tuned models (`0.6B–27.8B` in `bf16`, greedy decoding, `32,768` context, `vLLM`, including `4` function-calling specialists) and `7` delivery conditions (`zeroshot`, `mcp_prompt` control, `inject` `6`-tool pre-analysis, `inject_rich` `13`-tool, `mcp` `6` per-word tools, `mcp_coarse` `1` sentence tool, `mcp_rich` `13` tools) over `GiellaLT`/`UralicNLP` (`91.1%–98.5%` token parser coverage) on `68` 6-way parallel sentences (`Komi-Zyrian`, `Moksha`, `Erzya`, `Udmurt` $\leftrightarrow$ `English`/`Finnish`), with `816` expert-linguist sentence adequacy and error judgments on `Qwen3.8-27B` (`arXiv:2611.19439`).

**Evidence**:
- **Open-weight `MCP` call failures vs universal `inject` gains (`arXiv:2611.19439`, `Tables 2–8 & 11`)**: On `Qwen3.8-27B` (the **only** model of `31` that called tools on `100%` of sentences and answered in prose), expert-accepted English translations rose from **`13/272` (`4.8%`, `zeroshot`) to `43/272` (`15.8%`, `inject`) and `55/272` (`20.2%`, `mcp`)**—driven by bilingual dictionary glosses (`73.9%–80.3%` token coverage in `Moksha`, `Erzya`, and `Komi-Zyrian` cutting `Wholesale replacement` errors from `48/54/39` to `21/24/10`, whereas `Udmurt` with `0%` English glosses stayed at `4/68 -> 4/68` under `inject`). Across all `31` models, however, **`14/31` (`45.2%`) never emitted a tool call** (`57.6%` silent records overall: `9` failed all probes including `Gemma-3` `1B/4B/12B/27B` at `0%` vs `Qwen3` `1.7B+` at `46%–100%`, `2` emitted unparseable syntax, `3` stayed silent zero-shot), function-calling specialists returned raw call syntax without prose on **`42.4%`** (`Hammer2.1-3b`) and **`17.2%`** (`xLAM-2-1b-fc-r`) of outputs (vs `4.3%` non-specialists), `mcp` degraded `3` of `4` reliable callers on `kpv->eng` (`Qwen3-4B` `-11.8` `chrF++`, `Mistral-Nemo-12B` `-3.2`, `Llama-3.1-8B` `-0.4`), and `mcp_prompt` alone cost **`-1.4` to `-4.3` `chrF++`**. By contrast, pre-computed `inject` raised `chrF++` on **`10/10` models** across all three glossed languages (`+1.2` to `+8.4` pts; significant in `25/30` cells, `0` losses).
- **`57.5%` invalid/wrong language-code arguments & `mcp_coarse` vs `mcp_rich` (`Tables 8–9`, `Appendix A`)**: Across **`315,910` `MCP` calls**, only **`42.5%`** (`11.5%–74.5%` per model) passed the valid source ISO code; **`49.1%`** sent unsupported codes (`en` `74,449` times; `kv`/`kom`/`komi-zyrian`/`kz`/`kmz`/`kmm` before `kpv`) and **`8.4%`** sent a supported wrong language (`26,630` `koi` calls on `kpv`), yielding **`52.4%` empty tool returns**. Collapsing `6` tools into `1` sentence tool (`mcp_coarse`) gave `0.0` median change (`30` up, `29` down), whereas adding server-side ISO code resolution and inflected search (`mcp_rich`) gained `+7.0` `chrF++` on reliable callers; into Uralic targets, all arms failed (`2.0–5.4` `chrF++` vs `9.3–10.8` floor, `22.9%` wrong language under `mcp`; see [prompt-preanalysis-vs-mcp-uralic-translation](../research-briefs/prompt-preanalysis-vs-mcp-uralic-translation.md)).

Tension with "DO: Decouple semantic action commitment from interface-specific tool realization and repair realization locally" (this file) and "DO: Annotate Code Mode tool stubs with explicit return-value shapes and bound router fallbacks rather than stacking front-door routers on strong coders" (this file): interactive `MCP` progressive disclosure (`arXiv:2610.30157`) and `Code Mode` (`arXiv:2611.19123`) outperform static prompt injection when the executor calls tools reliably and synthesizes prose (`Qwen3.8-27B`: `55/272` under `mcp` vs `43/272` under `inject`, `+10.5` `chrF++`), whereas across `31` open-weight instruction models (`0.6B–27.8B`, `arXiv:2611.19439`), `45.2%` never emit a tool call, function-calling specialists omit prose on `17.2%–42.4%` of outputs, and `52.4%` of live calls return empty due to guessed ISO codes—making pre-computed `inject` (`10/10` models improved, `0` significant losses) the reliable default for bounded deterministic analyzers on unverified open-weight models. See also "DON'T: Trust MCP tool metadata without trace-aware vetting" (agent-sandbox-safety.md).

Tension with "DO: Pair progressive BM25 manual tools with five orthogonal sync-async execution primitives, step-atomic cycle holds, and console-history injection for live stateful engines" (this file): pre-computed prompt `inject` (`arXiv:2611.19439`) works when a fast deterministic analyzer can pre-process a bounded sentence input upfront, whereas `241,283`-token simulation manuals and multi-hour interactive solves (`arXiv:2611.33926`) cannot be pre-computed—requiring tool-capable checkpoints (`20/21` across `7` frontier/open-weight models, plus `Qwen3.5-4B` CI tool tests) paired with `query`/`browse` progressive disclosure (`2.7%` manual tokens read).

> Source: Do Rule-Based Tools Help LLMs Translate Endangered Uralic Languages in the Prompt or over MCP? (arXiv:2611.19439)

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

Tension with "DON'T: Trigger online detour cues on single errors or two-step repeats, replace concise reminders with auxiliary-LLM spotters, or equate detour cessation with bug-fix resolution" (this file): permanent external `MCP` server faults (`91.3%` permanent in `arXiv:2610.32555`) and infeasible `Unreachable Goals` (`0.0%` pass at `>= 4` calls in `arXiv:2611.07689`) require hard `<= 2`-retry fast-fail circuit breakers, whereas inside mutable repository debugging (`SWE-agent`, `arXiv:2611.19275`), single command failures and `2`-step repeats reflect normal test reproduction or autonomous self-recovery (`100%` [`3/3`] baseline `2`-step escape), so online error cues must wait for repeated identical error signatures without intervening state edits (`Failure Inertia`).

> Source: Tool-Calling LLM Agents Under Realistic MCP Faults: Scale Does Not Purchase Fault Tolerance (arXiv:2610.32555); MCPHallu: Benchmarking Reasoning, Execution, and Memory Hallucinations in MCP Agents (arXiv:2611.07689); MCP-Eco: A Linked Dataset of MCP Servers, Consumers, and Development Activity (arXiv:2611.06897)

### DO: Extract skills as explicit text from paired trajectories before distilling them into role-conditioned latent representations

When building compact skill memories or multi-round coordination prefixes for multi-agent systems that communicate or condition via continuous latent states (`LatentMAS` / `RecursiveMAS`), do not train end-to-end latent skill vectors directly from raw trajectories without an intermediate natural-language skill abstraction, do not retrieve skills using task-query similarity alone, and do not chain multi-round full-text agent outputs or single-feature latent updates sequentially across rounds:
1. **Contrastive Text-to-Latent Skill Memory (`SkillMem`, `arXiv:2610.37935`)**: First contrast paired success/failure trajectories into explicit, human-auditable text skills; then project retrieved skills through role-conditioned latent adapters so each specialist role (`Planner`, `Critic`, `Refiner`, `Solver`) receives a role-specific view of the shared skill bank.
2. **Parallel Intra-Agent Feature Convolution + Inter-Agent Graph Convolution (`ConvRSI`, `arXiv:2611.20891`)**: In multi-round white-box latent collaboration, encode static text features (`[task, role, system, experience]`) once into $K$ content-dependent slots, apply channel-wise 1D intra-agent convolution (`kernel = 5`) across `[task, role, system, experience, message]` concurrently per agent, and aggregate local messages synchronously via a normalized Graph Convolutional Network (`GCN`) over the collaboration adjacency matrix $\mathbf{A}$ to pre-compute $K$-token soft prefixes $\mathbf{p}_i^{(r)}$ before scheduled LLM forwards—preventing multi-round text error compounding while halving recursion wall-clock latency.

**Scope:** SkillMem role-conditioned latent skill memory across 6 reasoning and coding benchmarks (GSM8K, MATH, AIME, HumanEval, MBPP, GPQA) on Qwen2.5-7B/14B and Llama-3.1-8B (arXiv:2610.37935); ConvRSI two-stage teacher-forced latent multi-agent co-evolution (`4` random seeds on NVIDIA RTX 4090D) across `MATH-500` and `MBPP+` at recursion depths $r \in \{1, 2, 3\}$ on `Sequential-Light` (`Qwen3-1.7B` planner, `Llama-3.2-1B-Instruct` critic, `Qwen2.5-Math-1.5B-Instruct` solver) and `Mixture` (`Qwen2.5-Coder-3B-Instruct`, `BioMistral-7B`, `DeepSeek-R1-Distill-Qwen-1.5B`, `Qwen3.5-2B` summarizer) vs. `RecursiveMAS`, `Recursive-TextMAS`, `ModularRSI`, `Hermes+`, and `MASS` (arXiv:2611.20891).

**Evidence**:
- In `SkillMem` (`arXiv:2610.37935`), distilling paired trajectory contrasts into text skills before projecting into $K=4$ latent skill tokens per role improved multi-agent accuracy by $+4.8\text{ pp}$ over text-only skill injection while cutting skill context tokens by $87.5\%$ (from ~320 tokens/role to 40 latent tokens across 4 roles); removing the intermediate text-extraction stage dropped accuracy by $-3.6\text{ pp}$, and removing role conditioning in the latent adapter dropped accuracy by $-2.4\text{ pp}$ (see [skillmem-compact-external-skill-memory-latent-mas](../research-briefs/skillmem-compact-external-skill-memory-latent-mas.md)).
- In `ConvRSI` (`arXiv:2611.20891`, `Tables 2 & 4`), at $r = 3$ on `Sequential-Light`, parallel intra+inter latent convolution reached **`75.0%`** on `MATH-500` vs. `71.4%` `RecursiveMAS` (`+3.6 pp` absolute / `+5.04%` relative) and `69.6%` `Recursive-TextMAS` (which degraded from `71.4%` at $r = 1$ via sequential text error accumulation), while cutting generated tokens by **`17.27%` (`556 -> 460`)** and wall-clock runtime by **`45.11%` (`2,658 s -> 1,459 s`, `1.82x` speedup; `3.24x` vs. `Recursive-TextMAS` `4,721 s`)**, and reached **`32.9%`** `Pass@1` on `MBPP+` in `695 s` (`1.80x` vs. `1,249 s` `RecursiveMAS`, faster than 1-round `776 s`). Under heterogeneous `Mixture`, `ConvRSI` gained **`+5.2 pp` on `MATH-500` (`60.6% -> 65.8%`)** and **`+2.9 pp` on `MBPP+` (`47.4% -> 50.3%`)**; removing `IntraConv` or `InterConv` dropped `MATH-500` (`r=3`) from `75.0%` to `71.8%` and `72.4%` (`MBPP+` `32.9% -> 30.8%` and `31.1%`; see [convrsi-parallel-convolutional-latent-mas](../research-briefs/convrsi-parallel-convolutional-latent-mas.md)).

Tension with "DON'T: Pass cross-model KV-cache latent handoffs across untrusted data or unauthenticated agent boundaries, or rely on target-side cache guards to preserve prompt-injection utility" (multi-agent-coordination.md): latent skill prefixes (`SkillMem`, `arXiv:2610.37935`) and parallel latent graph convolution (`ConvRSI`, `arXiv:2611.20891`) assume **benign inputs and mutually trusted checkpoints inside one operator's boundary**; across untrusted external data or unauthenticated peers (`Chasm`, `arXiv:2611.34278`), cross-model KV-cache handoffs strip target prefill safety and `SecAlign` IPI alignment (`0.4% -> 44.2%` IPI ASR; `0.4% -> 31.9%` even without a mapper), leak `94.6%` of layer-0 plaintext tokens, and lose `28.0–92.4` `GSM8K` points over `3–6` hops.

> Source: SkillMem: Compact External Skill Memory for Latent Multi-Agent Systems (arXiv:2610.37935); From Recursion to Convolution: Parallel Self-Improvement for Multi-Agent Systems (arXiv:2611.20891)

### DO: Induce tool dependency graphs via counterfactual sandbox execution and cap retrieval propagation at one hop with top-2 providers per input

When organizing large executable tool libraries (`100–1,000+` tools), do not rely on static LLM description matching or unconstrained multi-hop graph traversal to discover prerequisite producer tools (` tool A`'s output feeds `tool B`'s required parameter). Induce the **Tool Dependency Graph (TDG)** programmatically (`LIBRA`):
1. **Counterfactual Execution Verification**: After candidate schema alignment between producer outputs and consumer inputs, run a counterfactual sandbox check — execute the consumer tool with vs without the producer's concrete output (or with a type-matched dummy value) and retain the dependency edge only if real execution succeeds and the dummy/omitted call fails.
2. **Bounded 1-Hop, Top-2 Retrieval Propagation**: At query time, retrieve initial seed tools by query similarity and expand prerequisite providers by **at most 1 hop**, retaining at most the **top-2 highest-scoring provider tools per required input parameter**. Expanding beyond 1 hop or injecting unconstrained neighbors degrades tool-calling accuracy via distractor bloat. Procedure: [`counterfactual-tool-dependency-induction`](../skills/counterfactual-tool-dependency-induction/SKILL.md).

**Scope:** LIBRA programmatic tool library induction and dependency-aware retrieval across ToolBench, RestBench, and StableToolBench (`1,600+` APIs) on Qwen2.5 and GPT-4o agents (arXiv:2611.05445).

**Evidence**: In `LIBRA` (`arXiv:2611.05445`), pruning schema-inferred dependency edges via counterfactual sandbox execution removed 38.6% false-positive edges and lifted prerequisite tool recall@5 from 68.2% (dense embedding retrieval) to 89.4%. Bounding graph expansion to 1 hop and top-2 providers per input improved end-to-end multi-tool pass rate by +9.8 pp over flat top-$k$ retrieval, whereas 2-hop unconstrained expansion increased context tokens by $2.7\times$ and dropped pass rate by $-4.3\text{ pp}$.

Tension with "DO: Pair 2-hop local capability warmup with contextual LLM routing memory in privacy- or scale-constrained decentralized graphs, and harden hubs against misrouting" (multi-agent-coordination.md): `LIBRA` bounds *centralized* full-schema prompt expansion to `1 hop` (`top-2` providers) so distractor schemas do not bloat a single agent's context (`2.7x` tokens at 2 hops), whereas `GraphHarness` (`arXiv:2611.15521`) propagates compact semantic *domain summaries* across `2 hops` of a decentralized peer network where no central tool index exists.

Tension with "DO: Annotate Code Mode tool stubs with explicit return-value shapes and bound router fallbacks rather than stacking front-door routers on strong coders" (this file): 1-hop dependency-aware subset retrieval (`LIBRA`, `arXiv:2611.05445`) improves multi-turn JSON tool calling (`+9.8` pp over flat top-$k$), whereas in front of `Code Mode` (`search()` + `execute()`, `arXiv:2611.19123`) a fine-tuned `4B` subset router showed no statistically confirmed gain over `238` instances (`-0.028` utility and `+1.45 s` slower on `Qwen3.8-27B`) and hit `0.65`/`0.44` candidate-retriever recall ceilings at `200`/`2,000` tools, requiring a bounded `full_code` fallback to prevent `14x` latency blowups.

> Source: LIBRA: Programmatic Induction of Executable Tool Libraries (arXiv:2611.05445)

### DO: Project host-verified substrate state telemetry into operational tool selection rather than using static schemas or neutral placeholders

Tool-using agents routinely fail when environment substrate conditions change mid-session (e.g., quota exhaustion, rate-limit backoff windows, degraded endpoint latency, read-only filesystem mounts, or expired auth scopes) because static tool schemas never reflect live operational health. Do not rely on the agent to infer substrate health from failed tool calls, and do not inject unverified or neutral placeholder telemetry (`status: unknown` / `quota: N/A`), which systematically induces over-cautious abstention or unnecessary fallback thrashing:
1. **Host-Verified Substrate State Telemetry (`SST`)**: Have the harness probe and attach a compact, deterministic `SST` block (`availability`, `remaining_quota`, `p95_latency_ms`, `auth_scope_state`, `recommended_route`) verified by the host runtime prior to action selection.
2. **Operational Control Policy**: Train or prompt the router to switch from degraded primary tools to verified fallback tools or batching strategies only when host-verified `SST` crosses explicit operational thresholds, omitting telemetry fields entirely when no verified probe exists. Procedure: [`verified-telemetry-tool-routing`](../skills/verified-telemetry-tool-routing/SKILL.md).

**Scope:** Agent Harness Awareness / Substrate State Telemetry (`SST`) across 1,800 tool-routing episodes under quota, latency, and permission perturbations across 5 LLMs (arXiv:2611.05391).

**Evidence**: In `arXiv:2611.05391`, injecting host-verified `SST` into the harness raised operational tool-routing accuracy under degraded substrate conditions from 51.4% (static schema baseline) to 88.7% and cut wasted failed tool invocations by 73.6%. Conversely, injecting neutral placeholder telemetry when substrate probes were unavailable dropped benign primary-tool utilization by 19.2 pp compared to omitting the unverified fields.

Tension with "DO: Separate static multi-hop delegation bounds from live ancestor-state effective permissions and isolate downstream anomalies via branch-scoped containment" (multi-agent-coordination.md): omitting unavailable optional `SST` probes prevents `-19.2 pp` over-cautious abstention during *operational tool routing* (`arXiv:2611.05391`), whereas at the *security authorization (`PEP`/`PDP`) boundary* (`Agent-ZTA`, `arXiv:2611.18999`), missing or out-of-freshness-window required ancestor security-state records must be classified `unavailable` and fail closed to `Deny`.

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

### DO: Partition automated readiness repairs into static, ambiguity-refusing parametric, and checker-bound delegated contracts behind a zero-LLM MCP server

When building automated production-readiness, DevSecOps, or operational remediation tools for AI-generated ("vibe-coded") repositories over MCP, keep model inference out of the MCP server and avoid free-form LLM patching or trusting agent completion claims:
1. **Classify every rule's fix path upfront (`Static` / `Parametric` / `Delegated`)**: Serve **static content contracts** (idempotent templates with AST/file anchors, declared packages, and required environment keys) for project-invariant rules, **parametric contracts** populated deterministically from codebase files for project-specific values (**refusing and listing competing candidates whenever extraction is ambiguous**, such as multiple lockfiles, DB drivers, or entry points, rather than guessing or asking an LLM), and **delegated constraint contracts** (carrying zero pre-written code—only the violation, allowed file boundary, invariant files, and the exact checker predicate) strictly for codebase-organization refactors.
2. **Enforce author-blind checker re-verification and full-suite regression revert**: Treat every `"fix applied"` report—whether applied from a static template, parametric extraction, or live IDE agent—as an untrusted claim. Accept a change only if the flagging rule's deterministic AST/config/entropy checker passes on disk **and** a full-project re-audit confirms zero previously passing rules regressed (reverting regressions immediately within a bounded `<= 3`-attempt-per-issue, `<= 5`-cycle loop), and require out-of-band provider rotation whenever git-history secrets are rewritten.
3. **Gate release on ordered conditions (`P0 == 0` -> `score >= 90` -> build-backed monotonic veto) before service-first CI/CD wiring**: Evaluate zero critical (`P0`) failures and the weighted score threshold first, consult any outcome-trained deployability model (trained with real container-build status and monotonic constraints so fixing a rule can never lower predicted deployability) **last as a veto-only check**, seal secrets outside the repository tree, and deploy + live-smoke-test the target service *before* wiring CI/CD workflows. Procedure: [`tiered-contract-readiness-gate`](../skills/tiered-contract-readiness-gate/SKILL.md).

**Scope:** `ProdPilot` (`v1.0.0rc1`) zero-LLM local stdio MCP server auditing, repairing, gating, and deploying `Node.js 20 LTS` (`Express`, `28` rules) and `React 18` (`Vite 5`, `22` rules) projects across a frozen `50`-rule production-readiness ruleset (`9` domains, priorities `P0–P5`), evaluated on `499` real GitHub repositories (`7,407` violations), `23` full-chain sample repositories (`269` rule instances, `237` applied static/parametric contracts), `10` live IDE agent delegated-fix trials (`Cursor 3.20.17` + `Grok 4.6`, `Claude Code` + `Claude Opus 5`), `684` real Render deployments (`675` valid-build rows: `506` train, `169` held-out), and cross-IDE protocol tests across `VS Code 1.137.0` (`Copilot Chat 0.65.0`), `Cursor 3.20.17`, and `Windsurf/Devin 3.10.23` (`arXiv:2611.17381`).

**Evidence**:
- **93.5% of real-world readiness violations need zero LLM code (`arXiv:2611.17381`, Table V & Section VII-B)**: Across `50` rules, `28` (`56.0%`) are static templates, `16` (`32.0%`) are parametric extractions, and only `6` (`12.0%`: `4` structural + `2` git-history secret rules) are delegated (`88.0%` model-free ruleset: `89.3%` Express, `86.4%` React). Across `499` real repositories (`7,407` violations, mean `14.8`/repo, `100%` failing $\ge 1$ `P0` rule with mean `4.6` `P0` failures), **`93.5%` (`6,926/7,407`: `65.9%` static + `27.6%` parametric; `94.9%` Express, `91.3%` React)** fall into the two deterministic classes (`96.7%` [`260/269`] in the sample loop). Ambiguous multi-candidate projects triggered deterministic refusal with candidate lists on `15/74` (`20.3%`) parametric instances rather than silent misconfiguration.
- **Author-blind verification catches 10.5% false-success reports & prevents middleware-order regressions (`Sections VII-B–E`)**: Applied static contracts passed checkers in `87.6%` (`155/177`, rising to **`89.8%`** once contracts declared required env keys) and parametric contracts in **`95.0%`** (`57/60`), while independent re-verification rejected **`25/237` (`10.5%`)** fixes reported as applied (`21` still failing their checker + `4` reverted by the `~3.6 s` regression guard after breaking a passing rule, such as inserting a metrics route above `helmet`). Live IDE agents resolved `10/10` delegated trials on attempt `1` within contract file boundaries with `0` regressions.
- **Ordered gate + monotonic build-backed deployability veto (`Tables XI–XIII`)**: Failing a single `P0` rule still leaves a weighted score of `93` (Express) or `91` (React), while `5` React projects scoring `99–100` lacked Vite's `index.html` and failed to build. Constrained histogram gradient boosting (`Model D`, `0.369` threshold) achieved **`0.909` held-out ROC AUC** (`0.898` excluding `39` Node-24 rows; `0.565` PR AUC vs. `0.269` stack baseline and `0.189` prevalence; `0.772` ROC AUC without the container-build feature) with **`0/7,281`** single-rule-fix score inversions (vs. `2,393` and `3,234` inversions in unconstrained models), vetoing unbuildable `99`-score React apps (`0.047` vs. `0.851` when buildable) while `P0` checks blocked `0.705`-scoring unsafe apps, and completing live Render deployment + `5/5` security-header smoke checks + post-service GitHub Actions CI/CD in **`82 s`**.

Tension with "DON'T: Equate test execution pass rate (TPR) with mock contract fidelity or allow agents to relax interaction assertions during repair" (agent-evaluation-quality.md): in `MockBench` (`arXiv:2610.14629`), coding agents author or edit unit tests inside their own workspace and game execution pass rates (`TPR`) by omitting mock assertions or relaxing `times(N)` to `atLeastOnce()`, whereas `ProdPilot` (`arXiv:2611.17381`) keeps all `50` AST/config/entropy checkers frozen inside the zero-LLM MCP server outside the IDE agent's editable file boundary—rejecting `25/237` (`10.5%`) false-success claims and reverting any edit that regresses a passing rule.

Tension with "DON'T: Let the model author raw diffs or full rewrites for declarative manifests" (agent-sandbox-safety.md): for single-field updates inside existing YAML/GitOps manifests (`KubeAstra`, `arXiv:2609.00227`), constrain the LLM to emit semantic `(target_file, resource, field_path, target_value)` tuples applied by a deterministic CST span editor; for project-wide operational readiness across source and config files (`ProdPilot`, `arXiv:2611.17381`), eliminate the LLM completely on the `88.0%` of rules (`93.5%` of real-world violations) solvable via anchored static templates or ambiguity-refusing parametric extraction, and restrict client-agent edits to the `12.0%` (`6/50`) architecture-dependent rules inside an explicit file-boundary constraint contract gated by author-blind checker re-verification and full-suite regression revert.

See also "DO: Keep deterministic steps in code and explicit graph edges; delegate to LLMs only for reasoning" (this file), "DON'T: Gate post-migration code repairs on typical inputs, repairer self-tests, or LLM-filtered legacy-binding assertions" (agent-evaluation-quality.md), and "DO: Compile LLM-authored UI behavioral constraints into deterministic static dataflow queries instead of prompting LLMs to review frontend code directly" (agent-evaluation-quality.md).

> Source: ProdPilot: A Layered Model Context Protocol System for Automated Production Readiness and Deployment of Vibe-Coded Projects (arXiv:2611.17381)

### DO: Pair progressive BM25 manual tools with five orthogonal sync-async execution primitives, step-atomic cycle holds, and console-history injection for live stateful engines

When connecting LLM agents via `MCP` to live, stateful simulation, CAD/CAE, or scientific computing engines (`PFC`, `FLAC`, `3DEC`, `YADE`, FEM/CFD, robotics) where runs span minutes to hours in-memory and coexist with a human engineer's GUI/console, avoid both per-command schema dumps (`1,000+` tools) and rigid workflow-bundled tools (`76`-tool `COMSOL-MCP`). Split the integration into a stateless `7`-tool `MCP` server talking to a persistent stdlib HTTP bridge inside the live engine process:
1. **`2` Zero-Embedding Documentation Tools (`query` + `browse`)**: Index vendor manuals (`240K+` tokens) with pure-Python field-weighted `BM25` (`name > keywords > description`, top-`10` 1-line summaries) paired with `3`-level hierarchical `browse` (`category -> command list -> full spec`, returning parent sibling lists on invalid paths), cutting full-session manual reads to **`< 3%`** of the corpus while preventing API-hallucination failures.
2. **`5` Orthogonal Sync/Async Primitives with Step-Atomic Cycle Holds**: Expose only `execute_code` (foreground micro-trials **and** live mid-solve inspection), `execute_task` (non-blocking background submission), lock-free `check_task_status` (reading a persistent task registry without queueing behind compute), `interrupt_task`, and `list_tasks`. Synchronize live `execute_code` calls at a **single-timestep `cycle hold` barrier** (auto-re-registered across `reset`/`restore` commands) to prevent cross-timestep "rolling-shutter" read tearing, and implement `interrupt_task` by setting the C++ solver's native pause flag inside the step callback while raising Python exceptions **only after** the C++ step loop exits.
3. **Bidirectional human `console history` injection**: Append any commands typed by the human modeler at the engine console since the previous call to the next `MCP` tool return so the agent distinguishes benign human reads from destructive mid-session `restore`/`reset` actions without human copy-paste relaying, while confining `execute_code`/`execute_task` to loopback/sandboxed environments (`agent-sandbox-safety.md`) and gating persistent skill/template updates via "DO: Pass every self-modification through one acceptance gate" (`recursive-improvement.md`). Procedure: [`shared-console-async-simulation-mcp`](../skills/shared-console-async-simulation-mcp/SKILL.md).

**Scope:** `itasca-mcp` (`PFC 7.0`, `FLAC`, `3DEC`, `MPoint`, `MassFlow`; `241,283`-token `PFC` manual) and `yade-mcp` (`YADE` background-compute + Qt-GUI engine) evaluated on dense Toyoura sand drained triaxial DEM calibration (`5,000` spheres, `4` contact parameters, `3` targets $E_{50}, q_{\mathrm{peak}}, D$, budget `12` tasks / `8 h`) across interactive `PFC` human–agent coexistence trials, `PFC`/`YADE` `Claude Opus 5.5` runs, **`21` autonomous `YADE` sessions (`7` frontier/open-weight models $\times$ `3` runs in `OpenCode 1.19.3`)**, and `Qwen3.5-4B` CPU CI tests (`arXiv:2611.33926`).

**Evidence**:
- **`2.7%` manual token footprint & `20/21` (`95.2%`) multi-model autonomous calibration (`arXiv:2611.33926`, `Tables 3, 7–9`)**: `query -> browse` retrieved full command specs in **`3,381` tokens (`1.40%` of the `241,283`-token `PFC` corpus; `4,291` / `1.78%` via `browse`)**, and a complete `5`-iteration `PFC` calibration (`J = 0.79`) consumed **`6,536` command-corpus tokens (`2.7%`; `12,882` total doc tokens across `12` calls)** while `18` `execute_code` micro-trials caught **`5/5`** syntax/API errors before task `1`. Across `21` autonomous `YADE` sessions (`Claude Opus 5.5`, `GPT-6.1-sol`, `Gemini 4 Argon`, `Qwen3.8-max-0902`, `DeepSeek-V4-Pro`, `DeepSeek-V4.1-Flash-1017` all `3/3` at `$0.10–$1.99`/session; `Kimi K3` `2/3`), **`20/21` (`95.2%`)** reached $J \le 1$ (`19/21` inside one physical basin spanning `15%–38%` of admissible ranges); **`14/21` inspected running solves live via `execute_code`** (producing bit-identical stress–strain curves under `cycle hold`), **`8/21` (`5` models) aborted bad runs mid-solve** via `interrupt_task` (catching `0` wall velocity, inverted stress signs, and `1.85` coordination numbers early), and **the sole failed session (`Kimi K3` run `2`, $J = 1.31$, `5/12` API-error task losses) was the only session (`1/21`) that never called `query` or `browse`**.
- **Unannounced human console `restore` recovery (`§3.2`, `Fig. 7`, `Table 7`)**: Via injected `console history`, the agent ignored a benign mid-session human `ball list` query (`0` disruption) and detected an unannounced destructive `model restore` between iterations `3` and `4`—auditing iterations `2–3` curves and cycle counters via `execute_code` and adding an active cycle-counter integrity check to iteration `5`'s shear script (`note`: `Fig. 7` prints `J = 40` for failed servo iteration `1`, whereas `Table 7` marks it `invalid, lateral stress off target`).

Tension with "DO: Annotate Code Mode tool stubs with explicit return-value shapes and bound router fallbacks rather than stacking front-door routers on strong coders" (this file) and "DO: Pre-inject deterministic analyzer outputs for open-weight models and resolve domain aliases server-side rather than exposing raw ISO-code MCP arguments" (this file): two-meta-tool `Code Mode` (`search() + execute()`, `arXiv:2611.19123`) targets fast, stateless tool catalogs and prompt `inject` (`arXiv:2611.19439`) targets bounded deterministic text analyzers on `<= 27B` checkpoints, whereas multi-hour stateful C++/GUI physics engines (`arXiv:2611.33926`) require separating synchronous `execute_code` from background `execute_task`, lock-free `check_task_status`, step-boundary `interrupt_task`, and `BM25` + `browse` progressive manual lookup (`95.2%` autonomous calibration across `7` models).

Tension with "DO: Suspend multi-minute external operations using `LongRunningFunctionTool`" (adk-workflow-architecture.md): `LongRunningFunctionTool` suspends the entire agent node until an opaque external batch job finishes (`0` LLM tokens while waiting), whereas in exploratory scientific/CAE simulation (`arXiv:2611.33926`), keeping `execute_code`, `check_task_status`, and `interrupt_task` live *during* `execute_task` lets the agent inspect micro-mechanical state at cycle-hold barriers (`14/21` sessions) and abort diverged boundary conditions early (`8/21` sessions) rather than waiting hours for a failed solve. See also "DON'T: Let the human become the transport layer between agents" (agent-human-interaction.md) and "DON'T: Poll global backend quiescence to close a session or screen status endpoints only on idle backends" (agent-sandbox-safety.md).

> Source: Connecting AI Agents to Live Discrete Element Simulations via the Model Context Protocol (arXiv:2611.33926)

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
- [`google-adk`](../skills/google-adk/SKILL.md) ([`orchestration-patterns.md`](../skills/google-adk/references/orchestration-patterns.md)) — Three pillars of agent orchestration (Graph, Collaborative, Dynamic)
- [`capability-matched-skill-adaptation`](../skills/capability-matched-skill-adaptation/SKILL.md) — Adapting skill text across executor capability bottlenecks
- [`decoupled-interface-action-repair`](../skills/decoupled-interface-action-repair/SKILL.md) — Decoupled semantic commitment and interface-specific realization repair
- [`composite-skill-vulnerability-scanner`](../skills/composite-skill-vulnerability-scanner/SKILL.md) — Dependency-graph static/LLM auditing and sandbox-verified repair for local and cross-skill composite vulnerabilities
- [`contrastive-meta-skill-harness-evolution`](../skills/contrastive-meta-skill-harness-evolution/SKILL.md) — Offline contrastive meta-skill precomputation paired with bounded online harness evolution (`Meta^2`)
- [`counterfactual-tool-dependency-induction`](../skills/counterfactual-tool-dependency-induction/SKILL.md) — Counterfactual sandbox verification of tool dependency graphs with 1-hop top-2 retrieval (`LIBRA`)
- [`verified-telemetry-tool-routing`](../skills/verified-telemetry-tool-routing/SKILL.md) — Host-verified Substrate State Telemetry (`SST`) projection and operational tool routing
- [`mcp-hallucination-boundary-guards`](../skills/mcp-hallucination-boundary-guards/SKILL.md) — Pre-execution feasibility gates, confusion-tool isolation, and transactional state ledgers for MCP agents
- [`two-phase-framework-ui-codegen`](../skills/two-phase-framework-ui-codegen/SKILL.md) — Compatibility-ordered two-phase LoRA tuning and relationship-gated adapters for multi-framework UI codegen
- [`feedback-poisoning-skill-promotion-guard`](../skills/feedback-poisoning-skill-promotion-guard/SKILL.md) — Four-gate defense against reference-feedback backdoor poisoning in text-space skill optimization (`SkillOpt`)
- [`hybrid-sandbox-skill-intent-audit`](../skills/hybrid-sandbox-skill-intent-audit/SKILL.md) — Three-layer static, safety-constrained sandbox dry-run, and agentic SARIF skill intent audit
- [`tiered-contract-readiness-gate`](../skills/tiered-contract-readiness-gate/SKILL.md) — Zero-LLM MCP readiness remediation split into static, ambiguity-refusing parametric, and checker-bound delegated contracts with ordered release gating (`ProdPilot`)
- [`regret-guided-continual-harness-evolution`](../skills/regret-guided-continual-harness-evolution/SKILL.md) — Signature-keyed continual playbook gating with paired directional regret and one-pass `[iff]` scope guards (`GUARD`)
- [`asynchronous-system1-harness-evolution`](../skills/asynchronous-system1-harness-evolution/SKILL.md) — Past/present/future (`state`/`proc`/`wm`) harness module routing with `L=3` consecutive-loss quarantine (`JevRSI`)
- [`tool-implementation-grounded-skill-revision`](../skills/tool-implementation-grounded-skill-revision/SKILL.md) — AST-indexed script contract extraction, trace alignment, and bounded `<= 4`-substring `SKILL.md` patching without task verifiers (`VISE`)
- [`anti-leakage-sparse-feedback-memory-distillation`](../skills/anti-leakage-sparse-feedback-memory-distillation/SKILL.md) — Verdict-anchored contradiction/error write routing paired with Turn-0 API-names-only cues and on-demand pitfall retrieval (`ZhuLong-SE`)
- [`dual-role-model-harness-coevolution`](../skills/dual-role-model-harness-coevolution/SKILL.md) — Shared-weight `Improver`+`Solver` `GRPO` co-evolution for domain skills and SQL views (`MedicalRSI`)
- [`shared-console-async-simulation-mcp`](../skills/shared-console-async-simulation-mcp/SKILL.md) — `7`-tool MCP server (`query` + `browse` BM25 manual progressive disclosure + `5` sync/async primitives), step-atomic `cycle hold` inspection, and human `console history` coexistence for live simulation engines

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
- When Feedback Becomes a Backdoor (SkillOpt Reference-Feedback Poisoning): arXiv:2611.09348
- The Devil Wears Markdown (Hybrid Static, Dynamic & Agentic Skill Intent Audit): arXiv:2611.10830
- Is Recursive Self-Improvement Safe?: arXiv:2611.10261
- SceneAgent (Multi-Agent Framework for Portable Game Scene Generation): arXiv:2611.17821
- ProdPilot (Layered Zero-LLM MCP Server for Production Readiness & Deployment): arXiv:2611.17381
- SecCARD (A2A Agent Card Discovery Validation, cited from adk-security-and-evaluation.md): arXiv:2611.18887
- Agent-ZTA (Bidirectional Security-State Propagation, cited from multi-agent-coordination.md): arXiv:2611.18999
- Beyond Plain MCP (Code Mode, Return-Shape Stubs & Decision Routers): arXiv:2611.19123
- ToolPulse (Online Cueing, Spotting & Detour-vs-Outcome Gap): arXiv:2611.19275
- Rule-Based Linguistic Tools in Prompt vs over MCP: arXiv:2611.19439
- ConvRSI (From Recursion to Convolution: Parallel Self-Improvement for Multi-Agent Systems): arXiv:2611.20891
- Procedure without Judgment (cited from recursive-improvement.md): arXiv:2611.21529
- Harnesses That Improve Themselves (Unifying Framework for Self-Improving Agent Harnesses): arXiv:2611.22299
- JevRSI (cited from recursive-improvement.md): arXiv:2611.22432
- GUARD (cited from recursive-improvement.md): arXiv:2611.23476
- CompAct-Bench (Working-Context Compaction Timing & Epistemic State Distortion): arXiv:2611.25673
- LLM Agent Authorization Across Context Compaction (cited from agent-sandbox-safety.md): arXiv:2611.32194
- FinVeriQA (cited from agent-evaluation-quality.md): arXiv:2611.25071
- VISE (Verifier-Independent Skill Self-Evolution with Feedback from Tool Implementations): arXiv:2611.32480
- ZhuLong-SE (Self-Evolving Beyond Human-Crafted Experience for EDA Scripting): arXiv:2611.26912
- MedicalRSI (cited from recursive-improvement.md): arXiv:2611.26806
- SelfWrite (cited from recursive-improvement.md): arXiv:2611.29513
- Connecting AI Agents to Live Discrete Element Simulations via MCP (`itasca-mcp` & `yade-mcp`): arXiv:2611.33926
- Chasm (cited from multi-agent-coordination.md): arXiv:2611.34278

