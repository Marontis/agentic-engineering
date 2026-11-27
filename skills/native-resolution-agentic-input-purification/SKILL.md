---
name: native-resolution-agentic-input-purification
description: >
  Adapt off-the-shelf diffusion purifiers to high-resolution VLM, GUI, shopping, and OCR agent
  inputs via overlapping native-resolution tiling, 4-step global-noise DDIM/Divide-and-Conquer
  denoising, clean-development readout fixing, and matched-clean-cost adaptive validation.
source: "arXiv:2611.34181"
repository: Marontis/agentic-engineering
license: CC-BY-4.0
---
<!-- License: CC BY 4.0 | Repository: https://github.com/Marontis/agentic-engineering -->

# Native-Resolution Diffusion Input Purification for VLM Agents (`AgenticPure`)

## When to Use

Use this procedure when protecting vision-language model (`VLM`) web, GUI, e-commerce, or document/OCR agents against **adversarial pixel perturbations**—including both imperceptible ($\ell_\infty = 8/255$) and **perceptible, web-pipeline-hardened perturbations** ($\ell_\infty = 64/255$ surviving `0.5x` downsampling + `JPEG-75` recompression)—on screenshots, rendered webpages (`960x540+`), or multi-region visual layouts where:
- Standard `256x256` classifier-oriented diffusion purification destroys small text, card layouts, and fine UI controls before any attack occurs.
- Cheap single-view pixel transforms (`JPEG` compression, bit-depth reduction, Gaussian noise/blur) fail at matched clean-task cost or collapse under gradient-aware adaptive attacks.

**Do NOT use when:**
- Defending against **clean typographic or DOM-rendered textual prompt injections** (plain readable instructions drawn on a page or hidden via `512x512 -> 64x64` thumbnail aliasing): diffusion purification intentionally preserves legible visual semantics (`4.0`-pt `TextVQA` clean cost), so clean typographic commands (`77.96%` `Replace` ASR in `arXiv:2611.24231`) survive intact. Pair with resolution parity (`>= 224x224–336x336`, `arXiv:2611.16744`) and downstream action-boundary provenance gates ([`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md), [`principal-context-permission-intersection`](../principal-context-permission-intersection/SKILL.md)).
- Hard real-time control loops require sub-`50 ms` per-frame perception without GPU batching (`4`-step tiled purification takes `~1.05–1.41 s` per draw on an `H100` GPU).

## Core Insight

In `AgenticPure` (`arXiv:2611.34181`), testing classifier-era diffusion purifiers on native-resolution VLM agent tasks (`Qwen3-VL-8B-Instruct` and `Qwen2.5-VL-7B` across `TextVQA` and `960x540` `5`-card `Web shop` pages) exposed three structural surprises:
1. **Classifier resizing—not diffusion denoising—causes VLM utility collapse**: Running the official `256x256`-resized Divide-and-Conquer purifier (`DC-R`) lost **`35.7` [`29.5, 42.0`] pts** clean accuracy on dev `TextVQA` (**`41.5` pts** on `n = 1,000` held-out; **`58.8` pts** on `Qwen2.5-VL-7B`) and **`16.5` / `17.3` pts** on `Web shop`. Denoising **overlapping `256x256` native-resolution tiles** in **`4` DDIM steps** (`DC-4`) cut clean loss to **`4.0` pts** (`TextVQA` `vote-20`, `5.9` held-out) and **`3.0` pts** (`Web shop` `logit-4`, `1.0` held-out) while running **`43.4x–45.2x` faster** than `200`-step `DC-200` (`1.05 s` vs. `45.57 s`/draw on `Web shop`; `1.41 s` vs. `63.70 s`/draw on `TextVQA`, `0.6`-pt clean diff).
2. **Decisive-element coincidence defeats VLM-attention region masks and input noise estimators**: On agentic pages, both clean accuracy and attacker leverage concentrate on the exact same decisive region (blanking the queried `176x176` product photo drops `Web shop` accuracy `93.0% -> 21.0%` vs. `93.5%` on decoys; `8/255` on text strokes alone hits `0.64` ASR vs. `0.05` equal-area background), so purifying *only* the decisive element already incurs **`1.05x–1.13x`** of full-page clean cost (`0.8` and `-0.2` pts for purifying the rest). Removing `DC-4`'s VLM-attention mask (`DC-4 no mask`) changed clean accuracy by `-0.25` pts and gray-box robust accuracy ($RA_{\mathrm{gb}}$) by `+3.3` pts (`0.0` pts on `Qwen2.5-VL-7B`), while fixed global noise `G@0.175` beat input-estimated `SSNI` (`56.7%`, fooled into $\hat{t} = 0.048$ by low-frequency perceptible perturbations) by **`+18.3` dev / `+17.9` held-out pts** at `2.5`-pt clean cost (`DiffCAP` embedding stopping scored only `28.3%–35.0%`).
3. **Large robustness gains emerge on perceptible web-hardened attacks at matched clean cost**: On `Web shop` ($\ell_\infty = 64/255$, human class agreement $\kappa = 0.90$, undefended `GB-T` `ASR` `61.7%` [`51.7%` after `0.5x` resize + `JPEG-75`]), at `<= 3.0`-pt clean cost (`JPEG-60`, `BIT-3`, `GN-8`), `DC-4` held **`85.0%` $RA_{\mathrm{gb}}$** (**`83.2%`** on `n = 273` held-out) vs. **`<= 40.0%`** for every matched cheap transform (**`+45.0` pts** on `Qwen3-VL-8B`; **`+50.0` pts** [`78.3%` vs. `28.3%`] on `Qwen2.5-VL-7B`), and under same-page BPDA/exact-gradient PGD (`Table 4`) held **`57.5%`** (`DC-4`) and **`80.8%`** (`DC-4+`, $t_s = 0.30$) while `JPEG-60` (`8.3%`) and `GN-16` (`12.1%`) collapsed.

## Step-by-Step Procedure

### Step 1: Tile High-Resolution Agent Inputs Without Global Downsampling (`Adapt`)

Wrap an off-the-shelf unconditional `256x256` diffusion denoiser (e.g., `ADM` ImageNet `256x256`) around native-resolution screenshots or document images $x \in [0, 1]^{H \times W \times 3}$ without resizing $(H, W)$:
1. **Partition into overlapping `256x256` tiles**: Slide a `256x256` window at **`stride = 224` (`32`-px overlap)** across the full native-resolution image (clamping border tiles to image edges so small UI icons, prices, and OCR strokes retain native pixel pitch).
2. **Apply uniform `4`-step reverse denoising and feather seams**: Forward-noise all tiles using a **fixed, input-independent noise schedule**—either uniform global DDIM at $t^* \in [0.175, 0.20]$ (`G@0.175` / `G@0.2`), `4`-step unmasked `DC-4` (`t = 0.4, 0.3, 0.2, 0.1` with rest noise $t_s = 0.20$), or **`DC-4+` ($t_s = 0.30$)** when white-box purifier-aware adaptive adversaries are in threat scope—and reassemble denoised tiles with a **`32`-px linear feathered blend** so tile-boundary seams cannot create phantom UI edges.
3. **Skip VLM-attention region masks and per-input noise/embedding estimators**: Do not spend extra VLM forward passes computing cross-attention region masks, high-frequency noise-level estimates (`SSNI`), or VLM-embedding stopping criteria (`DiffCAP`).

### Step 2: Fix Multi-Draw VLM Readout Exclusively on Clean Development Data

Because multi-draw aggregation (`k` independent stochastic purification draws) changes clean accuracy by up to **`6.8` pts** on the exact same denoised images (`TextVQA` `DC-4` loses `10.8` pts under pixel-averaged `mean-4` vs. **`4.0` pts** under `vote-20`), lock your readout rule on a **disjoint clean development split** (`~200–250` items) before evaluating any attacked inputs:
1. **Closed-set discrete agent actions** (clicking card `A..E`, choosing menu/button IDs, binary UI confirmations): Aggregate per-draw VLM next-token logits across $k = 4$ purified draws (**`logit-4`**), avoiding pixel-space averaging (`mean-k`) when small text must stay sharp and avoiding single-draw variance (`single`).
2. **Open-ended text extraction / OCR / VQA** (`TextVQA`, form-value reading): Sample $k = 8\text{--}20$ purified draws (`vote-8` or **`vote-20`**) and take the normalized majority-vote string across independent VLM generations rather than pixel-averaging denoised frames (`mean-4` blurs fine character strokes).
3. Record the clean development accuracy cost $\Delta_{\mathrm{clean}}$ (`clean_baseline - defended_clean`) and freeze `(schedule, t_s, readout, k)` before running adversarial tests. If you manage purifier configurations inside an automated harness-optimization loop, pass any config change through `"DO: Pass every self-modification through one acceptance gate"` in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md).

### Step 3: Calibrate Against Matched-Clean-Cost Transforms and Pipeline-Hardened Attacks

Validate that diffusion purification earns its `~1 s/draw` GPU cost on your target workload rather than comparing against untuned baselines:
1. **Match clean-accuracy budgets explicitly**: Sweep `JPEG` quality (`q = 10..90`), bit-depth reduction (`BIT-2..5`), and Gaussian noise (`GN`), and compare `DC-4` / `G@t` strictly against non-diffusion transforms whose clean dev loss $\le \Delta_{\mathrm{clean}}$ (`<= 3.0` pts on `Web shop`; `<= 4.0` pts on `TextVQA`), per `"DO: Measure each defense's benign cost on a matched benign arm, on the assembled stack"` in [`../../rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md).
2. **Harden gray-box test attacks across realistic delivery transforms (`EoT`)**: Optimize test perturbations through random JPEG/resize transformations (`GB-T` `q = 60..95` plus `GB-T10` `q = 10..95` and platform delivery $T_{\mathrm{web}}$) so brittle high-frequency `JPEG-20` artifacts (`70.6% -> 58.5%` under `GB-T10`) are not mistaken for genuine robustness.
3. **Run same-page adaptive BPDA / exact-denoiser-gradient checks (`>= 60` PGD steps + `APGD-CE` + perturbation-radius monotonicity `8/255 -> 128/255`)**: Differentiate through the tiled `4`-step DDIM denoiser (exact gradients or `BPDA` identity fallback if VRAM-constrained) and verify `RA_adap` degrades monotonically as $\varepsilon$ grows (`8/255 -> 128/255`) rather than relying on shattered gradients. Upgrade $t_s$ from `0.20` (`DC-4`, `57.5%` adaptive) to **`0.30` (`DC-4+`, `80.8%` adaptive at `5.3`-pt clean cost)** when white-box adaptive attacks are in scope.

### Step 4: Pair Input Purification with Action-Boundary Authorization

Treat `AgenticPure` strictly as a **perceptual integrity layer** that prevents $\ell_\infty$ pixel perturbations from flipping what the VLM sees on product cards, prices, and OCR fields. Always enforce deterministic capability, destination, and user-request grounding checks (`CapLite`, `Principal Contexts`, `Cross-Interface Authorization`) before executing state-mutating clicks, purchases, or API calls.

## Environment Caveats

- **Imperceptible vs. perceptible threat regimes**: Under tight imperceptible budgets ($\ell_\infty = 8/255$ on `TextVQA`), tuned `JPEG` or `G@0.2` comes closer to `DC-4` (`87.6%` `DC-4`, `84.7%` `SSNI`, `58.5%` `diff. JPEG-20` under `GB-T10`); `DC-4`'s `+45` to `+50` pt margin specifically governs **perceptible, web-surviving perturbations** ($\ell_\infty = 64/255$ on product photos, banners, and user-uploaded thumbnails where human viewers still agree on item categories at $\kappa = 0.90$).
- **Compute vs. draw count ($k$)**: Each purified draw on a `960x540` screenshot (`15` overlapping `256x256` tiles) takes **`1.05 s`** on an `H100` (`4.2 s` sequential for `logit-4`, reducible via multi-draw tile batching across GPU SMs; `vote-20` on `TextVQA` prioritizes OCR fidelity over latency). Apply `DC-4` selectively to untrusted external screenshots/uploads rather than trusted internal UI chrome.
- *(Citation-numbering note)*: Between the HTML (`LaTeXML`) and PDF (`BibTeX`) builds of `arXiv:2611.34181`, adjacent reference indices swap (`DiffPure-VLM [74]`/`GDMP [75]` in HTML vs. `[75]`/`[74]` in PDF; `Zhang pop-ups [85]`/`F3 [86]` in HTML vs. `[86]`/`[85]` in PDF); all experimental tables and numbers (`Tables 1–4, S1–S7`) are identical across both builds.

## Failure Modes

- **Resizing screenshots to `256x256` before denoising (`DC-R`)**: Destroys **`35.7–58.8` pts** of clean VLM accuracy on text-heavy inputs before any adversary acts.
- **Selecting readout (`vote-k` / `mean-k` / `logit-k`) on attacked test sets**: Inflates apparent robustness while hiding up to `6.8` pts of clean-accuracy degradation (`mean-4` blurring OCR text vs. `vote-20`).
- **Trusting input-estimated noise schedules (`SSNI`) or embedding stopping (`DiffCAP`)**: Low-frequency `64/255` attacks shift `SSNI`'s wavelet statistic by only `+0.82 x 10^-3` (selecting $\hat{t} = 0.048$, `33.3%–56.7%` $RA_{\mathrm{gb}}$ vs. `75.0%` for fixed `G@0.175`) and bypass `DiffCAP` (`28.3%–35.0%` across all `5` variants).
- **Assuming pixel purification strips readable typographic prompt injections**: Clean text banners or cross-scale `SISS` text survive denoising because they are large-scale semantic structures, not bounded pixel perturbations.

## Cross-References

- **Rules**:
  - [`../../rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DON'T: Downsample untrusted images into tiny thumbnails before VLM ingestion or rely on pixel-space smoothing"`, `"DO: Consider rendering untrusted prose as images as one prompt-injection layer, per model"`, and `"DO: Measure each defense's benign cost on a matched benign arm, on the assembled stack"`
  - [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Spec Templates**:
  - [`../../specs/agent-sandbox.spec.md`](../../specs/agent-sandbox.spec.md) — Multimodal VLM visual-input resolution and purification checklist
- **Related Skills**:
  - [`bounded-context-intervention-window-guardrail`](../bounded-context-intervention-window-guardrail/SKILL.md) — Out-of-band multi-step GUI screenshot action gating (`MobileGrail`, `arXiv:2611.29847`)
  - [`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md) — Deterministic write-argument authorization downstream of VLM perception (`CapLite`, `arXiv:2611.17115`)
  - [`principal-context-permission-intersection`](../principal-context-permission-intersection/SKILL.md) — System-level principal permission intersection at effect sinks (`Conflux`, `arXiv:2611.08768`)
- **Research Briefs**:
  - [`../../research-briefs/scale-induced-semantic-shift-vlm-web-agents.md`](../../research-briefs/scale-induced-semantic-shift-vlm-web-agents.md) — Why `64x64` thumbnail downsampling induces `58.75%` cross-scale visual prompt injection (`SISS`, `arXiv:2611.16744`)
  - [`../../research-briefs/conditional-protection-image-rendered-prompt-injection.md`](../../research-briefs/conditional-protection-image-rendered-prompt-injection.md) — Why clean typographic prompt injections (`77.96%` `Replace` ASR) survive in pixel space (`arXiv:2611.24231`)
  - [`../../research-briefs/erase-multimodal-prompt-injection-self-distillation.md`](../../research-briefs/erase-multimodal-prompt-injection-self-distillation.md) — Weight-level representation self-distillation against multimodal prompt injection (`ERASE`, `arXiv:2610.41307`)

## Sources

- Lin, Y., Guo, Z., Lin, J., & Liu, D. (2026). *Agentic-Level Adversarial Purification: Revisiting Diffusion Purifiers on Native-Resolution Agentic Inputs*. `arXiv:2611.34181` (`src:2611-34181v1`).
