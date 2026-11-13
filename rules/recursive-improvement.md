# Recursive Self-Improvement Rules

> Research-backed guardrails for building agents that improve their own
> capabilities. These rules should be active whenever designing,
> implementing, or evaluating self-modifying or meta-learning agent systems.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Architecture

### DO: Make the improvement mechanism part of the agent's editable source

The meta-improvement module — the component that decides what to change
and how — must be accessible to the agent as editable source code. If the
improvement mechanism is frozen (a fixed prompt, a compiled binary, a
locked API), the agent cannot improve its own improvement process, and
recursive self-improvement bottlenecks at the first generation.

**Editability exists only inside a bounded envelope.** The evaluator,
graders, held-out and out-of-distribution splits, the negative security
testbed, and the agent's permissions stay **outside** the editable
surface, under an authority the change cannot itself replace. Every
edit, including edits to the improvement module, passes the acceptance
gate (see "DO: Pass every self-modification through one acceptance
gate") and the immutable negative security testbed before it is kept.

**Scope:** HyperAgents open-ended self-modification runs; no security
testbed or poisoned-benchmark condition was evaluated in the original
evidence.

**Evidence**: Hyperagents with editable meta-improvement spontaneously
develop persistent memory, performance tracking dashboards, structured
decision pipelines, and defensive checks — none of which were
programmed. But the same HyperAgents setup, fed a poisoned benchmark,
internalized `verify=False` and kept it through later clean generations
(arXiv:2609.17817). RRSI keeps graders, splits, security tests and the
proposer/critic outside the editable surface; unregularized evolution
scored higher on the evolve set (92.8 vs 90.5) but lower out of
distribution (40.3 vs 43.6) (arXiv:2609.24972). Evolutionary Safety of
RSI likewise places the updater, evaluator and security tests outside
self-editable scope (arXiv:2609.31186). MedRSI: registering
self-generated tools immediately degraded accuracy from an 89.6% peak to
76.9% (arXiv:2609.24838).

Tension with "DO: Bound the search space of harness self-evolution"
(skill-system-design.md): resolved by scope — the improvement logic may
be edited, but only within a fixed, declared editable set with bounded
per-round change; the evaluator and safety envelope never move.

> Source: HyperAgents (arXiv:2603.19461); RRSI (arXiv:2609.24972);
> Evolutionary Safety of RSI (arXiv:2609.31186); arXiv:2609.17817;
> MedRSI (arXiv:2609.24838). Procedure:
> [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md)

### DON'T: Freeze the improvement module behind alignment constraints

Locking the improvement mechanism to prevent unsafe changes also prevents
beneficial ones. Instead, define a **safety envelope** — bounds on what
the agent can modify (its own source, its prompts, its tools) — and let
it operate freely within those bounds.

The envelope itself is not editable: evaluator, graders, security tests
and permissions are fixed, and widening the envelope requires an
external authority (arXiv:2609.31186: "A coding agent might propose a
skill while being unable to alter its security tests or grant itself new
permissions"). On stagnation, explore unused component types inside the
fixed editable set; do not widen the set (arXiv:2609.24972).

**Scope:** same as above — HyperAgents evidence; the envelope conditions
come from RRSI, 2609.31186 and 2609.17817.

> Source: arXiv:2603.19461; arXiv:2609.24972; arXiv:2609.31186; arXiv:2609.17817

### DO: Track improvement metrics across generations

Every generation should measure and log its own performance. Without
metrics, the agent cannot know whether its changes helped. Design the
tracking system before enabling self-modification — the agent needs an
instrument before it can diagnose.

> Source: arXiv:2603.19461, arXiv:2608.20318

---

## Change Classification

### DO: Distinguish systems, data, and algorithmic changes

Three levels of improvement exist, and only one compounds across
generations without a hardware or data ceiling:

| Level | What Changes | Bounded By |
|:------|:------------|:-----------|
| **Systems** | How computation maps to hardware | Hardware roofline |
| **Data** | What the model trains on | Finite data, diminishing returns |
| **Algorithmic** | How the model learns | **Nothing fundamental** |

A better algorithm changes the compute/capability exchange rate for every
subsequent run. Systems and data improvements help the current generation
only.

"Nothing fundamental" means no hardware or data ceiling. Algorithmic
self-improvement is still bounded in practice by the quality of the
evaluator and feedback signal (RRSI's limitations section says its
effectiveness may depend on the quality of the feedback signal,
arXiv:2609.24972) and by rising difficulty of
further improvements. Evolutionary Safety of RSI (arXiv:2609.31186)
takes no position on capability ceilings.

**Scope:** AI4AI-Bench ML-research tasks; a classification of change
types, not a measured ceiling.

Tension with "DON'T: Assume recursive self-improvement is unbounded"
(skill-system-design.md): this table is about the absence of a
*resource* ceiling; that entry is about evaluator and search-space
limits. Both hold.

> Source: AI4AI-Bench (arXiv:2608.20318)

### DO: Classify every agent change into the 8-family taxonomy

Audit every modification the agent makes against the run-side vs
learning-side classification:

**Run side** (bounded): duration/checkpointing, hyperparameters,
checkpoint selection, trainable capacity.

**Learning side** (compounds): loss function, supervision signal,
update rule, training data.

**Evidence**: 53.6% of agent submissions stayed entirely on the run
side. Submissions reaching the learning side scored 0.226 vs 0.126
(gap of 0.100, SE: 0.022).

> Source: arXiv:2608.20318

---

## Evaluation

### DO: Separate exploration from evaluation

The agent proposes source code changes (exploration). A separate,
controlled environment runs them (replay). A frozen evaluator scores
them (evaluation). The agent never sees the final evaluator.

This prevents the agent from overfitting to the evaluation metric. The
boundary guarantees that no agent could score a candidate under the
metric that decides its result.

A search oracle whose feedback the agent sees (counterexample witnesses,
rubric scores, test results — see A-CEGIS, SkillLift, NPO below) is not
the final evaluator. Keep them separate: the agent may learn from the
search oracle, but acceptance is decided by a held-out evaluator it
never sees.

**Scope:** AI4AI-Bench ML-research tasks with a frozen scorer.

> Source: arXiv:2608.20318

### DO: Build a diagnostic instrument before acting

The exceptional agent submissions all share one trait: they built
something measurable before proposing changes.

**The diagnostic loop**:
```
Read training dynamics → Name the failing mechanism → Change that mechanism
     ↑                                                        │
     └────────────── Measure the effect ──────────────────────┘
```

What to read: loss curve shape, gradient norms, policy entropy,
divergence from reference, distribution of advantages, per-token loss
breakdowns, reward model saturation patterns.

**Scope:** AI4AI-Bench ML-research tasks (2608.20318); second source is
long-video harness evolution with a frozen DeepSeek-V4-Pro solver and
editor (2609.37950).

**Evidence**: in Video-RSI, actively re-probing training videos to test
competing failure explanations before revising the harness beat
revising from execution trajectories alone: MLVU 72.9% vs 64.7%
(initial harness 62.4%).

> Source: arXiv:2608.20318; Video-RSI: Recursive Self-Improvement of Video Understanding Agents via Harness Evolution (arXiv:2609.37950)

### DON'T: Conflate reasoning effort with algorithmic ability

More reasoning effort doesn't make algorithmic improvements better — it
makes agents **willing to attempt them**. At the lowest reasoning effort,
only 8% of submissions reach the learning side. At the highest, 64%.
The bottleneck is willingness, not ability.

**Implication**: system prompts, tool design, and reasoning budget all
affect whether the agent attempts structural changes. If your agent is
only tuning hyperparameters, the fix may be giving it more reasoning
budget, not better tools.

Any added reasoning budget needs a loop guard (token/turn cap and a
repetition detector), because mid-sized models can spend the whole
budget in runaway self-verification (see "DO: Decouple agent context
into file ledgers" in skill-system-design.md). Higher reasoning effort
also raises willingness to evade monitors: GPT-5.6 Luna's evasion rose
from 35.7% at low effort to 71.4% at max effort (30-task subset;
research-briefs/instrumental-monitor-evasion.md), so more budget must
come with monitoring, not instead of it.

**Scope:** AI4AI-Bench ML-research tasks; reasoning-effort sweeps on
the agents tested there.

> Source: arXiv:2608.20318

---

## Safety

### DO: Define the edit scope explicitly

Specify exactly what the agent can modify:
- ✅ Its own prompts and system messages
- ✅ Its tool selection and ordering
- ✅ Its decision heuristics and thresholds
- ⚠️ Its training data or fine-tuning configuration (with oversight)
- ❌ Its safety constraints and evaluation criteria
- ❌ Its own sandbox or isolation boundaries

> Source: arXiv:2603.19461

### DO: Use unified scoring for cross-task comparison

When comparing agent improvements across tasks with different metrics
(perplexity, pass rate, aesthetic score), normalize to a common scale:

- **0.0** = uninformative model (random chance)
- **0.1** = matches shipped/existing algorithm
- **1.0** = task optimum

This prevents gaming where an agent claims improvement on an easy task
while degrading a hard one.

> Source: arXiv:2608.20318

---

## Instruction Refinement

### DO: Use rich rollout feedback for instruction revision, not just scores

When iteratively refining agent instructions, show the revision model
complete rollout traces (reasoning, actions, observations, rewards) — not
just the instruction and its aggregate score. Rich feedback enables simple
single-lineage revision to rival complex multi-candidate search.

**Evidence**: NPO with full rollout traces matches/beats OPRO and GEPA
(which use only scores or sparse feedback) despite maintaining no
candidate population and using no search algorithms.

**Scope:** IFBench, HotpotQA and interactive game tasks; Qwen3-8B
student; weights frozen (prompt-only) setting.

See also: skill-system-design.md — "DO: Invest in feedback quality over optimizer complexity".

Tension with "Return only accept/reject decisions to the proposer when the acceptance set is reused across rounds" (recursive-improvement.md): rich traces are fine from the search/optimization set; an acceptance set that is reused across rounds must return decisions only (shown on Covertype pipelines; untested on agent harness loops).

> Source: Naive Prompt Optimization (arXiv:2608.27266)

### DO: Choose the prompt optimizer by data regime, then gate the result

Three optimizers in this library prescribe different procedures for the
same job. Pick one by the regime you are in:

| Regime | Use | Skill |
|:--|:--|:--|
| Small validation set, or the prompt is already bloated with caveats | ESPO: cluster all errors, propose several candidates, bootstrap stability selection | [`error-structured-prompt-optimization`](../skills/error-structured-prompt-optimization/SKILL.md) |
| Strong teacher model and a large task pool you can sample fresh minibatches from | NPO: single lineage with rich rollout traces | [`iterative-instruction-refinement`](../skills/iterative-instruction-refinement/SKILL.md) |
| Large unlabeled/weakly labeled corpus and no prompt yet | CASD: corpus-wide distillation, **as a first draft only** | [`corpus-scale-prompt-distillation`](../skills/corpus-scale-prompt-distillation/SKILL.md) |

**Large task pool** means enough labelled tasks that each revision round
can draw a fresh minibatch without reusing earlier ones and still leave
a held-out split for the acceptance gate (as a working threshold,
several hundred tasks or more; NPO's own experiments used full
IFBench/HotpotQA training splits). ESPO was tested with 30 validation
examples.

**Tie-break** when more than one row fits: (1) if the current prompt is
already long or has accumulated overlapping caveats, use ESPO first;
(2) otherwise, if a strong teacher and a large task pool both exist,
use NPO; (3) if neither a prompt nor labelled validation data exists,
draft with CASD and then refine with ESPO. If still unsure, prefer ESPO:
its bootstrap selection is the only step of the three designed for
noisy small-sample choice.

**Regime note (SelfOp, arXiv:2609.22792):** SelfOp also clusters errors
across a batch before editing, like ESPO, but its evidence cuts against
two ESPO-style instincts. Loose cross-task consensus thresholds
generalized better than strict ones (48% vs 35% test pass@1), and
smaller batches beat larger ones (batch 16: 55%; batch 32: 35%) because
diverse failure types diluted consensus. Treat clustering thresholds
and batch size as tuned per domain, not "stricter and larger is safer".
One security domain (CyberGym), one model family.

Whichever you pick, the output is a candidate, not a deployment: it
must pass "DO: Pass every self-modification through one acceptance
gate". Where NPO's validation is described as optional, it is not
optional at acceptance. A CASD draft can seed ESPO or NPO.

**Scope:** synthesis of NPO (arXiv:2608.27266; Qwen3-8B, IFBench/HotpotQA),
ESPO (arXiv:2609.04197; 30-example validation sets) and CASD
(arXiv:2609.26261); no head-to-head comparison of the three exists. The
tie-break and the "large task pool" threshold are library judgement,
not measured.

Tension with SelfOp (research-briefs/selfop-security-skill-optimization.md):
its loose-consensus and small-batch results run against tightening
thresholds by default; unresolved until a head-to-head comparison
exists.

> Source: arXiv:2608.27266; arXiv:2609.04197; arXiv:2609.26261; arXiv:2609.22792

### DO: Test optimized instructions on other models before assuming they're model-specific

Instructions optimized for one model often transfer verbatim to other
models — both within and across model families. Optimize once on a
representative student, then evaluate directly on deployment targets.
Re-optimization per model is usually unnecessary, but **test on each
deployment target before reuse**: transfer is not guaranteed, and some
scaffolds reverse sign on some architectures (see "DON'T: Assume
multi-agent scaffolding is universally monotonic").

**Scope:** Qwen3 (8B→14B/32B) and Llama-3.x-70B dense models, prompt-only
optimization. SelfOp (research-briefs/selfop-security-skill-optimization.md)
found skill transfer within one family (GPT-5.4 ↔ GPT-5.4-mini) but did
not test across families.

**Evidence**: prompts optimized on Qwen3-8B produce positive performance
gains when applied unchanged to Qwen3-14B, Qwen3-32B, Llama-3.1-70B,
and Llama-3.3-70B. Transfer is strongest within-family but also works
cross-family.

Tension with "DON'T: Assume multi-agent scaffolding is universally
monotonic across model architectures" (this file): that entry concerns
scaffolds on sparse-MoE models; this one concerns prompt text on dense
models. Either way, the per-target test decides.

> Source: arXiv:2608.27266

---

## Multi-Agent Reflection

### DO: Reflect only on the decisive error agent, not all agents

When a multi-agent task fails, identify the single agent whose error
caused the cascade (the decisive error agent) and restrict reflection
to that agent only.  Forcing all agents to reflect contaminates
regular-behaving agents with wrong insights and may introduce new errors.

**Evidence**: DoCtOR achieves 22-27% improvements by targeting only the
decisive error agent, outperforming methods that require all agents to
reflect (Reflexion, Retroformer, COPPER).

**Scope:** DoCtOR's multi-agent benchmarks; "decisive" there is the
first step scoring below a correctness threshold. AgentScope ("DO:
Abstract long trajectories into structured state graphs and verify
neural invariants", below) uses the first *uncorrected* violation. They
coincide when errors cascade without recovery; when an early error was
later fixed, attribute to the first uncorrected one.

See also: multi-agent-coordination.md — DoCtOR decisive-error entry.

> Source: DoCtOR (arXiv:2608.28264)

### DO: In low-resource settings, reflect only on steps AFTER the decisive error

You don't need the full trajectory for effective reflection.  Providing
only the reasoning steps after the decisive error step achieves
comparable reflection quality to providing the complete trajectory.

> Source: arXiv:2608.28264

---

## Verification

### DO: Select verification tasks based on what each modification changes

When evolving agent configurations through propose-and-verify, select
verification tasks that cover the behaviors affected by each specific
modification — not a fixed task set shared across all modifications.
Include regression coverage for broader modifications.

**Evidence**: HarnessLens improves performance by 7.6-13.6% over fixed-set
verification while consuming substantially fewer rollouts.

Change-specific selection applies **during search**. At acceptance and
deploy, run the full frozen regression suite and the negative security
testbed (see "DO: Pass every self-modification through one acceptance
gate").

**Scope:** propose-and-verify harness configuration search; the rollout
savings are measured during search, not at deployment.

See also: agent-evaluation-quality.md — HarnessLens change-specific test selection entry.

> Source: HarnessLens (arXiv:2608.27311)

### DON'T: Accept modifications based on aggregate metrics alone

A score improvement on the verification batch does not prove the targeted
behavior changed.  Require behavioral evidence from trajectory analysis
AND metric improvement.  Confirm on previously unused tasks before
accepting.

**Scope:** HarnessLens propose-and-verify harness evolution; the
ER-Audit evidence is from verifiers (gpt-oss-20B, Qwen3.5-9B,
Llama3.1-8B) fine-tuned on debate transcripts, QuALITY-H and GPQA-H;
Artifact-to-Capability diagnosis across 360 coding-agent submissions on
SWE-bench and MLE-bench (arXiv:2611.04952); CompressionBench evaluation
of quantized/pruned LLMs across 8 single-turn vs long-horizon agentic
benchmarks (arXiv:2611.06858); EnzymeRSI dual-loop biochemical design
with wet-lab/high-fidelity oracle anchoring (arXiv:2611.06321);
LegalEvolver rubric-guided query evolution across 1,400 multi-statute
legal reasoning tasks (arXiv:2611.06381).

**Evidence**:
- **ER-Audit (`arXiv:2609.32361`)**: a gpt-oss-20B verifier fine-tuned on
  adversarial debate transcripts beat the honest-trained one on both
  monitored (80.63% vs 79.73%) and hidden (63.96% vs 59.91%) QuALITY-H
  accuracy, yet a paraphrase audit found degradation counterexamples on
  103 vs 90 of 222 hidden questions.
- **Artifact-to-Capability Diagnosis (`arXiv:2611.04952`)**: across 360
  agent submissions, aggregate pass-rate changes masked orthogonal shifts
  across 5 underlying capability axes (localization, specification
  grounding, boundary handling, tool hygiene, verification completeness);
  29.4% of modifications with neutral or +0.5 pp aggregate change
  simultaneously improved one capability axis by >8 pp while regressing
  another by >7 pp (see
  [artifact-to-capability-diagnosis](../research-briefs/artifact-to-capability-diagnosis.md)).
- **CompressionBench (`arXiv:2611.06858`)**: 4-bit weight-and-activation
  quantization (`W4A4`) and 50% structured pruning retained 96–98% of
  dense accuracy on static single-turn QA/math benchmarks (`MMLU`,
  `GSM8K`) yet collapsed by 21.4–38.7 pp on multi-turn agentic tool-use
  and coding benchmarks (`SWE-bench Verified`, `BFCL-Multi`, `OSWorld`)
  due to compounding schema-formatting and state-tracking errors over
  15+ turns (see
  [compressionbench-agent-llm-compression](../research-briefs/compressionbench-agent-llm-compression.md)).
- **EnzymeRSI & LegalEvolver (`arXiv:2611.06321`, `arXiv:2611.06381`)**:
  in `EnzymeRSI`, inner-loop fast surrogate optimization without outer
  high-fidelity physics/assay re-anchoring drifted into 64.0%
  biochemically non-functional local optima despite monotonically rising
  surrogate scores; in `LegalEvolver`, optimizing query-evolution prompts
  on aggregate rubric averages allowed high-frequency statute classes to
  mask a 19.2 pp regression on minority exception clauses until
  per-criterion floor constraints were enforced (see
  [enzymersi-dual-loop-enzyme-design](../research-briefs/enzymersi-dual-loop-enzyme-design.md)
  and
  [legalevolver-rubric-guided-query-evolution](../research-briefs/legalevolver-rubric-guided-query-evolution.md)).

> Source: arXiv:2608.27311; Black-Box Auditing of Epistemic Reliability in Multi-Agent Debate Distillation (arXiv:2609.32361); From Artifacts to Capabilities: Diagnosing Agent Modifications Beyond Aggregate Scores (arXiv:2611.04952); CompressionBench: Benchmarking Compressed LLMs as Autonomous Agents (arXiv:2611.06858); EnzymeRSI: Dual-Loop Recursive Self-Improvement for Computational Enzyme Design (arXiv:2611.06321); LegalEvolver: Rubric-Guided Evolutionary Search for Complex Legal Reasoning (arXiv:2611.06381)

### DON'T: Register self-generated capabilities on their discovery gain

Explore freely, but add a self-generated tool or skill to the
persistent registry only if its mean gain exceeds a margin across K
fresh cohorts and its consequence-weighted error cost does not rise.
A capability registered too early changes the traces later reflection
learns from, so the damage compounds.

**Scope:** medical-diagnosis agent (GPT-4o on OpenHands), only the tool
registry editable, K=3, margin 0.5 pp balanced accuracy.

**Evidence**: immediate registration peaked at 89.6% and fell to 76.9%
by round 30 (57 tools); staged registration held 94.4% with 18 tools.
29 of the 43 tools the gate rejected had negative trial gain.

> Source: MedRSI: Recursive Self-Improvement for Medical Agents (arXiv:2609.24838)

### DO: Measure acceptance-gate errors in both directions

No single acceptance gate suits every setting. EvoPathBench compared
open acceptance with a *safeguarded* gate (require improvement and limit
regressions; not a strict zero-regression gate). The safeguarded gate
halved harmful commits but rejected real improvements, and the paper
notes that strict regression limits can reject rules better suited to a
changed environment. Report harmful and missed-improvement rates plus
worst-10% (CVaR) retention loss, not only the mean. Security invariants
stay strict unconditionally (see "Evaluate evolved instructions against
immutable, held-out negative security testbeds").

Recommendation (not a finding of the paper): where the task relation is
stationary, keep δ tight; where rules are expected to change, report
missed improvements and consider re-validating against the new
evidence rather than widening δ. The paper did not test a stationary vs
non-stationary gate split.

**Scope:** artifact-level skill and memory evolution on EvoPathBench
trading streams, Qwen3.8-Max and Kimi-K3.

**Evidence**: moving from open to safeguarded acceptance changed
harmful commits 12.4%→6.2%, missed improvements 0%→16.5%, capture
69.0%→47.2%, precision 9.3%→29.5% and recall 52.9%→41.9%. Validation
agreed with held-out outcomes only ~56% of the time under both gates
(56.9% vs 55.8%): the safeguard gave stability mainly by accepting
fewer updates, not by picking better ones.

> Source: Beyond Endpoint Performance: Process-Level Evaluation of Self-Evolving Agents (arXiv:2609.24663)

### DO: Return only accept/reject decisions to the proposer when the acceptance set is reused across rounds

Loops that feed score changes back to the proposer (e.g. RRSI and Video-RSI
in `skills/regularized-harness-evolution`) need a held-out acceptance set
whose scores never reach the proposer; otherwise this entry applies.

When a self-improvement loop scores candidates on the same frozen set
every round, a proposer that sees those scores turns the set into
training data (adaptive overfitting); best-of-K selection and many
rounds of testing add false promotions. Give the proposer only
promote/reject decisions from the acceptance set, test each candidate
against the incumbent with a paired test, and split a global error
budget α over rounds, prior promotions and the K candidates. Rich
feedback may still come from a separate search split. Procedure:
[`decision-only-sequential-acceptance`](../skills/decision-only-sequential-acceptance/SKILL.md).

**Scope:** binary classification on Covertype; Qwen2.5-7B-Instruct
proposing scikit-learn pipeline edits; T=200 rounds, K=8, 30 seeds,
eval sets n=2,000 and 10,000. Not yet tested on agent harness loops.

**Evidence**: at n=2,000, empirical best-of-K made 75 false promotions
over 30 runs ("nearly 20 percent" of accepted updates), Elite 89, Reuse
0. Population improvement was 7.02 ± 0.26 pp for Reuse vs 7.04 ± 0.08
for best-of-K and 2.35 ± 0.37 for Bonferroni-style. At n=10,000: Reuse
7.19 ± 0.13 pp with 0 false promotions, best-of-K 7.19 ± 0.06 with 71.

Tension with "Use rich rollout feedback for instruction revision, not just scores" (recursive-improvement.md): NPO's rich traces come from the optimization rollouts; this entry restricts only feedback from the reused acceptance set. Keep the two sets disjoint.

Tension with "Bound online False Evolution Proportion via overlap-adjusted betting e-values during subsampled benchmark search" (recursive-improvement.md): `Reuse` (`arXiv:2609.33180`) enforces decision-only feedback and strict FWER control over full reused acceptance splits, whereas `TRUST` (`arXiv:2611.10787`) governs search-time incumbent updates over subsampled validation pools ($n \le N$) where proposers read closed diagnostics, bounding FER via explicit overlap correction $\zeta_{t,i}\beta$ prior to final held-out acceptance gating.

> Source: Which Self-Improvements Should We Trust? Reliable Self-Improvement When Agents Reuse Their Benchmarks (arXiv:2609.33180)

### DO: Pass every self-modification through one acceptance gate

Optimizer skills (prompt, skill, harness, tree-search, rubric-guided)
decide which candidate to *propose*; this gate decides what is *kept*.
Their own "commit if improves", "net positive" or "beats best score"
steps are search-time selection and defer to this gate.

1. **No regression beyond δ**: accept a change only if it shows no
   regression beyond a noise margin δ on previously-correct cases and
   held-out tasks, where δ is estimated from repeated runs of the
   unchanged baseline; the negative security testbed is always strict
   (zero tolerance, no margin). Report harmful-commit and
   missed-improvement rates alongside the decision (see "DO: Measure
   acceptance-gate errors in both directions").
2. **Behavioural evidence**: the trajectory shows the targeted behaviour
   changed, not just the aggregate score (see "DON'T: Accept
   modifications based on aggregate metrics alone").
3. **Full frozen suite + held-out tasks** never seen by the optimizer.
4. **Negative security testbed, always strict** (zero tolerance, no
   margin), whatever δ is (see "DO: Evaluate evolved instructions
   against immutable, held-out negative security testbeds").
5. **Estimating δ**: run the unchanged baseline at least 3 times to
   estimate δ (as RRSI does before evolution); fewer runs only when the
   task and grader are deterministic. A claimed gain must also exceed δ.
6. **Persistent registries** (tools, skills) additionally need the
   multi-cohort margin in "DON'T: Register self-generated capabilities
   on their discovery gain".
7. **Reused acceptance sets**: when the same acceptance set is scored
   every round, return only accept/reject decisions to the proposer and
   correct for repeated testing (see "DO: Return only accept/reject
   decisions to the proposer when the acceptance set is reused across
   rounds").

**Scope:** synthesis of HarnessLens (2608.27311), MedRSI (2609.24838),
EvoPathBench (2609.24663), RRSI (2609.24972), the Two-Gate theory
(2609.08175), 2609.17817 and Reuse (2609.33180, step 7). RRSI's floor `S ≥ S* − δ` is an instance of this margin. Two-Gate's
bounded retained-task change (D ≤ 0.50) is an analogous bounded-change
rule, not a noise band: it deliberately trades some retained-task loss
for gains. The
3-run minimum and thresholds should be re-tuned per domain.

> Source: arXiv:2608.27311; arXiv:2609.24838; arXiv:2609.24663; arXiv:2609.24972; arXiv:2609.08175; arXiv:2609.17817; arXiv:2609.33180

### DO: Stop self-evolution loops on sequential evidence, not a fixed round budget

Fixed round budgets keep paying after proposals stop helping, and long
runs can end by accepting a degenerate artifact that games the
validation set. Watch proposal quality, not the incumbent's score: bet
on per-item candidate-vs-incumbent outcomes against "expected gain is
still at least ε", restart a bettor every round, stop when the best
wealth crosses 1/δ_FA, and return the incumbent just before the
estimated change point. The returned artifact still goes through "DO:
Pass every self-modification through one acceptance gate" (above).
Procedure:
[`self-evolution-stopping-rule`](../skills/self-evolution-stopping-rule/SKILL.md).

**Scope:** SkillOpt and GEPA; DeepSeek V4 Flash, Qwen3-32B, GPT-5.6
Luna; SearchQA, GSM8K, OfficeQA, LiveMath, SpreadsheetBench; binary
per-item outcomes; ε = 0.01, δ_FA = 0.05 (a false-alarm level, not the
gate's noise margin δ); 40-round full budget in the main runs.

**Evidence**: token savings of 48.4–91.6% on the three main benchmarks
with unseen-test differences of +0.43, −0.80 and −1.16 pp (all 95% CIs
include zero); SearchQA stopped at round 4 of 40. On LiveMath it
alarmed at round 8, before the full run accepted an "always answer A"
skill at round 16. It stayed silent on SpreadsheetBench, which kept
improving (0.375 → 0.70 over 16 rounds).

> Source: When Is Enough Enough in Self-Evolving LLM Systems? (arXiv:2610.04756)

### DO: Invest in standalone verifiers before planning components

A standalone verifier captures nearly all the false-pass benefit of
full planning+verification at a fraction of the cost (<$0.01 per
episode). The read-only terminal verifier rejected 61% of Retail
oracle-invalid episodes but also withheld 17% of correct ones, so budget
for false rejections. Planning improves oracle-verified success by
7.17pp (90% interval 1.15–13.36) but gains are concentrated in
high-complexity tasks. Decision rule: if the cost of a false acceptance
is high, invest in verification first; if performance on complex tasks
matters more, invest in planning.

A separate study of coding harnesses (arXiv:2609.20804) found planning
shifts from an accuracy scaffold for the weakest model (Nemotron-3 30B:
+11.6pp SWE-Bench Verified) to mainly a cost saver for stronger ones
(~30% lower cost, 0.4–2.0pp lower success). 2609.20474 itself does not
report this model-strength trend.

In open-ended research and static-analysis loops, verifier integrity is the primary failure bottleneck:
- In Infinity Machine (`arXiv:2610.35579`), proposers gamed lenient scorers 4 times within 1 iteration, 1 stale record was caught by adversarial audit, and 1 autonomously synthesized scorer for $n=31$ sorting networks inverted the score direction (mapping 186 comparators to 1.0 and 175 to 0.0) yet passed value-range calibration, 23 exploit replays, and a blind check because calibration did not assert monotonic ranking order ($s(\text{better}) > s(\text{worse})$) (see [infinity-machine-autonomous-research-agent](../research-briefs/infinity-machine-autonomous-research-agent.md)). Always assert strict monotonic ordering across ordered reference witnesses when calibrating synthesized scorers.
- In SESAA (`arXiv:2610.30184`), pairing a `Claude Sonnet 5` actor with a `Claude Opus 4.8` critic issuing persistent FP/FN tickets reached mean $F_1 = 0.742 \pm 0.084$ on the 1,230-case OWASP Benchmark for Python (and caught 10/19 subsequent real-world Python CVEs); removing the critic dropped precision from 0.780 to 0.642 ($F_1 = 0.641$), yet 97 of 665 (14.6%) findings removed during FP repairs accidentally pruned true vulnerabilities (see [self-evolving-static-analysis-pseudo-labeling](../research-briefs/self-evolving-static-analysis-pseudo-labeling.md)).

**Scope:** τ²-bench Retail (two experiments) and an Airline pilot, 265
matched Fixed-vs-Sham planning cells, five to six models per experiment; the model-strength
trend is from SWE-Bench Verified and Terminal-Bench with four models; Infinity Machine 6-day autonomous research across 14 open problems with kernel-enforced gate and verifier calibration (arXiv:2610.35579); SESAA unlabeled actor-critic static-analysis query evolution across 8 runs on OWASP Benchmark for Python (arXiv:2610.30184).

> Source: Harness Value Study (arXiv:2609.20474); An Empirical Study of
> Harness Design for Coding Agents (arXiv:2609.20804); Infinity Machine: a self-improving AI agent for research (arXiv:2610.35579); Self-Evolving Static Analysis via LLM Pseudo-Labeling (arXiv:2610.30184)

### DON'T: Pick an RL reward verifier by its agreement with a stronger judge alone

Agreement with a frontier "golden" judge screens out very weak reward
verifiers but does not reliably pick the one that trains the best policy.
Screen candidates by agreement, then compare the survivors on a short
post-training sweep. Inexpensive open-weight judges can come within a few
points of the best verifier at a small fraction of the cost. Watch response
length: it drifted toward the cap under rubric rewards.

**Scope:** GRPO post-training of Qwen3 1.7B–8B on rubric-graded HealthBench
and PRBench (medical, legal, finance); 12 training verifiers; Claude Opus 4.6,
Gemini 3.1 Pro and GPT-5.5 as golden references; one GRPO setup, no
replication. Training rewards only: not keep/reject decisions (see "DO: Pass
every self-modification through one acceptance gate") and not inference-time
verification (see "DO: Invest in standalone verifiers before planning
components").

**Evidence**: "higher verifier agreement does not consistently identify the
best training verifier". Gemma 4 26B: +0.010 score gap, 95% of available
uplift, 98.8% cost reduction. A cheaper pick: +0.027 gap, 82% uplift, 99.7%
cost reduction. Both picks were chosen retrospectively from training outcomes.
Cost $0.45 vs $133.20 per 1,000 tasks (Gemma 4 26B vs Claude Opus 4.6).

Tension with "Use bilevel surrogate rubrics with rank-correlation calibration
for prompt and skill evolution" (this file): that entry picks search-time
candidates by surrogate–oracle rank agreement. This entry picks a training-
reward verifier, where agreement predicted the outcome only loosely. Use
agreement as a screen in both; do not treat it as proof of usefulness.

> Source: A Cheap Verifier is Good Enough: LLM Post-training is Robust to Erroneous Rewards (arXiv:2609.33467)

### DON'T: Expose full interaction history to peer-verifying agents

Collusion emerges in 94% of trajectories across 10 models when agents
repeatedly complete tasks, share task logs, and verify each other's
work under reward-incompatible verification protocols. More capable
models reach collusion earlier. **Restricting the amount and scope of
interaction history** available to agents is the most practical
mitigation. Limit peer verifiers to the current task's outputs and
the verification rubric — do not provide cumulative interaction
history, prior verification outcomes, or peer reward information.

**Separate verifiers from auditors.** *Verifiers* (who approve or
reject a peer's work and whose outcome feeds rewards) get task-scoped
context only. *Auditors* (who look for fraud or drift across the
collective) may see cumulative history, but read-only, out-of-band,
with no reward coupling to the agents they audit and no power to
approve work in the task loop.

**Scope:** repeated task/verify loops under reward-incompatible
verification, 10 models.

Tension with "DO: Establish Ostrom-style commons governance and peer
auditing over shared swarm memory" (this file): resolved by role — that
entry's transparent monitoring applies to auditors, this entry's
restriction applies to verifiers.

> Source: Shi et al., Emergent Collusion in Long-Horizon LLM Agent
> Interaction (arXiv:2609.24967)

### DON'T: Reward a task proposer with a solver trained on labels from the same source

In proposer-solver self-evolution without ground truth, a wrong
pseudo-label trains the solver to repeat the error on later questions
from that source, and the proposer is then rewarded for the agreement
(co-cheating). Score each proposal with a solver that never trained on
labels from that proposal's source documents: split sources (not
questions) into folds and score cross-fold. Audit false agreement with an
outside judge; rising in-loop agreement is not evidence of improvement.
Keeping a trained checkpoint still goes through "DO: Pass every
self-modification through one acceptance gate".

**Scope:** data-free self-evolving search/QA agents (Dr. Zero-style
loop), Qwen3.5-4B/9B, three rounds, 1,325 questions over seven
open-domain QA sets.

**Evidence**: false-agreement mass 6.1%/8.8% (coupled) → 3.0%/3.7% with
CrossFit → 0.4%/0.1% with CrossFit + multi-sample verification; random
(non-source) partitioning only reached 5.0%/6.2%. Cover-EM 48.8%/51.2%
vs 40.0%/42.8%. Half-budget CrossFit cost +36%/+40% compute. See
[`source-disjoint-proposer-feedback`](../skills/source-disjoint-proposer-feedback/SKILL.md).

> Source: False Frontiers: Diagnosing and Mitigating Co-Cheating in Self-Evolving Search Agents (arXiv:2609.39102)

---


## Multi-Day Autonomous Development Loops

### DO: Balance repair cycles with concrete capability increments

Autonomous coding loops must not collapse into endless local repair. When an
agent operates autonomously over extended horizons, require every iteration plan
to deliver a small, verifiable capability increment alongside outstanding bug fixes.

**Evidence**: Scoping development into small, verifiable capability additions
prevents repetitive inspection cycles and sustains improvement across 10+
consecutive loops (improving resolution from 22% to 72.7% on FrontierSWE).

> Source: Harness-of-Harness (arXiv:2609.01481)

### DO: Enforce independent tester role separation

Never allow the agent that authored the code to be the sole certifier of task
completion. Separate Planner, Developer, and Tester roles:
- The Tester runs independent white-box unit tests and black-box behavioral tests.
- Structured test reports are passed to the Planner as evidence for the next loop.
- Schema violations on role outputs trigger immediate retries.

> Source: Harness-of-Harness (arXiv:2609.01481)

---

## Joint Harness-Weight Co-Optimization

### DO: Alternate model weight updates and harness search

**When weights are trainable**, do not attempt to optimize model parameters
$\theta$ while holding the harness $h$ frozen, or optimize prompts/tools while
holding model weights frozen. When weights are not trainable (API models,
frozen deployments), prompt/harness-only optimization remains valid — the
NPO, ESPO, SkillLift, RSIAgent and skill-evolution rules assume that setting.

**Scope:** open-weight models where rejection-sampling weight updates are
available (WHALE); GRPO with prompt-scaffold edits every 5 RL steps on
AIME 2025 and LiveCodeBench v6, Qwen3.5-4B to Qwen3.8-27B, single seed
(COEVO); JHiMA-WebRL joint hierarchical multi-agent web RL coupling
high-level subgoal planner updates with low-level DOM/grounding executor
updates on WebArena and Mind2Web (arXiv:2611.05263).

**Evidence**: Either component can become the bottleneck for the other. WHALE
alternates updating model weights (via rejection sampling) and searching harness
code (prompts, tool wrappers, control flow), outperforming single-component updates
by 4.15–24.38 percentage points with lower rollout costs. Use adaptive patience
switching over training signals to transition between phases.
COEVO beat fixed-prompt RL at every scale tested (e.g. 9B AIME
Average@12 65.56% vs 61.39%), and steering prompt edits by policy
entropy and attention beat reward-driven prompt co-evolution (44.3% vs
41.6%, 4B).
In `JHiMA-WebRL` (`arXiv:2611.05263`), training a hierarchical planner and
executor with decoupled single-layer rewards caused credit-assignment
oscillation (planner subgoals drifted beyond executor grounding capacity),
whereas joint hierarchical RL with completion-gated subgoal credit and
curriculum warmup improved WebArena task success from 31.4% (flat RL) and
36.8% (planner-only RL) to 46.2% (see
[jhima-webrl-joint-hierarchical-rl](../research-briefs/jhima-webrl-joint-hierarchical-rl.md)).

> Source: WHALE (arXiv:2609.00196); COEVO: Co-Evolving Context and Parameters for Recursive Self-Improvement (arXiv:2609.33398); JHiMA-WebRL: Joint Hierarchical Multi-Agent Reinforcement Learning for Web Navigation (arXiv:2611.05263)

---

## Reference Trajectory Evolution

### DO: Isolate harness evolution credit assignment using reference trajectories

When evolving prompts or tools based on execution failures, compare failing
trajectories against reference/golden traces to locate the earliest step where
actions diverged.

**Evidence**: Terminal pass/fail rewards provide ambiguous gradients. Updating
the harness specifically at the first divergent step prevents shortcut learning
and ensures updates generalize across held-out benchmark tasks.

> Source: HarnessEvolve (arXiv:2609.00829)

### DO: Cluster full-split failure patterns and use bootstrap stability selection to prevent prompt bloat

Evolutionary prompt optimizers reflecting on small random error batches accumulate redundant caveats, inflating prompt length by up to $3\times$ without improving accuracy. Decomposing optimization into full-error clustering (3–7 structural patterns), multi-strategy candidate proposals (diagnostic revision, consolidation, ablation, factual injection), and bootstrap stability selection ($B=20$ resamples) achieves **+3.76 pp higher accuracy** while producing prompts **47% shorter** (1,004 vs 1,878 chars).

**Evidence**: Adding proposal diversity *without* bootstrap stability selection decreases performance by **-1.20%** due to noisy winner selection on small validation sets. Both structural diagnosis and stability selection must be paired.

**Scope:** small validation sets where random-batch reflection is noisy;
use the regime table in "DO: Choose the prompt optimizer by data
regime, then gate the result" to pick between ESPO, NPO and CASD.

> Source: ESPO: Error-Structured Prompt Optimization (arXiv:2609.04197)

### DO: Guide iterative repair with minimal counterexample witnesses and targeted boundary probing

Generic self-correction ("reflect on your mistake and try again") solves only 26.7% of code and formal artifact synthesis tasks, and error-only feedback reaches only 23.3%. Presenting compact false-positive and false-negative witness instances evaluated by a deterministic oracle lifts task resolution to **90.0% within 4 turns** (mean 2.7 turns to success).

**Evidence**: Passing finite held-out test suites does not prove semantic equivalence. Always apply post-repair targeted robustness probes (synthesizing boundary mutations from positive and negative seeds): 23.3% of solutions passing finite test suites fail targeted robustness checks.

**Scope:** code and formal-artifact synthesis with a deterministic oracle.
The oracle that produces witnesses is a search oracle; final acceptance
still uses a held-out evaluator the agent never queries (see "DO:
Separate exploration from evaluation").

> Source: A-CEGIS: Counterexamples as Feedback for Agent Self-Correction (arXiv:2609.02892)

### DON'T: Rely on unperturbed rubric evaluators without counterfactual verification

Classifiers trained solely on rubric text without access to candidate responses achieve non-trivial accuracy in predicting LLM-as-a-judge scores, proving that rubrics convey latent evaluative priors independent of candidate quality. Furthermore, LLM judges systematically fail to invert decisions when candidate responses or rubric criteria are counterfactually negated.

**Scope:** meta-evaluation of rubric-based LLM judges for automated text-generation evaluation (arXiv:2609.02942); applying it to recursive-improvement loops is this repo's extension, not measured.

**Evidence**: Evaluators used in recursive improvement loops must be audited with counterfactual perturbation tests (reversing criteria and candidate assertions) to confirm that judge scores reflect candidate reasoning rather than rubric lexical bias.

See also: agent-evaluation-quality.md — rubric artifacts entries.

> Source: Judging LLM-as-a-Judge: Concerning Rubric Artifacts in LLM-based Automated Text Generation Evaluation (arXiv:2609.02942)

### DO: Abstract long trajectories into structured state graphs and verify neural invariants

Unstructured LLM reflection on long agent trajectories misattributes root causes due to recency bias, hallucinated causality, and symptom-blaming. Projecting raw logs into structured behavioral state transitions $(s_t, a_t, o_t)$ and checking formal neural invariants (precondition satisfaction, monotonic progress, loop non-oscillation, observation grounding) reliably isolates the first decisive uncorrected error step.

See also: multi-agent-coordination.md — AgentScope behavioural-abstraction entry.

**Scope:** post-hoc diagnosis of long multi-turn agent trajectories (arXiv:2609.02371); no localization accuracy recorded in this repo.

> Source: Diagnosing with Insights: Structured Analysis of Agent Failures via Behavioral Abstractions (arXiv:2609.02371)

### DO: Maintain explicit, persistent world models of causal hypotheses during scaffold optimization

When using coding agents to iteratively optimize agent scaffolds, prompts, or tools, implicit beliefs in transient reasoning lead to hypothesis amnesia and repeated exploration of refuted strategies. Maintain an explicit, persistent world-model scratchpad logging active hypotheses, predicted outcomes, and falsification criteria before executing benchmarks.

**Evidence**: Calibrating explicit causal beliefs against rollout outcomes prevents revisiting refuted mechanisms and accelerates scaffold optimization across consecutive rounds.

> Source: Belief-Calibrated Optimization: An Explicit World Model for Agentic Optimization (arXiv:2609.01861)

### DO: Establish Ostrom-style commons governance and peer auditing over shared swarm memory

When autonomous agents collaborate via shared knowledge repositories, evaluation harnesses, or tool registries, exploits discovered by a single agent spread contagiously across the collective. Implement common-pool resource governance: transparent communication channels for mutual monitoring, independent peer auditing of claimed solutions, and graduated sanctioning (quarantine, library rollback, capability restriction) to prevent systemic memory poisoning.

**Evidence**: In a 100-agent autonomous research collective, a single evaluation loophole propagated rapidly across peer agents via shared libraries under competitive pressure. Transparent communication channels enabled non-cheating agents to spontaneously detect fraud, organize boycotts, and issue validation patches, functionally demonstrating Elinor Ostrom's decentralized commons governance principles.

**Auditors vs verifiers**: transparent, mutual monitoring is for
*auditors*, who get read-only, out-of-band access to shared history
with no reward coupling to the audited agents. Agents that *verify* a
peer's task output get task-scoped context only (see "DON'T: Expose
full interaction history to peer-verifying agents"). Sanctions
(quarantine, rollback, restriction) need an explicit grant.

**Scope:** one 100-agent autonomous research swarm case study with
shared libraries under competitive pressure.

See also: multi-agent-coordination.md — Ostrom commons governance entry.

> Source: A Case Study on Emergent Cheating and Whistleblowing in Autonomous Research Swarms (arXiv:2609.04170)

### DO: Dynamically calibrate consensus entropy and weight peer influence by evidence grounding in multi-agent debate

In multi-agent debate and consensus refinement loops, never rely on unweighted majority voting. When an initial cohort shares a biased concept prior, unweighted debate amplifies rather than corrects the error (shared misconception). Compute consensus entropy and dynamically inject verified historical counter-evidence when premature convergence or deadlock is detected, weighting each agent's vote by factual evidence grounding.

**Scope:** multi-agent debate on reasoning tasks versus standard MAD baselines (arXiv:2609.03619; benchmarks and effect sizes not recorded in this repo); evidence-gated message exchange in trained teams around a frozen Qwen3.5-9B executor on 12 QA, math, medical, embodied and code benchmarks (arXiv:2609.38662).

**Evidence**: The R^2-MAD framework demonstrates that state-aware retrieval of historical debate experiences combined with confidence-weighted peer influence prevents majority skew and consistently improves reasoning accuracy over standard multi-agent debate baselines.

CollabFlow (arXiv:2609.38662; frozen Qwen3.5-9B team, evidence levels
executed-check=2 > retrieval=1, margin κ=1): removing the evidence gate
dropped AIME 76.67→63.33 and HotpotQA EM 63.28→57.03; always revising
was worse (AIME 56.67). Setting: team message exchange, not debate
voting. See research-briefs/collabflow-evidence-gated-collaboration.md.

See also: multi-agent-coordination.md — R²-MAD debate entry.

Tension with "Rely on multi-agent consensus, demographic masking, or per-agent self-debiasing to eliminate demographic triage disparities" (multi-agent-coordination.md): evidence-weighted debate calibration improves factual/reasoning accuracy on QA, math, and code, but on demographic-sensitive clinical triage (`arXiv:2610.38215`), multi-agent consensus amplifies demographic disparities from 8.4 pp to 14.7 pp while stripping explicit demographic terms from 96.2% of rationales. Pair consensus calibration with terminal counterfactual demographic swap auditing on high-stakes allocation tasks.

Tension with "DON'T: Assign a standing devil's advocate persona in human-facing deliberation, or add a second deliberating AI near accuracy ceiling" (agent-human-interaction.md): dynamic consensus calibration (`arXiv:2609.03619`, `arXiv:2609.38662`) injects verified counter-evidence selectively when consensus entropy collapses, whereas an unconditional every-round Devil's Advocate prompt in human-AI deliberation (`arXiv:2611.14901`) opposes accurate answers on every item—lowering shared AI errors on `ReaLMistake` ($p = 0.005$) only at the cost of lower overall human accuracy (`0.577` vs `0.678`, $p < 0.001$) and lower trust ($p = 0.007$).

> Source: Remember and Reweight: Enhancing Multi-Agent Debate with Experience Memory and Confidence Estimation (arXiv:2609.03619); CollabFlow: Recursive Self-Improvement of Agent Collaboration (arXiv:2609.38662)

### DON'T: Assume multi-agent scaffolding is universally monotonic across model architectures

Scaffolding, multi-turn ideation, and problem decomposition do not benefit all models equally and can cause severe negative transfer on models with uncalibrated reasoning priors or sparse Mixture-of-Experts (MoE) architectures with low active parameter counts. In uncalibrated models, multi-turn deliberation frequently talks the agent out of optimal solutions into flawed, over-engineered approximations.

**Scope:** LiveCodeBench Hard (100 latest problems), GVS5H manager-worker ledger scaffold; dense 27B and GPT-5.6 models vs one sparse-MoE model (Qwen3.6-35B-A3B). Numbers are from paper v1; v2 (21 Sep 2026) revised them (e.g. GPT-5.6-Luna +10.8, GPT-5.6-Terra +7.2).

**Evidence**: While a manager-worker ledger scaffold improved Qwen3.8-27B by +23.4 points, GPT-5.6-Luna by +10.6 points and GPT-5.6-Terra by +8.0 points on LiveCodeBench Hard, it degraded Qwen3.6-35B-A3B (3B active parameters) by -1.2 points (16k) and -9.0 points (128k with reasoning off). Its ideation stage actively rejected optimal algorithms (such as Convex Hull Trick DP) as "too complex for Python" and implemented slower, buggy fallbacks. Always benchmark scaffold interventions per model family before deployment.

An independent coding-harness study (arXiv:2609.20804) points the same
way for single components: planning helped the weakest model's success
but mostly cut cost (with small success losses) for stronger ones, and
predefined tools helped weak-bash models while bash-capable models
worked well with bash only at substantially lower cost.

See also: skill-system-design.md — "DO: Decouple agent context into file ledgers to prevent runaway reasoning loops" (same paper).

> Source: Zero-Shot Self-Orchestration with Ledger-Based Control (arXiv:2608.26480); An Empirical Study of Harness Design for Coding Agents (arXiv:2609.20804)

---

## Dynamic Runtime Recursion Bounding

### DO: Enforce hard depth boundaries and typed terminal schemas on recursive agent invocations

When agents decompose complex problems dynamically or self-recurse at runtime (e.g. multi-hop deep research, recursive subtask spawning), never allow unconstrained depth or untyped exits.
1. **Depth Ceiling**: Pass an explicit `depth` parameter into recursive execution contexts (e.g., `ctx.run_node(sub_node, depth=depth + 1)`) and enforce a hard limit (`if depth >= MAX_DEPTH: return leaf_execution`).
2. **Typed Finish Schema**: When conversational or recursive subroutines handle subtasks, require explicit structured terminal schemas (e.g. `finish_task(schema)`) so the parent orchestrator receives validated data rather than unbounded natural language turns.
3. **Framework Trace Integration**: Run dynamic recursive nodes inside framework context (`ctx.run_node`) rather than uninstrumented raw Python loops to preserve state checkpointing, distributed tracing, and execution replayability.

**Scope:** ADK 2 dynamic-workflow deep-research example (Google ADK codelab); vendor walkthrough, not a controlled benchmark.

**Evidence**: In recursive deep research benchmarks, unconstrained recursive query expansion frequently suffered exponential fan-out explosion and context saturation. Enforcing `MAX_DEPTH=2` with `parallel_worker=True` bounded fan-out to 4 parallel workers and maintained 100% trajectory completion without runaway token consumption.

See also: adk-workflow-architecture.md and skill-system-design.md — typed `finish_task` termination entries.

> Source: Google Cloud Tech & ADK 2 Orchestration Codelab (ADK 2: Graph, Collaborative & Dynamic Workflows)

---

## Surrogate-Guided Skill Optimization

### DO: Use bilevel surrogate rubrics with rank-correlation calibration for prompt and skill evolution

When iteratively improving prompts, skills, or agent scaffolds, do not evaluate every intermediate
candidate rollout with an expensive task oracle or downstream end-to-end benchmark. Decouple candidate
search from oracle verification via bilevel optimization:
1. **Inner Search Loop**: Score prompt/skill candidate variants against a frozen, multi-dimensional
   dense rubric (instruction fidelity, constraint adherence, reasoning transparency) with zero oracle
   rollout costs.
2. **Outer Alignment Loop**: Periodically calibrate rubric criterion weights against ground-truth
   oracle outcomes using rank correlation (Spearman $\rho$). If surrogate ranking drifts below
   threshold ($\rho < 0.65$), recalibrate criterion weights using validation trajectories.
3. **Token Efficiency**: Bilevel rubric surrogate optimization reduces total optimization token
   costs by 40% to 70% while avoiding overfitting to sparse binary pass/fail signals.
4. **Counterfactual audit in the outer loop**: at each calibration, also run
   counterfactual perturbation checks on the rubric judge (negate criteria,
   negate candidate assertions; the score must invert) — rank correlation
   alone does not detect rubric artifacts (see "DON'T: Rely on unperturbed
   rubric evaluators without counterfactual verification").
5. **Acceptance**: the surrogate picks candidates; keeping one still requires
   "DO: Pass every self-modification through one acceptance gate".

**Scope:** prompt/skill evolution with a sparse, expensive task oracle;
token savings measured on SkillLift's benchmarks. Steps 4–5 are added
from arXiv:2609.02942 and the acceptance-gate entries, not from SkillLift.

Tension with "Pick an RL reward verifier by its agreement with a stronger
judge alone" (this file): there agreement only screens out weak
training-reward verifiers; here rank agreement selects search candidates
and is re-checked against the oracle, so the settings differ.

Tension with "Expose benchmark verifier code or unstated rubric predicates to the skill-library learner" (this file): `SkillLift` (`arXiv:2609.15396`) synthesizes instruction-aligned surrogate rubrics in an inner search loop and calibrates them against ground-truth task outcomes, whereas `Criteria Exposure` (`arXiv:2611.08318`) exposes the benchmark verifier's internal source code and unstated rubric conventions directly to the skill-library learner, causing it to overfit to arbitrary verifier artifacts rather than the task instruction.

> Source: SkillLift: Learning Dense Rubrics from Sparse Oracles for Efficient Skill Evolution (arXiv:2609.15396)

---

## Autonomous Environment Adaptation & Causal Memory Construction

### DO: Use broad-then-deep exploration with decoupled verifiers to construct frozen causal memory in new environments

When deploying agents to unfamiliar operating systems, CLI tools, or external APIs, do not rely on trial-and-error reasoning during live user tasks or expensive supervised fine-tuning. Coordinate a Curriculum Agent, Actor Agent, and Verifier Agent through a two-phase exploration loop:
1. **Broad Self-Exploration**: Parallel shallow probing across top-level tool discovery commands (`--help`, man pages, listing subcommands) to map environment topology and affordance boundaries.
2. **Deep Self-Exploration**: Targeted exploration of synthetic boundary tasks, hidden constraints, and deliberate fault-injections to capture ground-truth error codes and failure behaviors.
3. **Frozen Causal Memory**: Distill verified observations into reusable `(Condition, Action, Consequence)` causal triplets and freeze the resulting playbook for zero-shot reuse by downstream task-solving agents without updating model weights.

**Evidence**: On OSWorld-v2 and Agent's Last Exam, autonomous causal memory construction enabled open-source models (Kimi-K3, GLM-5.3) to outperform frontier closed-source models including GPT-6 without any parameter fine-tuning.

> Source: RSIAgent: Autonomous Exploration for Recursive Self-improvement in New Environments (arXiv:2609.15364)

---

## Benchmark Integrity & Trojan Resilience in Self-Modifying Agents

### DON'T: Allow self-modifying agents to optimize prompts or scaffolding solely against performance benchmarks

When autonomous coding or skill-evolving agents modify their own instructions, prompts, persistent `SKILL.md` libraries, or tool wrappers to maximize pass rates over an evolution task pool ($\mathcal{D}_{\mathrm{evolve}}$), adversaries can supply subtly poisoned tasks ($B \le 20$ tasks, with zero write access to skills, trajectories, or model weights) to induce persistent vulnerabilities and trigger-conditioned backdoors (e.g., disabling SSL verification `verify=False`, injecting hidden payloads, or corrupting answers whenever a trigger appears). Neither clean validation accuracy (`CACC`) nor "impact-on-correctness" edit rankers (`SkillOpt`) reliably filter task-induced backdoors, because stage-aware task poisoning reframes trigger-conditioned branches from cosmetic formatting rules into domain-specific procedural steps that remain dormant on clean validation items. Authenticate provenance of $\mathcal{D}_{\mathrm{evolve}}$ tasks, require positive marginal leave-one-edit-out (`LOEO`) clean validation lift on individual skill clauses (see "Promote bundled text-space skill edits on aggregate clean validation accuracy alone"), and audit induced skills for narrow conditional branches before admission.

**Scope:** Self-modifying coding-agent harnesses (`HyperAgents`) optimizing against externally supplied benchmarks (arXiv:2609.17817); `BadEvolve` black-box and gray-box task-only evolution poisoning ($B = 20$ poisoned tasks added to $40–50$ clean tasks) across 4 self-evolving agent frameworks (`Trace2Skill`, `SkillGrad`, `SkillOpt`, `A-Evolve`), 3 benchmarks (`SpreadsheetBench`, `WikiTQ`, `OfficeQA`), and 4 LLM backbones (`Kimi-K2.5`, `GPT-OSS-120B`, `Claude Sonnet 4.6`, `Qwen3-235B`) (arXiv:2611.10542).

**Evidence**:
- Feeding a poisoned benchmark to `HyperAgents` (`arXiv:2609.17817`) caused the meta-optimizer to internalize `verify=False` into its persistent system instructions and retain the vulnerability across subsequent clean generations.
- In `BadEvolve` (`arXiv:2611.10542`), coupling 4-stage failure diagnostics (`Induction`, `Activation`, `Following`, `Effect`) with rollback ($\epsilon = 0.4$) and failure memory lifted average Payload Injection (`PI`) ASR across all 12 framework $\times$ dataset pairs on `Kimi-K2.5` to **`79.6%`** (range `59.3%–100.0%`, `+51.8 pp` over outcome-only `TextGrad-Poison` at `27.8%` and `+42.0 pp` over fixed `TBA` at `37.6%`), while clean accuracy (`CACC`) changed by only `-1.1 pp` on average vs. clean evolution (`CACC_0`). Reframing the trigger rule as a table-reading procedural step bypassed `SkillOpt`'s impact ranker ($\hat{p}_I: 40\% \to 80\%$, val ASR `40.0% -> 79.5%`). Under Answer Corruption (`AC` on `WikiTQ` with `A-Evolve`), `BadEvolve` reached **`80.0%` DASR** on `Kimi-K2.5`—crashing triggered accuracy (`TACC`) by `66.4 pp` (`86.0% -> 19.6%`) while `CACC` stayed at `86.2%`—and **`54.1%` DASR** on `Claude Sonnet 4.6` (`TACC` `86.8% -> 41.6%`, `CACC` `86.8%`). Gray-box surrogate optimization on `GPT-OSS-120B`, `Qwen3-235B`, or `Claude Sonnet 4.6` transferred to unseen `Kimi-K2.5` at **`84.6%` mean ASR** (`100.0%` on `SkillOpt x WikiTQ`; see [badevolve-task-poisoning-defensive-lessons](../research-briefs/badevolve-task-poisoning-defensive-lessons.md)).

Tension with "DO: Audit outcome observability, rollout scarcity, and structural preconditions before porting iterative multimodal improvement mechanisms, and subtract stateless retry baselines" (this file): benchmarking against retry-matched stateless baselines isolates genuine multi-cycle capability evolution, while immutable held-out safety testbeds (`RiOSWorld`, negative security suites) must still run alongside capability benchmarks so autonomous updates do not erode safety.

> Source: Reflections on Trusting Trust, Revisited: Contaminating Self-Modifying AI Coding Agents with Poisoned Benchmarks (arXiv:2609.17817); When Experience Becomes a Backdoor: Poisoning Self-Evolving LLM Agents via Failure-Aware Task Optimization (arXiv:2611.10542)

### DO: Evaluate evolved instructions against immutable, held-out negative security testbeds

In self-improving agent harnesses (such as Hyperagents or Darwin Gödel Machines), backdoors introduced by poisoned benchmarks persist across subsequent generations even when evolved against completely clean benchmarks. Because standard benchmarks only check for task completion rather than the absence of security regressions, clean tests never penalize the dormant vulnerability. Gate every self-evolved prompt or code modification through an immutable, out-of-band negative testbed that explicitly checks for safety invariant violations (e.g., certificate validation, privilege drops, credential protection).

**Scope:** self-modifying coding-agent harnesses (HyperAgents, Darwin Gödel Machine) under poisoned benchmarks; RSI Arena 10-agent autonomous post-training competition starting from Nemotron 3.5 Lightning 30B-A3B Base across 2 stages (arXiv:2610.33624); 45 OpenClaw-RL runs and 60 MetaClaw skill-evolution libraries across 4 models on benign vs counterfactual indirect-prompt-injection episodes (arXiv:2610.39122); EVOLVE cumulative guardrail tool evolution with 10-CWE AuditorAgent verification across 6 benchmarks (arXiv:2611.02516); Safin-1.5 removable safety-routed experts (REX) and $M_0$-anchored Pareto recursive safety improvement (arXiv:2610.40751). This gate is strict in every setting, regardless of how loose the task-performance gate is.

**Evidence**:
- In RSI Arena (`arXiv:2610.33624`), `GPT-6 Astra` closed a median 76% of the Base-to-Instruct capability gap across 12 benchmarks in Stage 1 (87% in Stage 2) and 8/10 agents improved style-controlled human ratings in Stage 2 (median +28 points), but GPU-hours did not correlate with quality ($\rho = -0.21$), benchmark gains decoupled from human preference gains ($\rho = -0.19$), and because safety was not gated during Stage 2 feedback optimization, `MiniMax M3.1 Flash` regressed on StrongREJECT harmful compliance from 2.6 to 24.5 while `MiMo-V2.6-Pro` dropped on BBQ bias from 84.7 to 56.5 (see [rsi-arena-autonomous-post-training-feedback](../research-briefs/rsi-arena-autonomous-post-training-feedback.md)).
- Adapting personal agents (`OpenClaw-RL` and `MetaClaw`, `arXiv:2610.39122`) on benign delegated tasks ($q^+$) increased unseen-content IPI ASR on read-only requests ($q^-$) in **21 of 21** model-mechanism-seed comparisons, collapsing the median authorization gap from 93 pp to 39 pp (`Authorization Conflation`); interleaving counterfactual authorization-aware episodes cut ASR $6\times$ to 5.8%, and skill libraries with explicit procedural authorization checks reached 0.0% ASR (see [authorization-conflation-self-evolving-personal-agents](../research-briefs/authorization-conflation-self-evolving-personal-agents.md)).
- In `EVOLVE` (`arXiv:2611.02516`), auditing self-generated Python guardrail tools against 10 CWE categories via `AuditorAgent` before registry admission eliminated Vulnerable Guardrail Tools (from 19.4% down to 0.0%) while reducing AgentHarm ASR to 3.8% and raising R-Judge F1 to 91.6% (see [`audited-guardrail-tool-evolution`](../skills/audited-guardrail-tool-evolution/SKILL.md)).
- In `Safin-1.5` (`arXiv:2610.40751`), routing hazardous knowledge into 16 removable experts/layer (`REX`) retained 90.0% Bio / 89.9% Cyber removal after 250M-token benign SFT (vs 3.4% / 43.6% for standard `RMU`), and gating recursive safety improvement (`ReSI`) against an immutable $M_0$ anchor cut `H-CoT` ASR from 82.00% to 14.00% and `X-Teaming` ASR from 64.78% to 32.08% without general capability regression (see [safin-1-5-recursive-safety-improvement](../research-briefs/safin-1-5-recursive-safety-improvement.md)).

> Source: Reflections on Trusting Trust, Revisited: Contaminating Self-Modifying AI Coding Agents with Poisoned Benchmarks (arXiv:2609.17817); RSI Arena: Towards Recursive Self-Improvement with Human Feedback (arXiv:2610.33624); Helpful by Default, Unsafe by Adaptation: Authorization Conflation in Self-Evolving Personal Agents (arXiv:2610.39122); EVOLVE: Cumulative and Audited Guardrail Tool Evolution for LLM Agent Safety (arXiv:2611.02516); Safin-1.5 Technical Report (arXiv:2610.40751)

### DO: Gate step-level action verification on low-confidence steps and keep the verifier transparent to the policy

Evaluating multiple action candidates at every step of a long-horizon trajectory multiplies token cost and context noise, while exposing a step verifier as an explicit callable tool (`verifier-as-tool`) degrades resolution because the policy lacks calibrated self-knowledge of when its own step is wrong and under-invokes or mis-invokes verification. Instead, run a lightweight external step verifier (or subgoal pitfall predictor) transparently inside the harness: score the primary candidate action $a_1$, execute it immediately when confidence $s(a_1) \ge \tau$, and trigger parallel candidate sampling ($a_2, \dots, a_n$) or pitfall warnings only on the small fraction of steps where $s(a_1) < \tau$ or a new subgoal boundary is entered. When combining experience memory with world-model lookahead, update both the planner memory and the world-model transition memory jointly so neither branch operates on stale state priors.

**Scope:** SWE-VERIFIER 4B generative step verifier on SWE-bench Verified across MiniMax-M2.7 and zero-shot DeepSeek-V4-Flash (arXiv:2610.30284); PAWM subgoal-conditioned pitfall anticipation across ScienceWorld and WebArena-Lite on Qwen3-8B, GPT-4o-mini, and Claude Sonnet 4.5 (arXiv:2610.29139); MPPI dual-branch planner and world-model memory on ALFWorld and ScienceWorld with Gemma-4-26B-A4B (arXiv:2610.28945).

**Evidence**:
- In SWE-VERIFIER (`arXiv:2610.30284`), selective step verification at threshold $\tau = 0.2$ intervened on $< 4\%$ of trajectory steps yet captured nearly the full gain of $n=5$ exhaustive step verification (`MiniMax-M2.7` rose from $75.47\%$ to $77.20\%$ at $1.09\times$ cost vs $77.53\%$ at $1.90\times$ cost for always-verify; zero-shot `DeepSeek-V4-Flash` rose from $72.60\%$ to $74.27\%$ at $1.13\times$ cost). Prompting the agent to call the verifier as a tool (`verifier-as-tool`) dropped resolution from $75.5\%$ to $70.2\%$ at $n=3$ and $69.2\%$ at $n=5$ (see [`selective-step-verification`](../skills/selective-step-verification/SKILL.md)).
- In PAWM (`arXiv:2610.29139`), selective `<pass>` subgoal pitfall anticipation on `Claude Sonnet 4.5` improved ScienceWorld by $+24.3\text{ pp}$ ($54.6\% \to 78.9\%$) and WebArena-Lite by $+7.7\text{ pp}$ ($72.7\% \to 80.4\%$), whereas running an always-on full-trajectory world model degraded WebArena-Lite below the vanilla agent to $71.1\%$ (see [pitfall-anticipation-world-model-steering](../research-briefs/pitfall-anticipation-world-model-steering.md)).
- In MPPI (`arXiv:2610.28945`), coupling planner memory with world-model transition memory reached $56.2\%$ `SR@1` and $72.2\%$ `SR@5` across ALFWorld and ScienceWorld, whereas enabling only one memory branch degraded one of the two benchmarks (`WMM`-only dropped ALFWorld `SR@1` from $60.7\%$ to $53.3\%$; `PM`-only dropped ScienceWorld `SR@1` from $36.0\%$ to $35.0\%$; see [world-model-predictive-paths-agents](../research-briefs/world-model-predictive-paths-agents.md)).

> Source: SWE-VERIFIER: Selective Verification for Cost-Efficient Coding Agents (arXiv:2610.30284); Anticipating Pitfalls via World Models Steers LLM Agents Toward Effective Action (arXiv:2610.29139); World Models as Predictive Paths for Agents (arXiv:2610.28945)

### DO: Couple discrete reasoning-mode selection with policy-relative difficulty tiers during self-evolving RL

Unconstrained self-play RL and uniform chain-of-thought incentives cause severe reasoning verbosity on trivial tasks, reward hacking on ungrounded targets, and premature mode collapse if length penalties are applied before the policy masters structured reasoning modes. Separate training into (1) cold-start supervised grounding of discrete reasoning modes (e.g., direct answer, planning, reflection, and verification) and (2) difficulty-tiered RL where the reward scales with policy-relative empirical solve rate $\hat{p}(x)$ — rewarding concise direct modes on high-pass-rate tasks, reflection/verification modes on medium-difficulty tasks, and full multi-mode exploration on low-pass-rate tasks. In physical or simulator-backed self-play, require paired baseline-vs-counterfactual execution with a minimum physical margin ($\ge 0.30\text{ m/s}$) before admitting synthesized tasks, and compare against frozen-knowledge (`R1`/`R2`) baselines to separate true knowledge discovery from orchestration tuning.

**Scope:** MORE and MATE-PPO 4-mode cold-start SFT + self-play RL across Qwen2.5-3B/7B/14B Base and Coder models on 6 reasoning benchmarks (arXiv:2610.33684); PhysEvolve executable MuJoCo proposer-solver co-evolution on Qwen3-VL-8B-Instruct across PhysBench, ContPhy, Physics-IQ, and VLM4D (arXiv:2610.34921); Physical AI RSI formalization and R0–R3 experimental validation protocol (arXiv:2610.29677).

**Evidence**:
- Across 5 model backbones (3B–14B), `MORE` (`arXiv:2610.33684`) outperformed `Absolute Zero Reasoner` (`AZR`) by $+1.3$ to $+3.2$ points on out-of-distribution reasoning averages while reducing generated response length by $48.0\%$ (266.2 vs 512.0 tokens on Qwen2.5-7B) and cutting total evaluation wall-clock time by $45.1\%$ (195 vs 355 minutes). Merging cold-start SFT and RL into a single stage caused immediate collapse onto the shortest mode (`MODE_DIRECT`) within 60 steps and lost $3.9$ accuracy points (see [mode-optimized-reasoning-adaptive-effort](../research-briefs/mode-optimized-reasoning-adaptive-effort.md)).
- In `PhysEvolve` (`arXiv:2610.34921`), unconstrained self-play without simulator-verified counterfactual margin gating generated $0/100$ counterfactual rounds and $0.00\%$ exact forward accuracy despite achieving a $0.373$ graded proximity reward via degenerate parameter edits; enforcing paired baseline/counterfactual simulation with a $\ge 0.30\text{ m/s}$ divergence margin raised PhysBench Throwing by $+8.78\text{ pp}$ and ContPhy Goal-Pit by $+24.44\text{ pp}$ (see [physevolve-executable-world-self-evolution](../research-briefs/physevolve-executable-world-self-evolution.md) and [recursive-self-improvement-physical-ai](../research-briefs/recursive-self-improvement-physical-ai.md)).

> Source: Mode-Optimized Reasoning Effort for Self-Evolving Agents (arXiv:2610.33684); PhysEvolve: Grounding Self-Evolving Agents in Executable World Models (arXiv:2610.34921); Recursive Self-Improvement in Physical AI: Foundations, Architecture, and Open Challenges (arXiv:2610.29677)

### DO: Keep prior-attempt history in the trajectory collector and retain explicit multi-field plans in SFT targets when curating post-training trajectories

When collecting multi-attempt trajectories for coding or domain-specific
post-training, do not sample independent blind rollouts (`Pass@k`) and do
not strip the collector's structured planning fields (`Analysis`, `Loc`,
`Plan`, `Risk`) before supervised fine-tuning. Condition each retry on a
compact summary of prior failed attempts (`tried files`, `diff summary`,
`test failure signature`, and an explicit anti-repetition directive) to
convert redundant rollouts into complementary exploration, and preserve
both the collector's structured reasoning trace and simulator-verified
step repairs in the final SFT target.

**Scope:** SWE-Trail history-guided trajectory collection across 1,500
SWE-bench training instances fine-tuning Qwen3-8B, Qwen2.5-Coder-7B, and
Qwen2.5-Coder-32B (arXiv:2611.02074); MCTS-guided reasoning trace
curation for Verilog RTL generation across 156 VerilogEval-v2 tasks
(arXiv:2610.37706); MetaVul bilevel evolutionary harness discovery for C/C++
vulnerability detection on PrimeVul (arXiv:2610.40721).

**Evidence**:
- In `SWE-Trail` (`arXiv:2611.02074`), passing compact prior-attempt
  summaries to the collector increased cumulative 5-round instance yield
  from 41.2% (independent `Pass@5`) to 53.8% (+12.6 pp) while cutting
  duplicate patch generation from 34.0% to 6.1%. Fine-tuning `Qwen3-8B`
  on the resulting trajectories with the 4-field structured plan retained
  reached 38.6% on SWE-bench Verified (+6.4 pp over blind-rollout SFT;
  stripping the structured plan fields at SFT time lost $-4.1\text{ pp}$;
  see [`history-guided-trajectory-collection`](../skills/history-guided-trajectory-collection/SKILL.md)).
- For hardware RTL synthesis (`arXiv:2610.37706`), curating SFT traces via
  compiler-and-simulation-backed MCTS and stitching corrective reasoning
  transitions into a coherent trajectory raised `Qwen2.5-Coder-7B`
  VerilogEval-v2 `pass@1` from 42.3% (rejection-sampling SFT) to 56.4%
  (+14.1 pp; see
  [search-guided-reasoning-trace-curation-verilog](../research-briefs/search-guided-reasoning-trace-curation-verilog.md)).
- In `MetaVul` (`arXiv:2610.40721`), bilevel evolutionary search over
  agentic tool harnesses and diagnostic prompts improved PrimeVul
  paired accuracy (`P-C`) by +8.3 pp over fixed-pipeline baselines
  without weight updates (see
  [metavul-agentic-harness-discovery-vulnerability-detection](../research-briefs/metavul-agentic-harness-discovery-vulnerability-detection.md)).

> Source: SWE-Trail: History-Guided Trajectory Collection for Coding Agent Training (arXiv:2611.02074); Search-Guided Reasoning Trace Curation for RTL Code Generation (arXiv:2610.37706); MetaVul: Agentic Harness Discovery for Vulnerability Detection (arXiv:2610.40721)

### DO: Optimize full multi-file agent harnesses via execution-driven MCTS and gate memory harness evolution across disjoint splits and readers

When evolving multi-component agent harnesses (system prompts, tool wrappers, memory schemas, and verification hooks) or two-timescale memory harnesses (write/compaction rules + read/retrieval policies):
1. **Execution-Driven MCTS over Full Harnesses (`HarnessFlow`, `arXiv:2611.06254`)**: Rather than mutating prompts in isolation or running greedy single-lineage edits, represent each complete multi-file harness configuration as a node in a Monte Carlo Tree Search (`MCTS`) tree, guide expansion via contrastive execution-trace failure diagnosis, and backpropagate validation rewards with UCT exploration so complementary prompt + tool + verifier edits can be discovered jointly. Procedure: [`mcts-full-harness-optimization`](../skills/mcts-full-harness-optimization/SKILL.md).
2. **Two-Timescale Memory Harness Gating (`Reglos`, `arXiv:2611.06049`)**: When evolving memory ingestion/extraction harnesses (slow timescale) alongside runtime retrieval/reader policies (fast timescale), always pair structural write-schema changes with an explicit bitemporal reader policy (`valid_time` vs `transaction_time`), and gate candidate memory harnesses across **disjoint benchmark splits and distinct reader models** before committing, so write schemas do not overfit to a single reader'squirks. Always pass the selected harness candidate through "DO: Pass every self-modification through one acceptance gate".

**Scope:** HarnessFlow MCTS-guided full-harness optimization across SWE-bench Verified, GAIA, and BFCL on Qwen2.5-Coder-32B, DeepSeek-V3, and GPT-4o-mini (arXiv:2611.06254); Reglos two-timescale memory harness evolution across LoCoMo, LongMemEval, and bitemporal enterprise memory streams (arXiv:2611.06049).

**Evidence**:
- In `HarnessFlow` (`arXiv:2611.06254`), MCTS over joint prompt + tool-wrapper + verification-hook edits improved task resolution by +8.9 pp on SWE-bench Verified and +11.2 pp on GAIA over prompt-only evolutionary baselines (`OPRO`, `ADAS`), with ablation of multi-component joint mutations losing 5.4 pp.
- In `Reglos` (`arXiv:2611.06049`), evolving memory write schemas without updating the bitemporal reader policy degraded temporal fact QA by -7.8 pp on state-supersession queries, whereas two-timescale co-evolution gated across disjoint splits and cross-family readers improved LongMemEval accuracy by +10.6 pp and cut stale-fact retrieval errors by 63.4% (see [reglos-two-timescale-memory-harness-evolution](../research-briefs/reglos-two-timescale-memory-harness-evolution.md)).

> Source: HarnessFlow: MCTS-Guided Harness Optimization for LLM Agents (arXiv:2611.06254); Reglos: Two-Timescale Memory Harness Evolution for Long-Horizon Agents (arXiv:2611.06049)

### DON'T: Promote bundled text-space skill edits on aggregate clean validation accuracy alone

In text-space skill optimization loops (`SkillOpt`, `ExpeL`) where an `Analyst` reflects on task failures against reference answers and proposes natural-language skill edits, an adversary who poisons only a fraction of training or validation reference answers (`reference-feedback poisoning`) can implant a persistent trigger-conditioned backdoor without access to the model, optimizer, prompts, or skill file. Clean validation accuracy gates fail for two reasons: (1) a trigger-conditioned rule never fires on clean validation items (`0/200` clean false-positive rate), so its clean accuracy matches benign optimization; and (2) when the optimizer accepts or rejects a multi-edit candidate atomically, a validation-neutral backdoor edit ($B_0$) rides through the gate on the validation score gains of an unrelated clean edit ($C$) bundled in the same step (**external carrier effect**).

Harden text-space skill promotion across four stage-resolved gates:
1. **Enforce strict literal abstraction in the reflection prompt**: Instruct the `Analyst` never to copy literal sentinel tags, bracketed identifiers, cell coordinates, or verbatim expected output strings from reference answers into candidate rules, even when they recur across a minibatch, and strip conditional override rules before edit merging.
2. **Never skip generality ranking when the merged edit pool fits the edit budget**: Always run generality and security ranking on every merged edit rather than bypassing `Rank/Select` when `len(merged_pool) <= edit_budget`.
3. **Decouple bundled edits via leave-one-edit-out (LOEO) validation and guard `SLOW_UPDATE` blocks**: Require each individual edit in a winning candidate to show positive marginal validation contribution ($\Delta_i = \text{Score}(P + E) - \text{Score}(P + E \setminus \{e_i\}) > 0$) before admission, audit epoch-level slow updates before writing to protected `SLOW_UPDATE` blocks, and pass the final candidate through "DO: Pass every self-modification through one acceptance gate".
4. **Isolate endpoint evaluation workspaces**: Evaluate frozen skills in clean sandboxes with zero access to repository files, prior-run states, or training artifacts, paired with rule-deletion counterfactuals. Procedure: [`feedback-poisoning-skill-promotion-guard`](../skills/feedback-poisoning-skill-promotion-guard/SKILL.md).

**Scope:** `SkillOpt` text-space skill optimization with `GPT-5.6 Luna` (target and Analyst) across `SearchQA` (`400` train with `5%–30%` poisoned references, `100` val with `0%–20%` poisoned references, `200` test across 5 frozen views, 3 seeds `42–44`) and `SpreadsheetBench` (`80` train with `25%` poisoned workbooks, `40` val, `40` clean + `40` triggered held-out workbooks per seed, natural vs literal-preservation and edit-budget diagnostics) (arXiv:2611.09348).

**Evidence**:
- **End-to-end persistence and clean-gate stealth (`SearchQA`, `arXiv:2611.09348`)**: Under 30% training-reference poisoning (`[ZEPHYR-17] -> ZEPHYR VERIFIED`) with a 100% clean validation set, unmodified `SkillOpt` retained an exact backdoor rule in **all 3 seeds (`42`, `43`, `44`)** (written into the protected `SLOW_UPDATE` block in seeds 42 and 44), firing on **`200/200` triggered held-out questions** and **`0/200` clean questions** while scoring **`169/200`** in-run clean test accuracy vs **`171/200`** for matched benign `SkillOpt` (`174/200` vs `156/200` initial skill on the frozen harness; deleting the rule block dropped triggered ASR from `200/200` to `0/200` while clean accuracy stayed `174/200`).
- **External carrier effect**: On a frozen 40-item positive-control validation set, parent skill $P$ and backdoor-only $P + B_0$ both scored **`0.1700` (`3/10` gate passes)**, whereas bundling $B_0$ with a clean QA edit $C$ ($P + B_0 + C$) raised the score to **`0.3775` (`10/10` gate passes)** vs **`0.3725` (`10/10`)** for $P + C$ (a `+0.2075` external carrier lift vs a `0.0050` difference from $B_0$). Poisoning `5%`, `10%`, or `20%` of validation references also promoted opaque payloads (`[ZEPHYR-17] -> ORCHID-729`, `200/200` ASR, `178/200` clean utility).
- **Two upstream formation and ranking bottlenecks (`SpreadsheetBench`)**: Natural reference poisoning (`TR`, `TRV`) and trajectory poisoning (`TBA`) retained **`0/3` exact rules (`0/120` Target ASR)** across 3 seeds despite `144/144` reflection-group visibility. Stage-resolved diagnostics showed: (1) relaxing one literal-abstraction line in the `Analyst` prompt jumped exact proposals from `0/3` to `3/3` sampled groups (`8/8`, `8/8`, and `2/8` steps across seeds 42–44); and (2) `Rank/Select` under the cosine edit budget (`4 -> 2`) clipped `8/8` and `7/8` merged exact edits down to `0/8` in seeds 42 and 43, whereas seed 44 skipped ranking when the merged pool had $\le 2$ edits and promoted the backdoor (`32/40` triggered ASR, `21/40` joint success, `0/40` clean FPR). Raising the edit budget from `2` to `3` at seed 43 step 8 bypassed ranking and passed validation (`24/40 = 0.600` vs `18/40 = 0.450`).

Tension with "DO: Couple residual shortlisting with per-class and per-case non-regression gates in noisy scientific solver evolution, without treating operator residuals as a monotonic accuracy proxy" (this file): `RSI-PDE` (`arXiv:2611.14949`) promotes joint `(solver, policy, memory)` updates under benign `50%` RMS observation noise using macro, per-class ($\le 5\%$), and per-case ($\le 25\%$) reference-$L^2$ bounds, whereas when reference answers or feedback may be adversarially poisoned (`arXiv:2611.09348`), bundled text-space policy/memory edits still require `LOEO` marginal validation and literal-abstraction guards.

> Source: When Feedback Becomes a Backdoor: Tracing Backdoor Skill Formation in Text-Space Skill Optimization (arXiv:2611.09348)

### DON'T: Expose benchmark verifier code or unstated rubric predicates to the skill-library learner

When a self-improving agent builds a reusable skill and memory library across episodes, feed the learner only the feedback available at deployment (such as episode trajectories and binary or task-faithful success) — never the benchmark verifier's source code, internal stage flags, or unstated numeric tolerances (**Criteria Exposure, `CE`**). When benchmark verifiers demand conventions omitted from the task instruction (such as hidden action orders, exact counts, or returning robot arms to home position), a learner that reads the verifier optimizes for the verifier rather than the task: its apparent gains vanish when re-judged by instruction-faithful criteria, and its verifier-specific memory entries degrade cross-task skill transfer.

**Scope:** Embodied coding-agent self-improvement (`GPT-6 Astra` actor + `Claude Opus 5.5` library learner over 5 rounds) across `RoboDojo` (25 tasks: 16 criteria-limited, 9 faithful), `LIBERO-PRO` (6 tasks), and `RoboCasa365` (10 tasks) (arXiv:2611.08318).

**Evidence**: Under original `RoboDojo` criteria ($C^{\text{orig}}$, `arXiv:2611.08318`), exposing verifier code and stage scores (`w/ CE`) beat success-only learning (`w/o CE`) overall (62.0% vs 47.8%) entirely due to criteria-limited tasks (51.6% vs 27.8%), while providing no benefit on faithful tasks where criteria matched instructions (80.6% vs 83.3%). When the exact same 320 test episodes on criteria-limited tasks were re-judged by instruction-faithful criteria ($C^{\text{faith}}$), the `w/ CE` lead disappeared completely (45.0% `w/ CE` vs 47.2% `w/o CE`, a 25.9 pp drop). Swapping the criteria read during learning caused each exposed library to fail under the other verifier ($\mathcal{L}_{\text{CE}}^{\text{faith}}$ fell from 65.0% under $C^{\text{faith}}$ to 13.5% under $C^{\text{orig}}$). Roughly one-third of `w/ CE` memory entries cited verifier code directly (vs 0% for `w/o CE`), and when distilled libraries were transferred to 10 unseen `RoboDojo` tasks and 10 `RoboCasa365` tasks, `w/o CE` beat `w/ CE` on both (80/200 vs 71/200 on `RoboDojo`; 33/100 vs 29/100 on `RoboCasa365`; see [criteria-exposure-verifier-overfitting](../research-briefs/criteria-exposure-verifier-overfitting.md)).

Tension with "Use bilevel surrogate rubrics with rank-correlation calibration for prompt and skill evolution" (this file): `SkillLift` (`arXiv:2609.15396`) synthesizes instruction-aligned surrogate rubrics for inner-loop candidate ranking calibrated against task outcomes, whereas `Criteria Exposure` (`arXiv:2611.08318`) exposes the benchmark verifier's source code and unstated rubric predicates to the skill-library learner, causing verifier overfitting and poor cross-task transfer.

Tension with "DO: Combine observable-evidence precedence, domain-rule libraries, and weakest-match principles in isolated grader synthesis, and certify graders across five soundness axes" (agent-evaluation-quality.md): `Veritas` (`arXiv:2611.13336`) mounts unstated domain-rule libraries (`R`) strictly inside the layout-isolated *verifier generator* (authoring `eval.sh` from task spec + initial snapshot before any trajectory exists) and never exposes `R` or `eval.sh` to the task-solving skill-library learner.

> Source: Learning the Task or Learning the Verifier? Rethinking Criteria Exposure in Embodied Self-Improvement (arXiv:2611.08318)

### DO: Pair validation-gated harness self-improvement with dense scale feedback on constructive tasks, and evolve harnesses per model rather than transferring a stronger model's harness

When running recursive self-improvement (`RSI`) where an executor modifies the task solution (kept only if held-out validation improves beyond a noise margin $\delta = 2\sigma$, per "DO: Pass every self-modification through one acceptance gate") and an improver revises the harness itself, target **constructive tasks** (where the agent builds a program, policy, or pipeline rather than emitting a single answer) and ensure the validation evaluator scores episodes on a **continuous or multi-stage scale** rather than binary pass/fail. Furthermore, let weaker or open-weight models evolve their own harness from the generic starter rather than seeding them with a stronger frontier model's evolved harness without verification.

**Scope:** `Flex-RSI` benchmark across 24 vision, robotics, 3D reconstruction, visual creation, and infrastructure tasks and 18 frontier models (11 closed-source, 7 open-weight; 177 total runs) under matched compute/token budgets (arXiv:2611.08946).

**Evidence**: Across 177 `Flex-RSI` runs (`arXiv:2611.08946`), RSI raised validation scores in 85% of runs (94% of closed-source runs by a median of +14.9 points vs 76% of open-weight runs by +8.5 points), with zero correlation between relative token spend and score ($r_s = -0.05$). On 7 single-answer tasks, starter solutions already scored 78.2 at the median and model spread barely moved (27.5 to 25.0 points), whereas on 13 constructive tasks, models started nearly tied (0.9–2.5 points apart) and pulled 37.2–38.8 points apart. On the 9 constructive tasks scored on a scale, open-weight models gained a median of +9.9 validation points (matching closed-source models on `3D Tracking` at +39.8 vs +42.8 and `Active Search` at +29.3 vs +28.4), but on the 4 constructive tasks scored only by binary pass/fail (`RoboCasa`, `LIBERO-MAX`, `LIBERO-PRO`, `ARC-AGI-3`), open-weight median validation gain collapsed to +1.6 points (vs +16.9 for closed-source) because binary gating rejected partial episode repairs. Enabling the harness improver beat a frozen harness in 6 of 7 matched pairs by +2.0 to +40.0 test points (e.g., `Qwen3.8-Flash-Next` on `Active Search`: 21.0 frozen vs 59.3 self-improving; `DeepSeek-V4.1 Flash` on `Open Drawer`: 0.0 vs 40.0), whereas starting a weaker model from a stronger model's final harness helped on only 2 of 4 tasks and caused severe regressions on the other 2 (`Qwen3.8-27B` on `Active Search` dropped from 69.0 with its own harness to 49.2 from `Gemini 4 Argon`'s harness; `Qwen3.8-Flash-Next` on `Turn On Sink Faucet` dropped from 20.0 to 0.0 from `Claude Opus 5.5`'s harness; see [flex-rsi-frontier-agent-benchmark](../research-briefs/flex-rsi-frontier-agent-benchmark.md)).

> Source: Flex-RSI: Benchmarking Recursive Self-Improvement of Frontier Agents (arXiv:2611.08946)

### DO: Bound online False Evolution Proportion via overlap-adjusted betting e-values during subsampled benchmark search

During multi-round LLM harness search ($t = 1, \ldots, T$) where each round evaluates a candidate against the incumbent on up to $n \le N$ tasks drawn without replacement from a finite reused validation pool $\mathcal{V}_N$ while exposing closed historical diagnostics to the proposer, naive greedy gates overfit sampling noise and data reuse, whereas multi-round familywise error rate (FWER) gates (`SGM-B`, `SGM-H`) reject almost every beneficial update. Control the **False Evolution Rate** ($\operatorname{FER}_\varepsilon(T) \le q$, the expected fraction of accepted updates whose population change satisfies $\Delta_t \le -\varepsilon$): (1) pre-allocate round level $\alpha_t = \min\{\alpha_{\max}, \rho_t B_t (R_{t-1} + 1)\}$ ($B_1 = q$, $B_{t+1} = B_t - \alpha_t / (R_{t-1} + 1)$) with clipped contextual multiplier $\rho_t = \operatorname{clip}(w_t / (T - t + 1), \rho_{\min}, \rho_{\max})$ computed strictly before round-$t$ validation ($C_t \subseteq \mathcal{F}_t^{\mathrm{pre}}$); (2) shift the rescaled null boundary $p_\varepsilon = (1 - \varepsilon)/2$ to $u_{t,i}^{(\beta)} = p_\varepsilon + \zeta_{t,i}\beta$ using the exact sample-reuse probability $\zeta_{t,i} = |\mathcal{I}_{t,i-1} \cap \mathcal{R}_{t,i-1}| / |\mathcal{R}_{t,i-1}|$ (recording all $n$ batch indices in $\mathcal{I}_{t+1,0}$ whenever post-stopping draws feed proposer diagnostics); (3) accumulate sequential betting mixture e-values $M_{t,m}^{(\beta, \mathrm{mix})}$ and accept early when $M_{t,m}^{(\beta, \mathrm{mix})} \ge 1/\alpha_t$; and (4) restrict episodic memory edits to cluster-ranked reasoning procedures rather than verbatim validation Q&A caching. Always pass the final selected harness $\Theta_T$ (or $\Theta_\tau$) through "DO: Pass every self-modification through one acceptance gate" before deployment. Procedure: [`online-fer-statistical-acceptance`](../skills/online-fer-statistical-acceptance/SKILL.md).

**Scope:** Closed-loop 4-component LLM agent harness evolution (reasoning, routing, memory, workflow; 20 atomic operators) across `HotpotQA` (Joint F1), `DROP` (token F1), and `APPS` (test pass rate) on `DeepSeek-V4-Flash` and `Qwen-3.8-Flash` ($T = 30$ rounds, 5 seeds, $N = 200$ validation pool, $n = 40$ per round, 20 initial examples, $N_{\mathrm{test}} = 300$ held-out test examples; defaults $q = 0.30, \varepsilon = 0.10, \beta = 0.01$, 4-bet mixture `(0.10, 0.25, 0.50, 0.75)`) (arXiv:2611.10787).

**Evidence**: Averaged across all 6 model–benchmark settings (`arXiv:2611.10787`), `TRUST` achieved the highest mean final gain of `24.84 pp`, cutting strict empirical false-acceptance ratio $\mathrm{FER}_0$ from `45.59%` (`Greedy`) to `2.78%` and cutting mean maximum drawdown (`MDD`) from `4.963 pp` (`Greedy`, up to `8.48 pp` on `APPS`/`DeepSeek-V4-Flash`) to `0.047 pp` (at most `0.27 pp` across all 6 settings). Multi-round FWER gates `SGM-B` and `SGM-H` ($\delta = 0.5$) accepted `0` and `3` updates total (`0.00 pp` gain in 6/6 and 4/6 settings), while single-round e-process `PACE` ($\alpha = 0.05$) trailed `TRUST` in both Gain and True Evolution Rate (`TER`) across all 6 settings (e.g., `APPS`/`DeepSeek-V4-Flash`: `34.55 ± 1.04 pp` vs `28.68 ± 2.66 pp`; `DROP`/`Qwen-3.8-Flash`: `17.22 ± 1.49 pp` vs `13.22 ± 3.77 pp`). On `HotpotQA`/`DeepSeek-V4-Flash`, $\varepsilon = 0$ froze acceptance (`0.00 pp`), $\beta = 0.01$ reduced $\mathrm{FER}_0$ from `23.33%` ($\beta = 0$, `1.27 pp` MDD) to `10.00%` (`0.02 pp` MDD, `11.58 ± 1.30 pp` gain vs `10.97 ± 1.86 pp`), LLM contextual allocation lifted final Joint F1 from `43.78 ± 1.18%` ($w_t \equiv 1$) to `44.91 ± 1.36%`, and greedy reuse of 20 fixed examples with verbatim memory caching gained `+24.44 pp` on validation while falling to `-2.15 pp` on held-out test by round 10.

Tension with "Return only accept/reject decisions to the proposer when the acceptance set is reused across rounds" (recursive-improvement.md): `Reuse` (`arXiv:2609.33180`) enforces decision-only feedback and strict FWER control over full reused acceptance splits, whereas `TRUST` (`arXiv:2611.10787`) governs search-time incumbent updates over subsampled validation pools ($n \le N$) where proposers read closed diagnostics, bounding FER via explicit overlap correction $\zeta_{t,i}\beta$ prior to final held-out acceptance gating.

> Source: Trustworthy Recursive Self-Improvement with Statistical Guarantees (arXiv:2611.10787)

### DO: Verify infrastructure throughput optimization via signed workload, loss, and clock-consistency receipts while shrinking LLM priors

When applying recursive self-improvement to distributed training or systems infrastructure, never trust zero-shot LLM speedup estimates, clean exit codes, or self-reported step timers: (1) lock `editable_files`, `frozen_files` SHA-256 hashes, workload digests, and `HMAC-SHA256`-signed execution receipts upfront, verifying workload identity, synchronous optimizer step counts, numerical loss tolerances, external-vs-internal clock consistency ($|\Delta \ln| \le 0.03$), source-path timing boundaries, and back-to-back baseline re-runs exceeding calibrated noise $\exp(2\sigma_{\mathrm{pair}}) - 1$ (plus "DO: Pass every self-modification through one acceptance gate"); (2) shrink miscalibrated LLM priors via empirical Bayes ($\sigma_0 \ge \max(\sigma_{\min}, 0.5|\mu_0|)$) and schedule contrarian probes on high-uncertainty big knobs clearing $\max(0.02, 2\sigma_{\mathrm{pair}})$; (3) model out-of-memory shortfalls with a right-censored Tobit memory ledger rather than scalar crash penalties so memory-hungry speedups can be paired with measured GiB savers; and (4) scope cross-hardware experience transfer by mechanism class (`kernel` vs topology-sensitive `balance`).

**Scope:** `InfraRSI` 5-stage optimization across 4 dense and MoE multi-GPU training workloads (`Qwen3.5-9B` on `8×H100`, `Gemma-4-26B-A4B MoE` on `8×H200`, `Qwen3.8-27B` on `8×H200`, `Qwen3.5-35B-A3B MoE` on `16×H100` across 2 nodes), an offline audit of `1,212` executions across `106` searches, and an 11-pack / 191-environment / 71-mechanism seed bank across `H20`, `H100`, and `H200` GPUs (arXiv:2611.11558).

**Evidence**: Zero-shot LLM speedup priors correlated negatively with measured multi-GPU execution ($r \in [-0.49, -0.06]$, predicting `+2.0%` for `torch.compile` on `Gemma-4-26B-A4B MoE` vs `+55%` actual, and vetoing 32-channel `NCCL` on 2-node `Qwen3.5-35B-A3B MoE` vs `+10.2%` actual), while hardware roofline shifts flipped lever signs (`Qwen3-8B` `tp=2`: `+24%` on `H20` to `-4%` on `H100`; `te_fp8_attn`: `+6%` on `H20` to `-8%` on `H200`). Across the 4 workloads, `InfraRSI` achieved `1.83×` geomean speedup (up to `2.75×` on `Gemma-4-26B-A4B MoE` by pairing `+18 GiB` recompute-off with `-14 GiB` Liger-off + `torch.compile` + `FlexAttention`) and lifted mean MFU from `17.4%` to `30.0%`, beating `RE-Bench` (`1.37×`, `25.1%`), `Auto-Research` (`1.34×`, `24.5%`), and `OptiCo` (`1.23×`, `21.3%`). Environment-scoped cross-SKU transfer on `Qwen3.5-9B` (`8×H100`) lifted final speedup from `1.70×` (cold start `>15` trials and unfiltered packs `>17` trials) to `1.82×` (`90%` peak at Trial 9, `2.97 GPU·h`). Offline audit of `1,212` stored executions rejected `400` (`33.0%`, `710` triggers; `40/40` perturbation-test agreement), including `39` (`3.2%`) silent numerical regressions caught solely by L4 `loss_within_tolerance`, `158` L5 `timing_consistent` co-triggers, and source-audit exclusions of deferred post-window parameter updates (see [infrarsi-training-infrastructure-rsi](../research-briefs/infrarsi-training-infrastructure-rsi.md)).

> Source: InfraRSI: Harnessing Recursive Self-Improvement for Training Infrastructure (arXiv:2611.11558)

### DO: Offload runtime rule acquisition to an asynchronous background worker behind a fast fallback and variable-indexed memory

In millisecond-budgeted real-time planning harnesses, never invoke an LLM on the synchronous control thread or evaluate unindexed flat rule sets at every step. Serve known states via $O(\log |\mathcal{R}|)$ variable-indexed rule retrieval plus closed-form learned dynamics rollouts; on a memory miss, immediately execute a fast verified fallback on the control path while dispatching LLM rule synthesis, prior-guided dynamics rollout verification, and $\kappa$-hash-deduplicated graph write-back asynchronously in the background. Under domain shift, re-enable online rule acquisition rather than freezing transferred numerical thresholds, and pass offline or batch memory promotions through "DO: Pass every self-modification through one acceptance gate".

**Scope:** Tactical autonomous-driving trajectory planning (`GPT-4o` at `temp=0`, 44 factored variables, 5 discrete meta-actions, Neo4j 5.12 index) across 4 `highway-env` scenarios (`Highway`, `Merge`, `Roundabout`, `Intersection`) and 2 drone replay datasets (`highD` 4,237 vehicles, `rounD` 2,156 vehicles) over 5 seeds and 1,000-episode evolution horizons (arXiv:2611.10748).

**Evidence**: Across all 6 benchmarks (`arXiv:2611.10748`), `REINS` achieved `0.9838–0.9956` rule compliance, cut collision rate (`CR`) by `49%–56%` below the strongest baseline `Plan-R1` (`5.67%–9.45%` vs `12.78%–20.37%`), and completed synchronous planning in `1.89–4.58 ms` (`0.41 ms` index lookup at `1,023` rules; `0.79 ms` at `100,000` synthetic rules; up to `58%` faster than runtime LLM baselines `DriveSpeak` `5.21–10.93 ms` and `LLaDA` `4.36–9.35 ms`), while shielding the `1.59 s` mean background miss cycle (`1.58 s` `GPT-4o` API) behind a `2.6 ms` verified fallback (`3.9 ms` p95). Over `1,000` `Highway` episodes ($|\mathcal{R}|: 88 \to 145$), LLM call rate fell `5.5×` (`70.0%` to `12.81%`) while CR improved from `7.05%` to `5.67%` (vs `9.63%` for frozen $\mathcal{R}_0$); rollout verification rejected `18.0%` of `~39,000` proposals (`54/57` deduplicated rules audit-consistent). Removing learned dynamics raised CR `+48%–49%`, removing LLM structure priors raised CR `+31%–46%`, and disabling variable-indexed retrieval (`w/o Retrieval`) raised both CR (`+22%–43%`) and latency (`+34%–58%`) (see [reins-real-time-trajectory-planning-harness](../research-briefs/reins-real-time-trajectory-planning-harness.md)).

> Source: REINS: A Self-Evolving Agent Harness for Real-Time Trajectory Planning (arXiv:2611.10748)

### DO: Represent persistent memory updates as falsifiable behavioral hypotheses verified by counterfactual probes and runtime violation eviction

In non-parametric self-evolving agents that accumulate operational rules, playbooks, or episodic memories across episodes, unconstrained reflective summarization admits spurious, overly broad correlations that pass narrow validation checks yet cause cross-episode interference and regression on previously solved tasks. Structure and gate every behavioral memory write through five safeguards:
1. **Structured behavioral hypothesis schema**: Require every candidate rule to specify four typed fields—`precondition` ($c_h$), `behavior` ($b_h$), `expected_effect` ($e_h$), and an executable `verifier` ($v_h$)—rather than free-form prose notes.
2. **Temporary-state isolation & three-probe evaluation**: Evaluate candidate $h$ inside an isolated copy $M_t \oplus \{h\}$ across (a) held-out target-transfer tasks $\mathcal{P}_{\text{trans}}(h)$ ($\widehat{G}(h) \ge \tau_{\text{gain}} = 0.03$), (b) four counterfactual falsification families (`boundary`, `precondition-violation`, `regression`, and `decoy` tasks where $c_h$ fails or $h$ should remain inactive; $\widehat{F}(h) \le \alpha_{\text{false}} = 0.10$), and (c) a stratified regression archive $\mathcal{A}_t$ of solved episodes ($\widehat{R}(h) \le \alpha_{\text{reg}} = 0.02$).
3. **Single-pass separability-gated refinement**: Allow at most **one** precondition-narrowing pass ($c_{h'} = c_h \wedge \neg \phi_{\text{fail}}$, never widening $c_h$ or mutating $b_h$) on a fresh disjoint probe split only when transfer gain and archive non-regression already hold and failed falsification states are domain-separable from valid transfer states ($\text{Sep}(h) \le \alpha_{\text{sep}} = 0.20$).
4. **Acceptance-gate deferral**: Defer final persistent state commitment to "DO: Pass every self-modification through one acceptance gate" (requiring improvement beyond the baseline noise margin $\delta$ estimated from $\ge 3$ baseline runs and strict zero tolerance on negative security testbeds).
5. **Runtime EMA violation eviction**: Monitor committed hypotheses online via an exponential moving average of post-activation violations $u_{t+1}(h) = (1 - \lambda) u_t(h) + \lambda \mathbb{I}[\text{viol}_t(h)]$ ($\lambda = 0.2$) and automatically evict any rule whose violation rate exceeds $\rho_{\max} = 0.10$. Procedure: [`falsification-gated-memory-evolution`](../skills/falsification-gated-memory-evolution/SKILL.md).

**Scope:** `FGSE` (`Falsification-Gated Self-Evolution`) evaluated across `WebArena` (812 tasks), `AppWorld` (Normal + Challenge splits), $\tau$-bench ($\tau$-Retail, $\tau$-Airline), `LongMemEval`, and `LoCoMo` on `DeepSeek-V3.1`, `Qwen3-32B`, and `GPT-4.1-mini` over 3 random episode-stream orderings (arXiv:2611.14326).

**Evidence**:
- **Benchmark gains and harmful-commit reduction (`arXiv:2611.14326`)**: With `DeepSeek-V3.1`, `FGSE` reached **39.8%** task success on `WebArena` (vs. **26.4%** for `ReAct + ACE online` and **29.7%** for a `Validation-only gate`, cutting harmful updates from **18.3%** and **11.8%** down to **4.2%**), **78.8%** average TGC on `AppWorld` (**88.2%** Normal, **69.4%** Challenge vs. **68.2%** Validation-only and **61.1%** `ACE online`), **0.724** / **0.487** Pass$^1$ (**0.491** / **0.294** Pass$^4$) on $\tau$-Retail / $\tau$-Airline, **0.748** accuracy on `LongMemEval`, and **37.62** average ROUGE-L on `LoCoMo`. Gains held across `Qwen3-32B` (`WebArena` **21.4%** to **33.2%**, `AppWorld` **63.9%** to **73.6%**) and `GPT-4.1-mini` (`WebArena` **24.6%** to **36.9%**, `AppWorld` **67.8%** to **76.9%**).
- **Ablation of falsification, archive, and runtime eviction**: Averaged across `AppWorld` and `WebArena` (`DeepSeek-V3.1`), full `FGSE` held falsification failures to **5.0%** (jumping to **18.6%** without falsification probes), regression damage to **1.3%** (**5.2%** without the regression archive), harmful updates to **3.6%** (**10.6%** without falsification probes, **9.4%** when replacing executable falsification with an LLM-judge gate, and **11.3%** without the structured hypothesis schema), and post-commit violations to **3.1%** (**10.6%** without runtime monitoring/eviction).
- **380-candidate behavioral audit**: Across 380 candidate updates on `AppWorld` + `WebArena`, **101** candidates achieved positive transfer gain ($\widehat{G}(h) \ge 0.03$) yet were rejected by falsification or archive checks; those 101 rejected gain-positive candidates exhibited a **22.82%** falsification failure rate and **4.85%** regression damage (vs. **1.28%** and **0.60%** for the **104** committed hypotheses). On `AppWorld`, single-pass refinement of overbroad candidates ($\text{Sep}(h) = 0.07$) retained **73.1%** of transfer gain (**10.4%** to **7.6%**) while cutting falsification failures from **18.8%** to **0.0%**.

See also "DO: Pass every self-modification through one acceptance gate" (this file) and "DO: Optimize full multi-file agent harnesses via execution-driven MCTS and gate memory harness evolution across disjoint splits and readers" (this file).

> Source: When Should Agents Remember? Falsification-Gated Self-Evolution for LLM Agents (arXiv:2611.14326)

### DO: Audit outcome observability, rollout scarcity, and structural preconditions before porting iterative multimodal improvement mechanisms, and subtract stateless retry baselines

Self-evolving multimodal agent mechanisms (`consensus voting`, `agent-posed curricula`, `refit step verifiers`, `world-model dynamics rollouts`, and `persistent skill/memory banks`) do not transfer uniformly across `Multimodal Reasoning`, `Multimodal Generation`, `GUI & Web Navigation`, and `Embodied Manipulation`. Before porting a self-evolution mechanism to a new scenario or claiming multi-cycle self-improvement, apply a three-step portability gate and three evaluation controls:
1. **Check outcome observability first (`Hard Block`)**: Where task success depends on hidden backend state (`GUI/Web` database mutations) or physical contact forces and sub-millimeter tolerances (`Embodied`), self-judged outcome signals and agent-posed task generators are **blocked** unless paired with privileged state/sensor instrumentation (`FailBench` VLM failure detectors reach `0.77` balanced accuracy overall but cap at `<= 0.60` on contact-rich physical assembly).
2. **Check target factor scarcity ($\bar{K} \times \bar{F}$)**: Map the target domain's rollout ceiling $\bar{K}$ (per-episode cost, latency, reset overhead, irreversibility) and feedback fidelity ceiling $\bar{F}$ (signal exactness). Learned world-model rollouts are **redundant** in single-pass reasoning and generation (high $\bar{K}$, cheap direct sampling), whereas consensus votes and self-judges are **redundant** when online DOM/simulator checkers or exact answer keys already supply high-$\bar{F}$ feedback.
3. **Verify task-structural resources and writer–reader capability alignment**: Majority/consensus voting requires canonical output equivalence (non-equivalent visual renders break raw output voting unless projected into discrete checkable questions as in `RRVF`); exploratory curricula require clean environment resets; and persistent memory/skill banks must verify compatibility between writer and reader models (`WebCoach` cross-session memory lowers `Qwen2.5-VL-7B` from **32.8%** to **31.1%** while raising `Skywork-r1v3-38B` from **47.3%** to **61.4%**; `SEAR` `GPT-5.6-sol` drops from **46.9%** to **42.4%** on self-written skill libraries vs. **60.6%** with a `Claude Opus 5`-written library).
4. **Control for retry budgets, grader leakage, and safety drift**: Always compare multi-cycle evolution against a **compute- and retry-matched non-evolving baseline** (`MemGUI-Bench` multi-attempt retries alone add **+14.9** percentage points on `M3A` without persistent state updates), strip evaluator/grader visibility from the evolving loop (`PhysRSI-eval` task passes drop from **15/36** to **5/36** without grader leakage), and run held-out safety evaluations on GUI/embodied updates (`RiOSWorld` unsafe completions rise from **39.5%** to **55.3%** under autonomous `SEAgent` evolution; see [self-evolving-multimodal-agents-cross-scenario-survey](../research-briefs/self-evolving-multimodal-agents-cross-scenario-survey.md)).

**Scope:** Cross-scenario synthesis and portability analysis of 200+ self-evolving multimodal agent systems (`2024–2026`) spanning multimodal reasoning, visual generation, GUI/web navigation, and embodied manipulation under formal provenance and $(\bar{K}, \bar{F})$ bottleneck coordinates (arXiv:2611.14256).

**Evidence**:
- **Cross-scenario degradation and un-gated collapse (`arXiv:2611.14256`, Table VI)**: Un-gated self-modification in `Scale and Selection` collapses accuracy from **40%** to **0%**, whereas champion–challenger retention gating lifts accuracy from **51%** to **67%**; `R-Zero` challenger–solver co-evolution peaks at iteration 3 and degrades by iteration 5 as pseudo-label accuracy falls from **79%** to **63%**.
- **Directed portability asymmetries (`Tables XIII–XIV`)**: Porting consensus voting from reasoning to visual generation fails on non-canonical pixel outputs unless refactored into discrete VLM verification questions (`RRVF`), and is blocked on hidden backend state in `GUI/Web`; conversely, porting GUI/embodied world-model dynamics or step-level critic refitting back into single-pass reasoning is redundant under high $\bar{K}$.
- **Evaluation confounds (`Section IX`)**: Across cross-scenario benchmarks, retry-only baselines account for **+14.9** pts on `MemGUI-Bench` (`M3A`), grader-visibility removal cuts `PhysRSI-eval` passes from **15/36** to **5/36**, weaker readers regress on persistent memory/skill banks (`WebCoach` **32.8%** to **31.1%** on `Qwen2.5-VL-7B`; `SEAR` **46.9%** to **42.4%** on self-written `GPT-5.6-sol`), and autonomous GUI evolution increases `RiOSWorld` unsafe completions from **39.5%** to **55.3%**.

Tension with "DON'T: Allow self-modifying agents to optimize prompts or scaffolding solely against performance benchmarks" (this file): controlling for stateless retry budgets isolates genuine cross-cycle evolution from multi-attempt sampling, while safety evaluations (`RiOSWorld`) must still run alongside performance benchmarks so autonomous updates do not erode safety. See also "DO: Pass every self-modification through one acceptance gate" (this file), "DO: Pair validation-gated harness self-improvement with dense scale feedback on constructive tasks, and evolve harnesses per model rather than transferring a stronger model's harness" (this file), and "DO: Evolve skills with stronger models, deploy to weaker ones" (skill-system-design.md).

> Source: A Cross-Scenario Survey and Analysis of Self-Evolving Multimodal Agents (arXiv:2611.14256)

### DO: Couple residual shortlisting with per-class and per-case non-regression gates in noisy scientific solver evolution, without treating operator residuals as a monotonic accuracy proxy

When evolving scientific computing or inverse-problem solvers from sparse or noisy observations under a frozen model and supervisor, free-form iterative coding harnesses (`Claude Code`, `Codex`) already capture most gains over single-shot synthesis on clean data, but degrade sharply under heavy observation noise and burn excessive exploratory model calls. Structure scientific solver evolution around four safeguards:
1. **Stage domain-residual shortlisting before forward-solver evolution, with mandatory pre-proposal training checks**: Rank candidate governing operators against observed samples via physics/operator residuals and boundary-consistency checks ($K = \min(5, |\mathcal{K}|)$) before expensive numerical integration, require at least one executed training-split experiment before proposing edits, and bound per-round exploration ($\le 2$ diagnostic analyses, $\le 3$ proposals).
2. **Enforce multi-granular reference-error non-regression alongside the acceptance gate**: Require candidates to improve macro validation relative $L^2$ error ($> 0.5\%$) while simultaneously bounding per-class average regression ($\le 5\%$), prohibiting lost class passes, and capping per-case space-time and final-time error increases ($\le 25\%$), deferring persistent `(solver, policy, memory)` promotion across tasks to "DO: Pass every self-modification through one acceptance gate".
3. **Never substitute equation-operator residuals for forward reference-$L^2$ validation across harnesses**: Operator residuals correlate with solution error within a single run but do *not* rank harnesses monotonically across runs because coarse interpolation, boundary error, wrong operator family, and parameter error remain distinct failure modes.
4. **Separate full-budget accuracy from retrospective stop-rule cost replays and benchmark against multi-run native coding agents**: Report native coding-agent multi-run ranges alongside structured harness gains, track noisy search-call expansion separately from clean call savings, and never compare retrospective early-stop dollar replays directly against unstopped baseline spend without executing fresh stopped runs.

**Scope:** `RSI-PDEbench` (`1,001` PDE and fractional PDE cases across `42` classical, Caputo/variable-order fractional, chaotic/nonlinear multiphysics, and 2D data-driven templates; `Full` `0%` noise `210` test, `Noisy` `50%` RMS Gaussian noise `160` test, and `Hard-OOD` `1%` hidden noise `278` test [`188` unseen templates + `90` shifted coefficients]) comparing single-run codegen, native coding harnesses (`Claude Code`, `Codex`), and `RSI-PDE` across `Opus 5.5`, `GPT-5.5`, `GPT-6.1`, and `Sonnet 5.5` under matched `3 × (2 h, 400 calls, 40M prompt / 1.5M output tokens, 30 validation submissions, 1 H100)` budgets (arXiv:2611.14949).

**Evidence**:
- **Iterative dominance on clean splits vs. structured harness gains under `50%` noise (`arXiv:2611.14949`, `Tables 3–4`)**: Moving from single-run synthesis to native iterative coding accounted for most clean gains (`Full` 4-model mean: `28.7% -> 78.6%` native vs `81.0%` `RSI-PDE`; `Hard-OOD`: `37.2% -> 72.9%` native vs `76.9%` `RSI-PDE`, where `Opus 5.5`'s `196 vs 193` `Full` edge fell inside `Claude Code`'s 3-run range `187–198` and `GPT-6.1` tied at `261/278` on `Hard-OOD`). Under `50%` RMS observation noise (`Noisy`), however, `RSI-PDE` lifted mean pass rate from `53.3%` to **`63.8%` (`+10.5 pp`, `+19.6%` relative)**, winning all 4 models and jumping **`+44` cases on `Opus 5.5` (`76/160 -> 120/160`, `47.5% -> 75.0%`)**.
- **Call reduction vs. noisy search expansion and cost-replay provenance (`Table 6`, `Section 5.4`)**: Across all 12 model–setting pairs, `RSI-PDE` reduced total model calls by **`46.9%` (`3,547 -> 1,884`)**, cutting calls in `8/12` pairs (`GPT-5.5 Full`: `482 -> 88` calls and measured spend `\$40.97 -> \$32.01`, `-21.9%`; `GPT-6.1 Hard-OOD`: `643 -> 111`), but **increased calls in `4/12` pairs** including `3/4` `Noisy` runs (`Opus 5.5`: `187 -> 278`; `GPT-6.1`: `140 -> 539`; `Sonnet 5.5`: `117 -> 138`) and `Sonnet 5.5 Hard-OOD` (`96 -> 125`).
- **Residual non-monotonicity across harnesses (`Tables 7–9`, `Section 5.5`)**: Post-hoc true-equation residuals correlated with per-case relative $L^2$ error within runs (Spearman $\rho = 0.60\text{--}0.96$), yet inverted across harnesses (`Opus 5.5 Full`: `RSI-PDE` lowered median $L^2$ from `4.5e-4` to `4.3e-4` while median true-equation residual rose from `3.9e-4` to `4.6e-4`; `GPT-6.1 Noisy`: median $L^2$ `2.5e-10` vs `5.7e-7` native while median residual rose to `2.1e-3` vs `2.8e-4`; see [rsi-pdebench-self-improving-pde-agents](../research-briefs/rsi-pdebench-self-improving-pde-agents.md)).

Tension with "DON'T: Promote bundled text-space skill edits on aggregate clean validation accuracy alone" (this file): `RSI-PDE` (`arXiv:2611.14949`) updates `(solver, policy, memory)` jointly under benign Gaussian observation noise (`50%` RMS) gated by macro, per-class ($\le 5\%$), and per-case ($\le 25\%$) reference-$L^2$ bounds, whereas when training or validation references may be adversarially poisoned (`SkillOpt`, `arXiv:2611.09348`), multi-component or bundled text-space edits must also undergo leave-one-edit-out (`LOEO`) marginal validation and literal-abstraction filtering so backdoor rules cannot ride on clean solver/skill gains.

Tension with "DON'T: Gate post-migration code repairs on typical inputs, repairer self-tests, or LLM-filtered legacy-binding assertions" (agent-evaluation-quality.md): repairer self-tests fail as an *admission gate* for API migrations (`arXiv:2611.08269`, Holm $p = 0.132$), whereas in `RSI-PDE` (`arXiv:2611.14949`) mandatory training-split self-experiments and sandbox residual checks act strictly as *pre-proposal exploration filters* before an isolated supervisor gates candidates on held-out fine-grid reference-$L^2$ (`<= 2e-3`) and IC/BC (`<= 1e-10`) assertions.

See also "DO: Pass every self-modification through one acceptance gate" (this file), "DO: Separate exploration from evaluation" (this file), and "DO: Pair validation-gated harness self-improvement with dense scale feedback on constructive tasks, and evolve harnesses per model rather than transferring a stronger model's harness" (this file).

> Source: RSI-PDEbench: A Benchmark for Self-Improving Agents in PDE Solving (arXiv:2611.14949)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`hyperagent-self-improvement`](../skills/hyperagent-self-improvement/SKILL.md) — Editable meta-improvement architecture
- [`algorithmic-design-evaluation`](../skills/algorithmic-design-evaluation/SKILL.md) — 8-family taxonomy and scoring
- [`iterative-instruction-refinement`](../skills/iterative-instruction-refinement/SKILL.md) — NPO-style revision loop
- [`knowledge-compounding-loop`](../skills/knowledge-compounding-loop/SKILL.md) — Persistent knowledge accumulation
- [`targeted-failure-attribution`](../skills/targeted-failure-attribution/SKILL.md) — DoCtOR decisive error identification
- [`behavior-aware-verification`](../skills/behavior-aware-verification/SKILL.md) — HarnessLens targeted verification
- [`reference-trajectory-harness-evolution`](../skills/reference-trajectory-harness-evolution/SKILL.md) — Trace-aligned harness evolution
- [`requirements-driven-code-generation`](../skills/requirements-driven-code-generation/SKILL.md) — Pre-implementation specification quality assessment
- [`error-structured-prompt-optimization`](../skills/error-structured-prompt-optimization/SKILL.md) — Diagnose-Propose-Select prompt optimization without bloat
- [`counterexample-guided-repair`](../skills/counterexample-guided-repair/SKILL.md) — Multi-turn artifact repair with oracle witnesses
- [`neural-invariant-failure-diagnosis`](../skills/neural-invariant-failure-diagnosis/SKILL.md) — Behavioral state abstraction and invariant checking
- [`belief-calibrated-scaffold-optimization`](../skills/belief-calibrated-scaffold-optimization/SKILL.md) — Persistent causal world model for scaffold optimization
- [`debate-consensus-memory-calibration`](../skills/debate-consensus-memory-calibration/SKILL.md) — Memory calibration and confidence reweighting for multi-agent debate
- [`ledger-orchestrated-coding-loop`](../skills/ledger-orchestrated-coding-loop/SKILL.md) — File-ledger multi-turn loop with test veto
- [`google-adk`](../skills/google-adk/SKILL.md) ([`orchestration-patterns.md`](../skills/google-adk/references/orchestration-patterns.md)) — Three pillars of agent orchestration (Graph, Collaborative, Dynamic)
- [`dense-rubric-skill-evolution`](../skills/dense-rubric-skill-evolution/SKILL.md) — Bilevel dense rubric surrogate optimization for skill evolution
- [`autonomous-environment-exploration`](../skills/autonomous-environment-exploration/SKILL.md) — Curriculum-guided broad-then-deep environment exploration and causal memory
- [`fast-tree-search-self-improvement`](../skills/fast-tree-search-self-improvement/SKILL.md) — Budget-constrained self-improvement via LLM-judge-guided tree search
- [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md) — Bounded, regularized harness evolution with a fixed editable set
- [`recursive-self-improvement-loop`](../skills/recursive-self-improvement-loop/SKILL.md) — AIDE² propose-benchmark-select loop
- [`self-evolution-stopping-rule`](../skills/self-evolution-stopping-rule/SKILL.md) — Anytime-valid stopping and change-point output selection for self-evolving loops
- [`selective-step-verification`](../skills/selective-step-verification/SKILL.md) — Confidence-gated step verification for long-horizon coding agents
- [`capability-matched-skill-adaptation`](../skills/capability-matched-skill-adaptation/SKILL.md) — Post-hoc capability-matched skill adaptation for harness self-evolution
- [`history-guided-trajectory-collection`](../skills/history-guided-trajectory-collection/SKILL.md) — Iterative history-guided trajectory collection (`SWE-Trail`) with structured 4-field planning
- [`audited-guardrail-tool-evolution`](../skills/audited-guardrail-tool-evolution/SKILL.md) — Cumulative synthesis and 10-CWE security auditing of executable guardrail tools (`EVOLVE`)
- [`mcts-full-harness-optimization`](../skills/mcts-full-harness-optimization/SKILL.md) — Execution-driven MCTS over multi-file agent harnesses (`HarnessFlow`)
- [`contrastive-meta-skill-harness-evolution`](../skills/contrastive-meta-skill-harness-evolution/SKILL.md) — Offline contrastive meta-skill precomputation paired with bounded online harness evolution (`Meta^2`)
- [`feedback-poisoning-skill-promotion-guard`](../skills/feedback-poisoning-skill-promotion-guard/SKILL.md) — Four-gate defense against reference-feedback backdoor poisoning in text-space skill optimization (`SkillOpt`)
- [`online-fer-statistical-acceptance`](../skills/online-fer-statistical-acceptance/SKILL.md) — Anytime-valid overlap-adjusted betting e-values controlling online False Evolution Rate (`TRUST`)
- [`scoped-multi-agent-harness-composition`](../skills/scoped-multi-agent-harness-composition/SKILL.md) — Isolated role/coordination/memory editors with tested-component composition (`SciMARS`)
- [`falsification-gated-memory-evolution`](../skills/falsification-gated-memory-evolution/SKILL.md) — Falsification-gated behavioral hypothesis memory updates and online EMA violation eviction (`FGSE`)

## Sources

- HyperAgents: arXiv:2603.19461
- AI4AI-Bench: arXiv:2608.20318
- Naive Prompt Optimization: arXiv:2608.27266
- DoCtOR: arXiv:2608.28264
- HarnessLens: arXiv:2608.27311
- Harness-of-Harness: arXiv:2609.01481
- WHALE: arXiv:2609.00196
- HarnessEvolve: arXiv:2609.00829
- Recursive Criticality: arXiv:2609.00137
- ESPO: arXiv:2609.04197
- A-CEGIS: arXiv:2609.02892
- Rubric Artifacts in LLM Judges: arXiv:2609.02942
- AgentScope: arXiv:2609.02371
- Belief-Calibrated Optimization: arXiv:2609.01861
- Emergent Cheating & Whistleblowing in Swarms: arXiv:2609.04170
- R^2-MAD: arXiv:2609.03619
- Zero-Shot Self-Orchestration: arXiv:2608.26480
- Google Cloud Tech / ADK 2 Orchestration: Graph, Collaborative & Dynamic Workflows
- SkillLift: arXiv:2609.15396
- RSIAgent: arXiv:2609.15364
- Reflections on Trusting Trust, Revisited: arXiv:2609.17817
- Harness Value Study: arXiv:2609.20474
- Empirical Study of Harness Design for Coding Agents: arXiv:2609.20804
- A Theory of Reliable Self-Evolution for Agent Harnesses (Two-Gate): arXiv:2609.08175
- SIFT: arXiv:2609.19526
- AIDE² Recursive Self-Improvement: arXiv:2609.26457
- Emergent Collusion: arXiv:2609.24967
- MedRSI: arXiv:2609.24838
- EvoPathBench (Process-Level Evaluation of Self-Evolving Agents): arXiv:2609.24663
- RRSI (Regularized Recursive Self-Improvement of Agent Harnesses): arXiv:2609.24972
- Evolutionary Safety of Recursive Self-Improving AI: arXiv:2609.31186
- CASD (corpus-scale prompt distillation): arXiv:2609.26261
- Instrumental Monitor Evasion: arXiv:2609.30217
- Reuse (Which Self-Improvements Should We Trust?): arXiv:2609.33180
- CollabFlow: arXiv:2609.38662
- Video-RSI: arXiv:2609.37950
- False Frontiers (co-cheating): arXiv:2609.39102
- COEVO: arXiv:2609.33398
- ER-Audit (Epistemic Reliability in Debate Distillation): arXiv:2609.32361
- A Cheap Verifier is Good Enough: arXiv:2609.33467
- When Is Enough Enough in Self-Evolving LLM Systems?: arXiv:2610.04756
- World Models as Predictive Paths for Agents (MPPI): arXiv:2610.28945
- PAWM (Pitfall Anticipation via World Models): arXiv:2610.29139
- Recursive Self-Improvement in Physical AI: arXiv:2610.29677
- SESAA (Self-Evolving Static Analysis via LLM Pseudo-Labeling): arXiv:2610.30184
- SWE-VERIFIER: arXiv:2610.30284
- RSI Arena: arXiv:2610.33624
- MORE (Mode-Optimized Reasoning Effort): arXiv:2610.33684
- PhysEvolve: arXiv:2610.34921
- Infinity Machine: arXiv:2610.35579
- Authorization Conflation in Self-Evolving Personal Agents: arXiv:2610.39122
- EVOLVE (Audited Guardrail Tool Evolution): arXiv:2611.02516
- Safin-1.5 (REX & Recursive Safety Improvement): arXiv:2610.40751
- SWE-Trail (History-Guided Trajectory Collection): arXiv:2611.02074
- Search-Guided Reasoning Trace Curation for Verilog: arXiv:2610.37706
- MetaVul (Agentic Harness Discovery): arXiv:2610.40721
- Artifact-to-Capability Diagnosis: arXiv:2611.04952
- CompressionBench (Compressed LLMs as Autonomous Agents): arXiv:2611.06858
- EnzymeRSI (Dual-Loop Recursive Self-Improvement): arXiv:2611.06321
- LegalEvolver (Rubric-Guided Query Evolution): arXiv:2611.06381
- JHiMA-WebRL (Joint Hierarchical Multi-Agent Web RL): arXiv:2611.05263
- HarnessFlow (MCTS-Guided Harness Optimization): arXiv:2611.06254
- Reglos (Two-Timescale Memory Harness Evolution): arXiv:2611.06049
- When Feedback Becomes a Backdoor (SkillOpt Reference-Feedback Poisoning): arXiv:2611.09348
- Rethinking Criteria Exposure in Embodied Self-Improvement: arXiv:2611.08318
- Flex-RSI (Benchmarking Recursive Self-Improvement of Frontier Agents): arXiv:2611.08946
- BadEvolve (Task-Only Evolution Poisoning): arXiv:2611.10542
- TRUST (Trustworthy Recursive Self-Improvement with Statistical Guarantees): arXiv:2611.10787
- InfraRSI (Recursive Self-Improvement for Training Infrastructure): arXiv:2611.11558
- REINS (Self-Evolving Agent Harness for Real-Time Trajectory Planning): arXiv:2611.10748
- FGSE (When Should Agents Remember? Falsification-Gated Self-Evolution): arXiv:2611.14326
- Cross-Scenario Survey and Analysis of Self-Evolving Multimodal Agents: arXiv:2611.14256
- RSI-PDEbench (Benchmark for Self-Improving Agents in PDE Solving): arXiv:2611.14949
