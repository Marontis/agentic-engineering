# Safin-1.5: Safety-Native Architecture and Verifiable Reasoning for Recursive Safety Improvement

> **Source**: [arXiv:2610.40751](https://arxiv.org/abs/2610.40751) — Jingnan Zheng, Cheng Jin, Ming Zhang, Huan Sun, et al. (Safin Team, Shanghai AI Laboratory, 2026-10-29)
> **Praxis Source ID**: `src:2610-40751`
> **Category**: Research Brief (Safety-Native MoE Architecture, Recursive Safety Improvement & Neuro-Symbolic Formal Reasoning)

---

## Why Not a Skill?

**Safin-1.5** (`35B-A3B`) is an integrated full-stack system report combining three layers: (1) a safety-native Mixture-of-Experts architecture (`MARCH` persistent safety memory + `REX` multi-domain removable experts), (2) an automated 3-stage training loop (`ReSI`: Recursive Safety Improvement), and (3) an inference-time neuro-symbolic formal reasoning harness (`POGB`: Proof-Obligation-Guided Bridging). Because the first two layers require MoE expert surgery and multi-stage post-training, the full paper is cataloged as a research brief with architectural/training rules for [`../rules/recursive-improvement.md`](../rules/recursive-improvement.md) and [`../rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

---

## Core Findings

### 1. Multi-Domain `REX` Disentanglement Prevents Post-Training Rebound

Standard parameter-level unlearning (`RMU`, `NPO`) suppresses hazardous knowledge in shared weights, which rebounds almost completely during subsequent post-training or recursive self-improvement. On `Safin-1-35B-A3B` (256 routed experts/layer), **Safin-1.5** expands each layer by **16 removable experts** (272 total, source scaling $\gamma = 0.3$) selected by joint Bio+Cyber differential top-$K$ activation ($\approx 40\text{M}$ target tokens at `4:1 Bio:Cyber` + $\approx 27\text{M}$ general tokens), excises them, applies a 32M-token RMU cleanup on layers 7–9 (`A2`), and runs **250M tokens of standard full-parameter SFT on the recombined full model (`F3`) before excising again at deployment (`A3`)**:

| Stage / Training Route | `WMDP-Bio` ($\downarrow$, 25% chance) | `WMDP-Cyber` ($\downarrow$, 25% chance) | `MMLU` ($\uparrow$) | Kept Removal Share (Bio / Cyber) |
|:-----------------------|:--------------------------------------|:----------------------------------------|:--------------------|:---------------------------------|
| **Original `B` (`Safin-1`)** | 82.6% | 58.3% | 82.3% | — |
| **Base `R` (RMU on `B`)** | 56.9% | 32.7% | 82.0% | — |
| **Base `A2` (`REX` + identical RMU)** | **36.2%** | **29.5%** | 78.9% | — |
| **250M SFT `R-SFT` (on `R`)** | 81.7% | 47.2% | 82.4% | **3.4% / 43.6%** (rebounds) |
| **250M SFT `A3-direct` (on excised `A2`)** | 64.0% | 41.8% | 80.7% | 40.0% / 57.5% |
| **250M SFT `A3` (`REX` train full `F3`, excise)** | **40.8%** | **32.5%** | 80.2% | **90.0% / 89.9%** |
| **250M SFT `F3` (un-excised full model)** | 82.8% | 57.4% | 82.6% | — |

- **Train Full, Deploy Excised**: Training the excised model directly (`A3-direct`) pushes hazardous tokens back into retained experts (`WMDP-Bio` rises from `36.2%` to `64.0%`, keeping only `40.0%` of removal). Training the recombined full structure `F3` keeps router specialization intact so hazardous updates stay inside the removable experts and vanish upon excision (`A3` retains **90.0% Bio / 89.9% Cyber** removal vs. **3.4% / 43.6%** for `R-SFT`).

### 2. `ReSI` Recursive Safety Improvement Loop

In each round $r$, **ReSI** (1) attacks $M_r$ with extensible red-teaming pools (`DARWIN`, `JailbreakSkill`), (2) pilot-screens attack sources $\boldsymbol{\alpha}$ and alignment methods $a \in \{\text{A3}, \text{SInternal}, \text{AlphaAlign}\}$, and (3) runs full-scale training with up to $N_{\mathrm{refine}}$ feedback-guided revisions (`S1` attack composition, `S2` harmful–benign pairing, `S3` replay/LR adjustment, `S4` post-SFT safety GRPO/DAPO), accepting only checkpoints passing an **$M_0$-anchored Pareto gate** ($g_r(\omega) > 0 \land \mathrm{BC}(M_r^\omega) \ge \mathrm{BC}(M_0) - \epsilon \land \mathrm{IF}(M_r^\omega) \ge \mathrm{IF}(M_0) - \epsilon$):

| Model | `WildJailbreak` $\downarrow$ | `HarmBench` $\downarrow$ | `H-CoT` $\downarrow$ | `X-Teaming` $\downarrow$ | `XSTest` $\uparrow$ | `MMLU-Pro` $\uparrow$ | `IFEval` $\uparrow$ | `WMDP-Bio / Cyber` $\downarrow$ |
|:------|:-----------------------------|:-------------------------|:---------------------|:-------------------------|:--------------------|:----------------------|:--------------------|:--------------------------------|
| **Safin-1 (Base)** | 2.10% | **0.25%** | 82.00% | 64.78% | 88.40% | 77.10% | 85.58% | 82.56% / 58.33% |
| **Safin-1 + A3** | 0.70% | 1.00% | 24.00% | — | 84.80% | 77.40% | 80.59% | — |
| **Safin-1 + ReSI** | **0.35%** | **0.25%** | **6.00%** | — | 85.60% | **79.40%** | 84.29% | — |
| **Safin-1 + REX (`A3`)** | 2.10% | 1.00% | 64.00% | — | 95.20% | 79.20% | 92.61% | 40.8% / 32.5% |
| **Safin-1 + REX + A3** | 1.40% | 1.25% | 14.00% | — | 84.80% | **79.80%** | 72.46% | — |
| **Safin-1.5 (`+REX +ReSI`)** | **1.20%** | 1.25% | **14.00%** | **32.08%** | 86.80% | 76.80% | **87.06%** | **43.68% / 33.17%** |
| **GPT-5.6-Luna** | 1.90% | **0.00%** | **8.00%** | 56.69% | **100.00%** | — | — | — |
| **Claude Opus 5** | 9.25% | 3.50% | 38.00% | 84.85% | 98.80% | — | — | — |
| **GLM-5.3 / Kimi K3** | 5.35% / 4.50% | 3.25% / 3.75% | 24.00% / 18.00% | 76.73% / 77.80% | 99.20% / 99.60% | — | — | — |

### 3. `POGB`: Proof-Obligation-Guided Bridging for Verifiable Reasoning

To bridge missing semantic links in First-Order Logic (`FOL`) autoformalization without allowing the LLM to hallucinate proof steps, **POGB** constructs a typed/natural-language **Grounding Table $\mathcal{T}$** (`type` + `NL` referring/predicate templates), keeps recursive deduction (`Prove`, with ancestor cycle detection $\mathcal{A}$) and residual abduction ($\mathfrak{o} = \textsc{Abduce}(\mathcal{I}, \Sigma)$) strictly inside the symbolic solver $\mathcal{S}$, and restricts neural models (`all-MiniLM-L6-v2` similarity, `roberta-large-mnli` at $\tau_{\mathrm{NLI}} = 0.80$, and the LLM `Gate`) to validating candidate 1-to-2-literal semantic bridges $\Sigma \to \phi$:

- Across **1,804 problems** (`FOLIO` $N=204$, `ProofWriter` $N=600$, `PrOntoQA` $N=500$, `ProverQA-Hard` $N=500$), `Safin-1.5 + POGB` achieves **91.80% weighted average accuracy** (**88.73% `FOLIO`** [highest of all models, beating `Claude Opus 5 Direct` at `87.75%`], **99.50% `ProofWriter`**, **100.00% `PrOntoQA`**, **75.60% `ProverQA-Hard`**), outperforming `Kimi K3` (`91.02%`), `Gemini3-Flash CoT` (`89.63%`), `GLM-5.3 CoT` (`89.30%`), `Qwen3.8-Flash CoT` (`88.75%`), `GPT-5.5 Direct` (`88.08%`), `DeepSeek-V3.2 CoT` (`87.03%`), and `GPT-5.6-Luna CoT` (`83.65%`), while producing machine-checkable proofs.

---

## Relevance to Praxis

- **Recursive Self-Improvement Gating ([`../rules/recursive-improvement.md`](../rules/recursive-improvement.md))**: Anchor benign-compliance and instruction-following retention thresholds in recursive training gates to the **initial baseline model $M_0$** ($\mathrm{BC}(M_r^\omega) \ge \mathrm{BC}(M_0) - \epsilon$) rather than the previous round $M_r$ so small per-round losses cannot compound across rounds; when updating MoE models with excised capability modules (`REX`), train on the recombined full model and red-team/gate the excised deployment artifact.

---

## Key Citations

- **Jin et al. (2026)** — *REX: Relocating Hazardous Knowledge into Removable Experts in Mixture-of-Experts Models* (`arXiv:2610.25791`).
- **Zheng et al. (2026)** — *ReSI: Recursive Safety Improvement* (`arXiv:2610.12233`).
- **Sun et al. (2026)** — *Let Solvers Reason and Models Understand: Proof-Obligation-Guided Bridging (POGB)*.
