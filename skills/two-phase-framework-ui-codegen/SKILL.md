---
name: two-phase-framework-ui-codegen
description: >
  Eliminate cross-framework negative transfer and syntax mixing when fine-tuning
  multimodal LLMs for multi-framework WebUI code generation (Vanilla HTML/CSS,
  React, Vue, Angular). Uses moderate code normalization, offline pre-gradient
  compatibility and JSD heterogeneity estimation, compatibility-capacity phase
  partitioning, and scalar shared-adapter gradient gating. Derived from Ma et al.
  (arXiv:2611.01692).
source: https://arxiv.org/abs/2611.01692
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Two-Phase Framework UI Codegen

> **Source**: [Phase-wise MLLM Tuning for Multi-framework WebUI Code Generation](https://arxiv.org/abs/2611.01692) (Ma et al., 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Fine-tuning a single Multimodal Large Language Model (MLLM) to generate, edit, or repair WebUI code across multiple frontend frameworks (`Vanilla` HTML/CSS/JS, `React`, `Vue`, `Angular`, etc.) from UI screenshots.
- Diagnosing and resolving cross-framework syntax contamination (such as React `className` or JSX hooks leaking into Vue templates or Angular TypeScript components) that causes compilation failures.
- Designing parameter-efficient LoRA/adapter architectures and multi-stage training schedules for heterogeneous code generation domains without incurring expensive online gradient-tracking overhead.

---

## Core Concepts

### Cross-Framework Negative Transfer in UI-to-Code MLLMs

Mapping a visual screenshot to executable WebUI code requires two distinct capabilities: **shared visual-to-structural perception** (layout hierarchy, spatial alignment, styling) and **framework-specific syntactic realization** (DOM manipulation in Vanilla, JSX + hooks in React, template directives in Vue, and `@Component` decorators + TypeScript modules in Angular).

When a single MLLM is jointly fine-tuned on mixed batches across all frameworks simultaneously:
1. Shared adapter parameters suffer from **gradient direction conflicts** between syntactically incompatible frameworks.
2. High-heterogeneity frameworks with verbose boilerplate (especially `Angular`, averaging 1,309 tokens/sample vs. 1,023 for `Vanilla`, 1,142 for `Vue`, and 1,187 for `React`) distort shared visual-structural representations or get overwritten by majority patterns, collapsing compilation success rates.

### Offline Relationship Estimation (Compatibility + Heterogeneity)

Instead of tracking pairwise gradients online at every training step (which adds **+23% training time overhead**), cross-framework relationships can be estimated **offline once before training** (+2% overhead) using two complementary signals:
- **Representation Heterogeneity ($\Delta_{i,j} \in [0, 1]$)**: Normalized Jensen–Shannon divergence over unigram+bigram token distributions after **moderate code normalization**.
- **Optimization Compatibility ($S(\mathcal{D}_i, \mathcal{D}_j) \in [0, 1]$)**: Rescaled cosine similarity of offline pre-gradients computed on a shared LoRA adapter over $K=100$ mini-batches per framework before full tuning begins.

---

## Step-by-Step Procedure

### Step 1: Apply Moderate Code Normalization ($\mathrm{Norm}(y)$)

Before computing token-distribution divergence across frameworks, normalize code samples $y \in \mathcal{D}_j$ using **moderate normalization**—stripping superficial stylistic noise while strictly preserving framework-defining grammar:

1. **Standardize formatting**: Normalize whitespace, indentation, line breaks, and quote styles; strip all inline and block comments.
2. **Abstract non-syntactic identifiers**: Replace local variable names, temporary helper function names, auto-generated CSS class hashes, and random IDs with canonical placeholders.
3. **Normalize equivalent local expressions**: Canonicalize trivial local idioms while **preserving all framework-specific syntax tokens** (such as JSX tags, `useState`, `v-bind`/`v-for`, `@Component`, `ngFor`, and framework import structures).
   - *Why moderate normalization matters*: Weak normalization (formatting-only) leaves identifier noise that inflates divergence and drops downstream CLIP similarity by **0.014** (0.7812 vs. 0.7950), whereas strong normalization (stripping framework syntax into generic AST tokens) erases the true structural differences between frameworks and drops CLIP by **0.018** (0.7769) and compilation success from **0.9007 to 0.8694**.
4. **Compute mixed $n$-gram distributions**: Tokenize $\mathrm{Norm}(y)$ and form an equal mixture of empirical unigram and bigram distributions:
   $$Q_j = 0.5 \, Q_j^{(1)} + 0.5 \, Q_j^{(2)}$$
5. **Compute pairwise heterogeneity**: Calculate the normalized Jensen–Shannon divergence $\Delta_{i,j} = \mathrm{JSD}(Q_i \parallel Q_j) \in [0, 1]$ for all framework pairs $(i, j)$.

### Step 2: Configure Dual-Adapter Architecture and Estimate Offline Compatibility

1. **Attach shared and framework-specific LoRA adapters** to the frozen MLLM backbone (e.g., `Qwen2.5-VL-7B-Instruct`):
   - *Shared LoRA adapter ($w^s$)*: Rank $r = 16, \alpha = 32$, inserted into middle-to-deep cross-modal/language layers (**layers 16–27**), updated across phases via scalar gating.
   - *Framework-specific LoRA adapters ($\{w_j\}_{j=1}^N$)*: Rank $r = 8, \alpha = 16$, inserted into top syntax-realization layers (**layers 20–27**), where only $w_m$ is active when processing framework $m$.
2. **Measure offline shared pre-gradients**: With all adapters initialized at zero ($w^s = 0, w = 0$), sample $K = 100$ mini-batches per framework $\mathcal{D}_j$ and compute the average gradient $\bar{g}_j = \nabla_{w^s}\mathcal{L}(\mathcal{D}_j)$ extracted at **layer 15** (the boundary entering the shared adapter stack).
3. **Compute pairwise optimization compatibility**:
   $$S(\mathcal{D}_i, \mathcal{D}_j) = \frac{1 + \cos(\bar{g}_i, \bar{g}_j)}{2} \in [0, 1]$$

### Step 3: Partition Frameworks into Sequential Training Phases

Partition the $N$ frameworks into $M$ disjoint phases $\{P_1, \dots, P_M\}$ by maximizing the **compatibility-capacity objective** $G(P_1, \dots, P_M)$, which rewards grouping mutually compatible frameworks while penalizing phases whose intra-phase gradient variance exceeds the positive compatibility margin $\bar{m}(P_t) > C_{P_t}\epsilon_g$:

1. **Evaluate candidate partitions**: Across the four standard WebUI frameworks (`Vanilla`, `React`, `Vue`, `Angular`), `React` and `Vue` exhibit high compatibility ($S = 0.79$) and low heterogeneity ($\Delta = 0.18$), whereas `Vanilla` and `Angular` exhibit low compatibility ($S = 0.31$) and high heterogeneity ($\Delta = 0.73$).
2. **Select the optimal 2-phase schedule ($M = 2$)**:
   - **Phase 1**: $P_1^\star = \{\text{React}, \text{Vue}\}$ — jointly trains the component-centric, high-synergy frameworks first to establish strong shared visual-to-component representations.
   - **Phase 2**: $P_2^\star = \{\text{Vanilla}, \text{Angular}\}$ — trains the document-centric and heavily decorated TypeScript frameworks second without corrupting the Phase 1 component representations.
   - *Ordering rule*: Always train the high-synergy component phase (`React + Vue`) **before** the heterogeneous phase (`Vanilla + Angular`). Reversing the phase order drops average CLIP from **0.7950 to 0.7817** and Compilation Success Rate (CSR) from **0.9007 to 0.8789**.

### Step 4: Apply Offline Relationship-Guided Shared-Adapter Gating

1. **Compute per-framework scalar gates ($a_m \in [0, 1]$)**: For each framework $m$, compute its mean compatibility $\bar{S}_m = \frac{1}{N-1}\sum_{j \neq m} S(\mathcal{D}_m, \mathcal{D}_j)$ and mean heterogeneity $\bar{\Delta}_m = \frac{1}{N-1}\sum_{j \neq m} \Delta_{m,j}$, apply min-max normalization across the $N$ frameworks to obtain $\hat{S}_m, \hat{\Delta}_m \in [0, 1]$, and combine them equally:
   $$a_m = \mathrm{clip}\!\left(\frac{1}{2}\hat{S}_m + \frac{1}{2}(1 - \hat{\Delta}_m),\, 0,\, 1\right)$$
   - For the 4-framework WebUI benchmark, this yields **`React` $a_m = 0.96$**, **`Vue` $a_m = 0.95$**, **`Vanilla` $a_m = 0.49$**, and **`Angular` $a_m = 0.00$**.
   - Setting **`Angular` $a_m = 0.00$** completely blocks Angular gradients from modifying the shared adapter $w^s$, forcing Angular to read from the shared visual representation while writing 100% of its syntactic specialization into its dedicated adapter $w_{\text{Angular}}$.
2. **Execute phase-wise gated optimization**: For each phase $t = 1, \dots, M$ (3 epochs per phase, batch size 32, learning rate $2 \times 10^{-4}$):
   - Sample mini-batches exclusively from frameworks $m \in P_t^\star$ and freeze all out-of-phase specific adapters ($w_j$ for $j \notin P_t^\star$).
   - Update the active specific adapter normally: $w_m \leftarrow w_m - \eta \nabla_{w_m}\ell(w^s, w_m; B_m)$.
   - Scale the shared adapter update by $a_m$: $w^s \leftarrow w^s - \eta \, a_m \, \nabla_{w^s}\ell(w^s, w_m; B_m)$.

---

## Quantitative Justification

Evaluated on **13,224 multi-framework samples** combining DesignBench and WebCode2M (**10,862 train / 1,206 val / 1,156 test** across `Vanilla`, `React`, `Vue`, and `Angular`) plus **484 real-world webpages** from Design2Code:

- **Multi-Framework UI Generation (DesignBench Test Set — CLIP / Compilation Success Rate [CSR])**:
  - **Two-Phase Gated Tuning (`Ours` on `Qwen2.5-VL-7B`)**: Achieves **0.7950 Average CLIP** and **0.9007 Average CSR** (`Vanilla`: **0.7956 / 1.0000**, `React`: **0.8124 / 0.9582**, `Vue`: **0.8231 / 0.8310**, `Angular`: **0.7489 / 0.8135**).
  - Outperforms zero-shot `Qwen2.5-VL-7B` (**0.6481 CLIP / 0.3287 CSR**, where Angular CSR is only **0.0866**), `Claude-3.7` (**0.7470 CLIP / 0.8044 CSR**; Angular **0.6223 / 0.6029**), `GPT-4o` (**0.7000 / 0.7648**), `ScreenCoder` (**0.7300 / 0.8735**; Angular **0.6234 / 0.7822**), and `EfficientUICoder` (**0.7073 / 0.8444**).
- **Adapter, Phase, and Gate Ablations**:
  - *Specific-only adapters*: **0.7334 CLIP / 0.8359 CSR**; *Shared-only adapter*: **0.7408 / 0.8412**; *Shared + Specific without phases or gating*: **0.7468 / 0.8479**.
  - *Adding Phase Partitioning (ungated)* boosts performance to **0.7741 CLIP / 0.8712 CSR**.
  - *Adding Relationship-Guided Gating ($a_m$)* further boosts performance to **0.7950 CLIP / 0.9007 CSR**.
  - *Uniform gating ($a_m = 0.5$)* degrades performance to **0.7698 CLIP / 0.8681 CSR** (worse than ungated phase-wise tuning at **0.7741 / 0.8712**), and *Random gating* drops to **0.7643 / 0.8627**, proving that gate weights must reflect actual compatibility and heterogeneity rather than uniform dampening.
- **UI Code Editing and Repair (0–10 GPT-4o Judge Score)**:
  - Achieves **7.60 $\pm$ 0.09** average on Code Editing (vs. `Claude-3.7` **7.20**, `ScreenCoder` **7.12 $\pm$ 0.10**; on `Angular`, **6.89 $\pm$ 0.12** vs. `ScreenCoder` **6.12**) and **7.99 $\pm$ 0.08** on Code Repair (vs. `Claude-3.7` **7.76**, `ScreenCoder` **7.44 $\pm$ 0.10**; on `Angular`, **7.52 $\pm$ 0.11** vs. `ScreenCoder` **6.58**).
- **Real-World Generalization (Design2Code, 484 pages)**: Achieves **94.7** Block Match, **97.9** Text, **87.2** Position, **85.6** Color, and **91.3** CLIP (surpassing `GPT-4o` at **93.0 / 98.2 / 85.5 / 84.1 / 90.4** and `Claude-3.7` at **90.2 / 97.5 / 77.9 / 71.4 / 87.0**).

---

## Anti-Patterns to Avoid

- **Uniformly scaling shared adapter gradients ($a_m = 0.5$)**: Attenuating compatible frameworks (`React`, `Vue`) while still allowing incompatible frameworks (`Angular`) to update the shared adapter performs worse than having no gate at all (**0.7698 vs. 0.7741 CLIP**).
- **Stripping framework syntax during token-distribution normalization**: Removing JSX/directive/decorator tokens before computing JSD makes syntactically incompatible frameworks appear artificially similar, corrupting both phase partitioning and gate weights.
- **Training each framework in total isolation ($M = 4$ phases or specific-only adapters)**: Full separation forfeits shared visual layout perception from `React` and `Vue`, dropping performance from **0.7950 CLIP / 0.9007 CSR** ($M=2$) to **0.7801 / 0.8709** ($M=4$) and **0.7334 / 0.8359** (specific-only).

---

## Related Artifacts

- **Spec**: [Mobile and Generative UI Spec](../../specs/mobile-and-generative-ui.spec.md)
- **Spec**: [Next.js Public Agent App Spec](../../specs/nextjs-public-agent-app.spec.md)
- **Skill**: [Mobile UI Hierarchical Synthesis](../mobile-ui-hierarchical-synthesis/SKILL.md)
- **Skill**: [State-Aware Prototype to WebApp](../state-aware-prototype-to-webapp/SKILL.md)
- **Rules**: [Skill System Design](../../rules/skill-system-design.md), [Agent Evaluation Quality](../../rules/agent-evaluation-quality.md)
