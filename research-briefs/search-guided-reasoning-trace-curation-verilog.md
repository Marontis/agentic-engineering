# Search-Guided Reasoning Trace Curation for Verilog Generation

> Source: `src:2610-37706` — "Search-Guided Reasoning Trace Curation for Verilog Generation" (arXiv:2610.37706, 2026)

## Classification: Research Brief (Contextual Knowledge)

This paper is classified as a **research brief** rather than a standalone skill because `MCTS-SFT` is an offline training-data curation and LoRA Supervised Fine-Tuning (SFT) methodology for 7B hardware description language (Verilog) models, using a domain-specific 7-field RTL schema (`interface`, `clock_reset`, `state_elements`, `combinational_logic`, `fsm`, `edge_cases`, `implementation_constraints`). However, its controlled separation of **curation-time search state representation** (`Plan-MCTS` vs `Thought-MCTS`) from **training-time supervision serialization** (`explicit plan` vs `rendered NL plan` vs `rollout only`) provides critical empirical evidence for `rules/recursive-improvement.md`.

---

## Problem & Motivation

Distilling free-form chain-of-thought (CoT) reasoning traces from frontier teachers (`DeepSeek-R1`) into smaller coding models (`Qwen2.5-Coder-7B-Instruct`) suffers from two structural flaws:
1. **Unverified Intermediate Decisions**: Standard rejection sampling filters complete responses only by whether the final code passes a testbench, giving no credit assignment to intermediate architectural decisions.
2. **Free-Form Search Bloat**: Running Monte Carlo Tree Search directly over free-form reasoning prefixes (`Thought-MCTS`) discovers high-reward terminal programs during curation (**83.6%** yield), but produces **3.06$\times$ longer, lexically repetitive traces** (3,121 tokens, Distinct-2 = **0.607**) that *degrade* downstream student SFT performance below simple CoT sampling (**51.28%** vs **52.56%** pass@10).

---

## Architecture: `Plan-MCTS` and Plan-Preserving SFT Supervision

`MCTS-SFT` formulates trace curation as a UCT search tree ($M=10$ simulations, $K=3$ child expansions/node) where terminal rollouts $(r, v) \sim \pi_\theta^{\mathrm{rollout}}(\cdot \mid x, p_t)$ are compiled and verified against an executable testbench ($R(v) = N_{\mathrm{pass}}/N_{\mathrm{total}}$, or $\alpha_{\mathrm{NC}} < 0$ if non-compilable) without training a separate process reward model:
1. **Structured Search State (`Plan-MCTS`)**: Instead of accumulating prose prefixes, each search state $p_t$ is a compact 7-field hardware specification (`interface`, `clock_reset`, `state_elements`, `combinational_logic`, `fsm`, `edge_cases`, `implementation_constraints`). Tree branches represent discrete design updates $p_{t+1} = \mathrm{Update}(p_t, \Delta p_t)$.
2. **Plan-Preserving SFT Target Serialization**: When converting curated trajectories $(x, p, r, v)$ into student training pairs, `MCTS-SFT` serializes the explicit structured plan $p$ alongside the rollout reasoning $r$ and final code $v$: $y^{\mathrm{plan}} = \mathrm{Serialize}(p, r, v)$.

---

## Key Empirical Findings

### 1. Free-Form MCTS Hurts Student SFT, Whereas Explicit Structured-Plan Supervision Boosts It by +5.14 pp on Identical Trajectories (Tables 1–3, 10)
In a strictly controlled 1,000-trace study (100 `VeriThoughts` specs $\times$ 10 traces, unified `DeepSeek-R1` teacher for all calls, `Qwen2.5-Coder-7B-Instruct` LoRA-64 student evaluated on `VerilogEval-v1-Human`, $n=10$):

| Curation Strategy & SFT Target | Functional Trace Yield (RQ1) | Mean Verifier Reward | Mean Trace Tokens | Lexical Diversity (Distinct-2) | Student `pass@1` | Student `pass@5` | Student `pass@10` |
|:-------------------------------|:-----------------------------|:---------------------|:------------------|:-------------------------------|:-----------------|:-----------------|:------------------|
| `CoT` (Free-form, Independent) | 731 / 1,000 (73.1%) | 0.571 | 1,021 | 0.789 | 31.22% | 46.91% | 52.56% |
| `Thought-MCTS` (Free-form MCTS) | 836 / 1,000 (83.6%) | 0.754 | **3,121** | **0.607** *(repetitive)* | 27.37% | 46.71% | 51.28% |
| `Summary-MCTS` (Compressed free-form) | — | — | — | — | 29.23% | 46.43% | 51.92% |
| `Plan-CoT` (One-shot structured plan) | 819 / 1,000 (81.9%) | 0.755 | 1,649 | 0.747 | **32.37%** | 50.40% | 57.05% |
| `Plan-RandomTree` (Unguided tree) | 820 / 1,000 (82.0%) | 0.739 | 1,556 | 0.740 | 28.53% | 47.44% | 53.21% |
| `Plan-MCTS` (`rollout only` target) | **842 / 1,000 (84.2%)** | **0.780** | 1,561 | 0.743 | 29.17% | 46.48% | 52.56% |
| `Plan-MCTS` (`+ rendered NL plan`) | **842 / 1,000 (84.2%)** | **0.780** | 1,681 | 0.745 | 30.00% | 47.60% | 55.10% |
| **`Plan-MCTS` (`+ explicit plan`)** | **842 / 1,000 (84.2%)** | **0.780** | 1,759 | 0.748 | 31.50% | **50.80%** | **57.70%** |

Because the three `Plan-MCTS` SFT targets share **identical search trajectories, terminal Verilog programs, and verifier rewards (0.780)**, the **+5.14 pp** `pass@10` gain from `rollout only` (**52.56%**) to `explicit plan` (**57.70%**) and the **+2.60 pp** gain over `rendered NL plan` (**55.10%**) prove that **how intermediate search states are serialized in SFT targets is as important as discovering correct terminal programs**.

### 2. Extended 6,000-Trace Scaling Cuts Student Generation Tokens by ~50% While Improving Accuracy (Tables 4, 5, 12)
- Across 6,000 traces (`DeepSeek-V3` plan expansion + `DeepSeek-R1` rollout, Table 4):
  - **`VerilogEval-v1-Human`**: `Plan-MCTS` reaches **39.5% / 55.7% / 60.4%** (`pass@1/5/10`), beating full-response `CoT` (**36.9% / 52.5% / 57.2%**) by **+2.6 / +3.2 / +3.2 pp**.
  - **`VerilogEval-v2 Code Completion`**: `Plan-MCTS` reaches **43.3% / 57.4% / 62.5%** vs full `CoT` (**41.5% / 54.8% / 58.8%**, **+1.8 / +2.6 / +3.7 pp**) while cutting mean student output tokens by **50.5%** (from **$7,317 \pm 1,757$** to **$3,622 \pm 2,962$**).
  - **`VerilogEval-v2 Spec-to-RTL`**: `Plan-MCTS` reaches **41.4% / 55.9% / 60.6%** vs full `CoT` (**41.2% / 55.6% / 60.3%**) while cutting mean student output tokens by **49.2%** (from **$7,313 \pm 1,715$** to **$3,710 \pm 2,973$**).
- **Multi-Module Transfer (`CVDP-002/003`, 172 tasks, Table 5)**: `Plan-MCTS-SFT` achieves **12.21% (21/172)** overall and **4.82% (4 solved)** on Medium tasks vs **9.30% (16/172)** and **2.41% (2 solved)** for `CoT-SFT`.
- **Scaling to 60,000 Traces (Table 12)**: Scaling MCTS-curated supervision across 6,000 unique prompts from 10k to 60k traces monotonically lifts `pass@1` from **25.6%** (base) and **38.2%** (10k) to **49.0%** (60k, **+23.4 pp** over base) and `pass@10` from **42.6%** to **63.3%**.

---

## Why Not a Skill?

This paper describes an offline SFT training-trace curation methodology tailored to Verilog RTL generation rather than an inference-time agent skill. Its core finding on preserving explicit structured search states during trajectory distillation directly informs `rules/recursive-improvement.md`.

---

## Connections to Praxis

- **Trajectory Distillation & Self-Improvement (`rules/recursive-improvement.md`)**: Shows that curating training trajectories via tree search over free-form text (`Thought-MCTS`) inflates trace length $3.06\times$ and degrades student SFT unless search is conducted over a compact structured plan *and* the explicit plan schema is preserved in the SFT target.
