# Defensive Analysis of State-Tracked Multi-Turn Jailbreak Escalation ($M^3$)

> **Source**: [arXiv:2610.31937](https://arxiv.org/abs/2610.31937) — *"$M^3$: A Multi-LLM System for Multi-Turn Jailbreaking as a Markov Decision Process"* (Oct 2026)
> **Praxis Source ID**: `src:2610-31937`
> **Tier**: Research Brief (Defensive Security Analysis)

---

## Summary & Threat Model

Conventional multi-turn red-teaming frameworks (`Crescendo`, `ActorAttack`, `GOAT`) append every conversational turn and target refusal into a growing prompt history. Over multiple turns, this raw history saturates the attacker's context window, dilutes attention with repeated refusals, and causes attack efficacy to plateau after the first `2–3` turns.

This paper demonstrates that formulating multi-turn adversarial dialogue as a **Markov Decision Process (MDP)** with **explicit, bounded-size state compression** ($M^3$) removes that plateau. By separating the adversarial loop into three modular roles—a **State Maintainer ($L_s$)** that compresses full dialogue history and past failed branches into a compact state summary $S_i$, a **Policy/Attacker ($L_a$)** that chooses between `Proceed` (advancing the semantic framing) and `Backtrack` (pruning a refused conversational turn up to $C$ retries), and an **Evaluator ($L_j$, `CompassJudge-32B`)** that outputs a continuous risk exposure score $R_i \in [0, 100]$—an adversary achieves steep, monotonic risk escalation across turns even when using a small, low-cost language model.

### Headline Empirical Findings Across 6 Target Models and 2 Benchmarks

The authors evaluate Low-Capacity (`LC`, `Mistral-Small-2402`) and High-Capacity (`HC`, `Mistral-Large-2402`) configurations across **6 target LLMs** (`GPT-4o`, `GPT-4o mini`, `Claude 3.5 Sonnet`, `Claude 3 Haiku`, `Llama3-70B-IT`, `Llama3-8B-IT`) on **Crescendo Tasks** (`15` tasks across `8` risk categories) and **HarmBench** (`90` tasks across `6` risk categories; `12` unified non-overlapping risk categories total), measuring single-attempt (`ASR@1`) and five-attempt (`ASR@5`) attack success rates:

| Benchmark | Method & Capacity | `GPT-4o` (`ASR@1 \| @5`) | `GPT-4o mini` (`ASR@1 \| @5`) | `Claude 3.5 Sonnet` (`ASR@1 \| @5`) | `Claude 3 Haiku` (`ASR@1 \| @5`) | `Llama3-70B-IT` (`ASR@1 \| @5`) | `Llama3-8B-IT` (`ASR@1 \| @5`) |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **Crescendo Tasks** | `ActorAttack` (`HC`) | `13.3% \| 20.0%` | `20.0% \| 40.0%` | `0.0% \| 0.0%` | `0.0% \| 0.0%` | `6.7% \| 13.3%` | `6.7% \| 13.3%` |
| **Crescendo Tasks** | `GOAT` (`HC`) | `33.3% \| 46.7%` | `26.7% \| 46.7%` | `20.0% \| 40.0%` | `6.7% \| 13.3%` | `13.3% \| 26.7%` | `20.0% \| 33.3%` |
| **Crescendo Tasks** | `Crescendo` (`HC`) | `6.7% \| 20.0%` | `13.3% \| 26.7%` | `13.3% \| 26.7%` | `0.0% \| 0.0%` | `13.3% \| 20.0%` | `6.7% \| 13.3%` |
| **Crescendo Tasks** | **`M^3` (`LC` - Mistral-Small)** | `26.7% \| 46.7%` | `33.3% \| 53.3%` | **`33.3% \| 53.3%`** | `26.7% \| 46.7%` | `26.7% \| 46.7%` | `26.7% \| 46.7%` |
| **Crescendo Tasks** | **`M^3` (`HC` - Mistral-Large)** | **`33.3% \| 60.0%`** | **`40.0% \| 53.3%`** | **`33.3% \| 53.3%`** | **`33.3% \| 66.7%`** | **`40.0% \| 60.0%`** | **`33.3% \| 60.0%`** |
| **HarmBench** | `ActorAttack` (`HC`) | `7.8% \| 13.3%` | `3.4% \| 11.2%` | `1.1% \| 2.2%` | `2.2% \| 5.6%` | `3.3% \| 7.8%` | `3.3% \| 6.7%` |
| **HarmBench** | `GOAT` (`HC`) | `10.0% \| 15.6%` | `4.4% \| 8.9%` | `3.3% \| 6.7%` | `4.4% \| 10.0%` | `8.9% \| 15.6%` | `7.8% \| 14.4%` |
| **HarmBench** | `Crescendo` (`HC`) | `4.4% \| 6.7%` | `2.2% \| 2.2%` | `1.1% \| 2.2%` | `1.1% \| 2.2%` | `4.4% \| 7.8%` | `3.3% \| 5.6%` |
| **HarmBench** | **`M^3` (`LC` - Mistral-Small)** | `16.7% \| 31.1%` | **`23.3% \| 36.7%`** | `7.8% \| 20.0%` | `14.4% \| 27.8%` | `15.6% \| 31.1%` | `14.4% \| 28.9%` |
| **HarmBench** | **`M^3` (`HC` - Mistral-Large)** | **`24.4% \| 42.2%`** | **`28.9% \| 43.3%`** | **`11.1% \| 27.8%`** | **`21.1% \| 37.8%`** | **`22.2% \| 38.9%`** | **`20.0% \| 35.6%`** |

### Key Analytical Findings

1. **Small state-tracked attackers outperform large full-history attackers by up to `+26% ASR@1` and `+34% ASR@5`**:
   - Simply replacing raw conversation history with a Markov state summary $S_i$ and backtracking allows a small attacker (`Mistral-Small-2402`, $M^3$-`LC`) to beat high-capacity baselines (`Mistral-Large-2402`, `HC`) by **up to `+26%` in `ASR@1` and `+34%` in `ASR@5`** (for example, on HarmBench `GPT-4o mini`, $M^3$-`LC` achieves `23.3% | 36.7%` vs `GOAT-HC` at `4.4% | 8.9%` and `Crescendo-HC` at `2.2% | 2.2%`; on Crescendo Tasks `Claude 3 Haiku`, $M^3$-`LC` achieves `26.7% | 46.7%` vs `0.0%` for `ActorAttack-HC`/`Crescendo-HC` and `6.7% | 13.3%` for `GOAT-HC`).
   - At matched high capacity (`HC`), $M^3$ improves overall success by **up to `+33%` in `ASR@1` and `+53%` in `ASR@5`** (e.g., `66.7%` vs `13.3%` on `Claude 3 Haiku`).
2. **Monotonic multi-turn risk escalation without early saturation**:
   - Trajectory risk exposure curves ($R_i \in [0, 100]$ across turns $i = 1 \dots N$) show that baseline attacks flatten after turn `2` or `3` as context length grows, whereas $M^3$ maintains a positive risk slope through turn `5+` because failed refusal turns are pruned via `Backtrack` and summarized into negative constraints inside $S_i$.
3. **Uniform vulnerability across all 12 risk categories (Gini index reduction of up to `4.82`)**:
   - Without relying on any predefined attack taxonomy or human-written jailbreak templates, $M^3$ reduces cross-category ASR inequality (Gini index $\downarrow$) by **up to `4.82` points** (`4.24–6.22` for $M^3$-`HC` and `5.39–7.05` for $M^3$-`LC`, compared to `6.20–10.76` for baselines), demonstrating that state-tracked escalation exploits structural multi-turn context drift rather than category-specific keywords.

---

## Defensive Architecture & Mitigation Requirements

1. **Deploy symmetric state-compressing safety monitors across multi-turn sessions**:
   - As the authors highlight in their defensive discussion, a defender that evaluates only the current turn—or that passes raw, uncompressed multi-turn dialogue history into a guardrail—suffers from the exact same context dilution that handicaps stateless attackers. Multi-turn guardrails should maintain a **compact defensive risk state $D_i$** that tracks cumulative semantic intent, partial information disclosures across turns, and cumulative risk exposure $R_i$.
2. **Persist refusal and edit/rollback telemetry across conversational branches**:
   - In $M^3$, the `Backtrack` operator prunes a refused turn $(q_i, r_i)$ from the target LLM's visible dialogue context while recording the refusal trigger in the attacker's state $S_i$ so the next query skirts the boundary. When an application or API allows users/agents to edit, regenerate, or rewind prior conversational turns after a refusal, the **session-level safety monitor must retain an immutable append-only log of refused attempts** across branches and elevate scrutiny on subsequent turns.
3. **Restore original safety constraints as dialogue depth increases**:
   - Because state-tracked adversaries incrementally shift benign framing toward harmful fulfillment over `4–5+` turns, combine compact trajectory risk tracking with periodic **historical safety-constraint restoration** (see [`historical-constraint-restoration`](../skills/historical-constraint-restoration/SKILL.md)) whenever cumulative session risk $R_i$ crosses an intermediate warning threshold.

---

## Why Not a Skill?

Per Praxis content standards, multi-turn jailbreak generation algorithms are analyzed strictly for defensive architecture and guardrail design rather than packaged as offensive procedures. The actionable defensive procedures for countering multi-turn drift and context-window erosion are already captured in [`historical-constraint-restoration`](../skills/historical-constraint-restoration/SKILL.md) and [`black-box-trajectory-risk-monitoring`](../skills/black-box-trajectory-risk-monitoring/SKILL.md).

---

## Cross-References

- **Related Rules**: [`agent-sandbox-safety`](../rules/agent-sandbox-safety.md), [`agent-evaluation-quality`](../rules/agent-evaluation-quality.md)
- **Related Skills**: [`historical-constraint-restoration`](../skills/historical-constraint-restoration/SKILL.md), [`black-box-trajectory-risk-monitoring`](../skills/black-box-trajectory-risk-monitoring/SKILL.md), [`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md)
