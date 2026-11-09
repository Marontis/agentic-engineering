# MPIDetector: Detecting Multi-modal Prompt Injection via LLM-based Reasoning

> **Source**: [arXiv:2610.30202](https://arxiv.org/abs/2610.30202) — Yuchen Yang, Yiming Li, Baoyuan Wu, Pin-Yu Chen, Dacheng Tao (2026)
> **Praxis Source ID**: `src:2610-30202`
> **Category**: Research Brief (Multimodal Prompt Injection Detection & Evaluation)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

MPIDetector is a prompting and benchmark study evaluating whether off-the-shelf Multimodal Large Language Models (MLLMs) can act as zero-training, few-shot In-Context Learning (ICL) security judges for textual and visual prompt injection across 3,902 samples. While its **Visual-Semantic Decoupling** prompt instruction improves detection of obfuscated web-agent injections (`WebInject`) on `Gemini-2.0-Flash`, its performance is highly model-dependent—dropping to **67.00% recall** on `Qwen3-VL-32B-Instruct` and suffering a **25.00% false-positive rate (FPR)** on benign text inputs for both `Gemini-2.0-Flash` and `Qwen3-VL-32B-Instruct`. Because Praxis already maintains dedicated runtime defenses for tool and multimodal injection ([`../skills/covert-tool-injection-defense/SKILL.md`](../skills/covert-tool-injection-defense/SKILL.md), [`../skills/google-adk/references/mcp-multimodal-tool-interception.md`](../skills/google-adk/references/mcp-multimodal-tool-interception.md)), this paper is best captured as a research brief with quantitative evidence for [`../rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

---

## Core Findings

### 1. Cross-Modal Intent-Scrutiny Architecture & Visual-Semantic Decoupling

MPIDetector frames multimodal prompt injection detection as a structured security-audit reasoning task rather than surface token or pixel anomaly classification:

- **Few-Shot ICL Judge**: The detector prompts an MLLM as an "AI Security Researcher" with **4 in-context demonstrations** (2 benign controls illustrating safe emotional or imperative phrasing, and 2 injection attacks illustrating instruction overrides) and requires a structured output containing:
  1. `Verdict`: `Benign`, `Suspicious`, or `Malicious` with a `0–100%` confidence score (both `Suspicious` and `Malicious` are mapped to positive attack detections),
  2. `Summary`: Concise explanation of whether the input attempts to hijack system instructions, and
  3. `Attack Vectors`: Specific textual or visual manipulation mechanisms identified.
- **Visual-Semantic Decoupling (for Obfuscated Environmental Web Injections)**: Standard visual prompts fail when attackers blend low-opacity typography, micro-fonts, or adversarial pixel perturbations ("Green Noise") into complex UI screenshots (`WebInject`). MPIDetector adds a 3-step cross-layer reasoning instruction:
  1. *Visual Rendering Isolation ("Green Noise" Check)*: Scan the raw image for unnatural high-frequency pixel grain, localized color distortion, or semi-transparent overlays independent of the text meaning.
  2. *Semantic Intent Extraction*: Perform OCR and UI layout parsing across all visible text regions, pop-ups, and banners.
  3. *Cross-Layer Consistency Reconciliation*: Flag the input if either visual anomalies accompany imperative commands or rendered UI text contradicts the host application's legitimate workflow.

### 2. Benchmark Composition (3,902 Total Samples)

The evaluation aggregates **3,902 samples** across three evaluation splits (Table I):

- **Textual Domain ($N = 330$)**: **210 malicious** prompts spanning 8 attack categories from WAInjectBench (`EIA_W_EI`, `EIA_WO_EI`, `popup`, `VPI_E_M`, `VPI_web_text`, `VWA_adv_w_EI`, `VWA_adv_wo_EI`, `wasp`) and **120 benign** controls across 4 categories (`comment_issue`, `email_msg`, `img_caption`, `web_text`) and HuggingFace datasets.
- **Standard Visual Domain ($N = 3,072$)**: **2,000 malicious** images across 6 visual attack categories from WAInjectBench (`VWA-Adv`, `EIA`, `Pop-up`, `WASP`, `WebInject`, `VPI`) and **1,072 benign** images (1,000 natural images from `Yoga-82` + 72 benign UI screenshots from HuggingFace `naaakuuul/prompt-injection-classifier`).
- **Obfuscated WebInject Stress-Test ($N = 1,000$)**: **500 malicious** `WebInject` samples featuring stealthy pixel/typographic obfuscation paired with **500 benign** control images sampled from the 1,072 benign pool (making 7 visual attack categories total when `WebInject` is analyzed separately).

### 3. Quantitative Performance Across Models and Baselines

| Domain / Split | Detector / Model | TP | FN | TN | FP | Accuracy | Precision | Recall | FPR |
|:---------------|:-----------------|:---|:---|:---|:---|:---------|:----------|:-------|:----|
| **Textual ($N = 330$)** | `Gemini-2.0-Flash` (MPIDetector) | 210 | 0 | 90 | 30 | **90.91%** | 87.50% | **100.00%** | **25.00%** |
| **Textual ($N = 330$)** | `Qwen3-VL-32B-Instruct` (MPIDetector) | 180 | 30 | 90 | 30 | 81.82% | 85.71% | 85.71% | **25.00%** |
| **Textual ($N = 330$)** | `Doubao-seed-1.6-flash` (MPIDetector) | 150 | 60 | 120 | 0 | 81.82% | **100.00%** | 71.43% | **0.00%** |
| **Textual ($N = 330$)** | GPT-2 Perplexity Filter ($PPL > 150.0$) | — | — | — | — | 25.76% | 5.13% | 0.95% | 30.83% |
| **Textual ($N = 330$)** | DeBERTa-v3 PromptShield (fine-tuned) | — | — | — | — | 60.91% | 96.55% | 40.00% | 2.50% |
| **Visual ($N = 3,072$)** | `Gemini-2.0-Flash` (MPIDetector) | 1978 | 22 | 1072 | 0 | **99.28%** | **100.00%** | **98.91%** | **0.00%** |
| **Visual ($N = 3,072$)** | `Doubao-seed-1.6-flash` (MPIDetector) | 1938 | 62 | 1072 | 0 | 97.98% | **100.00%** | 96.93% | **0.00%** |
| **Visual ($N = 3,072$)** | `Qwen3-VL-32B-Instruct` (MPIDetector) | 1726 | 274 | 1072 | 0 | 91.08% | **100.00%** | 86.30% | **0.00%** |
| **Visual ($N = 3,072$)** | EasyOCR + Rule-Based Keyword Blacklist | — | — | — | — | 92.39% | **100.00%** | 88.31% | **0.00%** |
| **Visual ($N = 3,072$)** | SnapGuard (Laplacian $> 150$, TV $> 30$) | — | — | — | — | 65.10% | 65.10% | **100.00%** | **100.00%** |
| **WebInject ($N = 1,000$)** | `Gemini-2.0-Flash` (+ Visual-Semantic Decoupling) | 499 | 1 | 500 | 0 | **99.80%** | **100.00%** | **99.80%** | **0.00%** |
| **WebInject ($N = 1,000$)** | `Doubao-seed-1.6-flash` (+ Visual-Semantic Decoupling) | 417 | 83 | 500 | 0 | 91.70% | **100.00%** | 83.40% | **0.00%** |
| **WebInject ($N = 1,000$)** | `Qwen3-VL-32B-Instruct` (+ Visual-Semantic Decoupling) | 335 | 165 | 500 | 0 | 83.50% | **100.00%** | 67.00% | **0.00%** |

### 4. Ablation of Visual-Semantic Decoupling & Failure Modes of Baselines

- **Catastrophic Drop Without Visual-Semantic Decoupling on `WebInject`**: When the explicit Visual-Semantic Decoupling instructions are removed (reverting to the standard visual prompt), `WebInject` recall collapses from **99.80% to 66.20%** on `Gemini-2.0-Flash` ($-33.60$ pp), from **83.40% to 11.80%** on `Doubao-seed-1.6-flash` ($-71.60$ pp), and from **67.00% to 10.20%** on `Qwen3-VL-32B-Instruct` ($-56.80$ pp).
- **Why Traditional Baselines Fail on Web-Agent Injections**:
  - *Perplexity Filters*: Coherent natural-language web injections have low perplexity, so GPT-2 perplexity filtering catches only **0.95%** of attacks while flagging **30.83%** of benign technical/conversational text.
  - *High-Frequency Image Statistics (`SnapGuard`)*: Complex modern web UIs naturally exhibit sharp edges and high Laplacian variance ($> 150.0$) and Total Variation ($> 30.0$), causing pixel-variance thresholds to flag **100.00%** of benign screenshots as adversarial.
- **High Textual False-Positive Rate (25.00% FPR)**: Mapping `Suspicious` verdicts to `Malicious` causes `Gemini-2.0-Flash` and `Qwen3-VL-32B-Instruct` to misclassify **30 of 120 (25.00%)** benign textual inputs (such as imperative issue comments or system-like email instructions) as prompt injections.

---

## Relevance to Praxis

- **Multimodal & Web-Agent Input Screening ([`../rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md))**: When screening untrusted screenshots or web-agent DOM/visual observations for indirect prompt injection, neither pixel-variance thresholds (`SnapGuard`, 100% FPR) nor generic MLLM prompts (10.20%–66.20% recall on obfuscated `WebInject`) suffice; prompts must explicitly decouple visual-rendering anomalies from OCR/UI semantic intent, and MLLM judges should not be used as sole blocking gates on text without FPR calibration (25.00% FPR on benign text).
- **Complementary Sandbox Defenses**: Pair perception-level screening with HTTP-layer sandboxing ([`../skills/browser-agent-http-sandbox/SKILL.md`](../skills/browser-agent-http-sandbox/SKILL.md)) and return-anchor tool output sanitization ([`../skills/covert-tool-injection-defense/SKILL.md`](../skills/covert-tool-injection-defense/SKILL.md)).

---

## Key Citations

- **Liu et al. (2024)** — *WAInjectBench: Benchmarking Prompt Injection Attacks on Web Agents* — Primary source of the 8 textual and 6+1 visual web-agent injection attack categories evaluated.
- **ProtectAI (2024)** — *DeBERTa-v3-base-prompt-injection-v2 (PromptShield)* — Supervised transformer baseline that reaches 96.55% precision but only 40.00% recall on agent-oriented contextual injections.
