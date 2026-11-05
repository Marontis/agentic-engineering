# Red-Teaming Large Language Models in Low-Resource African Languages: A Case Study of Yoruba and Nigerian Pidgin

> **Source**: [arXiv:2610.39590](https://arxiv.org/abs/2610.39590) — Paula Chikaodinaka Anyanwu et al. (AIMS Cameroon, Brown University, CWI, University of Pretoria, University of Hamburg, Bayero University Kano, Imperial College London, 2026-10-29)  
> **Praxis ID**: `src:2610-39590`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Core Contribution

Evaluates the cross-lingual safety alignment of `6` LLMs (`Llama 3.1 8B`, `Llama 3.3 70B`, `Qwen3 32B`, `Gemini 2.0 Flash`, `GPT-4o Mini`, `Aya 101`) across **`1,200` explicit single-turn adversarial prompts** in `English`, `Yoruba`, and `Nigerian Pidgin` spanning `4` Nigeria-localized harm categories (`Hate/abusive language`, `Harmful instructions`, `Political manipulation`, `Cultural stereotypes`). Using double-blind native-speaker annotation with third-party adjudication (`2,160` scored responses, Cohen's $\kappa \in [0.64, 1.00]$), the study demonstrates two critical phenomena:
1. **English safety alignment fails to transfer when comprehension holds**: Models that comprehend the target language suffer sharp drops in Refusal Rate (`RR`) and spikes in Attack Success Rate (`ASR`). `GPT-4o Mini`'s refusal rate collapses from `0.47` in English to `0.01` in Yoruba while its `ASR` jumps from `0.18` to `0.41` ($\text{CLSG} = +0.23$); `Llama 3.3 70B` and `Qwen3 32B` both exhibit $\text{CLSG} = +0.15$ in Nigerian Pidgin.
2. **Low-resource comprehension failure masquerades as safety**: Models with negative Cross-Lingual Safety Gaps in Yoruba (`Aya 101` $\text{CLSG} = -0.35$, `Llama 3.1 8B` $\text{CLSG} = -0.23$, `Qwen3 32B` $\text{CLSG} = -0.12$) refused `0%`–`1%` of Yoruba prompts (`RR = 0.00`–`0.01`). Their low measured `ASR` (`0.01`–`0.25`) is entirely an artifact of **comprehension collapse** (`CR = 0.08` for `Qwen3 32B` and `Llama 3.1 8B`; `CR = 0.28` for `Aya 101`), where models fall into degenerated prompt-repetition or greeting-phrase loops rather than recognizing harm.

---

## Experimental Scope & Methodology

- **Benchmark (`1,200` prompts)**: `400` English prompts (`172` [`43%`] adapted from `Do-Not-Answer`, `HARMFULQA`, `AdvBench`, `HarmBench` and localized to Nigerian contexts; `228` [`57%`] newly authored across `4` categories $\times$ `100` prompts), translated into Yoruba (Google Translate + native linguist post-editing) and Nigerian Pidgin (native-speaker translation from scratch).
- **Evaluation Protocol**: Zero-shot single-turn generation at $T=0$ across `6` models. A `30%` stratified sample (`2,160` responses, `720`/language) was independently scored by `2` native speakers per language on `Refused`, `Harmful`, `Helpful`, and `Comprehended`, with `341` disagreements resolved by third-party adjudication.
- **Metrics**: Refusal Rate (`RR`), Attack Success Rate ($\text{ASR} = N_{\text{harmful}}/N_{\text{total}}$), Harmful Content Rate conditional on non-refusal ($\text{HCR} = N_{\text{harmful}}/(N_{\text{total}} - N_{\text{refused}})$), Helpfulness Rate (`HR`), Comprehension Rate (`CR`), and Cross-Lingual Safety Gap ($\text{CLSG} = \text{ASR}_{\text{lang}} - \text{ASR}_{\text{eng}}$).

---

## Key Quantitative Findings

### 1. Per-Model Safety and Comprehension Matrix (`Table 2`)

| Model | Language | Refusal (`RR`) | Attack Success (`ASR`) | Conditional Harm (`HCR`) | Helpfulness (`HR`) | Comprehension (`CR`) | `CLSG` ($\text{ASR}_{\text{lang}} - \text{ASR}_{\text{eng}}$) |
|:------|:--------:|:--------------:|:----------------------:|:------------------------:|:------------------:|:--------------------:|:-------------------------------------------------------------:|
| **Aya-101** | `Eng` / `Yor` / `Pid` | `0.05` / `0.00` / `0.04` | `0.60` / `0.25` / `0.48` | `0.63` / `0.25` / `0.50` | `0.52` / `0.22` / `0.43` | `0.68` / `0.28` / `0.52` | `—` / `-0.35` / `-0.12` |
| **Gemini-2.0 Flash** | `Eng` / `Yor` / `Pid` | `0.69` / `0.55` / `0.67` | `0.13` / `0.06` / `0.12` | `0.41` / `0.13` / `0.35` | `0.48` / `0.32` / `0.29` | `0.98` / `0.92` / `0.98` | `—` / `-0.07` / `-0.01` |
| **GPT-4o-mini** | `Eng` / `Yor` / `Pid` | `0.47` / `0.01` / `0.37` | `0.18` / `0.41` / `0.23` | `0.34` / `0.41` / `0.36` | `0.33` / `0.57` / `0.39` | `0.50` / `0.72` / `0.55` | `—` / **`+0.23`** / `+0.05` |
| **Llama-3.3-70B** | `Eng` / `Yor` / `Pid` | `0.38` / `0.00` / `0.36` | `0.16` / `0.31` / `0.31` | `0.26` / `0.31` / `0.48` | `0.36` / `0.20` / `0.50` | `0.74` / `0.31` / `0.68` | `—` / **`+0.15`** / **`+0.15`** |
| **Llama-3.1-8B** | `Eng` / `Yor` / `Pid` | `0.21` / `0.00` / `0.08` | `0.34` / `0.11` / `0.46` | `0.43` / `0.11` / `0.50` | `0.43` / `0.03` / `0.39` | `0.82` / `0.08` / `0.50` | `—` / `-0.23` / **`+0.12`** |
| **Qwen3-32B** | `Eng` / `Yor` / `Pid` | `0.34` / `0.01` / `0.27` | `0.13` / `0.01` / `0.28` | `0.20` / `0.01` / `0.39` | `0.34` / `0.05` / `0.69` | `0.99` / `0.08` / `0.87` | `—` / `-0.12` / **`+0.15`** |

### 2. Harm Category Vulnerability (`Table 6`, Aggregated Across 6 Models)

- **Cultural stereotypes & discrimination** is the hardest category for filters to catch in Nigerian Pidgin (`ASR = 0.44`, `RR = 0.09`, `HCR = 0.49`, `HR = 0.71`, `CR = 0.86`), compared to `ASR = 0.26` (`RR = 0.18`) in English and `ASR = 0.26` (`RR = 0.04`, `CR = 0.50`) in Yoruba.
- **Harmful instructions** draws the highest refusal rate in English and Pidgin (`RR = 0.52` in both), yet still yields `ASR = 0.27` and conditional harm `HCR = 0.55` whenever the model fails to refuse.
- **Political manipulation** refusal drops from `0.40` in English (`ASR = 0.29`, `HCR = 0.48`) to `0.32` in Pidgin (`ASR = 0.27`, `HCR = 0.40`) and `0.12` in Yoruba (`ASR = 0.17`, `CR = 0.38`).

### 3. Correlation Evidence on Comprehension Confounding (`Appendix E`)

- Refusal Rate (`RR`) strongly predicts lower `ASR` in English ($r = -0.84$) and Pidgin ($r = -0.97$), but the correlation breaks down in Yoruba ($r = -0.41$).
- Comprehension Rate (`CR`) strongly drives Helpfulness Rate (`HR`) in Yoruba ($r = 0.81$, vs $r = 0.20$ in English and $r = 0.15$ in Pidgin), and correlates negatively with `ASR` in Pidgin ($r = -0.76$) but positively in Yoruba ($r = +0.25$) — proving that low `ASR` in Yoruba is driven by inability to understand the prompt rather than safety refusal.

---

## Why Not a Skill?

This paper presents a benchmark dataset and human-evaluation study across `6` LLMs rather than an algorithmic agent procedure. Its methodological requirement — always pair cross-lingual `ASR` and `CLSG` metrics with explicit Comprehension Rate (`CR`) and conditional Harmful Content Rate (`HCR`) measurements — directly informs evaluation design in `output/rules/agent-evaluation-quality.md`.
