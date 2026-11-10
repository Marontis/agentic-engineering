# When Experience Becomes a Backdoor: Poisoning Self-Evolving LLM Agents via Failure-Aware Task Optimization

> **Source**: [arXiv:2611.10542](https://arxiv.org/abs/2611.10542) — Minhua Lin, Zongyu Wu, Hanqing Lu, Xianfeng Tang, Xiang Zhang, Qi He, Suhang Wang (2026)
> **Praxis Source ID**: `src:2611-10542v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`BadEvolve` is an offensive task-poisoning framework designed to implant persistent trigger-conditioned backdoors into self-evolving LLM agents by optimizing poisoned tasks injected into the agent's evolution dataset ($\mathcal{D}_{\mathrm{evolve}}$). Per the offensive-security policy in [`AGENTS.md`](../AGENTS.md), we do not package offensive backdoor optimization loops as reusable skills; instead, this brief extracts the structural vulnerability analysis, empirical threat telemetry across four skill-evolution frameworks, and defensive hardening requirements for self-improving agent pipelines.

---

## Threat Model & Core Vulnerability Mechanism

Self-evolving agent frameworks (`Trace2Skill`, `SkillGrad`, `SkillOpt`, `A-Evolve`) iteratively solve tasks in an evolution set $\mathcal{D}_{\mathrm{evolve}}$ (`40` clean tasks on `SpreadsheetBench` and `WikiTQ`, `50` on `OfficeQA`) and distill successful/failed trajectories into persistent Markdown or structured skills reused at test time. Unlike direct skill-file injection ([`skill-evolution-defense`](../skills/skill-evolution-defense/SKILL.md)) or reference-answer feedback poisoning ([`feedback-poisoning-skill-promotion-guard`](../skills/feedback-poisoning-skill-promotion-guard/SKILL.md)), `BadEvolve` assumes the attacker has **zero direct write access** to the victim's skill repository, internal trajectories, evolution prompts, or model weights—only contributing up to $B = 20$ poisoned tasks ($\mathcal{D}_{\mathrm{poison}}$) to the task stream.

### Why Outcome-Only Poisoning Stalls vs. Four-Stage Causal Coupling

For a task-level poison to become an active deployment backdoor on triggered test queries, it must survive **four sequential stages**:

1. **Induction ($\hat{p}_I$)**: The evolution module abstracts a trigger-conditioned rule from poisoned task rollouts and retains it through candidate ranking and validation gates into the persistent skill library.
2. **Activation ($\hat{p}_{A \mid I}$)**: At test time, the skill selector/router loads the poisoned skill when the trigger appears.
3. **Following ($\hat{p}_{F \mid A}$)**: The downstream solver LLM executes the conditional branch rather than ignoring it as irrelevant boilerplate.
4. **Effect ($\hat{p}_{E \mid F}$)**: Executing the rule produces the target payload (`Payload Injection`, `PI`) or corrupts task reasoning (`Answer Corruption`, `AC`).

Naive black-box prompt optimizers (`TextGrad-Poison`, which updates $\mathcal{D}_{\mathrm{poison}}$ from final downstream ASR alone) stall at `27.8%` mean ASR on `Kimi-K2.5` and `28.8%` on `GPT-OSS-120B` (`0.0%` in `3/8` configurations) for two reasons:
- **Diagnostic collapse**: `0%` downstream ASR hides *which* stage failed (`Induction` vs. `Activation` vs. `Following`).
- **Destructive stage coupling**: Edits that strengthen one stage frequently collapse another—for example, aggressively specializing poisoned tasks on `A-Evolve x SpreadsheetBench` boosts `Induction` from `40%` to `80%` while crashing `Activation` to `0%`, and a single unguarded edit on `SkillGrad x WikiTQ` collapses validation ASR from `53%` to `0%`.

By probing a local shadow run ($K = 5$ stochastic rollouts across $L = 5$ optimization rounds) with stage-wise diagnostic rates, rolling back updates whose validation ASR drops by more than $\epsilon = 0.4$, and recording failed edits in a failure memory, `BadEvolve` resolves cross-stage bottlenecks—even when the attacker optimizes on a **different surrogate LLM** (`gray-box` setting).

---

## Key Empirical Findings

### 1. Persistent Payload Injection (`PI`) Across 4 Frameworks and 3 Benchmarks

Across all `12` framework $\times$ dataset combinations (`Trace2Skill`, `SkillGrad`, `SkillOpt`, `A-Evolve` $\times$ `SpreadsheetBench`, `WikiTQ`, `OfficeQA`) on `Kimi-K2.5` (`100` test tasks, `40` validation tasks):

| Method | Mean `PI` ASR (`Kimi-K2.5`) | ASR Range Across `12` Settings | Clean Accuracy (`CACC`) Impact vs. Clean Evolution (`CACC_0`) |
|:---|:---:|:---:|:---:|
| Fixed `TBA` task-poisoning baseline | `37.6%` | — | Preserved |
| Outcome-only `TextGrad-Poison` | `27.8%` (`28.8%` on `GPT-OSS-120B`) | `0.0%` in `3/8` `GPT-OSS-120B` settings | Preserved |
| **`BadEvolve` (4-stage + rollback + memory)** | **`79.6%`** (`+51.8 pp` vs. `TextGrad-Poison`, `+42.0 pp` vs. `TBA`) | **`59.3%–100.0%`** (`100.0%` `SkillOpt x SB`, `98.7%` `A-Evolve x WikiTQ`, `96.7%` `SkillGrad x WikiTQ`, `92.0%` `Trace2Skill x SB`) | **`-1.1 pp` mean `CACC` delta**; triggered task accuracy (`TACC`) drops `<= 3.3 pp` vs. `CACC` |

### 2. Bypassing Impact Rankers and Clean-Accuracy Gates via Procedural Reframing (`Answer Corruption`)

A critical defensive finding is **why** `SkillOpt`'s generality/impact ranker and clean validation accuracy (`CACC`) gates fail to reject `BadEvolve`:
- When an induced rule looks like `"output formatting"`, `SkillOpt`'s ranker drops it as having *"no impact on answer correctness"*.
- Stage-aware optimization reframes the trigger-conditioned rule as an **essential domain-specific procedural step** (for example, a table-reading convention or *"apply one final advance"* step on `WikiTQ`), doubling `Induction` ($\hat{p}_I: 40\% \to 80\%$) and lifting validation ASR from `40.0%` to `79.5%`.
- Under the **`Answer Corruption (AC)`** objective on `WikiTQ` (where the trigger causes the agent to compute wrong answers while clean tasks behave normally):
  - **`A-Evolve` on `Kimi-K2.5`**: Achieves **`80.0%` Degradation ASR (`DASR`)** vs. `68.5%` best baseline—crashing triggered task accuracy (`TACC`) by **`66.4 pp`** (from `86.0%` `CACC_0` down to **`19.6%`**) while clean accuracy (`CACC`) stays at **`86.2%`** (`+0.2 pp` above clean evolution!).
  - **`A-Evolve` on `Claude Sonnet 4.6`**: Achieves **`54.1%` `DASR`** vs. `18.0%` best baseline—dropping `TACC` by **`45.2 pp`** (`86.8% -> 41.6%`) while `CACC` stays identical at **`86.8%`**.
  - **`Trace2Skill` on `Kimi-K2.5`**: Achieves **`34.0%` `DASR`** vs. `<= 14.1%` for all baselines.

### 3. Cross-Backbone Gray-Box Surrogate Transfer & Ablation Sensitivity

- **Unknown Victim Backbone (`Gray-Box`)**: When poisoned tasks are optimized on open-weight surrogates (`GPT-OSS-120B`, `Qwen3-235B`, or `Claude Sonnet 4.6`) and evaluated against an unseen `Kimi-K2.5` victim, `BadEvolve` averages **`84.6%` ASR** (`59.7%–100.0%`, with `CACC`/`TACC` within `4.6 pp` of `CACC_0`). On `SkillOpt x WikiTQ`, surrogate optimization from `GPT-OSS-120B` or `Qwen3-235B` reaches **`100.0%` ASR**, exceeding same-backbone optimization (`66.7%`) because stronger/cleaner surrogate rollouts induce more portable procedural rules.
- **Component Ablations**: Removing stage-wise feedback (`BadEvolve\SF`) or failure memory (`BadEvolve\FM`) collapses ASR to **`0.0%`** on `OfficeQA x SkillGrad`, and removing rollback (`BadEvolve\RB`) drops `WikiTQ x Trace2Skill` ASR to **`33.3%`**.

---

## Defensive Lessons for Self-Evolving Agent Systems

1. **Treat $\mathcal{D}_{\mathrm{evolve}}$ task streams as untrusted supply-chain inputs**: Never ingest crowdsourced issues, unverified user tickets, or scraped tasks directly into skill-evolution loops without provenance attestation and anomaly clustering across task phrasing/sentinel patterns.
2. **Never rely on clean accuracy (`CACC`) or "impact-on-correctness" rankers as security gates**: Trigger-conditioned procedural branches (`if <marker/pattern> -> apply offset/override`) achieve `0.0–0.2 pp` `CACC` delta while inflicting `45.2–66.4 pp` accuracy collapse on triggered inputs (`AC`). Pair [`feedback-poisoning-skill-promotion-guard`](../skills/feedback-poisoning-skill-promotion-guard/SKILL.md) (leave-one-edit-out marginal validation $\Delta_i > 0$ on clean validation tasks—where a dormant trigger rule has $\Delta_i \approx 0$ even when disguised as a procedural step!) with `"DO: Pass every self-modification through one acceptance gate"` in [`rules/recursive-improvement.md`](../rules/recursive-improvement.md).
3. **Audit candidate skills for conditional branching and counterfactual rule deletion**: Statically and semantically inspect newly induced skill clauses for Narrow-Condition / High-Impact branches (`when query/table contains X, adjust step Y`) and verify that every retained clause demonstrably improves clean held-out trajectories when ablated individually.
4. **Monitor post-deployment `Activation` and `Following` concentration**: Track whether specific skill clauses activate disproportionately on inputs containing unusual formatting, lexical markers, or rare structural motifs.

## Related Artifacts

- [`feedback-poisoning-skill-promotion-guard`](../skills/feedback-poisoning-skill-promotion-guard/SKILL.md) — Four-gate defense (literal abstraction, mandatory ranking, leave-one-edit-out marginal validation, clean endpoint sandboxes) against `SkillOpt` backdoor promotion (`arXiv:2611.09348`).
- [`skill-evolution-defense`](../skills/skill-evolution-defense/SKILL.md) — Provenance verification, mutation filtering, and quarantine for evolving skill libraries (`arXiv:2608.30429`).
- [`hybrid-sandbox-skill-intent-audit`](../skills/hybrid-sandbox-skill-intent-audit/SKILL.md) — Three-layer static, sandbox dry-run, and agentic `SKILL.md` intent scanner (`arXiv:2611.10830`).
- [`rules/recursive-improvement.md`](../rules/recursive-improvement.md) — `"DON'T: Allow self-modifying agents to optimize prompts or scaffolding solely against performance benchmarks"` and `"DON'T: Promote bundled text-space skill edits on aggregate clean validation accuracy alone"`.
