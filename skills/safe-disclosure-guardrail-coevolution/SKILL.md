---
name: safe-disclosure-guardrail-coevolution
description: >
  Decouple runtime action-guardrail verdicts from public rejection explanations (`Decide-then-Disclose`)
  and co-evolve compact natural-language decision and safe-disclosure skills offline on authorization-matched
  twin pairs against sequential refusal-reading adversaries, recovering benign compound tasks without
  exposing adaptation oracles.
source: "arXiv:2611.33879"
repository: Marontis/agentic-engineering
license: CC-BY-4.0
---
<!-- License: CC BY 4.0 | Repository: https://github.com/Marontis/agentic-engineering -->

# Safe-Disclosure and Decision Skill Co-Evolution for Action Guardrails

## When to Use

Use this procedure when deploying or hardening an LLM-based pre-execution action guardrail (`G_FORK`) around tool-calling agents where:
- Untrusted external content (emails, documents, tickets, Slack messages, webpages) or direct callers can **observe public rejection explanations or outward agent replies across multiple attempts**, turning verbose refusal rationales into an iterative bypass oracle.
- Legitimate user tasks frequently trigger benign false blocks or mixed benign-plus-injected compound tool calls, so **silent binary blocking strands recovery** while **prompt-only explanatory refusals increase adaptive Attack Success Rate (`ASR`)**.
- You want a **portable, model-agnostic natural-language skill bundle** (`decision` + `disclosure` rules, frozen at deployment) rather than per-backbone guardrail weight fine-tuning.

**Do NOT use when:**
- The caller's **own primary goal** directly violates policy (`EvasionBench`, [`../../research-briefs/instrumental-monitor-evasion.md`](../../research-briefs/instrumental-monitor-evasion.md)) or optimizes endpoint-defense evasion (`BypassGym`, [`../../research-briefs/bypassgym-edr-evasion-defensive-lessons.md`](../../research-briefs/bypassgym-edr-evasion-defensive-lessons.md)): when `Q_t = \emptyset` (unauthenticated/rogue caller) or the same forbidden target is retried repeatedly, return opaque denials and terminate/escalate the session (`"DO: Give blocking action monitors recent call history, and make denials terminal"` in [`../../rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md)).
- You need sub-`5 s` on-device mobile screenshot gating with `1.6B–2B` VLMs where cloud LLM calls are unacceptable: use [`bounded-context-intervention-window-guardrail`](../bounded-context-intervention-window-guardrail/SKILL.md) (`MobileGrail`, `arXiv:2611.29847`) instead.
- Deterministic schema, capability, or principal-permission invariants suffice without LLM judgment: enforce those first in code via [`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md) or [`principal-context-permission-intersection`](../principal-context-permission-intersection/SKILL.md).

## Core Insight

Static single-turn benchmarks dramatically understate adaptive risk: in `FORK` (`arXiv:2611.33879`), frontier agents (`Claude Sonnet 4.5`, `GPT-5.6-Sol`) that suffered only **`0.1%–0.2%` unguarded `ASR`** on static `AgentDojo` jumped to **`66.3%–73.9%` unguarded `ASR`** (`78.4%` `3`-agent mean including `Qwen3-Next-80B` at `95.0%`; **`55.0%` `ASR`** even behind the strongest baseline `TS-Guard`) on `FORK-World` (`474` verified-user scenarios) when an online attacker adapted over `5` sequential attempts after reading public refusals.

Prompting a guardrail to *"explain rejections safely"* without learned skills (**`Explanatory seed`**) **backfires**, raising verified-user `FORK-World` `ASR` on `Qwen3-Next-80B` + `Qwen3-32B` from **`30.3%` (`Silent seed`) to `39.3%` (`+9.0` pp)** for only `+1.5` pp Utility under Attack (`UA`: `58.6% -> 60.1%`) because unguided explanations inadvertently name confidential boundaries or suggest forgeable confirmation steps. **`FORK`** resolves this tradeoff by (1) enforcing a runtime **`Decide-then-Disclose`** split that freezes the binary verdict $d$ using **decision skills** ($S_{\mathrm{dec}}$) *before* drafting a public rejection $e_{\mathrm{usr}}$ constrained by **disclosure skills** ($S_{\mathrm{dis}}$) while keeping operator audit rationales $e_{\mathrm{op}}$ strictly private, and (2) co-evolving $S_{\mathrm{dec}}$ and $S_{\mathrm{dis}}$ offline once on **`65` verified-user twin pairs** (`4` `SHADE-Arena` worlds) against trajectory-reading attackers via maximin/PSRO checkpoint selection. Frozen at `4` compact skills ($D_4$), `FORK (Sonnet 4.5)` cut `3`-agent verified-user `FORK-World` `ASR` from **`78.4%` to `14.1%`** (`-64.3` pp vs. unguarded; `-40.9` pp vs. `TS-Guard`'s `55.0%`) while preserving **`87.1%` Benign Utility (`BU`, `-0.5` pp cost)**, lifting `Qwen3-Next-80B` post-rejection **Recovery Rate (`RR`) from `38.5%` (`Silent`) and `58.1%` (`+Decision`) to `79.2%`** (`UA` `64.0% -> 86.1%`, `ASR` `22.8% -> 22.1%`), cutting guardrail/tool calls per success to **`26.4 / 19.0`** (`-23.5% / -23.1%` vs. `Silent` in `Table 4`; `-26.7% / -26.4%` vs. `+Decision` in `§4.4` prose), and transferring zero-shot to unseen `MT-AgentRisk` (**`70.6% -> 9.1%` `3`-agent `ASR` at `93.1%` `BU`**).

## Step-by-Step Procedure

### Step 1: Enforce Runtime Provenance Tagging and Untrusted Data Fencing at Ingress

Before invoking the guardrail on any pending tool call or outward user-facing reply $u \in U_t$:
1. **Capture immutable trusted context $c = (P_{\mathrm{agent}}, P_{\mathrm{sys}}, Q_t)$ outside model control**: Record the authenticated first-party user request set $Q_t$ directly at trusted channel ingress. Under unauthenticated, external-webhook, or rogue-caller threat models, set $Q_t = \emptyset$ so caller turns never inherit verified user authority.
2. **Tag trajectory provenance deterministically**: Mark each historical user/instruction turn in $h_{t-1}$ as **`VERIFIED`** if and only if its text matches an entry in $Q_t$, and **`NOT VERIFIED`** otherwise. Wrap all external tool returns, retrieved documents, and unverified strings inside explicit data delimiters (`[[data: ... ]]`) and strip raw agent chain-of-thought from external-facing logs.
3. **Pass sibling batch context and prior episode rulings**: Supply the guardrail with `(u, sibling_calls = U_t \ {u}, h_{t-1}, prior_rulings = r_{t-1}, c)` so split/batched exfiltration across parallel tool calls and repeated probing across turns are visible together.

### Step 2: Execute the Single-Call `Decide-then-Disclose` Runtime Split

Structure every guardrail invocation so verdict determination precedes and constrains explanation drafting, emitting `(decision, e_op, e_usr)`:
1. **Freeze `decision` ($d \in \{\mathrm{approve}, \mathrm{reject}\}$) and private `e_op` first**: Evaluate $u$ against trusted scope $Q_t$, untrusted data provenance, sibling batch calls, and $S_{\mathrm{dec}}$ (`Applies when` / `Does not apply when` / `Action`). Record detailed rule matches, sensitive attribute hits, and forensic evidence **only** in the private operator log `e_op`, which is never returned to the agent, tool server, or caller.
2. **Draft `e_usr` strictly after `d` is fixed**:
   - If $d = \mathrm{approve}$, return `e_usr = ""` (empty public message) and dispatch $u$.
   - If $d = \mathrm{reject}$, draft `e_usr` under $S_{\mathrm{dis}}$ (`Applies when` / `Say` / `Avoid`) subject to three hard invariants:
     - **Verified-fact grounding**: State only the concrete mismatch between the blocked action/component and verified task scope $Q_t$ or publicly observable schema facts (e.g., *"Recipient X was not requested in the verified user prompt; proceed only with the requested recipient Y"*).
     - **Zero confidential-set or detector leakage (`Confidential-set negatives`)**: Never name private allowlists/blocklists, thresholds, internal rule IDs, or the members/count of confidential entity sets that triggered the block.
     - **Zero caller-assertable unlock recipes**: Never tell the caller or untrusted content what phrase, confirmation, or status flag would flip `reject` to `approve` (banning hints such as *"ask the user/sender to confirm or authorize"* when untrusted channels can spoof confirmation text).

### Step 3: Build Compact Authorization-Matched Twin Pairs for Offline Distillation

To evolve or refresh $S_{\mathrm{dec}}$ and $S_{\mathrm{dis}}$ offline without leaking production evaluation suites:
1. Construct **`50–70` authorization-matched verified-user twin pairs** across `3–4` representative multi-tool sandbox worlds (`65` pairs across `4` `SHADE-Arena` worlds sufficed in `FORK`): each pair shares the same tools and sensitive resources, pairing a **contaminated episode** (where untrusted data attempts an unauthorized side effect alongside a legitimate user goal) with an **authorization-matched benign twin** (where the verified user legitimately authorizes a structurally similar sensitive action).
2. Grade safety outcomes via **deterministic environment-state snapshot diffs** (database records, sent messages, file/permission mutations) rather than transcript-only LLM judges, while keeping all target evaluation benchmarks completely unseen.

### Step 4: Co-Evolve `Decision` and `Disclosure` Skills Under Asymmetric Views

Run a bounded alternating co-evolution loop (`4` attacker rounds $A_1, A_3, A_5, A_7$ interleaved with `4` guardrail rounds $D_2, D_4, D_6, D_8$; `k = 5` sequential refusal-informed attempts per episode):
1. **Maintain strict information asymmetry**: During rollouts and reflection, any simulated stress-tester sees **only** observable trajectory turns and public `e_usr` rejections—never `e_op`, guardrail prompts, $S_{\mathrm{guard}}$, or verifier code (`"DON'T: Expose benchmark verifier code or unstated rubric predicates to the skill-library learner"` in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md)). Conversely, the **Defensive Reflector** inspects full guardrail traces `(d, e_op, e_usr)`, false-positive benign blocks, and multi-attempt compromises where `e_usr` leaked an adaptation cue.
2. **Enforce typed skill schemas (`diagnose -> apply -> reconcile`)**:
   - **Decision skills ($S_{\mathrm{dec}}$)** must specify `Applies when`, `Does not apply when` (explicit benign carve-out preventing over-refusal), and `Action`—targeting recurring structural patterns such as **equivalent side-effect channels** (`Equivalent effects`), **benign-vs-injected component splitting** (`Component isolation`, blocking only the unauthorized slice or guiding isolated re-invocation of the authorized slice), and **broad-read vs. targeted-exfiltration disambiguation** (`Scoped lookup`).
   - **Disclosure skills ($S_{\mathrm{dis}}$)** must specify `Applies when`, `Say`, and `Avoid`—rewriting leak-prone rejection templates into non-oracle boundary statements (`Confidential-set negatives`).
   - Run a **reconcile/merge pass** after each round so the combined skill bank stays compact (`3–6` non-overlapping skills) rather than accumulating contradictory per-task patches.
3. **Sample opponent mixtures across all retained rounds (`PSRO` / maximin)**: In each defender round, evaluate against a mixture of up to `3` opponents drawn from the game-theoretic equilibrium over **all** prior stress-test checkpoints (plus uniform exploration) alongside the clean benign twin stream so skills do not cycle or forget earlier bypasses.

### Step 5: Select by Worst-Case Maximin `ASR` and Gate Promotion

1. Score every defender checkpoint $D_{2n}$ across the **entire retained opponent archive** plus the benign twin split, and select the frozen checkpoint minimizing **worst-case `ASR`** subject to your benign-utility (`BU`) and recovery-rate (`RR`) floor (in `FORK`, $D_4$ lowered worst-case training `ASR` from `51.0%` at $D_0$ and `96.9%` unguarded to **`35.9%`** [`32.7%` mean `ASR`, `85.6%` `BU`], whereas dropping maximin selection raised held-out `FORK-World` `ASR` from `31.1%` to `36.2%`).
2. Pass the frozen skill bundle $S_{\mathrm{guard}} = (S_{\mathrm{dec}}, S_{\mathrm{dis}})$ through `"DO: Pass every self-modification through one acceptance gate"` in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) (verifying zero regression beyond baseline noise margin $\delta$ on protected benign tasks and strict zero tolerance on your immutable negative security testbed) and score end-to-end benign cost per `"DO: Measure each defense's benign cost on a matched benign arm, on the assembled stack"` in [`../../rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) before deployment. Never mutate $S_{\mathrm{guard}}$ online from live untrusted traffic (see [`../../research-briefs/poisoning-self-evolving-security-policies-defensive-lessons.md`](../../research-briefs/poisoning-self-evolving-security-policies-defensive-lessons.md)).

## Environment Caveats

- **Guardrail backbone floor**: While the frozen `4`-skill bundle improved all three tested guardrail models (`Claude Sonnet 4.5`, `GLM-5`, `Qwen3-32B`) without retraining, absolute residual `ASR` scales with guardrail reasoning strength (`14.1%` `3`-agent mean `ASR` with `Sonnet 4.5` vs. `20.4%` with `GLM-5` and `25.5%` with `Qwen3-32B` on verified-user `FORK-World`). Pair mid-size open-weight guardrails with deterministic sink capability monitors for irreversible side effects.
- **Rogue-user vs. verified-user operating mode**: When the caller itself is unauthenticated (`Q_t = \emptyset`, `203` rogue-user `FORK-World` scenarios), there is no legitimate root task to recover (`FORK` still cuts rogue-user `ASR` to `14.7%–34.6%` vs. `40.6%–73.1%` baselines, but public explanations provide zero benign recovery benefit). Switch `e_usr` to minimal static refusal codes and enforce strict retry caps when `Q_t = \emptyset`.
- **Call-efficiency accounting**: Because `FORK` prevents wasted blind retries after a compound tool block, total guardrail and tool invocations **per successful task** fall (`26.4` guardrail / `19.0` tool calls vs. `34.5 / 24.7` `Silent` and `36.0 / 25.8` `+Decision`), even though every proposed action undergoes `1` synchronous structured guardrail call.

## Failure Modes

- **Prompt-only "helpful refusal" instructions (`Explanatory seed` trap)**: Asking a guardrail to explain blocks helpfully without co-evolved `Say`/`Avoid` disclosure skills leaks rule boundaries and raises adaptive `ASR` by **`+9.0` pp (`30.3% -> 39.3%`)** for negligible utility gain (`+1.5` pp `UA`).
- **Joint verdict-and-explanation reasoning**: Allowing the guardrail to draft the user-facing refusal *before* locking `decision` induces sycophantic softening on borderline compound actions; always bind `decision` first.
- **Echoing caller-assertable preconditions**: Phrases like *"I cannot share this file unless an administrator confirms in the thread"* tell an indirect prompt injector inside a Slack/email thread the exact social-engineering wrapper to inject on attempt `2`.
- **Online runtime policy self-writing from live judge flags**: Updating guardrail policies live in production from `is_harmful=True` flags exposes the guardrail to single-episode availability/over-refusal poisoning (`100% -> 36%–52%` benign completion drop in `arXiv:2611.33385`); keep co-evolution strictly offline behind the frozen acceptance gate.

## Cross-References

- **Rules**:
  - [`../../rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DO: Give blocking action monitors recent call history, and make denials terminal"`, `"DO: Partition recurrent guardrail context into authorized scope versus untrusted screen evidence and decouple commit-point risk from intervention-window blocking"`, `"DON'T: Allow self-initiated CUA risk checks to widen read scope, fetch untrusted URLs, or leave flagged secrets in context"`, and `"DO: Measure each defense's benign cost on a matched benign arm, on the assembled stack"`
  - [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"` and `"DON'T: Expose benchmark verifier code or unstated rubric predicates to the skill-library learner"`
  - [`../../rules/agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — `"DO: Benchmark instruction-hierarchy adherence with benign orthogonal tool targets, and hide defender CoT from untrusted callers"`
- **Spec Templates**:
  - [`../../specs/agent-sandbox.spec.md`](../../specs/agent-sandbox.spec.md) — Pre-execution denial handling and audit-log separation
  - [`../../specs/self-improving-agent.spec.md`](../../specs/self-improving-agent.spec.md) — Offline skill promotion behind the frozen acceptance gate
- **Related Skills**:
  - [`bounded-context-intervention-window-guardrail`](../bounded-context-intervention-window-guardrail/SKILL.md) — Compact `1.6B–2B` on-device GUI guardrail training over `k = 3` screenshot windows (`MobileGrail`, `arXiv:2611.29847`)
  - [`strategy-diverse-ipi-purple-teaming`](../strategy-diverse-ipi-purple-teaming/SKILL.md) — Offline weight-level purple-teaming with `BPDN` strategy coverage (`PIPETTE`, `arXiv:2611.24362`)
  - [`audited-guardrail-tool-evolution`](../audited-guardrail-tool-evolution/SKILL.md) — Offline 10-CWE `AuditorAgent` verification for synthesized Python guardrail tools (`EVOLVE`, `arXiv:2611.02516`)
  - [`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md) — Zero-LLM schema-derived write commitment and request n-gram binding (`CapLite`, `arXiv:2611.17115`)
- **Research Briefs**:
  - [`../../research-briefs/conartist-cua-consistency-and-risk-auditing-defensive-lessons.md`](../../research-briefs/conartist-cua-consistency-and-risk-auditing-defensive-lessons.md) — Why in-agent risk auditing (`P1–P7`) and exposed `L3` refusal rationales drive adaptive bypasses (`arXiv:2611.29977`)
  - [`../../research-briefs/bypassgym-edr-evasion-defensive-lessons.md`](../../research-briefs/bypassgym-edr-evasion-defensive-lessons.md) — Why stage-level failure reasons act as localization oracles for rogue callers (`arXiv:2611.13684`)
  - [`../../research-briefs/poisoning-self-evolving-security-policies-defensive-lessons.md`](../../research-briefs/poisoning-self-evolving-security-policies-defensive-lessons.md) — Why online judge-gated policy writing suffers single-episode over-refusal poisoning (`arXiv:2611.33385`)

## Sources

- Man, H., Shang, C., Dong, R., Kulshreshtha, D., Qi, Y., & Swamy, S. (2026). *FORK: Co-Evolving Safe Disclosure and Decision Skills Against Attackers Who Read Every Refusal*. `arXiv:2611.33879` (`src:2611-33879v1`).
