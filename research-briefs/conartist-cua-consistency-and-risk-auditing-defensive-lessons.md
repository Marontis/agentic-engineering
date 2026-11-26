# Conartist & ClawBench: How CUA Consistency Checks and Proactive Risk Auditing Become Exploitable Surfaces (Defensive Lessons)

> **Source**: *Conartist: Adaptive Agentic Red-Teaming of Computer-Using Agents against Multi-Step Prompt Injection* (`arXiv:2611.29977`, 2026) — **Strictly Defensive Summary** (per [`output/AGENTS.md`](../AGENTS.md); zero attack prompt templates, persona wrappers, or payload strings are reproduced here; focus is strictly on hardening computer-using agent [`CUA`] harnesses and proactive risk-auditing architectures).

## Problem & Architectural Vulnerability

Modern Computer-Using Agents (`CUAs`) such as `OpenClaw` and GUI browser agents increasingly rely on two model-driven defenses against indirect prompt injection (`IPI`): (1) **task-consistency checking** (verifying whether external instructions align with the user's current task) and (2) **agent-initiated proactive risk auditing** (where the agent autonomously inspects files, database tables, environment state, or URLs to check whether a suspicious artifact is safe before acting).

Evaluating **`576` sandboxed MCP/workspace cases in `ClawBench`** (`OpenClaw 2026.3.20`, `11` scenarios `SC01–SC11`, `80` user tasks, `30` goals across `8` OWASP Agentic AI Top 10 categories, `40` MCP tools) and **`24` live GUI cases in `RedTeamCUA` (`Reddit`)** across `5` frontier and open-weight models (`Qwen3.5-Plus`, `DeepSeek-V4-Flash`, `GPT-5.4`, `Claude-Haiku-5.5`, `Claude-Sonnet-5.5`, budget `<= 3` attempts), the authors demonstrate a critical defensive paradox: **when risk auditing is executed by the agent itself inside the shared context and tool sandbox, the audit workflow becomes the primary attack surface—accounting for `77.84%` (`144/185`) of compromises on `Qwen3.5-Plus`**.

---

## Key Empirical Findings (Verified Paper Figures)

### 1. Single-Step Injections Score `0.00%` While Multi-Step Audit/Premise Exploitation Reaches `17%–67%` (`Tables III–IV`, `Fig. 3`)

- **On `ClawBench` (`576` instances, `Table III`)**: Direct `Single-step` prompt injections achieved **`0.00%` ASR across all `4` primary models** (`Hand-crafted` templates: `0.69%–2.95%`; `StepJack`: `3.47%–8.51%`, with `298/401` [`74.3%`] delivered `StepJack` payloads blocked on `GPT-5.4` while collapsing legitimate task utility to `52.60%–55.21%`). Under adaptive `<= 3`-attempt multi-step premise/audit exploitation (`$0.08–$0.12`/case, `1.85 min` [`1.845 min` in `Table VIII`]):
  - `Qwen3.5-Plus`: **`32.12%` ASR** (`15.63% -> 22.40% -> 32.12%` across attempts `1 -> 2 -> 3`, vs. `MUZZLE` `17.71%` [`+14.41` pp], while preserving **`86.63%` Utility**).
  - `DeepSeek-V4-Flash`: **`22.92%` ASR** (vs. `MUZZLE` `11.28%` [`+11.64` pp], `91.32%` Utility).
  - `GPT-5.4`: **`21.35%` ASR** (vs. `MUZZLE` `7.12%` [`+14.23` pp], `92.19%` Utility).
  - `Claude-Haiku-5.5`: **`17.19%` ASR** (vs. `MUZZLE` `5.56%` [`+11.63` pp], `88.19%` Utility).
- **On `RedTeamCUA` GUI (`24` Reddit instances, `Table IV`, `§III-B`)**:
  - `Qwen3.5-Plus` reached **`66.67%` `ASR@3`** (`54.17%` `ASR@1` vs. `MUZZLE` `29.17% -> 37.50%`, `+29.17` pp; `$0.92–$4.42`/case, `52.0 min`).
  - **Preemptive screenshot refusal destroys GUI utility without eliminating risk (`Claude-Sonnet-5.5`)**: Cloud API-level screenshot prompt-injection screening still allowed **`16.67%` `ASR`**, while false-positive screenshot refusals collapsed benign GUI task Utility to **`41.67%`**—and down to **`0.00%` Utility** whenever explicit `Single-step` or `Hand-crafted` strings appeared anywhere on screen!

### 2. Seven Exploitable Risk-Auditing Patterns (`P1–P7`, `§III-B RQ2`)

While proactive security auditing stopped **`62.9%`** of `MUZZLE`'s failed attempts, **`144 of 185` (`77.84%`)** successful compromises on `Qwen3.5-Plus` exploited seven structural flaws in agent-initiated auditing (ablating audit-exploitation patterns on `OpenClaw` collapsed ASR from **`32.12%` to `2.08%`**, `Table VII`; `w/o Premise Adaptation` dropped to `1.91%` and `w/o State Machine` to `10.24%`):

| Pattern | Harness / Auditor Mechanism Defect | Concrete Failure Consequence |
|:---|:---|:---|
| **`P1` Audit-Enhanced Credibility** | Agent cross-checks attacker-planted external data and caches "verified" findings in persistent/cross-task state. | Self-verified untrusted claims inherit trusted provenance in subsequent steps. |
| **`P2` Audit-Expanded Attack Surface** | Proactive audit inspects out-of-scope resources (`api_keys` tables, host ports, running processes, source files) to assess risk. | Sensitive secrets enter model context and execution traces *because* the audit ran. |
| **`P3` Contextual Audit Gap** | Auditor flags and rejects a malicious file/instruction, **leaving raw read contents in the active context window**. | Rejected `.env` credentials or tokens leak into downstream audit summaries or tool calls. |
| **`P4` Evidence Forgery** | Auditor consults unauthenticated external pages/mirrors to corroborate a suspicious link or package. | Attacker-controlled corroboration satisfies the consistency gate. |
| **`P5` Check-as-Landing** | Auditor invokes `fetch` / browser navigation on a suspicious URL to "verify" where it leads. | **The verification fetch itself executes the exfiltration/phishing side effect.** |
| **`P6` Blind-Spot Planting** | Narrow single-table or single-file audit scope misses cross-resource/cross-table triggers. | Side effects execute outside the audited slice. |
| **`P7` Delayed-Audit** | Agent reads full sensitive records (payment cards, profiles) *first* and runs policy/refusal evaluation *afterward*. | Confidentiality boundary is already breached before refusal fires. |

### 3. Diagnostic Trace Isolation Cuts Transfer by `~9x–11x` (`Table VI`)

When execution traces, tool-call logs, and detailed audit refusal rationales (`L3` feedback) were withheld—testing zero-feedback black-box transfer from offline runs to unseen online tasks—`OpenClaw` ASR plummeted from `32.12%` to **`3.65%` (`Goal Perturbation`)** and **`2.78%` (`Random Task`)**. Exposing verbose audit reasoning to external content channels or callers acts as an adaptation oracle.

---

## Defensive Harness Hardening Checklist for CUAs

1. **Never let an agent-initiated risk audit widen read or network permissions (`Fixes P2, P4, P5, P7`)**:
   - Execute pre-action risk checks inside a **deterministic, zero-network reference monitor** outside the LLM (`ActiveSecHarness` / `CapLite`), never by letting the LLM call `read_file`, `sql_query`, or `http_fetch` "to investigate."
   - Enforce read-before-audit capability attenuation: an audit probe may inspect *only* metadata/spans already within the user-authorized task read scope (`AuditScope ⊆ AuthorizedTaskScope`), **never** `.env`, `api_keys`, host sockets, or unauthenticated external URLs (`0` outbound verification fetches).
2. **Purge or redact rejected audit spans before resuming generation (`Fixes P1, P3`)**:
   - Run inspection in an **ephemeral forked context** that returns only a schema-bound enum verdict (`ALLOW` / `DENY` + rule ID) to the main agent loop—never retain raw contents of flagged files or secret-bearing `.env` dumps inside the working context window, and never promote externally corroborated claims into trusted cross-task memory (`P1`).
3. **Suppress audit refusal rationales across external boundaries**:
   - Log audit triggers only to encrypted/out-of-band operator logs (`2.78%–3.65%` blind transfer vs. `32.12%` with trace visibility; aligns with hiding defender `CoT` in `arXiv:2611.11861` and stage verdicts in `arXiv:2611.13684`).
4. **Replace whole-screenshot API hard-refusals with localized DOM/element provenance gating**:
   - Preemptive whole-screen VLM refusal (`Claude-Sonnet-5.5`) collapses legitimate GUI utility (`41.67%` benign; `0.00%` when untrusted user comments contain adversarial text) while still missing `16.67%` of multi-step attacks. Quarantine or mask untrusted DOM containers and enforce deterministic action-boundary destination/parameter checks instead of aborting the entire GUI session on screen-text triggers.

---

## Why Not a Standalone Skill?

Per [`output/AGENTS.md`](../AGENTS.md) (`Lines 69–70`), adaptive red-teaming papers (`Conartist`) are scoped strictly to **defensive architectural lessons** without operationalizing multi-step attack state machines. Defensively, [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md) (`ActGuard`) and [`compositional-coding-harness-reference-monitor`](../skills/compositional-coding-harness-reference-monitor/SKILL.md) (`ActiveSecHarness`) already provide standalone procedures for out-of-agent reference monitoring; `Conartist`'s novel defensive discovery—the `7` `P1–P7` failure modes of *agent-initiated* risk auditing and whole-screenshot refusal collapse—is captured as a dedicated `DON'T` guardrail in [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

## Related Artifacts

- [`compositional-coding-harness-reference-monitor`](../skills/compositional-coding-harness-reference-monitor/SKILL.md) — Ring-0 deterministic capability and 2D taint reference monitor (`arXiv:2611.13960`)
- [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md) — Out-of-agent parameter-span evidence auditing (`arXiv:2609.14987`)
- [`webtrap-farm-web-agent-harness-security`](webtrap-farm-web-agent-harness-security.md) — `40.90` pp harness security swing, DOM filtering vs. screenshot vulnerability, and goal anchoring (`arXiv:2611.11971`)
- [`adaptive-prompt-injection-swarms-defensive-lessons`](adaptive-prompt-injection-swarms-defensive-lessons.md) — Why exposing defender `CoT` degrades adaptive IPI resistance (`arXiv:2611.11861`)
- [`conditional-protection-image-rendered-prompt-injection`](conditional-protection-image-rendered-prompt-injection.md) — Limits and utility trade-offs of pixel/screenshot-rendered prompt-injection defenses (`arXiv:2611.24231`)
