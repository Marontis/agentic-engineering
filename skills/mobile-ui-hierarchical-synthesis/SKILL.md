---
name: mobile-ui-hierarchical-synthesis
description: >
  Fine-grained mobile UI understanding and renderable component-tree synthesis
  using an 80-category two-level front-end component taxonomy, compact JSON
  component DSL, and sequential online render-aware GRPO. Covers element
  referring, dense full-screen grounding with Dual-IoU rewards, and online
  Playwright visual verification. Derived from UI-UG 2 (arXiv:2611.00926).
source: https://arxiv.org/abs/2611.00926
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Mobile UI Hierarchical Synthesis

> **Source**: [UI-UG 2: Advancing Mobile UI Understanding and Generation with Fine-Grained Supervision and Reinforcement Learning](https://arxiv.org/abs/2611.00926) (Yang et al., 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Building or fine-tuning vision-language models (VLMs) and UI coding agents that must both parse mobile screenshots (element referring, single-target GUI grounding, and full-screen dense detection) and generate renderable mobile UI code from natural-language requirements.
- Designing intermediate representations (DSLs) for mobile UI generation where raw HTML/JSX suffers from high token overhead and structural syntax errors.
- Training RL post-training pipelines (such as GRPO) for UI generation and dense spatial grounding where naive reward functions cause reward hacking or cross-task gradient interference.

---

## Core Concepts

### The Granularity and Modality Gap in Mobile UI Agents

Most GUI perception pipelines rely on coarse, flat label sets (10–20 generic categories such as `Text`, `Icon`, `Image`, `Input`) that do not map to reusable front-end component libraries (such as Ant Design Mobile, Material UI, or Vant). Meanwhile, UI code generation pipelines optimize token-level cross-entropy over verbose HTML/CSS without verifying how the rendered output looks or behaves, and treat UI understanding and UI generation as isolated tasks rather than exploiting how perceptual supervision (OCR, color, spatial layout) improves visual synthesis.

### Two-Level Front-End Component Taxonomy (80 Categories)

Instead of flat OS accessibility class names, align UI perception and synthesis around a **two-level hierarchy of 9 parent classes and 71 child subcategories (80 categories total)** directly mapped to front-end component libraries:

- **`Card` (9 subcategories)**: `HorizontalCard`, `VerticalCard`, `BannerCard`, `GridCard`, `PanelCard`, `CouponCard`, `ProfileCard`, `ArticleCard`, `ProductCard`.
- **`Collapse` (9 subcategories)**: `AccordionItem`, `DropdownMenu`, `ExpandableText`, `FilterDrawer`, `PopupModal`, `BottomSheet`, `ActionSheet`, `PopoverTip`, `CascaderPicker`.
- **`Chart` (7 subcategories)**: `LineChart`, `BarChart`, `PieChart`, `RadarChart`, `GaugeChart`, `CandlestickChart`, `ProgressRingChart`.
- **`Navigation` (7 subcategories)**: `TopNavBar`, `BottomTabBar`, `SegmentTab`, `SideBarNav`, `BreadcrumbNav`, `IndexBar`, `PaginationDot`.
- **`Progress` (6 subcategories)**: `LinearProgress`, `StepIndicator`, `TimelineNode`, `SliderBar`, `LoadingSpinner`, `SkeletonBlock`.
- **`Button` (10 subcategories)**: `PrimaryButton`, `SecondaryButton`, `OutlineButton`, `TextButton`, `IconButton`, `FloatingActionButton`, `SwitchToggle`, `StepperButton`, `TagButton`, `CloseButton`.
- **`Text` (16 subcategories)**: Including fine-grained functional text roles such as `SingleLineText`, `MultiLineText`, `MoneyLineText`, `TitleText`, `SubtitleText`, `BadgeText`, `TimestampText`, `LinkText`, `PlaceholderText`, and `NoticeBarText`.
- **`Image` (3 subcategories)**: `AvatarImage`, `IllustrationImage`, `ThumbnailImage`.
- **`Checkbox` (4 subcategories)**: `RadioItem`, `SquareCheckbox`, `CheckTag`, `AgreementCheck`.

### Compact Renderable JSON Component DSL

Represent generated mobile interfaces as a recursive JSON component tree rather than raw HTML. Each node specifies five structured attributes:

1. `type`: Either `"Component"` (referencing a library widget from the 80-category taxonomy) or `"Tag"` (layout containers such as `div` or `span`).
2. `name`: The exact component or tag identifier (for example, `ProductCard`, `TopNavBar`, `PrimaryButton`).
3. `className`: Utility CSS styling tokens (Tailwind CSS classes) controlling layout, spacing, typography, and colors.
4. `params`: Key-value props where each property includes its value and a `bindType` (`"Static"` for constants or `"Data"` for dynamic state bindings).
5. `children`: Ordered array of nested child nodes.

In UI-UG 2 (>5,000 requirement–screenshot–JSON tuples), this JSON DSL reduces token count by **16.7% on average** compared to equivalent HTML while guaranteeing direct deterministic compilation into live mobile views.

---

## Step-by-Step Procedure

### Step 1: Curate Multi-Source Fine-Grained Supervision Data

1. **Deduplicate screenshot corpora**: Filter raw mobile screenshot pools (such as RICO, VINS, Android in the Wild [AITW], and Android Control [AC]) using CLIP visual embeddings to remove near-duplicate screens (~7.5K images per source, >30,000 screenshots total).
2. **Annotate with human-in-the-loop verification**: Label bounding boxes using the 80-category two-level taxonomy, plus OCR transcriptions and foreground hex color codes for text categories (`SingleLineText`, `MultiLineText`, `MoneyLineText`). Audit annotations against a held-out verification set (target inter-annotator agreement Cohen's $\kappa > 0.82$).
3. **Order dense grounding targets deterministically**: For full-screen dense detection prompts, sort ground-truth bounding boxes first by category frequency and then by top-left coordinates $(y_1, x_1)$ so the autoregressive model learns a canonical generation order.

### Step 2: Run Unified Supervised Fine-Tuning (SFT) with Calibrated Task Mixing

1. **Unify coordinate and DSL formatting**: Train a single VLM backbone (freezing the ViT vision encoder while updating the multimodal adapter and LLM backbone) across three task families:
   - *Element Referring*: Given a bounding box $[x_1, y_1, x_2, y_2]$, predict the fine-grained component class, plus OCR text and hex color if the target belongs to $\mathcal{T}_{\text{txt}} = \{\text{SingleLineText, MultiLineText, MoneyLineText}\}$.
   - *GUI & Dense Grounding*: Given an instruction or full-screen dense prompt, output target bounding boxes and component classes.
   - *UI Generation*: Given a natural-language user requirement, synthesize the complete JSON component DSL tree.
2. **Calibrate the SFT task ratio**: Mix Referring, Dense/GUI-Grounding, and Generation instructions at a **3:3:4 ratio** (120K instruction samples, ~0.6B tokens, max sequence length 8192). Under a fixed sample budget, including **20% UI understanding data (`U20`)** maximizes downstream UI generation quality (**4.760** overall generation score vs. **4.668** for generation-only `U0`), while higher understanding ratios (`U20` to `U100`) monotonically improve referring accuracy (**0.789 to 0.838**) and dense grounding F1 (**0.475 to 0.690**).

### Step 3: Apply Task-Conditional Composite Rewards

Design verifiable, task-specific rewards for Group Relative Policy Optimization (GRPO) across $G=8$ rollouts per prompt:

1. **Referring Reward ($R_{\text{ref}}$)**:
   $$R_{\text{ref}} = R_{\text{fmt}} + R_{\text{cls}} + \mathbf{1}[t^* \in \mathcal{T}_{\text{txt}}] \cdot (R_{\text{ocr}} + R_{\text{col}})$$
   - $R_{\text{fmt}} \in \{0, 1\}$ checks valid structured output format.
   - $R_{\text{cls}} \in \{0, 1\}$ checks exact match on the 80-category label.
   - $R_{\text{ocr}} = 1 - \text{ED}(\hat{s}, s^*) / \max(|\hat{s}|, |s^*|)$ measures normalized character edit distance.
   - $R_{\text{col}} = \max(0, 1 - \Delta E_{ab}(\hat{\mathbf{c}}, \mathbf{c}^*) / 50)$ converts predicted and ground-truth hex colors into perceptual **CIE $L^*a^*b^*$** space and penalizes Euclidean chromatic distance $\Delta E_{ab}$.
2. **Dense & Single-Target Grounding Reward ($R_{\text{ground}}$)**:
   - For single-target captioned grounding: $R_{\text{cap}} = \text{IoU}(\hat{b}, b^*) + R_{\text{fmt}}$.
   - For full-screen dense grounding: Use **bidirectional Dual-IoU** ($R_{\text{dense}} = R_{\text{rec}} + R_{\text{pre}} + R_{\text{fmt}}$), where $R_{\text{rec}}$ averages each ground-truth box's best IoU over predicted boxes of the same class, and $R_{\text{pre}}$ averages each predicted box's best IoU over ground-truth boxes of the same class.
   - *Critical safeguard*: **Never optimize dense recall ($R_{\text{rec}}$) alone.** Optimizing $R_{\text{fmt}} + R_{\text{rec}}$ causes severe reward hacking where the model over-generates bounding boxes—pushing Recall up to 0.742 but collapsing Precision to 0.754, F1 to **0.727**, and mIoU to **0.836** (worse than the SFT baseline of **0.742 F1 / 0.865 mIoU**). Full Dual-IoU achieves **0.777 F1 / 0.832 Precision / 0.729 Recall / 0.894 mIoU**.
3. **Online Render-Aware Generation Reward ($R_{\text{gen}}$)**:
   $$R_{\text{gen}} = R_{\text{fmt}} + R_{\text{render}} + R_{\text{perc}}, \quad R_{\text{perc}} = 0.5 \cdot R_{\text{judge}} + 0.5 \cdot R_{\text{cpr}}$$
   - Execute an online server-side **Playwright** rendering pipeline during RL rollout evaluation to compile each candidate JSON DSL into a live viewport screenshot.
   - Gate perceptual scoring ($R_{\text{perc}}$) strictly on $R_{\text{fmt}} = 1$ (valid JSON schema) AND $R_{\text{render}} = 1$ (zero runtime/rendering exceptions in Playwright).
   - Compute $R_{\text{judge}} \in [0, 1]$ using a rubric-based VLM judge (`Qwen3-VL-235B-A22B`) scoring the rendered screenshot from 0–10 across four dimensions: *Color & Aesthetic Design*, *Visual Structure & Alignment*, *Textual & Content Consistency*, and *Interface Usability & Interactivity*.
   - Compute $R_{\text{cpr}} \in [0, 1]$ via **Contrastive Preference Ranking (CPR)**: conduct round-robin pairwise visual comparisons across all $G=8$ rendered rollouts in the group, evaluating every pair in both `(A-left, B-right)` and `(B-left, A-right)` orders to eliminate VLM positional bias.

### Step 4: Execute Sequential Curriculum GRPO (Generation $\rightarrow$ Referring $\rightarrow$ Grounding)

1. **Separate RL into sequential task stages rather than joint multi-task RL**: Because UI generation produces long multi-thousand-token JSON trees while referring and grounding produce short structured outputs with distinct reward scales, joint multi-task RL suffers from gradient interference (+2.73% Gen, +2.70% Grd F1, +0.86% Ref Acc over SFT, worse than single-task RL at +4.43% Gen, +4.02% Grd F1, +1.47% Ref Acc).
2. **Run a 3-stage sequential curriculum** (1 epoch per stage, KL coefficient `0.01`, max LR `1e-6`, global batch size 64, $G=8$ rollouts):
   - **Stage 1 — Generation RL** (2,000 samples with online Playwright rendering + $R_{\text{gen}}$): Establishes high structural and visual synthesis quality first.
   - **Stage 2 — Referring RL** (6,000 samples with $R_{\text{ref}}$): Sharpens fine-grained component classification, OCR text fidelity, and CIE $L^*a^*b^*$ color perception.
   - **Stage 3 — Grounding RL** (6,000 samples with $R_{\text{ground}}$): Refines spatial localization and full-screen layout alignment without degrading generation or referring capabilities.

---

## Quantitative Justification & Cross-Task Transfer

- **Understanding-to-Generation Reward Transfer**: Fine-grained perceptual rewards directly improve corresponding dimensions of visual UI generation:
  - Adding the CIE $L^*a^*b^*$ color reward ($+R_{\text{col}}$) improves generated *Color & Aesthetic Design* by **+1.60%**.
  - Adding the OCR edit-distance reward ($+R_{\text{ocr}}$) improves generated *Textual & Content Consistency* by **+2.48%**.
  - Adding the dense Dual-IoU layout reward ($+R_{\text{dense}}$) improves generated *Visual Structure & Alignment* by **+4.72%** (plus +1.64% Color, +0.25% Text, and +1.74% Interactivity), whereas single-target grounding ($+R_{\text{cap}}$) provides negligible or slightly negative transfer (-0.27% Structure, -0.25% Text, -0.17% Interactivity).
- **Benchmark Performance (`UI-UG 2-4B` initialized from `Qwen3-VL-4B-Instruct`)**:
  - *UI Generation (out of 6.0 across JSON validity, Renderability, Color, Structure, Text, Interactivity)*: `UI-UG 2-4B` achieves **4.92** (**0.99 JSON / 0.98 Rend / 0.73 Col / 0.72 Str / 0.79 Txt / 0.71 Int**), a **+5.8%** improvement over `UI-UG 2-4B-SFT` (**4.65**), outperforming `Claude Sonnet 4.5` (**4.70**), `Qwen3-VL-235B` (**4.59**), `GPT-5.2` (**4.33**), `Kimi K2.5` (**4.32**), `UI-UG-7B` (**4.20**), and `Gemini 3.1 Pro` (**3.89**).
  - *Element Referring (Category / OCR / Color)*: Achieves **0.906 / 0.938 / 0.739**, outperforming `UI-UG-7B` (**0.738 / 0.759 / 0.583**), `Gemini 3.1 Pro` (**0.535 / 0.690 / 0.501**), and `Kimi K2.5` (**0.514 / 0.845 / 0.689**).
  - *Dense Grounding (Hungarian set-matching at $\text{IoU} \ge 0.5$)*: Achieves **0.777 F1 / 0.832 Precision / 0.729 Recall / 0.894 mIoU** (vs. `Gemini 3.1 Pro` at **0.471 F1 / 0.759 mIoU** and `UI-UG-7B` at **0.447 F1 / 0.840 mIoU**).
  - *GUI Grounding*: Achieves **0.902** on ScreenSpot-V1 Mobile (502 samples) and **0.929** on ScreenSpot-V2 Mobile (449 samples), up from `Qwen3-VL-4B` (**0.861 / 0.886**).

---

## Anti-Patterns to Avoid

- **Training dense UI detectors with recall-only IoU rewards**: Omitting the precision term $R_{\text{pre}}$ incentivizes bounding-box flooding, degrading both F1 (0.742 $\rightarrow$ 0.727) and mIoU (0.865 $\rightarrow$ 0.836) below the SFT checkpoint.
- **Scoring generated UI code with text-only rewards**: Evaluating UI code generation without executing a headless browser renderer (`R_render`) and checking visual aesthetics (`R_judge` + pairwise `R_cpr`) misses broken layouts and unrenderable component trees.
- **Running single-direction pairwise VLM judging**: Comparing rollout pairs in only one spatial order introduces left/right positional bias; always average both `(A, B)` and `(B, A)` presentations in Contrastive Preference Ranking.
- **Mixing heterogeneous UI tasks into a single joint GRPO loop**: Combining long-sequence UI code generation with short-sequence referring/grounding in one simultaneous RL stage causes gradient interference; use sequential curriculum stages instead.

---

## Related Artifacts

- **Spec**: [Mobile and Generative UI Spec](../../specs/mobile-and-generative-ui.spec.md)
- **Skill**: [Mobile Spatial Accessibility Grouping](../mobile-spatial-accessibility-grouping/SKILL.md)
- **Skill**: [Two-Phase Framework UI Codegen](../two-phase-framework-ui-codegen/SKILL.md)
- **Rules**: [Skill System Design](../../rules/skill-system-design.md), [Agent Evaluation Quality](../../rules/agent-evaluation-quality.md)
