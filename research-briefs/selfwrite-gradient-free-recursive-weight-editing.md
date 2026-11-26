# SelfWrite: Gradient-Free Recursive Self-Editing in Weight Space

> **Source**: [arXiv:2611.29513](https://arxiv.org/abs/2611.29513) — *Recursive Self-Editing: LLMs Program Their Own Weight Edits for Self-Improvement* (Linghua Zhang, Yunhe Li)
> **Praxis Source ID**: `src:2611-29513v1`
> **License**: CC-BY-4.0

## Why Not a Skill?

`SelfWrite` is a white-box parameter-editing loop coupled to a custom GPU inspection/algebra DSL (`svd`, `acts(source="own")`, `project_out`, `scale_singular`, `tensor_compute`) over raw `BF16` Transformer projections (`8` GPUs: `7` `vLLM` rollout workers + `1` dedicated `Transformers` activation/edit GPU), evaluated on a single backbone (`Qwen3.8-27B`) and a single mathematical dataset (`DAPO-Math-17K`). Per `AGENTS.md` (architecture-bound white-box weight-editing pipelines without cross-project portability belong in Research Briefs + Rules), it is documented here alongside governance rules in `output/rules/recursive-improvement.md`.

## Core Idea: Closing the Recursive Loop in Weight Space Without Gradients

Prompt/harness evolution (`GEPA`, `AlphaEvolve`) leaves model parameters frozen, while gradient-based RLVR (`GRPO`) fixes the update rule as human-written backpropagation. `SelfWrite` tests whether an open-weight LLM $M_g$ can **author executable programs that inspect its own weights and hidden activations on self-generated reasoning traces and output bounded low-rank parameter edits $\Delta W$**—with each accepted edited checkpoint $M_{g+1}$ becoming the programmer for generation $g + 1$.

## Architecture & Sandboxed Edit Protocol (`§3`, `Appendix A`)

1. **Data Isolation (`14,738` decontaminated `DAPO-Math-17K` integer-answer problems)**:
   - `500` fixed **unseen test** problems (never touched during exploration, screening, or gating).
   - `500` fixed **hidden gate** problems $\mathcal{G}$ (never shown in text or solutions to the editor).
   - `500` **per-generation screen** problems $S_g$ freshly sampled each generation from the remaining `13,738` problems, leaving `13,238` exploration problems $T_g$.
2. **Sandboxed Weight-Space Programming (`8` parallel sessions/generation)**:
   - Each session runs up to `30` tool rounds (`100` tool calls, `160k` completion tokens, `2,400 s` per candidate; `7,200 s` program GPU + `600 s` exploration GPU budget per generation).
   - Allowed read/compute primitives: architecture/norm inspection, cached `svd`, `acts(source="own")` (contrasting layer activations on $M_g$'s own correct vs. failed rollouts on $T_g$, strictly blocking external teacher activations), `project_out`, `scale_singular`, `tensor_compute`, and small exploration `probe` rollouts.
   - **Hard structural bounds**: Every proposed edit must compile to a LoRA adapter `(A, B)` of **rank $r \le 64$** and **relative Frobenius norm $\|\Delta W\|_F / \|W_g\|_F \le 0.1$** per target matrix (`BF16` storage, `FP32` accumulation), with filesystem/network escapes blocked.
3. **Two-Stage Paired Screening, Gate Succession, & Stopping**:
   - **Stage 1 (Fresh Screen $S_g$)**: Evaluate each candidate's `avg@4` (`temp = 1.0, top_p = 0.95, top_k = 20, max_tokens = 16,384`) on $S_g$; discard any candidate with $\Delta_k^{\mathrm{scr}} \le 0$.
   - **Stage 2 (Hidden Gate $\mathcal{G}$)**: Evaluate surviving candidates on $\mathcal{G}$ and accept the highest-gain candidate satisfying both $\Delta_k > 0$ and a **`95%` paired bootstrap confidence interval (`10,000` resamples over per-problem mean rewards) strictly above `0`**. Merge `(A, B)` into $W_g$ to form $M_{g+1}$ and halt after `3` consecutive generations with `0` accepted edits.

## Key Quantitative Findings (`Table 1`, `§4.2–4.3`)

Across `5` recursive generations with **zero gradient steps**:

| Generation / Checkpoint | `500`-Problem Gate `avg@4` | Gate Step $\Delta$ | Unseen `500`-Problem Test `avg@4` | Unseen `500`-Problem Test `pass@4` |
|:------------------------|:--------------------------:|:------------------:|:---------------------------------:|:----------------------------------:|
| $M_0$ (`Qwen3.8-27B` base) | `73.95%` | — | `76.30%` | `82.60%` |
| $M_1$ (Gen 1 accepted) | `75.15%` | `+1.20` | — | — |
| $M_2$ (Gen 2 accepted) | `75.65%` | `+0.50` | — | — |
| $M_3$ (Gen 3 accepted) | `75.75%` | `+0.10` | — | — |
| $M_4$ (Gen 4 accepted) | **`76.45%`** | `+0.70` | **`77.75%`** (`+1.45`) | **`84.80%`** (`+2.20`) |
| $M_5$ (Gen 5: `0` accepted) | `76.45%` | `0.00` | `77.75%` | `84.80%` |

- **Emergent edit strategy (`§4.3`)**: Without human templates, `Qwen3.8-27B` converged on contrastive activation-subspace editing—sampling multi-rollout mixed-outcome problems from $T_g$, extracting residual/MLP activations separating correct from incorrect reasoning chains via `acts(source="own")`, projecting onto dominant `svd` singular directions, and applying damped `project_out` / `scale_singular` updates across selected upper-middle projections.
- **Generalization vs. gate-reuse shrinkage**: Held-out test `avg@4` improved by **`+1.45` points** (`58%` of the `+2.50` gate gain) and `pass@4` improved by **`+2.20` points** (`82.60% -> 84.80%`), confirming genuine out-of-sample transfer while exhibiting `1.05` points of gate-to-test shrinkage.

## Governance Caveats & Limitations

- **Leaky gate summary metadata (`§3.1, §3.4, Appendix A.2`)**: Although `SelfWrite` hid $\mathcal{G}$'s problem text and solutions, its cross-generation summary returned numeric $\Delta_k$, `95%` bootstrap CIs, and fixed/broken gate problem counts and IDs to subsequent generations—explaining part of the `+2.50` gate vs. `+1.45` test gap and reinforcing `"DO: Return only accept/reject decisions to the proposer when the acceptance set is reused across rounds"` (`arXiv:2609.33180`).
- **Diminishing returns & single-domain scope**: Gains plateaued by Generation 5 (`+1.20, +0.50, +0.10, +0.70, 0.00`), and cross-domain retention (code, instruction following, safety refusal) after merged subspace edits was not audited.

## Relevance to Praxis

- **Rules**: [`recursive-improvement.md`](../rules/recursive-improvement.md) — Complements [`basersi-training-free-harness-internalization`](basersi-training-free-harness-internalization.md) (`arXiv:2611.24578`, which internalizes *external* LOBO-verified harnesses into `0.230%` low-activity neurons via fixed `ReGap`/`ReKey`) by bounding *model-authored* low-rank weight-edit programs (`r <= 64`, `||Delta W||_F / ||W_g||_F <= 0.1`) under paired screening and non-leaky acceptance gates.
- **Specs**: [`self-improving-agent.spec.md`](../specs/self-improving-agent.spec.md) — Blast-radius bounds and gate-feedback hygiene for weight-modifying RSI loops.
