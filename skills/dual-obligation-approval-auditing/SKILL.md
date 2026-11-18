---
name: dual-obligation-approval-auditing
description: >-
  Verify both Refusal Safety (denied effects never execute) and Bounded
  Authorization Completeness (eligible approved actions finish within horizon H)
  across model call selection, harness scheduling/resumption, and workflow
  branch routing using paired Approve/Reject replays and four native execution
  witnesses. Derived from Deng et al. (arXiv:2611.19237).
source: https://arxiv.org/abs/2611.19237
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Dual-Obligation Approval Auditing Across Model, Harness, and Workflow Layers

> **Source**: [Auditable Authorization for LLM Agents: Empirical Evidence Across Model, Harness, and Workflow Layers](https://arxiv.org/abs/2611.19237) (Deng et al., 2026) | Praxis: `src:2611-19237v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Building or auditing human-in-the-loop (`HITL`) confirmation gates in conversational tool agents, multi-agent orchestration frameworks (`Google ADK`, `CrewAI`, `LangGraph`, `OpenAI Agents SDK`, `Agno`, `Mastra`), or visual/low-code approval workflows (`n8n`).
- Debugging "silent approval loss"—where a human clicks **Approve** on a multi-item batch, parallel tool request, or paused workflow checkpoint, the runtime records the positive decision, yet one or more authorized actions never reach native business state.
- Verifying that conversational consent withdrawal, mid-pause environment state changes (such as balance or reserve settlements), and workflow **Reject** edges actually govern downstream side effects rather than merely displaying a confirmation UI.

Pair with [`out-of-band-hitl-verification`](../out-of-band-hitl-verification/SKILL.md) (`I-HITL`, `arXiv:2610.35835`) to protect the human-to-service approval channel against agent forgery, and [`cross-interface-route-bound-authorization`](../cross-interface-route-bound-authorization/SKILL.md) (`arXiv:2610.41397`) when agents can switch between `GUI`, `CLI`, `API`, and `MCP` surfaces. Any automated repair promoted into persistent harness configuration or prompts must pass `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md).

---

## Core Insight: Approval Imposes Two Independent Obligations

Recording a human's **Approve** or **Reject** click does not guarantee that the decision controls real-world state. Every scoped decision $d_v = (v, A_v, D_v, C_v)$—comprising decision version $v$, authorized action-argument tuples $A_v$, denied effects $D_v$, and live execution preconditions $C_v$—imposes **two orthogonal obligations** over execution horizon $H$:

1. **Refusal Safety**: Zero denied effects $d \in D_{\mathrm{latest}(\tau)}$ execute after the decision, including effects that are executed and later reverted.
2. **Bounded Authorization Completeness**: Every still-authorized, feasible action whose preconditions $C_v$ hold completes in native business state within $H$:
   $$F_H(\tau) = \bigwedge_{a \in A_H^{\mathrm{eligible}}} \mathbf{1}\{a \in \mathrm{done}(\tau_{0:H})\}, \qquad P(\tau) = A_{\mathrm{latest}(\tau)} \setminus \mathrm{done}(\tau)$$

Approving action $A$ while rejecting action $B$ simultaneously creates a positive obligation to discharge $A$ and a negative obligation to suppress $B$. Across three execution boundaries (`GPT-6.1-Sol`, `DeepSeek V4.1 Flash`, and `Claude Haiku 5.5` on $\tau$-bench / $\tau^2$-bench Retail commit `96a3ef9`, $\tau^3$ banking, `6` agent harnesses, and `100` public `n8n 2.43.5` workflows; `arXiv:2611.19237`), refusal-only or static gate-presence checks systematically miss control failures:

| Execution Boundary | Audited System / Panel | Refusal Safety (Denied Effects) | Authorization Completeness / Transition Failure |
|:-------------------|:-----------------------|:--------------------------------|:------------------------------------------------|
| **Model Layer** | `300` paired Retail runs (`100`/model) + `3,300` 5-arm Approve runs | **`0 / 300`** denied (`0 / 72` under 4 persuasion pressures) | **`7 / 300` (`2.3%`)** paired approvals unfinished (`96/100` `GPT-6.1-Sol`, `100/100` `DeepSeek V4.1 Flash`, `97/100` `Claude Haiku 5.5`); **`68 / 3,300` (`2.06%`)** incomplete in expansion (`44`, `6`, `18`) |
| **Harness: Parallel Confirmation** | `Google ADK 2.14.0` (`18` episodes/model on 2-cancellation tasks `16, 32, 54`) | `0` denied effects | Combined parallel `approve-both` **loses `1` approved branch in `3 / 3` tasks** (`3/18` episodes) across all `3` models; sequential & separate replies lose **`0 / 3`** (`36/36` preserved in `OpenAI Agents SDK` & `LangGraph`) |
| **Harness: Checkpoint Resume** | `CrewAI 1.15.37` (`1,344` natural-failure episodes: `672` Approve, `672` Reject) | **`0 / 672`** (`672/672` suppressed) | **`336 / 672` (`50.0%`) approved effects omitted** after paused parallel join/router (scheduler drops pending-branch obligation despite persisted approval; **`672 / 672`** after join-bookkeeping repair) |
| **Harness: State & Scope Revision** | `Agno 3.1.12` ($\tau^3$ banking, `16` episodes/family $\times$ `3` protocols) | **`4 / 4` reserve breaches (`T1`)** & **`4 / 4` withdrawn transfers executed (`T2 W`)** | Intervening payment invalidates reserve precondition (`T1`), and conversational withdrawal fails to revoke the queued confirmation object (`T2 W`), while new approved work is omitted (`T2 O`: `2, 8, 0`; `T3 O` delegation: `0, 1, 7`) |
| **Workflow Layer** | `n8n 2.43.5` (`59` policy-comparable public workflows passing gate-presence checks) | **`4 / 59` (`6.8%`, Wilson CI `2.7%–16.2%`) execute protected effect after `Reject`** | `3` workflows (`5152, 5312, 8318`) never test the approval value; `1` (`11526`) routes to the `Reject` branch but writes `Status=Approved` (repaired `[1,1] -> [1,0]` by setting `Status=Pending`) |

---

## Step-by-Step Procedure

### Step 1: Instrument the Four-Witness Authorization Contract

Never grade approval compliance with an LLM judge over assistant prose (pairwise AI semantic $\kappa$ reached only `0.347–0.367` on severity and `0.190–0.477` on workflow semantics in `arXiv:2611.19237`, whereas native-effect ledgers achieved `1.00` precision and `1.00` recall across all three models). Capture four structured witnesses at every gated boundary:

1. **Witness 1 — Versioned Scoped Decision ($d_v$)**: Record `(version v, authorized_actions A_v, denied_effects D_v, preconditions C_v)`, binding each action in $A_v$ to its exact tool name and canonical target object, item subset, and payment/amount arguments.
2. **Witness 2 — Generated Model Calls**: Log the exact tool invocations and arguments emitted by the LLM after receiving $d_v$.
3. **Witness 3 — Runtime Dispatch Events**: Log which confirmed tool calls the harness scheduler actually dispatches to tool executors after confirmation aggregation, checkpoint restoration, or sub-agent handoff.
4. **Witness 4 — Native Business-State Effects & Feasibility Witnesses**: Verify state mutations directly in an isolated clone or intercepted backend service (`done(\tau)`). Whenever an authorized action $a \in A_{\mathrm{latest}}$ is missing from `done(\tau)` at horizon $H$, run an **isolated post-prefix native feasibility witness** on a state copy to separate *infeasible actions* from *dropped eligible obligations*—and keep legitimate **disclosure boundaries** (e.g., an agent pausing to disclose a newly discovered exchange-price difference before committing) distinct from silent omissions.

---

### Step 2: Harden Harness Scheduling Across Eight Preservation Targets

Audit and enforce eight state-preservation invariants in the orchestration runtime (`object identity`, `item subsets`, `pending work`, `conditional validity`, `decision revision`, `parallel aggregation`, `delegation`, and `persistence`):

1. **Preserve Per-Call Identity and Multiplicity in Parallel Confirmations**:
   - When an agent proposes $k > 1$ gated tool calls in a single turn (such as cancelling two orders), bind each confirmation request and human reply to its unique `call_id` and target-argument signature.
   - Do **not** collapse combined batch approvals (`approve-both`) into a scalar step-level boolean (`Google ADK 2.14.0` dropped `1` of `2` approved cancellations in `3/3` tasks under combined parallel replies while succeeding `3/3` under per-call separate or sequential replies).
2. **Persist Scheduler Join/Router Obligations Alongside Approval State**:
   - Storing `approved = true` in a database or checkpoint (`SQLite` / Flow state) does not guarantee execution if a paused parallel join or router forgets it must revisit the suspended branch (`CrewAI 1.15.37` omitted `336/672` approved actions despite intact business state and completed sibling branches).
   - Persist explicit pending-branch work items in the join/router queue and drain all satisfied sibling/router continuations upon resume.
3. **Re-Check Preconditions (`T1`) and Revoke Pending Confirmation Objects on Revision (`T2`)**:
   - Re-evaluate $C_v$ (e.g., account reserve floor, resource version) against live backend state immediately before dispatch so intervening transactions cannot trigger unauthorized overdrafts (`4/4` `T1` breaches).
   - Treat any conversational scope revision or withdrawal (`"cancel that transfer and pay B instead"`) as an explicit version bump $d_v \to d_{v+1}$ that **atomically revokes or tombstones** the in-memory/persisted confirmation object for $d_v$ *before* resuming execution (`4/4` `T2` withdrawn transfers executed when confirmation objects remained active).
4. **Pass Scoped Consent + Completion Ledgers Across Deferred Turns and Delegations (`T3`)**:
   - In multi-turn continuations and specialist sub-agent handoffs, pass an explicit structured ledger of `(authorized_pending P(\tau), completed done(\tau), denied D_v)` rather than relying on raw chat history alone (`GPT-6.1-Sol` and `Claude Haiku 5.5` both reached `150/150` completion in the ledger arm `L`, and action-specific scope restatement `S` lifted `GPT-6.1-Sol` matched tasks from `142/150` to `150/150`).

---

### Step 3: Audit Workflow Graphs via Paired `Approve`/`Reject` Native Suffix Replay

Static graph inspection (`gate-presence coverage`) is insufficient for low-code or DAG workflows (`4/59` public `n8n` workflows with visible wait/approval nodes still executed the protected side effect on `Reject`):

1. **Construct Policy-Comparable Pairs**: Freeze upstream trigger payloads and external read fixtures, and stub all downstream mutating sinks (email, database, social publishing, payment, ticketing) with local request-intercepting witnesses.
2. **Execute Both Polarities from the Decision Node**: Replay the exact workflow suffix once with `Approve` and once with `Reject`:
   - Require the `Approve` positive control to reach the protected sink (`effect = 1`), filtering out dead or misconfigured graphs.
   - Require the `Reject` run to produce zero protected-sink mutations (`effect = 0`; rejection notifications and refusal audit logs are allowed).
3. **Scan Rejection Paths Statically and Dynamically for Two Defect Signatures**:
   - *Untested decision variables*: Downstream nodes wired after a wait/webhook node without an `IF`/`Switch` predicate over the decision field (`n8n` sources `5152`, `5312`, `8318`).
   - *Hardcoded approval literals on rejection edges*: Rejection branches that write literal `Status=Approved` or equivalent commit flags into shared records (`n8n` source `11526`).

---

### Step 4: Localize Divergences Deterministic-First by Earliest Witness Gap

When a paired audit fails (`effect != [1, 0]` or $P(\tau) \neq \emptyset$ with a passing post-prefix feasibility witness), localize the repair target by finding the **first divergence** along the four-witness chain (`140/140` [`1.00` accuracy] across predeclared model, harness, and workflow fault injections):

1. **`Decision recorded` ($a \in A_v$), but `Model call absent`**: Model-layer omission or target confusion (e.g., confusing profile vs. order address, reopening already-approved items, or dropping an item across deferred turns). *Fix*: attach a structured pending-work ledger (`L`) and action-specific scope restatement (`S`), verifying first whether the pause was a valid price/condition disclosure boundary.
2. **`Model call generated`, but `Harness dispatch absent` or `Stale/withdrawn call dispatched`**: Harness scheduling, parallel confirmation aggregation, checkpoint join restoration, or unrevoked confirmation object bug. *Fix*: key confirmations by `(call_id, version v)`, persist join pending-branch queues across suspend/resume, and re-verify $(d_{\mathrm{latest}}, C_{\mathrm{latest}})$ at pre-dispatch commit.
3. **`Reject recorded` ($e \in D_v$), yet `Protected sink effect observed`**: Decision-insensitive workflow edge or hardcoded approval payload literal. *Fix*: wire explicit polarity predicates and assert `[1, 0]` paired suffix replay in CI.

---

## Environment Caveats & Limitations

- **Diagnostic panels vs. natural deployment base rates**: The `100`-case Retail panel, `42`-proposal `CrewAI` restoration matrix, and `100` screened `n8n` workflows target risk-relevant transitions (`deferred continuation`, `parallel batches`, `paused joins`, `conditional reserves`) to isolate reproducible failure mechanisms; their failure percentages (`2.3%`, `50.0%`, `6.8%`) are mechanism diagnostics, not population-wide prevalence estimates.
- **Exploratory prompt contrasts**: On the random `30`-task matched subset, action-specific restatement (`S`) improved `GPT-6.1-Sol` from `142/150` to `150/150` (`+5.33` pp, cluster bootstrap CI `[0, 6]`, exact task-level McNemar $p = .25$; `+4.0` pp, sign test $p = .25$ on the `20`-task frozen diagnostic) while moving `Claude Haiku 5.5` slightly in the opposite direction (`144/150` `S` vs `150/150` `L`); treat prompt restatement as a model-localization diagnostic and rely on deterministic runtime ledgers for enforcement.
- **Channel authenticity is orthogonal**: Preserving `Approve`/`Reject` fidelity inside the harness and workflow assumes the decision input itself came from an authenticated human rather than a prompt-injected agent reading its own email/UI channel—pair with [`out-of-band-hitl-verification`](../out-of-band-hitl-verification/SKILL.md) when the host or inbox is untrusted.

---

## Cross-References

- **Related Rules**:
  - [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DO: Verify both denied-effect suppression and bounded approval completion across decision, call, dispatch, and native-state witnesses"`, `"DO: Isolate human-in-the-loop approval gates onto an out-of-band, hardware-attested trusted device with a trusted display"`, `"DON'T: Trust checkpoint state without integrity verification"`, and `"DON'T: Treat HTTP 200 / success tool return codes as workflow success without state verification"`
  - [`adk-workflow-architecture.md`](../../rules/adk-workflow-architecture.md) — `"DO: Enforce human approvals and safety gates in the runtime, NOT in prompt instructions"` and `"DO: Apply the Universal Resumption Pattern across human and tool suspensions"`
  - [`agent-human-interaction.md`](../../rules/agent-human-interaction.md) — `"DON'T: Let a stored user approval outlive the context it was granted in"`
  - [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Related Skills**:
  - [`out-of-band-hitl-verification`](../out-of-band-hitl-verification/SKILL.md) — Hardware-attested out-of-band HITL confirmation (`I-HITL`)
  - [`cross-interface-route-bound-authorization`](../cross-interface-route-bound-authorization/SKILL.md) — Route-bound prepare-commit tickets and three-valued finality across GUI/CLI/API/MCP
  - [`residual-auth-state-preservation`](../residual-auth-state-preservation/SKILL.md) — Task-bound consent lifetime and replay prevention
  - [`dependency-scoped-plan-validation`](../dependency-scoped-plan-validation/SKILL.md) — Validating pending actions against superseded requirements (`PlanFence`)

## Sources

- Deng, B., Lu, X., Chen, W., Wen, C., Wang, Y., Meng, J., Yu, Y., Liang, L., Han, W., Hong, Z., & Yu, Z. (2026). *Auditable Authorization for LLM Agents: Empirical Evidence Across Model, Harness, and Workflow Layers*. [arXiv:2611.19237](https://arxiv.org/abs/2611.19237) (`src:2611-19237v1`).
