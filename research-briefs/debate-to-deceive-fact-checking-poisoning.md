# Debate to Deceive: Poisoning LLM's Fact-Checking via Game-Theoretic Multi-Agent Debate

> **Source**: [arXiv:2611.08756](https://arxiv.org/abs/2611.08756) — Huang, Liang, Lei, Ma, & Ojha (2026)
> **Praxis Source ID**: `src:2611-08756v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Per `output/AGENTS.md`, `Debate-to-Deceive (D2D)` is an offensive black-box knowledge-poisoning framework designed to flip automated LLM fact-checking verdicts (`SUPPORT` $\leftrightarrow$ `REFUTE`) by injecting rhetorically optimized adversarial evidence passages (the authors themselves withhold prompt templates and operational scripts for dual-use safety). Rather than packaging an offensive poisoning generator as a skill, this brief documents the game-theoretic mechanism, exact vulnerability benchmarks across `FEVER`, `HealthVer`, `CLIMATE-FEVER`, and `SciFact`, and the defensive implications for RAG and multi-agent verification pipelines.

---

## Core Mechanism: Decoupling Game-Theoretic Rhetorical Strategy from Passage Generation

Existing knowledge-poisoning and prompt-injection attacks against RAG and fact-checking systems face a structural trade-off:
- **Gradient-based suffix attacks (`GCG`, `JudgeDeceiver`)** emit high-perplexity token sequences or require heavy white-box/optimization overhead (`495–797 s/sample`), making them slow and brittle.
- **Template-based genetic attacks (`AutoDAN`)** rely on fixed structural templates that achieve `100%` Attack Success Rate (ASR) without defenses but collapse to **0.0% ASR** under `Known-answer` detection across all models.
- **Single-agent self-reflection attacks (`ADMIT`)** suffer from early confirmation bias and collapse to **0.0%–1.5% ASR** under `LLM-based` judge detection.

**Debate-to-Deceive (D2D)** overcomes confirmation bias and template predictability by casting adversarial evidence generation as a **four-phase human debate** (adapted from the Singapore debate format: *Foundational* definitions/facts $\rightarrow$ *Associative* arguments/counterarguments $\rightarrow$ *Core* novel rebuttals $\rightarrow$ *Conclusive* synthesis) between a true-label agent $A_L$ and a target-label agent $A_{L'}$, factored into two hierarchical layers:

1. **Strategic Layer (Evolutionary Game Over Rhetorical Modes)**:
   - At each debate phase $t \in \{1, \dots, T\}$, agents select from a compact 3-strategy rhetorical simplex $\mathbf{S} = \{S_{\text{Logos}}, S_{\text{Pathos}}, S_{\text{Ethos}}\}$:
     - **Logos ($S_1$)**: Formal deductive logic and analytical rigor.
     - **Pathos ($S_2$)**: Emotional rhetoric and narrative framing.
     - **Ethos ($S_3$)**: Appeals to institutional authority and credible source citations.
   - Competitive interactions follow a skew-symmetric zero-sum cyclic payoff matrix $\mathbf{B} = -\mathbf{B}^{\top}$ (parameterized by $\alpha=1, \beta=2, \gamma=2$) where no pure strategy dominates.
   - Each agent combines the expected game-matrix payoff $r_{\text{matrix}}(s_t, S_{j,t}^i)$ (over its belief distribution $\mathcal{P}(S_{k,t}^{-i} \mid D)$ of the opponent's rhetorical stance) with a real-time execution quality reward $r_{\text{quality}} = \lambda_q r_{\text{score}} - \lambda_t c_{\text{time}} - \lambda_e c_{\text{econ}}$ scored by a judge LLM $A_J$.
   - Policies update via **strategy-averaged temporal-difference (TD) replicator dynamics**:
     $$\pi_{t+1}^i(S_k \mid s_t) = \frac{1}{Z_t^i}\,\pi_t^i(S_k \mid s_t)\exp\!\big(\eta^i \bar{\delta}^i(s_t, S_k)\big), \qquad \bar{\delta}^i(s_t, S_k) = \bar{Q}^i(s_t, S_k) - \bar{V}^i(s_t)$$
   - As proved in Proposition 1 & 2 (Appendix B.1), the learned policy does not collapse to a static equilibrium $\mathbf{w}^*$; instead, it follows closed non-stationary periodic orbits around the quality-shifted rest point $\hat{x}(q)$, producing claim-dependent, temporally correlated rhetorical mixes (`56%` of D2D claims fall outside the $80\%$ $\mathbf{w}^*$ contour, with a `0.43` strategy-repeat transition probability vs. `0.34–0.38` for i.i.d. controls).
2. **Generation Layer + Stance Gate**:
   - Conditioned on the selected rhetorical stance $S_{j,t}^{L'}$ and the accumulated debate pool $D$, the target-side agent generates a fluent closing passage $R_T^{L'}$.
   - Because aligned LLMs frequently drift back toward arguing the ground-truth label $L$ during synthesis, D2D enforces an explicit **Stance Gate** (up to $U=2$ repair attempts and $C_b=2$ critic rewrite rounds) to verify that $R_T^{L'}$ genuinely argues for the flipped verdict $L'$ before injecting it into the victim fact-checker $A_G$.

---

## Key Empirical Results

### 1. Scaling to `Qwen3-32B` Across Four Fact-Checking Domains (1,600 Attacks)

When `Qwen3-32B` serves simultaneously as debater, judge ($A_J$), and target fact-checker ($A_G$) across 200 attacks per cell (100 `SUPPORT` and 100 `REFUTE` claims per dataset), D2D achieves near-ceiling verdict flipping and completely evades `Known-answer` detection (which blocked **0 of 800** defended attacks):

| Benchmark Dataset | Domain | `No Defense` ASR % (95% Wilson CI) | `Known-Answer Defense` ASR % (95% Wilson CI) |
|:---|:---|:---:|:---:|
| **`FEVER`** | General factual claims | **98.5%** `[95.7, 99.5]` | **96.5%** `[93.0, 98.3]` |
| **`HealthVer`** | Public health / COVID-19 | **97.0%** `[93.6, 98.6]` | **97.5%** `[94.3, 98.9]` |
| **`CLIMATE-FEVER`** | Climate science claims | **99.5%** `[97.2, 99.9]` | **99.5%** `[97.2, 99.9]` |
| **`SciFact`** | Biomedical / scientific | **100.0%** `[98.1, 100.0]` | **99.5%** `[97.2, 99.9]` |
| **4-Dataset Average** | — | **98.8%** | **98.3%** |

- **Bare-Claim Audit**: Auditing 487 trials on bare claims without injected passages showed $A_G$ already returned the flipped label unprompted in `23.5%` (`95% CI [19.0, 28.2]`) of cases; excluding those and recomputing over the **1,224 trials** where the passage was required to flip the verdict leaves D2D's true causal ASR at **99.0%** (`95% CI [98.4, 99.5]`).
- **Why Residual Attacks Fail**: Out of 1,600 total trials, only 13 passages failed to flip $A_G$, and 11 failed because the aligned generator refused to argue a blatant health falsehood during stance gating—showing that internal model alignment on hard medical facts, not external prompt-injection detection, was the only active bound.

### 2. Comparison Against 4 Attack Baselines and 6 Defense Mechanisms (Table 3 & Table 9)

Across `Llama3-8B`, `Gemma2-9B`, `Llama3.1-8B`, and `Mistral-7B` evaluated under 6 defense conditions (`None`, `Instructional`, `Known-answer`, `LLM-based` self-examination, `Response-based` backtranslation, and `Paraphrasing`):

| Target Model | Defense | `AutoDAN` ASR | `Open-Prompt-Inj.` ASR | `JudgeDeceiver` ASR | `ADMIT` ASR | **`D2D` ASR** |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **`Llama3-8B`** | `None` / `Instr.` / `Known` / `LLM` / `Resp.` / `Para.` | 100.0 / 100.0 / **0.0** / 100.0 / 99.8 / 99.8 | 63.7 / 32.9 / 31.6 / **0.0** / 61.3 / 36.2 | 13.0 / 14.5 / 18.5 / 29.0 / 18.0 / 23.5 | 82.5 / 20.0 / 55.3 / **0.0** / 53.8 / 37.8 | **100.0 / 100.0 / 94.8 / 100.0 / 100.0 / 100.0** |
| **`Gemma2-9B`** | `None` / `Instr.` / `Known` / `LLM` / `Resp.` / `Para.` | 100.0 / 100.0 / **0.0** / 25.8 / 100.0 / 100.0 | 69.4 / 57.8 / 38.8 / **0.0** / 71.5 / 38.4 | 1.0 / 1.0 / 1.0 / 0.0 / 1.0 / 1.0 | 84.0 / 34.3 / 36.3 / **1.5** / 73.8 / 32.5 | **100.0 / 100.0 / 97.0 / 100.0 / 100.0 / 100.0** |
| **`Llama3.1-8B`** | `None` / `Instr.` / `Known` / `LLM` / `Resp.` / `Para.` | 100.0 / 100.0 / **0.0** / 66.0 / 100.0 / 100.0 | 44.7 / 12.1 / 24.4 / **0.0** / 38.6 / 31.8 | 83.0 / 68.0 / 80.0 / 74.5 / 77.5 / 80.0 | 85.0 / 44.0 / 41.5 / **0.3** / 54.5 / 34.5 | **88.0 / 100.0 / 93.5 / 100.0 / 100.0 / 100.0** |
| **`Mistral-7B`** | `None` / `Instr.` / `Known` / `LLM` / `Resp.` / `Para.` | 100.0 / 100.0 / **0.0** / 12.5 / 100.0 / 100.0 | 52.3 / 43.2 / 27.2 / **0.0** / 49.6 / 37.7 | 64.0 / 84.5 / 87.0 / 90.0 / 89.0 / 90.5 | 80.8 / 80.5 / 82.3 / **0.0** / 78.8 / 78.8 | **100.0 / 100.0 / 84.5 / 100.0 / 100.0 / 100.0** |

- **Per-Dataset No-Defense Breakdown (Table 9)**: On `Gemma2:9B`, `Llama3:8B`, and `Mistral:7B`, D2D reaches **100.0% ASR** on all four datasets (`FEVER`, `HealthVer`, `CLIMATE-FEVER`, `SciFact`), averaging `57.33 s` (`1,220` tokens), `63.46 s` (`1,313` tokens), and `138.15 s` (`1,338` tokens) per sample respectively. On `Llama3.1:8B`, D2D achieves `84.0%` (`FEVER`), `89.0%` (`HealthVer`), `85.0%` (`CLIMATE-FEVER`), and `94.0%` (`SciFact`), averaging **88.0% ASR** (`114.48 s`, `2,189` tokens).
- **Order-of-Magnitude Speedup Over Optimization Baselines (Table 10)**: On `Llama3:8B`, D2D takes `50.51–63.46 s/sample` across defenses, whereas `JudgeDeceiver` takes `495.26–796.99 s/sample` ($8\times\text{–}15\times$ slower) and `ADMIT` takes `77.13–283.60 s/sample` ($1.4\times\text{–}5\times$ slower).
- **Debate-Phase Ablation Under `Known-Answer` Defense (Table 8)**: Removing *any single phase* of the four-phase debate (`Foundation`, `Associative`, `Core`, or `Summary`) causes D2D's ASR under `Known-answer` detection to collapse from `84.5%–98.3%` down to **0.0% ASR** (while token usage balloons from `~1,300` to `25,316–28,609` tokens), demonstrating that full four-stage dialectical synthesis is what eliminates the surface artifacts that `Known-answer` detectors catch.

---

## Defensive Takeaways for Fact-Checking and RAG Systems

1. **Prompt-Injection Detectors Cannot Catch Dialectically Synthesized Evidence**: Standard input/output defenses (`Instructional`, `Paraphrasing`, `Known-answer` canary probes, `LLM-based` self-examination, and `Response-based` backtranslation) look for directive overrides, template signatures, or anomalous perplexity. Because D2D optimizes argumentative quality (`Logos`, `Pathos`, `Ethos`) rather than instruction-override tokens, it achieves **98.3%–100% ASR** right through these filters.
2. **Never Feed Single-Sided Unverified Passages to an LLM Judge**: As the authors note in Section 4.2, D2D succeeds because the victim fact-checker $A_G$ ingests the adversarial passage *without a matching rebuttal or independent provenance verification*. Defending RAG fact-checkers requires **cryptographic or domain-governed source provenance** and **bidirectional counter-evidence retrieval** before verdict synthesis.
3. **Audit Rhetorical Framing (`Pathos` / Fabricated `Ethos`) Separately from Entailment**: Fact-checking pipelines should decompose retrieved passages into atomic factual claims and verify source existence independently rather than evaluating holistic persuasive summaries where emotional narrative (`Pathos`) and fabricated institutional citations (`Ethos`) outweigh ground-truth priors.

## Cross-References

- [`rag-hallucination-repair`](../skills/rag-hallucination-repair/SKILL.md) — Claim-level decomposition and source verification for RAG outputs
- [`rag-evidence-triage`](../skills/rag-evidence-triage/SKILL.md) — Classifying retrieved evidence sufficiency and conflict before answering
- [`evidence-gated-adversarial-deliberation`](../skills/evidence-gated-adversarial-deliberation/SKILL.md) — Gating multi-agent deliberation on verified external evidence
- [`debate-consensus-memory-calibration`](../skills/debate-consensus-memory-calibration/SKILL.md) — Calibrating multi-agent debate against persuasive majority skew
- [`governed-knowledge-graph`](../skills/governed-knowledge-graph/SKILL.md) — Provenance tracking and admission review for knowledge stores
- [`rules/adk-security-and-evaluation.md`](../rules/adk-security-and-evaluation.md) — Security and evaluation rules for RAG and multi-agent systems
- [`rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md) — Rules for multi-agent debate and verification architectures
