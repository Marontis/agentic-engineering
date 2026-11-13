---
name: schema-derived-write-integrity-gate
description: >
  Enforce prompt-injection write integrity for small language model (SLM)
  and local tool-using agents without model-written security artifacts.
  Derives tool and argument roles deterministically from tool schemas,
  commits write calls before reading untrusted tool outputs, binds
  placeholders only from exact request-grounded candidates, and mediates
  all read destinations and writes in deterministic code. Derived from
  CapLite (arXiv:2611.17115).
source: https://arxiv.org/abs/2611.17115
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Schema-Derived Write Integrity Gate

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when hardening a **small language model (SLM)** or **open-weight local tool-calling agent** (`1.7B–35B` parameters) that reads untrusted data (emails, web pages, shared documents, reviews, transaction memos) while holding side-effecting write tools (`send_email`, `transfer_money`, `create_event`, `delete_file`, `post_message`).

## When to Use

- Your agent runs on a small or mid-sized open-weight model (`1.7B–35B`) where asking the model to author its own **security artifact** fails open (admitting prompt injections via permissive `Progent` policies, `IPIGuard` dependency graphs, or `DRIFT` checklists) or fails closed (producing unrunnable `CaMeL` Python programs and burning repair tokens).
- You need a **constructive write-integrity guarantee** (`0` unauthorized writes added after reading untrusted data, and `0` authority arguments routed to unstated recipients, amounts, accounts, object IDs, or URLs) enforced entirely by deterministic code from standard tool registries.
- Token budget and edge latency matter: you cannot afford `60k–94k` tokens per episode for multi-round policy updates or code-interpreter repair loops.

**When to prefer an alternative:**
- When running **frontier coder backbones** (`Claude Sonnet-4.6`, `GPT-5.6-Luna`) on tasks that must **loop over retrieved records or branch control flow on observed values**, prefer [`compile-then-execute-web-agent-gateway`](../compile-then-execute-web-agent-gateway/SKILL.md) (`Baya`, `arXiv:2611.06039`).
- When running frontier models (`GPT-4o`, `Qwen3-max`) where legitimate authority targets routinely originate from trusted upstream read tools rather than the user's literal prompt, see [`provenance-capability-grants`](../provenance-capability-grants/SKILL.md) (`ToolFence`, `arXiv:2609.37196`)—noting that `ToolFence` relies on a model-compiled capability blueprint and runtime LLM judge that SLMs cannot author reliably.
- When you have human security engineers to write and SMT-verify domain policies offline, see [`verified-policy-action-governance`](../verified-policy-action-governance/SKILL.md) (`ActGov`, `arXiv:2609.24446`).

**Deference to the repository acceptance gate:** If an automated harness or self-improvement loop proposes expanding the lexical verb/token classification tables in Step 1, that change **must** pass `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md) (no regression beyond baseline noise margin $\delta$ and strict zero tolerance on the prompt-injection security testbed).

---

## Core Insight: Why SLMs Must Never Write Their Own Security Artifacts

Enforcement defenses (`CaMeL`, `Progent`, `IPIGuard`, `DRIFT`) are only as sound as the security artifact the model writes:
1. **Artifacts that decide what is allowed fail open**: Across `15` open-weight models (`13` SLMs from `1.7B–12B` plus `Qwen3-32B` and `Qwen3.6-35B-A3B`) on `AgentDojo v1.2.2` (`97` benign tasks, `949` attacked pairs, `929` tool-goal pairs = `13,935` pooled episodes), model-authored `Progent` policies admit attacks on **`14/15` models** (`676` attacks, `4.85%` ASR, up to `132/929` on `Qwen3-32B`, while blocking `25–77%` of attempted writes under attack), `IPIGuard` graphs fail on **`13/15` models** (`435` attacks, `3.12%` ASR), and `DRIFT` checklists fail on **`11/15` models** (`214` attacks, `1.54%` ASR; its `4` zero-ASR models complete only `4.7%–9.5%` of tasks due to inaction). Scaling up within `Qwen3` (`1.7B -> 32B`) and `Gemma-4` (`E2B -> 12B`) **increases** `Progent` ASR monotonically (`3.0% -> 14.2%` and `0% -> 12.7%`; capability correlation $|\rho| \le 0.33, p > 0.2$).
2. **Artifacts that decide what runs fail closed**: `CaMeL` admits only `20/13,935` attacks (`0.14%` ASR, `17` on `LFM2.5-2.6B`), **but fails to produce a runnable program in `>15%` of episodes on `8/15` models and `68%` on `Granite-4.2-8B`**, spending **`93.7k` tokens/episode** across up to `10` syntax/interpreter repair rounds for `24.9%` benign utility.

**CapLite** eliminates model-written security artifacts: the SLM only **proposes** plans, candidate indices, and free-text payloads, while **deterministic code** derives the policy from tool schemas, extracts the exact grounding set $\mathcal{G}(q)$ from the user request $q$, and mediates every read destination and write call.

| Defense (`15`-model mean on `AgentDojo v1.2.2`) | Benign Utility (`BU` ↑) | Utility Under Attack (`UA` ↑) | Pooled `ASR` (↓) | Breached Episodes (`k / 13,935` ↓) | Zero-ASR Models (↑) | Tokens / Episode (↓) | `UA / kTok` (↑) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| *Undefended reference* | `59.4%` | `50.2%` | `16.66%` | `2,322` | `0 / 15` | `28.0k` | `1.79` |
| `Progent` | `43.8%` | `40.6%` | `4.85%` | `676` | `1 / 15` | `63.4k` | `0.64` |
| `IPIGuard` | `40.1%` | `35.7%` | `3.12%` | `435` | `2 / 15` | `60.5k` | `0.59` |
| `DRIFT` | `35.7%` | `34.9%` | `1.54%` | `214` | `4 / 15`‡ | `28.1k` | `1.24` |
| `CaMeL` | `24.9%` | `27.2%` | `0.14%` | `20` | `12 / 15`‡ | `93.7k` | `0.29` |
| **`CapLite`** | **`28.1%`** | **`29.0%`** | **`0.00%`** | **`0`** | **`15 / 15`** | **`17.1k`** | **`1.69`** |

*(‡ Includes models whose zero ASR comes from `<10%` benign and attacked task completion due to inaction.)*

---

## Step-by-Step Procedure

### Step 1: Derive Tool & Argument Roles Deterministically from Tool Schemas

Inspect only the trusted tool registry ($\Sigma$: tool name, docstring, and JSON parameter schema) using fixed lexical rules—never an LLM classifier:

1. **Classify Each Tool (`read-only` / `write` / `unclassified`)**:
   - Extract the leading verb of the tool's name and the leading verb of its docstring.
   - Mark the tool **`read-only`** only when **both** leading verbs belong to the fixed read-verb set: `get`, `read`, `search`, `find`, `list`, `check`, `view`, `lookup`, `fetch`, `retrieve`, `return`, `show`, `query`, `count` (plus third-person singular forms).
   - Mark the tool **`write`** when **either** leading verb belongs to the effect-verb set: `send`, `delete`, `create`, `cancel`, `reschedule`, `add`, `append`, `share`, `update`, `book`, `reserve`, `make`, `pay`, `transfer`, `schedule`, `invite`, `remove`, `post`, `set`, `write`, `move`, `upload`, `edit`, `modify`, `rename`, `publish`, `submit`, `purchase`, `order`, `grant`, `revoke` (plus third-person forms).
   - Otherwise mark the tool **`unclassified`** and **deny it by default** in the Mediator (unfamiliar verbs fail closed, trading utility rather than safety).
2. **Classify Each Write-Tool Parameter (Default = `authority`)**:
   - Treat **every** parameter of a `write` tool as **`authority`** (deciding whom or what the effect reaches: recipients, accounts, amounts, channels, object IDs, file names, destinations) *unless* the schema matches one of three narrower roles:
     - **`payload`** (free text): parameter name matches payload tokens (`body`, `content`, `subject`, `title`, `description`, `message`, `text`, `note`, `notes`, `comment`, `comments`) and is string-typed without destination markers.
     - **`temporal`**: parameter name contains `date`, `time`, or `day`, or its schema description specifies `YYYY-MM-DD` or ISO date/time formatting.
     - **`control`**: JSON schema declares an `enum` or `boolean` type.
3. **Promote Read Destinations to `authority`**:
   - Even on a `read-only` tool, classify any parameter whose name contains `url`, `uri`, `link`, `webpage`, or `website` as **`authority`**. Fetching an attacker-chosen URL exfiltrates context via query strings (`0/168` read-exfiltration ASR with destination gating vs. `85/168` undefended, `69/168` `IPIGuard`, and `21/168` `Progent`).

*(Audit validation: across all `74` `AgentDojo` tools and `79` write arguments, deterministic derivation matched blind labels on `74/74` tools and misclassified **`0` authority arguments as `payload`**.)*

---

### Step 2: Pre-Compute the Request Grounding Set $\mathcal{G}(q)$

Before invoking any model or tool, deterministically parse the authenticated user request $q$ into a canonical grounding set $\mathcal{G}(q)$:

1. Extract all structured literals stated in $q$: email addresses, IBANs/account identifiers, URLs, dates, quoted strings, and numeric literals.
2. Extract every contiguous token $n$-gram of $q$ up to length $n \le 8$.
3. Canonicalize all strings uniformly (lowercase, collapse internal whitespace, strip URL scheme prefixes `http://` / `https://`).
4. Enforce **exact member equality** rather than substring containment: a request stating `100` grounds `100`, **never** `1` or `10`.

> **Critical Pitfall — Never Use "Record Grounding" (Descriptor Matching)**: Do **not** admit an unstated record ID merely because a retrieved record's title, filename, or subject matches a phrase in $q$. In `CapLite`'s ablation (`Appendix F`), record grounding shifted benign utility by only `-2.1` to `+3.1` points while allowing **descriptor-collision attacks** (planting a fake invitation, shared file, email, or transaction bearing the user's own descriptor) to succeed in **`23/103` episodes** (`0/104` against exact-grounding `CapLite`). A descriptor proves what a record *contains*, not *who created it*.

---

### Step 3: Commit Write Calls on the Trusted Path (`Planner`)

Run a single schema-constrained `Planner` call that receives **only** the user request $q$ and the tool documentation $\Sigma$ (zero untrusted observations):

- Output a bounded plan of at most `10` tool calls (`temperature = 0`).
- Populate each write argument either directly from $q$ or with a typed placeholder token (e.g., `$event_id`, `$recipient_iban`).
- **Freeze the write sequence immediately**: no downstream component may append a new write call, swap a write tool, or reorder committed writes. *(Allowing the Planner to append writes after reading tool results breaks write integrity, admitting `53/7,432` [`0.7%` ASR] attacks whenever the attacker's goal reuses values already present in $q$.)*

---

### Step 4: Execute Adaptive Reads & Candidate-Only Placeholder Binding

Run the untrusted observation path under strict structural confinement:

1. **Adaptive `Reader` Loop ($\le 10$ read-only steps)**:
   - Give the `Reader` the user request $q$, the committed write plan, and prior read results (truncated to `6,000` chars per observation).
   - Route every proposed `Reader` call through the deterministic `Mediator` first: reject any non-`read-only` tool and reject any read call whose `authority` destination (e.g., URL) is not in $\mathcal{G}(q)$.
2. **Candidate-Only `Binder` (Constrained Enum Decoding)**:
   - For each open `$placeholder` in a committed write call, deterministically extract scalar leaf values of matching JSON type from the `Reader` observations (retaining key path and tool source, capped at `32` candidates).
   - **Pre-filter `authority` and `control` candidates against $\mathcal{G}(q)$**: discard any candidate value not equal to an element of $\mathcal{G}(q)$.
   - Have the `Binder` decode **only an enum choice** over the surviving candidate indices plus `none` and `ask`—the `Binder` never emits raw string/number values (`+2.0` points benign utility over free-text binding while keeping `0.0%` ASR).
3. **`Composer` for Free-Text Payloads**:
   - Have the `Composer` draft `payload` fields (e.g., email/message bodies) from $q$ and the observations under structured output decoding.

---

### Step 5: Mediate Writes Deterministically & Halt on First Violation

Before dispatching each committed write call, execute the deterministic **`Mediator`** in code:

1. Verify the tool is classified as `write` (never `unclassified`), matches the next uncommitted entry in the frozen `Planner` prefix, has zero unresolved `$placeholders`, and validates against the tool's JSON schema.
2. Verify **every `authority` argument** equals an element of $\mathcal{G}(q)$ (canonicalized exact match) or an out-of-band user-confirmed value. *(Removing the `Mediator` admits `106/7,432` [`1.4%` ASR] attacks across every tested model.)*
3. **Make denials and missing-grounding stops terminal for the remaining write queue**:
   - If an authority value exists only inside untrusted tool results (e.g., *"message the channel mentioned in the onboarding doc"* where the channel name was not in $q$), no candidate survives $\mathcal{G}(q)$ filtering; halt remaining writes and emit an explicit user confirmation request naming that exact target (`8.0%–11.8%` of benign episodes; route confirmation out-of-band per [`out-of-band-hitl-verification`](../out-of-band-hitl-verification/SKILL.md)).
   - Stop remaining writes on the first denial, confirmation interrupt, or tool execution error.
4. Invoke a final **`Reporter`** call (`+13.1` to `+15.1` pts utility over omitting `Reporter`) to synthesize the user-facing response from the observations, and optionally run an out-of-process **trace audit** re-deriving $\Sigma$ roles and $\mathcal{G}(q)$ from raw logs (`0` violations across `25,452` `CapLite` episodes).

---

## Environment Caveats & Known Boundaries

- **Planning Ceiling on Small Models (`-21` pp UA vs. Undefended)**: `CapLite` averages `29.0%` utility under attack (`28.1%` benign) vs. `50.2%` undefended (`59.4%` benign). Across `1,046` failed benign episodes, `42.8%` (`448`) stem from the small model failing to commit the needed write upfront (`354` committing zero writes) and `38.4%` (`402`) from reasoning/read answers rather than `Mediator` over-blocking (`8.0%` confirmation requests). Furthermore, static placeholder plans cannot loop over dynamic list lengths; on models that reliably synthesize `CaMeL` Python (`Gemma-4-E4B` and `Gemma-4-12B`, `3–14%` program failure), `CaMeL` beats `CapLite` by `+12.2` and `+13.5` points (`CapLite` beats `CaMeL` by `+21.3` pts on `Granite-4.2-8B` and `+6.8` pts on `LFM2.5-2.6B` at `5.5x` lower token cost).
- **Free-Text `payload` Fields & Final Prose Answers Are Outside Write Integrity**: Because `Composer` and `Reporter` read untrusted observations, injected text can influence the *prose body* of an authorized message (sent only to a user-stated recipient) or inject a sentence into a pure read-only text answer (`20` `AgentDojo` Travel answer-only episodes; `Appendix H, Case 5`), and `temporal` fields are not request-grounded. Pair `CapLite` with outbound DLP / secret redaction (`CredentialGuard` in [`compositional-coding-harness-reference-monitor`](../compositional-coding-harness-reference-monitor/SKILL.md) or SDP in [`adk-security-and-evaluation.md`](../../rules/adk-security-and-evaluation.md)) when confidential records coexist in context with external messaging tools.
- **Trusted Tool Registry Requirement**: `CapLite` assumes tool names, docstrings, and parameter schemas are trusted. Pin third-party MCP descriptors and container digests before deriving schema policies (see [`mcp-zero-trust-tool-authorization`](../mcp-zero-trust-tool-authorization/SKILL.md)).

---

## Cross-References

- **Related Rules**:
  - [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — Action-boundary authorization, open-privilege measurement, compile-then-execute tradeoffs, and out-of-band HITL confirmation
  - [`adk-workflow-architecture.md`](../../rules/adk-workflow-architecture.md) — Runtime `RequestInput` interrupts and pre-LLM deterministic policy checks
  - [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Related Skills**:
  - [`provenance-capability-grants`](../provenance-capability-grants/SKILL.md) — Frontier-LLM provenance blueprint compilation and shape caching (`ToolFence`, `arXiv:2609.37196`)
  - [`compile-then-execute-web-agent-gateway`](../compile-then-execute-web-agent-gateway/SKILL.md) — Offline Python compilation for frontier web agents (`Baya`, `arXiv:2611.06039`)
  - [`germline-isolated-tool-execution`](../germline-isolated-tool-execution/SKILL.md) — Destination/content view splitting and data-free germline forks (`arXiv:2611.06585`)
  - [`out-of-band-hitl-verification`](../out-of-band-hitl-verification/SKILL.md) — Hardware-attested confirmation channel when authority targets appear only in tool outputs (`arXiv:2610.35835`)
- **Related Research Briefs**:
  - [`untrusted-model-deterministic-policy-taint-hitl.md`](../../research-briefs/untrusted-model-deterministic-policy-taint-hitl.md) — Deterministic capability monitors + taint-triggered HITL on `Qwen2.5-1.5B/7B` (`arXiv:2611.11571`)
  - [`task-tampering-indirect-prompt-injection.md`](../../research-briefs/task-tampering-indirect-prompt-injection.md) — Why `Progent` and `DRIFT` miss within-tool argument tampering (`arXiv:2611.07640`)

## Sources

- Xu, Z., Liu, W., & Nakayama, H. (2026). *CapLite: Prompt-Injection Defense for Small Language Model Agents without Model-Written Security Artifacts*. [arXiv:2611.17115](https://arxiv.org/abs/2611.17115) (`src:2611-17115v1`).
