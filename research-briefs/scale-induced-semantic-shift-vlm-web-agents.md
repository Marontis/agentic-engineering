# Scale-Induced Semantic Shift in Visual Prompt Injection Against VLMs and Web Agents

> **Source**: [arXiv:2611.16744](https://arxiv.org/abs/2611.16744) — Yiheng Zhao, Runze Ji, Chenyu Yi, Yi Yu, Bingquan Shen, Alex Kot, Xudong Jiang (2026)
> **Praxis Source ID**: `src:2611-16744v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

First, the core contribution of this paper (`SISS`) is an offensive black-box visual prompt-injection synthesis pipeline (closed-loop surrogate filtering + shallow ControlNet LoRA + pixel-space noise regularization) that hides textual imperatives at native `512x512` resolution so they emerge after aggressive `64x64` downsampling; per [`AGENTS.md`](../AGENTS.md) lines 69–70, we omit offensive generation and fine-tuning recipes. Second, evaluating the paper's defensive detector (`ScaleGuard`, Section IV-E) against [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md) shows it should **not** be packaged as a standalone `SKILL.md`:
1. **Unmeasured `10x` Inference Cost & Clean Utility**: `ScaleGuard` queries **ten VLM views per input image** (`1` native `512x512` view + `9` low-resolution probes), and the authors explicitly note that wall-clock latency and downstream clean-task VLM accuracy were not measured (`0/70` and `0/40` clean FPR reflect small matched-control counts, not a general utility benchmark).
2. **Partial Residual Protection on a Narrow Threat Regime**: Even at `10x` view cost on a single open-weight model (`Qwen2.5-VL-7B-Instruct`), `ScaleGuard` leaves `39.5%` remaining ASR on initially successful non-adaptive attacks (`24.3%` overall vs. `61.4%` undefended) and `35.3%` under one-round adaptation (`15.0%` vs. `42.5%`), and the paper does not publish closed-form transcript-similarity formulas or numeric threshold constants.
3. **Simpler Architectural Mitigation Dominates**: The paper's own resolution sweep proves `SISS` collapses by `-41.07` percentage points between `64x64` (`58.75%`) and `128x128` (`17.68%`), down to **`6.85%` at `224x224` and `5.60%` at `336x336`**. Avoiding aggressive `< 224 px` thumbnail downsampling before VLM ingestion is a one-step architectural rule, making a defensive Research Brief + targeted rule guidance the cleanest representation.

---

## Threat Formulation: Instruction-Level Cross-Resolution Semantic Separation

Multimedia pipelines, document previews, and browser agents routinely resize, compress, or tile visual assets between the **presentation view** shown to a human user (e.g., `512x512`) and the **model-consumption view** ingested by a vision-language model (`VLM`). `Scale-Induced Semantic Shift` (`SISS`) defines an asymmetric black-box failure mode over frozen image assets (`300` evaluation cases pairing `30` Direct Injection, Escape Character, and Context Ignoring payloads with `10` high-frequency textured scenes such as woven fabrics, foliage, scales, and striped shadows):
- **Success Criterion ($\neg b_{512}^m \land b_r^m$)**: Under an identical benign inspection prompt and a fixed text-only semantic judge (`Gemini 3 Pro`, which never sees the image), the target VLM **does not recover** the hidden textual instruction from the native `512x512` presentation view, **but recovers it** after downsampling to $r \times r$ (stress-tested at `512 -> 64` Lanczos).

---

## Key Empirical Findings

### 1. Black-Box Cross-Family Transfer at Extreme Compression (`512 -> 64`) — Bounded Sharply by Resolution (`>= 224x224`)

Evaluated zero-shot on `300` frozen `SISS-Bench` images selected solely with a `Qwen2.5-VL` surrogate (never querying target models during generation; Round 4 declined on `Claude Sonnet 4.6` from `57.67%` to `38.67%` and `Qwen3.5-Plus` from `62.67%` to `51.00%` due to surrogate over-specialization):

| Target Closed-Source VLM | `Z-image-Turbo` (`Zero-shot`) | `QR-Monster` (`64x64`) | `SISS` Round 3 (`64x64`) | `SISS` at `128x128` | `SISS` at `224x224` | `SISS` at `336x336` |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `GPT-4o` | `4.67%` | `35.33%` | `60.33%` | `15.3%` | `<= 10.7%` | `<= 10.7%` |
| `Claude Sonnet 4.6` | `19.00%` | `49.33%` | `57.67%` | `30.7%` | `<= 10.7%` | `<= 10.7%` |
| `Qwen3.5-Plus-02-15` | `20.67%` | `47.67%` | `62.67%` *(R2: `67.67%`)* | `17.7%` | `<= 10.7%` | `<= 10.7%` |
| `Gemini-3-Flash` | `9.00%` | `32.00%` | `54.33%` | `7.0%` | `<= 10.7%` | `<= 10.7%` |
| **4-Model Mean ASR** | **`13.34%`** | **`41.08%`** | **`58.75%`** | **`17.68%`** | **`6.85%`** | **`5.60%`** |

**Critical Boundary**: `SISS` is **not** a resolution-invariant visual jailbreak. Raising the model-consumed image resolution from `64x64` to `128x128` cuts mean ASR by **`41.07` percentage points** (`58.75% -> 17.68%`), and standard VLM encoder resolutions (`224x224` and `336x336`) reduce mean ASR to **`6.85%`** and **`5.60%`** (`<= 10.7%` on every tested model). Short natural-language imperatives (`Context Ignoring`, `Direct Injection`) survive downsampling more consistently than formatting-dependent `Escape Characters` (`\n`, `\t`).

### 2. Perception $\neq$ Action: High Instruction Recovery Yields Only `~4%` Web-Agent Hijacking

In a `1920x1080` browser testbed (`3` benign buttons + `10` attacker-controlled probe elements alongside one `512x512` adversarial image), `SISS` substantially increased explicit hidden-instruction verbalization ($M_{\mathrm{perceive}}$), **but downstream behavioral compromise ($M_{\mathrm{behavior}}$) remained ~`4%`**:

| Web-Agent Metric (`%`) | `Gemini-3-Flash` (Baseline $\to$ `SISS`) | `GPT-4o` (Baseline $\to$ `SISS`) |
|:---|:---:|:---:|
| Explicit Hidden-Text Perception ($M_{\mathrm{perceive}}$) | `37.33%` $\to$ **`67.67%`** | `12.67%` $\to$ **`30.33%`** |
| Attacker-Relevant Webpage Action ($M_{\mathrm{behavior}}$) | `2.33%` $\to$ **`4.00%`** | `1.67%` $\to$ **`3.67%`** |
| Joint Perception & Action ($P(\mathrm{perceive} \cap \mathrm{behavior})$) | `2.33%` $\to$ **`4.00%`** | `1.00%` $\to$ **`3.67%`** |

Trace inspection revealed distinct failure modes: `Gemini-3-Flash` acted primarily after explicitly verbalizing a recovered phrase (e.g., mapping `CLICK DELETE` to an interface button), whereas `GPT-4o` probed controls on partial/normalized cues (`3.67%` behavior vs. `3.67%` joint, vs. `1.67%` / `1.00%` baseline) without always reproducing the payload verbatim.

### 3. Generic Single-View Preprocessing Fails Completely (`p = 1.000`), Whereas Multi-Scale Consistency (`ScaleGuard`) Cuts ASR by `>60%`

On a paired `100`-image defense benchmark evaluated with `Qwen2.5-VL-7B-Instruct` (`Qwen2.5-32B` primary judge; exact two-sided McNemar tests):

| Input-Level Defense | Eval `n` | Undefended ASR | Defended ASR (↓) | Attack Rejected | Clean `FPR` (↓) | Remaining ASR on Hits (↓) | McNemar `p` |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Area resampling | `100` | `68.0%` | `67.0%` | `—` | `—` | `95.6%` | `1.000` |
| `3x3` Median reconstruction | `100` | `68.0%` | `67.0%` | `—` | `—` | `94.1%` | `1.000` |
| `JPEG(75)` + area resampling | `100` | `68.0%` | `69.0%` | `—` | `—` | `95.6%` | `1.000` |
| Gaussian low-pass ($\sigma = 1$) | `100` | `68.0%` | `67.0%` | `—` | `—` | `94.1%` | `1.000` |
| Randomized masking (`5` replicas, majority) | `100` | `68.0%` | `68.0%` | `—` | `—` | `94.1%` | `1.000` |
| **`ScaleGuard` (non-adaptive, disjoint split)** | `70` | `61.4%` | **`24.3%`** | **`40.0%` (`28/70`)** | **`0 / 70`** | **`39.5%` (`17/43`)** | **`2.98e-8`** |
| **`ScaleGuard` (1-round defense-aware adaptive)** | `40` | `42.5%` | **`15.0%`** | **`27.5%` (`11/40`)** | **`0 / 40`** | **`35.3%` (`6/17`)** | **`9.77e-4`** |

- **Why single-view filters fail**: Because `SISS` payloads are encoded into coarse low-frequency spatial stroke aggregations masked by high-frequency scene textures, blurring, median filtering, JPEG compression, and random masking preserve the low-resolution signal (`94.1%–95.6%` remaining ASR, $p = 1.000$).
- **How `ScaleGuard` works**: Compares the VLM transcript of `1` high-resolution `512x512` view against `9` low-resolution probes (`{256, 128, 64}` $\times$ `{area, bicubic, Lanczos}`), calibrated on a disjoint `30`-attack / `30`-clean split ($\text{FPR} \le 5\%$), rejecting inputs when textual instructions absent at `512x512` appear consistently across low-resolution probes. Under a stricter `Gemini` exact-match judge, `ScaleGuard` similarly reduced non-adaptive ASR from `15.7%` to `5.7%` ($p = 0.0156$) and adaptive ASR from `17.5%` to `7.5%` ($p = 0.125$, limited power on `7` undefended hits).

---

## Defensive Takeaways for Multimodal & Web-Agent Pipelines

1. **Preserve Presentation-to-Model Resolution Parity (`>= 224x224` / `336x336`)**: Never aggressively downsample untrusted user images, document thumbnails, or webpage assets to ultra-low resolutions (`64x64`–`128x128`) for "fast preview" VLM triage or context-token savings while displaying higher-resolution originals to human reviewers (`58.75%` ASR at `64x64` vs. `6.85%` at `224x224` and `5.60%` at `336x336`).
2. **Do Not Rely on JPEG, Gaussian Blur, Median Filtering, or Random Masking Against Cross-Scale Visual Injections**: All five generic single-view preprocessing transformations had zero statistically significant effect ($p = 1.000$, `67.0%–69.0%` vs. `68.0%` ASR).
3. **Gate Mandatory Low-Resolution Ingestion with Multi-Scale Consistency Checking (`ScaleGuard`) + Action-Boundary Controls**: Where low-resolution thumbnails are unavoidable, compare high-resolution vs. multi-kernel low-resolution OCR/caption transcripts on a calibrated benign budget (`10` views/image latency cost; measure end-to-end benign cost per [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md)), and enforce downstream action-level goal anchoring and capability gates so residual perceptual leaks (`15.0%–24.3%`) cannot execute unauthorized browser actions.
4. **Separate Perceptual Recovery ($M_{\mathrm{perceive}}$) from Behavioral Compromise ($M_{\mathrm{behavior}}$) in Multimodal Red-Teaming**: Static caption/OCR recovery (`58.75%` static, `30.33%–67.67%` web perception) vastly overstates end-to-end agent hijacking (`3.67%–4.00%`); always report both metrics when benchmarking VLM agent security.

## Related Artifacts

- [`pictionary-render-untrusted-content.md`](pictionary-render-untrusted-content.md) — Rendering untrusted text as images (`arXiv:2609.36121`), which explicitly leaves already-visual assets unprotected
- [`erase-multimodal-prompt-injection-self-distillation.md`](erase-multimodal-prompt-injection-self-distillation.md) — Representation self-distillation against typographic/visual prompt injection (`arXiv:2610.41307`)
- [`mpidetector-multimodal-prompt-injection-reasoning.md`](mpidetector-multimodal-prompt-injection-reasoning.md) — Visual-semantic decoupling for screenshot prompt-injection detection (`arXiv:2610.30202`)
- [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — `"DO: Measure each defense's benign cost on a matched benign arm, on the assembled stack"`, `"DO: Consider rendering untrusted prose as images as one prompt-injection layer, per model"`, and `"DO: Anchor downstream web-agent navigators to the original user goal and pair security metrics with usability calibration"`
