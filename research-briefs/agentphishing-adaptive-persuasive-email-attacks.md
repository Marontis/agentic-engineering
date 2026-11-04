# AgentPhishing: A Benchmark of LLM Email Agents Under Adaptive Persuasive Attack

> **Source**: [arXiv:2610.31404](https://arxiv.org/abs/2610.31404) — *AgentPhishing: A Benchmark of LLM Email Agents Under Adaptive Attack* (`src:2610-31404`)
> **Authors**: AgentPhishing Team (2026)
> **Category**: Agent Security & Defensive Evaluation / Adaptive Social-Engineering Benchmarks

---

## Executive Summary

Most evaluations of LLM email agents test either **syntax-level prompt injection** (`IGNORE PREVIOUS INSTRUCTIONS`, chat-template spoofing) or **static public phishing corpora** authored for human targets. **AgentPhishing** evaluates a distinct, realistic threat surface: **purely persuasive, workflow-plausible workplace emails** that contain *no* prompt-injection overrides or exploit artifacts, where an email agent must triage an inbox mixed with benign messages and choose both a handling action (`report`, `archive`, `ignore`, `unsubscribe`, or `reply`) and whether to comply with embedded requests (clicking a link, supplying internal data, or drafting an unsafe reply).

Across **6 primary target agents** (`Qwen3.7-Plus`, `Kimi-K2.5`, `Grok-4.20`, `GPT-5.4`, `Claude-Sonnet-5`, `Gemini-3.5-Flash`), **every single agent achieves 100% phishing detection ($D = 1.000$) and 0% malicious-request compliance ($C = 0.000$) on static public phishing datasets** (`Seven Phishing Email Datasets`), yet adaptive persuasive skill optimization (**PhishOpt**) drives severe failures on 4 of the 6 agents (e.g., `Qwen3.7-Plus` susceptibility $J$ jumps from **`0.12` to `0.95`**, with detection dropping to **`0.000`** and compliance rising to **`0.833`**). Furthermore, a **universal persuasive skill** synthesized from Cialdini persuasion-principle telemetry transfers zero-shot to **9 held-out email agents**: while 5 frontier models remain resilient (mean $J \le 0.1036$), **4 of the 9 held-out agents exhibit `< 10%` phishing detection (`0.00%–9.09%`) and `> 45%` malicious-request compliance (`45.45%–90.91%`)**. Crucially for defenders, the vulnerability is driven by **Commitment and Consistency framing** (continuing an apparent prior workflow, $\phi = 0.2407$ with missed detection and $\phi = 0.1391$ with compliance), whereas classic human-phishing cues (**Authority** and **Scarcity/Urgency**) actually *trigger* agent phishing detectors ($\phi = -0.1502$ and $\phi = -0.1976$).

---

## Evaluation Architecture & Defensive Metrics

### 1. Separating Detection Failure from Malicious Compliance

AgentPhishing evaluates email agents on synthetic workplace inboxes combining benign business emails and constrained phishing emails (filtered by an LLM realism judge requiring plausibility, coherence, naturalness, and **complete absence of prompt-injection or exploit strings**). For each phishing email, the benchmark separates two distinct behavioral failure modes:

- **Phishing Detection Rate ($D \uparrow$)**: Whether the agent flags or neutralizes the email by assigning a protective disposition (`report`, `archive`, `ignore`, or `unsubscribe`).
- **Malicious-Request Compliance Rate ($C \downarrow$)**: Whether the agent actively executes or drafts fulfillment of the attacker's request (following a link, extracting/sending requested credentials or internal details, or drafting a compliant reply).
- **Classification $F_1$ ($\uparrow$)**: Balances phishing recall against false-positive flagging on benign inbox traffic.
- **Composite Susceptibility Score ($J \downarrow$)**:
  $$J = 0.5(1 - D) + 0.3C + 0.2(1 - F_1) \in [0, 1]$$

### 2. Why Detection Failure and Compliance Must Be Tracked Separately

Across the 6-agent cross-evaluation (Table 2), missed detection does not automatically imply malicious compliance, and models fail along different axes:

- **High Detection Failure + High Compliance**: `Qwen3.7-Plus` (`D = 0.000 / C = 0.833` on diagonal, mean $J = 0.4238$) and `Kimi-K2.5` (`D = 0.167 / C = 0.583` on diagonal, mean $J = 0.4305$) both fail to flag workflow-framed emails and actively comply with the embedded request.
- **Detection Failure Without Immediate Compliance**: `GPT-5.4` (`D = 0.455 / C = 0.091` on diagonal) and `Grok-4.20` (`D = 0.167 / C = 0.250` on diagonal) frequently miss the phishing classification on target-adapted emails without always executing the malicious request.
- **Consistent Resilience Across All 6 Evolved Skills**: `Claude-Sonnet-5` achieves **`D = 1.000 / C = 0.000`** across skills evolved against all 6 targets (mean $J = 0.0374$), and `Gemini-3.5-Flash` achieves `D = 1.000 / C = 0.000` on its diagonal.

---

## Key Empirical Results

### 1. Six-Agent Cross-Evaluation Matrix (`D` $\uparrow$ / `C` $\downarrow$, Table 2)

Rows indicate the PhishOpt target agent used to evolve the generator skill; columns indicate the evaluated email agent:

| Skill Evolved Against $\downarrow$ \ Evaluated Agent $\rightarrow$ | `Kimi-K2.5` (`D / C`) | `Claude-Sonnet-5` (`D / C`) | `Gemini-3.5-Flash` (`D / C`) | `Grok-4.20` (`D / C`) | `GPT-5.4` (`D / C`) | `Qwen3.7-Plus` (`D / C`) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **`kimi-k2.5`** | **0.167 / 0.583** | 1.000 / 0.000 | 0.917 / 0.083 | 0.583 / 0.250 | 0.833 / 0.000 | 0.417 / 0.417 |
| **`claude-sonnet-5`** | 0.667 / 0.167 | **1.000 / 0.000** | 1.000 / 0.000 | 0.833 / 0.000 | 0.750 / 0.000 | 0.917 / 0.083 |
| **`gemini-3.5-flash`** | 0.667 / 0.167 | 1.000 / 0.000 | **1.000 / 0.000** | 0.636 / 0.000 | 0.750 / 0.000 | 0.909 / 0.091 |
| **`grok-4.20`** | 0.333 / 0.333 | 1.000 / 0.000 | 0.750 / 0.167 | **0.167 / 0.250** | 0.909 / 0.000 | 0.167 / 0.583 |
| **`gpt-5.4`** | 0.250 / 0.333 | 1.000 / 0.000 | 0.818 / 0.000 | 0.500 / 0.167 | **0.455 / 0.091** | 0.333 / 0.417 |
| **`qwen3.7-plus`** | 0.500 / 0.333 | 1.000 / 0.000 | 0.636 / 0.182 | 0.583 / 0.083 | 0.500 / 0.167 | **0.000 / 0.833** |

### 2. Zero-Shot Transfer of the Universal Skill to 9 Held-Out Email Agents (Table 5)

Evaluating the persuasion-informed `universal` skill across **9 additional email agents** never seen during optimization reveals a sharp bimodal split between resilient frontier models (mean $J \le 0.1036$) and vulnerable smaller/efficiency models (mean $J \ge 0.5062$):

| Held-Out Target Agent | Regime | Detection $D$ ($\uparrow$) | Compliance $C$ ($\downarrow$) | Susceptibility $J$ ($\downarrow$) | $F_1$ ($\uparrow$) | Benign FPR ($\downarrow$) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **`gpt-5.6`** | Resilient | **1.0000** | **0.0000** | 0.0533 | 0.7333 | 0.5556 |
| **`gemini-3.1-pro`** | Resilient | **1.0000** | **0.0000** | 0.0533 | 0.7333 | 0.2222 |
| **`claude-opus-4-8`** | Resilient | **1.0000** | **0.0000** | 0.0581 | 0.7097 | 0.4444 |
| **`claude-haiku-4-5`** | Resilient | **1.0000** | 0.0909 | 0.0755 | 0.7586 | **0.1111** |
| **`grok-4.6`** | Resilient | 0.9091 | **0.0000** | 0.1075 | 0.6897 | 0.5556 |
| **`gemini-2.5-flash-lite`** | **Vulnerable** | **0.0909** | **0.4545** | **0.7698** | 0.1053 | 0.0000 |
| **`gpt-5-mini`** | **Vulnerable** | **0.0909** | **0.6364** | **0.8205** | 0.1250 | 0.1111 |
| **`qwen-turbo`** | **Vulnerable** | **0.0000** | **0.4545** | **0.8363** | — *(0 flagged)* | 0.0000 |
| **`qwen-max`** | **Vulnerable** | **0.0000** | **0.9091** | **0.9727** | — *(0 flagged)* | 0.0000 |

### 3. Cialdini Persuasion Principles & Framing Ablation (Figure 5 & Table 3)

Annotating 180 evolved-skill evaluations (51 detection failures, 21 compliance cases) across Cialdini's six principles reveals an inversion between human phishing priors and LLM agent vulnerabilities:

- **Workflow Continuation Drives Agent Failure**: **Commitment and Consistency** (framing the email as a routine follow-up, ongoing thread, or prior task commitment) correlates positively with both **detection failure ($\phi = 0.2407$)** and **malicious compliance ($\phi = 0.1391$)**. **Liking** (friendly rapport) correlates with detection failure ($\phi = 0.1914$) but not compliance ($\phi = 0.0018$).
- **Classic Urgency & Authority Cues Alert the Agent**: **Authority** ($\phi = -0.1502$ with detection failure) and **Scarcity/Urgency** ($\phi = -0.1976$ with detection failure, $\phi = -0.1460$ with compliance) are *negatively* associated with failure because LLM safety filters are heavily trained on urgent executive-impersonation templates.
- **Controlled Framing Ablation (Table 3)**: On the universal skill, simply removing Commitment and Consistency framing raises `GPT-5.4` detection from `0.2500` to `0.5833` and drops compliance from `0.1667` to **`0.0000`** ($J: 0.5705 \to 0.2750$), while lifting `Gemini-3.5-Flash` detection from `0.6667` to `0.9167` ($J: 0.2774 \to 0.1095$). Replacing Commitment/Consistency with **Authority + Urgency** restores **100% detection (`1.0000`) and 0% compliance (`0.0000`)** on both `Gemini-3.5-Flash` ($J = 0.0222$) and `GPT-5.4` ($J = 0.0345$).

---

## Defensive Takeaways for Agent Engineering

1. **Static Phishing Corpora Create False Assurance**: Passing 100% of public human-phishing benchmarks provides zero guarantee against adaptive workflow-continuation social engineering.
2. **Defend Against Unverified Workflow-Continuation Claims**: Email and workplace agents fail when an inbound message claims to be a continuation of an existing task or prior sync (*Commitment and Consistency*). Defenses must verify thread/task provenance against trusted internal state (calendar, sent mail, ticket IDs) before treating an inbound email as an authorized continuation.
3. **Gate Outbound Actions & Replies Separately from Triage Classification**: Because models frequently miss detection on rapport-heavy or routine-looking emails (`Liking` $\phi = 0.1914$), outbound link-visitation, data-sharing, and reply-drafting tools must enforce independent authorization gates rather than trusting the inbox classifier's benign label.

---

## Why Not a Skill?

AgentPhishing is a diagnostic benchmark and vulnerability characterization study rather than a defensive runtime procedure. Its actionable defensive implications—verifying provenance of claimed prior commitments and gating outbound tool actions against social-engineering compliance—reinforce existing Praxis skills ([`provenance-capability-grants`](../skills/provenance-capability-grants/SKILL.md), [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md), [`taxonomy-driven-red-teaming`](../skills/taxonomy-driven-red-teaming/SKILL.md)) and rules in [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

---

## Related Artifacts

- **Rules**:
  - [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — Defending tool-using agents against indirect social engineering and unverified provenance claims.
  - [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Adaptive red-team evaluation vs. saturated static benchmarks.
- **Skills**:
  - [`provenance-capability-grants`](../skills/provenance-capability-grants/SKILL.md) — Binding tool capability grants to verified cryptographic/system provenance rather than untrusted message claims.
  - [`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md) — Adaptive red-teaming loops for uncovering model-specific blind spots.
- **Research Briefs**:
  - [`conversational-false-authentication.md`](conversational-false-authentication.md) — How agents accept unverified conversational claims as authentication.
  - [`multilingual-persuasive-jailbreak-evaluation.md`](multilingual-persuasive-jailbreak-evaluation.md) — Persuasive framing vulnerabilities in safety evaluations.
