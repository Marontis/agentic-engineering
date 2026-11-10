# LEGION: Benchmarking Language Agents on Sparse-Signal Investigation Under Adversarial Noise

> **Source**: [arXiv:2611.11896](https://arxiv.org/abs/2611.11896) — Samuel Joseph Amouyal, Ofek Glick, Yaniv Menasherov, Eyal Fisher, Ohav Barbi (2026)
> **Praxis Source ID**: `src:2611-11896v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

LEGION contributes a synthetic enterprise telemetry generator (`Legion-SIM`) and a 74-scenario cybersecurity investigation benchmark (`Legion-Bench`) comparing five standard agent scaffolds (`Direct`, `ReAct`, `See-Plan-Act`, `Reflexion`, `Multi-Agent`) against a deterministic domain-playbook upper bound (`Golden Workflow`). It does not propose a new transferable agent algorithm that solves the precision deficit it uncovers; instead, its diagnostic findings provide quantitative benchmark-design and multi-agent precision rules for [agent-evaluation-quality.md](../rules/agent-evaluation-quality.md) and [multi-agent-coordination.md](../rules/multi-agent-coordination.md).

---

## Benchmark Architecture (`Legion-SIM` & `Legion-Bench`)

Real-world incident response, fraud triage, and SRE root-cause investigations require finding sparse multi-day causal chains buried inside millions of routine events and benign anomalies. `Legion-SIM` simulates two complete enterprise environments in SQLite across **`10` on-premises telemetry tables** (`edr_process`, `edr_network`, `edr_file`, `identity_auth`, `dns`, `proxy`, `dlp`, `email`, `firewall`, `usb`) and **`3` cloud tables** (`cloud_audit`, `saas_activity`, `oauth_grants`):

- **Role-conditioned behavioral baselines**: Models **`60` distinct job roles across `13` departments** across `Meridian` (`300+` employees, `~600k` events) and `NexusTech` (`2M+` events), so normal behavior varies realistically by role (e.g., engineers spawn compilers and SSH sessions; finance staff exchange external attachments).
- **Adversarial benign confounders**: Injects **`4` deceptive benign anomaly patterns**—`late_night_work`, `travel_login`, `bulk_file_operation`, and `failed_login_cluster` (capped at `3` per employee per window)—that match surface heuristics for compromise unless cross-checked against HR/travel/role context.
- **Stratified threat scenarios (`74` templates × `5` seeds per company)**: Covers `7` MITRE ATT&CK threat-surface families plus compound multi-vector campaigns across three temporal/relational complexity tiers:
  - **`T1` (`4` scenarios)**: Minutes-scale single-source triage.
  - **`T2` (`44` scenarios)**: Hour-scale cross-source correlation across `2–4` log streams.
  - **`T3` (`26` scenarios)**: Multi-day dwell time, slow-drip exfiltration, and cross-identity lateral movement.
- **Four-metric evaluation (`20` LLM-call budget)**: Grades **Event Recall (`ER`)**, **Findings Recall (`FR`, `gpt-4o-mini` judge with `98%` human agreement on `100` audited judgments)**, **IoC Recall (`IoC R`)**, and **IoC Precision (`IoC P`)**.

---

## Key Empirical Findings

### 1. Universal Precision-Recall Asymmetry Across Agent Architectures
Across all five standard scaffolds driven by `GPT-5.5`, agents reliably uncover ground-truth malicious events and narrative findings, **but `28%–39%` of their reported Indicators of Compromise (IoCs) are false-positive benign confounders**:

| Metric (`GPT-5.5` Range Across 5 Scaffolds) | Observed Score | Diagnostic Interpretation |
|:--------------------------------------------|:---------------|:--------------------------|
| **Event Recall (`ER`)** | **`0.89–0.97`** | Agents locate relevant SQLite log rows effectively within 20 calls |
| **Findings Recall (`FR`)** | **`0.91–0.96`** | Attack-stage narrative reconstruction is consistently strong |
| **IoC Recall (`IoC R`)** | **`0.82–0.88`** | True malicious IPs, hashes, domains, and accounts are surfaced |
| **IoC Precision (`IoC P`)** | **`0.61–0.72`** | **Severe false-positive floor**: neither explicit planning (`SPA`), self-critique (`Reflexion`), nor specialist delegation (`Multi-Agent`) eliminates confounder over-flagging |

### 2. Precision Failure Is Structural (Baseline Neglect), Not Volume Overload
- **Invariance to `3x` confounders and `3x` log volume (`ReAct` on `Meridian`)**: Scaling from baseline (`ER 0.91`, `FR 0.92`, `IoC R 0.88`, `IoC P 0.69`) to **`3x` benign confounders** (`ER 0.90`, `FR 0.92`, `IoC R 0.87`, `IoC P 0.67`) or **`3x` total background events** (`ER 0.89`, `FR 0.92`, `IoC R 0.86`, `IoC P 0.65`) barely moves performance. Agents do not fail from context drowning; they fail structurally because they treat every anomalous-looking event in an investigation window as guilty by association instead of querying per-entity historical baselines.
- **Tier progression (`Meridian / NexusTech` 5-agent means)**:
  - **`T1`**: `ER 0.97 / 0.95`, `FR 1.00 / 1.00`, `IoC R 0.76 / 0.80`, `IoC P 0.56 / 0.59` (lowest precision because short single-indicator alerts tempt agents to pad reports with unrelated background anomalies).
  - **`T2`**: `ER 0.97 / 0.97`, `FR 0.97 / 0.96`, `IoC R 0.86 / 0.86`, `IoC P 0.70 / 0.72`.
  - **`T3`**: `ER 0.82 / 0.86`, `FR 0.86 / 0.91`, `IoC R 0.89 / 0.92`, `IoC P 0.60 / 0.68` (moderate `5–10 pp` `FR` and `11–15 pp` `ER` degradation on multi-day chains).

### 3. Specialist Multi-Agent Fan-Out Inflates False Positives Across Model Families
Evaluating `GPT-5.6 Terra`, `GPT-5.6 Luna`, `Gemini Pro`, and `Claude Opus 4.7` reveals a sharp multi-agent failure mode:
- Domain-specialist `Multi-Agent` orchestration pushes **`IoC Recall` to `0.94–1.00`** (`1.00` on `GPT-5.6 Terra`, `0.99` on `GPT-5.6 Luna` and `Claude Opus 4.7`, `0.94` on `Gemini Pro`), **but collapses `IoC Precision` to `0.40` on `Claude Opus 4.7`** (vs. `0.61` `ReAct`), **`0.47` on `GPT-5.6 Luna`**, and **`0.67` on `GPT-5.6 Terra`** (vs. `0.75` `Direct`), while dropping `Gemini Pro`'s `Findings Recall` from **`0.84` (`ReAct`) to `0.37`**. Each specialist sub-agent feels compelled to report suspicious indicators from its assigned log table, and the coordinator aggregates uncalibrated alarms without cross-stream falsification.

### 4. Pre-Built Heuristic Detection Tools Hurt Precision; Slow-Drip & Insider Attacks Remain Blind Spots
- **Tool ablation (`GPT-5.5`)**: Stripping pre-built anomaly-summary/detection tools (`No analysis tools`) actually **improves `IoC Precision`** from `0.64 -> 0.69` (`Direct`) and `0.69 -> 0.72` (`ReAct`) with negligible `ER` loss (`0.92 -> 0.92` and `0.91 -> 0.88`), whereas dropping down to raw SQL + Threat Intelligence (`Query-only`) lowers `ER` to `0.85` / `0.84`. Heuristic "anomaly finder" tools anchor agents onto benign confounders.
- **Persistent blind spots**: Scenarios lacking sharp point-in-time signatures suffer steep recall drops—specifically **slow-drip multi-week campaigns** such as BEC invoice diversion (`38–75%` `FR`, `37–76%` `ER`), malicious browser extensions (`49%` `ER`, `68%` `FR`), and OAuth consent phishing (`44%` `ER`, `61%` `FR`), alongside **valid-credential insider threats** including pre-resignation mass downloads (`52–72%` `FR`, `50–66%` `ER`) and source-code repository theft (`57–83%` `FR`, `56–83%` `ER`).

---

## Engineering Takeaways

1. **Always pair recall metrics with `IoC/Indicator Precision` under role-conditioned benign confounders**: Recall-only log benchmarks (compare [seclog-bench-scaffolded-log-reasoning](seclog-bench-scaffolded-log-reasoning.md)) reward over-reporting agents that would trigger severe SOC alert fatigue in production.
2. **Require explicit baseline-falsification queries before promoting an indicator**: Force investigative agents (and multi-agent coordinators) to query the target employee's `30`-day role baseline and HR/travel context before labeling an anomaly malicious.
3. **Prefer structured entity-query tools over pre-packaged heuristic "anomaly scanner" tools**, which bias LLMs toward unverified false positives.
