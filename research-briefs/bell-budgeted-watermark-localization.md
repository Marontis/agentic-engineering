# Query-Efficient Scan-and-Search Watermark Localization (BELL)

> **Source**: [arXiv:2611.02030](https://arxiv.org/abs/2611.02030) — Liyuan Wang, Xinsong Ma, Ziye Ma (City University of Hong Kong), published 2026-11-01. Praxis ID: `src:2611-02030v1`.

## Summary

Localizing LLM-watermarked spans inside mixed human/machine documents typically requires running a watermark detector densely over every token in the document (`WinMax`, `WaterSeeker`, `AOL`), which is expensive when watermarked segments are sparse or detector calls require model forward passes. Wang et al. introduce **BELL** (**B**udgeted **E**-evidence **L**ocalization for **L**LM Watermarks), a statistical localization framework that operates under a strict token-query budget $B \le N$ while providing a finite-sample, distribution-free bound on the **token-weighted False Discovery Rate ($\text{FDR}_L \le \alpha$)**.

BELL separates localization into three layers:

1. **Watermark-Agnostic Local E-Value Adapters ($\mathcal{A}_W$)**: Maps each queried token's raw detector statistic $Z_{x_{a_t}}$ into a sequentially valid local e-value ($\mathbb{E}[e_t \mid \mathcal{F}_{t-1}, H_{j_t, 0}] \le 1$) via likelihood-ratio (`KGW`, `Hu Unbiased`) or moment-generating-function (`SynthID-style`, `Gumbel`) constructions, and accumulates block-level evidence multiplicatively ($E_j(B) = \prod_{t \in \mathcal{T}_j(B)} e_t$). For composite block nulls ($H_{j,0}: \theta_j \le \theta_0$ with $\theta_0 > 0$), finite-population hypergeometric likelihood-ratio and MGF normalizers preserve exact block-level validity.
2. **Four-Mechanism Adaptive Query Allocation**: Allocates the $B$ token queries across $m$ variable-length blocks using clipped log-evidence surrogates $Y_s = \operatorname{clip}(\log(e_s \vee \epsilon), -C_-, C_+)$ by combining: (a) **Broad Coverage** ($b_j = \min\{L_j, \max\{b_{\min}, \lceil c_{\text{cov}} L_j^\beta \rceil\}\}$ plus periodic forced-coverage rounds $\mathcal{T}_{\text{cov}}$ every 25 queries), (b) **UCB Optimistic Exploration** $U_j(t)$, (c) **Neighborhood Expansion** $\eta V_j(t)$ from adjacent blocks $j \pm 1$, and (d) **Near-Confirmation Focusing** ($\widehat{h}_j(t) \le H = 64$), which prioritizes blocks within $H$ optimistic queries of crossing the planning rejection threshold $\tau_{\text{plan}} = \log(N / (\alpha C_{\text{plan}}))$.
3. **Token-Weighted e-BH Procedure**: Orders block e-values $E_{(1)}(B) \ge \dots \ge E_{(m)}(B)$ with cumulative token mass $C_i = \sum_{\ell=1}^i L_{(\ell)}$ and rejects blocks $1 \dots i^*_{\text{TEBH}}$ where $i^*_{\text{TEBH}} = \max\{i \in [m] : E_{(i)}(B) \ge \frac{N}{\alpha C_i}\}$. Because the proof relies only on $\mathbb{E}[E_j(B) \mid H_{j,0}] \le 1$, $\text{FDR}_L \le \alpha$ holds under **arbitrary dependence** across blocks and adaptive query rounds.

## Key Quantitative Findings

- **65%–70% Query Budget Reduction at High Recall**:
  - Across `Qwen2.5-7B-Instruct` and `Mistral-7B-Instruct-v0.3` on `C4` and `WikiText-103` ($N = 4,096$ tokens, $m = 40$ blocks, 5 watermarked spans totaling $800\text{--}1,200$ tokens), reaching **80% token recall** under $\text{FDR}_L \le 0.05$ requires querying only **`12%–15%`** of tokens with `BELL`, vs **`37%–46%`** for `WinMax`, **`41%–52%`** for `WaterSeeker`, and **`43%–54%`** for `AOL`.
  - Reaching **90% token recall** requires querying only **`20%–24%`** of tokens with `BELL`, compared with **`79%–93%`** for `WinMax`, `WaterSeeker`, and `AOL` (e.g., `23%` vs `~90%` on `Mistral-7B` + `WikiText-103` with `Hu Unbiased`, a **`67 percentage point` query reduction**).
- **Localization Accuracy at Fixed $B/N = 20\%$ Budget**:
  - On `Qwen2.5-7B-Instruct` + `C4` (Table 1), `BELL` averages **`94.8%` Precision, `88.7%` Recall, `91.6%` F1, and `84.6%` IoU** across all 4 watermark families, beating the best baseline (`WinMax`) by **`+8.9%` Precision, `+20.4%` Recall, `+15.6%` F1, and `+23.2%` IoU**.
  - Similar gains hold across `Qwen2.5-7B` + `WikiText-103` (`90.4%–91.7%` F1 vs `70.6%–77.6%` for `WinMax`), `Mistral-7B` + `C4` (`91.7%–93.1%` F1 vs `75.3%–78.8%`), and `Mistral-7B` + `WikiText-103` (`91.0%–92.3%` F1 vs `73.1%–78.2%`).
- **Finite-Sample $\text{FDR}_L$ Guarantee Verified Empirically**:
  - Across all `320` test conditions (`4` algorithms $\times$ `4` watermark families $\times$ `4` model–dataset pairs $\times$ `5` query budgets $5\%\text{--}50\%$), `BELL`'s empirical $\text{FDR}_L$ averages **`1.36%–1.68%`** and never exceeds **`2.09%`**, well below the prescribed $\alpha = 5.0\%$ bound.
- **Ablation of the 4 Allocation Mechanisms ($B/N = 20\%$, `Qwen2.5-7B` + `C4`)**:
  - Removing **Coverage** causes the largest drop in Recall (`-9.4%` avg, e.g., `87.9%` $\to$ `77.6%` on `Hu Unbiased`) and IoU (`-9.0%` avg), proving that premature exploitation creates document blind spots.
  - Removing **Neighborhood Expansion** causes the second-largest drop in Recall (`-6.8%` avg) and IoU (`-6.3%` avg).
  - Removing **Near-Confirmation** causes the largest drop in per-query **Evidence Gain (`EG`)** (from `32.8% / 18.1% / 23.3% / 22.4%` down to `26.9% / 14.9% / 19.2% / 18.4%`), confirming its role in converting borderline blocks into terminal rejections without wasting queries on already-decided blocks.

## Why Not a Skill?

BELL is a domain-specific statistical forensics algorithm for localizing cryptographic/statistical LLM watermarks (`KGW`, `Hu Unbiased`, `SynthID`, `Gumbel`) rather than a general-purpose agent or harness subtask transferable across software engineering projects. Its methodological principle for budgeted multi-block auditing—separating heuristic bandit allocation from exact e-value / e-BH terminal testing—is captured as a rule in `output/rules/agent-evaluation-quality.md`.
