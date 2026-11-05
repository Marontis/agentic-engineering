---
name: counterfactual-tool-dependency-induction
description: >-
  Induce runtime-verified tool dependency graphs ahead of time without task
  trajectories by synthesizing per-tool executable contracts, testing
  input-provenance and state-precondition edges via counterfactual sandbox
  execution, and applying bounded one-hop retrieval propagation. Derived from
  LIBRA (arXiv:2611.05445).
---

# Counterfactual Tool Dependency Induction

> **Source**: [arXiv:2611.05445](https://arxiv.org/abs/2611.05445) — *LIBRA: Programmatic Induction of Executable Tool Libraries* (Li et al., 2026) | `src:2611-05445v1`

## When to Use This Skill

Use this procedure when an agent operates over a large catalog of executable tools, APIs, or MCP endpoints (hundreds of tools across multi-step workflows) where dense query-to-tool retrieval misses **prerequisite provider tools** — such as authentication/login calls, entity-ID lookup endpoints, or schema-inspection helpers — that are never mentioned in the user's natural-language prompt. Unlike trajectory-mined tool graphs (which require historical task logs) or schema-only similarity graphs (which flood retrieval with false-positive type matches), this procedure constructs a runtime-verified directed dependency graph $\mathcal{L} = (\mathcal{T}, \mathcal{C}, \mathcal{E})$ **ahead of time from tool metadata and sandbox execution alone**, requiring zero user queries and zero training trajectories.

---

## Why Schema Matching Fails Without Counterfactual Execution

Many tool pairs share superficial parameter names or primitive types (`string`, `int`, `id`) without any true operational dependency. On `AppWorld` (473 tools), `SciToolEval` (477 tools), and `BFCL v4` (128 tools), propagating retrieval scores over a **Schema-Only** graph (edges accepted whenever output/input types and field embeddings match) yields virtually zero gain over standalone dense retrieval (`QTS`): **29.2% vs 28.7%** Recall@15 on `AppWorld`, **84.1% vs 84.1%** Recall@10 on `SciToolEval`, and **81.4% vs 81.8%** Recall@15 on `BFCL`. Filtering candidate pairs through **counterfactual sandbox execution** prunes **581,690** candidates down to **1,946** verified edges on `AppWorld`, **163,608** down to **732** on `SciToolEval`, and **12,762** down to **672** (595 value-based + 77 state-based) on `BFCL`, lifting one-shot Recall by **+12.0**, **+7.0**, and **+4.6** percentage points (**+7.9 pp** average Recall and **+3.7 pp** NDCG) and recovering **18.3% to 58.8%** of dense retrieval misses.

---

## Step-by-Step Procedure

### Step 1: Synthesize Per-Tool Executable Contracts ($O(|\mathcal{T}|)$ LLM Calls)

Before testing pairwise tool interactions, induce a structured executable contract $c_i = (\Pi_i, \mathcal{X}_i, S_i^+, S_i^-)$ for each tool $t_i \in \mathcal{T}$ using only its public documentation and parameter schema:
1. **Draft Initial Contract**: Prompt an LLM at temperature 0 to propose:
   - **Preconditions ($\Pi_i$)**: Required argument types, value constraints, and environment state assumptions.
   - **Exported Outputs ($\mathcal{X}_i$)**: Structured return fields and state mutations produced on success.
   - **Positive Test Suites ($S_i^+$)** and **Negative Test Suites ($S_i^-$)**: Minimal concrete invocation arguments expected to succeed and fail in a clean sandbox snapshot.
2. **Bounded Runtime Revision ($\le 2$ retries)**: Execute $S_i^+$ and $S_i^-$ inside an isolated sandbox snapshot. If a positive test fails unexpectedly or a return schema mismatches $\mathcal{X}_i$, feed the exact runtime exception and return payload back to the LLM to revise $c_i$ for **at most 2 revision rounds**. This keeps LLM cost strictly linear in catalog size ($1 + \le 2$ calls per tool; e.g., only 218 total revisions across 473 `AppWorld` tools, 48 across 477 `SciToolEval` tools, and 37 across 128 `BFCL` tools) while ensuring every tool has a known-good invocation template and captured output fixtures.

---

### Step 2: Induce Directed Edges via Counterfactual Sandbox Execution

Using the captured outputs and valid invocation templates from Step 1, test candidate provider-consumer pairs $(t_p, t_c)$ in isolated, resettable sandbox snapshots $\sigma$ using two counterfactual protocols:

#### Protocol A: Input-Provenance and Compatibility Edges ($\mathcal{E}_{\text{prov}}, \mathcal{E}_{\text{comp}}$)
For a candidate pair where output field $f_{\text{out}} \in \mathcal{X}_p$ of provider $t_p$ is type-compatible with input parameter $f_{\text{in}}$ of consumer $t_c$:
1. **Treatment Execution (Provider-Supplied Value)**: From sandbox state $\sigma$, execute $t_p$ to obtain real output value $v = t_p(\dots)[f_{\text{out}}]$, then invoke consumer $t_c$ with $f_{\text{in}} \leftarrow v$ (holding all other required arguments of $t_c$ at their validated template values from $S_c^+$). If $t_c$ fails, discard the candidate pair immediately.
2. **Counterfactual Control Execution (Synthetic Literal or Omission)**: Reset the sandbox to the exact state $\sigma$ (after $t_p$ has run, so any state side effect of $t_p$ is held constant) and invoke $t_c$ again, replacing $v$ at parameter $f_{\text{in}}$ with an independently synthesized type-valid literal $\tilde{v}$ (or omitting $f_{\text{in}}$ if optional).
3. **Edge Classification**:
   - **Strict Input-Provenance Edge ($\mathcal{E}_{\text{prov}}$)**: If $t_c$ **succeeds** with the provider's output $v$ and **fails** under the counterfactual control $\tilde{v}$, retain $(t_p, t_c, f_{\text{out}} \rightarrow f_{\text{in}})$ as a verified provenance dependency (for example, an opaque token, live record ID, or file handle that cannot be guessed).
   - **Value-Compatibility Edge ($\mathcal{E}_{\text{comp}}$)**: If $t_c$ succeeds under both $v$ and $\tilde{v}$, retain the edge **only if** the dense field-embedding cosine similarity between the output and input descriptions clears a strict threshold $\cos(h_f(f_{\text{out}}), h_f(f_{\text{in}})) > \tau$; otherwise discard it as a coincidental primitive type match.

#### Protocol B: State-Dependency Edges ($\mathcal{E}_{\text{state}}$)
Some provider tools enable a consumer solely by mutating environment state (such as logging in, mounting a workspace, or initializing a session) without passing an output value into $t_c$'s arguments:
1. **Before-Provider Control**: In initial sandbox state $\sigma$, invoke consumer $t_c$ with its validated arguments $x_c \in S_c^+$.
2. **After-Provider Treatment**: Execute provider $t_p$ to transition the sandbox to state $\sigma'$, then invoke $t_c$ with the **exact same arguments** $x_c$.
3. **Edge Classification**: Retain a directed state-dependency edge $(t_p \rightarrow t_c) \in \mathcal{E}_{\text{state}}$ **if and only if** $t_c(x_c)$ fails in state $\sigma$ and succeeds in state $\sigma'$.

---

### Step 3: Prune and Propagate Scores via Bounded One-Hop Retrieval

At query time, given user request $q$, use the induced edge set $\mathcal{E} = \mathcal{E}_{\text{prov}} \cup \mathcal{E}_{\text{comp}} \cup \mathcal{E}_{\text{state}}$ to surface prerequisite tools alongside directly relevant consumer tools:

1. **Compute Base Dense Relevance**: Embed the user query $q$ and each tool's **original public metadata** (do not stuff synthesized contracts into the tool text, which degrades base dense retrieval) to obtain base similarity scores $s_q(t)$ for all $t \in \mathcal{T}$.
2. **Select Top-$K_s$ Consumer Seeds**: Identify the top $K_s$ tools by base score $s_q(t)$ (default $K_s = 15$) as candidate consumer seeds.
3. **Enforce Top-2 Per-Input Provider Pruning**: Unbounded fan-in from all validated providers floods the top-$K$ cutoff with redundant helpers (dropping `SciToolEval` Recall@10 from **91.1%** to **76.4%** and NDCG from **86.6%** to **75.0%**). For each input parameter $f_{\text{in}}$ of a seeded consumer $t$, retain **at most 2** incoming provider tools $u$:
   - **`Field-best` ($u_{\text{field}}$)**: The validated provider whose output field $f_{\text{out}}$ has the highest embedding similarity to $f_{\text{in}}$.
   - **`Dense-best` ($u_{\text{dense}}$)**: The validated provider with the highest direct query relevance $s_q(u)$ for the current query $q$.
   (Plus any verified state-dependency provider $(u \rightarrow t) \in \mathcal{E}_{\text{state}}$.)
4. **One-Hop Max-Mean Score Propagation**: Let $C_q(u)$ be the set of seeded consumer tools for which provider $u$ was retained in step 3. Compute the propagated score:
   $$g_q(u) = \frac{s_q(u) + \sum_{t \in C_q(u)} s_q(t)}{1 + |C_q(u)|}$$
   Set each tool's final retrieval score to $s'_q(u) = \max\!\big(s_q(u),\, g_q(u)\big)$ and return the top-$K$ tools sorted by $s'_q$.
   - **Stop at 1 hop**: Do not propagate across 2 or more hops by default; 2-hop propagation dilutes precision with transitive noise, reducing `SciToolEval` Recall@10 by **−2.3 pp** (**88.8%** vs **91.1%**) with no gain on `AppWorld` or `BFCL`.

---

## Integration with Iterative Agentic Retrieval

When the agent uses an iterative retrieve-and-reason loop (such as `ToolReAGt`, where the agent refines search queries across turns), apply the exact same 1-hop propagation on every retrieval turn. Across 3 LLMs (`Gemma-4-12B`, `Nemotron-9B`, `Qwen3.5-9B`) and 10 iterations, pairing agentic retrieval with counterfactual dependency propagation improves Recall by **+4.5 pp** and NDCG by **+2.9 pp** on average over dense agentic retrieval (+8.5 pp Recall on `AppWorld`), winning **8 of 9** model-benchmark settings at iteration 10 and **30 of 36** intermediate checkpoints.

---

## Failure Modes & Guardrails

| Pitfall | Why It Fails | Guardrail |
|:---|:---|:---|
| **Accepting edges on positive execution alone** | Consumer tools with optional or permissive string/integer parameters succeed even when passed arbitrary values, creating thousands of spurious edges. | Always run the counterfactual control ($\tilde{v}$ replacement for value edges; pre-provider invocation in state $\sigma$ for state edges) and require control failure for $\mathcal{E}_{\text{prov}}$ and $\mathcal{E}_{\text{state}}$. |
| **Propagating over all validated providers per parameter** | A single popular consumer parameter with 20 valid providers crowds out other required tools in the top-$K$ window (−14.7 pp Recall on `SciToolEval`). | Cap incoming providers to at most **2 per consumer input parameter** (`Field-best` + `Dense-best`). |
| **Appending synthesized contracts into tool index text** | Verbose LLM-generated preconditions and test fixtures shift tool embeddings away from natural user queries. | Index only the canonical tool metadata for base score $s_q(t)$; use synthesized contracts strictly for sandbox edge induction. |
| **Executing un-sandboxed mutative tools during induction** | Pairwise probing invokes tools hundreds of thousands of times (e.g., 581,690 pairs on `AppWorld`). | Run all contract and counterfactual probes inside disposable, snapshot-resettable sandboxes with external network/production side effects blocked. |

---

## Related Skills and Rules

- [`capability-aware-skill-selection`](../capability-aware-skill-selection/SKILL.md) — Set-level selection of complementary capabilities under a token budget.
- [`decoupled-interface-action-repair`](../decoupled-interface-action-repair/SKILL.md) — Progressive tool disclosure (`get_tool` + `invoke_tool`) and local action repair.
- [`speculative-macro-commit`](../speculative-macro-commit/SKILL.md) — Speculative execution of recurring multi-step tool chains in sandbox snapshots.
- [`rules/skill-system-design.md`](../../rules/skill-system-design.md) — "DON'T: Rely on dense semantic embeddings alone for retrieving code or executable skills without execution verification".
- [`rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — "DO: Snapshot before uncertain commands".
