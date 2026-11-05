# Erase the Injected Region: Multimodal Prompt-Injection Defense with On-Policy Self-Distillation

> **Source**: [arXiv:2610.41307](https://arxiv.org/abs/2610.41307) — Shuo Hong, Jiaxin Ma, Xidi Cai, Qianli Ma (South China University of Technology, 2026-10-30)  
> **Praxis ID**: `src:2610-41307`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Core Contribution

Multimodal Large Language Models (MLLMs) are vulnerable to **indirect multimodal prompt injection**, where adversarial instructions are embedded inside images (visual text patches), audio clips (concatenated or `0` dB SNR overlaid speech), or video frames. Existing training-time defenses (`ARGUS`, `Meta-SecAlign`, `GRPO`) teach the model *what output to prefer or refuse*, but leave the model's predictive distribution heavily dependent on the injected region — causing severe utility loss on benign tasks and catastrophic false-positive refusals out of distribution.

**ERASE** reformulates multimodal prompt-injection defense as **injected-region invariance** via **teacher-first on-policy self-distillation**:
1. **In-Place Erased Teacher View ($x^{\text{erase}}$)**: During training, a frozen copy of the base MLLM reads an *in-place erased view* of the input where only the injected region is masked (a white patch over the image injection, zero-amplitude silence over the injected audio segment, or black frames + silence over the injected video segment). Unlike an unmodified clean input $x^{\text{clean}}$ (`SecOPD`), $x^{\text{erase}}$ contains the exact same non-injected evidence available to the student.
2. **On-Policy Full-Vocabulary KL Distillation**: The student generates an on-policy trajectory $y \sim p_S(\cdot | x^{\text{inj}}, u)$ conditioned on the injected input $x^{\text{inj}}$ and trusted user prompt $u$, and minimizes token-level forward KL divergence from the frozen teacher's full next-token distribution $p_T(\cdot | x^{\text{erase}}, u, y_{<t})$.

---

## Experimental Scope & Methodology

- **Models**: `Qwen2.5-Omni-3B` and `Qwen2.5-Omni-7B` fine-tuned with LoRA ($r=128$, `128` grad accumulation steps, $2\times$ A800 GPUs).
- **In-Domain Benchmarks (`1,000` val / `1,000` test per modality)**:
  - **Image**: `VTQA` (`10,312` train) with visual text patch injections.
  - **Audio**: `Clotho-AQA` (`8,108` train) with appended and `0` dB overlaid speech injections.
  - **Video**: `MSR-VTT` (`18,539` train) with audio-visual segment injections.
  - **Diverse-test**: `1,000` test samples per modality across `75` `BIPIA` attack instructions (`15` categories), judged by `Qwen3-30B-A3B-Instruct-2507`.
- **7 Out-of-Distribution (`OOD`) Benchmarks**: `GSM8K`, `MathVista`, `MMMU`, `Omni-Bench`, `OCRBench`, `MSVD-QA` (`1,000` items), and `LibriSpeech` (`test-clean` and `test-other` WER).
- **Baselines (`8`)**: `No Defense`, `System Prompt`, `Ignore Prompt`, `Noise`, `ARGUS`, `Meta-SecAlign`, `GRPO`, and `SecOPD`.

---

## Key Quantitative Findings

### 1. In-Domain Security and Utility Recovery (`Table 1`)

| Model & Method | Audio `UIA_c` / `UIA_i` | Audio `AIA` / `AIFR` | Image `UIA_c` / `UIA_i` | Image `AIA` / `AIFR` | Video `UIA_c` / `UIA_i` | Video `AIA` / `AIFR` |
|:---------------|:-----------------------:|:--------------------:|:-----------------------:|:--------------------:|:-----------------------:|:--------------------:|
| **3B No Defense** | `0.606` / `0.259` | `0.085` / `0.184` | `0.517` / `0.426` | `0.046` / `0.048` | `0.380` / `0.202` | `0.269` / `0.290` |
| **3B ARGUS** | `0.594` / `0.331` | `0.001` / `0.001` | `0.517` / `0.498` | `0.000` / `0.000` | `0.376` / `0.368` | `0.008` / `0.008` |
| **3B Meta-SecAlign** | `0.571` / `0.540` | `0.000` / `0.000` | `0.511` / `0.502` | `0.000` / `0.000` | `0.366` / `0.353` | `0.001` / `0.001` |
| **3B SecOPD** ($x^{\text{clean}}$) | `0.594` / `0.585` | `0.000` / `0.000` | `0.516` / `0.517` | `0.000` / `0.000` | `0.372` / `0.366` | `0.000` / `0.000` |
| **3B ERASE** ($x^{\text{erase}}$) | **`0.612` / `0.601`** | **`0.000` / `0.000`** | **`0.520` / `0.541`** | **`0.000` / `0.000`** | **`0.389` / `0.394`** | **`0.000` / `0.000`** |
| **7B No Defense** | `0.666` / `0.323` | `0.080` / `0.124` | `0.593` / `0.466` | `0.083` / `0.094` | `0.383` / `0.274` | `0.163` / `0.187` |
| **7B ARGUS** | `0.663` / `0.352` | `0.001` / `0.002` | `0.592` / `0.545` | `0.001` / `0.001` | `0.380` / `0.369` | `0.004` / `0.006` |
| **7B Meta-SecAlign** | `0.642` / `0.619` | `0.001` / `0.002` | `0.510` / `0.531` | `0.000` / `0.000` | `0.372` / `0.379` | `0.000` / `0.000` |
| **7B SecOPD** ($x^{\text{clean}}$) | `0.647` / `0.642` | `0.000` / `0.000` | `0.584` / `0.584` | `0.000` / `0.000` | `0.382` / `0.375` | `0.000` / `0.000` |
| **7B ERASE** ($x^{\text{erase}}$) | **`0.664` / `0.634`** | **`0.000` / `0.000`** | **`0.592` / `0.597`** | **`0.000` / `0.000`** | **`0.397` / `0.394`** | **`0.000` / `0.000`** |

### 2. OOD Post-Filter Refusal Collapse vs. Self-Distillation (`Table 2`, `3B`)

- Across `6` OOD accuracy benchmarks (`GSM8K`, `MathVista`, `MMMU`, `Omni-Bench`, `OCRBench`, `MSVD-QA`), the base `3B` model averages `0.5849` accuracy and `0.0790` `LibriSpeech` WER.
- **`ERASE`** preserves OOD capability across all three training modalities: `0.5776` Acc / `0.0881` WER (audio-trained), `0.5803` Acc / `0.0820` WER (image-trained), and `0.5820` Acc / `0.0887` WER (video-trained).
- **`ARGUS`** collapses on OOD benchmarks: `0.1277` Acc / `0.7401` WER (audio-trained), `0.2967` Acc / `0.3622` WER (image-trained), and `0.2429` Acc / `0.2378` WER (video-trained). Specifically on `GSM8K` (base `0.7339`), `ARGUS` drops to `0.0334` (audio), `0.1365` (image), and `0.0015` (video) because its output post-filter rejects **`96.0%`** (audio) and **`82.9%`** (image) of benign math responses as unsafe.

### 3. Mechanistic Diagnosis & Ablations (`Tables 3–7`)

- **Injected-region sensitivity ($D_{\text{inj}}$)**: On `3B` audio, `ERASE` reduces $D_{\text{inj}}$ from `6.26` nats (base) and `5.15` (`ARGUS`) to `0.0095` nats ($<1/650$ of base) and argmax token flips from `67.3%` to `2.2%`, while keeping erased-view drift $\Delta_{\text{erase}}$ at `0.048` nats (vs `56.4` nats for `Meta-SecAlign`).
- **Why In-Place Erased View ($x^{\text{erase}}$) Beats Clean View ($x^{\text{clean}}$)**: When an injection overwrites part of an image or audio clip, forcing the student to match a teacher that sees the uncorrupted original $x^{\text{clean}}$ (`SecOPD`) trains the student to hallucinate missing signal, degrading audio OOD WER from `0.088` (`ERASE`) to `0.221` (`SecOPD`).
- **Full-distribution vs. single-token supervision**: Distilling only the sampled teacher token drops `3B` `UIA_i` from `0.601` to `0.531` on audio (`-7.0` pp) and from `0.541` to `0.441` on image (`-10.0` pp).

---

## Why Not a Skill?

`ERASE` is a weight-space LoRA fine-tuning objective for omni-modal backbones (`Qwen2.5-Omni`) that requires ground-truth spatial bounding boxes or temporal timestamps of injected segments during training to construct $x^{\text{erase}}$. It cannot be executed as an inference-time procedure by an agent without weight-training access and labeled injection coordinates. Its operational lessons for defense evaluation belong in `output/rules/agent-sandbox-safety.md`.
