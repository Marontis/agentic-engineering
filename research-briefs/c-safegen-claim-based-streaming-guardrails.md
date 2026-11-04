# C-SafeGen: Certified Safe LLM Generation with Claim-Based Streaming Guardrails

> **Paper**: [C-SafeGen: Certified Safe LLM Generation with Claim-Based Streaming Guardrails](https://arxiv.org/abs/2610.34961)
> **Praxis source**: src:2610-34961

## Why Not a Skill?

The paper presents an inference-time token/claim decoding loop (Claim-based
Stream Decoding with KV-cache perturbation and backtracking) and conformal
risk bounds tailored to token-level language model decoding rather than an
agent-level orchestration procedure. Its insights on claim-boundary streaming
interception, KV-cache backtracking, and non-monotonic model-scale safety are
captured here and as evidence in `rules/agent-sandbox-safety.md`.

---

## Core Concept

Off-the-shelf guardrail classifiers (e.g., LlamaGuard3-8B, ShieldGemma-9B)
typically operate post-hoc on full responses, while empirical safety decoding
methods lack formal risk guarantees. **C-SafeGen** pairs **Claim-based Stream
Decoding (CSD)** with a finite-sample **conformal risk certification**
framework:

1. **Claim Critical Point Detection**: Instead of prompting an LLM to extract
   claims, CSD detects claim boundaries structurally during streaming when the
   probability of a termination token $t \in \mathcal{T}$ (e.g., period,
   newline) exceeds $\alpha_t$ and the segment length since the last claim
   boundary exceeds a minimum length $\alpha_l$.
2. **Guardrail Backtracking & KV-Cache Reuse**: At each claim boundary, a
   guardrail model $G$ scores the prefix $y_{<n}$. CSD computes a claim
   backtrack probability $B_{\alpha_b}(G(x, y_{<n}), C_{\text{desired}})$
   controlled by threshold $\alpha_b \in [0, 1]$ ($\alpha_b = 1.0$ strictly
   enforces the guardrail; $\alpha_b = 0.0$ reduces to greedy decoding). If
   flagged, CSD erases only the KV-cache entries for the current unsafe claim
   while preserving verified prefix claims $\text{KV}_{1:\text{LastClaimPoint}}$,
   and resamples. If decoding stagnates beyond tolerance $\alpha_g$
   ($|\text{counter} - n| > \alpha_g$), CSD applies SmoothLLM-style perturbations
   directly to the KV cache (random masking/permutation, Gaussian noise, or
   structured perturbations). Under a claim risk cascade assumption
   (Assumption 4.1), Theorem 3 proves that CSD without safe resampling exactly
   recovers the guardrail-restricted output distribution $p_G(y)$.
3. **Two-Level Conformal Risk Certification**:
   - *Theorem 1 (Risk Upper Bound)*: For a fixed configuration $\alpha$ calibrated
     on $N_{\text{cal}}$ exchangeable samples, bounds the true risk
     $\mathbb{P}[R_G(x, P_\alpha(x)) \le \hat{r}_\alpha] \ge 1 - \delta$ using
     the minimum of a likelihood-ratio inversion bound $h^{-1}$ and an inverse
     binomial CDF bound $\Phi_{\text{bin}}^{-1}$.
   - *Theorem 2 (Configuration Set Certification)*: Given a nominal risk target
     $r$ (e.g., $0.10$), certifies a family-wise error rate (FWER) controlled
     set of configurations $\bm{\alpha}_r = \{\alpha_j : p_j \le \delta_j\}$
     with $\sum_j \delta_j = \delta$.

### Key Findings

- **Lowest empirical and certified risk**: Evaluated on AdvBench and
  JailbreakBench with GCG adversarial suffixes across `Llama-3.1-8B` and
  `Llama-3.1-13B` (using `LlamaGuard3-8B` and `ShieldGemma-9B`), CSD
  consistently achieves lower empirical and conformal safety risk than Vanilla
  ($T = 1.0$), Self-Reminder, Safety-Opt, Best-of-N ($N = 10$), and
  SafeDecoding.
- **Certified nominal risk holds across scales**: All configurations certified
  for nominal safety risk $r = 0.10$ (Theorem 2) remain strictly below $0.10$
  empirically across both benchmarks and both model sizes; raising the
  backtrack threshold $\alpha_b$ reduces both mean risk and variance.
- **8× faster than Best-of-N with lower risk**: Best-of-N ($N = 10$) exceeds
  40 seconds per instance while leaving the highest mean safety risk among the
  compared safe-generation methods; CSD runs in ~7 seconds per instance, and
  CSD+KV Cache reduces runtime to below 5 seconds per instance without
  degrading safety.
- **Model size alone does not improve adversarial safety**: `Llama-3.1-13B`
  does not uniformly outperform `Llama-3.1-8B`; under Self-Reminder and
  Best-of-N, the 13B model exhibits slightly higher safety risk than the 8B
  model.

## Relevance to Praxis

- **Stream-level claim interception beats whole-response rejection**: Erasing
  and resampling only the offending claim segment preserves valid prefix work
  and avoids the >40 s latency of full-response Best-of-N sampling.
- **Calibrate decoding thresholds with finite-sample bounds**: Theorem 1 and
  Theorem 2 show how black-box guardrail scores can be turned into certified
  configuration sets ($\bm{\alpha}_r$) with $1 - \delta$ coverage.
- **Related artifacts**:
  - `rules/agent-sandbox-safety.md`: "DON'T: Assume model scale implies safety
    robustness" and "DO: Calibrate safety-detector thresholds on realistic
    benign traffic, per target model".
  - [`rag-hallucination-repair`](../skills/rag-hallucination-repair/SKILL.md):
    claim-level verification and repair for grounded generation.
