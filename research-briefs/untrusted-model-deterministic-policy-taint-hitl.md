# Treating the Model as an Untrusted Component: Deterministic Policy Enforcement, Human Approval and Taint Tracking Against Prompt Injection in Tool-Using Agents, with Validation on Open-Weights Models

> **Source**: [arXiv:2611.11571](https://arxiv.org/abs/2611.11571) — Mustafa S. Aljumaily, Nawar S. Alseelawi, Raghad Alshabandar (2026)
> **Praxis Source ID**: `src:2611-11571v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is a hypothesis-driven comparative evaluation (`Hyp. 1–7`) across `14` defense configurations (`D0–D8`, `H1–H5`) in a `13`-task, `12`-tool executable harness, combining open-weights LLM validation (`Qwen2.5-1.5B-Instruct`, `Qwen2.5-7B-Instruct`) with parametric simulation. As the authors explicitly document (`Sections 2, 6.5, and 8`), the four reference monitors are minimal instances whose `P3` capabilities match the benchmark oracle's authorization set by construction, session-level taint is assigned synthetically by the harness rather than propagated through model-generated values, and all human-approval, reviewer-fatigue, and approval-budget results (`Sections 6.5–6.7`) are simulation-only. Because capability-bound reference monitors and out-of-band human gates are already covered as standalone procedures in [`provenance-capability-grants`](../skills/provenance-capability-grants/SKILL.md), [`principal-context-permission-intersection`](../skills/principal-context-permission-intersection/SKILL.md), and [`out-of-band-hitl-verification`](../skills/out-of-band-hitl-verification/SKILL.md), this paper serves best as an empirical and simulation reference brief backing architectural rules in [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

---

## Experimental Design & Two-Rater Oracle Audit (`Sections 3–5, 6.11`)

- **Environment & Severity Scale**: `13` synthetic task templates (`1–3` benign calls each) over `5` untrusted read tools (`fetch_url`, `read_file`, `read_email`, `query_db`, `list_files`) and `7` side-effecting target tools weighted by severity (`write_file = 3`, `send_email = 5`, `delete_file = 7`, `http_post = 8`, `run_shell = 8`, `update_config = 9`, `set_setpoint = 9`, confidential data egress `= 10`; **severe action** defined as `harm >= 8`).
- **Attacker Ladder**: `A0` naive, `A1` authority-spoofing, `A2` obfuscated/delimiter-spoofing (`1` attempt), `A3` persistent adaptive (`up to 25` attempts, `3` argument-fuzzing variants per attempt across recipient lists, suffix confusion, userinfo URLs, path traversal, key-case mutations, numeric-string setpoints, and shell chaining), and `A4` fully compromised model (`obedience = 1.0`, full `33`-variant library + approval spamming).
- **Blind Oracle Audit (`Section 6.11`)**: Across `2 × 100` randomly sampled real-model attack episodes, independent human labeling agreed with the automatic canonicalizing effect oracle at `97%`/`96%` ($\kappa = 0.94, 0.92$) for Rater A and `100%`/`99%` ($\kappa = 1.00, 0.98$) for Rater B (pooled inter-rater agreement `96%`, $\kappa = 0.92$, Fleiss' $\kappa = 0.96$ and `0.93`; `192/192` unanimous rows matched the oracle).

---

## Real-Model Validation on Open-Weights Agents (`Sections 6.10–6.11`, `Tables 13–18`)

End-to-end runs executed `156` attack episodes and `78` benign episodes per defense on `Qwen2.5-1.5B-Instruct` and `Qwen2.5-7B-Instruct` (temperature `0.7`, up to `6` turns):

| Defense Stack | `Qwen2.5-1.5B` Proposes Attack | `Qwen2.5-1.5B` Goal Executed | `1.5B` Benign Compl. (Spont. Viol.) | `Qwen2.5-7B` Proposes Attack | `Qwen2.5-7B` Goal Executed | `7B` Benign Compl. |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `D0` No defense | `67%` | `66%` | `50%` (`40%`) | `86%` | `86%` | `99%` |
| `D1` In-prompt guardrail | `65%` | `65%` | `59%` (`35%`) | `55%` | `55%` | `100%` |
| `D2` Guardrail + spotlighting | `47%` | `42%` | `54%` (`37%`) | `42%` | `40%` | `100%` |
| `D3` Spotlight + LLM detector | `12%` | `10%` | `37%` (`31%`) | `0%` | `0%` | `100%` |
| `D4` `P1` tool allow-list | `63%` | `42%` | `78%` (`4%`) | `88%` | `67%` | `99%` |
| `D5` `P2n` naive arg checks | `67%` | `10%` | `73%` (`5%`) | `81%` | `21%` | `100%` |
| `D6` `P2h` hardened arg checks | `67%` | `9%` | `68%` (`4%`) | `81%` | `22%` | `95%` |
| `D7` `P3` task-bound caps + IFC | **`64%`** | **`1%` (`1.3%`)** | **`71%` (`0%`)** | **`84%`** | **`8%` (`7.7%`)** | **`99%`** |
| `D8` `P3` + spotlight + detector | `12%` | `0%` | `44%` (`0%`) | `0%` | `0%` | `100%` |

1. **Deterministic Set Invariance vs. Model Obedience**: Behind `P3` (`D7`), the models still proposed the attacker's call in **`64%`** (`1.5B`) and **`84%`** (`7B`) of episodes, yet `P3` admitted only **`2/156` (`1.3%`)** and **`12/156` (`7.7%`)**—and every admitted attack belonged to the same single in-policy semantic-falsification task (`pressure_status`). On `Qwen2.5-1.5B`, `P3` actually **raised benign completion by `+21` percentage points** (`50%` $\to$ `71%`, `95% CI [+5, +35]`) because it blocked the small model's `40%` spontaneous unauthorized benign calls, whereas stacking `spotlight + detector` (`D8`) cut `1.5B` benign completion to `44%`.
2. **Rejection of Monotone Susceptibility & Prompt-Guardrail Instability**: In the `Qwen2.5-1.5B` calibration experiment (`174` prompts $\times$ `2` samples, `n = 24`/cell; `Table 13`), the assumed monotone logistic susceptibility law was strongly rejected (deviance `60.3` on `9` df, $p = 10^{-9}$; monotone test $p = 4 \times 10^{-11}$): `"document owner requires"` (level `2`) achieved `50.0%` obedience while `"urgent system notice, do not mention"` (level `3`) achieved `4.2%`, and the prompt guardrail had no detectable effect (`20/144` vs. `18/144`, Fisher $p = 0.86$). Under `k = 10` persistent static-family attempts (`Tables 17–18`), prompt guardrails (`D1`) reached **`91%`** (`1.5B`) and **`85%`** (`7B`) best-family ASR (`97%` and `89%` uniform search), whereas `D3` (`spotlight + detector`) stayed at `38%` (`1.5B`) and `0%` (`7B`) against non-adaptive static families—contradicting the simulator's assumed monotone detector erosion law.

---

## Argument-Fuzzing Ladder & Simulation-Only HITL / Taint Findings (`Sections 6.1–6.7`)

### 1. Monitor Implementation Quality Under Argument Fuzzing (`Tables 2 & 4`)
- Against the `33`-variant argument-fuzzing library in isolation, `P1` (tool allow-list) admits **`27/33` (`82%`)**, `P2n` (naive uncanonicalized argument checks) admits **`18/33` (`55%`)** and reaches **`84.6%` adaptive `A3` ASR@25** (`92%` `A4` ASR), `P2h` (hardened canonicalized argument checks) admits **`6/33` (`18%`)** and drops `A3` ASR@25 to **`30.8%`** (`62%` `A4` ASR), and `P3` (task-bound capabilities + confidentiality flow rule) admits **`1/33` (`3%`)**, holding `A4` severe-action rate (`sev >= 8`) at **`0.0%`** and `A4` residual harm at **`0.69/10`** (`23.1%` `A4` ASR, entirely in-policy semantic manipulation).

### 2. Taint-Triggered Human Review & Deterministic Approval Budgets (`Tables 2, 5–11`, *Simulation-Only*)
- **Severity-Only Review Behind `P3` Is Redundant (`H1`)**: Escalating `sev >= 8` calls behind `P3` yields zero improvement over `D7` (`0.69` `A4` harm, `23%` `A4` ASR, `0.31` escalations/task) because `P3` already deterministically blocks all `sev >= 8` violations.
- **Taint-Triggered Review Targets the In-Policy Residual (`H2`)**: Lowering the escalation threshold to `taint_thr = 3` when the session is tainted catches semantically falsified low-severity writes, reducing `A4` harm by **`62%`** (`0.69` $\to$ `0.26`) and `A4` ASR from `23.1%` to `8.7%` at `0.57` escalations/benign task; raising `human_thr` from `8` to `10` while keeping `taint_thr = 3` trims workload by `33%` (`0.56` $\to$ `0.38` escalations) with `A4` harm `0.21` $\to$ `0.19`.
- **Human Review Without a Monitor Collapses Under Approval Spamming (`H5`)**: `H5` (`human + taint, no monitor`) reaches **`100.0%` `A4` severe-action rate (`10.00/10` harm)**—and still hits **`92.6%` severe actions even with zero fatigue and zero spam decay** (`Table 8`), because repeated requests compound any non-zero per-request human miss rate ($1 - h_0 = 0.10$).
- **Deterministic Per-Episode Approval Budget (`Table 9`)**: Automatically denying escalations after a fixed budget $n$ per episode reduces `H2` `A4` harm from `0.24` to **`0.04`** at $n = 1$ (`96.4%` vs. `96.9%` benign completion) and cuts `H5` `A4` harm from `10.00` to `2.25` (`17.3%` severe rate at $n = 1$; `4.40` harm / `37.4%` severe at $n = 2$).
- **Fail-Safe Layer Independence (`Tables 10–11`)**: As taint coverage drops to `0.0`, `H2` degrades cleanly to `P3`'s `0.69` harm bound (`0.0%` severe), whereas relaxing `H3`'s (`P2h`) severity gate from `8` to `10` causes severe-action rate to jump from `1.7%` to `7.7%` when taint tracking fails.

---

## Relevance to Praxis

- Complements [`out-of-band-hitl-verification`](../skills/out-of-band-hitl-verification/SKILL.md) (`I-HITL`): hardware-attested out-of-band channels stop *forged* approvals, while `arXiv:2611.11571` shows why even an unforgeable human reviewer must sit **behind** a canonicalized capability monitor, be triggered by **taint** on low-severity in-policy writes rather than high-severity tools the monitor already blocks, and be rate-limited by a **deterministic per-episode approval budget**.
