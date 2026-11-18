# From Recursion to Convolution: Parallel Self-Improvement for Multi-Agent Systems (`ConvRSI`)

> **Source**: [arXiv:2611.20891](https://arxiv.org/abs/2611.20891) — Zheng Wang, Yuang Liu, Sachith Abeywickrama, Yangkai Ding, Tao Yu, Xinyu Zhang, Hongbo Wang, Qi Ye, Xuefeng Jin, Zhangchun Zhao (`openJiuwen Team`, Huawei Technologies Co., Ltd., November 2026)
> **Code**: [github.com/LYA2333/ConvRSI](https://github.com/LYA2333/ConvRSI)
> **Praxis Source ID**: `src:2611-20891v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Like [`skillmem-compact-external-skill-memory-latent-mas`](./skillmem-compact-external-skill-memory-latent-mas.md) (`arXiv:2610.37935`) and [`heterofold-cross-family-kv-transfer`](./heterofold-cross-family-kv-transfer.md), `ConvRSI` is a **white-box neural multi-agent architecture** built on `RecursiveMAS` (`LatentMAS` family) that requires direct access to internal Transformer hidden states ($\mathbf{H}_{i,f} \in \mathbb{R}^{L_{i,f} \times H_i}$), custom trainable PyTorch slot-reader / 1D-depthwise-convolution / Graph Convolutional Network (`GCN`) / `InnerLink` / `OuterLink` projection layers, and two-stage teacher-forced cross-entropy training on supervised multi-agent reference datasets (`Sequential-Math`, `Sequential-Code`). It cannot be deployed as a prompt, tool, or black-box API workflow procedure. We document its space–time latent convolution design and empirical trade-offs here and integrate its architectural evidence into [`skill-system-design.md`](../rules/skill-system-design.md).

---

## Core Architecture: Space–Time Latent Co-Evolution

Sequential multi-agent self-improvement (`Recursive-TextMAS`, `RecursiveMAS`) suffers from compounding error across chain-like rounds, repeated text decode/re-encode bottlenecks, and isolated single-feature updates. `ConvRSI` replaces deep sequential recursion with **coupled spatial convolutions in continuous latent space** across $N$ heterogeneous frozen LLM backbones $\{\mathcal{F}_i\}_{i=1}^N$ (native widths $H_i$, shared convolutional width $D$, $K$ content-dependent slots per feature, $R$ convolutional rounds):

1. **One-Time Static Encoding & Content-Dependent Slot Reader (`Eq. 8`)**:
   - Each agent encodes $F - 1 = 4$ static text features (`task`, `role`, `system`, and optional `experience`; $F = 5$ with recurrent `message`) **once** per example with stop-gradient $\operatorname{sg}[\mathcal{F}_i(\operatorname{Emb}_i(x_{i,f}))]$ and pools valid tokens into $K$ slots $\mathbf{z}_{i,f,k} \in \mathbb{R}^{H_i}$, projected via $\mathbf{W}_i^{\mathrm{in}}\operatorname{LN}(\mathbf{z}_{i,f,k}) + \mathbf{b}_i \in \mathbb{R}^D$.
2. **Intra-Agent 1D Feature Convolution (`Eqs. 5–6`)**:
   - At each slot $k$, a channel-wise 1D convolution (`kernel = 5`, `dilation = 1`, `same` padding) with residual `GELU` + `LN` mixes local dependencies across the ordered `[task, role, system, experience, message]` axis (`message` masked to `0` at $r = 1$), followed by softmax gate pooling ($\beta_{i,f,k}$) and a residual MLP $\psi_i$ to emit local message $\mathbf{u}_{i,k} \in \mathbb{R}^D$ concurrently across all $N$ agents.
3. **Inter-Agent Graph Matrix Convolution & Pre-Computed Soft Prefixes (`Eqs. 3, 7, 9–10`)**:
   - Stacking local messages into $\mathbf{U}_k \in \mathbb{R}^{N \times D}$ (`[B, N, K, D]` batched), a shared GCN layer updates all agents in parallel along normalized collaboration adjacency $\mathbf{S} = \widetilde{\mathbf{D}}^{-1/2}(\mathbf{A} + \mathbf{I})\widetilde{\mathbf{D}}^{-1/2}$ (supporting `Sequential`, `Mixture`, asymmetric `Distillation`, and symmetric `Deliberation` graphs):
     $$\mathbf{M}_k = \operatorname{LN}\!\left[\operatorname{GELU}\!\left(\mathbf{S}\mathbf{U}_k\mathbf{W}_g + \mathbf{1}\mathbf{b}_g^\mathsf{T}\right)\right]$$
   - Because static slots $\mathbf{Z}_{\mathrm{static}}$ are cached, **all $R$ convolutional rounds run upfront** ($\mathbf{M}^{(r)} = \mathcal{G}_{\mathbf{A}}(\mathcal{C}(\mathbf{Z}_{\mathrm{static}}, \mathcal{Q}(\mathbf{M}^{(r-1)})))$) to pre-compute $K$-token soft prefixes $\mathbf{p}_i^{(r)} = \mathcal{Q}_i(\mathbf{m}_i^{(r)})$ before scheduled LLM forwards (`InnerLinks` $\mathcal{I}_i$ and cross-model `OuterLinks` $\mathcal{O}_{i \to j}$), with perturbation contraction guaranteed when Lipschitz product $\kappa = L_{\mathrm{LN}} L_\sigma \|\mathbf{S}\|_2 \|\mathbf{W}_g\|_2 L_{\mathcal{C}} L_{\mathcal{Q}} < 1$ and $\max(\kappa, b) < 1$ (`Eqs. 12–13`).
   - **Two-stage supervised training (`Eq. 11`)**: *Inner training* trains each agent's slot reader, $\mathcal{C}_i$, and $\mathcal{Q}_i$ independently in parallel via token cross-entropy $\mathcal{L}_{\mathrm{in},i}$; *Outer training* jointly optimizes local modules, GCN weights $\mathbf{W}_g$, and `OuterLinks` via terminal cross-entropy $\mathcal{L}_{\mathrm{out}} = \operatorname{CE}(\mathbf{P}_{\mathrm{out}}^{(R)}, \mathbf{y}^\star)$ while keeping LLM backbones and `InnerLinks` frozen.

---

## Key Empirical Results (`4` Random Seeds, NVIDIA RTX 4090D)

> **Metric note**: The abstract/introduction headline of **`5.04%` performance improvement, `17.27%` inference-cost (token) reduction, and `45.11%` latency reduction** vs. `RecursiveMAS` on `MATH-500` at $r = 3$ corresponds to **relative** changes over `Table 2`'s exact numbers: `(75.0 - 71.4) / 71.4 = +5.04%` (`+3.6 pp` absolute), `(556 - 460) / 556 = -17.27%` generated tokens, and `(2658 - 1459) / 2658 = -45.11%` runtime (`1.82x` speedup).

### 1. Scaling Across Recursion Depths $r \in \{1, 2, 3\}$ (`Sequential-Light`, `Table 2`)

Team roster: `Qwen3-1.7B` (`Planner`) $\to$ `Llama-3.2-1B-Instruct` (`Critic`) $\to$ `Qwen2.5-Math-1.5B-Instruct` (`Solver`):

| Round & Method | `MATH-500` Acc. (`%`) | `MATH-500` Time (`s`) | `MATH-500` Gen. Tokens | `MBPP+` `Pass@1` (`%`) | `MBPP+` Time (`s`) | `MBPP+` Gen. Tokens |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **$r = 1$**: `Recursive-TextMAS` (text) | `71.4` | `2,254` | `1,195` | **`30.4`** | `1,489` | `1,163` |
| **$r = 1$**: `RecursiveMAS` (latent) | `70.1` | `1,409` | `558` | `29.1` | `776` | `603` |
| **$r = 1$**: **`ConvRSI` (Ours)** | **`71.6`** | **`1,162`** | **`471`** | `30.0` | **`431`** | **`559`** |
| **$r = 2$**: `Recursive-TextMAS` (text) | `71.0` | `3,761` | `2,201` | `30.0` | `3,030` | `1,879` |
| **$r = 2$**: `RecursiveMAS` (latent) | `70.9` | `1,799` | `482` | `29.5` | `982` | `566` |
| **$r = 2$**: **`ConvRSI` (Ours)** | **`72.4`** | **`1,255`** | **`464`** | **`30.3`** | **`549`** | **`508`** |
| **$r = 3$**: `Recursive-TextMAS` (text) | `69.6` | `4,721` | `3,088` | `29.1` | `3,575` | `2,548` |
| **$r = 3$**: `RecursiveMAS` (latent) | `71.4` | `2,658` | `556` | `32.1` | `1,249` | `611` |
| **$r = 3$**: **`ConvRSI` (Ours)** | **`75.0`** | **`1,459`** | **`460`** | **`32.9`** | **`695`** | **`584`** |

- **Text recursion degrades with depth on `1B–1.7B` models, whereas convolutional latent co-evolution scales**: From $r = 1 \to 3$, `Recursive-TextMAS` **drops `-1.8 pp` on `MATH-500` (`71.4% -> 69.6%`) and `-1.3 pp` on `MBPP+` (`30.4% -> 29.1%`)** while more than doubling tokens (`1,195 -> 3,088`) and runtime (`+109.4%`). `ConvRSI` rises **`+3.4 pp` (`71.6% -> 75.0%`)** and **`+2.9 pp` (`30.0% -> 32.9%`)** with flat token output (`-2.3%` on `MATH-500`, `+4.5%` on `MBPP+`) and only `+25.6%` runtime growth on `MATH-500` (vs. `+88.6%` for `RecursiveMAS`)—finishing `3`-round `MBPP+` (`695 s`) faster than `1`-round `RecursiveMAS` (`776 s`) and `3`-round `MATH-500` (`1,459 s`) within `50 s` of `1`-round `RecursiveMAS` (`1,409 s`, `+4.9 pp`).

### 2. Topology Generalization (`Mixture`) & Cross-Paradigm Baselines (`Tables 3–5`)

- **`Mixture` topology (`Qwen2.5-Coder-3B-Instruct` + `BioMistral-7B` + `DeepSeek-R1-Distill-Qwen-1.5B` $\to$ `Qwen3.5-2B` summarizer, `Table 4`)**: `ConvRSI` improves over `RecursiveMAS` by **`+5.2 pp` on `MATH-500` (`60.6% -> 65.8%`)** and **`+2.9 pp` on `MBPP+` (`47.4% -> 50.3%`)**, demonstrating larger gains on fan-in specialist aggregation than on `3`-node chains.
- **Comparison against harness/memory/workflow RSI baselines (`Table 5`)**: `ConvRSI` (`75.0%` `MATH-500` / `32.9%` `MBPP+`) outperforms adapted `ModularRSI` (`Qwen3.5-4B`: `67.1%` / `32.1%`), `Hermes+` (`Sequential-Light` solver: `64.6%` / `28.6%`; `Qwen3.5-4B`: `67.2%` / `27.3%`), and `MASS` (`Qwen2.5-Math-1.5B-Instruct` `Level-0`: `62.8%` / `23.5%`; `Level-1`: `68.7%` / `28.7%`, trailing `ConvRSI` by `-6.3 pp` and `-4.2 pp`).

---

## Related Artifacts

- **Rules**: [`skill-system-design.md`](../rules/skill-system-design.md) (`"DO: Extract skills as explicit text from paired trajectories before distilling them into role-conditioned latent representations"`), [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md)
- **Research Briefs**: [`skillmem-compact-external-skill-memory-latent-mas`](./skillmem-compact-external-skill-memory-latent-mas.md) (`arXiv:2610.37935`), [`heterofold-cross-family-kv-transfer`](./heterofold-cross-family-kv-transfer.md), [`thinkflow-latent-conversational-memory`](./thinkflow-latent-conversational-memory.md)
