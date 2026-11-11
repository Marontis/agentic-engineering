---
name: code-grounded-sast-finding-explanations
description: >
  Explain static analysis and policy findings with a read-only repository and
  rule-inspection agent, deterministic CWE and taint-role pre-enrichment, and a
  demand-tiered single-response schema while keeping detection auditable and
  remediation judgment with the developer. Derived from Code-Grounded Agentic
  Explanations for Static Analysis Vulnerability Findings (arXiv:2611.13041).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Code-Grounded Agentic Explanations for Static Analysis Findings

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

> **Source**: [Code-Grounded Agentic Explanations for Static Analysis Vulnerability Findings](https://arxiv.org/abs/2611.13041) — Oshando Johnson, Ranjith Krishnamurthy, Rohith Kumar Shanmuganathan, Goran Piskachev, Eric Bodden (2026) | Praxis: `src:2611-13041v1`

## When to Use

- Integrating LLM-generated explanations into Static Application Security Testing (`SAST`), linter, Infrastructure-as-Code (`IaC`), or compliance-policy tooling that emits `SARIF` (`Static Analysis Results Interchange Format`) reports inside an IDE plugin, pull-request review comment, or security triage dashboard.
- Helping developers without deep security expertise localize, understand, and remediate multi-hop taint or data-flow findings (`source -> propagator -> sanitizer -> sink`) without overwhelming them with generic CWE prose or forcing them out of their editor into external chat workflows.
- Replacing single-prompt "explain this warning" wrappers or self-reported audience selectors (`beginner` / `intermediate` / `advanced`) that hallucinate control flow outside the flagged snippet, confuse the fired rule's pattern with a broader CWE family, or push unverified automated patches.

## Core Insight

Combining rule-based static analysers with LLMs succeeds only when **detection, explanation, and remediation authority stay cleanly separated**:

1. **Detection stays rule-based and auditable; judgment stays human**: Static analysers (`Semgrep`, `CodeQL`, `Qodana`) provide deterministic, reproducible `SARIF` rules and taint traces, whereas LLMs used as vulnerability *detectors* suffer uncalibrated false positives and non-determinism, and LLMs permitted to *auto-patch* findings risk applying broken fixes to false positives or eroding developer comprehension. In closing interviews across a `24`-participant controlled crossover study (`SAFE`), `22/24` participants discussed the automation boundary and **`20/24` explicitly insisted that the developer—not the agent—judge true/false positives and apply fixes** (`6` citing knowledge retention, `5` diff inspection, `5` false-positive patch bugs, and `3` developer liability).
2. **Two-artifact agentic grounding beats single-snippet prompting**: A static finding is defined jointly by **what the codebase actually does** across callers/callees and **what specific heuristic pattern the fired rule matched** (since SAST rules are noisy proxies for CWE categories). Equipping a read-only explanation agent (`SAFE Agent`) with six narrow tools to inspect both the **fired SAST rule definition** and **surrounding repository code**—paired with deterministic pre-enrichment of CWE metadata and data-flow hop roles—more than doubled `correct` remediation proposals on `64` true-positive responses from **`19%` (`SAFE-Blue` single-prompt baseline) to `41%` (`SAFE-Red`)** (participant-clustered cumulative-link **odds ratio `2.6`**, `95% CI [0.93, 7.09]`, `p = .069`; `2.8`, `p = .064` with period and finding-set covariates), raised System Usability Scale (`SUS`) from **`77.3` to `85.0`** (`17/22` non-tied participants higher, Wilcoxon `z = -2.55`, `p = .011`, `r = 0.62`), and increased perceived remediation actionability by **`+0.67` on a 5-point scale** (`z = -2.53`, raw `p = .011`, Holm-adjusted `p = .057`, `r = 0.73`).
3. **Grounding improves comprehension and actionability, NOT blind trust**: Across the crossover study, **perceived trust remained flat (`+0.04` on a 5-point scale)** even as usability, actionability, and fix correctness rose. Grounding explanations in real identifiers and data-flow hops helps developers *understand and verify* a warning faster without inflating uncritical belief that the analyser's verdict is right.

---

## Step-by-Step Procedure

### Step 1: Keep Detection Deterministic in `SARIF` and Pre-Enrich Metadata Outside the LLM

Do not ask the LLM to scan files for vulnerabilities, invent CWE classifications, or guess taint-step roles when deterministic static artifacts already exist.

1. **Ingest Auditable `SARIF 2.1.0` Output**:
   - Run the deterministic analyser (`Semgrep`, `CodeQL`, `Qodana`, etc.) to produce `SARIF 2.1.0` runs containing rule identifiers, severity levels, primary physical locations (`artifactLocation`, `region`), and `codeFlows` / `threadFlows` taint traces when available.
   - Normalize multi-tool schemas (e.g., `Qodana` vs. standard `SARIF`) into one internal finding model before invoking any agent.
2. **Deterministically Enrich CWE Metadata**:
   - Map each finding's rule tags/identifiers against a bundled, version-pinned **MITRE CWE catalog** outside the LLM (`CWE ID`, canonical name, official description, likelihood, and common consequences).
   - Never rely on the LLM's parametric memory to map a vendor rule ID to a CWE; ungrounded lookup causes weakness-class misattribution when rule names are terse or framework-specific.
3. **Classify Data-Flow Step Roles Before Explanation**:
   - When `codeFlows` are present, deterministically classify each trace hop into one of five canonical roles—**`source`**, **`propagator`**, **`call`**, **`sanitizer`**, or **`sink`**—using step position and lightweight syntactic cues on the hop snippet.
   - Pass this typed hop sequence to both the UI trace renderer and the explanation agent so step indices (`0..N-1`) are 1-to-1 aligned.

---

### Step 2: Enforce Two-Artifact Grounding via a Read-Only Repository & Rule Toolkit

Give the explanation agent **read-only** access to the workspace and the analyser's rule registry—no file-write, shell-execution, or patch-application tools—and constrain its system prompt to verify **two artifacts** before drafting an explanation.

1. **Expose a Minimal Six-Tool Read-Only Surface**:
   - `lookup_sast_rule(rule_id)`: retrieves the exact rule definition, pattern/taint specification, message template, and metadata from the local rule pack or vendor registry (e.g., Semgrep registry API with local fallback).
   - `get_code_structure(file_path)`: returns file AST/symbol outline (classes, methods, signatures, imports) to orient navigation cheaply without reading entire large files.
   - `read_code(file_path, start_line, end_line)`: reads bounded line ranges around the flagged location, callers, callees, and helper sanitizers.
   - `search_codebase(query, path_glob)`: runs exact/regex identifier search across the repository to locate custom validators, configuration wrappers, or shared sinks.
   - `list_files(dir_path)` and `find_files(pattern)`: inspect project layout, framework conventions, and dependency manifests (`pom.xml`, `package.json`, `pyproject.toml`) so proposed fixes use libraries and idioms already present in the repository.
2. **Mandate the Pre-Answer Grounding Contract**:
   - Require the agent in its system prompt to:
     1. Call `lookup_sast_rule` on the fired rule ID so it explains *why this specific rule fired* rather than reciting a textbook CWE summary.
     2. Call `read_code` on the primary flagged region **and** on the `source` and `sink` endpoints (plus any candidate `sanitizer` or cross-file `call` hops) when a multi-step taint flow exists.
     3. Inspect surrounding callers/imports before recommending a library or API fix so mitigation code compiles against the project's actual stack.
   - Explicitly forbid the agent from declaring a definitive true-positive/false-positive verdict; instruct it to surface concrete evidence (e.g., whether an upstream guard actually constrains the tainted input type or path) so the developer can judge.
3. **Stream Tool Calls as an Auditable Evidence Trail**:
   - Stream each tool invocation (`lookup_sast_rule`, `read_code` file + line span, `search_codebase` pattern) to the client over Server-Sent Events (`SSE`) while generating, and retain the read file/line spans as an inspectable provenance trail.

---

### Step 3: Emit a Single-Call Structured Schema Tiered by Demand (Not Audience Label)

Formative workshops (`19` practitioners) and crossover telemetry showed that asking users to self-select `beginner` / `intermediate` / `advanced` depth fails because developers' familiarity varies **per finding and per CWE**, not globally per person. Instead, generate a **single structured JSON response** organized into progressive-disclosure tiers that the developer expands on demand.

1. **Validate Against a Fixed Eight-Part Output Schema**:
   - **Default Primary Card (always visible)**:
     1. `title`: concise, code-specific summary of the flagged pattern.
     2. `tldr`: strictly **one sentence** stating what input reaches what sensitive operation and why the rule flagged it.
     3. `what`: concrete explanation referencing the **actual variable, method, and parameter names** in the repository (never generic `foo`/`userInput` placeholders).
     4. `why`: how the issue manifests in **this application's context** (e.g., controller exposure, privilege boundary, or data store).
     5. `where`: exact file path, line range, and enclosing class/method construct.
     6. `how_to_fix`: concrete attack/failure scenario paired with a **project-specific remediation** using the repository's existing APIs/frameworks (e.g., parameterized `PreparedStatement`, path canonicalization + allowlist root check, context-matched output encoding).
   - **On-Demand Secondary Disclosures (collapsed by default, zero extra LLM calls to open)**:
     7. `deepdive`: extended mechanics, edge cases, framework caveats, and external CWE/OWASP references (opened selectively—`12` times by `6/16` telemetry-logged participants when encountering unfamiliar CWEs).
     8. `steps[]`: array of `1–2` sentence plain-language annotations indexed to every hop in the pre-enriched taint trace (`source -> ... -> sink`), generated inside the **same initial agent response** so clicking any hop in the trace (`134` opens across `12/16` logged participants) renders instantaneously without a follow-up LLM round-trip.
2. **Keep the Verbatim Static-Analyser Output Inspectable**:
   - Always render a collapsible **"Original rule message"** disclosure containing the verbatim `ruleId`, severity, and raw `SARIF` message alongside inline glossary hover tooltips for security terms (`149` hovers across `12/16` logged participants). Never hide or overwrite the underlying deterministic tool's words.

---

### Step 4: Embed Inline in the Review Surface, Pre-Warm Cache, and Preserve the Human Boundary

1. **Co-Locate Trace Navigation with the Code Editor**:
   - Render findings inline in the IDE or PR diff view with one-click step-to-editor navigation (`106` jumps across `11/16` logged participants) and editor line decorations highlighting the active trace hop. Avoid external copy-paste chat tabs, which break spatial orientation on multi-file taint flows.
2. **Pre-Warm and Key the Persistent Explanation Cache**:
   - Multi-step agentic tool loops incur multi-second latency if triggered cold when a developer clicks a finding. Run the explanation agent asynchronously in CI or background scan indexing immediately after `SARIF` generation, caching validated JSON responses keyed by `(rule_id, rule_version, primary_snippet_hash, codeflow_hashes)`.
   - Invalidate and regenerate entries only when a finding's underlying code span, taint hops, or rule definition changes.
3. **Enforce the Judgment & Application Boundary**:
   - Provide copyable reference snippets or side-by-side illustrative diffs inside `how_to_fix`, plus explicit triage disposition controls (`True Positive`, `False Positive`, `Needs Review`) that require human selection.
   - Do **not** auto-commit patches or auto-suppress `SARIF` findings based on the explanation agent's prose.

---

## Environment Caveats & Construct Boundaries

- **Orientation Overhead Dominates Short Time Caps**: Across `122` timed decisions in the `SAFE` crossover study, overall median review time was `3.5` minutes per finding (`5.1` min median on `SAFE-Blue` vs `4.7` min on `SAFE-Red`, geometric mean ratio `0.87`, `p = .21`), but the **first finding in a block took `1.8x` longer** (`5.1` min median on finding 1 vs `3.7`, `2.5`, and `1.2` min on subsequent findings). Completing `5` findings required ~`17.7` minutes at observed medians, so `15`-minute experimental caps truncate throughput (`124/240` decisions completed) and obscure triage-accuracy differences (`0.46` `SAFE-Blue` vs `0.53` `SAFE-Red` counting `unsure` as wrong, `p = .59`; `0.56` vs `0.63` excluding `unsure`). Budget realistic codebase-orientation warm-up time when evaluating SAST explanation tools.
- **Bundled Treatment & Pre-Caching Caveat**: The `SAFE` crossover study compared `SAFE-Blue` (single-prompt backend + audience-level selector UI) against `SAFE-Red` (6-tool `SAFE Agent` + demand-tiered UI) as a holistic system with a **prewarmed explanation cache** on a single Java web codebase (`Health-Doc-Exchange`, `Semgrep v1.160.0` across `CWE-23`, `CWE-78`, `CWE-79`, `CWE-89`, `CWE-918`). It does not factorially isolate how much of the `+7.7` `SUS` gain and `2.6x` fix-correctness odds ratio comes from agentic repository grounding versus demand-tiered UI layout, nor does it measure developer abandonment under uncached live agent latency.

---

## Failure Modes & Guardrails

| Failure Mode | Symptom | Guardrail |
|:---|:---|:---|
| **CWE-vs-Rule Conflation** | Agent explains textbook SQL injection while the fired Semgrep rule actually matched an unparameterized string logger or ORM wrapper | Force `lookup_sast_rule(rule_id)` before drafting and keep the verbatim `SARIF` rule message accessible in a collapsible block |
| **Snippet-Boundary Hallucination** | Agent claims input is unsanitized (or sanitized) because validation happens two call hops upstream | Require `read_code` on `source`, `sink`, and intermediate `call`/`sanitizer` hops before generating `what` and `how_to_fix` |
| **Foreign-Stack Fix Suggestions** | Agent recommends Spring Security or Guava helpers in a plain Jakarta/stdlib module where those dependencies do not exist | Inspect `list_files` / build manifests and surrounding imports so `how_to_fix` uses libraries already present in the repo |
| **Per-Click Latency Stalls** | Clicking each hop in a 7-step taint flow fires a separate LLM request, stalling code navigation | Generate all `steps[]` hop annotations and `deepdive` inside the initial structured JSON response and pre-warm cache after CI scans |
| **Silent False-Positive Patching** | Developers click "auto-apply" on a false positive, introducing regressions or bypassing legitimate business logic | Withhold write/commit tools from the explanation agent; keep verdict disposition and patch application strictly human-gated |

---

## Related Artifacts

- **Rules**:
  - [`agent-human-interaction.md`](../../rules/agent-human-interaction.md) — Human-agent review boundaries (`DON'T: Treat agent output as implicit authorization`, `DON'T: Present all information at once`, `DO: Make agent reasoning auditable and navigable`, and code-grounded SAST explanation guardrails)
  - [`agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — Dual PoC + functional preservation repair validation (`DON'T: Validate repairs using crash suppression alone`)
  - [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — Read-only tool scoping and least-privilege capability boundaries
- **Skills**:
  - [`security-aware-context-slicing`](../security-aware-context-slicing/SKILL.md) — Security-relevant repository context selection for code generation and review
  - [`cost-effective-repo-exploration`](../cost-effective-repo-exploration/SKILL.md) — Escalation-oriented read-only repository navigation (`outline -> search -> bounded read`)
- **Research Briefs**:
  - [`cognitive-tours-understanding-deliverable-swe`](../../research-briefs/cognitive-tours-understanding-deliverable-swe.md) — Preserving human comprehension and productive friction in AI-assisted software engineering
  - [`rag-vulnerability-detection-dissection`](../../research-briefs/rag-vulnerability-detection-dissection.md) — Why LLM/RAG vulnerability *detection* struggles with noisy retrieval and false positives
