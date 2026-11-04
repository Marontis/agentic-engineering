# On the Framing Effect of AI Red-Teaming Instructions: Evidence from Prior Exercises and Controlled Simulations

> Source: `src:2611-00412` — "On the Framing Effect of AI Red-Teaming Instructions: Evidence from Prior Exercises and Controlled Simulations" (arXiv:2611.00412, 2026)

## Classification: Research Brief (Contextual Knowledge)

This paper is classified as a **research brief** rather than a standalone skill because it is a methodological survey (228 red-teaming papers) and controlled statistical simulation study ($N=20,812$ primary attacks + $N=24,965$ and $N=15,807$ frontier replications) rather than a single operational procedure. Its findings provide direct quantitative guardrails for `rules/agent-evaluation-quality.md` on how human-authored instructions bias automated red-teaming benchmarks.

---

## Problem & Motivation

Every AI red-teaming exercise—whether conducted by human participants or automated attacker LLMs—begins with human-written instructions defining the scope, risk domain, examples, and rules of engagement. Yet prior literature treats these instructions as neutral scaffolding, rarely reporting or controlling for their wording.

By coding **228 prior red-teaming works** (**38 manual**, **190 automated**), the authors organize the red-teaming instruction design space into **13 dimensions** across three groups:
1. **Prompt Content (4)**: Domain specificity, Instruction length, Examples and demonstrations, Definitions of harm.
2. **Task Context (4)**: Participant expertise, Attack target and surface, Activity guidelines, Role in workflow.
3. **Operational Rules (5)**: Evaluation, Structural constraints, Resource limits, Synchronization, Incentives.

---

## Controlled Simulation Design

To isolate how the four **Prompt Content** dimensions affect Attack Success Rate (ASR), the authors construct a factorial simulation pipeline:
- **45 Instruction Frames ($5 \times 3 \times 3$)**: Derived from **5 real-world templates** (`Anthropic` [169 words, examples=True, harm_defs=False], `Meta BAD` [138 words, examples=False, harm_defs=True], `KAIST` [73 words, Short, examples=False, harm_defs=False], `Gray Swan` [159 words, examples=False, harm_defs=False], `UK AISI / Gray Swan` [373 words, Very Long, examples=True, harm_defs=True]) crossed with **3 risk domains** (`Autonomy harm`, `Physical harm`, `Psychological harm`) and **3 risk granularities** (`Low` = broad domain, `Medium` = subdomain, `High` = subdomain + concrete example such as `"manufacturing ricin"`).
- **Execution**: An attacker LLM (`GLM-4.7-Flash` in the primary study; a proprietary frontier attacker in Suite B) generates 100 baseline attack prompts per frame and refines them via HarmBench `PAIR` against **5 open-weight target models** (`Mistral-7B-Instruct-v0.1`, `Mistral-7B-Instruct-v0.3`, `Mistral-Small-3.2-24B-Instruct-2506`, `GLM-4.7-Flash`, and hybrid-quantized `GLM-5.2`, plus a proprietary frontier target in Suite A). `Gemini 3.8 Flash` ($T=0.0$) scores responses on the 1–10 HarmBench rubric ($\text{Score} \ge 6 \implies \text{success}$), yielding $N=20,812$ valid primary evaluations.

---

## Key Empirical Findings

### 1. All Four Instruction Framing Dimensions Significantly Shift ASR (Tables 2 & 11)
| Framing Dimension | LRT Statistic ($p$-value) | Level / Value | Autonomy ASR | Physical ASR | Psychological ASR | Overall Pooled ASR (95% CI) |
|:------------------|:--------------------------|:--------------|:-------------|:-------------|:------------------|:----------------------------|
| **Wordcount Category** | $\text{LRT} = 150.89$ ($p < 0.001$) | `Low` (Short) | 0.169 (.015) | 0.109 (.014) | **0.243 (.017)** | 0.180 ($\pm 0.009$) |
| | | `Medium` | 0.159 (.016) | 0.133 (.015) | 0.151 (.012) | **0.149 ($\pm 0.008$)** *(lowest)* |
| | | `High` (Very long) | **0.199 (.014)** | **0.157 (.015)** | 0.232 (.022) | **0.192 ($\pm 0.009$)** *(highest)* |
| **Risk Granularity** | $\text{LRT} = 26.36$ ($p < 0.001$) | `Low` (Domain) | **0.192 (.015)** | **0.146 (.014)** | 0.207 (.016) | **0.183 ($\pm 0.009$)** |
| | | `Medium` (Subdomain) | 0.189 (.015) | 0.131 (.014) | 0.160 (.014) | 0.161 ($\pm 0.009$) |
| | | `High` (Subdomain + Example) | 0.153 (.014) | 0.125 (.016) | **0.227 (.017)** | 0.173 ($\pm 0.009$) |
| **Examples Provided** | $\text{LRT} = 11.31$ ($p < 0.001$) | `True` | **0.253 (.016)** | **0.184 (.016)** | **0.207 (.014)** | **0.217 ($\pm 0.009$)** (+50.7% rel.) |
| | | `False` | 0.129 (.010) | 0.104 (.010) | 0.191 (.011) | 0.144 ($\pm 0.006$) |
| **Harm Defs. Provided** | $\text{LRT} = 4.14$ ($p = 0.042$) | `True` | 0.158 (.013) | **0.138 (.013)** | 0.155 (.013) | **0.151 ($\pm 0.008$)** (-19.3% rel.) |
| | | `False` | **0.192 (.012)** | 0.133 (.011) | **0.226 (.012)** | **0.187 ($\pm 0.007$)** |

### 2. Why Opposite Framing Choices Diverge
- **Worked Examples Help Attackers, Harm Definitions Constrain Them**: Providing concrete attack examples raises overall ASR from **0.144 to 0.217** (and from **0.072 to 0.203** on `GLM-5.2` Autonomy), whereas providing explicit normative definitions of harm *reduces* ASR from **0.187 to 0.151** (appears to activate safety-aligned priors or narrow the attacker's creative search space).
- **High Risk Granularity Can Backfire on Guarded Targets**: While open-ended (`Low` granularity) instructions allow the attacker to explore diverse subtle vectors, anchoring the attacker to a canonical high-specificity hazard (`"manufacturing ricin"`) causes `GLM-5.2` Physical ASR to plummet from **0.139 (`Low`) to 0.051 (`Medium`) and 0.053 (`High`)** because target guardrails easily detect canonical keywords.
- **U-Shaped Instruction Length**: Both terse (`Low`, ASR **0.180**) and highly detailed (`High`, ASR **0.192**) instructions outperform medium-length instructions (**0.149**, $p \le 0.0102$).

### 3. Instruction Framing Variance Rivals Target-Model and Risk-Domain Variance (Tables 3, 10, 16–18)
- In the primary GLMM ($N=20,812$), Nakagawa's marginal $R^2$ (fixed instruction-framing effects alone) is **0.062**, accounting for **61.4%** of the total systematic variance explained by the full model (conditional $R^2 = \mathbf{0.101}$).
- Random-intercept standard deviations on the log-odds scale are $\text{SD} = \mathbf{0.273}$ ($e^{\text{SD}} = \mathbf{1.31\times}$ odds multiplier) for `Target Model`, $\text{SD} = \mathbf{0.214}$ ($e^{\text{SD}} = \mathbf{1.24\times}$) for `Risk Domain`, and $\text{SD} = \mathbf{0.144}$ ($e^{\text{SD}} = \mathbf{1.16\times}$) for residual `Template Instruction` identity.
- All four fixed framing effects replicate when adding a proprietary frontier target ($N=24,965$, Table 16) and when using a proprietary frontier attacker ($N=15,807$, Table 18, all four effects $p < 0.001$: Wordcount $\text{LRT}=348.02$, Examples $\text{LRT}=168.64$, Harm defs $\text{LRT}=136.46$, Granularity $\text{LRT}=131.13$).

---

## Why Not a Skill?

The paper analyzes evaluation confounding across red-teaming instruction templates rather than proposing an operational software procedure. Its actionable guidance is an evaluation hygiene rule for `rules/agent-evaluation-quality.md`.

---

## Connections to Praxis

- **Evaluation Quality (`rules/agent-evaluation-quality.md`)**: Establishes that red-teaming ASRs cannot be compared across studies or runs unless the attacker's meta-prompt framing (length, granularity, worked examples, and harm definitions) is held fixed and disclosed alongside the prompts.
- **Self-Improving Red-Teaming (`skills/self-improving-red-team/SKILL.md`)**: Explains why over-specifying canonical harmful examples in red-team seed prompts reduces discovery against guarded frontier models (`0.139` $\to$ `0.053` on `GLM-5.2` Physical harm).
