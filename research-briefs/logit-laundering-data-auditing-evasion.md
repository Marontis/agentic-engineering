# Logit Laundering: Evading Data-Use Auditing in Large Language Models

> **Source**: [arXiv:2611.09446](https://arxiv.org/abs/2611.09446) — *Logit Laundering: Evading Data-Use Auditing in Large Language Models* (Hu et al., November 2026)
> **Praxis Source ID**: `src:2611-09446v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Per [`output/AGENTS.md`](../AGENTS.md), papers describing adversarial evasion or offensive techniques (`Logit Laundering` enables a non-compliant LLM provider to conceal unauthorized training on watermarked copyrighted corpora during API-based data-use auditing) are captured as research briefs focused on **defensive auditing lessons** rather than packaged as reusable offensive evasion skills.

---

## Threat Model & Why Naive Evasion Fails (`Sections 3–4`)

In **watermark-based data-use auditing**, a data owner embeds traceable signals into copyrighted texts $\mathbb{D}_{\text{wm}}$ before release, and an auditor queries a suspect LLM API (observing output text, tokenizer, and token logits) to test whether $\mathbb{D}_{\text{wm}}$ was used in continual pretraining ($p < \alpha = 0.05$):

1. **Injection-Based Watermarks Are Fragile to Data Preprocessing (`Section 4.1`, `Table 2`)**: Inserting length-`40` random canary strings or global Unicode homoglyphs into `100` paragraphs achieves a `100.00%` hit rate before filtering, but simple sliding-window perplexity filtering (`100`-char window, `GPT-2-XL` $\text{PPL} > 100$) and Unicode-to-ASCII normalization reduce both hit rates to **`0.00%`**.
2. **Data-Level Perturbations on Paraphrase-Based Watermarks Destroy Training Utility (`Section 4.1`, `Table 3`)**: When $\mathbb{D}_{\text{wm}}$ is watermarked via a red-green list LLM (`LLaMA-3.1-8B-Instruct`, green fraction $\gamma = 0.25$, logit bias $\delta = 4.0$, window $w = 1$), character-level (`homoglyph`, `insertion`, `typo`), `paraphrase`, `synonym`, and `translation` attacks severely degrade semantic preservation (`P-SP` drops to `0.570–0.730`) and fluency (`PPL` rises to `36.794–292.106`), while still failing to erase the watermark ($z$-scores remain `3.697–6.503`, $p$-values $7.152\times 10^{-5}$ to $6.324\times 10^{-3} < 0.05$).
3. **Token-Level Decoding Perturbations (`Rank-Swap`) Collapse Reasoning Utility (`Section 4.2`, `Tables 5, 8, 10`)**: Swapping the top-1 token with probability $r = 0.3$ during decoding (`Top-2 Swap (2S)`, `Synonym Swap (SS)`, `Semantic Top-5 Swap (SK)`) leaves likelihood-based (`STAMP`) and green-token (`Radioactive`) audit signals detectable in most settings while causing catastrophic drops on multiple-choice knowledge retention (`73.4%` $\to$ `29.6–38.2%` on `LLaMA-3.2-1B`) and `GSM8K` math reasoning (`0.260–0.680` $\to$ `0.000–0.070`).

---

## Mechanism of `Logit Laundering` (`Section 5`)

To preserve full model weights learned during standard continual pretraining on $\mathbb{D} = \mathbb{D}_{\text{pub}} \cup \mathbb{D}_{\text{wm}}$ while suppressing auditor-visible statistical signals at the API boundary, `Logit Laundering` operates exclusively in the inference-time logit space without knowing the watermark key or detection algorithm:

1. **Plug-and-Play Statistical Bias Estimator ($\Theta_c$)**: Repurposes the first `8` Transformer layers and LM head of the base model (sharing its tokenizer) and trains for `4,000` steps (batch size `10`, mixing ratio $\rho = 0.6$) on a dual objective $\mathcal{L}_c = \mathcal{L}_{\text{fit}} + \eta \mathcal{L}_{\text{flat}}$ ($\eta = 3$):
   - **Distribution Flattening on $\mathbb{D}_{\text{pub}}$ ($\mathcal{L}_{\text{flat}}$)**: Minimizes divergence $D(\mathcal{U} \parallel P_{\theta_c}(\cdot \mid x))$ toward the uniform vocabulary distribution $\mathcal{U}$ so $\Theta_c$ produces near-zero bias on general public prompts.
   - **Local Segment Fitting on $\mathbb{D}_{\text{wm}}$ ($\mathcal{L}_{\text{fit}}$)**: Minimizes cross-entropy on short contiguous local segments $x_{ws}$ of length ratio $\alpha = 0.05$ sampled from $\mathbb{D}_{\text{wm}}$, absorbing local green-token and perplexity biases without memorizing full contexts.
2. **Confidence-Aware Scaling ($\lambda_t$)**: Subtracting a fixed multiple of estimator logits $z_c$ from base logits $z_b$ distorts flat, uncertain next-token distributions. Instead, `Logit Laundering`:
   - Computes safe scaling bounds $[\lambda_{\min}, \lambda_{\max}]$ over top-$K$ dominant tokens such that expected Jensen-Shannon divergence $D_{\text{JS}}(\tilde{p}_b^K \parallel \tilde{p}_{B,\lambda}^K)$ stays within $[\tau_{\min}, \tau_{\max}] = [0.01, 0.1]$.
   - Uses the top-1/top-2 base logit margin $m_t = z_b^{(1)} - z_b^{(2)}$ at step $t$ to scale suppression dynamically ($S = 1$):
     $$\lambda_t = \lambda_{\min} + (\lambda_{\max} - \lambda_{\min}) \cdot \frac{m_t}{m_t + S}, \qquad z_B(\cdot \mid x_{<t}) = z_b(\cdot \mid x_{<t}) - \lambda_t \cdot z_c(\cdot \mid x_{<t}).$$

---

## Quantitative Evaluation (`Section 6`, `Tables 4–11`)

Evaluated under continual pretraining on a mixed corpus of `500` arXiv papers, `1,000` `Pile-CC` documents, `646` `Hacker News` posts, and **`4,959` 512-token watermarked paragraphs from `50` books published in 2025** across `5` foundation models (`LLaMA-3.2-1B-Instruct`, `LLaMA-3.2-3B-Instruct`, `Qwen-2.5-1.5B-Instruct`, `Gemma-2-2B-IT`, `Stable-LM-2-1.6B-Chat`) and `8` auditing variants (`STAMP` with `PPL`, `Min-K`, `Min-K++`, `Lowercase`, `Zlib`; `Radioactive` with `Greedy top-1`, `Top-k=40`, `Nucleus top-p=0.9`):

### 1. Auditing Evasion & Copyrighted Knowledge Retention (`Tables 5, 8`)

Across all `5` models, `Logit Laundering` increases detection $p$-values by **`513×` on average** (pushing every $p_t$ and $p_z$ value far above the $\alpha = 0.05$ infringement threshold, from $10^{-6}\text{–}10^{-3}$ up to `0.4117–0.9999`) while preserving a **`56.8%` average relative improvement** in copyrighted book MCQ accuracy over the un-updated foundation models:

| Model | `STAMP` $p_t$-value (`Non-Evasion` $\to$ `Logit Laundering`) | `STAMP` $t$-stat (`Non-Evasion` $\to$ `LL`) | `Radioactive` $p_z$-value (`Non-Evasion` $\to$ `Logit Laundering`) | `Radioactive` $z$-score (`Non-Evasion` $\to$ `LL`) | Copyright MCQ Acc (`Foundation` / `Non-Evasion` / `Logit Laundering`) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **`LLaMA-3.2-1B-Instruct`** | $1.778\times 10^{-3} \to \mathbf{0.7482}$ | $-5.371 \to +1.132$ | $1.995\times 10^{-4} \to \mathbf{0.9948}$ | $+7.289 \to -5.118$ | `31.8%` / `73.4%` / **`72.8%`** (`+41.0 pp`) |
| **`LLaMA-3.2-3B-Instruct`** | $4.076\times 10^{-3} \to \mathbf{0.8905}$ | $-4.213 \to +2.073$ | $7.526\times 10^{-3} \to \mathbf{0.9914}$ | $+5.654 \to -7.157$ | `64.5%` / `82.9%` / **`82.3%`** (`+17.8 pp`) |
| **`Qwen-2.5-1.5B-Instruct`** | $1.250\times 10^{-5} \to \mathbf{0.4117}$ | $-10.420 \to -0.882$ | $2.965\times 10^{-6} \to \mathbf{0.9999}$ | $+8.853 \to -7.448$ | `71.8%` / `79.7%` / **`80.0%`** (`+8.3 pp`) |
| **`Gemma-2-2B-IT`** | $2.624\times 10^{-3} \to \mathbf{0.7056}$ | $-4.364 \to +0.798$ | $3.220\times 10^{-4} \to \mathbf{0.9074}$ | $+11.551 \to -3.588$ | `56.2%` / `83.6%` / **`83.3%`** (`+27.2 pp`) |
| **`Stable-LM-2-1.6B-Chat`** | $1.990\times 10^{-4} \to \mathbf{0.9645}$ | $-5.564 \to +2.593$ | $5.947\times 10^{-5} \to \mathbf{0.9983}$ | $+12.293 \to -7.687$ | `35.2%` / `59.2%` / **`59.1%`** (`+23.9 pp`) |

- On extended `LLaMA-3.2-1B` auditing variants (`Tables 6–7`), `Logit Laundering` raises `STAMP` $p_t$-values to `0.7482` (`PPL`), `0.6640` (`Min-K`), `0.1221` (`Min-K++`), `0.8886` (`Lowercase`), and `0.1680` (`Zlib`), and raises `Radioactive` $p_z$-values to `0.9948` (`Greedy`), `0.9907` (`Top-k=40`), and `0.9862` (`Nucleus`).

### 2. General Utility & Confidence-Scaling Ablation (`Tables 9–11`)

- **Generation Quality (`Table 9`)**: Compared to `Non-Evasion` (`Fluency-PPL` `6.222`, `MAUVE` `0.178`, `LLM Judge` `83.7`), `Logit Laundering` maintains natural text (`Fluency-PPL` **`5.752`**, `MAUVE` **`0.255`**, `LLM Judge` **`79.9`**), whereas `Rank-Swap (SS)` degrades `Fluency-PPL` to `36.480`, `MAUVE` to `0.055`, and `LLM Judge` to `43.9`.
- **Downstream Benchmarks (`Table 10`)**: Across all `5` models on `ARC-Challenge`, `MMLU`, `TriviaQA`, and `GSM8K`, `Logit Laundering` stays within `0.000–0.040` of `Non-Evasion` (e.g., `LLaMA-3.2-3B` `MMLU` `0.603` vs. `0.611`, `GSM8K` `0.680` vs. `0.680`).
- **Necessity of Confidence Scaling (`Table 11`)**: Replacing adaptive $\lambda_t$ with fixed $\lambda \in \{0.170, 0.365, 0.560\}$ on `LLaMA-3.2-1B` collapses `MAUVE` from **`0.107`** to **`0.018 / 0.016 / 0.018`**; on `Qwen-2.5-1.5B`, fixed $\lambda \in \{0.140, 0.295, 0.450\}$ collapses `MAUVE` from **`0.151`** to **`0.019 / 0.017 / 0.017`**.

---

## Defensive Lessons for Data-Use & Model Auditors (`Section 6.4`)

1. **One-Sided Statistical Tests Are Vulnerable to Active Over-Suppression**: Notice in `Table 5` that `Logit Laundering` drives `Radioactive` $z$-scores from strongly positive (`+5.654` to `+12.293`) to **strongly negative (`-3.588` to `-7.687`)** and flips `STAMP` $t$-statistics from negative (`-4.213` to `-10.420`) to positive (`+0.798` to `+2.593` on `4/5` models). Because standard watermark detectors run one-sided hypothesis tests ($p = 1 - \Phi(z)$, testing only for an *excess* of green tokens or *lower* perplexity on watermarked text), active logit subtraction hides behind $p \approx 0.99$ while leaving a massive **anti-watermark anomaly** in the opposite tail.
2. **Implement the `True-key Placebo Check` (`Section 6.4`)**: Auditors should compare the suspect model's green-token frequency under the **real watermark key** against the mean green-token frequency across **$K = 10$ random placebo keys** on the same prefixes:
   - An unwatermarked clean model exhibits a near-zero **True-key Shift** ($\hat{h}_{\text{real}} - \bar{h}_{\text{placebo}} \approx 0$) because neither the real key nor random keys correlate with its output distribution.
   - A model employing inference-time logit suppression exhibits a **statistically significant negative True-key Shift** ($\hat{h}_{\text{real}} \ll \bar{h}_{\text{placebo}}$) specifically under the true watermark key, flagging suspicious false negatives for forensic auditing of the provider's decoding layer.
3. **Combine Distributional Watermarks with Semantic/Fact-Level Canaries**: Because logit reshaping operates on local surface-token distributions ($\alpha = 0.05$ segment length) while intentionally preserving learned factual associations (`72.8–83.3%` MCQ accuracy), pairing red-green paraphrase watermarks with semantic/fictitious-knowledge canaries (`Cui et al.`) forces an adversary to choose between failing semantic fact audits or destroying the factual utility they sought to acquire.

---

## Related Artifacts

- **Brief**: [`bell-budgeted-watermark-localization.md`](bell-budgeted-watermark-localization.md) — Two-stage watermark localization under FWER/FDR control.
- **Brief**: [`watermarks-without-verification.md`](watermarks-without-verification.md) — Governance and verification gaps in AI text watermarking.
- **Skill**: [`llm-api-relay-integrity-verification`](../skills/llm-api-relay-integrity-verification/SKILL.md) — Auditing inference-layer manipulation and middleman tampering on LLM API outputs.
