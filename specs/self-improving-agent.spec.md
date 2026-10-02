# Self-Improving Agent Specification Template

> Fill in this template when designing an agent system that can modify its
> own capabilities, training process, or decision-making procedures. Each
> section surfaces research-backed decision points for architecture, safety,
> evaluation, and change classification.

---

## 1. Improvement Scope

### What can the agent modify?

Define the edit scope explicitly. Every item outside this scope is frozen.

| Component | Editable? | Justification |
|:----------|:----------|:-------------|
| Its own system prompts | [ ] Yes / [ ] No | |
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
