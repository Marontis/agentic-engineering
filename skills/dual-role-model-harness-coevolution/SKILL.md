---
name: dual-role-model-harness-coevolution
description: >
  Co-evolve a single shared-weight adapter as both a failure-grounded harness
  Improver (skills or SQL views) and a workflow Solver via case-balanced
  counterfactual gain rewards, margin-gated workflow memory, and zero-retraining
  test-time retrieval for unseen workflows and schemas (MedicalRSI).
source: arXiv:2611.26806
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Dual-Role Model-Harness Co-Evolution

Co-train a single shared-weight parameter-efficient adapter (`LoRA`) to act simultaneously as a **Harness Improver** ($\mathcal{I}_\theta$, authoring structured workflow skills or executable SQL helper views from reference-free failure traces) and a **Workflow Solver** ($\mathcal{S}_\theta$, executing multi-step API or database tasks with or without a harness), then adapt zero-shot to unseen workflows and schemas at test time without retraining.

## When to Use

- Multi-step API, EHR/FHIR, CRM/ERP, or relational SQL agents operating across recurring workflow types where **RL on the solver alone** stalls on zero-success tasks (`19%` of workflows still failing `8/8` rollouts at Round 10) and **harness evolution with a frozen solver or frozen proposer** hits a capability ceiling (`51.6%–62.8%` vs. `85.1%` co-evolved).
- Cross-workflow and cross-database generalization where downstream deployments introduce **unseen workflow categories or new relational schemas** (`MIMIC-III -> eICU`) under strict read-only weight constraints at test time.
- Authoring compact, transferable domain harnesses with a small open-weight model (`4B–9B`) to lift larger frozen production solvers (`26B–284B` / frontier APIs) without fine-tuning those target models (`+16.8` to `+32.3` percentage points across `7` frozen solvers).
- Do **not** select candidate harnesses at test time using raw majority-output agreement on action-optional workflows (`Order Needed` vs. `No Action Needed`), where passive inaction agrees artificially (`Never Order` bias).

## Core Insight

Model weights and inference harnesses solve complementary halves of agentic error: harnesses eliminate repeatable domain/schema pitfalls across attempts (`68% -> 42%` repeat-mistake rate), while weight updates build step-by-step execution fluency. However, freezing either side creates a mismatch:
- A **frozen Round-1 harness** becomes stale and redundant as the `Solver` improves (`+3.9` pts over trained `Solver` on `Qwen3.5-9B`, negative on `Gemma-4-E4B`, vs. `+20.1` and `+10.2` pts for co-evolved harnesses).
- A **solver trained without harnesses (`GRPO Solver`)** fails to exploit strong external harnesses at test time (`+0.7` pts from `GPT-6.1-Sol` harnesses vs. `+10.7` pts on a co-trained `Solver`).
- **Separate `Improver` and `Solver` LoRA adapters** underperform a **single shared-weight adapter** (`80.0%` vs. `85.1%` overall, `58.1%` vs. `66.1%` on unseen workflows) because execution mastery directly informs diagnostic harness writing and vice versa.

## Step-by-Step Procedure

### Phase 1: Failure-Grounded SFT Warm Start

1. **Define a bounded, typed harness artifact schema**:
   - **API / tool workflows**: Compact Markdown skill (`< 1,500` characters) containing exactly three sections—`When to use`, `Steps`, and `Pitfalls` (endpoint selection, parameter formatting, prerequisite lookups, and when *not* to write/order).
   - **Database / SQL workflows**: Executable `CREATE TEMP VIEW` definitions paired with concise usage notes encapsulating multi-table joins, unit normalizations, and cohort filters.
2. **Synthesize and filter warm-start `(WorkflowEvidence -> Harness)` pairs**:
   - Run the base model unharnessed ($\mathcal{H}_0$) on training workflows to collect failed trajectories.
   - Generate candidate harnesses (using a teacher or multi-sample rejection) and retain **only** candidates that parse cleanly, stay within the `1,500`-character cap, and strictly beat the unharnessed baseline ($r(\mathcal{H}) > r(\mathcal{H}_0)$) when re-executed by the base `Solver`.
   - Fine-tune the shared LoRA adapter (`r = 32, alpha = 64`) briefly on both gain-filtered `(WorkflowEvidence -> Harness)` pairs (`Improver` role) and successful harnessed execution trajectories (`Solver` role). Skipping this warm start raises early RL parse failures from `2%` to `11%`, inflates over-length harnesses to nearly `50%` (vs. `13%`), and costs `-15.6` outcome points (`69.5%` vs. `85.1%`).

### Phase 2: Reference-Free Evidence Construction (`WorkflowEvidence`)

At the start of each co-evolution round (and during test-time adaptation on unseen workflows), for each workflow type $\tau$:

1. **Run a deterministic unharnessed baseline pass ($\mathcal{H}_0$, `temperature = 0`)**:
   - Execute $\mathcal{S}_\theta(\cdot; \mathcal{H}_0)$ on the workflow's task batch (`~20` tasks).
2. **Assemble reference-free `WorkflowEvidence` $P_\tau$ (never leaking ground-truth answers)**:
   - Prioritize failed or anomalous episodes (empty tool returns, HTTP/SQL errors, schema mismatches, truncated budgets, or missing terminal actions) paired with `1–2` contrasting clean traces on the same workflow so $\mathcal{I}_\theta$ observes structural divergences without seeing gold labels.

### Phase 3: Shared-Weight Dual-Role `GRPO` Co-Evolution

 Maintain a persistent per-workflow harness memory $M[\tau]$ (initialized to $\mathcal{H}_0$). In each co-evolution round:

1. **Sample mixed `Improver` candidates ($G = 4$ per workflow)**:
   - If $M[\tau] \neq \mathcal{H}_0$, generate $G/2$ **memory-revision** candidates conditioned on `(P_\tau, M[\tau])` and $G/2$ **from-scratch** candidates conditioned on `P_\tau` alone (preventing local-optimum lock-in). Otherwise sample all $G$ from `P_\tau`.
2. **Evaluate counterfactual gain with case-type balancing**:
   - Execute $\mathcal{S}_\theta$ under each candidate $\mathcal{H}_g$ (`temperature = 1.0`) and under $\mathcal{H}_0$ ($N = 8$ unharnessed rollouts).
   - Score each episode with a composite process + outcome reward (e.g., valid tool/SQL execution milestones + exact terminal state/answer verification).
   - **Balance rewards across case subtypes** (`Order Needed` / write-required vs. `No Action Needed` / read-only): compute mean counterfactual gain $\Delta r(\mathcal{H}_g) = \bar{r}_{\text{bal}}(\mathcal{H}_g) - \bar{r}_{\text{bal}}(\mathcal{H}_0)$ equally across subtypes rather than raw micro-averaging, penalizing parse failures or length violations.
3. **Update shared LoRA parameters jointly across both roles**:
   - Compute group-relative advantages over the $G$ candidate harnesses for $\mathcal{D}^{\textsc{imp}}$ and over the **combined** $(G \text{ harnessed} + N \text{ unharnessed } \mathcal{H}_0)$ solver rollouts for $\mathcal{D}^{\textsc{sol}}$ (mixing $\mathcal{H}_0$ rollouts ensures $\mathcal{S}_\theta$ retains standalone competence and prevents reward gaming).
   - Apply a single equal-weighted clipped policy update to the shared adapter $\theta$:
     $$\mathcal{L}_{\mathrm{co}}(\theta) = \frac{1}{2}\mathcal{L}_{\mathrm{clip}}(\theta; \mathcal{D}^{\textsc{imp}}) + \frac{1}{2}\mathcal{L}_{\mathrm{clip}}(\theta; \mathcal{D}^{\textsc{sol}})$$
4. **Gate workflow memory replacement on a strict dual-temperature margin ($\delta = 0.03$)**:
   - Promote the round's best candidate $\mathcal{H}^\star$ into $M[\tau]$ **only if** it beats the incumbent $M[\tau]$ by at least **$\delta = 0.03$** under both stochastic (`temperature = 1.0`) and greedy (`temperature = 0.0`) evaluation. Defer cross-run checkpoint and persistent memory commits to `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md).

### Phase 4: Zero-Retraining Test-Time Adaptation to Unseen Workflows & Schemas

When encountering an unseen workflow or new database schema at deployment (weights $\theta$ frozen):

1. **Known workflow**: Retrieve $M[\tau]$ directly (`0` `Improver` calls) and execute $\mathcal{S}_\theta(\cdot; M[\tau])$.
2. **Unseen workflow or new database schema**:
   - Retrieve the **top-3 closest stored harnesses** from $M$ via TF-IDF similarity over task descriptions and schema/endpoint metadata as structural style references.
   - **Single-pass feedback-free mode (`w/o feedback`, recommended default when batching is restricted)**: Have $\mathcal{I}_\theta$ synthesize `1` workflow harness directly from the task description, schema/API docs, and top-3 retrieved memory references (`84.5%` vs. `85.1%` with batch feedback on `MedAgentBench`, cutting tokens per solved unseen task `~2x` from `40,389` to `20,808`).
   - **Batch-evidence mode (`optional`, when an unlabeled batch of `~20` tasks is available)**: Run one greedy $\mathcal{H}_0$ pass to build reference-free `WorkflowEvidence` $P_{\tau_{\text{new}}}$ (break-even after `88` unseen tasks / `140` overall tasks) and synthesize `1` harness via $\mathcal{I}_\theta$.
   - **Never pick among multiple test-time candidate harnesses by raw majority output agreement** on write/order-optional tasks: passive `No Action` predictions agree far more easily than parameterized orders, inflating `Never Order` failure rates to `34.4%–71.6%` on baselines. Use a single greedy/random draw from the case-balanced `Improver` (`0.7%` `Never Order`) or check explicit precondition evidence before accepting an abstention.

## Failure Modes & Guardrails

- **Action-omission (`Never Order`) bias under majority agreement**: On clinical/operational workflows that conditionally require side-effecting writes (`Order Needed`), selecting among $G$ candidate harnesses by cross-harness answer agreement favors harnesses that suppress all writes (`GRPO Improver` `Order Needed` accuracy drops `42.4% -> 36.3%`). Case-type-balanced counterfactual training + single-harness deployment keeps `Order Needed` at `82.8%` (`0.7%` `Never Order`).
- **Skipping $\mathcal{H}_0$ rollouts in `Solver` training**: Training $\mathcal{S}_\theta$ exclusively with harnesses causes baseline collapse when `M[\tau]` is absent and corrupts the $\mathcal{H}_0$ reference baseline used by $\mathcal{I}_\theta$ in later rounds.
- **Unbounded harness growth**: Without the `1,500`-character cap and $\delta = 0.03$ replacement margin, workflow memories accumulate brittle case-specific exceptions that hurt unseen-workflow transfer.

## Cross-References

- **Rules**: [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Alternate model weight updates and harness search"` (contrasting frozen-proposer `WHALE`/`COEVO` alternation with shared-weight `Improver`+`Solver` RL), `"DON'T: Register self-generated capabilities on their discovery gain"` (`MedRSI` `arXiv:2609.24838` staged tool registration with frozen weights vs. `MedicalRSI` `arXiv:2611.26806` shared-weight co-evolution), and `"DO: Pass every self-modification through one acceptance gate"`.
- **Rules**: [`skill-system-design.md`](../../rules/skill-system-design.md) — `"DO: Evolve skills with stronger models, deploy to weaker ones"` (note tension: a co-trained `9B` `MedicalRSI` `Improver` beats a frozen `GPT-6.1-Sol` proposer by `+33.5 pp` and lifts `7` frozen `26B–284B`/frontier solvers by `+16.8` to `+32.3` pts).
- **Skills**: [`staged-capability-registration`](../staged-capability-registration/SKILL.md) — Probationary registration and pruning for persistent Python tool libraries on frozen LLMs.
- **Research Briefs**: [`joint-harness-weight-optimization`](../../research-briefs/joint-harness-weight-optimization.md) (`WHALE`), [`coevo-policy-aware-context-evolution`](../../research-briefs/coevo-policy-aware-context-evolution.md) (`COEVO`), and [`basersi-training-free-harness-internalization`](../../research-briefs/basersi-training-free-harness-internalization.md) (`BaseRSI`).
- **Specs**: [`self-improving-agent.spec.md`](../../specs/self-improving-agent.spec.md) and [`skill-library.spec.md`](../../specs/skill-library.spec.md).

## Sources

- *MedicalRSI: Medical Recursive Self-Improving Agents via Clinical Model-Harness Co-Evolution* (`MedicalRSI`, `arXiv:2611.26806`)
