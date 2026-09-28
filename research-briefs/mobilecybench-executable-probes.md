# MobileCybench: Evaluating Agent Vulnerability Discovery via Executable Probes

> **Source**: Zhang et al., arXiv:2609.23980, Sep 2026
> **Status**: Research Brief — benchmark and evaluation framework

## Why Not a Skill?

The contribution is a benchmark (13 Android apps, 495 hand-written probes) and an evaluation design, not a subtask procedure an agent runs. The transferable idea, grading security findings by replaying the exploit and running executable property checks instead of reading the report, is an evaluation principle already close to `cve-history-executable-detection` and `static-dynamic-verification-gap-measurement`.

## Core Concept

Agents now file vulnerability reports faster than maintainers can review them, and each report depends on security properties specific to the app. MobileCybench grades a report by **replaying the submitted exploit** (a malicious APK or a remote-attacker script) from a seeded baseline in an isolated environment, then running **probes**: executable checks of application-specific security properties that inspect emulator state, backend databases and services. A triggered probe shows both that the exploit worked and which property (confidentiality, integrity, availability, access control) it broke. Because a probe encodes a property rather than a known bug, it can catch vulnerabilities nobody knew about when it was written. An attribution step replays against patched/unpatched reference builds to name the underlying vulnerability.

## Key Findings

- **Setup**: 13 open-source Android apps, 495 probes; 5 coding agents (OpenCode with GPT-5.5, GPT-5.6-Sol, GLM-5.2; Claude Code with Opus 4.8 and Opus 5); 2 attack settings (malicious app, remote attacker with a low-privilege account) × 2 access levels (obfuscated APK only, source visible); 2-hour budget per run in a Kali container, pass@2.
- **APK-only, malicious-app setting**: the top agent (OpenCode / GPT-5.6-Sol) triggers probes in **53.8%** of apps; the weakest (OpenCode / GLM-5.2) in **15.4%**.
- **APK-only, remote-attacker setting**: all five agents at **16.7%** (2 of 12 apps).
- **Source access helps little on rate**: trigger rate across all agents and both settings goes from **28.8% to 32.8%**. For both Claude Code configurations source access made no difference (Opus 4.8: 28% → 28%; Opus 5: 32% → 32%).
- **Generic probes never fired**: all **124** triggered runs came from application-specific probes; generic probes triggered in 0 of 80 malicious-app triggered runs. A no-op exploit triggered nothing in **0 of 25** runs, so probes do not fire spontaneously.
- **Findings concentrate**: 3 vulnerabilities account for 57 of the 124 triggered runs.
- **Probe coverage is incomplete**: reference exploits triggered at least one probe in **19 of 24** attribution packages (79%); a silent probe means only "no checked property failed".
- **Safety refusals in an authorized setting**: Claude Code / Opus 4.8 refused in **25.0%** of runs and Claude Code / Opus 5 in **42.4%**; no refusals were observed for the OpenCode agents.
- **Real-world yield**: **23** previously unreported vulnerabilities; maintainers confirmed 12, patched 7, and 6 were assigned CVEs.

## Relevance to Praxis

- Grade security agents on executed, replayed evidence, not on the report text. This supports `rules/agent-sandbox-safety.md` "DON'T: Treat HTTP 200 / success tool return codes as workflow success without state verification" and the evidence-receipt approach in [`pentest-harness-assurance`](../skills/pentest-harness-assurance/SKILL.md).
- Generic checks did nothing here: probes (and by extension verifiers) must encode application-specific properties.
- Refusal rates of 25–42% for one harness family in an authorized pentest setting are a capability cost that attack-success benchmarks do not show. This bears on the false-refusal budget item (M6) for offensive-security deployments.
- Related: [`cve-history-executable-detection`](../skills/cve-history-executable-detection/SKILL.md), [`static-dynamic-verification-gap-measurement`](../skills/static-dynamic-verification-gap-measurement/SKILL.md), brief [`pentestchain-cost-aware-mcp-pentesting`](pentestchain-cost-aware-mcp-pentesting.md).

> Source: Zhang et al., "MobileCybench: Evaluating Agent Vulnerability Discovery via Executable Probes" (arXiv:2609.23980)
