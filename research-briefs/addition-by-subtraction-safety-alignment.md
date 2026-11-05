# Addition by Subtraction: Toward Mitigating Fragile Safety Alignment in Large Language Models

> **Source**: [arXiv:2611.06553](https://arxiv.org/abs/2611.06553) | `src:2611-06553`
> **Authors**: Hamid Dashtbani, Alexandra Dmitrienko (University of Duisburg-Essen)
> **Date**: November 2026
> **Categories**: cs.CR, cs.AI, cs.CL, cs.LG
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Summary

Standard post-training safety alignment (`RLHF`, `DPO`) concentrates refusal behavior inside a tiny, sparse subset of parameters—typically the top `1%–5%` of MLP `gate` and `up` projection neurons (`safety-critical neurons`). Because the remaining `95%+` of the network relies on these bottleneck neurons to trigger refusals, white-box sparsity attacks (`TwinBreak`, `NeuroStrike`, `Refusal-Direction Ablation`) can jailbreak aligned LLMs by zeroing out as little as `1%–5%` of neurons without degrading general utility.

`Addition by Subtraction` (`ABS-Align`) eliminates this single point of failure during `DPO` post-training (`2` epochs on `1,000` `PKU-SafeRLHF` preference pairs + `850` `Alpaca` and `150` `XSTest` benign retain samples) through a **gradual prune-then-restore curriculum**:
1. Identify the top `5%` safety-critical MLP neurons ($S$) using `5` iterative rounds of `TwinBreak` (`1%` per round based on mean activation separation $T^{(\ell)}$ between matched benign/malicious twin prompts).
2. **Freeze** all neurons in $S$ (plus the **first and last Transformer layers** to preserve input/output representations and prevent over-refusal).
3. Start `DPO` fine-tuning with the top $r = 20\%$ most important neurons in $S$ zeroed out ($W_{\text{gate}}^{(\ell)}[:, j] = 0, W_{\text{up}}^{(\ell)}[:, j] = 0$), and progressively zero out the next $r = 20\%$ of $S$ every $t_p = 200$ steps (`biggest-first` schedule) until `100%` of $S$ is deactivated—forcing gradients to construct redundant, distributed refusal circuits ($S'_1, S'_2, S'_3$) across previously non-safety neurons.
4. **Restore** all frozen safety neurons $S$ at the end of training, uniting the original circuit $S$ with the newly formed distributed circuits $S'$.

---

## Key Findings

1. **Redundant safety circuits slash white-box neuron-pruning ASR by `55%–86%`**: Against `5`-iteration `TwinBreak` on `StrongREJECT` (`313` harmful prompts, 0–1 score), `ABS-Align` lowers cumulative `ASR` from `0.71` to `0.23` (`-67.6%`) on `Gemma-2-2B-IT`, from `0.81` to `0.11` (`-86.4%`) on `Llama-3-8B-Instruct`, from `0.74` to `0.33` (`-55.4%`) on `Llama-3.2-3B-Instruct`, and from `0.79` to `0.13` (`-83.5%`) on `Qwen-3-4B`. Even under an adaptive white-box attacker that triples the pruning budget from `5` to `15` iterations (`15%` of model neurons pruned), `ABS-Align` holds `ASR@15` to `0.27`, `0.25`, `0.39`, and `0.29` across the four models—still far below the undefended 5-iteration baseline (`0.71–0.81`).
2. **Strong zero-shot transfer to unseen white-box sparsity attacks**: Without training against `NeuroStrike` (`NS`) or `Refusal-Direction Ablation` (`Rf-Dir`), `ABS-Align` reduces `NS` / `Rf-Dir` `ASR` from `0.50 / 0.80` to `0.05 / 0.08` (`-90%`) on `Gemma-2-2B-IT` and from `0.84 / 0.75` to `0.03 / 0.05` (`-96.4% / -93.3%`) on `Llama-3-8B-Instruct`. In contrast, representation-space defense `Circuit Breaker` collapses under `NeuroStrike` on `Llama-3-8B-Instruct` (`0.79` `ASR`), and weight-regularization baseline `W-DOOR` leaves `Rf-Dir` `ASR` at `0.55` on `Gemma-2-2B-IT`.
3. **Black-box jailbreak ASR drops by `20–41 pp` without adversarial prompt training**: Evaluated across `10` linguistic and persuasion black-box attack categories on `SORRY-Bench` (`440` prompts per category), `ABS-Align` lowers mean fulfillment rate (`ASR`) from `41.58%` to `13.24%` on `Gemma-2-2B-IT`, `48.34%` to `17.79%` on `Llama-3-8B-Instruct`, `53.07%` to `33.02%` on `Llama-3.2-3B-Instruct`, and `68.75%` to `27.20%` on `Qwen-3-4B`.
4. **Avoids the catastrophic over-refusal of activation-steering defenses while boosting `TruthfulQA`**: While `Deep Refusal` suffers a `48.00%` false-refusal rate on held-out `XSTest` benign prompts (`Llama-3-8B-Instruct`) and `W-DOOR` reaches `9.00%` (`Gemma-2-2B-IT`), `ABS-Align` keeps `XSTest` over-refusal at `1.00%–4.00%` across all four models (`4.00%` `Gemma-2-2B-IT`, `1.00%` `Llama-3-8B-Instruct`, `4.00%` `Llama-3.2-3B-Instruct`, `1.00%` `Qwen-3-4B`) and improves `TruthfulQA` by `+9.14` to `+14.26` points (`+9.14` `Gemma-2-2B-IT`, `+14.26` `Llama-3-8B-Instruct`, `+13.78` `Llama-3.2-3B-Instruct`, `+11.75` `Qwen-3-4B`).
5. **Gradual biggest-first pruning and boundary-layer freezing are both essential**: On `Gemma-2-2B-IT` (`0.23` `ASR`, `4.0%` over-refusal), standard `DPO` without pruning leaves `TwinBreak` `ASR` at `0.52` (`7.0%` over-refusal); pruning random neurons instead of `TwinBreak` safety neurons yields `0.50` `ASR`; pruning all `5%` safety neurons at step 0 (`non-gradual`) degrades `ASR` to `0.38`; and unfreezing the first and last Transformer layers nearly doubles `XSTest` over-refusal (`4.0%` $\to$ `7.0%`) while hurting `ARC` (`-1.09%`) and `WinoGrande` (`-1.95%`).

---

## Quantitative Summary

### Cross-Model Defense Comparison (`StrongREJECT` White-Box, `SORRY-Bench` Black-Box, `XSTest` Over-Refusal, `TruthfulQA`)

| Model & Method | `TwinBreak` (`5` iter) `ASR` $\downarrow$ | `NeuroStrike` (`NS`) `ASR` $\downarrow$ | `Refusal-Dir` (`Rf-Dir`) `ASR` $\downarrow$ | Adaptive `TwinBreak` `@10 / @15` $\downarrow$ | `SORRY-Bench` Mean (`10` attacks) $\downarrow$ | `XSTest` Over-Refusal (`%`) $\downarrow$ | `TruthfulQA` (`%`) $\uparrow$ |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`Gemma-2-2B-IT`** (No Defense) | `0.71` | `0.50` | `0.80` | — | `41.58%` | `2.00%` | `46.51%` |
| `Gemma-2-2B-IT` + `W-DOOR` | `0.62` | `0.19` | `0.55` | — | `35.36%` | `9.00%` | `51.65%` |
| **`Gemma-2-2B-IT` + `ABS-Align`** | **`0.23`** | **`0.05`** | **`0.08`** | **`0.26 / 0.27`** | **`13.24%`** | **`4.00%`** | **`55.65%`** (`+9.14`) |
| **`Llama-3-8B-Instruct`** (No Defense) | `0.81` | `0.84` | `0.75` | — | `48.34%` | `5.00%` | `51.65%` |
| `Llama-3-8B-Instruct` + `Circuit Breaker` | `0.16` | `0.79` | `0.24` | — | `16.06%` | `4.00%` | `51.90%` |
| `Llama-3-8B-Instruct` + `Deep Refusal` | `0.25` | `0.06` | `0.07` | — | `21.81%` | `48.00%` | `58.95%` |
| **`Llama-3-8B-Instruct` + `ABS-Align`** | **`0.11`** | **`0.03`** | **`0.05`** | **`0.25 / 0.25`** | **`17.79%`** | **`1.00%`** | **`65.91%`** (`+14.26`) |
| **`Llama-3.2-3B-Instruct`** (No Defense) | `0.74` | `0.79` | `0.57` | — | `53.07%` | `4.00%` | `49.45%` |
| **`Llama-3.2-3B-Instruct` + `ABS-Align`** | **`0.33`** | **`0.37`** | **`0.30`** | **`0.38 / 0.39`** | **`33.02%`** | **`4.00%`** | **`63.23%`** (`+13.78`) |
| **`Qwen-3-4B`** (No Defense) | `0.79` | `0.89` | `0.70` | — | `68.75%` | `3.00%` | `54.96%` |
| **`Qwen-3-4B` + `ABS-Align`** | **`0.13`** | **`0.44`** | **`0.09`** | **`0.22 / 0.29`** | **`27.20%`** | **`1.00%`** | **`66.71%`** (`+11.75`) |

### `ABS-Align` Ablation Study on `Gemma-2-2B-IT` (Table VII)

| Ablation Variant | `TwinBreak` `ASR` $\downarrow$ | `XSTest` Over-Refusal (`%`) $\downarrow$ | Key Takeaway |
|:---|:---:|:---:|:---|
| **Full `ABS-Align` (`2` epochs, gradual `20%`/step, freeze $S$ + first/last layers)** | **`0.23`** | **`4.0%`** | Optimal balance of distributed redundancy and low over-refusal |
| `DPO` without neuron pruning | `0.52` | `7.0%` | Standard `DPO` reinforces existing bottleneck neurons ($S$) instead of creating new circuits |
| Prune random neurons (instead of `TwinBreak` safety neurons $S$) | `0.50` | `6.0%` | Leaving $S$ active prevents gradients from migrating refusal to backup neurons |
| Non-gradual pruning (prune `100%` of $S$ from step 0) | `0.38` | `3.0%` | Sudden removal of all safety neurons destabilizes refusal recovery (`+0.15` `ASR` vs. gradual) |
| Decremental pruning (prune all at start, gradually restore) | `0.31` | `3.0%` | Early restoration lets the model fall back on $S$ prematurely |
| Unfreeze first and last Transformer layers | `0.23` | `7.0%` | Boundary-layer drift inflates benign false refusals (`4.0%` $\to$ `7.0%`) and hurts general utility |
| Shorter (`1` epoch) / Longer (`4` epochs) training | `0.45` / `0.32` | `3.0%` / `5.0%` | `1` epoch under-trains later circuit tiers; `4` epochs overfits the small dataset |

---

## Why Not a Skill?

1. **Weight-level post-training procedure**: `ABS-Align` modifies internal MLP weight tensors ($W_{\text{gate}}^{(\ell)}, W_{\text{up}}^{(\ell)}$) during `DPO` fine-tuning of open-weight LLMs rather than operating as an inference-time or harness-level procedure for an AI agent.
2. **Complements existing MoE and representation-probe briefs**: It pairs directly with [`moe-safety-sensitive-experts.md`](moe-safety-sensitive-experts.md) and [`safestart-moe-expert-reduction-safety.md`](safestart-moe-expert-reduction-safety.md) as model-layer safety context.

---

## Actionable Takeaways

- **Do not rely on single-circuit safety alignment for open-weight models**: Standard `DPO` leaves `TwinBreak` `ASR` at `0.52–0.81` when just `5%` of MLP neurons are ablated. Gradual biggest-first deactivation (`20%` of top `5%` safety neurons every `200` steps) during `DPO` followed by neuron restoration forces multi-circuit refusal redundancy.
- **Freeze the first and last Transformer blocks during safety fine-tuning**: Allowing `DPO` updates on the input embedding block and final projection block nearly doubles false refusals on benign `XSTest` prompts (`4.0%` $\to$ `7.0%`) and degrades reasoning benchmarks (`ARC`, `WinoGrande`) without improving safety (`0.23` `ASR` in both cases).
- **Benchmark white-box defenses against both weight-space (`TwinBreak`, `NeuroStrike`) and direction-space (`Refusal-Direction`) attacks**: Representation-rerouting defenses like `Circuit Breaker` resist `TwinBreak` (`0.16`) and `Refusal-Direction` (`0.24`) but fail completely against `NeuroStrike` (`0.79` on `Llama-3-8B-Instruct`).

---

## Related Artifacts

- **Research Brief**: [`moe-safety-sensitive-experts.md`](moe-safety-sensitive-experts.md) — Safety concentration in sparse Mixture-of-Experts routing and expert layers.
- **Research Brief**: [`safestart-moe-expert-reduction-safety.md`](safestart-moe-expert-reduction-safety.md) — Mitigating refusal loss from active expert truncation during MoE serving.
- **Skill**: [`layered-defense-ensemble`](../skills/layered-defense-ensemble/SKILL.md) — Combining model-level and harness-level safety defenses with measured failure correlation.
- **Rules**: [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — Defense-in-depth requirements for aligned models and agent runtimes.
