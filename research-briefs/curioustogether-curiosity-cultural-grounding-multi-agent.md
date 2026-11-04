# CuriousTogether: Implications of Curiosity and Cultural Grounding in Multi-Agent LLM Interactions

> **Source**: [arXiv:2611.01301](https://arxiv.org/abs/2611.01301) — Borah et al. (University of Michigan, University of Toronto & Vector Institute, MPI for Intelligent Systems, EuroSafeAI, 2026-10-31)  
> **Praxis Source ID**: `src:2611-01301`  
> **Tier**: Research Brief

## Summary

CuriousTogether evaluates how explicit curiosity prompting (`All-Curious`, `Single-Curious`, `No-Curiosity`) and cultural persona grounding (20 countries across 6 continents) shape $K=3$ agent, $T=2$ round discussions across 8 benchmarks and 6 open-weight models (`7B–14B`) plus 2 larger models (`70B–72B`). Curiosity and cultural diversity significantly improve open-ended hypothesis generation (`+0.053` inter-agent alignment, $p_{\text{Holm}} < 8 \times 10^{-7}$; `+0.050` idea diversity) and social bias mitigation (`+14.90` percentage points in non-stereotypical responses, $p_{\text{Holm}} < 7 \times 10^{-6}$), but yield null or negative returns on convergent multi-hop reasoning tasks (`StrategyQA`: `-0.77` pp from curiosity, `-1.96` pp from cultural personas) after Holm multiple-testing correction.

## Key Findings

### 1. Divergent Exploration vs. Convergent Reasoning Split Across 8 Benchmarks

Pooled across six `7B–14B` models (`Llama-3-8B-Instr`, `Qwen-2.5-14B-Instr`, `Mistral-7B-Instr`, `deepseek-llm-7b-chat`, `gemma-3-12b-it`, `olmo-7b-instr`; 3 seeds each), curiosity and cultural grounding selectively benefit divergent and socially situated tasks while adding noise to convergent epistemic tasks:

| Benchmark | Metric | `Curiosity` (MAS) | `No-Curiosity` (MAS) | Holm $p$-value (`Curiosity`) | `Culture` (MAS) | `No-Culture` (MAS) | `R Single` | `TM Single` |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| `Story Generation` (`1,000`) | `Nov` / `SD` / `LR` | `.647 / .620 / .787` | `.600 / .514 / .729` | $p = 0.150$ (n.s.) | `.647 / .602 / .772` | `.588 / .579 / .774` | `.522 / .507 / .665` | `.526 / .543 / .782` |
| `Hypothesis Gen` (`5,500`) | `PPL` $\downarrow$ / `IA` / `ID` | `185.1 / .595 / .840` | `174.2 / .542 / .790` | **$p < 8 \times 10^{-7}$** | `175.4 / .578 / .830` | `164.9 / .564 / .832` | `236.6 / .559 / .779` | `84.5 / .729 / .808` |
| `Codenames` (`90`) | `BLEU` / `ROUGE-L` | `.062 / .261` | `.046 / .177` | **$p < 0.006$** | `.060 / .253` | `.060 / .243` | `.052 / .220` | `.057 / .259` |
| `CSQA` (`1,221`) | `Acc %` | `73.77±2.7` | `72.81±2.8` | $p = 0.196$ (n.s.) | `73.41±2.7` | `73.77±2.7` | `70.70±2.8` | `66.34±2.9` |
| `StrategyQA` (`1,603`) | `Acc %` | `69.56±2.8` | `70.33±2.8` | $p = 0.196$ (n.s.) | `68.37±2.9` | `70.33±2.8` | `66.68±2.9` | `62.19±3.0` |
| `Novel Concepts` (`32`) | `Acc %` | `34.33±2.9` | `30.21±2.9` | $p = 0.196$ (n.s.) | `32.12±2.9` | `34.33±2.9` | `22.40±2.6` | `31.67±2.9` |
| `Bias Scenarios` (`111`) | `1 - SR %` $\uparrow$ (`SR` $\downarrow$) | `75.36%` (`24.64%`) | `60.46%` (`39.54%`) | **$p < 7 \times 10^{-6}$** | `76.78%` (`23.22%`) | `74.68%` (`25.32%`) | `44.90%` (`55.10%`) | `62.12%` (`37.88%`) |
| `ETHICS` (`14,332`) | `Acc %` | `49.39±3.1` | `48.97±3.1` | $p = 0.196$ (n.s.) | `49.39±3.1` | `48.97±3.1` | `44.62±3.1` | `46.52±3.1` |

### 2. Curiosity Framing Outperforms Generic Questioning and Non-Interacting Ensembles on Bias Reduction

- **Interacting Curiosity vs. Ensembling**: On `Bias Scenarios` (Stereotype Rate `SR` $\downarrow$), interacting curious multi-agent debate lowers `Llama-3-8B-Instr` stereotyping from `55.45%` (Single) and `49.55%` (Non-Interacting Ensemble) to `33.08%` (`Self-Refine`: `40.33%`), and lowers `Qwen-2.5-14B-Instr` from `65.77%` (Single) and `32.38%` (Ensemble) to `27.16%` (`Self-Refine`: `36.04%`).
- **Curiosity vs. Generic Questioning (`Table 19`)**: Prompting agents simply to "ask questions" without curiosity framing (`Generic Question`) causes Stereotype Rate to jump from `24.64%` to `49.42%` (`+24.78` pp worse), `ETHICS` accuracy to drop from `49.39%` to `43.33%` (`-6.06` pp), and Hypothesis Idea Diversity to fall from `0.840` to `0.656` (`-0.184`), whereas `Generic Question` outperforms `Curiosity` on convergent `Novel Concepts` (`41.93%` vs. `34.33%`, `+7.60` pp) and `Codenames` `BLEU` (`0.101` vs. `0.062`).
- **Human and LLM Judge Validation**: Four human annotators (`160` outputs) rated `Curiosity` higher in creative quality (`3.48` vs. `2.93` on a 5-point scale) and coherence (`87.5%` vs. `78.75%`), matching `Claude Sonnet 4.6` evaluations (`r = 0.755` relevance, `r = 0.726` coherence) on `Hypothesis Generation` (`710` outputs: relevance `3.74` vs. `2.84`, coherence `3.86` vs. `2.29`) and `Story Generation` (`300` outputs: relevance `3.98` vs. `2.04`, coherence `2.98` vs. `1.42`).

## Why Not a Skill?

CuriousTogether investigates prompt-level persona and curiosity framing across benchmarks rather than introducing a reusable programmatic workflow or architectural component. Furthermore, 5 of the 8 evaluated benchmarks show non-significant differences after Holm correction (`p >= 0.150`), and cultural/curious framing degrades multi-hop factual reasoning (`StrategyQA`). The actionable decision boundary—when to enable vs. disable divergent curiosity and cultural persona prompts in multi-agent debate—is captured as a rule in `output/rules/multi-agent-coordination.md`.
