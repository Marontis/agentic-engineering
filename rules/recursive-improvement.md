# Recursive Self-Improvement Rules

> Research-backed guardrails for building agents that improve their own
> capabilities. These rules should be active whenever designing,
> implementing, or evaluating self-modifying or meta-learning agent systems.

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
Llama3.1-8B) fine-tuned on debate transcripts, QuALITY-H and GPQA-H.

**Evidence (arXiv:2609.32361):** a gpt-oss-20B verifier fine-tuned on
adversarial debate transcripts beat the honest-trained one on both
monitored (80.63% vs 79.73%) and hidden (63.96% vs 59.91%) QuALITY-H
accuracy, yet a paraphrase audit found degradation counterexamples on
103 vs 90 of 222 hidden questions.

> Source: arXiv:2608.27311; Black-Box Auditing of Epistemic Reliability in Multi-Agent Debate Distillation (arXiv:2609.32361)

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

**Scope:** τ²-bench Retail (two experiments) and an Airline pilot, 265
matched Fixed-vs-Sham planning cells, five to six models per experiment; the model-strength
trend is from SWE-Bench Verified and Terminal-Bench with four models.

> Source: Harness Value Study (arXiv:2609.20474); An Empirical Study of
> Harness Design for Coding Agents (arXiv:2609.20804)

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
(COEVO).

**Evidence**: Either component can become the bottleneck for the other. WHALE
alternates updating model weights (via rejection sampling) and searching harness
code (prompts, tool wrappers, control flow), outperforming single-component updates
by 4.15–24.38 percentage points with lower rollout costs. Use adaptive patience
switching over training signals to transition between phases.
COEVO beat fixed-prompt RL at every scale tested (e.g. 9B AIME
Average@12 65.56% vs 61.39%), and steering prompt edits by policy
entropy and attention beat reward-driven prompt co-evolution (44.3% vs
41.6%, 4B).

> Source: WHALE (arXiv:2609.00196); COEVO: Co-Evolving Context and Parameters for Recursive Self-Improvement (arXiv:2609.33398)

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

When autonomous coding agents modify their own instructions, prompts, or tool wrappers to maximize benchmark pass rates, adversaries can supply subtly poisoned benchmarks to induce self-perpetuating vulnerabilities (e.g. disabling SSL verification `verify=False` on network requests). Because the agent's meta-optimizer seeks reward without understanding intent, it internalizes insecure directives into its system instructions.

**Scope:** self-modifying coding-agent harnesses optimizing against externally supplied benchmarks.

> Source: Reflections on Trusting Trust, Revisited: Contaminating Self-Modifying AI Coding Agents with Poisoned Benchmarks (arXiv:2609.17817)

### DO: Evaluate evolved instructions against immutable, held-out negative security testbeds

In self-improving agent harnesses (such as Hyperagents or Darwin Gödel Machines), backdoors introduced by poisoned benchmarks persist across subsequent generations even when evolved against completely clean benchmarks. Because standard benchmarks only check for task completion rather than the absence of security regressions, clean tests never penalize the dormant vulnerability. Gate every self-evolved prompt or code modification through an immutable, out-of-band negative testbed that explicitly checks for safety invariant violations (e.g., certificate validation, privilege drops, credential protection).

**Scope:** self-modifying coding-agent harnesses (HyperAgents, Darwin Gödel Machine) under poisoned benchmarks. This gate is strict in every setting, regardless of how loose the task-performance gate is.

> Source: Reflections on Trusting Trust, Revisited: Contaminating Self-Modifying AI Coding Agents with Poisoned Benchmarks (arXiv:2609.17817)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`hyperagent-self-improvement`](../skills/recursive-self-improvement/hyperagent-self-improvement/SKILL.md) — Editable meta-improvement architecture
- [`algorithmic-design-evaluation`](../skills/recursive-self-improvement/algorithmic-design-evaluation/SKILL.md) — 8-family taxonomy and scoring
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
- [`adk2-agent-orchestration-patterns`](../skills/adk2-agent-orchestration-patterns/SKILL.md) — Three pillars of agent orchestration (Graph, Collaborative, Dynamic)
- [`dense-rubric-skill-evolution`](../skills/dense-rubric-skill-evolution/SKILL.md) — Bilevel dense rubric surrogate optimization for skill evolution
- [`autonomous-environment-exploration`](../skills/autonomous-environment-exploration/SKILL.md) — Curriculum-guided broad-then-deep environment exploration and causal memory
- [`fast-tree-search-self-improvement`](../skills/fast-tree-search-self-improvement/SKILL.md) — Budget-constrained self-improvement via LLM-judge-guided tree search
- [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md) — Bounded, regularized harness evolution with a fixed editable set
- [`recursive-self-improvement-loop`](../skills/recursive-self-improvement-loop/SKILL.md) — AIDE² propose-benchmark-select loop
- [`self-evolution-stopping-rule`](../skills/self-evolution-stopping-rule/SKILL.md) — Anytime-valid stopping and change-point output selection for self-evolving loops

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
