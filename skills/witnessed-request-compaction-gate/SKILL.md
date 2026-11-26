---
name: witnessed-request-compaction-gate
description: >
  Prevent context-compaction privilege escalation by separating the agent's
  low-authority compacted summary view from the authorizer's cryptographically
  witnessed user-request channel using ingress occurrence MACs, monotonic
  boundary sequence commitments, and fail-closed count verification. Derived
  from LLM Agent Authorization Across Context Compaction (arXiv:2611.32194).
source: https://arxiv.org/abs/2611.32194
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Witnessed-Request Compaction Gate

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when building or securing **long-horizon multi-turn agent harnesses** (CLI coding assistants, enterprise workflow agents, banking/operations copilots, or orchestrator-to-subagent runtimes) that compact conversation history **and** derive tool-call permissions, alignment checks, `PreToolUse` hook decisions, or sub-agent task scopes from user requests.

## When to Use

- Your harness runs automatic or manual context compaction (`Claude Code`, `Codex`, `Gemini CLI`, `OpenHands`, `Cline`, `Goose`, `Aider`, `LangChain`, or custom loops) and feeds post-compaction messages to a request-derived authorizer (`Progent`, `LlamaFirewall AlignmentCheck`, auto-mode classifiers, or `PreToolUse` hooks).
- Freezing tool policy at turn `1` breaks multi-turn usability (`7/60` [`12%`] second-turn task completion vs. `41/60` [`68%`] when updating policy per user request), so authorization must evolve across turns that span compaction boundaries.
- Session transcripts, compacted summaries, or persistent instruction files (`CLAUDE.md`, `.jsonl` rollout logs, checkpoint stores) reside on disk or in mutable state where stale prefixes, omitted user revocations, or spliced `role: "user"` entries could be replayed.

Pair with [`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md) (`CapLite`) or [`principal-context-permission-intersection`](../principal-context-permission-intersection/SKILL.md) (`Conflux`) for single-turn parameter and principal enforcement, and [`historical-constraint-restoration`](../historical-constraint-restoration/SKILL.md) (`STAR-Guard`) so the *model itself* remembers benign user prohibitions across long sessions.

**Deference to the repository acceptance gate:** If you register or evolve any deterministic trusted extractor (`tool_top`) whose output is eligible for an ingress witness, pass that extractor specification through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md) with zero-tolerance negative security testing before deployment.

---

## Core Insight

Across **`1,108/1,108` live automatic compactions** (`100` in `Claude Code 2.1.312`/`2.1.319` and `1,008` across `51` live `Codex 0.163.0`/`0.164.0` sessions) and **`8` more open-source harnesses** (`11` harnesses / `18` shipped compaction prompts total), the harness replaces prior turns with a model-written summary placed in a **`role: "user"` message**. Because request-derived authorizers treat `user` messages as the authority root, compaction silently promotes untrusted tool outputs summarized by the model into **user authority** (`31/100` post-compaction `Progent` attack successes vs. `33/100` undefended).

Crucially, **prompting the compactor to drop identifiers or mark untrusted provenance cannot fix this**:

1. **Tight Text-Only Impossibility (`Theorem 1`)**: For any text-only compactor and authorizer, differentiating legitimate state from injected state is bounded by total variation distance $p_L(\pi) - p_A(\pi) \le \mathrm{TV}(P_L, P_A)$. While frontier compactors (`gpt-5.4-mini`, `gpt-5.5`) mark **injected instructions** in `219/220` kept summaries, they mark **plain-data payloads** (e.g., an updated IBAN in a routine rent notice where $P_A = P_L$) **`0/40` times** in two-request sessions. Even when the user **explicitly named the payee**, summarizing alongside a plain-data rent notice caused policies to admit the attacker's account in **`290/320` (`90.6%`; `91%` in abstract) trials** under `gpt-4o` policy generation (`189/320` [`59%`] under `gpt-5.5`) vs. **`0/80` (`0%`)** from the user's own words.
2. **Dropping Identifiers Fails Open**: Suppressing all identifiers in summaries (`0/918` dropped high-entropy IDs guessed, Lemma 1 $\le \ell^2 2^{-h}$) leaves the recipient unconstrained in generated schemas, still admitting **`41%` (`78/410`)** of banking transfers.
3. **Metadata Labels Alone Fail on Writable Carriers**: Relabeling summaries in-memory (`Codex Guardian` post-Oct 2026) blocks in-process escalation (`0/33`), **but fails `76/76` `Replay` and `76/76` `Splice` attacks** once session `.jsonl` or `CLAUDE.md` carriers are writable.

**Verified Empirical Evidence** (`arXiv:2611.32194`, `40` attacked multi-turn episodes in `Table VII` + `608` adaptive carrier-tampering trials [`8` attacks $\times 76$ transcripts] in `Table VIII`):

| Compaction & Authorization Design | Tasks Completed (`Table VII`, `/40`) | Policies Naming Attacker (`/40`) | Attacker Actions Completed (`/40`) | Adaptive Tampering Admitted (`Table VIII`, `608` trials) |
|:----------------------------------|:-------------------------------------|:---------------------------------|:-----------------------------------|:---------------------------------------------------------|
| **Uncompacted Baseline** | `27` | `0` | `0` | — |
| **Summary in `user` Request Slot (Standard Harness)** | `15` | **`18`** | **`7`** | Fails slot authority (`57%` in `Table II`) |
| **Metadata-Only Role Filter (`Codex Guardian`-style)** | — | — | — | Fails **`Replay` (`76/76`), `Splice` (`76/76`), `Omission`, `Stale prefix`** |
| **Ingress Witnesses Only (No Sequence/Count Binding)** | — | — | — | Fails **`Replay` (`76/76`), `Omission` (`76/76`), `Stale prefix` (`76/76`)** |
| **`Witnessed-Request Gate` + Summary as `tool` Result** | **`19`** *(matches ungated tool summary `18`)* | **`0`** | **`0`** | **`0 / 608`** across all `8` adaptive attacks (`0.25–0.40 ms`/req) |
| **`Witnessed-Request Gate` + Verbatim User Text** | **`26`** (`22` after 2nd boundary) | **`0`** | **`0`** | **`0 / 608`** across all `8` adaptive attacks |

---

## Step-by-Step Procedure

### Step 1: Split the Agent's Execution Context from the Authorizer's Request View

Never pass the same post-compaction message array to both the LLM agent and the policy/hook authorizer when summaries are represented as `user` turns:

1. **Demote Compacted Summaries in the Agent View**: Deliver the compacted history summary $s$ to the executing agent strictly inside a non-authoritative **`tool` result** (with an explicit synthetic precursor tool call so strict alternating chat APIs accept the transcript) or a dedicated untrusted-context block—**never** as `role: "user"` (and in frameworks like `smolagents`, disable mapping `ToolOutput` to `Role.USER`, which caused `16/16` attacker target naming and `11/16` completed attacks). Holding summary bytes identical (`Table II`), moving the summary from the `user` request slot to a `tool` result drops policy admission of attacker targets from **`17/30` (`57%`) to `0/28` (`0%`)**.
2. **Route Only Verbatim User Requests to the Authorizer**: Feed request-derived policy generators (`Progent`), alignment checkers (`AlignmentCheck`), `PreToolUse` hooks, and sub-agent permission binders **only** the ordered sequence of authenticated user requests $(u_1, \dots, u_m)$—never model-generated summaries, assistant turns, or untrusted tool outputs. User turns are typically compact (`~20–150` tokens each), so retaining verbatim user turns across `2+` compactions preserves `26/40` (`1` boundary) and `22/40` (`2` boundaries) task completion at negligible token cost.

---

### Step 2: Mint Domain-Separated Occurrence Witnesses ($w_i$) at Ingress

Provision two independent `32`-byte secret keys (`K_occ` and `K_seq`, HMAC-SHA256) inside the trusted host runtime—outside the LLM context, workspace filesystem, and child tool environments:

1. **Canonicalize & Tag Trusted Ingress Only**: When and only when a message enters the harness directly from the authenticated human user interface ($o = \textsc{user}$) or from a pre-audited deterministic host extractor ($o = \textsc{tool}_\top$, never an LLM summarizer or external API/web/email/file read $o = \textsc{tool}_\bot$), canonicalize its UTF-8 text $\operatorname{can}(x_i)$ (NFC normalization, line-ending normalization) and assign its monotonic session occurrence index $i$.
2. **Compute the Occurrence MAC**:
   $$w_i = \mathsf{MAC}_{K_{\text{occ}}}\!\left(\texttt{"occ"} \parallel \mathsf{frame}(sid, i, o, \operatorname{can}(x_i))\right)$$
   where $\mathsf{frame}(\cdot)$ applies unambiguous length-prefixed encoding over session ID $sid$, turn index $i$, origin tag $o \in \{\textsc{user}, \textsc{tool}_\top\}$, and canonical text $\operatorname{can}(x_i)$.
3. **Never Mint Witnesses During Compaction or Session Reload**: Model summaries, `CLAUDE.md` memory files, sub-agent return payloads, and deserialized `.jsonl` transcript lines must **never** call the ingress witness constructor.

---

### Step 3: Commit Boundary Order & Count ($\sigma, b, m$) in the Trusted Packager

Occurrence witnesses $w_i$ alone prevent forged `user` text (`Splice` and `Summary` blocked), **but Proposition 1 proves they still fail against `Omission` (dropping a user turn that revoked or narrowed an earlier recipient), `Replay` (reordering turns), and `Stale prefix` (rolling back to an earlier compaction snapshot)**:

1. **Maintain a Monotonic Compaction Boundary Counter $b$**: Inside trusted host memory (or an anti-rollback monotonic counter), increment boundary epoch $b \leftarrow b + 1$ at every context compaction or session packaging step.
2. **Sign the Ordered Retained-Request Vector**: Let $R = (i_1, i_2, \dots, i_m)$ be the strictly increasing occurrence indices of all authoritative user requests up to boundary $b$, and let $m = |R|$. Have the trusted packager compute:
   $$\sigma = \mathsf{MAC}_{K_{\text{seq}}}\!\left(\texttt{"seq"} \parallel \mathsf{frame}(sid, b, m, R)\right)$$
3. **Attach the Witness Bundle Out-of-Band**: Store `(sid, b, m, R, [(i_k, o_k, x_{i_k}, w_{i_k})]_{k=1}^m, \sigma)` in the authorizer envelope alongside—not inside—the agent's compacted prompt view.

---

### Step 4: Verify All Three Invariants Fail-Closed at the Authorization Gate

Before generating or updating the active tool-call policy $\pi$ (adds **`0.25–0.40 ms` per request**):

1. **Fresh Boundary Commitment ($\sigma$)**: Verify $sid$ matches the active session, boundary index $b$ equals the current live boundary epoch (rejecting `Stale prefix` rollbacks), and $\mathsf{MAC}_{K_{\text{seq}}}$ over $(sid, b, m, R)$ matches $\sigma$ in constant time.
2. **Ingest Completeness Count ($m$)**: Confirm that the number of delivered request records equals $m$ and matches $|R|$ exactly (blocking `Omission` of later user overrides or constraints, such as *"actually, hold off on paying the landlord until Friday"*).
3. **Per-Item Occurrence Authenticity & Order ($w_{i_k}$)**: For every $k \in \{1, \dots, m\}$, verify $o_{i_k} \in \{\textsc{user}, \textsc{tool}_\top\}$, confirm index $i_k$ matches $R[k]$ in strictly increasing order (blocking `Replay` and permutation), and verify $\mathsf{MAC}_{K_{\text{occ}}}$ over $(sid, i_k, o_{i_k}, \operatorname{can}(x_{i_k}))$ matches $w_{i_k}$.
4. **Fail Closed to $\bot$**: If **any** check fails—missing witness, wrong key, count mismatch, reordered index, stale $b$, or spliced `user` message—set the active tool policy to the **empty policy $\bot$** (denying all side-effecting tool calls) and surface an integrity alert.

---

## Environment Caveats & Failure Modes

- **Every One of the Three Checks Is Necessary (`Table VIII`)**: Dropping occurrence MACs ($w_i$) lets writable session files splice arbitrary `user` turns (`76/76` `Splice`); dropping sequence MAC ($\sigma$) or monotonic $b$ admits `Replay` and `Stale prefix` (`76/76`); dropping count verification ($m$) lets an attacker strip a user's revocation turn (`76/76` `Omission`). Never deploy a partial subset.
- **Legitimate Runtime Identifier Discovery Requires Trusted Extractors or User Confirmation**: Because witnessed user turns contain only values the user stated (e.g., *"pay my landlord"*, without knowing the landlord's IBAN stored in an invoice), tasks that legitimately discover an authority-bearing identifier from a tool read will be blocked if the policy demands an explicit user-stated recipient (`19/40` vs. `27/40` uncompacted completion). Bridge legitimate dynamic discovery via out-of-band human confirmation ([`out-of-band-hitl-verification`](../out-of-band-hitl-verification/SKILL.md)) or candidate-only trusted lookup bindings ([`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md)), **never** by trusting LLM-summarized tool prose.
- **Agent Reasoning Still Reads the Untrusted Summary**: The `Witnessed-Request Gate` makes *authorization* immune to poisoned summaries (`0/40` attacker policies, `0/40` completed attacker transfers), but the agent's own reasoning context still consumes the `tool`-role summary for task continuity—so pair with [`historical-constraint-restoration`](../historical-constraint-restoration/SKILL.md) and structured epistemic tags (`CompAct-Bench`) to preserve benign task accuracy after compaction.

---

## Cross-References

- **Related Rules**:
  - [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DO: Restore earlier-turn safety constraints and enforce them at a deterministic action boundary"`, `"DON'T: Place SLM-generated security artifacts on the write-integrity path"`, and `"DO: Intersect permissions across all influencing principals in a no-laundering Principal Context outside model judgment"`
  - [`skill-system-design.md`](../../rules/skill-system-design.md) — `"DO: Enforce protocol-aware context trimming with adaptive budget guardrails"`
  - [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Related Skills**:
  - [`historical-constraint-restoration`](../historical-constraint-restoration/SKILL.md) — Preserving benign earlier-turn safety constraints across long sessions (`STAR-Guard`)
  - [`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md) — Zero-LLM schema role derivation and literal user-request n-gram grounding (`CapLite`)
  - [`principal-context-permission-intersection`](../principal-context-permission-intersection/SKILL.md) — Pointwise ACS permission intersection across influencing principals (`Conflux`)
  - [`protocol-preserving-context-trimming`](../protocol-preserving-context-trimming/SKILL.md) — Preserving tool-call protocol invariants during context reduction
- **Related Research Briefs**:
  - [`arcbench-rule-compliance-context-compaction.md`](../../research-briefs/arcbench-rule-compliance-context-compaction.md) — Benign and injected model rule-compliance drift across compaction (`ARC-Bench`, `arXiv:2611.03223`)
  - [`compact-bench-working-context-compaction.md`](../../research-briefs/compact-bench-working-context-compaction.md) — Environment-backed vs. context-resident compaction lossiness across `12` frontier models (`CompAct-Bench`, `arXiv:2611.25673`)

## Sources

- Fei, Z., Fei, H., Xu, Y., Wang, X., & Zhang, Y. (2026). *LLM Agent Authorization Across Context Compaction*. [arXiv:2611.32194](https://arxiv.org/abs/2611.32194) (`src:2611-32194v1`).
