<!--
Licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
Attribution: Marontis / agentic-engineering (https://github.com/Marontis/agentic-engineering).
-->

# Deconfliction Report — 2026-11-11 (Agentic High-Tier Wave 7)

## Scope

This audit covers the 10 strictly agentic high-tier (`score >= 8.0`) papers ingested on `2026-11-11` across `cs.AI`, `cs.SE`, `cs.CR`, `cs.HC`, and `cs.MA`, which produced:
- **4 new skills**:
  - [`compositional-coding-harness-reference-monitor`](../skills/compositional-coding-harness-reference-monitor/SKILL.md) (`arXiv:2611.13960` — `ActiveSecHarness`)
  - [`falsification-gated-memory-evolution`](../skills/falsification-gated-memory-evolution/SKILL.md) (`arXiv:2611.14326` — `FGSE`)
  - [`certified-task-verifier-harness`](../skills/certified-task-verifier-harness/SKILL.md) (`arXiv:2611.13336` — `Veritas`)
  - [`code-grounded-sast-finding-explanations`](../skills/code-grounded-sast-finding-explanations/SKILL.md) (`arXiv:2611.13041` — `SAFE`)
- **6 new research briefs**:
  - [`private-knowledge-retrieval-multi-agent-semantic-memory`](../research-briefs/private-knowledge-retrieval-multi-agent-semantic-memory.md) (`arXiv:2611.13696` — `tipp++`)
  - [`bypassgym-edr-evasion-defensive-lessons`](../research-briefs/bypassgym-edr-evasion-defensive-lessons.md) (`arXiv:2611.13684` — `BypassGym`, defensive lessons only)
  - [`self-evolving-multimodal-agents-cross-scenario-survey`](../research-briefs/self-evolving-multimodal-agents-cross-scenario-survey.md) (`arXiv:2611.14256`)
  - [`enterprise-analytics-agent-eval-framework-comparison`](../research-briefs/enterprise-analytics-agent-eval-framework-comparison.md) (`arXiv:2611.14493`)
  - [`language-grounded-hrl-multi-agent-sar`](../research-briefs/language-grounded-hrl-multi-agent-sar.md) (`arXiv:2611.13161`)
  - [`lilo-multi-agent-conversational-sandbox-study`](../research-briefs/lilo-multi-agent-conversational-sandbox-study.md) (`arXiv:2611.14260`)
- **8 new rule entries and 1 evidence extension** across [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md), [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md), [`agent-human-interaction.md`](../rules/agent-human-interaction.md), [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md), [`adk-security-and-evaluation.md`](../rules/adk-security-and-evaluation.md), and [`recursive-improvement.md`](../rules/recursive-improvement.md), plus targeted checklist updates to [`agent-sandbox.spec.md`](../specs/agent-sandbox.spec.md), [`self-improving-agent.spec.md`](../specs/self-improving-agent.spec.md), [`adk-eval-quality-gate.spec.md`](../specs/adk-eval-quality-gate.spec.md), and [`skill-library.spec.md`](../specs/skill-library.spec.md).

---

## Genuine Tensions Resolved (`Tension with`)

### 1. Compositional 2D $(\tau, \sigma)$ Taint & Disk Provenance (`ActiveSecHarness`) vs. Decode-Time MCP Provenance, Principal Intersection, and Post-Hoc SAST (`agent-sandbox-safety.md`)
- **Entry A**: `"DO: Enforce a 2D trust-by-sensitivity taint lattice, disk provenance ledger, and dual-key encrypted audit logs in Ring-0 coding kernels"` (`ActiveSecHarness`, `arXiv:2611.13960`)
- **Entries B, C & D**: `"DO: Bind cryptographic provenance at decode boundaries and reject unsigned high-risk MCP actions"` (`arXiv:2610.31974`), `"DO: Intersect permissions across all influencing principals and isolate context per task branch"` (`Conflux`, `arXiv:2611.08768`), and `"DO: Combine deterministic SAST with unrestricted AI security agents rather than relying on either alone"` (`arXiv:2610.22866`)
- **Resolution**: Added reciprocal `Tension with` notes across all four entries. Decode-time MCP envelopes authenticate external tool calls and principal-context intersection limits capability widening across users, while inside local coding sandboxes untrusted content also launders across turns through workspace files (`0% -> 80%` block rate only when tracked by a persistent disk provenance ledger) and exfiltrates secrets via high-trust sinks unless sensitivity $\sigma$ is tracked orthogonally to trust $\tau$. Inline Ring-0 semantic AST patching (`93.3%` block rate across 15 CWEs) prevents unsafe writes at tool-execution time, whereas out-of-band deterministic SAST + AI security review audits broader cross-file business-logic flaws prior to merge.

### 2. Closed-Loop Telemetry Oracle Suppression & Signed-Binary DLL Inspection (`BypassGym`) (`agent-sandbox-safety.md`)
- **Entries A & B**: `"DO: Give blocking action monitors recent call history, and make denials terminal"` (extended with `BypassGym`, `arXiv:2611.13684`) and `"DON'T: Exempt signed host executables from DLL-load inspection or assume frontier-weight caps contain dual-use agent synthesis"` (`arXiv:2611.13684`)
- **Resolution**: Documented how returning structured rule names, static/dynamic stage breakdowns, or signature identifiers to an iterative coding harness converts an endpoint detector into a closed-loop hill-climbing oracle (`0.0% -> 100.0%` evasion against open-source rule engines within a 20-turn budget, and up to `75.0%` by an open-weight `35B-A3B` coder). Denials to the agent caller must remain opaque and terminal while rich telemetry flows exclusively to out-of-band SOC pipelines, and signed host binaries must never receive blanket DLL-search-order exemptions.

### 3. Isolated Agent-Blind Verifier Synthesis & Soundness Certification (`Veritas`) vs. Verifier Exposure Overfitting (`agent-evaluation-quality.md`, `recursive-improvement.md`)
- **Entry A**: `"DO: Combine observable-evidence precedence, domain-rule libraries, and weakest-match principles in isolated grader synthesis, and certify graders across five soundness axes"` (`Veritas`, `arXiv:2611.13336`)
- **Entry B**: `"DON'T: Expose benchmark verifier code or unstated rubric predicates to the skill-library learner"` (`arXiv:2611.08903`)
- **Resolution**: Added reciprocal `Tension with` notes across both files. Compiling deterministic task-specific `check.py` graders in an isolated workspace calibrated against human rubric sensitivity (`E + R + H` reaching `85.1%` agreement and `0.684` Cohen's $\kappa$) eliminates subjective LLM-judge drift without leaking hidden evaluation predicates—provided the executing agent and any skill-distillation loop remain strictly blind to the synthesized grader code and `G1–G5` certification artifacts.

### 4. Full OpenTelemetry Trajectory Span Grading vs. Trajectory Match Gates (`agent-evaluation-quality.md`, `adk-security-and-evaluation.md`)
- **Entry A**: `"DO: Expose OpenTelemetry trajectory spans to analytics-agent graders and combine functional boundary synthesis with security probing"` (`arXiv:2611.14493`)
- **Entry B**: `"DO: Gate production deployment on golden dataset trajectory validation in CI/CD"` (`adk-security-and-evaluation.md`)
- **Resolution**: Added reciprocal `Tension with` notes. Exact `tool_name` sequence gates catch coarse routing regressions, while passing full OpenTelemetry intermediate tool arguments, SQL/Python queries, and raw tool outputs into LLM-as-judge rubrics catches silent execution errors hidden behind polished prose (`2/25` human-approved `"pass"` labels overturned on trace inspection) so long as judge `showThinking` modes that inflate invalid-JSON errors (`0.33% -> 10.67%`) are disabled.

### 5. Retry-Matched Stateless Baselines (`pass@k`) vs. Capability-Only Benchmark Optimization (`recursive-improvement.md`)
- **Entry A**: `"DO: Audit outcome observability, rollout scarcity, and structural preconditions before porting iterative multimodal improvement mechanisms, and subtract stateless retry baselines"` (`arXiv:2611.14256`)
- **Entry B**: `"DON'T: Allow self-modifying agents to optimize prompts or scaffolding solely against performance benchmarks"` (`arXiv:2609.17817`, `arXiv:2611.10542`)
- **Resolution**: Added reciprocal `Tension with` notes. Subtracting retry-matched stateless baselines (`pass@k` at identical rollout budgets) isolates genuine cross-episode evolution from test-time sampling variance, while immutable held-out negative security and safety suites (`RiOSWorld`, trojan/backdoor gates) must always run alongside capability metrics so autonomous updates cannot trade away safety.

---

## Triage Rigor & Automated Lint Verification

- **Research Brief Scope Discipline**:
  - [`language-grounded-hrl-multi-agent-sar.md`](../research-briefs/language-grounded-hrl-multi-agent-sar.md) (`arXiv:2611.13161`) and [`lilo-multi-agent-conversational-sandbox-study.md`](../research-briefs/lilo-multi-agent-conversational-sandbox-study.md) (`arXiv:2611.14260`) were intentionally retained as contextual Research Briefs without standalone rule entries: `2611.13161` omits grounding-LLM identity and exact environment parameters alongside manuscript bibliography/caption anomalies, and `2611.14260` is a single-session exploratory child-AI study ($N = 28$, $n = 26$ logs) without controlled ablation baselines.
- **`kb_lint.py` Audit**:
  - Running `python -X utf8 scripts/kb_lint.py --base origin/master` across both `bo-praxis/output` and `agentic-engineering` passed with **`0 error(s)`**, **`0` `conflict:` warnings**, and **`0` new `copied-stat` warnings**.
