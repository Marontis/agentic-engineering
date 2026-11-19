---
name: strategy-diverse-ipi-purple-teaming
description: >
  Harden open-weight tool-using LLM agents against indirect prompt injection
  (IPI) via offline two-stage purple-teaming: prevent red-team strategy mode
  collapse using rolling sparse dictionary learning (`BPDN`) and separate
  group-decoupled (`GDPO`) binary/continuous reward normalization, then align
  the defender via `C1`/`C2` task-alignment checks and symmetric `z+/z-`
  contrastive token-level on-policy self-distillation (`OPSD`) without auxiliary
  inference latency or benign utility loss. Derived from "PIPETTE: Prompt
  Injection Purple-Teaming for Robust LLM Agents" (arXiv:2611.24362).
source: https://arxiv.org/abs/2611.24362
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Strategy-Diverse Offline IPI Purple-Teaming (`PIPETTE`)

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when **post-training an open-weight tool-using LLM agent (`4B–27B+`) offline to resist indirect prompt injection (`IPI`) inside untrusted tool outputs** without adding runtime classifier/canary calls or degrading clean task completion (`Benign Utility`, `BU`).

## When to Use

- You have weight-update access (`LoRA` or full-weight `GDPO`/`GRPO`) to a tool-calling agent (such as an enterprise workspace/CRM assistant, repository/CLI coding agent, or multi-step RAG/API workflow agent) and want intrinsic model-level defense that runs at **`1.0x` native inference latency** (`0` auxiliary runtime calls).
- Prior adversarial `SFT` or binary-outcome `RL` runs either **overfit narrow red-team patterns** (failing under `TAP` or `Genetic` adaptive search on unseen environments) or **collapsed clean Benign Utility** via over-refusal on benign untrusted records.
- You want to pair weight-level `IPI` resilience with deterministic downstream sink authorization (such as [`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md) or `Principal Contexts`) in a defense-in-depth stack.

Do **not** use this skill when you only have closed-API access to the target model (use [`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md) or [`pre-execution-action-auditing`](../pre-execution-action-auditing/SKILL.md)), when you only want black-box evaluation coverage auditing without defender weight updates (see [`autopi-taxonomy-coverage-adaptive-red-teaming.md`](../../research-briefs/autopi-taxonomy-coverage-adaptive-red-teaming.md) and [`taxonomy-driven-red-teaming`](../taxonomy-driven-red-teaming/SKILL.md)), or as a replacement for deterministic server-side access control on irreversible tool sinks.

## Core Insight

Prompt-injection purple-teaming fails along two distinct axes that naive RL coupling makes *worse* (`arXiv:2611.24362`):

1. **Higher train-time red-team `ASR` can *worsen* downstream defender robustness (`Strategy Mode Collapse`)**: Standard RL red-teamers (`RL-Hammer`, `PISmith`) amplify whatever high-yield tactic succeeds earliest, while surface lexical/embedding penalties (`self-BLEU`, sentence embeddings, token entropy) reward superficial rephrasings of the **exact same redirection mechanism**. On `AgentDyn` (`Qwen3-4B`), `PISmith` more than doubled `RL-Hammer`'s train-time cumulative `ASR` (`68.75%` across `7,132` strings vs. `33.39%` across `4,282` strings), yet **degraded** unseen worst-case adaptive `ASR` on `AgentDojo` under `RL` adversarial training from `27.5%` to **`47.5%`** (and worsened `3 of 4` model-trainer cells overall) because its unseen `ChatInject` strategy Explainability Score (`ES`) stagnated near `0.20` (`Qwen3-4B`) and `0.35` (`Llama-8B`).
2. **Coarse trajectory-level defense rewards induce benign over-refusal**: Off-policy `SFT` shifts the policy away from its own trajectory distribution (`Llama-8B` clean `BU` dropped from `40.21%` to `15.46%–29.90%`), while binary trajectory-outcome `RL` (`r_def` alone) assigns a single scalar across an entire multi-step rollout (`35.05%` `BU` on `Llama-8B`, `59.79%` vs. `61.86%` base on `Qwen3-4B`), failing to localize *which generated tokens* were steered by untrusted tool data versus the legitimate user goal.

`PIPETTE` resolves Stage 1 by rewarding **unexplained task-agnostic strategy novelty** relative to a rolling $\ell_1$-sparse strategy dictionary (`BPDN`), and resolves Stage 2 by combining explicit step-level `C1`/`C2` task-alignment checks with **symmetric `z+/z-` contrastive token-level On-Policy Self-Distillation (`OPSD`)** on contaminated rollout steps—lifting unseen `ES` to `~0.60` / `0.77`, restoring or improving clean `BU` (`64.95%` vs. `61.86%` on `Qwen3-4B`; `41.24%` vs. `40.21%` on `Llama-8B`), and cutting `250`-attempt `TAP` / `248`-attempt `Genetic` adaptive `ASR` to **`0.00% / 2.50%`** (`Llama-8B`), **`2.50% / 5.00%`** (`Qwen3.6-27B`), and **`5.00% / 10.00%`** (`gpt-oss-20b`, vs. `50.00% / 92.50%` native `Instruction Hierarchy`).

---

## Step-by-Step Procedure

### Step 1: Isolate Disjoint Training Environments & Format Warm-Up

1. **Keep purple-teaming environments strictly disjoint from evaluation suites**: Construct or select multi-step sandboxed `(benign user task t_u, orthogonal redirect objective t_adv, injection slot)` pairs (`560` pairs across `3` domains in `AgentDyn`) that share **zero** tasks, schemas, or static evaluation templates with your held-out certification benchmarks (`AgentDojo`, `ASB`, or production golden suites). Enforce owner-authority hygiene on evaluation splits via [`owner-authority-ipi-eval-construction`](../owner-authority-ipi-eval-construction/SKILL.md).
2. **Stabilize structured generation before RL**: Warm up the offline red-team policy briefly on weak format-demonstration examples (`<think>...</think><injection>...</injection>`) strictly on the training environment (`AgentDyn`), and exclude any warm-up template family from downstream security evaluation.

### Step 2: Build a Coverage-Aware Red-Team Archive via Rolling Sparse Dictionary Learning (`PIPETTE-Red`)

Run online group-based RL ($S_{\mathrm{RT}} = 250$ steps, group size $G = 6$, `12` task pairs/step, $\text{LR} = 10^{-5}$) against a frozen copy of the target agent, rewarding **functional redirection success weighted by strategy novelty** rather than raw `ASR` or surface text distance:

1. **Abstract successful rollouts into task-agnostic strategy descriptions**: Whenever a rollout $\tau'$ satisfies the deterministic environment verifier $\Phi_{t_{\mathrm{adv}}}(\tau') = 1$, pass only the extracted `<injection>` span $d_{\mathrm{adv}}$ to a lightweight local summarizer (`Qwen3-1.7B` in `arXiv:2611.24362`) instructed to describe **how** redirection was attempted in **task-agnostic operational terms** (persuasion framing, authority/system mimicry, context seam exploitation, structural formatting) while stripping all domain nouns, tool names, and concrete argument literals. Embed the resulting strategy summary into a unit-normalized vector $\mathbf{x} = \mathcal{E}(\psi(d_{\mathrm{adv}})) \in \mathbb{R}^d$ (`Qwen3-Embedding-0.6B`).
2. **Score Explainability (`ES`) against the current sparse primitive dictionary $\mathbf{D}_\ell \in \mathbb{R}^{d \times K}$**:
   - Retrieve up to `5` dictionary atoms (learned strategy primitives, each auto-labeled with a short canonical name + `1–2` sentence definition by `Qwen3-1.7B`) most relevant to $\psi(d_{\mathrm{adv}})$.
   - Have a calibrated offline rubric grader (`Qwen3-14B`) rate how completely those primitives explain the candidate's high-level tactics on a **`1–5` Weighted Coverage scale** (`1` = `<20%` novel strategy, `3` = `40%–60%` hybrid, `5` = `>80%` fully explained by existing primitives), rescaled linearly to $\mathrm{ES}(\mathbf{D}_\ell, d_{\mathrm{adv}}) \in [0, 1]$ (`ES = 0` before the first dictionary build at $\ell = 0$).
3. **Decouple binary and continuous rewards via `GDPO` (`Group reward-Decoupled Normalization Policy Optimization`)**:
   - Compute three separate reward components per rollout: binary redirect success $r_{\mathrm{atk}} = \Phi_{t_{\mathrm{adv}}}(\tau') \in \{0, 1\}$, binary XML tag validity $r_{\mathrm{fmt}} \in \{0, 1\}$, and continuous coverage novelty $r_{\mathrm{cov}} = \Phi_{t_{\mathrm{adv}}}(\tau') \cdot (1 - \mathrm{ES}(\mathbf{D}_\ell, d_{\mathrm{adv}})) \in [0, 1]$.
   - **Critical normalization rule**: Never sum binary (`{0, 1}`) and continuous (`[0, 1]`) rewards before group z-scoring—high variance in binary outcomes drowns out continuous novelty gradients. Normalize $r_{\mathrm{atk}}$, $r_{\mathrm{fmt}}$, and $r_{\mathrm{cov}}$ **independently within each $G$-rollout group** first, then combine normalized advantages with weights $(w_{\mathrm{atk}}, w_{\mathrm{fmt}}, w_{\mathrm{cov}}) = (1, 0.25, 0.5)$.
4. **Rebuild $\mathbf{D}_{\ell+1}$ every $M = 25$ steps via $\ell_1$-sparse `BPDN`**:
   - Admit newly successful `(d_adv, x)` records into the cumulative strategy memory $\mathcal{M}_{\ell+1}$ **only when $\mathrm{ES}(\mathbf{D}_\ell, d_{\mathrm{adv}}) < \delta = 0.5$** so near-duplicate variants do not bloat the archive.
   - Solve alternating dictionary learning over normalized embeddings $\mathbf{X}_{\ell+1}$ with $K = 32$ unit-norm atoms (select $K \in \{16, 32, 64\}$ so atoms remain non-redundant yet specific): alternate `Basis Pursuit Denoising` (`BPDN`, $\lambda = 10^{-4}$) sparse coding $\min_{\mathbf{A}} \frac{1}{2}\|\mathbf{X} - \mathbf{D}\mathbf{A}\|_F^2 + \lambda \|\mathbf{A}\|_1$ with column-wise atom updates and unit-norm projection, selecting target sparsity $\alpha \in [0.1, 0.9]$ by minimizing trade-off score $(1 - R^2)/\alpha$ (`R^2 ≈ 0.87` at $K = 32$).

### Step 3: Warm Up Explicit `C1`/`C2` Task-Alignment Reasoning on the Defender

Before launching adversarial `RL` on the defender $\pi_\theta$, teach a lightweight, auditable pre-action reasoning discipline (`384` trajectories mixed `50/50` clean and attacked from the Stage-2 archive):

1. **`C1` (Observation Redirect Check)**: Immediately after ingesting any untrusted external observation or tool return $o_{t-1}$, inspect whether $o_{t-1}$ attempts to introduce new instructions, override workflow rules, or redirect parameters away from the authenticated user request $t_u$.
2. **`C2` (Pre-Tool Goal Authorization Check)**: Immediately before emitting any tool call $a_t$ (or terminal answer), verify that both the **selected tool** and **every argument value** are required and authorized by the original user goal $t_u$ rather than untrusted observation content.

Keep `C1`/`C2` concise: on `Qwen3-4B`, trained `PIPETTE` trajectories changed clean end-to-end latency by only **`-0.47` to `+0.62 s`** (`3.53–8.32 s` vs. `3.50–7.70 s` undefended) and token usage by **`-28%` to `+16%`** (`10,154` vs. `14,042` on `Banking`; `21,348` vs. `18,378` on `Workspace`).

### Step 4: Train the Defender via `GDPO` + Symmetric `z+/z-` Token-Level Self-Distillation (`PIPETTE-Blue`)

Run online defender `RL` ($S_{\mathrm{AT}} = 200$ steps, group size $G = 6$, `12` tasks/step, $\text{LR} = 5 \times 10^{-6}$) over the Stage-2 strategy-diverse archive interleaved with a **`25%` clean-task retain mix** (`t_adv = ∅`):

1. **Combine trajectory outcome and step-level `CoT` rewards via `GDPO`**:
   - Define trajectory defense reward $r_{\mathrm{def}}(\tau) = \Phi_{t_u}(\tau)$ on clean episodes, and $r_{\mathrm{def}}(\tau) = \Phi_{t_u}(\tau) \cdot (1 - \Phi_{t_{\mathrm{adv}}}(\tau))$ on attacked episodes so the agent earns `+1` **only when it both blocks the redirect AND completes the user's benign task** (preventing degenerate refuse-everything policies).
   - Score each reasoning step with an **offline-only** rubric judge (`Qwen3-14B`, never deployed at runtime) awarding $r_{\mathrm{CoT}, t} = \frac{1}{2}(c_{t,1} + c_{t,2}) \in \{0, 0.5, 1\}$ for `C1` and `C2`, averaged over steps to $r_{\mathrm{CoT}}(\tau)$, and normalize $r_{\mathrm{def}}$ and $r_{\mathrm{CoT}}$ separately per rollout group (`GDPO`) with weights $(w_{\mathrm{def}}, w_{\mathrm{CoT}}) = (1, 0.5)$.
2. **Add symmetric `z+/z-` contrastive token-level self-distillation (`r_tok`) on contaminated steps**:
   - For every rollout step $t \ge t_0$ after an injected observation enters history $H'_t$ (`r_tok = 0` on clean tasks and pre-injection steps $t < t_0$), re-evaluate the **frozen reference policy** $\pi_{\theta_{\mathrm{old}}}$ on the **exact on-policy tokens** $y_{t,j}$ generated by the student under two symmetric privileged diagnostic prefixes (`Table XI`):
     - **Safe teacher (`z+`)**: discloses $t_u$ and $t_{\mathrm{adv}}$, instructing the model to treat untrusted tool content strictly as data, ignore $t_{\mathrm{adv}}$, and execute only $t_u$.
     - **Unsafe teacher (`z-`)**: symmetrically discloses $t_u$ and $t_{\mathrm{adv}}$, instructing the model to abandon $t_u$ and prioritize $t_{\mathrm{adv}}$.
   - Compute the per-token log-probability ratio and clip it to $[-\kappa, \kappa]$ ($\kappa = 2$):
     $$r_{\mathrm{tok}}(y_{t,j}) = \operatorname{clip}\!\left(\log \frac{\pi_{\theta_{\mathrm{old}}}(y_{t,j} \mid H'_t, z^+, y_{t,<j})}{\pi_{\theta_{\mathrm{old}}}(y_{t,j} \mid H'_t, z^-, y_{t,<j})},\ -\kappa,\ \kappa\right)$$
   - Normalize $r_{\mathrm{tok}}(y_{t,j})$ across tokens in contaminated steps of the rollout group (`\hat{A}_tok`) and add it to the trajectory advantage: $\hat{A}_{i,t,j} = \hat{A}^{\mathrm{traj}}_i + w_{\mathrm{tok}} \hat{A}^{\mathrm{tok}}_{i,t,j}$ with $w_{\mathrm{tok}} = 0.1$. Because `z+` and `z-` have symmetric prompt structure and identical task disclosure, task-irrelevant phrasing cancels out while exact redirect-compliance tokens receive sharp negative credit and task-preserving tokens receive positive credit (`Table VII`: adding `C1/C2` and `r_tok` on `Qwen3-4B` `ChatInject` improved `ASR / UA / clean BU` monotonically from `3.57% / 45.48% / 59.79%` [`r_def` only] $\to$ `2.38% / 56.90% / 60.82%` [`+ C1/C2`] $\to$ **`1.43% / 58.10% / 64.95%`** [`+ C1/C2 + r_tok`]).

### Step 5: Certify Zero-Shot Generalization & Gate Checkpoint Promotion

Before promoting the hardened checkpoint, pass it through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md):

1. **Clean Benign Utility (`BU`) non-regression**: Assert clean completion on held-out multi-step tool benchmarks does not regress beyond baseline noise (e.g., `PIPETTE` achieved `64.95%` vs. `61.86%` base on `Qwen3-4B`, `41.24%` vs. `40.21%` on `Llama-8B`, `92.78%` vs. `93.81%` [`84.54%` `SecOPD`] on `Qwen3.6-27B`, and `49.48%` vs. `50.52%` on `gpt-oss-20b`).
2. **Multi-step iterative-adaptive + taxonomy-diverse static `IPI` suites**: Test on unseen environments under both `>= 250`-attempt iterative search (`TAP`, `Genetic`) and multi-turn/taxonomy-diverse suites (`ChatInject`, `PIAtlas`), reporting `ASR`, `Utility under Attack` (`UA`), reach-adjusted `Effective ASR` ([`owner-authority-ipi-eval-construction`](../owner-authority-ipi-eval-construction/SKILL.md)), and construction-taxonomy coverage (`Cov@k` at equal compute, [`autopi-taxonomy-coverage-adaptive-red-teaming.md`](../../research-briefs/autopi-taxonomy-coverage-adaptive-red-teaming.md)).
3. **Defense-in-depth composition**: Keep deterministic capability and field-level source-authority checks (`CapLite`, `Principal Contexts`) in front of high-impact write/exec sinks so residual tail breakthroughs (`up to 10.00%` `Genetic` ASR on `gpt-oss-20b`) cannot trigger unauthorized side effects.

---

## Failure Modes & Guardrails

- **Penalizing lexical or raw-injection embedding similarity instead of abstracted strategy coverage**: Computing diversity directly on raw adversarial text $d_{\mathrm{adv}}$ rewards swapping domain nouns or surface punctuation while repeating the same authority/override primitive (`PISmith` `ES` stagnated after iteration `2` in `Fig. 4`). Always abstract $d_{\mathrm{adv}} \mapsto \psi(d_{\mathrm{adv}})$ into task-agnostic operational prose before embedding and dictionary fitting.
- **Summing raw binary and continuous rewards before `GRPO` normalization**: Adding $r_{\mathrm{atk}} \in \{0, 1\}$ and $r_{\mathrm{cov}} \in [0, 1]$ prior to group standardization lets high-variance binary flips dominate gradient direction; always apply per-component `GDPO` group normalization first.
- **Using single-sided (`z+` only) self-distillation or omitting clipping**: Without the symmetric `z-` contrast, prompt-length and disclosure formatting differences between $H'_t$ and $(H'_t, z^+)$ inject spurious KL drift into benign tokens; without $[-\kappa, \kappa]$ clipping ($\kappa = 2$), extreme log-ratio spikes destabilize policy updates.
- **Deploying the training-time `r_CoT` judge as a runtime blocking monitor**: Keep `r_CoT` strictly offline during `PIPETTE-Blue` RL so policies cannot optimize monitor-evasion phrasing against a live CoT gate (see `"DON'T: Deploy the chain-of-thought monitor you optimized the policy against, or score raw reasoning"` in [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md)).

## Cross-References

- [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DO: Pair strategy-dictionary coverage with contrastive token-level on-policy RL when purple-teaming agents against prompt injection"`, `"DO: Test with evolving adversaries, not static attack sets"`, and `"DON'T: Place SLM-generated security artifacts on the write-integrity path"`
- [`agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — `"DO: Report construction-taxonomy coverage alongside ASR at equal total compute in adaptive prompt-injection evaluations"` and `"DO: Enforce owner-authority boundaries, action-deflection cases, and reach-adjusted Effective ASR when evaluating indirect prompt injection defenses"`
- [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"` and `"DO: Evaluate evolved instructions against immutable, held-out negative security testbeds"`
- [`autopi-taxonomy-coverage-adaptive-red-teaming.md`](../../research-briefs/autopi-taxonomy-coverage-adaptive-red-teaming.md) — Companion evaluation brief (`arXiv:2611.24313`) showing why `ASR`-optimized red-teamers collapse onto narrow construction subsets on `PIAtlas`
- [`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md) — Deterministic zero-LLM write-integrity gate (`CapLite`, `arXiv:2611.17115`) to compose downstream of `PIPETTE`-hardened weights

## Sources

- Lipeng He, Yihan Wang, Jiawen Zhang & N. Asokan, "PIPETTE: Prompt Injection Purple-Teaming for Robust LLM Agents" ([arXiv:2611.24362](https://arxiv.org/abs/2611.24362), `src:2611-24362v1`)
