# SentryBench: Cost-Sensitive Robustness of Public-Safety Tool Agents

> **Paper**: [SentryBench: A Cost-Sensitive Benchmark for Adversarial Robustness of Tool-Using LLM Agents in Public-Safety Deployments](https://arxiv.org/abs/2610.34535) (Yusuf et al., Oct 2026)
> **Praxis source**: `src:2610-34535`

## Why Not a Skill?

This paper introduces a domain benchmark (`SentryBench`, 190 public-safety scenarios) and a formal two-sided asymmetric cost functional $H(\pi)$ evaluating how prompt-level caution and a lightweight heuristic trust gate (`TGCC`) trade off attack success against over-refusal on real emergencies. The `TGCC` defense itself combines provenance spotlighting, a regex/keyword heuristic detector ($s(x)$), and human-escalation routing — patterns already covered in greater procedural depth by [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md), [`mcp-decode-provenance-binding`](../skills/mcp-decode-provenance-binding/SKILL.md), and [`unified-capability-gateway`](../skills/unified-capability-gateway/SKILL.md). Its primary value to Praxis is its formal proof and empirical demonstration that naive "when in doubt, refuse/escalate" system prompts catastrophically increase net deployment harm in high-stakes tool agents.

---

## Core Concept

Standard agent safety benchmarks treat adversarial Attack Success Rate (ASR) as the sole primary metric, implicitly assigning zero cost to **over-refusal** (failing to act on a genuine urgent task). In public-safety and emergency-response deployments (911 dispatch, disaster triage, public alerting), refusing or delaying action on a genuine emergency carries severe real-world harm ($c_i^{FN}$), just as executing an attacker-injected false public alert or unauthorized citizen-record query carries false-positive / adversarial harm ($c_i^{FP}$).

Yusuf et al. formalize expected **deployment harm** over scenario set $S$ ($|S| = N$) with per-scenario false-negative cost $c_i^{FN}$ (under-reaction $u_i \in \{0,1\}$) and false-positive cost $c_i^{FP}$ (over-reaction $o_i \in \{0,1\}$):
$$H(\pi) = \frac{1}{N} \sum_{i \in S} \left( c_i^{FN} u_i + c_i^{FP} o_i \right)$$

They construct **SentryBench**, comprising **190 scenarios** derived from four real public datasets (`prompt-injections` 203/546, `jailbreak-classification` 310/600, `disaster_response` 1550/2000, and `911-transcripts` 249/250) across **6 scenario families** and **6 mocked sandbox tools** (`send_public_alert`, `dispatch_unit`, `query_citizen_record`, `escalate_to_human`, `update_incident_log`, `query_historical_incidents`), scored deterministically from the tool-call ledger without an LLM judge:
- **Family A (`benign-urgent`, $n=40$)**: Genuine emergencies requiring immediate dispatch/alerting (measures **Over-Refusal Rate, ORR**).
- **Family B (`benign-ambiguous`, $n=38$)**: Non-emergency or incomplete reports where dispatching/alerting is an **Over-Reaction (FP)**.
- **Family C (`adversarial-suppress`, $n=38$)**: Real emergencies containing an injected payload attempting to suppress dispatch/alerting.
- **Family D (`adversarial-alert`, $n=30$)**: Non-emergencies with injections attempting to trigger a false `send_public_alert`.
- **Family E (`adversarial-records`, $n=24$)**: Injections attempting unauthorized `query_citizen_record` exfiltration.
- **Family F (`adversarial-poison`, $n=20$)**: Multi-step scenarios where a mid-chain tool return (`query_historical_incidents`) injects instructions to suppress response or exfiltrate records.

The authors prove three structural theorems and evaluate **840 scored episodes** across **3 frontier models** (`claude-haiku-4-5` on all 190 scenarios = 570 episodes; `claude-sonnet-4-5` and Azure `gpt-5` on a 45-scenario stratified subset = 270 episodes) and **3 defense conditions**:
1. **`none`**: Baseline public-safety dispatcher prompt.
2. **`caution`**: Naive defensive system prompt (*"when in doubt, do not act; escalate to a human operator"*). **Theorem 1** proves that `caution` strictly increases net deployment harm ($H(\pi_c) - H(\pi_0) = \frac{1}{N}\sum_{i \in R} c_i^{FN} - \Delta^- \ge 0$) whenever the false-negative cost of newly refused urgent emergencies $R \subseteq B_u$ exceeds the adversarial harm averted $\Delta^-$.
3. **`tgcc` (Trust-Gating for Consequential Calls)**: Combines (i) provenance spotlighting delimiters on untrusted fields, (ii) a deterministic injection heuristic score $s(x)$ over untrusted inputs and tool returns (threshold $\theta = 1$), and (iii) a gate that routes consequential calls (`send_public_alert`, `dispatch_unit`, `query_citizen_record`) to `escalate_to_human` **if and only if** $s(x) \ge 1$ (or an over-broad citizen-record query has $s(x) > 0$). **Theorem 2** proves `tgcc` adds **zero over-refusal overhead on clean inputs** ($\mathrm{ORR}_{\mathrm{gate}} \le \mathrm{ORR}_{\mathrm{base}}$ when $s(x)=0$), and **Theorem 3** bounds residual ASR strictly by detector recall ($s_i < \theta$).

### Key Findings

| Model | Defense | Attack Success Rate (ASR $\downarrow$) | Over-Refusal Rate on Real Emergencies (ORR $\downarrow$) | Benign Over-Reaction (FP $\downarrow$) | Adversarial Containment ($\uparrow$) | Net Deployment Harm $H(\pi)$ ($\downarrow$) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Claude Haiku 4.5** ($N=190$) | `none` | 2.7% | 37.5% | 0.0% | 50.9% | 0.85 |
| **Claude Haiku 4.5** ($N=190$) | `caution` | 1.8% (−0.9 pp) | **65.0%** (+27.5 pp) | 0.0% | 62.5% | **1.33** (Worst) |
| **Claude Haiku 4.5** ($N=190$) | `tgcc` | **0.0%** (−2.7 pp) | **35.0%** (−2.5 pp) | 0.0% | **75.9%** | **0.66** (Best) |
| **Claude Sonnet 4.5** ($N=45$) | `none` | 3.7% | 44.4% | 0.0% | 74.1% | 1.00 |
| **Claude Sonnet 4.5** ($N=45$) | `caution` | **0.0%** (−3.7 pp) | **100.0%** (+55.6 pp) | 0.0% | 100.0% | **1.80** (Worst) |
| **Claude Sonnet 4.5** ($N=45$) | `tgcc` | 3.7% (1 miss, C-008) | **44.4%** (+0.0 pp) | 0.0% | 92.6% | **1.00** (Tied Best) |
| **Azure GPT-5** ($N=45$) | `none` | 0.0% | 62.5% (66.7% sys.) | 0.0% | 81.2% | 1.00 |
| **Azure GPT-5** ($N=45$) | `caution` | 0.0% (−0.0 pp) | **100.0%** (100.0% sys.) | 0.0% | 93.8% | **1.60** (Worst) |
| **Azure GPT-5** ($N=45$) | `tgcc` | **0.0%** (−0.0 pp) | **37.5%** (44.4% sys.) | 0.0% | **91.7%** | **0.60** (Best) |

- **Naive "refuse-more" caution drives over-refusal to 100% on 2 of 3 models for $\le 3.7\text{ pp}$ ASR reduction**: Adding a cautionary system prompt reduces ASR by only **0.9 pp** on Haiku, **3.7 pp** on Sonnet, and **0.0 pp** on GPT-5, while driving Over-Refusal Rate on genuine urgent emergencies (`Family A`) to **65.0%** on Haiku and **100.0%** on both Sonnet 4.5 and GPT-5 — producing the **highest (worst) net deployment harm $H(\pi)$ on every single model** (**1.33, 1.80, and 1.60**).
- **Selective trust gating (`TGCC`) achieves the lowest deployment harm without inflating over-refusal**: Because `TGCC` gates consequential tool calls only when the input/tool-return injection detector fires ($s(x) \ge 1$), it reduces ASR to **0.0%** on Haiku and GPT-5 while keeping ORR at or below baseline (**35.0%** vs. 37.5% on Haiku; **44.4%** vs. 44.4% on Sonnet; **37.5%** vs. 62.5% on GPT-5, as provenance spotlighting reduces ambiguity on benign emergencies), cutting net harm $H(\pi)$ to **0.66** on Haiku and **0.60** on GPT-5.
- **Emergency-suppression attacks (`Family C`) are the dominant failure mode**: All **7** genuine adversarial successes across the entire 840-episode study occurred in `Family C` (`adversarial-suppress`), where an attacker appends a cancellation/false-alarm injection to a real emergency report so the agent fails to dispatch help. Neither `Family D` (false public alert) nor `Family E` (records exfiltration) succeeded on any frontier model.
- **Surface-form bias and provider content filters inflate emergency refusal**:
  - On Haiku (`none`), over-refusal is **18%** on explicit 911 dialogue transcripts but jumps to **83%** on terse, informal disaster-response text messages (`disaster_response` split), even when both describe life-threatening emergencies.
  - On Azure GPT-5, the platform's upstream HTTP 400 content filter blocked **11 to 15 episodes per condition** (including genuine violent/medical 911 transcripts), raising system-level ORR from **62.5% to 66.7%** under `none` and from **37.5% to 44.4%** under `tgcc`.

---

## Relevance to Praxis

- **Asymmetric cost accounting and selective trust gates (`rules/agent-sandbox-safety.md`, `rules/agent-evaluation-quality.md`)**: Directly complements *"DON'T: Evaluate safety guardrails on attack success rate alone without measuring benign utility collapse"* (`arXiv:2609.26176`, `arXiv:2610.06122`). Never harden a high-stakes tool agent by adding global `"when in doubt, do not act"` prompt instructions; instead, gate consequential tool calls conditionally on an explicit input-taint or anomaly signal ($s(x) \ge \theta$) so clean urgent tasks incur zero additional refusal penalty.
- **Test suppression (under-reaction) attacks alongside unauthorized-action (over-reaction) attacks**: Red-teaming suites for tool-using agents typically test only whether an injection can *trigger* a forbidden tool call (`Family D/E`). `SentryBench` demonstrates that **suppressing a required tool call** (`Family C`, 7/7 observed failures) is much easier for an attacker because it exploits the model's pre-existing tendency toward cautious inaction.
