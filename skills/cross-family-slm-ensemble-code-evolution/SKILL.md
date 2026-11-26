---
name: cross-family-slm-ensemble-code-evolution
description: Evolve executable programs, ML pipelines, or low-level kernels under tight compute budgets by running synchronous cross-family small-model (8B–12B) best-idea-wins rounds over a monotonically gated shared incumbent, bounded strategy notes, and a cross-model failure log.
source: "arXiv:2611.28420"
repository: "https://github.com/usc-isi-i2/dive-rsi"
license: "CC BY 4.0"
---

# Cross-Family SLM Ensemble Code Evolution (`DiVE`)

Use this procedure when running iterative evolutionary code search against an automated practice evaluator—across **5+ project types** including machine-learning feature/model pipelines (`MLE-bench`), GPU/VLIW/SIMD kernel cycle optimization, heuristic combinatorial solvers, SQL/query-plan rewrite discovery, and compiler/DSP pass tuning—when frontier API budgets are constrained or open-weight models (`8B–12B`) must run locally or via low-cost endpoints.

Single small models stall `86%–99%` of evolutionary rounds in `>= 20`-round plateaus (`0.8–5.4` escaping jumps per task), and standard multi-LLM evolutionary harnesses (`OpenEvolve`, `ShinkaEvolve`) select **one model before writing**, wasting rounds whenever the sampled model hits a local blind spot or emits invalid code. `DiVE` (*Diversity over Scale*, `arXiv:2611.28420`) flips selection to **after execution (`best-idea-wins`)** across $K \approx 5$ small models from **distinct model families**, coupling them through a strictly monotonic single-incumbent **Shared Memory** and a **`5`-entry cross-model Failure Log**. Across `22` `MLE-bench Lite` competitions (`200` rounds), a `5`-SLM ensemble (`8B–12B`, `$1.42`/comp all-in) removed **`38.1%`** of starting test error—achieving **`25.4%` less test error** than its average member (`20/21` scored comps, $p < 0.001$), **`16.7%` less test error** than `Llama 3.3 70B` (`19/21` scored comps, $p < 0.001$; matching `70B`'s final score in `21/22` comps at median Round 1 for `$0.10` vs. `$0.49`, **`5.2x` cheaper**), and coming within **`7.1%`** of `Qwen 3.5 122B-A10B` (`41.4%` error removal) at **`75%` of its cost (`$1.42` vs. `$1.90`)**—while on Anthropic's VLIW kernel benchmark (`147,734` cycles) it was the **only configuration of 8 tested** to improve under both `bare` (`-11.1%`, `131,338` cycles) and `debug` (`-8.3%`, `135,445` cycles) feedback where every solo SLM and `Llama 3.3 70B` gained `0.0%`.

---

## When to Use This Skill

- Iterative program, pipeline, or kernel optimization where every candidate can be executed and scored deterministically on a **practice split** or cycle-accurate simulator.
- Low-cost or local/open-weight deployments (`$0.10–$2.30` per 200-round search) where you do not know in advance which small model family fits the target task (`Alone` winners split `12 / 3 / 3 / 3 / 1` across `5` SLMs on `MLE-bench Lite`).
- Escaping reasoning plateaus where a single `8B–70B` model repeats slight variations of the same algorithm (`95%` stalled rounds on `Llama 3.3 70B` vs. `66%` and `14.1` escaping jumps/comp for the `5`-SLM ensemble, with `59%` of accepted improvements building directly on a *different* family's prior program).

Do **not** use this procedure when no executable practice scorer exists (use [`abstaining-guardrail-best-of-n`](../abstaining-guardrail-best-of-n/SKILL.md) for label-free single-question artifacts) or for single-pass non-interactive routing/voting without execution verification (see *"DON'T: Expand candidate model pools with arbitrary heterogeneous architectures"* in [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md)).

---

## Step-by-Step Procedure

### Step 1: Assemble $K \approx 5$ Cross-Family Open-Weight Proposers (`8B–12B`)
1. Select $K = 4\text{--}6$ small instruction/coding models drawn from **distinct model families, pretraining corpora, and providers**—for example, `Qwen 3.5 9B`, `Granite 4.2 8B`, `Llama 3.1 8B`, `Ministral 8B`, and `Gemma 3 12B`—rather than $K$ temperature samples or size tiers of a single model family.
2. **Do not prune low-validity exploratory members prematurely**: Under post-write `best-idea-wins` gating, a model whose proposals fail execution `>90%` of the time (`Ministral 8B` had only `8%` valid programs alone and `9%` inside the ensemble) cannot corrupt the incumbent when it crashes, yet contributed **`21%` of total ensemble error reduction** whenever one of its aggressive structural edits ran cleanly (`Granite 8B` `31%`, `Qwen 9B` `21%`, `Gemma 12B` `16%`, `Llama 8B` `12%` across all `22` tasks).
3. Set sampling temperature (`~0.7`) and cap per-call output tokens (`~8,192–16,384`) so one runaway generation cannot stall synchronous round barriers.

### Step 2: Initialize Shared State and Disjoint Practice vs. Acceptance Splits
Partition evaluation data **before Round 0** so proposers never touch held-out test feedback:
1. **Practice Split ($\mathcal{D}_{\text{practice}}$)**: Stratified validation split (e.g., `80/20` split of training data or deterministic cycle simulator) used to score candidates inside the evolutionary loop.
2. **Held-Out Acceptance Split ($\mathcal{D}_{\text{accept}}$)**: Strictly unseen test/acceptance suite reserved exclusively for post-search promotion under *"DO: Pass every self-modification through one acceptance gate"* ([`recursive-improvement.md`](../../rules/recursive-improvement.md)).
3. **Seed Shared Memory $(p_0, s_0, \text{notes}_0)$**: Obtain one minimal runnable starter program $p_0$ (either a deterministic template or `1` one-shot baseline draft verified to run and emit a valid practice score $s_0$), and initialize the **Failure Log** $F_0 = []$ as an empty bounded FIFO queue of capacity **$L = 5$**.

### Step 3: Enforce the Pre-Execution `Idea Card` + Rewritten `Notes` Contract
In every round $t = 1, \dots, T$, broadcast the exact same read-only prompt containing `(task spec, incumbent program p_{t-1}, incumbent practice score s_{t-1}, incumbent strategy notes_{t-1}, and failure log F_{t-1})` to all $K$ models in parallel, requiring three structured output blocks:

| Required Output Block | Format & Bounds | Gate Behavior |
|:---|:---|:---|
| **1. `Idea Card`** | Short idea name + `1–2` sentence rationale explaining *why* it improves on $p_{t-1}$ and avoids $F_{t-1}$ + numbered implementation steps | **Reject pre-execution** if missing or empty; log format rejection without wasting sandbox compute so every failed run has an interpretable cross-model summary |
| **2. Full Program $c_t^k$** | Complete runnable source file in a fenced code block (respecting editable-region hashes if kernel/harness scaffolding is frozen) | Execute in an isolated sandbox with hard wall-clock timeout (e.g., `300 s`) and memory cap |
| **3. Updated `Notes` ($\le 150$ words)** | Rewritten cumulative strategy summary describing what $c_t^k$ now does and key empirical lessons | Admitted into Shared Memory **only if** $c_t^k$ becomes the new best-scoring incumbent (preventing unbounded prompt bloat across `200+` rounds) |

### Step 4: Execute Candidates, Update the Cross-Model `FIFO` Failure Log, and Apply `Best-Idea-Wins`
1. **Sandbox Evaluation**: Run all $K$ syntax- and contract-valid programs against $\mathcal{D}_{\text{practice}}$ (in parallel sandboxes if CPU/memory permits, or sequentially on a single host).
2. **Cross-Model Failure Logging ($L = 5$ FIFO)**: Whenever any candidate $c_t^k$ crashes, times out, hits OOM, violates output schemas, or fails correctness assertions before producing a valid practice score, append `(idea_name, error_type, concise_error_message, crash_line)` to $F_t$, evicting the oldest entry once $|F_t| > 5$. Because all $K$ models read $F_t$ next round, one model's timeout or shape bug warns all other families away from the same dead end.
3. **Strict Monotonic Incumbent Gate (`Best-Idea-Wins`)**:
   - Let $\mathcal{V}_t \subseteq \{1, \dots, K\}$ be the subset of candidates that completed cleanly and produced a valid practice score $s_t^k$ (using lower-is-better or higher-is-better canonical orientation).
   - If $\mathcal{V}_t$ is non-empty and the round winner $k^\star = \arg\max_{k \in \mathcal{V}_t} s_t^k$ **strictly beats** the incumbent ($s_t^{k^\star} > s_{t-1}$), update $(p_t, s_t, \text{notes}_t) \leftarrow (c_t^{k^\star}, s_t^{k^\star}, \text{notes}_t^{k^\star})$.
   - Otherwise (**all $K$ crashed or none beat $s_{t-1}$**), keep $(p_t, s_t, \text{notes}_t) \leftarrow (p_{t-1}, s_{t-1}, \text{notes}_{t-1})$ unchanged. Broken or regressive code **never** enters Shared Memory.

### Step 5: Stop on Budget or Sequential Plateau, Then Run the Single Acceptance Gate
1. **Budget & Stopping**: For fast cost-parity baselines (e.g., beating a single `70B` model at `5.2x` lower cost), `15–30` rounds often suffice (`DiVE` matched `Llama 3.3 70B` at median Round `1` and matched `Qwen 3.5 122B` on `5` comps at median Round `18`); for deep exploration, pair the round cap $T$ with sequential plateau stopping ([`self-evolution-stopping-rule`](../self-evolution-stopping-rule/SKILL.md)) or overlap-adjusted subsampled validation ([`online-fer-statistical-acceptance`](../online-fer-statistical-acceptance/SKILL.md)) when practice evaluations are expensive.
2. **Final Acceptance Gate**: Treat $(p_T, s_T)$ strictly as a **search-time proposal**. Before committing $p_T$ to a production codebase, persistent skill library, or benchmark submission, pass $p_T$ through **"DO: Pass every self-modification through one acceptance gate"** in [`recursive-improvement.md`](../../rules/recursive-improvement.md): verify improvement beyond baseline noise margin $\delta$ on the untouched held-out split $\mathcal{D}_{\text{accept}}$, confirm behavioral/output validity (`41.7%` practice error removal vs. `38.1%` held-out test error removal on `MLE-bench Lite` illustrates mild practice-split optimism), and enforce strict zero tolerance on held-out security/safety checks.

---

## Failure Modes & Caveats

- **Practice-split overfitting across `200` rounds**: Repeated `best-of-K` hill-climbing on a small validation split can select hyperparameter luck (`41.7%` practice vs. `38.1%` test error reduction in `DiVE` `Table 2`; and `1` of `22` competitions—`Text Normalization (ru)`—produced no valid test submission score on `Ensemble`, `Qwen 9B`, and `Qwen 122B`, which is why manuscript `§1` cites `19 of 22` wins over `Llama 70B` while `§5.2` reports `19 of 21` scored test pairs). Always validate output-submission format on a synthetic dry-run schema check and gate final retention on an untouched holdout.
- **Verbose debug traces overwhelming single large models**: On the VLIW kernel task (`Table 10`), switching evaluator feedback from `bare` cycle counts to `debug` per-engine utilization diagnostics collapsed `Qwen 3.5 122B-A10B` from `30.5%` gain (`82%`/`70%` valid) to **`0.0%` gain (`0%` valid)** due to over-long reasoning traces, whereas the `5`-SLM ensemble still achieved **`-8.3%` cycles (`25%` valid)** because unaffected families absorbed the round when another family timed out or truncated. Keep prompt feedback compact (`<= 5` failure entries, `<= 150`-word notes).
- **Shared mutable workspace collisions**: If all $K$ candidates execute in the same working directory, one candidate's temporary cache or file write corrupts sibling evaluations. Isolate each of the $K$ candidate executions in its own temporary directory or snapshot sandbox.

---

## Related Artifacts

- **Rules**: [`recursive-improvement.md`](../../rules/recursive-improvement.md) (*"DO: Run synchronous cross-family SLM best-idea-wins rounds over a monotonically gated incumbent and shared failure log in verifier-backed code evolution"*, *"DO: Pass every self-modification through one acceptance gate"*, *"DO: Return only accept/reject decisions to the proposer when the acceptance set is reused across rounds"*), [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md) (*"DON'T: Expand candidate model pools with arbitrary heterogeneous architectures"*, *"DO: Scale test-time compute on verifiable long-horizon tasks via parallel small flat teams rather than solo Best-of-N, one giant team, or manager orchestration"*)
- **Skills**: [`parallel-small-team-tts-scaling`](../parallel-small-team-tts-scaling/SKILL.md), [`abstaining-guardrail-best-of-n`](../abstaining-guardrail-best-of-n/SKILL.md), [`online-fer-statistical-acceptance`](../online-fer-statistical-acceptance/SKILL.md), [`self-evolution-stopping-rule`](../self-evolution-stopping-rule/SKILL.md)
