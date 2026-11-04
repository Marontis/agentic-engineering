# Context Compaction for World Models

> Source: `src:2610-38980` — "Context Compaction for World Models" (arXiv:2610.38980, 2026)

## Classification: Research Brief (Contextual Knowledge)

This paper is classified as a **research brief** rather than a standalone skill because its compaction algorithm (a Christofides Traveling Salesperson shortest-walk constructor over 2D room coordinates) is specialized to grid-world video game simulation, and general prompt-cache-aware context compaction is already covered by `skills/prefix-preserving-context-assembly/SKILL.md`. However, the paper provides a uniquely clean experimental separation of **harness-layer context compaction** vs **model-layer KV-cache architectures** (`Decoder-only`, `CED`, `CED-SWA`, `Decoder-Decoder`) and uncovers a severe failure mode where **lower-layer Sliding Window Attention (SWA) loses almost all context retrieval once an agent "dreams" (feeds its own predictions back into its context)**.

---

## Problem & Motivation

Long-horizon world agents must recall states visited hundreds of steps earlier without exceeding GPU KV-cache memory budgets or retraining on longer sequences. Designers can attack this bottleneck at two layers:
1. **Model layer**: Compress the KV cache via cross-attention over middle hidden states (`Causal Encoder-Decoder` / `CED`), lower-layer Sliding Window Attention (`CED-SWA`), or shared upper-layer KV caches (`Decoder-Decoder` / `DD`, as in YOCO).
2. **Agent harness layer**: Compact the interaction history outside the model by pruning redundant revisits while preserving a valid transition trajectory.

Prior evaluations conflate three ways a world model can produce the right room on a revisit: **context reconstruction** (memorizing worlds in weights), **context inference** (guessing from immediately adjacent frames), and true **context retrieval** (reading the earlier visit from the context window).

---

## Experimental Design: Isolating Context Retrieval ($\Delta_{\mathrm{cr}}$)

- **Benchmark World**: `8x8` grid of rooms, each a `16x16` grid of 8 tile types encoded as **8 room tokens + 1 action token = 9 tokens/step**. Models are trained on 5,000 episodes of 512 steps with a **128-step training window** (3 seeds: 42, 43, 44; 21 checkpoints) and evaluated on 400 unseen procedurally generated worlds across 7 revisit-gap bins (`1–7` through `256–511` steps, 40 revisits/bin).
- **Context Retrieval Gain ($\Delta_{\mathrm{cr}} = \alpha_{\mathrm{oc}} - \alpha_{\mathrm{sc}}$)**: Subtracting accuracy on a **shuffled context ($\alpha_{\mathrm{sc}}$)**—which preserves the **5 most recent steps** (matching the 5-step receptive field of four 2-step SWA lower blocks) and replaces older steps with another world—isolates true retrieval from local inference. Beyond the 128-step window, raw context yields $\Delta_{\mathrm{cr}} \in [0.03, 0.06]$.
- **Four 8-Block Architectures ($h=6, d_h=64, D=384$)**:
  - `Decoder-only` (14.35M params): 16 KV vectors/token; 28.3 MB for 128 steps.
  - `CED` (14.35M params, after DeepSeek-V4.1-Flash): 4 lower self-attention blocks + 4 upper cross-attention blocks projecting K/V from middle hidden state $z$; 16 KV vectors/token, $\mathcal{O}(N_s L^2 + N_c L)$ prefill.
  - `CED-SWA` (14.35M params): 4 lower blocks use 2-step SWA; 8 KV vectors/token.
  - `DD` (13.47M params, after YOCO): 4 lower 2-step SWA blocks + 1 shared $K^\star, V^\star$ across all 4 upper blocks; **2 KV vectors/token** (fits 1,020 steps in 28.3 MB).

---

## Key Empirical Findings

### 1. Lazy Harness Compaction (`Compact When Full`) Beats Per-Step Compaction on Both Accuracy and Latency
- At revisit gaps `[128, 511]` (**4$\times$ beyond the 128-step training window**, zero retraining):
  - **Raw 128-step window**: $\Delta_{\mathrm{cr}} \in \mathbf{[0.03, 0.06]}$
  - **`Compact every step`**: $\Delta_{\mathrm{cr}} \in \mathbf{[0.39, 0.51]}$ across all 4 architectures, but adds **7.8 ms/step** mean TSP overhead (15.0 ms max) and forces a full prefill on every step.
  - **`Compact when full`**: Appends raw steps until reaching 128 steps, then compacts (triggering once every **$\sim 50$ steps**, average length **103 steps**), achieving $\Delta_{\mathrm{cr}} \in \mathbf{[0.44, 0.54]}$ while prefilling on only **8 of 512 steps**.

### 2. Model-Layer KV Compression vs Retrieval Quality (Table 1)
| Architecture | Params | KV Vectors / Token | Steps in 3.5 MB (2,304 vecs) | Decode B=1 (ms) | Decode B=16 (ms) | 128-Step Prefill (ms) | Gap `[64, 127]` $\Delta_{\mathrm{cr}}$ (128-step window) |
|:-------------|:-------|:-------------------|:-----------------------------|:----------------|:-----------------|:----------------------|:--------------------------------------------------------|
| `Decoder-only` | 14,352,000 | 16 | 16 | 5.74 | 17.42 | 14.53 | **0.54** |
| `CED` | 14,352,768 | 16 | 16 | 5.89 | 18.06 | **9.80** | $\approx$ `Decoder-only` (no loss) |
| `CED-SWA` | 14,352,768 | 8 | 32 | 5.30 | 11.37 | 9.56 | Degraded by lower SWA |
| `DD` (YOCO) | 13,465,728 | **2** | **128** | **4.49** | **7.53** | **9.20** | **0.39** |

Projecting upper-layer K/V from the middle layer $z$ (`CED`) speeds up 128-step prefill by **$\sim 1.5\times$** (14.53 ms $\to$ 9.80 ms) with zero retrieval loss, whereas lower-layer SWA and upper-layer KV sharing trade retrieval accuracy for memory capacity.

### 3. Lower-Layer SWA Collapses When the World Agent "Dreams" (Section 5.4)
When the agent **dreams**—storing its own predicted room frames in context on revisits rather than ground-truth environment frames during 512-step sessions:
- **Without dreaming**: `Compact every step` achieves $\Delta_{\mathrm{cr}} \in \mathbf{[0.37, 0.50]}$ across all four architectures.
- **With dreaming**: `Decoder-only` and `CED` (full lower-layer attention) maintain $\Delta_{\mathrm{cr}} \in \mathbf{[0.28, 0.42]}$ at 128-step loops (and **$\ge 0.33$** on 8-step loops), whereas `CED-SWA` and `DD` (2-step SWA lower blocks) collapse to **$\le 0.09$** at 128-step loops and **$\le 0.14$** even on 8-step loops—whether using raw or compacted context. Because `CED` and `CED-SWA` differ *only* in whether the 4 lower blocks use SWA, the collapse is directly caused by lower-layer SWA under self-generated context rollouts.

---

## Why Not a Skill?

The Christofides TSP walk constructor assumes reversible 2D grid transitions where revisiting a coordinate renders intermediate walk steps Markov-redundant. General coding and tool-use agents should continue using `prefix-preserving-context-assembly` for KV-cache-preserving lazy compaction.

---

## Connections to Praxis

- **Workflow & Context Architecture (`rules/adk-workflow-architecture.md` & `skills/prefix-preserving-context-assembly/SKILL.md`)**: Confirms from a world-modeling perspective that lazy threshold-triggered compaction (`compact when full`, prefilling on 8/512 steps) beats every-step compaction on both latency and accuracy, and establishes a critical architectural constraint against using lower-layer SWA in autoregressive self-rollout ("dreaming") loops.
