---
name: self-evolution-stopping-rule
description: >
  Decide online when to stop a self-evolving loop (prompt, skill,
  harness or program evolution) and which earlier artifact to return.
  Bet against "proposals still gain at least ε per item" using the
  per-item candidate-vs-incumbent outcomes the loop already produces,
  restart a wealth process every round, alarm when the largest wealth
  crosses 1/δ_FA, and return the incumbent just before the estimated
  change point. Replaces fixed round budgets; the returned artifact
  still goes through the acceptance gate.
  Derived from "When Is Enough Enough in Self-Evolving LLM Systems?"
  (arXiv:2610.04756).
source: https://arxiv.org/abs/2610.04756
---

# Self-Evolution Stopping Rule (Restart E-Detector)

Use this skill when a propose → evaluate → keep loop runs against a
fixed validation set with binary per-item outcomes and you are paying
for rounds after improvement has stopped, or want to avoid the late,
degenerate artifacts that long runs accept.

## When to Use

- The loop scores both the incumbent and each round's candidate on the
  same n validation items (pass/fail per item).
- You currently run to a fixed round or token budget.
- Score plateaus are ambiguous: a greedy gate leaves the incumbent's
  score flat when it rejects candidates, so a flat curve says nothing
  about proposal quality.
- You can wrap the loop without changing the evolution algorithm.

This skill decides when to stop and which artifact to output. It does
not decide what is kept. It defers to "DO: Pass every self-modification
through one acceptance gate" (`rules/recursive-improvement.md`): the
returned artifact still needs behavioural evidence, held-out tasks, no
regression beyond the gate's noise margin δ on previously-correct
cases, and the strict negative security testbed. To avoid a name clash
with that δ, this skill writes the paper's false-alarm parameter as
**δ_FA**.

## Core Insight

Watch proposal quality, not the incumbent's score. For each round t and
item i, take the paired outcome X_{t,i} = c_{t,i} − b_{t,i} ∈ {−1, 0, +1}
(candidate minus incumbent), whether or not the candidate is accepted.
Evolution is worth continuing while the expected per-item proposal gain
E[Z_t | F_{t−1}] ≥ ε, where Z_t is the round average. Test that
hypothesis with a betting martingale: each item pays G = ε − X, so
items below ε grow the wealth. Start a fresh bettor every round so
early gains don't have to be paid back before a later stall shows.
Alarm when the best bettor's wealth crosses 1/δ_FA. The bettor started
nearest the transition ends up richest, which estimates when useful
improvement stopped.

**Evidence** (SkillOpt with DeepSeek V4 Flash, ε = 0.01, δ_FA = 0.05,
aGRAPA betting, 40-round full budget; unseen-test comparison is the
returned artifact vs the full run's selection on the same examples):

| Benchmark | Tokens saved | Δacc (pp) | Token efficiency vs full run |
|---|---|---|---|
| SearchQA | 91.6% (alarm at round 4) | +0.43 | 12.9× |
| GSM8K | — | −0.80 | 9.3× |
| OfficeQA | — | −1.16 | 1.8× |

Savings across the three were 48.4–91.6%; all three Δacc 95% CIs
include zero. SearchQA: 82.43% vs 82.00% unseen-test accuracy.

- **Negative control**: SpreadsheetBench kept improving (validation
  0.375 → 0.70 over 16 rounds, gains as late as round 11); no alarm.
- **Degenerate late artifact avoided**: on LiveMath the full run would
  accept, at round 16, a skill that answers "A" without reasoning,
  exploiting a skewed answer distribution. The detector alarmed at
  round 8, estimated ν̂ = 2 and returned the round-1 artifact. It does
  not detect reward hacking; it stopped because real gains had ended.
- **Transfer**: with GEPA instead of SkillOpt, alarms at rounds 5
  (SearchQA, 73.8% saved) and 6 (GSM8K, 65.5% saved; GEPA tokens
  estimated). Across DeepSeek V4 Flash, Qwen3-32B and GPT-5.6 Luna,
  savings were 68.9–92.6%, and slower-improving models stopped later
  (Qwen3-32B at round 8 on GSM8K vs round 4 for the others).

---

## Procedure

### 0. Set Up

- Freeze the validation set D_val (n items). Keep a separate unseen
  test set for reporting, as the gate requires.
- Choose ε, the smallest expected per-item proposal gain worth another
  round (paper default 0.01), and δ_FA (default 0.05). Smaller δ_FA
  means a later, more conservative alarm.
- Check detectability before running. On a pure plateau, the rounds
  needed to alarm are about

  ```
  T_need ≈ (log(1/δ_FA) + log|Λ|) / (n · λ_max · ε)
  ```

  For n = 200, λ_max = 0.4, ε = 0.01, δ_FA = 0.05 and |Λ| = 3 this is
  about 5 rounds (our arithmetic from the paper's formula). The
  resolvable ε scales as 1/n: halving n doubles T_need. If T_need is
  near your budget, the detector will stay silent; that is a loss of
  power, not of validity.

### 1. Record Paired Outcomes Every Round

For each round t, log b_{t,i} (incumbent) and c_{t,i} (candidate) for
every item, then X_{t,i} = c_{t,i} − b_{t,i}. Do this for rejected
candidates too. For loops that don't do a full validation pass (e.g.
GEPA's Pareto selection), read per-item correctness from the saved
validation subscore matrix.

### 2. Run One Wealth Process per Start Round

At every round s, start a bettor with wealth W^{(s)} = 1. Each round
u ≥ s, multiply each live bettor's wealth over items:

```
W_u^(s) = W_{u-1}^(s) · Π_i (1 + λ_{s,u} · (ε − X_{u,i}))
```

λ_{s,u} must be fixed before round u's outcomes are seen and lie in
[0, ½]. Two choices:

- **Fixed mixture**: run one process per λ ∈ Λ = {0.1, 0.2, 0.4} and
  average them with uniform weights. No online estimation.
- **aGRAPA** (paper's main results): from rounds s..u−1, take
  Z̄ = mean round-average gain and q̄ = mean discordant rate
  ((n₀₁ + n₁₀)/n). Set μ̂ = ε − Z̄, σ̂² = q̄ − Z̄², and
  λ = min(max(μ̂ / (σ̂² + μ̂²), 0), ½) (λ = 0 if the denominator is 0;
  a fixed λ₀ ∈ (0, ½] on the first round).

In the paper both schemes gave the same ν̂ in every matched setting
and alarm rounds differed by at most a few rounds.

### 3. Alarm

```
M_t = max_{s ≤ t} W_t^(s)
stop at the first t with M_t ≥ 1/δ_FA
```

Under the pre-change condition and conditional independence of items
within a round, this gives an average run length to false alarm of at
least 1/δ_FA.

### 4. Pick the Output Artifact

Estimate the change point as the start round whose wealth is largest
at the alarm: ν̂ = argmax_s W_{T_alarm}^(s). Return θ_{ν̂−1}, the
incumbent just before improvement stopped being worthwhile, not the
latest incumbent. Log T_alarm, ν̂, and tokens spent through the alarm.

### 5. Hand Off to the Acceptance Gate

Run θ_{ν̂−1} through the full acceptance gate. Report the returned
artifact against the full-run or latest incumbent on the unseen test
set as a paired difference with a confidence interval, not as two
separate accuracies.

---

## Environment Caveats

- **Binary outcomes only.** The method needs per-item pass/fail on a
  shared validation set. Graded or rubric scores are future work.
- **Small validation sets are slow.** Going from n = 200 to n = 100
  moved alarms from round 4 to 6 (SearchQA) and 4 to 5 (GSM8K), still
  saving over 85% of tokens. LiveMath (n = 18) and OfficeQA (n = 24)
  ran with very small sets; treat their numbers as indicative.
- **Assumes a persistent stall.** The model assumes once proposals fall
  below ε they stay there. A loop that plateaus and then improves again
  (as SpreadsheetBench almost did) may be stopped early if the plateau
  is long enough. Raise n or lower ε if late gains matter.
- **Localization guarantee is for fixed λ.** The paper proves change-point
  localization only for a common fixed λ; aGRAPA is covered for
  stopping validity, not localization.
- **Not a reward-hacking detector.** It stops on lack of real progress.
  Keep the gate's held-out and behavioural checks.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Stopping on a flat score curve | Watching incumbent accuracy | Bet on paired candidate-vs-incumbent outcomes (step 1) |
| Early gains mask a later stall | One bettor from round 1 | Restart a bettor every round (step 2) |
| Invalid bet | λ chosen after seeing round outcomes, or > ½ | Predictable λ in [0, ½] (step 2) |
| Returning a degraded late artifact | Output = latest incumbent | Return θ_{ν̂−1} (step 4) |
| Detector never fires | Small n or tiny ε | Check T_need up front (step 0) |
| δ confusion | Paper's δ vs gate noise margin δ | Name the false-alarm level δ_FA |

## Cross-References

- `rules/recursive-improvement.md`: "DO: Stop self-evolution loops on
  sequential evidence, not a fixed round budget" (this skill's rule),
  "DO: Pass every self-modification through one acceptance gate",
  "DO: Measure acceptance-gate errors in both directions".
- [`decision-only-sequential-acceptance`](../decision-only-sequential-acceptance/SKILL.md):
  the per-round promote/reject test on a reused set. This skill uses
  the same paired outcomes to decide when the whole loop should end.

> Source: When Is Enough Enough in Self-Evolving LLM Systems?
> (arXiv:2610.04756), Oct 2026. Praxis source: src:2610-04756
