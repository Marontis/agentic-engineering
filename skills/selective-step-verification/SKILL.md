---
name: selective-step-verification
description: >
  Selectively verify coding-agent actions at the step level by scoring each
  initial proposed command with a lightweight rubric-trained verifier,
  triggering multi-candidate sampling and two-stage checklist ranking only when
  the initial score falls below threshold (<4% of steps), and executing the
  top-ranked candidate without modifying policy prompting. Derived from
  SWE-Verifier (arXiv:2610.30284).
source: https://arxiv.org/abs/2610.30284
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Selective Step-Level Action Verification (SWE-Verifier)

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Activate this skill when:

- **Scaling test-time compute for multi-step coding agents** where trajectory-level verification (generating $k$ full trajectories and selecting one) multiplies inference cost by $3\text{--}4\times$ and leaves mid-trajectory mistakes uncorrected until after completion.
- **Replacing uniform all-step verification** where sampling and scoring $n$ candidate actions at every turn inflates inference cost by $>2\times$ (`2.03x--3.99x` across verifier configurations) and degrades trajectory coherence when applied indiscriminately.
- **Training or deploying a lightweight step-level action verifier** (`4B`-scale model) that transfers zero-shot across frontier coding policies without retraining on the target policy's trajectories.
- **Integrating a verifier into an agent loop** where prompting the policy to propose diverse alternatives for a selector risks destabilizing the policy's exploration/edit workflow.

Do **not** use this skill when:

- Tasks are single-turn code generation where candidate selection happens once at the output boundary.
- Environment actions have irreversible external side effects during offline training data collection and cannot be replayed from saved sandbox snapshots to record immediate observations.
- The base policy model is nearly deterministic across repeated samples at the current temperature, leaving candidate sets with near-identical commands after deduplication.

---

## Core Insight

In long-horizon software engineering tasks (averaging `35--47` steps on SWE-Bench Verified), most steps are routine navigation or inspection commands where the policy's first proposed action is already adequate. Uniformly sampling and ranking $n$ candidates at every step wastes compute and introduces selector noise on steps that do not need intervention: on a 202-task SWE-Bench Verified subset, forcing a trained step-level verifier to intervene on `100%` of steps ($\tau = 1$) reduces resolution rate to `67.16%` (below the `68.48%` unverified baseline), whereas intervening only on the lowest-scoring `<4%` of steps ($\tau = 0.2$) raises resolution rate while keeping cost near `1.1x`.

Furthermore, **how the verifier is trained and invoked determines whether step-level intervention helps or harms**:

1. **Execution-informed teacher rubrics beat raw action text.** A verifier trained only on trajectories without immediate post-action environment observations cannot distinguish plausible-looking edits from commands that fail on execution. Replaying contrasting candidate actions from the same state to capture their immediate observation $o_t$ allows a teacher (`GPT-5.6`) to construct a task-specific `<checklist>` (`must | should | nice`) and calibrate scalar scores in $[0.0, 1.0]$ for a student verifier (`Qwen3.5-4B`) that only sees the trajectory prefix and a single candidate action at inference time.
2. **Two-stage rubric scoring outperforms single-pass scoring.** Having the student verifier generate a step-specific `<checklist>` in a first call and score each checklist item in a second call yields higher resolution rates than predicting a bare scalar (`Score Only`) or generating the rubric and score jointly (`Joint Rubric`).
3. **Never prompt the policy to generate diverse candidates for the verifier.** Explicitly telling the policy model that a verifier will choose among its proposals (`verifier-as-tool`) shifts its phase distribution (phase agreement with the baseline drops to `83--86%` in the `10--40%` trajectory region vs `>93%` for ordinary step verification) and lowers SWE-Bench Verified resolution on `MiniMax-M2.7` from `75.5%` to `70.2%` ($n = 3$, `1.40x` cost) and `69.2%` ($n = 5$, `1.97x` cost).

### Empirical Performance on Full SWE-Bench Verified (500 Tasks)

| Policy Model | Verification Regime | Method | Resolved (%) | Relative Cost | Avg Steps (% Verified) |
|:---|:---|:---|:---|:---|:---|
| `MiniMax-M2.7` | None | No Verification | `75.47 +/- 1.40` | `1.00x` | `46.38 (0.00%)` |
| `MiniMax-M2.7` | Trajectory-Level | `LLM-as-a-Verifier@3` | `75.85 +/- 0.87` | `3.50x` | — |
| `MiniMax-M2.7` | Trajectory-Level | `Oracle@3` | `82.20` | `3.00x` | — |
| `MiniMax-M2.7` | All-Step ($n=3$) | `Self-Verification` | `75.27 +/- 1.86` | `3.35x` | `38.51 (100.00%)` |
| `MiniMax-M2.7` | All-Step ($n=3$) | `Qwen3.5-4B` | `76.40 +/- 0.69` | `2.26x` | `39.98 (100.00%)` |
| `MiniMax-M2.7` | Selective ($\tau=0.2, n=3$) | `Untrained` (`Qwen3.5-4B`) | `76.93 +/- 1.21` | `1.20x` | `44.05 (12.61%)` |
| `MiniMax-M2.7` | Selective ($\tau=0.2, n=3$) | `Score Only` | `76.93 +/- 0.95` | `1.05x` | `46.93 (0.45%)` |
| `MiniMax-M2.7` | Selective ($\tau=0.2, n=3$) | `Joint Rubric` | `76.87 +/- 0.81` | `1.14x` | `47.28 (3.40%)` |
| `MiniMax-M2.7` | Selective ($\tau=0.2, n=3$) | **`Two-Stage Rubric`** | **`77.20 +/- 0.87`** (`+1.73 pp`) | **`1.09x`** | **`46.36 (3.43%)`** |
| `DeepSeek-V4-Flash` (Preview) | None | No Verification | `72.60 +/- 0.53` | `1.00x` | `41.64 (0.00%)` |
| `DeepSeek-V4-Flash` (Preview) | Trajectory-Level | `LLM-as-a-Verifier@3` | `74.30 +/- 0.58` | `4.19x` | — |
| `DeepSeek-V4-Flash` (Preview) | Trajectory-Level | `Oracle@3` | `80.60` | `3.00x` | — |
| `DeepSeek-V4-Flash` (Preview) | All-Step ($n=3$) | `Self-Verification` | `72.67 +/- 0.90` | `3.99x` | `33.56 (100.00%)` |
| `DeepSeek-V4-Flash` (Preview) | All-Step ($n=3$) | `Qwen3.5-4B` | `72.53 +/- 0.70` | `2.03x` | `37.14 (100.00%)` |
| `DeepSeek-V4-Flash` (Preview) | Selective ($\tau=0.2, n=3$) | `Untrained` (`Qwen3.5-4B`) | `73.60 +/- 0.35` | `1.17x` | `41.36 (8.01%)` |
| `DeepSeek-V4-Flash` (Preview) | Selective ($\tau=0.2, n=3$) | `Score Only` | `73.20 +/- 0.35` | `1.11x` | `41.56 (3.94%)` |
| `DeepSeek-V4-Flash` (Preview) | Selective ($\tau=0.2, n=3$) | `Joint Rubric` | `73.93 +/- 1.03` | `1.08x` | `41.05 (3.54%)` |
| `DeepSeek-V4-Flash` (Preview) | Selective ($\tau=0.2, n=3$) | **`Two-Stage Rubric` (Zero-Shot Transfer)** | **`74.27 +/- 1.01`** (`+1.67 pp`) | **`1.13x`** | **`42.15 (3.59%)`** |

---

## Procedure

### Step 0: Check the Per-Step Cost Break-Even Condition

Before deploying step-level verification, compute the relative per-step cost multiplier against unverified execution. Let $c_p(t)$ and $c_v(t)$ denote the dollar cost of one policy call and one verifier call at step $t$ (accounting for cached prefix tokens, uncached context, and generated tokens), and let $r = \frac{1}{T}\sum_{t=1}^T \frac{c_v(t)}{c_p(t)}$ be the average verifier-to-policy cost ratio across a trajectory of length $T$.

With gate indicator $g_t \in \{0, 1\}$ (where $g_t = 1$ triggers sampling $n - 1$ additional policy candidates and scoring all $n$ candidates) and verification rate $\rho = \frac{1}{T}\sum_{t=1}^T g_t$, the average per-step cost multiplier is:

$$\frac{C_{\text{selective}}}{C_{\text{base}}} \approx 1 + r + \rho(n - 1)(1 + r)$$

- **All-step self-verification** ($\rho = 1, r = 1$) costs $2n\times$ per step (`6x` per step for $n = 3$, or `3.35x--3.99x` per trajectory after step-count reduction).
- **Lightweight selective verification** with a `4B` verifier ($r \ll 1$, $\rho < 0.04$, $n = 3$) keeps total trajectory cost at `1.05x--1.14x` while preserving trajectory length (`46.36` vs `46.38` steps on `MiniMax-M2.7`).

### Step 1: Build Execution-Informed Contrasting Action Datasets (Offline Training)

To train or update the student verifier (`Qwen3.5-4B` with a `65,536`-token context window), construct multi-candidate step comparisons grounded in real execution outcomes:

1. **Sample seed trajectories**: Collect `500` successful trajectories from strong reference agents (e.g., `Opus 4.7` and `GPT-5.5` on SWE-Smith `llm_rewrite` and `pr_mirror` tasks).
2. **Sample contrasting candidate actions per step**: At each step $t$ (across `6,000` agent steps), sample `5` candidate actions from models of contrasting capability (e.g., `MiniMax-M2.7` and `Qwen3.5-27B`) conditioned on the identical trajectory prefix $h_t$.
3. **Deduplicate by token Jaccard similarity**: Tokenize each candidate action $a$ into token set $S(a)$ and discard any candidate whose pairwise Jaccard similarity to an already retained candidate meets or exceeds `0.8`:
   $$J(a, b) = \frac{|S(a) \cap S(b)|}{|S(a) \cup S(b)|} < 0.8$$
4. **Replay each retained action to capture immediate observations**: Execute each retained candidate $a_{t,i}$ in the sandbox from state $h_t$ to record its immediate environment output $o_{t,i}$. Drop candidates that produce duplicate non-empty environment observations so the teacher compares behaviorally distinct actions (`30k` labeled actions across `6,000` steps).

### Step 2: Distill Rubric-Guided Teacher Supervision into the Student Verifier

1. **Teacher labeling with execution visibility**: Present the trajectory prefix $h_t$, all retained candidate actions $\{a_{t,i}\}$, and their immediate execution observations $\{o_{t,i}\}$ to a strong teacher (`GPT-5.6`). Require the teacher to emit:
   - `<summary>`: structured fields covering `Task_State`, `Completed_Progress`, `Open_Blockers`, `Constraints`, `Likely_Next_Needs`, and `Failure_Modes_To_Avoid`.
   - `<checklist>`: atomic evaluation criteria weighted as `must`, `should`, or `nice` (adapted to the current stage: localization, editing, testing, or submission).
   - Per-candidate evaluation blocks (`<candidate id="i">`) containing `NEXT_STATES_PREDICTION` (`Immediate_Observation` and `Expected_Progress`), `CHECKLIST_ITEM_SCORES`, `REASONING`, and a calibrated scalar `SCORE` in $[0.0, 1.0]$:
     - `1.0`: ideal next action; directly and safely advances the task.
     - `0.7--0.9`: strong action; minor inefficiency or risk.
     - `0.6--0.69`: slightly positive; useful progress with notable limitations.
     - `0.5`: neutral / mixed; limited progress or unclear payoff.
     - `0.4--0.49`: slightly negative; weak, redundant, or poorly targeted.
     - `0.1--0.39`: negative; likely wastes a step or goes in the wrong direction.
     - `0.0`: clearly harmful, invalid, or irrelevant.
2. **Student formatting without execution leakage**: Unpack the teacher's multi-candidate output into single-candidate training examples for the student verifier. At inference time, the student receives **only** $(h_t, a)$—never the post-execution observation $o_t$ or sibling candidates—and learns to anticipate `NEXT_STATES_PREDICTION` and `<checklist>` scores from the prefix and proposed command alone.

### Step 3: Gate Mode — Score the Initial Action Against Threshold $\tau$

At each online agent step $t$:

1. Have the policy model generate a single proposed action $a_{t,1} \sim \pi(\cdot \mid h_t)$ using its standard system prompt and sampling parameters (do **not** mention the verifier to the policy).
2. Validate that $a_{t,1}$ contains a syntactically valid bash command block.
3. Run the student verifier on $(h_t, a_{t,1})$ to obtain scalar score $s_{t,1} = v(h_t, a_{t,1}) \in [0, 1]$.
4. Apply the threshold gate ($\tau = 0.2$ transfers across both `MiniMax-M2.7` and `DeepSeek-V4-Flash` without retuning):
   - If $s_{t,1} \ge \tau$ ($g_t = 0$, which occurs on `>96%` of steps), **execute $a_{t,1}$ immediately** in the environment and advance to step $t + 1$.
   - If $s_{t,1} < \tau$ ($g_t = 1$, triggered on `3.43%--3.59%` of steps under `Two-Stage Rubric`), escalate to **Selector Mode** (Step 4).

### Step 4: Selector Mode — Two-Stage Checklist Generation and Candidate Ranking

When $s_{t,1} < \tau$ at step $t$:

1. **Sample $n - 1$ additional candidates** ($n = 3$ total: $A_t = \{a_{t,1}, a_{t,2}, a_{t,3}\}$) independently from the policy $\pi(\cdot \mid h_t)$ from the same prefix $h_t$. Filter out any candidate that lacks a valid bash action (`valid_action == True`).
2. **Score each additional candidate using the Two-Stage Rubric protocol**:
   - **Call 1 (Checklist Generation)**: Given $(h_t, a_{t,i})$, the verifier summarizes the trajectory state and outputs the step-specific `<checklist>` of `must | should | nice` criteria.
   - **Call 2 (Checklist Scoring)**: Given the generated `<checklist>` and $(h_t, a_{t,i})$, the verifier predicts the immediate observation and expected progress, scores each checklist item, and outputs the final scalar `SCORE: <float>`.
3. **Select the winning action**: Choose the valid candidate with the highest verifier score:
   $$a_t^* = \arg\max_{a \in A_t} v(h_t, a)$$
   (Note: if additional policy calls are inexpensive and you want maximum resolution on a smaller subset, a trained `Score Only` gate can also be paired with the policy model itself as selector, which reached `73.27%` vs `68.48%` baseline on the 202-task ablation set at `1.29x` total cost.)

### Step 5: Execute and Preserve Clean Trajectory History

Execute only the selected command $a_t^*$ in the environment, append $(a_t^*, o_t^*)$ to the agent trajectory $h_{t+1}$, and discard all rejected candidate actions and verifier rubrics from the policy's context window so KV-cache prefixes and trajectory coherence remain intact.

---

## Environment Caveats

- **Verification value concentrates in edit and closeout phases, not periodic intervals**: In phase-specific ablations on `MiniMax-M2.7` (`75.5%` baseline), verifying only the **Closeout** phase (`4%` of steps, $n=5$) reaches `76.6%` at `1.29x` cost and verifying only the **Fix** phase (`9%` of steps, $n=5$) reaches `76.2%` at `1.35x` cost, whereas periodic verification every 5th step (`21%` of steps) drops resolution to `75.0%` (`-0.5 pp`) at `1.39x` cost.
- **Over-triggering degrades performance**: On the 202-task threshold sweep (`68.48%` baseline), `Score Only` achieves `72.28%` at `1.02x` cost (`0.47%` of steps verified) and `71.95%` at $\tau = 0.2$ (`5.79%` of steps verified), but raising $\tau \to 1.0$ (`100%` of steps verified) degrades resolution to `67.16%` (`-1.32 pp` below baseline) at `2.35x` cost.
- **Context truncation in long trajectories**: When trajectory history exceeds the verifier's `65,536`-token window, retain the initial task prompt and most recent observations while summarizing or truncating middle observations so the `<summary>` and `<checklist>` remain grounded in the original issue specification.

---

## Failure Modes & Mitigations

| Failure Mode | Symptom | Mitigation |
|:---|:---|:---|
| **Verifier-as-tool policy distortion** | Policy is prompted to propose $n$ diverse candidate actions for a verifier; early-trajectory phase agreement drops to `83--86%` and resolution falls by `5.3--6.3 pp` (`75.5% -> 70.2%` at $n=3$, `69.2%` at $n=5$). | Keep the verifier completely transparent to the policy. Sample candidates via independent standard calls from the unmodified policy prompt. |
| **Untrained gate over-firing** | Base `Qwen3.5-4B` (`Untrained`) triggers verification on `12.61%` of steps on `MiniMax-M2.7` (`8.01%` on `DeepSeek-V4-Flash`), inflating cost to `1.17x--1.20x` with lower accuracy than `Two-Stage Rubric`. | Fine-tune the student verifier on execution-informed teacher labels so low scores reliably isolate genuine failure steps (`~3.4--3.6%` of steps at $\tau = 0.2$). |
| **Single-pass rubric collapse** | `Joint Rubric` underperforms `Two-Stage Rubric` on both policies (`76.87%` vs `77.20%` on `MiniMax-M2.7`; `73.93%` vs `74.27%` on `DeepSeek-V4-Flash`). | Split inference on triggered steps into two calls: generate the `<checklist>` first, then score the action against the locked checklist. |
| **Duplicate candidate waste** | Policy samples $n=3$ identical commands when temperature is too low or during offline data collection. | During offline collection, enforce token Jaccard similarity $J(a,b) < 0.8$ and deduplicate identical non-empty observations $o_t$ before teacher labeling. |

---

## Cross-References

- **Related Rules**: [`agent-evaluation-quality`](../../rules/agent-evaluation-quality.md), [`recursive-improvement`](../../rules/recursive-improvement.md)
- **Related Skills**: [`behavior-aware-verification`](../behavior-aware-verification/SKILL.md), [`black-box-trajectory-risk-monitoring`](../black-box-trajectory-risk-monitoring/SKILL.md), [`self-evolution-stopping-rule`](../self-evolution-stopping-rule/SKILL.md)

> Source: SWE-VERIFIER: Selective Verification for Cost-Efficient Coding Agents (arXiv:2610.30284), Oct 2026. Praxis source: `src:2610-30284`
