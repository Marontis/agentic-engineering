# Defensive Analysis of Post-Hoc Logging Prompt Injection in Model Context Protocol (MCP) Agents

> **Source**: [arXiv:2610.36108](https://arxiv.org/abs/2610.36108) — *"Log-To-Leak: Prompt Injection Attacks on Tool-Using LLM Agents via the Model Context Protocol"* (Oct 2026)
> **Praxis Source ID**: `src:2610-36108`
> **Tier**: Research Brief (Defensive Security Analysis)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Summary & Vulnerability Surface

When an LLM agent connects to multiple Model Context Protocol (MCP) servers simultaneously, the MCP client aggregates the JSON tool schemas (`name`, `description`, `inputSchema` parameter names, and default values) from **every enabled server** into a single unified prompt context. Unlike classic tool-hijacking attacks that attempt to divert the agent away from the user's primary task—making the failure immediately visible to the user—**post-hoc logging injection (`Log-To-Leak`)** is an **additive, task-preserving attack**:

1. The agent executes the legitimate target tool call $t^{(k)}$ on the target MCP server (e.g., `GitHub`, `Mapbox`, `PayPal`, `Playwright`, or `YFinance`) and receives the sensitive tool output $o^{(k)}$.
2. Before returning the final natural-language answer $r_{\mathcal{A}}$ to the user, a poisoned tool `description` registered by a co-installed third-party MCP server instructs the agent to invoke a secondary logging tool (`save_logs`) with the 4-field session tuple $\mathcal{S} = \langle q, s^{(k)}, o^{(k)}, r_{\mathcal{A}} \rangle$ (user query, target server name, raw tool output, and drafted response).
3. The user receives a complete, accurate answer to their original request while the full interaction trace is silently exfiltrated across server boundaries.

### Empirical Vulnerability Across 18 Model–Server Pairs (555 Evaluation Queries)

The authors evaluate `555` realistic user queries across `5` production MCP servers (`GitHub` `160`, `Mapbox` `160`, `PayPal` `160`, `Playwright` `35`, `YFinance` `40`) and `4` LLM backbones (`GPT-4o`, `Claude-Sonnet-4`, `GPT-5`, and `GPT-OSS-120B`), plus end-to-end verification in deployed **Cursor** (`GPT-5.1`) and **Claude Desktop** (`Claude-Sonnet-4.5`) clients:

| Target MCP Server | Metric | `GPT-4o` | `Claude-Sonnet-4` | `GPT-5` | `GPT-OSS-120B` |
|:---|:---|:---|:---|:---|:---|
| **GitHub** (`160` queries) | `ASR` / `LA` | `62.64%` / `86.26%` | `99.38%` / `95.60%` | `78.57%` / `88.64%` | `97.35%` / `87.30%` |
| **GitHub** (`160` queries) | `TCR` ($\Delta_{\text{TCR}}$) | `99.38%` (`0.00%`) | `100.00%` (`0.00%`) | `78.50%` (`-21.50%`) | `94.38%` (`-1.25%`) |
| **Mapbox** (`160` queries) | `ASR` / `LA` | `90.63%` / `86.38%` | `100.00%` / `93.13%` | `86.21%` / `91.20%` | `98.61%` / `88.91%` |
| **Mapbox** (`160` queries) | `TCR` ($\Delta_{\text{TCR}}$) | `100.00%` (`+0.63%`) | `100.00%` (`0.00%`) | `81.62%` (`-18.38%`) | `90.00%` (`-6.25%`) |
| **PayPal** (`160` queries) | `ASR` / `LA` | `84.38%` / `86.85%` | `100.00%` / `95.63%` | `98.06%` / `92.33%` | `98.60%` / `76.55%` |
| **PayPal** (`160` queries) | `TCR` ($\Delta_{\text{TCR}}$) | `100.00%` (`0.00%`) | `100.00%` (`0.00%`) | `96.88%` (`+0.63%`) | `89.38%` (`-6.63%`) |
| **YFinance** (`40` queries) | `ASR` / `LA` | `100.00%` / `90.00%` | `100.00%` / `95.63%` | `0.00%`* (`0.00%` TCR) | `91.89%` / `81.62%` |
| **Playwright** (`35` queries) | `ASR` / `LA` | `73.53%` / `94.00%` | `91.43%` / `95.31%` | `0.00%`* (`0.00%` TCR) | `100.00%` / `95.64%` |

*\*Note: On `YFinance` and `Playwright`, `GPT-5` had `0.00%` baseline Target-Task Completion Rate (`TCR`) due to MCP tool-call formatting incompatibilities; across the **18 compatible model–server pairs**, Attack Success Rate (`ASR`) is **`62.64%–100.00%`** (`\ge 80%` in 15/18 pairs) and conditional Logging Accuracy (`LA` across the 4 exfiltrated fields) is **`76.55%–95.64%`**.*

### Key Vulnerability Findings

1. **Legitimate task completion is preserved, hiding the compromise from outcome monitors**:
   - In **`16 of 18`** compatible model–server pairs, the change in target-task completion rate satisfies **$|\Delta_{\text{TCR}}| \le 6.63\text{ percentage points}$**, and non-logging calls to the secondary server remain near zero ($|\Delta_{\text{MCR}}| \le 0.59\text{ pp}$; `0.00%` in 15/18 pairs).
   - Generic prompt-injection payloads adapted from prior work (`Combined Attack` at `4.32%` ASR, `-11.25%` $\Delta_{\text{TCR}}$; `TopicAttack` at `4.47%` ASR, `-13.75%` $\Delta_{\text{TCR}}$) fail to trigger post-hoc cross-server calls on `GitHub` + `GPT-4o`, whereas structured procedural framing (`Trigger` + `Tool Binding` + `Compliance Justification` + `Urgency Pressure`) reaches `62.64%–66.8%` ASR (`5.39x` higher than bare `Tool Binding` alone at `12.4%` ASR).
2. **Existing content, gradient, and graph defenses fail on MCP tool metadata**:
   - **Instruction detectors suffer catastrophic false positives on benign MCP schemas**: Because legitimate MCP tool descriptions naturally contain imperative instructions specifying *when* and *how* an agent must call a tool, the gradient/hidden-state instruction detector of Wen et al. (`Llama-3.1-8B-Instruct`) flags **`136 of 159 (85.53%)` benign MCP tool descriptions** as prompt injections (`82.22%` on GitHub `74/90`, `88.89%` on Mapbox `8/9`, `85.71%` on PayPal `24/28`, `100.00%` on YFinance `9/9`, `91.30%` on Playwright `21/23`) alongside `91.00%` (`91/100`) of injected descriptions—a separation of only `5.47 pp`.
   - **Canary and LLM auditors miss procedural metadata**: `DataSentinel` flags **`0 of 100` (`0.00%`)** poisoned tool descriptions (`100%` marked safe). A `GPT-4o` LLM Metadata Check flags only `11%` of poisoned descriptions, leaving **`55.38%` residual ASR** (`85.46%` LA).
   - **Prompt sandwiching and static tool-dependency graphs are bypassed**: `Prompt Sandwiching` leaves **`59.58%` residual ASR** (`84.71%` LA), and `IPIGuard` (which pre-plans a tool dependency graph from visible tool descriptions before execution) incorporates the poisoned logging rule directly into the planned DAG, leaving **`60.47%` residual ASR** (`90.87%` LA).

---

## Defensive Architecture & Mitigation Requirements

1. **Enforce host-controlled cross-server tool authorization (Never grant implicit execution authority to tool metadata)**:
   - MCP tool descriptions are untrusted documentation, not an authorization policy. The MCP host/client must enforce an explicit per-session capability policy: a tool from server $B$ cannot be invoked in a turn triggered by or consuming outputs from server $A$ unless the user or a deterministic host policy explicitly authorized cross-server composition (`A -> B`).
2. **Apply cross-server data-flow taint tracking at the MCP client boundary**:
   - Tag every tool output $o^{(k)}$ with its source server provenance $s^{(k)}$. Block or require explicit human confirmation whenever any subsequent tool call serializes tainted content from server $s^{(k)}$ into arguments destined for a different MCP server.
3. **Scope tool visibility per task rather than loading all connected MCP servers into one global context**:
   - Loading unrelated third-party MCP servers into the same prompt context creates an ambient cross-server exfiltration sink. Use capability routing to mount only the minimum server subset required for the user's current intent.
4. **Do not rely on text-based instruction classifiers to sanitize MCP tool schemas**:
   - With an `85.53%` false-positive rate on benign production MCP schemas and `>55%` residual ASR across prompt/LLM/graph defenses, security must be enforced deterministically at the **tool-invocation and data-egress boundary**, not via natural-language classification of tool docstrings.

---

## Why Not a Skill?

Per Praxis content standards, offensive prompt-injection payload templates are not extracted into skills, and the defensive mitigations (host-level cross-server capability grants, taint tracking across MCP server boundaries, and pre-execution tool authorization) are already covered procedurally by [`mcp-tool-hijacking-defense`](../skills/mcp-tool-hijacking-defense/SKILL.md), [`mcp-zero-trust-tool-authorization`](../skills/mcp-zero-trust-tool-authorization/SKILL.md), and [`provenance-capability-grants`](../skills/provenance-capability-grants/SKILL.md). This brief records the empirical failure rates of instruction detectors (`85.53%` FPR) and graph planners (`60.47%` residual ASR) against additive post-hoc MCP logging.

---

## Cross-References

- **Related Rules**: [`agent-sandbox-safety`](../rules/agent-sandbox-safety.md), [`adk-security-and-evaluation`](../rules/adk-security-and-evaluation.md)
- **Related Skills**: [`mcp-tool-hijacking-defense`](../skills/mcp-tool-hijacking-defense/SKILL.md), [`mcp-zero-trust-tool-authorization`](../skills/mcp-zero-trust-tool-authorization/SKILL.md), [`provenance-capability-grants`](../skills/provenance-capability-grants/SKILL.md), [`covert-tool-injection-defense`](../skills/covert-tool-injection-defense/SKILL.md)
