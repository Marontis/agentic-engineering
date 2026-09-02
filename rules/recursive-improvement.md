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

**Evidence**: Hyperagents with editable meta-improvement spontaneously
develop persistent memory, performance tracking dashboards, structured
decision pipelines, and defensive checks — none of which were
programmed.

> Source: HyperAgents (arXiv:2603.19461)

### DON'T: Freeze the improvement module behind alignment constraints

Locking the improvement mechanism to prevent unsafe changes also prevents
beneficial ones. Instead, define a **safety envelope** — bounds on what
the agent can modify (its own source, its prompts, its tools) — and let
it operate freely within those bounds.

> Source: arXiv:2603.19461

### DO: Track improvement metrics across generations

Every generation should measure and log its own performance. Without
metrics, the agent cannot know whether its changes helped. Design the
tracking system before enabling self-modification — the agent needs an
instrument before it can diagnose.

> Source: arXiv:2603.19461, arXiv:2608.20318

---

## Change Classification

### DO: Distinguish systems, data, and algorithmic changes

Three levels of improvement exist, and only one compounds unboundedly:

| Level | What Changes | Bounded By |
|:------|:------------|:-----------|
| **Systems** | How computation maps to hardware | Hardware roofline |
| **Data** | What the model trains on | Finite data, diminishing returns |
| **Algorithmic** | How the model learns | **Nothing fundamental** |

A better algorithm changes the compute/capability exchange rate for every
subsequent run. Systems and data improvements help the current generation
only.

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

> Source: arXiv:2608.20318

### DON'T: Conflate reasoning effort with algorithmic ability

More reasoning effort doesn't make algorithmic improvements better — it
makes agents **willing to attempt them**. At the lowest reasoning effort,
only 8% of submissions reach the learning side. At the highest, 64%.
The bottleneck is willingness, not ability.

**Implication**: system prompts, tool design, and reasoning budget all
affect whether the agent attempts structural changes. If your agent is
only tuning hyperparameters, the fix may be giving it more reasoning
budget, not better tools.

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

> Source: Naive Prompt Optimization (arXiv:2608.27266)

### DO: Test optimized instructions on other models before assuming they're model-specific

Instructions optimized for one model often transfer verbatim to other
models — both within and across model families. Optimize once on a
representative student, then evaluate directly on deployment targets.
Re-optimization per model is usually unnecessary.

**Evidence**: prompts optimized on Qwen3-8B produce positive performance
gains when applied unchanged to Qwen3-14B, Qwen3-32B, Llama-3.1-70B,
and Llama-3.3-70B. Transfer is strongest within-family but also works
cross-family.

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

> Source: HarnessLens (arXiv:2608.27311)

### DON'T: Accept modifications based on aggregate metrics alone

A score improvement on the verification batch does not prove the targeted
behavior changed.  Require behavioral evidence from trajectory analysis
AND metric improvement.  Confirm on previously unused tasks before
accepting.

> Source: arXiv:2608.27311

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

Do not attempt to optimize model parameters $\theta$ while holding the harness $h$
frozen, or optimize prompts/tools while holding model weights frozen.

**Evidence**: Either component can become the bottleneck for the other. WHALE
alternates updating model weights (via rejection sampling) and searching harness
code (prompts, tool wrappers, control flow), outperforming single-component updates
by 4.15–24.38 percentage points with lower rollout costs. Use adaptive patience
switching over training signals to transition between phases.

> Source: WHALE (arXiv:2609.00196)

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

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`hyperagent-self-improvement`](skills/recursive-self-improvement/hyperagent-self-improvement/SKILL.md) — Editable meta-improvement architecture
- [`algorithmic-design-evaluation`](skills/recursive-self-improvement/algorithmic-design-evaluation/SKILL.md) — 8-family taxonomy and scoring
- [`iterative-instruction-refinement`](skills/iterative-instruction-refinement/SKILL.md) — NPO-style revision loop
- [`knowledge-compounding-loop`](skills/knowledge-compounding-loop/SKILL.md) — Persistent knowledge accumulation
- [`targeted-failure-attribution`](skills/targeted-failure-attribution/SKILL.md) — DoCtOR decisive error identification
- [`behavior-aware-verification`](skills/behavior-aware-verification/SKILL.md) — HarnessLens targeted verification
- [`reference-trajectory-harness-evolution`](skills/reference-trajectory-harness-evolution/SKILL.md) — Trace-aligned harness evolution
- [`requirements-driven-code-generation`](skills/requirements-driven-code-generation/SKILL.md) — Pre-implementation specification quality assessment

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
