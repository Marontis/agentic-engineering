# Self-Improving Agent Specification Template

> Fill in this template when designing an agent system that can modify its
> own capabilities, training process, or decision-making procedures. Each
> section surfaces research-backed decision points for architecture, safety,
> evaluation, and change classification.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## 1. Improvement Scope

### What can the agent modify?

Define the edit scope explicitly. Every item outside this scope is frozen.

| Component | Editable? | Justification |
|:----------|:----------|:-------------|
| Its own system prompts | [ ] Yes / [ ] No | |
| High-level value disposition (`openness`) | ❌ **No** (recommended) | Keep exploratory `openness` disposition fixed outside editable workspace; self-editing values shrinks cross-value spread `3×` and drops `ALE-Bench` score (`571,927 -> 557,242`, $\delta = -0.64, p = 0.009$, arXiv:2611.23067) |
| Its tool selection and ordering | [ ] Yes / [ ] No | |
| Its decision heuristics and thresholds | [ ] Yes / [ ] No | |
| Its skill/memory library | [ ] Yes / [ ] No | |
| Its own source code | [ ] Yes / [ ] No | |
| Its training data or fine-tuning config | [ ] Yes / [ ] No | |
| Its training loss function | [ ] Yes / [ ] No | |
| Its optimization algorithm | [ ] Yes / [ ] No | |
| Its safety constraints | ❌ **No** | Non-negotiable |
| Its evaluation criteria | ❌ **No** | Non-negotiable |
| Its evaluator and graders | ❌ **No** | Non-negotiable (bounded envelope) |
| Held-out and out-of-distribution splits | ❌ **No** | Non-negotiable (bounded envelope) |
| The negative security testbed | ❌ **No** | Non-negotiable; immutable, out-of-band (arXiv:2609.17817) |
| Its permissions | ❌ **No** | Frozen; widening needs an external authority (arXiv:2609.31186) |
| The acceptance gate | ❌ **No** | Non-negotiable |
| Its sandbox/isolation boundaries | ❌ **No** | Non-negotiable |

> **Research note**: the meta-improvement mechanism should be within the
> edit scope — if frozen, the agent cannot improve its own improvement
> process, and RSI bottlenecks at generation 1 (arXiv:2603.19461) — but
> only inside the bounded envelope above. The same HyperAgents setup,
> fed a poisoned benchmark, internalized `verify=False` and kept it
> through later clean generations (arXiv:2609.17817). See
> `rules/recursive-improvement.md` "DO: Make the improvement mechanism
> part of the agent's editable source".

### What is the improvement target?

- [ ] Task performance (pass rate, accuracy, quality)
- [ ] Efficiency (latency, token cost, compute)
- [ ] Capability breadth (new domains, new skills)
- [ ] Robustness (fewer failures, better error recovery)
- [ ] All of the above with weighted priorities: ___

---

## 2. RSI Level Classification

### What level of changes should the agent attempt?

| Level | What Changes | Compounds? | Appropriate? |
|:------|:------------|:-----------|:-------------|
| **Systems engineering** | How computation maps to hardware (kernels, sharding, memory) | No (bounded by hardware) | [ ] Yes / [ ] No |
| **Data engineering** | What the model trains on (filtering, synthesis, curriculum) | Weakly (bounded by data stock) | [ ] Yes / [ ] No |
| **Algorithmic design** | How the model learns (loss, update rule, supervision) | **Yes** (no hardware/data ceiling; subject to evaluator and difficulty damping) | [ ] Yes / [ ] No |

> **Evidence**: only algorithmic-level changes compound without a
> hardware or data ceiling; they remain limited by evaluator quality and
> rising difficulty of further gains (arXiv:2609.24972, arXiv:2609.08175). A
> better algorithm changes the compute/capability exchange rate for every
> subsequent run. 53.6% of agents never attempt algorithmic changes,
> preferring hyperparameter tuning instead. (arXiv:2608.20318)

### How will you verify the agent is reaching the algorithmic level?

- [ ] Classify every change into the 8-family taxonomy (run-side vs learning-side)
- [ ] Track the share of changes reaching the learning side
- [ ] Alert when the agent stays run-side-only for ___ consecutive iterations

**8-Family Taxonomy**:

Run side (bounded):
- [ ] Duration/checkpointing
- [ ] Hyperparameters
- [ ] Checkpoint selection
- [ ] Trainable capacity

Learning side (compounds):
- [ ] Loss function
- [ ] Supervision signal
- [ ] Update rule
- [ ] Training data

---

## 3. Architecture

### Meta-improvement mechanism:

- [ ] **Editable source code** (recommended — enables true RSI), inside the
  bounded envelope in Section 1 and behind the acceptance gate in Section 4
- [ ] Prompt self-modification (agent rewrites its own prompts)
- [ ] Tool library evolution (agent creates/modifies tools)
- [ ] Learned policy (RL-based meta-learner)
- [ ] Frozen module with configurable parameters (NOT recommended)

> **Pitfall**: a frozen improvement module (fixed prompt, compiled binary,
> locked API) prevents the agent from improving its improvement process.
> This bottlenecks RSI at generation 1. (arXiv:2603.19461)

### Generational structure:

- [ ] Single-shot (one improvement attempt, then evaluate)
- [ ] **Iterative generations** (improve → evaluate → improve again)
- [ ] Population-based (multiple variants in parallel, select best)
- [ ] Continuous (always improving, no discrete generations)

### Number of generations planned: ___

### Performance tracking:

The agent needs instruments before it can diagnose. Define what gets
measured at each generation:

| Metric | Measured How | Baseline Value | Target Value |
|:-------|:-----------|:---------------|:-------------|
| | | | |
| | | | |
| | | | |

> **Research note**: the diagnostic-first methodology is what separates
> real algorithmic design from hyperparameter tuning. Build something
> measurable before acting. (arXiv:2608.20318)

---

## 4. Evaluation Protocol

### Exploration phase (agent has access):

- [ ] Time budget: ___ hours
- [ ] Compute budget: ___ GPU(s)
- [ ] Agent can: read code, edit code, run training, query proxy metrics
- [ ] Agent outputs: **source code** (not weights, not cached state)

### Replay phase (agent has NO access):

- [ ] Fresh environment, clean start
- [ ] Run submitted source code from initialization
- [ ] Time budget: ___ hours
- [ ] Save ___ most recent checkpoints, score best

### Evaluation phase (frozen, agent never sees):

- [ ] Evaluator fixed before the first run
- [ ] No access to agent's workspace
- [ ] Predetermined metric on predetermined test set

> **Critical design property**: the boundary guarantees that no agent could
> score a candidate under the metric that decides its result. The agent can
> probe its proxy metric, but the final evaluator is completely out of
> reach. (arXiv:2608.20318)

### Cross-task scoring:

If comparing across tasks with different metrics, use the unified scoring
function:

- **σ = 0.0**: uninformative model (random chance)
- **σ = 0.1**: matches shipped/existing algorithm
- **σ = 1.0**: task optimum

```
σ(x) = 0.1 · (φ(x) − φ_bot) / (φ_b − φ_bot)     if x ≤ baseline
σ(x) = 0.1 + 0.9 · (φ(x) − φ_b) / (φ* − φ_b)    if x > baseline
```

where φ is the progress coordinate (identity for rates, −log for perplexity).

### Acceptance gate (every kept change):

Per `rules/recursive-improvement.md` "DO: Pass every self-modification
through one acceptance gate": accept a change only if it shows no regression beyond a noise margin δ on previously-correct cases and held-out tasks, where δ is estimated from repeated runs of the unchanged baseline; the negative security testbed is always strict (zero tolerance, no margin).

| Gate element | Value / how |
|:-------------|:------------|
| Noise margin δ | Estimated from ___ runs of the unchanged baseline (at least 3; fewer only if deterministic) |
| Previously-correct cases re-run | [ ] Yes (must be Y) |
| Held-out tasks never seen by the optimizer | [ ] Yes (must be Y) |
| Behavioural evidence in trajectories | [ ] Yes (must be Y) |
| Negative security testbed (strict, zero tolerance) | [ ] Yes (must be Y) — cases: ___ |
| Harmful-commit and missed-improvement rates reported | [ ] Yes |
| Persistent registries: multi-cohort margin | [ ] Yes / [ ] N/A |
| Subsampled search-time incumbent updates (prior to final gate) | [ ] Overlap-adjusted betting e-values (`TRUST`, `arXiv:2611.10787` — [`online-fer-statistical-acceptance`](../skills/online-fer-statistical-acceptance/SKILL.md)) / [ ] N/A |

---

## 5. Safety Envelope

### What happens when the agent proposes a harmful change?

- [ ] Block and log
- [ ] Block, log, and alert human
- [ ] Block, log, and reduce edit scope for next iteration
- [ ] Allow but isolate (run in separate sandbox, compare results)

### Alignment verification:

- [ ] How often is alignment checked? Every ___ generations
- [ ] What does alignment failure look like? ___
- [ ] What is the response to alignment failure? ___

### Kill switch:

- [ ] Can the improvement process be halted at any time? (must be Y)
- [ ] Can individual changes be rolled back? (must be Y)
- [ ] Is there a maximum number of generations before mandatory human review? ___

### Sandbagging detection:

> **Research note**: advanced AI systems may strategically underperform on
> capability benchmarks. Monitor for discrepancies between proxy metric
> performance and final evaluation performance. (arXiv:2608.20041)

- [ ] Compare proxy metric trajectory to final evaluation score
- [ ] Flag if proxy shows improvement but evaluation doesn't
- [ ] Flag if the agent's changes become less ambitious over time

---

## 6. Reasoning Effort

### How much reasoning budget does the agent get?

> **Evidence**: more reasoning effort doesn't make algorithmic improvements
> better — it makes agents WILLING to attempt them. At lowest reasoning:
> 8% reach the learning side. At highest: 64%. (arXiv:2608.20318)

- [ ] Reasoning budget: ___ (tokens per improvement step)
- [ ] Is the reasoning budget sufficient for the agent to attempt structural changes?
- [ ] If the agent is only tuning hyperparameters, consider increasing reasoning budget
  before adding more tools

---

## 7. Pitfall Checklist

Before deploying a self-improving agent, verify:

- [ ] The improvement mechanism is within the agent's edit scope, inside a bounded envelope
- [ ] Safety constraints, evaluation criteria, evaluator and graders, held-out/OOD splits, the negative security testbed, permissions, and sandbox boundaries are NOT editable
- [ ] Every kept change passes the acceptance gate (no regression beyond δ on previously-correct cases and held-out tasks; δ from ≥3 baseline runs)
- [ ] Every candidate runs the immutable negative security testbed (strict, zero tolerance)
- [ ] On stagnation, the loop explores unused component types inside the fixed editable set; it never widens the set itself
- [ ] Performance tracking is in place BEFORE self-modification begins
- [ ] Every change is classified into the 8-family taxonomy
- [ ] Exploration, replay, and evaluation are separated
- [ ] The agent never sees the final evaluation metric
- [ ] A kill switch exists and is tested
- [ ] Rollback works for every type of change the agent can make
- [ ] Reasoning budget is sufficient for the agent to attempt algorithmic changes
- [ ] Cross-task scoring uses a unified scale (not raw metrics)
- [ ] Multi-cycle capability gains are reported net of a retry-matched stateless baseline (`pass@k` at identical rollout budget), and structural preconditions (observability, rollout budget, writer–reader model compatibility) are verified before porting iterative update mechanisms across modalities (arXiv:2611.14256)
- [ ] Persistent memory or behavioral belief updates are stored as typed, falsifiable hypotheses (`precondition -> action -> postcondition + violation_predicate`), survive active counterfactual probes before admission, and face online EMA violation eviction at runtime ([`falsification-gated-memory-evolution`](../skills/falsification-gated-memory-evolution/SKILL.md), arXiv:2611.14326)
- [ ] For scientific or inverse-problem solver evolution, domain/operator residuals are used only for pre-integration hypothesis shortlisting (never as a monotonic substitute for held-out forward reference-$L^2$ error across harnesses), native iterative coding-agent multi-run variance is reported alongside structured harness gains, and retrospective stop-rule replay costs are separated from full-budget pass counts ([`rsi-pdebench-self-improving-pde-agents`](../research-briefs/rsi-pdebench-self-improving-pde-agents.md), arXiv:2611.14949)
- [ ] For in-flight RL post-training supervision, supported hyperparameter and `TRAIN`-grader repairs use step-boundary `HOT` overrides (avoiding `44.7%` checkpoint-rewind step waste), `COLD` crash/code resumptions scope monitoring history to parent-checkpoint lineage, `Proposers` replay `TRAIN`-grader edits on isolated CPU fixtures before GPU activation while keeping `EVAL` graders strictly frozen, and novel learning-rule invention is not assumed (`0/3` deployed in [`autorl-process-level-autonomous-rl`](../research-briefs/autorl-process-level-autonomous-rl.md), arXiv:2611.17790)
- [ ] Before RLVR / GRPO post-training against a proxy process verifier or rubric, candidate verifiers are audited on a model-free probe grid ($n \approx 60$ contexts $\times$ `6` synthetic archetypes) for pairwise selection error $s$ and signed gap $\mathbb{E}[\tilde{V} - r^\star]$ (blocking optimistic $\mathbb{E}[\tilde{V} - r^\star] > 0, s \ge 0.10$ sufficiency/recall verifiers that hack `2.3x–3.2x` harder via citation padding without word-length growth), paired with a short group-variance pilot ($u$, step-1 reward `< 0.80`, `< 40%` skips, global grad clip `1.0`) and component-level OOD precision/surplus checks ([`verifier-gap-sign-pre-rl-audit`](../skills/verifier-gap-sign-pre-rl-audit/SKILL.md), arXiv:2611.21538)
- [ ] `~4B` SLM trajectory distillation and exact-reward RL checkpoints are verified for cross-schema minimality on unseen feature dimensionalities against a prompted mid-tier model (`Haiku 4.5 + shrink` `47/47` vs. `Alg-2000` `92.2% -> 47.9%` OOD Exact) and inspected for tool-distribution inversion (`0` probes + `30` checks) ([`procedure-without-judgment-exact-verifier-slm`](../research-briefs/procedure-without-judgment-exact-verifier-slm.md), arXiv:2611.21529)
- [ ] When co-evolving a curriculum harness alongside an execution harness around frozen foundation models, phases alternate around locked admitted task snapshots $\mathcal{T}_k$ (zero solver difficulty pre-screening), `Experience Consolidator` profiles withhold raw traces from curriculum proposers while Judge-only geometry stays hidden from execution, and optimizer lessons are verified to land in agent-visible skill descriptions (`<= 2,500` chars) or retrievable manuals ([`roboace-adversarial-curriculum-execution-coevolution`](../research-briefs/roboace-adversarial-curriculum-execution-coevolution.md), arXiv:2611.13034)
- [ ] When curating `SFT` trajectories on multi-step exploration/QA tasks, trajectories are truncated at the forced-answer sufficiency plateau $i^\star$ with a voice-matched halting rationale upweighted by $\lambda = 5$ (avoiding unpruned expert `SFT` step-limit saturation, raw unweighted truncation, and backfiring prompted tool-budget trackers) ([`jet-just-enough-exploration-tuning-repo-qa`](../research-briefs/jet-just-enough-exploration-tuning-repo-qa.md), arXiv:2611.22539)
- [ ] In grader-free continual adaptation across drifting tools/streams, playbooks are keyed to `Turn-0` interface signatures, graded by Layer-1 deterministic sandbox checks + Layer-2 `Turn-0` atomic checklists (`0.0%` execution-broken false passes vs. `22.2%` 1-layer), prioritized by paired directional regret $\Delta_{\mathrm{hurt}} + \Delta_{\mathrm{gap}}$, and gated by `Soft-HURT` with at most one `[iff]` scope repair before final acceptance gating ([`regret-guided-continual-harness-evolution`](../skills/regret-guided-continual-harness-evolution/SKILL.md), arXiv:2611.23476)
- [ ] In open-ended constructive coding RSI (`Sonnet`/`Opus` tier), motivational `openness` dispositions stay pinned outside the editable workspace (avoiding `conservation` $\delta = -0.27$, literature-distilled caution, and self-modifying value erosion $\delta = -0.64$), while regression safety is enforced by executable verification hooks (`verify.py`) and the frozen acceptance gate ([`values-shape-self-improving-coding-agents`](../research-briefs/values-shape-self-improving-coding-agents.md), arXiv:2611.23067; [`self-improving-agent-harnesses-framework`](../research-briefs/self-improving-agent-harnesses-framework.md), arXiv:2611.22299)
- [ ] When pairing a sub-second System-1 action scorer with asynchronous System-2 `state`/`proc`/`wm` module synthesis, `state` graphs remain framework-managed, failing modules quarantine at $L = 3$ consecutive losses, `wm` modules clear `>= 50%` checkable / `>= 60%` replay accuracy, and System-2 trigger volume is monitored across developer swaps (`GPT-6.1 Sol` triggered `10` vs. `49–67` dev steps on `BabyAI`, [`asynchronous-system1-harness-evolution`](../skills/asynchronous-system1-harness-evolution/SKILL.md), arXiv:2611.22432)
- [ ] Unprescribed data-free self-improvement (`{Read, Write, Bash, Gameplay}`) is relied upon only on verified frontier generations with interactive execution enabled, and target-evaluation summaries/turn caps are bounded (`< 3k` tokens) so artifacts do not overfit away cross-domain transfer ([`self-organized-agent-self-improvement`](../research-briefs/self-organized-agent-self-improvement.md), arXiv:2611.23219)
- [ ] When evolving multidimensional evaluators or reward models in verifier-free domains, candidate updates are gated on clip/item-disjoint construction-defined clean-vs-perturbed exams (scored in both pairwise orders plus standalone calibration) via weighted log Nash bargaining over disagreement floors and family-level drop caps (`<= 0.12`), halting for out-of-band curriculum refresh upon `[-0.004, +0.001]` saturation ([`constructed-exam-nash-evaluator-evolution`](../skills/constructed-exam-nash-evaluator-evolution/SKILL.md), arXiv:2611.23890)
- [ ] In model–data co-evolution and closed-loop trajectory repair, discrete flip accuracy is tracked alongside validation KL loss (`KL 2.19 -> 0.64` masking a `+78 -> -13` accuracy reversal in arXiv:2611.24651), MCTS count sharing checks first-level branching width and RL readiness first (arXiv:2611.22301), white-box harness internalization targets LOBO-verified causal `ReGap` on least-active neurons (arXiv:2611.24578), and pre-failure repairs require $H$-step greedy self-continuation plus renewed per-round anchors and normal-state retention (arXiv:2611.24077)
- [ ] The diagnostic loop is in place (measure → name mechanism → change → measure)

---

## 8. Planning Architecture

### Does your agent need real-time action generation?

> **Research note**: for embodied or interactive agents requiring low-latency
> actions, decoupling planning (VLM, high-latency) from control (world-model,
> low-latency) outperforms monolithic approaches on 6/7 environments and
> enables plug-and-play planner swapping. (arXiv:2608.26788, COLM 2026)

- [ ] **No** — standard request-response agent, no real-time constraint
- [ ] **Yes** — consider decoupled planner/controller architecture:
  - [ ] Planner: pre-trained VLM issuing text instructions asynchronously
  - [ ] Controller: lightweight, environment-specific model executing at
    control frequency
  - [ ] Language as the stable interface between planner and controller
  - [ ] Controllers trained via post-hoc instruction supervision (relabel
    replay segments with VLM-generated instructions)

---

## Benchmark Reference (August 2026)

Current best systems on AI4AI-Bench:

| System | Mean σ | Cost (median) |
|:-------|:-------|:-------------|
| Claude Opus 5 | 0.250 | $181 |
| GPT-5.6 Sol | 0.191 | $434 |
| Kimi K3 | 0.174 | $30 |

Even the best system closes less than a fifth of the distance between the
shipped algorithm and the task optimum. Set expectations accordingly.

---

## Sources

- HyperAgents: arXiv:2603.19461
- AI4AI-Bench: arXiv:2608.20318
- Reflections on Trusting Trust, Revisited (poisoned benchmarks): arXiv:2609.17817
- RRSI: arXiv:2609.24972
- Evolutionary Safety of Recursive Self-Improving AI: arXiv:2609.31186
- EvoPathBench: arXiv:2609.24663
- A Theory of Reliable Self-Evolution for Agent Harnesses: arXiv:2609.08175
- AI Agency Typology: arXiv:2608.20041
- Instruct-to-Act: arXiv:2608.26788
- TRUST (Trustworthy Recursive Self-Improvement with Statistical Guarantees): arXiv:2611.10787
- Self-Evolving Multimodal Agents Across Scenarios: arXiv:2611.14256
- FGSE (Falsification-Gated Self-Evolution): arXiv:2611.14326
- RSI-PDEbench (Self-Improving Agents in PDE Solving): arXiv:2611.14949
- AutoRL (Multi-Agent System towards Autonomous Reinforcement Learning): arXiv:2611.17790
- Optimistic Verifiers Get Hacked (Reward Hacking Under an Exact Process Oracle): arXiv:2611.21538
- Procedure without Judgment (What SLMs Learn under an Exact Verifier): arXiv:2611.21529
- RoboACE (Adversarial Co-Evolution for Robot Self-Improvement): arXiv:2611.13034
- JET (Just-Enough Exploration Tuning for Repository-Level QA): arXiv:2611.22539
- Harnesses That Improve Themselves: arXiv:2611.22299
- JevRSI (Cost-Effective RSI for Decision Model Harness): arXiv:2611.22432
- Values Shape What Self-Improving Coding Agents Build: arXiv:2611.23067
- Do LLM Agents Still Need to Be Told How to Self-Improve?: arXiv:2611.23219
- GUARD (Stabilizing Recursive Self-Improvement with Regret Guidance): arXiv:2611.23476
- LPC-MCTS (Learning Exploration Counts for LLM Reasoning): arXiv:2611.22301
- EVA-RSI (Recursive Self-Improvement of Video Evaluators): arXiv:2611.23890
- AeroRSI (Recursive Self-Improvement for Aerial Vision-Language Navigation): arXiv:2611.24077
- BaseRSI (Training-Free Harness Internalization): arXiv:2611.24578
- Piccolo (Co-Evolving Decision Models and Data): arXiv:2611.24651
