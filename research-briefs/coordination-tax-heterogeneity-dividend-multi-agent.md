# The Coordination Tax and the Heterogeneity Dividend: Break-Even Conditions for Multi-Agent LLM Pipelines

> **Source**: [arXiv:2610.37700](https://arxiv.org/abs/2610.37700) — Andreas Zettl, Diego Gosmar (VoiceInteroperability.ai, Linux Foundation AI & Data, 2026-10-25)  
> **Praxis ID**: `src:2610-37700` | **Code**: `https://github.com/azettl/coordination-tax-harness`

---

## Core Contribution

Practitioners frequently debate whether multi-agent pipelines built on interoperability protocols like the Open Floor Protocol (`OFP`) or `A2A` are slower and more expensive than a single frontier model call. Zettl and Gosmar prove that this question is ill-posed unless **role decomposition**, **protocol transport**, and **model heterogeneity** are separated. They derive a closed-form economic model of the **coordination tax** versus the **heterogeneity dividend** and measure every parameter across `2,430` runs (`135` `HumanEval` and `ClassEval` tasks $\times$ `6` architectures $\times$ `3` rounds) using `Claude Opus 5.5` (`\$4/\$20` per 1M tokens) and `Claude Haiku 5.5` (`\$0.10/\$0.50` per 1M tokens, price ratio $r = 0.025$).

Four headline findings emerge:
1. **The interoperability protocol tax is negligible (`0.11%` of wall time)**: Direct timestamping across `2,430` `OFP` handoffs shows `OFP` adds a median of **`7.2 ms` per handoff** (`20.5 ms` per 3-stage pipeline, `19.5 kB` of envelopes, `1.01x` cost/time vs raw in-process API calls).
2. **Hard feasibility bound ($\alpha < 1/r$) and break-even threshold ($f^\star$)**: If decomposing a single call into $k$ stages inflates total output tokens by factor $\alpha$ and routes fraction $f$ of tokens to a cheap model at price ratio $r$, decomposition is cheaper than one strong call iff:
   $$f > f^\star = \frac{\alpha - 1}{\alpha(1 - r)}, \qquad \text{which is impossible for any } f \le 1 \text{ once } \alpha \ge \frac{1}{r}.$$
3. **Cheap-model reasoning inflation breaks naive cost forecasts (`-19%` error)**: Uniform 3-role decomposition (`planner` $\to$ `coder` $\to$ `reviewer`) costs **`3.22x`** as much as a single `Opus 5.5` call, takes **`3.24x`** as long, and improves accuracy by **`0` (`-1.5` pp)**. Assigning `planner` and `reviewer` to `Haiku 5.5` (`D`) cuts pipeline cost to `0.39x` of the uniform pipeline (`C`), but still leaves `D` **`1.27x` more expensive, `2.60x` slower, and `-8.1` pp less accurate** (`-10.6` pp on `ClassEval`) than a single `Opus 5.5` call — because `Haiku 5.5` spends `37.6%` of its output on reasoning tokens (vs `21.9%` for `Opus 5.5`), inflating $\alpha_{\text{out}}$ from `2.95` to `4.10` (a `1.32x` volume factor that offsets the `0.30x` price factor).
4. **Route whole tasks, not pipeline roles**: On self-contained coding tasks, per-task routing between a single strong call and a single cheap call (`Oracle Router`) solves **`94.3%`** of runs at **`\$0.0098` per solved task** (half of `Opus 5.5`'s `\$0.0198`/solved), strictly dominating every multi-agent role pipeline without paying decomposition or protocol overhead.

---

## Analytical Equations

- **Full Input + Output Cost Ratio**:
  $$\frac{C_k}{C_1} = \rho\,\alpha_{\text{in}}\left[(1 - f_{\text{in}}) + f_{\text{in}} r_{\text{in}}\right] + (1 - \rho)\,\alpha_{\text{out}}\left[(1 - f_{\text{out}}) + f_{\text{out}} r_{\text{out}}\right]$$
  where $\rho = p_{\text{in}}^s I_1 / C_1$ is the input share of single-call cost, and $\alpha_{\text{in}}$ is typically larger than $\alpha_{\text{out}}$ (`4.89` vs `2.95` in `C`, `5.13` vs `4.10` in `D`) because context is re-sent at every stage.
- **Latency Break-Even Condition**:
  $$f > \frac{\alpha - 1 + \theta}{\alpha(1 - w)}, \qquad \text{feasible only if } \alpha < \frac{1 - \theta}{w}$$
  where $w = s_s / s_c$ is the strong/cheap throughput ratio (`115 / 244 = 0.47`) and $\theta = \Omega s_s / O_1$ is the fixed multi-stage prefill + protocol overhead ($H\tau$). Because $\theta > 0$ does not shrink when roles move to a faster model, latency parity is strictly harder to reach than cost parity.
- **Misrouting & Unrefunded Retry Condition**:
  $$f > \frac{\alpha - 1}{\alpha\left(1 - r + q(r - \kappa)\right)}, \qquad \text{dividend vanishes at } q = \frac{1 - r}{\kappa - r}$$
  where $q$ is the cheap-model misroute failure rate (`q = 28.8%` observed for zero-shot router `R`) and $\kappa > 1$ is the retry cost multiplier.

---

## Key Empirical Results (`135` Tasks, `2,430` Runs)

### 1. Accuracy, Cost, and Latency by Tier (`Table 2`)

| Condition | `HumanEval` (`50`) pass@1 | `HumanEval` \$/solved | `HumanEval` Wall (s) | `ClassEval` (`85`) pass@1 | `ClassEval` \$/solved | `ClassEval` Wall (s) | `ClassEval` Tokens in / out (reas.) |
|:----------|:-------------------------:|:---------------------:|:--------------------:|:-------------------------:|:---------------------:|:--------------------:|:-----------------------------------:|
| `A`: Single `Opus 5.5` | `100.0%` | `\$0.0063` | `2.8 s` | **`90.2%`** | `\$0.0287` | `8.4 s` | `893 / 1114 (244)` |
| `A'`: Single `Haiku 5.5` | `98.7%` | **`\$0.00019`** | **`1.7 s`** | `52.5%` | **`\$0.0020`** | **`6.4 s`** | `893 / 1942 (771)` |
| `R`: Zero-Shot Router | `98.7%` | `\$0.00045` | `2.7 s` | `55.3%` | `\$0.0090` | `7.7 s` | `1847 / 1860 (725)` |
| `B`: 3-Role Plain (`Opus` $\times 3$) | `100.0%` | `\$0.0279` | `12.8 s` | `89.4%` | `\$0.0875` | `26.2 s` | `4257 / 3060 (666)` |
| `C`: 3-Role `OFP` (`Opus` $\times 3$) | `100.0%` | `\$0.0279` | `13.0 s` | `87.8%` | `\$0.0898` | `26.6 s` | `4263 / 3092 (693)` |
| `D`: 3-Role `OFP` Mixed (`H-O-H`) | `100.0%` | `\$0.0074` | `9.1 s` | `77.3%` | `\$0.0429` | `20.8 s` | `4633 / 4381 (1536)` |

### 2. Paired Contrasts Across All `135` Tasks (`Table 3`)

- **Decomposition tax (`B vs A`)**: `3.20x` cost (`[3.07, 3.35]`), `3.20x` wall time (`[3.06, 3.35]`), `-0.5` pp pass@1 ($p = 0.31$).
- **Protocol tax (`C vs B`)**: `1.01x` cost (`[0.99, 1.02]`, $p = 0.36$), `1.01x` wall time (`+0.29 s`, $p = 0.15$), `-1.0` pp pass@1 ($p = 0.38$).
- **Heterogeneous role assignment (`D vs C` & `D vs A`)**: Cuts cost vs `C` to `0.39x` (`0.30` price factor $\times$ `1.32` volume factor) and wall time to `0.80x`, but loses `-6.7` pp pass@1 overall (`-10.6` pp on `ClassEval`, $p = 0.002$) because the cheap `reviewer` has the last word on the graded code, leaving `D` at `1.27x` cost, `2.60x` wall time, and `-8.1` pp pass@1 relative to single call `A`.

---

## Why Not a Skill?

This paper is an econometric and empirical benchmarking study establishing closed-form cost/latency feasibility bounds ($\alpha < 1/r$, $f > f^\star$) rather than a procedural skill executed by an agent. Its formulas and empirical findings directly belong in `output/rules/multi-agent-coordination.md`.
