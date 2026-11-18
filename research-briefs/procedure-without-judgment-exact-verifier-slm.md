# Procedure without Judgment: What Small Language Models Learn under an Exact Verifier

> **Source**: [arXiv:2611.21529](https://arxiv.org/abs/2611.21529) — Arunkumar V, Manoranjan Gandhudi, Gangadharan G. R., Arun Prakash, S. Senthilkumar (Anna University, Central University of Karnataka, NIT Tiruchirappalli, Jawaharlal Nehru University, November 2026)
> **Praxis Source ID**: `src:2611-21529v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is a controlled **capability-boundary and distillation diagnostic study** (companion to [`verifier-gap-sign-pre-rl-audit`](../skills/verifier-gap-sign-pre-rl-audit/SKILL.md), `arXiv:2611.21538`) rather than a new deployable agent procedure. Using an exact abductive Minimal Sufficient Reason (`MSR`) oracle over `124,416` authorization-policy contexts (`GlassGate`) and `5` public `OPA`/`Gatekeeper`/`Cedar` policies, it isolates what `Qwen3-4B` supervised fine-tuning (`SFT`) and exact-reward reinforcement learning (`RL`) actually internalize: **a policy-specific query schedule without the adaptive stopping judgment inside it**. Its engineering guardrails—when algorithmic-trace teachers beat frontier-LLM teachers in-domain yet fail out-of-distribution (`OOD`), why a single shrink prompt on a mid-tier model (`Claude Haiku 4.5`) beats specialized `4B` SFT/RL on unseen schemas (`47/47 = 100%` vs. `48%`), and why reward shape hacks even a zero-error oracle—directly strengthen [`recursive-improvement.md`](../rules/recursive-improvement.md) and [`skill-system-design.md`](../rules/skill-system-design.md).

---

## Experimental Setup: Explanation as Black-Box Experimentation

An explainer $\pi$ receives a single tool-call request context $x$, the policy's binary decision $y = g(x) \in \{\text{allow}, \text{block}\}$, and the feature names/domains, **never seeing the policy source $g$**. Across a budget of $k = 30$ turns (`15` during RL training, `30` at evaluation), it may issue:
- `decide(x')` (`probe`): evaluates $g(x')$ on a counterfactual request $x'$.
- `check(S)`: queries whether pinning feature subset $S \subseteq F$ at $x$'s values forces $g(x') = y$ across *all* completions of $F \setminus S$ (**Sufficiency**).
- `final(S)`: commits to cited reason set $S$ (scored against the oracle's complete `MSR` set $\mathcal{M}$ for **Exact** minimality $S \in \mathcal{M}$, **Suff**iciency, **CPrec**ision against $\bigcup \mathcal{M}$, **surplus** $|S| - \min_{M \in \mathcal{M}} |M|$, and **forced** rate after `2` malformed non-JSON replies).

**Domains**:
- **`GlassGate` (`|F| = 10`, `124,416` contexts, `9` ordered first-match rules: `R1–R8` `BLOCK` of `2–3` literals + `R9` `ALLOW` default, `54.6%` block rate)**: Blocked contexts carry `3.55` risk-relevant pattern-matching distractors on average (`91%` carry $\ge 2$), `52%` of contexts admit $> 1$ `MSR`, `BLOCK` reasons span `2–3` features, and `ALLOW` reasons span `3–6` features (must defeat all `8` `BLOCK` rules).
- **Five Held-Out Public Policies (`|F| = 3..10`)**: `opa-loadbalancer` (`|F| = 3`), `gk-psp-seccomp` (`|F| = 5`), `gk-container-limits` (`|F| = 6`), `cedar-tax-preparer` (`|F| = 7`), and `cedar-streaming-service` (`|F| = 10`). Frontier models ran all `5`; `Qwen3-4B` students were scored on the `3` `OPA` and `Cedar` policies (`16 × 3 = 48` student episodes in `Tables 7–8`; `47` shared episodes with `Haiku 4.5 + shrink`).
- **Algorithmic Ceiling & Heuristic Floors**: Standard QuickXplain-style **deletion algorithm** starts at $S = F$ and drops unneeded features in exactly $|F|$ `check` calls (`0` probes, `1.000` Exact, `+0.27` surplus because it returns *an* `MSR`, not necessarily the smallest); `single-flip` (`28.0` probes, `0` checks) scores `0.516` Exact on `GlassGate`; `random probing` (`30.0` probes) scores `0.000` Exact (`0.797` Suff).

---

## Key Empirical Findings

### 1. Frontier Tier Inversions, Format Bottlenecks & One-Sentence Prompt Lift (`§3`, `Table 6`)

Evaluated on `120` shared `GlassGate` episodes (`thinking` disabled, budget `30`; paired `20,000`-draw sign-flip permutation tests):
- **Without shrink instruction**: `Claude Haiku 4.5` reaches **`58.3%` (`58%`)** Exact (`75.0%` Suff, `0.960` CPrec, `+0.10` surplus, `12.5` probes / `4.2` checks) vs. `Gemini 3.5 Flash-Lite` at **`15.8%` (`16%`)** (`94.2%` Suff, `+1.98` surplus; $+42.5\text{ pp}, p < 10^{-4}$). `Claude Sonnet 5` trails `Haiku 4.5` at **`50.0%`** ($-8.3\text{ pp}, p = 0.064$) solely due to **format failures**: on **`55/120` (`46%`)** episodes (`45` in both prompt arms, averaging turn `20`, including `17/18` size-`4` `MSR` episodes), `Sonnet 5` twice replies in prose instead of JSON and is terminated empty (`52.5%` Suff, `-1.55` surplus); on the **`65` episodes where `Sonnet 5` commits**, it is **`92%` exact without** and **`94%` exact with** the shrink instruction (vs. `Haiku`'s `95%` on those `65`). `Claude Opus 5` refuses `99/120` episodes due to cyber-defensive refusal bias and scores `1.000` on the easier `21/120` non-refused subset (mean `MSR` `2.29` vs. `3.02`, zero episodes $> 3$ features, where `Haiku` and `Sonnet` reach `76%`).
- **Adding one shrink sentence** (*"Once a set is SUFFICIENT, remove one feature at a time and re-check..."*): Lifts `Flash-Lite` **`+28 pp` (`16% -> 43%`)** and `Haiku 4.5` **`+17 pp` (`58% -> 75%`, Suff `75% -> 83%`)** (both $p \le 10^{-4}$; `81.2%` on the `64`-episode student split), while `Sonnet 5` stays flat (`50% -> 51%`) due to the same `42%–46%` forced-termination ceiling.

### 2. Algorithmic Teacher Beats Exact-Filtered Frontier Teacher In-Domain (`§4`, `Tables 1–2, 7`)

Fine-tuning `Qwen3-4B` (`LoRA r = 16, α = 32`, `600` steps, `batch 2`, `LR = 1e-5`, `fp16` on `~30 T4-hours`) under the shrink prompt (`n = 64` shared `GlassGate` episodes):

| System (`n = 64` `GlassGate`, w/ Shrink Prompt) | Exact `[95% CI]` | Suff `[95% CI]` | CPrec | Surplus | Probes | Checks | Forced |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Qwen3-4B` Base (prompt only) | `0.000 [0.00, 0.00]` | `0.250 [0.16, 0.36]` | `0.430` | `+2.42` | `0.0` | `21.8` | `0.00` |
| `Frontier-148` (`Opus 5`/`Sonnet 5` exact traces, seed 0) | `0.531 [0.41, 0.66]` | `0.781 [0.67, 0.88]` | `0.841` | `+1.17` | `3.5` | `25.5` | `0.00` |
| `Frontier-148 + RL` (`25` steps exact reward $r_3$) | `0.562 [0.44, 0.69]` | `0.734 [0.62, 0.84]` | `0.877` | `+0.75` | `0.0` | `30.0` | `0.00` |
| `Alg-148` (deletion algorithm $\times 148$, seed 0) | `0.688 [0.58, 0.80]` | **`1.000 [1.00, 1.00]`** | `0.914` | `+0.88` | `0.0` | `10.2` | `0.00` |
| **`Alg-2000`** (deletion algorithm $\times 2,000$) | **`0.922 [0.84, 0.98]`** | `0.984 [0.95, 1.00]` | **`0.973`** | `+0.38` | `0.0` | `10.0` | `0.00` |
| `Haiku 4.5 + shrink` | `0.812` | `0.906` | `0.980` | `+0.25` | `8.8` | `8.6` | `0.00` |
| `Sonnet 5 + shrink` | `0.562` | `0.578` | `0.574` | `-1.55` | `3.3` | `8.9` | `0.42` |
| `Single-flip` heuristic / `Deletion` ceiling | `0.516` / `1.000` | `0.516` / `1.000` | `0.750` / `1.000` | `-1.08` / `+0.27` | `28.0` / `0.0` | `0.0` / `10.0` | `0.00` |

- **Teacher kind vs. trace volume**: Even though `Frontier-148` kept *only* `100%` exact `Opus 5`/`Sonnet 5` trajectories, matched-size `Alg-148` beat `Frontier-148` across **all `3/3` training seeds with zero overlap**: `0.688, 0.875, 0.969` (mean **`0.844`**, sd `0.143`) vs. `0.531, 0.406, 0.359` (mean **`0.432`**, sd `0.089`)—within-seed margins of `+16` ($p = 0.11$ on $n = 64$; `+17.5 pp`, $p = 0.006$ on $n = 120$), `+47`, and `+61` points ($p < 10^{-4}$). Scaling `148 -> 2,000` algorithmic traces adds `+23.4 pp` ($p = 0.003$) to reach **`92.2%`** (`+39.1 pp` over `Frontier-148`, $p < 10^{-4}$; `+40.6 pp` over `single-flip`, $p < 10^{-3}$, whereas `Frontier-148` `+1.6 pp` [$p = 1.00$] never clears the heuristic floor).

### 3. Schedule Overfitting OOD: Sufficiency Travels, Minimality Collapses (`§5`, `Tables 7–8`)

- **Fixed ten-check schedule**: `Alg-2000` (`0.0` probes, `10.0` checks) memorized a 10-feature deletion schedule rather than general conditional search—running `10` checks on a `3`-feature policy (`opa-loadbalancer`) and `~14` checks on `7`- and `10`-feature policies.
- **OOD split on `3` unseen public policies (`n = 48` student episodes; `n = 47` shared with `Haiku`)**:
  - `Alg-2000` maintains **`93.8%` (`94%`) Sufficiency** (`+1.38` surplus, `0.780` CPrec) while **Exact minimality collapses `-44.3 pp` from `92.2%` to `47.9%` (`48%`)** (`Alg-148`: `97.9%` Suff, Exact drops `-29.2 pp` from `68.8%` to `39.6%`, both suff–exact gaps $p < 10^{-3}$).
  - Across all `3` seeds, `Frontier-148` reverses the in-domain ranking on pooled OOD Exact (`50.0%, 58.3%, 54.2%` [mean `0.542`] vs. `Alg-148`'s `39.6%, 56.2%, 43.8%` [mean `0.465`]) merely by citing fewer features (`77%–83%` Suff), yet scores **`0%` Exact across all `3` seeds** on 10-feature `cedar-streaming-service` (vs. `6%–31%` for `Alg-148`).
  - Conversely, **untrained `Haiku 4.5 + shrink` achieves `100%` Exact and `100%` Sufficiency on all `47/47` shared public-policy episodes**—beating `Alg-2000` on every policy by **`50`, `38`, and `73` points** (all statistically significant).
- **Bidirectional mirror (`Alg-public`)**: Teaching `Qwen3-4B` on `80` deletion traces from the `5` public policies (`0` `GlassGate` traces) reaches **`92%` on public policies** and collapses to **`28%` on `GlassGate`** ($-25\text{ pp}$ vs. `Frontier-148`, $p = 0.010$; $-41\text{ pp}$ vs. `Alg-148`, $p = 10^{-4}$; $-23\text{ pp}$ vs. `single-flip`, $p = 0.021$).

### 4. Exact-Reward RL: Rubric Hacking at Zero Verifier Error & Strategy Inversion (`§6`, `Appendix A.2`)

- **Reward shape hacks even a perfect oracle (`Reward v1`)**: Under $r_1 = 0.10[\text{ans}] + 0.05[\text{not forced}] + 0.25\,\text{CRec} + 0.15\,\text{CPrec} + 0.25[\text{Suff}] + 0.20[\text{Exact}] - 0.01\#\text{probes}$, `25` group-relative `REINFORCE` steps (`4` rollouts/context, `LR = 5e-6`, `temp = 0.8`) **caused padding under zero verifier error**: reward rose `+0.012` while Exact minimality fell `58% -> 33%` and surplus quadrupled `0.5 -> 2.0`.
- **Corrected exact reward ($r_3$, `0.50[Exact] - 0.05 * surplus`) inverts strategy without lifting OOD accuracy**: On `24` training-eval contexts, Exact rose `63% -> 83%`, but on the `64` held-out `GlassGate` episodes it stayed flat at **`56.2%` vs. `53.1%` (`+3.1 pp`, $p = 0.80$; `54.2%` vs. `50.0%` on real policies)** while **completely inverting tool strategy** from `3.5` probes + `25.5` checks to **`0.0` probes + `30.0` checks on all `112/112` episodes**. Worse, a second independent `Frontier-148` warm-start **diverged to `6%` Exact** (`3.5` surplus), and `Alg-2000` RL produced **`0` within-group variance across `21/21` steps**.

---

## Related Artifacts

- **Skills**:
  - [`verifier-gap-sign-pre-rl-audit`](../skills/verifier-gap-sign-pre-rl-audit/SKILL.md) — Companion pre-RL verifier audit (`arXiv:2611.21538`)
  - [`capability-matched-skill-adaptation`](../skills/capability-matched-skill-adaptation/SKILL.md) — Adapting distilled procedures to small-model executor bottlenecks (`arXiv:2610.33024`)
- **Rules**:
  - [`recursive-improvement.md`](../rules/recursive-improvement.md) — Verifier auditing, post-training trajectory curation, and OOD behavioral verification
  - [`skill-system-design.md`](../rules/skill-system-design.md) — Stronger-to-weaker distillation limits and decoupled semantic-vs-realization repair
