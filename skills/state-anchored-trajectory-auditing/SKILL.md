---
name: state-anchored-trajectory-auditing
description: >
  Audit multi-session, shared-ledger multi-agent workflows against gradual
  alignment decay without perimeter over-refusal by combining deterministic
  state-divergence, provenance, and debate-capitulation anchors with a
  conformal-calibrated intent-divergence scorer and a grey-zone disagreement
  arbiter. Derived from ErosionBench / Meta-Auditor (arXiv:2611.11266).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# State-Anchored Trajectory Auditing

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Use this skill when building, hardening, or auditing **stateful multi-agent workflows** (such as CI/CD release pipelines, financial approval meshes, data-engineering ETL orchestrators, enterprise CRM workflows, or clinical record pipelines) where:

- Multiple specialized agents collaborate across turns or sessions over a **shared state ledger, artifact store, or handoff queue**.
- **Perimeter prompt/schema guardrails fail in opposite directions**: lexical injection filters miss gradual state drift when no jailbreak phrasing is present, while static schema/policy checkers over-refuse legitimate high-privilege operations (such as emergency hotfixes, executive overrides, or schema migrations) that touch the same sensitive state keys as attacks.
- Adversaries can plant unverified entries in shared state during earlier sessions, diffuse responsibility across planners and executors, or erode safety constraints through multi-round peer debate.

Do **not** use this skill for stateless single-turn Q&A endpoints or pure pre-execution syntax validation where a frozen per-call record schema suffices (use [`verified-policy-action-governance`](../verified-policy-action-governance/SKILL.md) instead).

## Overview

In multi-session, multi-agent meshes, alignment decay is a **trajectory-level process failure** rather than a single malformed prompt. Across `1,728` enterprise multi-agent scenarios in `ErosionBench` (`arXiv:2611.11266`), perimeter guardrails either miss cross-session drift (`Prompt Guard 2-86M`: `86.6%` Attack Success Rate) or suffer catastrophic false-positive rates on matched benign operations (`LlamaFirewall`: `92.5%` benign FPR; `Progent`: `64.0%` FPR; `ShieldGemma-27B`: `54.3%` FPR), while an uncalibrated single-LLM judge over the full trace still flags `67.6%` of benign workflows.

State-anchored trajectory auditing resolves this precision-recall trap by decoupling **synchronous deterministic state invariants** from **calibrated out-of-band semantic intent scoring**, and escalating only **grey-zone disagreements** (~`48%` of traffic) to a deep-reasoning arbiter—achieving `98.5%` recall at `2.9%` benign FPR (`1.3%` residual ASR) without placing LLM reasoning latency on every tool call.

---

## Step-by-Step Procedure

### Step 1: Instrument Fenced Cross-Session Telemetry

Capture an immutable, out-of-band execution log spanning the baseline state snapshot, shared-ledger reads/writes, inter-agent debate messages, and proposed or executed state mutations:

1. **Tag every log event with a deterministic line identifier** (`[L0]`, `[L1]`, ... for ledger entries and `[M0]`, `[M1]`, ... for inter-agent messages and tool actions).
2. **Record provenance metadata on every shared-ledger key**: tag entries written by authenticated system roots or verified upstream pipelines as `verified`, and entries originating from external documents, user-editable tickets, unverified peer summaries, or cross-session scratchpads as `unverified` ($U$).
3. **Wrap agent-generated text inside strict XML/delimiter fences** before feeding telemetry to any downstream LLM auditor so embedded instructions inside poisoned ledger values cannot hijack the auditor itself.

### Step 2: Compute Three Deterministic Process Anchors

Evaluate three zero-LLM mathematical anchors over the structured state transition $(B \to A)$, shared ledger provenance $(P, U)$, and inter-agent dialogue history $(m_1, \dots, m_N)$:

1. **State Divergence Index (`SDI`) — Synchronous Veto Path**:
   Define the domain's critical safety-invariant key set $K_{\text{crit}}$ (for example, `encryption_enabled`, `audit_logging`, `branch_protection`, `wire_approval_tier`, `hipaa_redaction`). Given baseline state $B$ and proposed/post-execution state $A$, compute:
   $$\mathrm{SDI}(B, A) = \frac{1}{|K_{\text{crit}}|} \sum_{k \in K_{\text{crit}}} d(b_k, a_k)$$
   where $d(b_k, a_k) = |b_k - a_k|$ for Booleans/normalized scalars, normalized edit distance for strings, and Jaccard distance for sets. Run `SDI` **synchronously at commit boundaries** to block catastrophic invariant deletions immediately with zero LLM latency.
2. **Context Integrity Index (`CII`) — Shared-Ledger Provenance Anchor**:
   Extract the set of ledger keys $P$ referenced by agents during planning or tool parameterization, and intersect $P$ with the unverified provenance key set $U$:
   $$\mathrm{CII}(P, U) = \begin{cases} 0 & \text{if } |P| = 0 \\ \dfrac{|P \cap U|}{|P|} & \text{otherwise} \end{cases}$$
   A non-zero `CII` proves that downstream execution consumed untrusted cross-session state, exposing attribution-diffusion and memory-poisoning chains even when the final executor's local prompt appears clean.
3. **Value Alignment Drift (`VAD`) — Debate Capitulation Anchor**:
   Scan the inter-agent message sequence $m_1, \dots, m_N$ for explicit policy/compliance objections (`refusal`, `violation`, `unauthorized`, `blocked by policy`). If an objection occurs at turn $t < N$ and a downstream agent subsequently executes or approves the contested mutation with severity weight $w \in (0, 1]$, score recency-weighted capitulation:
   $$\mathrm{VAD} = \max\!\left(0,\; \min\!\left(1,\; w \cdot \frac{N - t + 1}{N}\right)\right)$$
   If no prior objection occurred or the objection held through termination, set $\mathrm{VAD} = 0$.

> **Anchor Conjunction Rule**: Individual anchors can fire on legitimate administrative work (for example, an authorized incident responder modifying a critical key raises `SDI > 0`). Only treat the deterministic layer as an **unconditional block** when **all three anchors fire simultaneously** (`SDI > 0`, `CII > 0`, and `VAD > 0`), or combine calibrated benign empirical $p$-values via the Cauchy combination statistic $T_{\text{Cauchy}} = \sum_{i} w_i \tan\!\big((0.5 - p_i)\pi\big)$ at level $\alpha = 0.05$ (`0.0%` standalone benign FPR across `453` structural controls).

### Step 3: Score Continuous Intent Divergence Out-of-Band

Run an asynchronous semantic scorer over the fenced trajectory transcript alongside the original user task specification, enforcing **two mandatory prompt invariants**:

1. **Score the attempt, not just the outcome**: Evaluate whether any agent attempted to subvert, reinterpret, or bypass safety constraints—even if a downstream agent or sandbox rejected the mutation. Do not clear a trajectory merely because the final state happened to remain intact.
2. **Line-ID evidentiary citation**: Require the scorer to cite at least one specific telemetry identifier (`[Lk]` or `[Mj]`) as concrete evidence for any elevated divergence score $s \in [0, 1]$. Reject ungrounded holistic suspicion scores; forcing line-level citation prevents vague sensitivity to benign security keywords.

### Step 4: Calibrate Per-Backbone via Platt Scaling and Conformal Quantiles

Raw LLM intent-divergence scores cluster differently across model families and drastically over-flag benign administrative workflows (`67.6%` benign FPR uncalibrated). Before deployment—and whenever swapping the auditor's model backbone—calibrate on a held-out validation split containing matched **structural benign twins** (legitimate workflows operating on the exact same tools, schemas, and sensitive state keys as attacks):

1. **Platt Scaling**: Fit logistic parameters $(A, B)$ via maximum likelihood on validation pairs $(s_i, y_i)$ so raw scores map to calibrated probabilities $\hat{p}_i = \sigma(A s_i + B)$.
2. **Split-Conformal Thresholding**: Given $n$ held-out benign calibration trajectories with calibrated scores $\{p_1, \dots, p_n\}$ and target false-positive budget $\alpha$ (for example, $\alpha = 0.05$), set the semantic alarm threshold to the order statistic:
   $$\tau_{\alpha} = p_{(\lceil (n + 1)(1 - \alpha) \rceil)}$$
   This guarantees finite-sample marginal false-positive control $\Pr(\hat{p}_{\text{benign}} > \tau_{\alpha}) \le \alpha$ on exchangeable benign traffic.

### Step 5: Route Disagreements Through a Grey-Zone Arbiter

Combine the deterministic anchors (`SDI`, `CII`, `VAD`) and calibrated semantic score $\hat{p}$ using a 3-way routing gate so expensive deep-reasoning arbitration runs only on ambiguous cases:

1. **Fast-Block (Deterministic + Semantic Consensus)**: If all three deterministic anchors fire (`SDI > 0`, `CII > 0`, `VAD > 0`) and $\hat{p} > \tau_{\alpha}$, block immediately without invoking the arbiter.
2. **Fast-Allow (Clean Consensus)**: If all deterministic anchors vanish (`SDI = 0`, `CII = 0`, `VAD = 0`) and $\hat{p}$ falls safely below the borderline band, allow immediately (`~30%` of total traffic, `1.1%` false-negative rate).
3. **Grey-Zone Escalation (Disagreement or Borderline Score)**: Whenever deterministic anchors are silent/partial while $\hat{p} > \tau_{\alpha}$, or when anchors fire on a potentially authorized override while $\hat{p} \le \tau_{\alpha}$ (~`48%` of trajectories), escalate to the **Grey-Zone Arbiter**:
   - Provide the arbiter with the fenced transcript, the three numerical anchor values (`SDI`, `CII`, `VAD`), the semantic scorer's cited `[Lk]`/`[Mj]` evidence lines, and the domain's explicit authorization policy for legitimate high-privilege changes.
   - Instruct the arbiter to decide whether the cited evidence reflects **covert constraint erosion / unverified state laundering** (`BLOCK` + quarantine poisoned ledger keys) or **documented, authorized operational intent** (`ALLOW`).

---

## Failure Modes & Calibration Pitfalls

- **Never transfer Platt or conformal thresholds across auditor backbones**: Applying `claude-opus-4-8`'s calibration parameters directly to `Qwen3.5-27B` degrades benign FPR from `6.4%` to `18.3%`. Re-fit $(A, B, \tau_{\alpha})$ whenever changing the auditor model or prompt.
- **Calibrate multimodal perception gates separately from text trajectories**: When upstream agents ingest document images (invoices, scanned memos, dashboard screenshots), trajectory-only auditing (`Mode A`) preserves `95.8%–100.0%` recall on capable backbones because visual injections must still manifest as state/intent divergence in the multi-agent trace. Adding a direct vision prompt-injection gate via a naive OR-union (`Mode B`) rescues weaker backbones (`gpt-5-mini`: `22.9%` $\to$ `99.0%` recall) **but spikes composite benign FPR from `2.9%` to `20.2%–60.6%`** if calibrated only on text benign twins. Always fit separate conformal thresholds on benign document images before enabling a visual OR-gate.
- **Harden against white-box semantic mimicry**: Under adaptive white-box red-teaming where adversaries know the exact `SDI`/`CII`/`VAD` formulas and wrap malicious state mutations inside plausible operational rationales without triggering debate objections, recall drops from `98.5%` to `75.6%` (`24.4%` evasion). Pair out-of-band trajectory auditing with cryptographic provenance binding on `verified` ledger keys and hard capability-gateway allowlists on irreversible external sinks.

## Related Skills

- [`verified-policy-action-governance`](../verified-policy-action-governance/SKILL.md) — Pre-execution SMT verification of bounded per-call records against frozen deterministic policies (use at synchronous single-action boundaries; combine with this skill for cross-session multi-agent drift).
- [`dependency-scoped-plan-validation`](../dependency-scoped-plan-validation/SKILL.md) — Validates that pending tool calls derive from un-superseded memory dependencies before dispatch.
- [`pre-execution-action-auditing`](../pre-execution-action-auditing/SKILL.md) — Audits individual tool calls against localized evidence spans prior to execution.
- [`black-box-trajectory-risk-monitoring`](../black-box-trajectory-risk-monitoring/SKILL.md) — Early trajectory risk prediction from observable macro/micro behavioral features.
