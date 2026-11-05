# Identically Trained Language Models Break on Different Jailbreaks

> **Source**: [arXiv:2610.34074](https://arxiv.org/abs/2610.34074) — *"Identically Trained Language Models Break on Different Jailbreaks"* (Oct 2026)
> **Praxis Source ID**: `src:2610-34074`
> **Tier**: Research Brief
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Summary & Core Findings

This paper investigates whether a language model's susceptibility to specific jailbreak prompts is determined primarily by its pretraining data composition, its safety post-training run, or the stochastic trajectory of its pretraining run. Taking **75 pretrained 1B-parameter models** from the DataDecide suite (**25 pretraining data recipes $\times$ 3 pretraining random seeds**, each trained on 100B tokens with dropout disabled) plus **150M and 300M** scale checkpoints, the authors apply an identical Tülu 3 safety post-training pipeline (SFT + DPO) across **2 post-training seeds** per checkpoint (**150 safety-trained 1B models** total, plus 4 post-training seeds on the main DCLM-Baseline recipe) and evaluate 20 sampled responses per model across **6,226 decontaminated prompts** (`3,212` adversarial-harmful, `1,240` plain harmful, and `1,774` benign).

### Headline Empirical Results

1. **Pretraining seed dominates per-prompt jailbreak agreement (The Ancestry Gap)**:
   - Across `3,212` adversarial-harmful prompts, **monozygotic (MZ) twins**—models sharing the exact same pretrained checkpoint but trained with different safety post-training seeds—achieve a Spearman-corrected Pearson correlation of **$r_{\text{MZ}} = 0.984$** (95% CI `[0.982, 0.985]`) in per-prompt non-refusal rates.
   - **Same-recipe pairs**—models trained on the *exact same pretraining data recipe* and safety pipeline, differing only in their pretraining random seed—drop to **$r_{\text{S}} = 0.811$** (`[0.804, 0.817]`), an **ancestry gap of `0.173`** (`[0.167, 0.179]`) that is positive (`0.145` to `0.209`) across all 25 data recipes.
   - **Cross-recipe pairs**—models trained on different pretraining corpora and different pretraining seeds—reach **$r_{\text{X}} = 0.779$** (`[0.766, 0.788]`), only `0.032` (`[0.024, 0.043]`) below same-recipe pairs. Changing the pretraining seed reduces per-prompt agreement **`5.4x`** (`[4.0, 7.2]`) as much as changing the entire pretraining corpus.
   - On HarmBench (`1,212` prompts pairing `300` harmful requests with `91` attack templates), subtracting the main effects of average request difficulty and average template strength increases the ancestry gap from **`0.210` to `0.525`**, showing that residual prompt-by-model interaction is largely locked in during a specific pretraining trajectory.

| Model Pair Relationship | Shared Pretraining Corpus? | Shared Pretraining Checkpoint? | Shared Post-Training Seed? | Per-Prompt Non-Refusal Correlation ($r$) | Best-of-91 Template Agreement | 10–20 pp Template Lead Reversal Rate |
|:---|:---|:---|:---|:---|:---|:---|
| **MZ Twins** | Yes | Yes | No | **`0.984`** (`[0.982, 0.985]`) | **`67%`** (`[55%, 79%]`) | **`2.2%`** (`[1.9%, 2.6%]`) |
| **Same-Recipe Pairs** | Yes | No (different seed) | No | **`0.811`** (`[0.804, 0.817]`) | **`27%`** (`[19%, 35%]`) | **`25.3%`** (`[24.5%, 26.2%]`) |
| **Cross-Recipe Pairs** | No | No | No | **`0.779`** (`[0.766, 0.788]`) | — | **`26.6%`** (`[26.5%, 26.7%]`) |

2. **Hardware non-determinism alone creates a fresh vulnerability profile**:
   - Rerunning pretraining from the *exact same initialization and data order* on H200 GPUs (diverging only via floating-point non-determinism) yields $r = 0.844$ (`[0.835, 0.853]`), only `0.030` above independent pretraining seeds (`0.814` on DCLM-Baseline) and far below MZ twins (`0.985`).
   - Partial reruns sharing only weight initialization ($r = 0.822$) or only batch order ($r = 0.822$) are indistinguishable from sharing neither ($r = 0.823$). Thus, MZ twins agree because they share a specific **converged checkpoint**, not because of initial weights or data order alone.

3. **Attack rankings and single-checkpoint safety benchmarks are fragile across pretraining seeds**:
   - **Template winner instability**: The single most effective attack template out of `91` HarmBench templates transfers to an MZ twin **`67%`** of the time, but transfers to another pretraining seed of the exact same data recipe only **`27%`** of the time. Even when one attack template beats another by `>20 percentage points` on one checkpoint, their ranking reverses **`8.9%`** of the time on a sibling pretraining seed (vs **`0.05%`** on an MZ twin).
   - **Aggregate benchmark reversals**: Across all 150 models, pretraining data recipe explains **`49%`** (`[12%, 70%]`) of variance in *mean* vulnerability rate, pretraining run within recipe explains **`32%`** (`[16%, 59%]`), and post-training seed explains **`19%`** (`[11%, 37%]`). Because a single model's standard error (`3.44 pp`) is nearly as large as the true standard deviation across data recipes (`3.5 pp`), comparing two pretraining corpora using a single checkpoint per corpus reverses their true 6-model safety ordering in **`23.4%`** of recipe pairs (averaging 3 pretraining seeds reduces the standard error to `1.99 pp`).

4. **50-prompt pretraining lineage fingerprinting**:
   - Matching a safety-tuned model's non-refusal profile against reference models across all `3,211` complete prompts identifies its exact pretraining run out of `75` candidates with **`100%` (`75/75`)** accuracy.
   - Querying just **`50` randomly chosen adversarial prompts** identifies the exact pretraining run among `75` runs **`98%`** of the time across 200 random subsets—whereas even all `3,211` prompts identify the training *data recipe* of an unseen pretraining seed only **`48%` (`24/50`)** of the time.

---

## Architectural & Evaluation Implications

- **Multi-seed requirements for pretraining safety claims**: Evaluating a data filtering intervention, pretraining mix, or architecture change on a single pretraining seed conflates `32%` run-to-run variance and `19%` post-training variance with the treatment effect, reversing pairwise conclusions nearly a quarter of the time (`23.4%`).
- **Red-team benchmark overfitting to base checkpoints**: Because `60.9%` of prompts that reliably jailbreak one checkpoint ($\ge 9/10$ samples) also break a sibling pretraining seed (vs `75.0%` on MZ twins) and `10–20 pp` template leads reverse in `25.3%` of same-recipe pairs, red-teaming suites tuned against a single base checkpoint overestimate attack transferability to independently pretrained models.
- **Black-box base-model provenance auditing**: The `0.984` MZ correlation persists even when replacing Tülu 3 safety data with five external safety datasets (Nemotron-SFT-Safety-v2, Llama-Nemotron, PKU-SafeRLHF, BeaverTails, HH-RLHF; ancestry gap `+0.178` vs `0.175`), enabling grey/black-box auditors to verify whether a downstream fine-tuned model derives from a specific pretrained checkpoint using ~`50` adversarial queries.

---

## Why Not a Skill?

This paper is an empirical measurement study across a controlled 150-model pretraining and post-training grid rather than a subtask-level runtime procedure for an agent. Its actionable takeaways are quantitative decision criteria for **benchmark evaluation design** (requiring multiple pretraining seeds when comparing safety interventions and avoiding single-seed template ranking claims), which belong in always-active evaluation and safety rules rather than a procedural `SKILL.md`.

---

## Cross-References

- **Related Rules**: [`agent-evaluation-quality`](../rules/agent-evaluation-quality.md), [`agent-sandbox-safety`](../rules/agent-sandbox-safety.md)
- **Related Skills**: [`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md), [`self-improving-red-team`](../skills/self-improving-red-team/SKILL.md)
