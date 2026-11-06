# TRAP: Trust-Responsive Runtime Authorization and Gradual-Degradation Blindness

> **Paper**: [Trust Responsive Runtime Authorization for Agentic AI with Empirical Characterization of Policy Behavior and Parameter Sensitivity](https://arxiv.org/abs/2611.06996) (Shihab et al., 2026)
> **Praxis source**: `src:2611-06996v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

Shihab et al. introduce and empirically characterize **TRAP (Trust-Responsive Authorization Policy)** (`v1.0.0`, commit `020373241154`), a runtime authorization controller that dynamically adjusts an autonomous agent's discrete authority level $a_t \in \{0, 1, 2, 3, 4, 5\}$ across time intervals $t$ based on three normalized runtime signals in $[0, 1]$: behavioural trust $T_t$, operational stability $S_t$, and contextual risk $R_t$. TRAP combines these signals into a scalar Authorization Readiness Score:

$$g_t = \mathrm{ARS}(T_t, S_t, R_t) = w_0 T_t + w_1 S_t - w_2 R_t$$

Using baseline weights $w = (0.5, 0.3, 0.2)$ and readiness band thresholds $\mathcal{B} = (0.20, 0.35, 0.50, 0.65, 0.80)$, TRAP applies an **asymmetric hysteresis transition rule**:
1. **Immediate Restriction**: If the single-step readiness change $d_t = g_t - g_{t-1} < -\theta_r$ (baseline $\theta_r = 0.10$), authority drops immediately to $a_t \leftarrow \min(a_{t-1}, \sigma(g_t))$ and the escalation persistence counter resets ($c_t \leftarrow 0$).
2. **Conservative Escalation**: Otherwise, if $g_t \ge \mathrm{up}(a_{t-1}) + \theta_e$ (baseline $\theta_e = 0.05$), $c_t$ increments by `1`; only when $c_t \ge k$ consecutive intervals (baseline $k = 3$) does authority rise by a single step ($a_t \leftarrow a_{t-1} + 1$, $c_t \leftarrow 0$).
3. **Hold**: In all other cases, $a_t \leftarrow a_{t-1}$ and $c_t \leftarrow 0$—meaning that if $g_t$ falls below the static band $\sigma(g_t)$ *without* exceeding the single-step drop threshold $-\theta_r$, the agent retains its prior higher authority level $a_{t-1}$.

Through matched Monte Carlo trace experiments (`exp003`, `exp009`, `exp010`, `exp011`, `exp012`), the paper demonstrates where asymmetric step-triggered hysteresis outperforms symmetric and single-signal baselines—and exposes a severe structural vulnerability under **gradual trust degradation**.

---

## Key Empirical Findings

### 1. Abrupt Degradation Performance (`exp010`, $n = 100$ Matched Traces)

Across $n = 100$ matched Monte Carlo traces of horizon $H = 100$ intervals (seed `42`, abrupt degradation onset at $t_F = 40$, recovery onset at $t_R = 60$), TRAP was compared against four baselines:

| Policy | Authorization Stability ($\mathrm{AS}$) | Restriction Responsiveness ($\mathrm{RR}$, intervals) | Recovery Time ($\mathrm{RT}$, intervals) | Protective Efficiency ($\mathrm{PER}$) | Progressive Recovery ($\mathrm{PRR}$) |
|:-------|:----------------------------------------|:------------------------------------------------------|:-----------------------------------------|:---------------------------------------|:--------------------------------------|
| **TRAP** | **`0.9699 ± 0.0064`** | **`0.00`** (`100/100` traces) | **`10.72`** (`[9.10, 12.49]`) | **`0.0000`** | `0.5550` (`[0.5256, 0.5844]`) |
| **Symmetric** | `0.9646 ± 0.0104` | `2.00` (`[2.00, 2.00]`) | `17.14` (`[15.38, 18.93]`) | `0.0000` | `0.4798` (`[0.4494, 0.5112]`) |
| **Trust-Only** | `0.9673 ± 0.0100` | `0.00` | `15.13` (`[12.71, 17.55]`) | `0.0096` | `0.5053` |
| **Risk-Only** | `0.9385 ± 0.0148` | `0.00` | `2.28` (`[1.98, 2.59]`) | `0.2405` | `0.7950` |
| **Static** | `1.0000 ± 0.0000` | N/A (`0/100` restricted) | N/A | `0.0000` | `0.0000` |

- **Paired TRAP vs. Symmetric advantages** ($n = 99$ paired traces for RT/PRR): TRAP improves stability by $\Delta \mathrm{AS} = +0.0053$ (`95% CI [+0.0033, +0.0072]`), eliminates the `2.00`-interval restriction delay ($\mathrm{RR} = 0.00$), and recovers `6.38` intervals faster ($\Delta \mathrm{RT} = -6.38$, `95% CI [-8.28, -4.57]`, a `37.5%` reduction), at the trade-off of a higher Progressive Recovery Ratio ($\Delta \mathrm{PRR} = +0.0707$, `95% CI [+0.0421, +0.1027]`, indicating more post-recovery escalations granted while $T_t < 0.60$).
- **Risk-Only failure mode**: Relying solely on risk ($R_t$) yields $\mathrm{PER} = 0.2405$, meaning **`24.05%` of authority escalations are erroneously granted during the active degradation window** ($t \in [40, 60)$).

### 2. Parameter Sensitivity (`exp011`, 13 Sweep Points / 10 Distinct Configurations)

- **Restriction Responsiveness ($\mathrm{RR}$)** remains `0.00` across all `10` configurations under abrupt degradation.
- **Recovery Time ($\mathrm{RT}$)** increases monotonically with escalation margin $\theta_e \in \{0.03, 0.05, 0.07\}$ (`9.18 -> 10.72 -> 12.57` intervals) and persistence requirement $k \in \{2, 3, 4\}$ (`9.48 -> 10.72 -> 11.74` intervals), is **completely invariant** to the restriction threshold $\theta_r \in \{0.05, 0.10, 0.15\}$ (`10.72` intervals across all three), and varies non-monotonically across weight profiles $w$ (`9.99` intervals at $(0.4, 0.3, 0.3)$ to `12.58` intervals at $(0.6, 0.2, 0.2)$).

### 3. Critical Failure Mode: Gradual-Degradation Blindness (`exp012`)

When the exact same total readiness drop (`~0.308` ARS units) is spread linearly over a ramp of $L \in \{1, 5, 10, 20\}$ intervals during the 20-interval degradation window:

- Under abrupt onset ($L = 1$), the single-step drop (`~0.308`) exceeds $\theta_r = 0.10$ on `100/100` traces, so TRAP restricts immediately (`100%` restriction rate) and holds **Excess-Authority Duration ($\mathrm{EAD}$)**—intervals where $a_t > \sigma(g_t)$—for only **`0.81` intervals** (`95% CI [0.38, 1.31]`), beating Symmetric (`9.79` intervals, $\Delta \mathrm{EAD} = -8.98$).
- Under a 5-step ramp ($L = 5$, mean step `~0.062`), TRAP restricts on **only `4/100` traces** (the `4` traces where stochastic noise pushed a single step past `0.10`; `0/96` on truly gradual traces where $\max \text{drop} \le 0.10$).
- Under 10-step and 20-step ramps ($L = 10$ and $L = 20$, where maximum single-step drops are `0.094` and `0.075`), TRAP restricts on **`0/100` traces (`0%`)**.
- Consequently, TRAP's Excess-Authority Duration explodes from `0.81` intervals ($L = 1$) to **`18.92` intervals** at $L = 5$ (`19.17` on the `96` non-triggered traces), **`18.15` intervals** at $L = 10$, and **`15.89` intervals** at $L = 20$—performing **worse than the Symmetric baseline** (`10.12`, `10.28`, and `9.85` intervals; paired differences $+8.80$, $+7.87$, and $+6.04$ intervals) and degrading to the **Static no-restriction policy** (`19.05`, `17.89`, and `15.41` intervals).

### 4. Hysteresis and Path-Dependence (`exp003`, `exp009`)

- In `4,000` ordinary traces per setting (`exp003`), **`46.40%` to `68.87%` of recurring signal conditions** $(T_t, S_t, R_t)$ map to $\ge 2$ distinct authority levels (`50.97%` at bin width `0.01`, `46.40%` at `0.02`).
- Across `50` target condition probes (`exp009`), the Hysteresis State Fraction reaches $\widehat{\mathrm{HSF}} = 1.000$ with a mean Path-Dependence Index of $\widehat{\mathrm{PDI}} = 3.000$ bands—meaning identical instantaneous telemetry $(T_t, S_t, R_t)$ routinely yields authority level `0` or level `3` depending solely on trajectory history.

---

## Practical Design Rules for Agent Authorization Controllers

1. **Never Gate Authority Restriction Solely on a Single-Step Derivative ($d_t < -\theta_r$)**:
   - A first-difference trigger is blind to slow-roll drift and adversarial salami-slicing where per-step trust decay stays below $\theta_r$. Always OR the single-step drop trigger with an **absolute band-ceiling violation** (e.g., restricting whenever $g_t < \mathrm{down}(a_{t-1}) - \theta_{\text{level}}$ for $m$ intervals or when a sliding-window cumulative drop $g_t - \max_{j \in [t-W, t-1]} g_j < -\theta_r$).
2. **Combine Trust, Stability, and Risk Signals Rather Than Relying on Risk Alone**:
   - Single-signal risk controllers grant `24.05%` of escalations during active degradation ($\mathrm{PER} = 0.2405$) because momentary risk dips mask collapsed behavioural trust.
3. **Log Both Instantaneous Signals and Hysteresis State (`a_{t-1}`, `c_t`) in Audit Trails**:
   - Because hysteresis creates a `3.000`-band path-dependence spread across `100%` of target conditions, auditing an authorization decision requires recording the prior authority level and persistence counter alongside $(T_t, S_t, R_t)$.

---

## Why Not a Skill?

This paper is an empirical characterization and sensitivity study of a specific mathematical transition function (TRAP `v1.0.0`) evaluated on synthetic Monte Carlo signal traces rather than a standalone, end-to-end engineering procedure. Most importantly, the paper's core empirical contribution (`exp012`) demonstrates that the baseline TRAP rule as formulated **fails completely on gradual degradation (`0%` restriction on $L \in \{10, 20\}$, `15.89–18.92` intervals of excess authority)**. Its high-value quantitative insights—combining multi-dimensional signals, using asymmetric persistence $k$ for escalation, and avoiding single-step derivative blindness—are directly captured as decision criteria in our security rules and paired with our multi-hop authorization skill.

---

## Related Artifacts

- **Rule**: [Agent Sandbox Safety](../rules/agent-sandbox-safety.md)
- **Rule**: [ADK Security and Evaluation](../rules/adk-security-and-evaluation.md)
- **Skill**: [Multi-Hop Delegation Authorization Propagation](../skills/multi-hop-delegation-auth-propagation/SKILL.md)
