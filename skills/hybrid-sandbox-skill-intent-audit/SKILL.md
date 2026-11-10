---
name: hybrid-sandbox-skill-intent-audit
description: >
  Audit third-party or candidate Markdown agent skills (`SKILL.md` bundles)
  before admission by combining severity-curated static pattern extraction,
  safety-constrained dry-run sandbox execution with provenance-weighted
  evidence multipliers, and bounded retrieval-augmented multi-agent
  adjudication emitting line-cited SARIF reports. Eliminates alert-count
  inversion and cuts false positives by 87.5% over standalone static+LLM
  skill scanners. Derived from The Devil Wears Markdown (arXiv:2611.10830).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Hybrid Sandbox Skill Intent Audit

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Agent skill packages (`SKILL.md` instructions paired with helper scripts and references) blur documentation and executable directives: malicious instructions masquerade as setup prerequisites, administrative recipes, or troubleshooting steps, while benign developer and security skills legitimately mention `curl`, shell pipelines, API keys, and system utilities. As a result, raw static alert counts invert on real-world skill corpora—benign skills trigger *more* alerts on average than malicious skills (`11.70` vs. `6.34` on `OSS-Detect-Backdoor`, `F1 = 0.42`; `105.78` vs. `60.05` on `YARA`, `FPR = 0.82`)—and passing static rule hits alone to an LLM reviewer collapses recall from `0.68` to `0.35` (`F1 = 0.50`) because benign-looking stealth instructions produce few high-severity static matches.

This skill specifies a three-layer pre-admission audit workflow that pairs severity-curated static provenance extraction with a **safety-constrained dry-run sandbox** (which blocks harmful actions while logging attempted intent and weighting observations by source-to-trace provenance) and a **bounded retrieval-augmented agentic adjudicator** that emits line-cited `SARIF 2.1.0` reports (`F1 = 0.89`, `Precision = 0.93`, `Recall = 0.85`, `FPR = 0.08` across `140` held-out skills).

## When to Use

- **Skill marketplace and registry ingestion gates** — screening community-submitted `SKILL.md` bundles before indexing or publishing them.
- **Enterprise CI/CD repository security checks** — producing line-anchored `SARIF 2.1.0` findings on pull requests that add or update `.agents/skills/`, `.claude/skills/`, or MCP companion instructions.
- **Autonomous skill-evolution quarantine pipelines** — vetting externally retrieved or agent-synthesized candidate skills before passing survivors to downstream dependency-graph and acceptance gates.

## When Not to Use

- **Cross-skill composition hazards across an installed library** — this workflow audits one candidate skill package in isolation. Pair it with [`composite-skill-vulnerability-scanner`](../composite-skill-vulnerability-scanner/SKILL.md) to detect multi-skill taint chains (`66.3%` of composite vulnerabilities arise from individually benign skills).
- **Sole defense without provenance or runtime containment** — even the full hybrid pipeline misses `15%` (`12/80`) of malicious skills on held-out evaluation, and adaptive attackers with repeated scanner oracle access can optimize around pre-execution checks (`3.23` rounds mean in `SkillDRE`; see [skill-scanner-evasion-defensive-lessons](../../research-briefs/skill-scanner-evasion-defensive-lessons.md)). Always enforce provenance checks and per-task runtime sandboxing per [`rules/skill-system-design.md`](../../rules/skill-system-design.md).
- **Sub-second inline request filtering** — full dynamic + agentic adjudication takes roughly `2–7` minutes per skill (`300 s` sandbox cap + `109.35 s` median agentic adjudication); run asynchronously at ingestion or PR time rather than on synchronous user chat turns.

## Prerequisites

1. **Curated static rule set**: Regex and YARA/AST rules mapped to explicit `Low`, `Medium`, and `High` severity tiers (deduplicated and pruned of noisy generic prose matches).
2. **Isolated ephemeral container runtime**: Non-root user (`appuser`), read-only mount of the candidate skill copied into a disposable workspace (`/home/appuser/workdir`), hard wall-clock timeout (`300 s`), syscall tracing (`strace`), packet capture (`tcpdump`), and filesystem snapshot diffing across `/home/appuser`, `/tmp`, and `/var/tmp`.
3. **Threat-intelligence vector store**: Indexed skill-abuse patterns, OWASP Agentic Security Top 10 (`AST01`), and CWE/MITRE ATT&CK references for bounded RAG lookup.

---

## Procedure

### Step 1: Extract Provenance-Preserving Static Findings (Never Threshold Raw Counts)

1. Deduplicate the candidate skill bundle (e.g., by canonical content hash) and enumerate `SKILL.md` plus all bundled scripts, templates, and hidden/Unicode-normalized text.
2. Run curated static pattern and YARA rules classified into `Low`, `Medium`, and `High` severity tiers (for example, `58,674` curated rules distilled from `115,209` raw rules after removing noisy duplicates and reassigning severities).
3. Record every match with its exact file path, line span, matched snippet, rule identifier, and severity tier.
4. **Do not emit a binary pass/fail verdict from static alert totals**, and **do not forward static findings to an LLM adjudicator without dynamic behavioral evidence**—doing so biases the adjudicator toward false negatives when stealth instructions avoid obvious exploit keywords (`Recall` drops from `0.68` to `0.35`). For deeper AST/dataflow taint extraction on bundled scripts, combine this stage with Phase 1 of [`evidence-guided-skill-audit`](../evidence-guided-skill-audit/SKILL.md).

### Step 2: Run a Safety-Constrained Dry-Run Sandbox

1. Boot a fresh, unprivileged container (`appuser`) and stage a read-only copy of the candidate skill into the agent's skill directory alongside a disposable working directory (`/home/appuser/workdir`) populated only with synthetic fixture files and decoy non-production environment tokens.
2. Invoke a sandboxed executor agent under a hard timeout (`300 s`) to interpret and dry-run the skill's primary workflow under an **explicit safety-constrained execution policy**:
   - **Permit** benign local setup, parsing, dry-run validation, and read-only inspection inside `/home/appuser/workdir`.
   - **Intentionally intercept, skip, and log with explicit block reasons** any unsafe primitive: reading host/user credentials (`~/.ssh`, `~/.aws`, secret env vars), external data exfiltration, persistence modification (`crontab`, shell profiles, startup hooks), disabling security controls (`verify=False`, `chmod 777`, firewall edits), or fetching and executing unverified remote payloads (`curl ... | bash`).
3. Collect four synchronized runtime artifacts at container exit:
   - `agent_output.txt` — executor reasoning, tool calls, and safety-policy skip/block explanations.
   - `strace.log` — process execution and file/socket system calls.
   - `network.pcap` — DNS lookups and outbound connection attempts.
   - `filesystem_changes.json` — pre/post snapshot diffs over `/home/appuser`, `/tmp`, and `/var/tmp`.

### Step 3: Score Dynamic Telemetry with Provenance-Weighted Multipliers

Map every candidate behavioral indicator extracted from the four sandbox artifacts to a base pattern severity (`40` Low, `70` Medium, `100` High) and multiply it by a **provenance multiplier** reflecting how strongly the runtime trace connects back to the skill's source instructions:

| Provenance Tier | Multiplier | Guardrail Cap / Floor | Meaning |
|:---|:---:|:---:|:---|
| **Ungrounded narrative** | `0.45` | Cap `<= 25` | Mentioned only in executor prose without concrete skill-source or trace support |
| **Supporting intent only** | `0.50` | Cap `<= 25` | Auxiliary setup/context reference without an unsafe operational target |
| **Intent only** | `0.55` | Cap `<= 30` | Executor planned an action without source-anchored hazardous primitive |
| **Grounded intent** | `0.70` | None | Planned action anchored to specific lines in `SKILL.md` or bundled scripts |
| **Strong intent only** | `0.85` | Floor `>= 85` | Source-grounded hazardous primitive (e.g., exfiltration or remote script pipe) intentionally blocked by the sandbox safety policy |
| **Executed** | `1.00` | None | Hazardous behavior directly observed in `strace.log`, `network.pcap`, or `filesystem_changes.json` |
| **Corroborated** | `1.15` | Cap `<= 100` | Source-grounded instruction corroborated across multiple runtime telemetry channels |

Aggregate deduplicated evidence groups into a raw dynamic risk score:
$$S_{\mathrm{raw}} = \min\!\Big(100,\; e_{\max} + \lambda \sum_{i \neq \max} e_i + B(C)\Big)$$
with $\lambda = 0.1$ and cross-category diversity bonus $B(C) \in \{0, 5, 10, 15\}$ across distinct threat categories $C$ (disable $B(C)$ whenever a directly executed malicious behavior is already present so single executed exploits are not double-counted). Flag dynamic telemetry above `35.0` as high-risk behavioral evidence and pass the full provenance breakdown—including what was *attempted and safely blocked* versus *unexecuted prose*—to Step 4.

### Step 4: Adjudicate via Bounded Threat-Grounded Multi-Agent Review

1. Assemble a structured evidence dossier containing: (a) full `SKILL.md` and script contents, (b) severity-curated static matches from Step 1, and (c) the provenance-weighted dynamic trace summary and `S_raw` breakdown from Step 3.
2. Run a **Planner–Worker–Evaluator** adjudication loop strictly bounded to **at most 3 retrieval rounds**:
   - **Planner**: Decomposes ambiguous discrepancies between declared skill purpose and static/dynamic evidence into targeted verification questions (e.g., whether an outbound endpoint or API key read is a documented vendor SDK requirement vs. covert exfiltration).
   - **ReAct Retrieval Workers**: Query the threat-intelligence vector store (OWASP `AST01`, known malicious skill templates, CWE/ATT&CK mappings) and inspect referenced file/line spans.
   - **Early-Stop Rule**: Terminate immediately on Round 1 when corroborated RCE, credential theft, or unauthorized exfiltration is unambiguous.
   - **Vendor-Bootstrap Disambiguation Check**: Before labeling `curl | bash` installers or named API key reads (e.g., `OPENROUTER_API_KEY`) as malware when `S_raw < 35.0`, verify whether the domain/key matches the skill's declared first-party vendor documentation and emit a `supply-chain-risk / unpinned-bootstrap` warning rather than conflating unpinned vendor setup with active trojan intent.
3. **Escalation & Final Gate**:
   - If Planner and Evaluator remain unresolved after `3` rounds, route the dossier to **human security review** rather than auto-approving.
   - Emit a `SARIF 2.1.0` report binding every finding to exact file paths, line numbers, static rule IDs, and runtime trace artifacts.
   - If this audit runs inside an autonomous skill-acquisition or self-evolving harness, treat a clean `SARIF` verdict as a **necessary pre-filter**, and pass surviving skill candidates through `"DO: Pass every self-modification through one acceptance gate"` in [`rules/recursive-improvement.md`](../../rules/recursive-improvement.md) as well as cross-skill dependency verification ([`composite-skill-vulnerability-scanner`](../composite-skill-vulnerability-scanner/SKILL.md)).

---

## Concrete Empirical Reference (`arXiv:2611.10830`)

Evaluated on `140` held-out skills (`80` malicious, `60` benign) stratified from a SHA-256 deduplicated `700`-skill corpus (`MalSkillBench`, `Datadog AI-Skills`, `VoltAgent Awesome Agent Skills`):

| Pipeline Configuration | Precision | Recall | F1 | FPR (`FP / 60`) | FN (`/ 80`) | Median Agentic Latency |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `OSS-Detect-Backdoor` (alert threshold `>= 6`) | `0.61` | `0.33` | `0.42` | `0.28` (`17`) | `54` | — |
| `YARA` (alert threshold `>= 11`) | `0.60` | `0.91` | `0.72` | `0.82` (`49`) | `7` | — |
| `Cisco Skill Scanner` (static, threshold `>= 1`) | `0.69` | `0.91` | `0.79` | `0.55` (`33`) | `7` | — |
| `Cisco Skill Scanner + LLM` (`Qwen3:8B` `is_safe`) | `0.63` | `0.85` | `0.72` | `0.67` (`40`) | `12` | — |
| Agentic (`Qwen3.5 122B`) — **Skill content only** | `0.72` | `0.68` | `0.70` | `0.35` (`21`) | `26` | `319.95 s` |
| Agentic — **+ Static evidence only** | `0.90` | `0.35` | `0.50` | `0.05` (`3`) | `52` | `94.75 s` |
| Agentic — **+ Dynamic sandbox evidence only** | `0.93` | `0.79` | `0.85` | `0.08` (`5`) | `17` | `89.45 s` |
| **Full Hybrid Pipeline (Static + Dynamic + Agentic)** | **`0.93`** | **`0.85`** | **`0.89`** | **`0.08` (`5`)** | **`12`** | **`109.35 s`** (+ `<= 300 s` sandbox) |

## Failure Modes & Mitigations

- **Static-only evidence anchoring (`Recall 0.68 -> 0.35`)**: Feeding static regex/YARA hits to an LLM judge without sandbox execution causes the judge to equate "zero high-severity static hits" with benignity, missing `52/80` malicious skills written in natural prose. *Mitigation*: Never run Step 4 with static evidence alone; require Step 2–3 dynamic telemetry.
- **Unpinned vendor bootstrap false positives (`research-lookup` failure case)**: Benign skills that instruct agents to install official vendor CLIs via `curl -fsSL https://<vendor>/install.sh | bash` and read documented API keys can trigger high-confidence `malware` verdicts even when dynamic `S_raw` is sub-threshold (`27.5 < 35.0`). *Mitigation*: Separate `unpinned-supply-chain-bootstrap` policy violations (remediated by pinning digests/packages) from `confirmed-malicious-intent` verdicts when `S_raw < 35.0` and all endpoints match declared vendor domains.
- **Dormant environment-triggered payloads (`12/80` FN)**: Payloads gated on specific hostnames, dates, or live production repositories remain inactive during a `300 s` synthetic dry-run. *Mitigation*: Enforce runtime capability scoping and network/filesystem sandboxing on all admitted skills in production.

## Related Skills & Rules

- [`evidence-guided-skill-audit`](../evidence-guided-skill-audit/SKILL.md) — Static AST/dataflow evidence pack construction for single-pass offline skill review when container sandboxes are unavailable.
- [`composite-skill-vulnerability-scanner`](../composite-skill-vulnerability-scanner/SKILL.md) — Dependency-multigraph (`G_0`) auditing for cross-skill privilege escalation and taint flows.
- [`skill-evolution-defense`](../skill-evolution-defense/SKILL.md) — Provenance tracking and quarantine governance for self-evolving skill libraries.
- [`rules/skill-system-design.md`](../../rules/skill-system-design.md) — Skill provenance and multi-layer admission guardrails.
- [`rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`.
