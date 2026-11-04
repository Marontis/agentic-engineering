# Disparity Laundering: Consensus Without Fairness in Clinical Multi-Agent Systems

> **Source**: [arXiv:2610.38215](https://arxiv.org/abs/2610.38215) — *Disparity Laundering: Consensus Without Fairness in Clinical Multi-Agent Systems* (Wang et al., published 2026-10-28)  
> **Praxis ID**: `src:2610-38215`  
> **Tier**: Research Brief

## Summary

Multi-agent clinical decision systems are deployed on the assumption that peer deliberation averages out individual agent errors. Wang et al. demonstrate across a full $5 \times 4$ factorial (`5` open-weight model families $\times$ `4` communication topologies, `3` seeds per cell) on `120` real MIMIC-IV-ED emergency encounters under byte-identical counterfactual demographic swaps that **deliberation does not average out demographic allocation bias—it launders it**. While single agents flip Emergency Severity Index (ESI) triage levels on `6.2%`–`10.6%` of cases under a Black vs. White swap (`63:26` to `99:11` toward more acute triage for Black patients) at equal diagnostic accuracy against gold outcomes ($\Delta \text{MAE}$ within $\pm 0.034$ ESI), **all `20` multi-agent model-by-topology cells** (`57/60` replicate runs negative, `3/60` zero, `0/60` positive; `80/80` deliberation stage readings negative) commit the exact same directional disparity. Every model has at least one topology that amplifies its single-agent baseline gap (`12/20` cells amplify, `15/20` retain $\ge 80\%$ of baseline gap while consensus rises in `16/20`), and which topology amplifies is model-dependent. Crucially, late-stage aggregator fairness instructions and demographic masking move the gap by at most `~0.02` ESI, per-agent self-debiasing *backfires* and widens the gap in **`17 of 20` cells** (`5/5` models pooled, more than doubling `Phi-4` from `-0.033` to `-0.078`), and **`0 of 1,983` free-text rationales** behind divergent decisions mention race—because the bias is already encoded in the upstream agents' structured clinical numbers. The only effective repair is to make counterfactual comparisons internal to deliberation: the **Diverse-Perspective Ensemble (DPE)**—feeding each of the 5 agents a different demographic variant (`White`, `Black`, `Hispanic`, `Asian`, `control`) under an all-to-all pooling topology (`SharedPool`)—re-converges `88%`–`98%` of initial disagreements and collapses the triage disparity by **`67%` to `94%`** at zero accuracy cost.

## Why Not a Skill?

This paper is an empirical clinical fairness audit and topology factorial study on MIMIC-IV-ED vignettes. Its methodological contributions—the **Cross-Version Counterfactual Audit** and **Diverse-Perspective Ensemble (DPE)**—are documented in full below and distilled into multi-agent coordination and evaluation rules in `output/rules/multi-agent-coordination.md` and `output/rules/agent-evaluation-quality.md`.

## Experimental Scope

- **Cohorts**: `120` MIMIC-IV-ED encounters in `5` race variants (`White`, `Black`, `Hispanic`, `Asian`, `control`; `60` with gold ESI labels) + `118` sex-invariant encounters in `3` sex variants (`Male`, `Female`, `control`, `8` seeds on `Qwen3`).
- **Models (`5` families, vLLM on A40 GPUs, temp `0.7`, `3` seeds/cell)**: `Qwen3-32B`, `Mistral Small 3.1 24B`, `MedGemma 27B`, `Phi-4 14B`, `Llama 3.3 70B`, plus a 5-family mixed team.
- **Topologies (`5` agents, $r_0 \to r_1 \to r_2 \to \text{agg}$)**: `SharedPool` (all-see-all), `Decentralized` (ring of 2 neighbors), `Layers` (chain of 1 predecessor), `Centralized` (1 hub + 4 spokes).
- **6-Field JSON Schema**: `triage_acuity` (`1`–`5` ESI), `testing_recommended`, `imaging_recommended`, `admission_recommended`, `analgesia_strength` (`0`–`3`), `mental_health_referral`.

## Key Quantitative Findings

### 1. Full $5 \times 4$ Triage Disparity Grid Across Topologies & Interventions (`Table 4`, `Black - White` ESI Gap)

| Model | Topology | Independent ($r_0$) | Committed (`agg`) | `+ fairness` | `+ masking` | `+ self-debias` | Homogeneous $r_2$ | `+ DPE` (Internal $r_2$) |
|:------|:---------|:--------------------|:------------------|:-------------|:------------|:----------------|:------------------|:-------------------------|
| **`Qwen3`** | `SharedPool` | `-0.044` | `-0.047` | `-0.047` | `-0.050` | `-0.050` | `-0.050` | **-0.003** (`94%` reduction) |
| | `Decentralized` | `-0.036` | `-0.058` | `-0.058` | `-0.061` | `-0.044` | `-0.056` | **0.000** (`100%` reduction) |
| | `Layers` | `-0.033` | `-0.064` | `-0.050` | `-0.044` | `-0.083` | `-0.039` | `-0.042` |
| | `Centralized` | `-0.039` | `-0.031` | `-0.044` | `-0.039` | `-0.067` | `-0.036` | `-0.025` |
| **`Mistral`** | `SharedPool` | `-0.058` | `-0.069` | `-0.072` | `-0.072` | `-0.050` | `-0.058` | **+0.006** (`91%` reduction) |
| | `Decentralized` | `-0.022` | `-0.019` | `-0.034` | `-0.014` | `-0.064` | `-0.025` | `-0.008` |
| | `Layers` | `-0.086` | `-0.053` | `-0.072` | `-0.049` | `-0.083` | `-0.050` | `-0.138` (widened) |
| | `Centralized` | `-0.056` | `-0.025` | `-0.033` | `-0.033` | `-0.061` | `-0.033` | `+0.039` |
| **`MedGemma`** | `SharedPool` | `-0.042` | `-0.053` | `-0.047` | `-0.056` | `-0.047` | `-0.047` | `-0.006` (`89%` reduction) |
| | `Decentralized` | `-0.053` | `-0.058` | `-0.053` | `-0.056` | `-0.078` | `-0.058` | **+0.003** (`95%` reduction) |
| | `Layers` | `-0.033` | `-0.039` | `-0.036` | `-0.039` | `-0.078` | `-0.036` | `-0.094` (widened) |
| | `Centralized` | `-0.064` | `-0.039` | `-0.031` | `-0.033` | `-0.092` | `-0.028` | **-0.003** |
| **`Phi-4`** | `SharedPool` | `-0.025` | `-0.025` | `-0.014` | `-0.025` | `-0.078` | `-0.019` | **-0.008** (`67%` reduction) |
| | `Decentralized` | `-0.014` | `-0.025` | `-0.025` | `-0.031` | `-0.075` | `-0.047` | `-0.017` |
| | `Layers` | `-0.031` | `-0.039` | `-0.058` | `-0.044` | `-0.086` | `-0.050` | `-0.081` (widened) |
| | `Centralized` | `-0.031` | `-0.042` | `-0.036` | `-0.044` | `-0.072` | `-0.042` | `-0.031` |
| **`Llama`** | `SharedPool` | `-0.061` | `-0.039` | `-0.039` | `-0.039` | `-0.075` | `-0.039` | **-0.003** (`92%` reduction) |
| | `Decentralized` | `-0.053` | `-0.044` | `-0.044` | `-0.044` | `-0.078` | `-0.042` | `-0.011` |
| | `Layers` | `-0.050` | `-0.061` | `-0.064` | `-0.064` | `-0.072` | `-0.058` | `-0.047` |
| | `Centralized` | `-0.047` | `-0.050` | `-0.050` | `-0.050` | `-0.078` | `-0.053` | `-0.025` |

### 2. Diagnostic Signatures of Disparity Laundering

- **Rationale Audits Are Blind (`Appendix C.8`)**: Across `23,021` free-text rationales (`11,520` per model on `Qwen3` and `Mistral` `SharedPool`), **`0 of 1,983` rationales** behind the `62` divergent Black vs. White committed decisions mention race, ethnicity, or any demographic term.
- **Per-Agent Self-Debiasing Backfires (`Table 10`)**: Prepending self-debiasing instructions to every agent and the synthesizer enlarges the committed gap in **`17 of 20` cells** and in **all `5` models** pooled (`Qwen3` `-0.050 → -0.061`, `Mistral` `-0.042 → -0.065`, `MedGemma` `-0.047 → -0.074`, `Phi-4` `-0.033 → -0.078`, `Llama` `-0.049 → -0.076`).
- **Trajectory-Only Sex Disparity (`Appendix C.3`)**: On `118` sex-invariant cases (`Qwen3`, `8` seeds), `Centralized` debate introduces a unanimous `10/10` male-favoring imaging disparity at $r_1$ that vanishes at the final `agg` output—invisible to both single-model and final-output audits.
