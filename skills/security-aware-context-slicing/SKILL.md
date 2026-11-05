---
name: security-aware-context-slicing
description: >
  Construct security-aware repository context for code generation and coding agents using CWE-agnostic source-sink call-graph slicing, early-exit endpoint guard linking, and static exemplar screening. Prevents silent omission of project-specific validators and imitation of unfixed sibling vulnerabilities. Derived from A.S.E 2.0 / CASE-Bench (arXiv:2611.06294).
---

# Security-Aware Repository Context Slicing

> **Source**: [arXiv:2611.06294](https://arxiv.org/abs/2611.06294) | `src:2611-06294`

## When to Use

- Building or operating a repository-level code generation pipeline, RAG retriever, or autonomous coding agent (`SWE-agent`, `Claude Code`, IDE completion) on multi-file codebases.
- Generating or modifying code that touches untrusted inputs (HTTP parameters, CLI arguments, deserialized payloads, file paths), sensitive operations (SQL/command execution, memory allocation/copy, file I/O), or access-control boundaries (permissions, session state, multi-tenant isolation).
- Curating few-shot or sibling code examples from the surrounding repository when legacy or unpatched sibling functions may exist in the codebase.

## When NOT to Use

- Isolated single-function algorithmic tasks with no external inputs, privileged sinks, or repository-level helper contracts.
- Purely static vulnerability scanning of already-written code where no context assembly or code synthesis occurs.

---

## Core Insight

Standard functionality-oriented repository retrieval (lexical `BM25`, dense embeddings, import-graph expansion, and agentic grep/file search) optimizes for **functional similarity** (`FuncPass@1`) while remaining blind to **security enforcement roles** (validators, safe wrapper APIs, and project-specific access policies). Across `49,590` generations on `CASE-Bench` (`145` real CVE tasks across `51` repositories, median `86 KLOC` / `1.1M` tokens), all `11` functionality-oriented retrieval methods improve `FuncPass@1` (by up to `+8.2 pp`) yet fail to produce any statistically significant gain in `SecPass@1` (`-1.1` to `+3.7 pp`, $p_{\text{Holm}} \ge .19$), leaving **`40.3%` to `50.2%` of all generated patches functionally correct but exploitable (`CbE@1`)**.

Worse, expanding retrieval budgets beyond `8K` tokens (or feeding `128K` full-repo contexts / running unconstrained coding agents over `127K–204K` tokens) actively **degrades security**: as context grows from `8K` to `32K` tokens, the fraction of contexts containing an unfixed sibling vulnerability (**insecure exemplar**) jumps from `41%` to `90%`, causing `SecPass@1` to drop (`16.6%` $\to$ `14.6%`). Even when a safeguard is retrieved, burying it in the middle of a `64K` context costs `-5.9 pp` `SecPass@1`, and `50%` of remaining `CbE` failures (`21.3` per `100` generations) occur because the model leaves the retrieved safeguard **unused or misused** (e.g., called on the wrong path or without checking its return value).

---

## The Procedure

### Step 1: Classify Task Security Locality and Anchor Sources and Sinks

Before retrieving sibling implementations, parse the target file around the focal edit region to identify dataflow and control-flow anchors without assuming a fixed CWE taxonomy:

1. **Untrusted Sources**: Mark function parameters, request objects, headers, environment reads, database/file reads, and deserialization entry points entering the focal function.
2. **Sensitive Sinks**: Mark calls to command/query execution, filesystem mutation, network dispatch, raw memory indexing/copying, response serialization, and state-mutating domain APIs.
3. **Locality Tier Assessment**:
   - `L1` (Language built-in): Standard bounds or null checks sufficient.
   - `L2` (Project API): Requires calling a repository-specific sanitizer, safe wrapper, or validator module (`67/145` tasks in `CASE-Bench`).
   - `L3` (Repository policy): Requires enforcing custom authorization rules, caller contracts, or state preconditions (`37/145` tasks, including nearly all access-control bugs).

If the edit touches `L2` or `L3` surfaces, functional similarity search alone is insufficient; proceed to Step 2.

### Step 2: Execute Two-Hop Source-Sink Guard Slicing

Construct a compact (`~4K` token) security slice over the repository's import and call graphs:

1. **Two-Hop Call-Graph Neighborhood**: From the focal function and its resolved imports, traverse up to `2` hops along caller and callee edges connecting any identified source to any identified sink.
2. **Path-Condition and Guard Extraction**: Along every candidate path between a source and a sink, extract conditional branches, early-return guards, exception-raising predicates, and helper functions whose names, types, or control flow gate execution before the sink (validators, sanitizers, permission checks, safe wrapper APIs).
3. **Request-to-Endpoint Early-Exit Linking (Web & API Handlers)**: Frameworks often decouple authentication/authorization middleware or decorators from endpoint bodies without explicit call edges. Link request-handling entry points to endpoint bodies by scanning for shared request/context state mutations and early-exit return patterns (such as status-code returns, redirect responses, or permission-denied exceptions) across sibling handlers in the same router or controller module.

### Step 3: Screen Retrieved Sibling Exemplars Against Static Anti-Patterns

Before adding any similarity-retrieved sibling function or usage example to the prompt context:

1. **Detect Unfixed Sibling Exemplars**: Run lightweight static pattern checks (`CodeQL` / `Joern` queries or AST structural rules matching unguarded source-to-sink flows) on candidate sibling snippets. In `CASE-Bench`, `74` of `145` real-world CVE tasks contain naturally occurring insecure sibling functions elsewhere in the repository, and injecting **even a single insecure exemplar into a context that already contains the correct safeguard increases `CbE@1` by `+6.3 pp`** (`+4.8 pp` in functional retrieval contexts).
2. **Filter or Annotate**: Drop any sibling exemplar that invokes the target sink without an intervening guard or safe API. If a sibling exemplar must be retained to illustrate functional wiring, strip the unguarded sink call or explicitly annotate it as a prohibited anti-pattern.
3. **Enforce Tight Token Budgets (`4K–8K` Cap for Retrieval Slices)**: Do not pad the context with low-relevance repository files. Irrelevant code dilutes security density (from `.19` at `8K` to `.06` at `32K`), whereas a focused `4.1K`-token `Source-sink` slice achieves `0.74` fix-API recall and outperforms `118K`-token `Repo-128K` contexts by `+6.0 pp` `SecPass@1` (`18.1%` vs. `12.1%`).

### Step 4: Position Safeguards at Context Boundaries with Explicit Contract Summaries

How safeguards are packed into the prompt determines whether the model notices and invokes them:

1. **Boundary Placement (Avoid the Middle of Long Contexts)**: Place extracted validators, safe APIs, and policy checks at the **beginning or end** of the retrieved context block, immediately adjacent to the focal task instructions and target file. Moving a safeguard from the boundary to the middle of a `64K` context degrades `SecPass@1` by `-5.9 pp` (`-0.6 pp` at `4K`).
2. **Preserve Security-Indicative Identifiers and Contracts**: Do not obfuscate or strip docstrings/type signatures from security helpers. Neutralizing security-indicative function names repository-wide drops `SecPass@1` by `-3.1 pp` (`-4.6 pp` on web tasks). Include the helper's **caller contract** (whether it returns a boolean, mutates the input in place, returns a sanitized copy, or raises on failure)—omitting the caller contract alone costs `-3.9 pp` `SecPass@1`.

### Step 5: Verify Post-Generation Safeguard Utilization Before Acceptance

Retrieving the right safeguard solves *discovery* (`Missing` failures drop from `20.6` to `12.3` per `100` generations), but **utilization failures (`Unused` + `Misused`) double from `10.7` to `21.3` per `100` generations** (`50%` of all remaining `CbE` cases). Before accepting a generated patch:

1. **Check Safeguard Invocation (`Unused` Check)**: Verify that at least one retrieved validator, safe wrapper API, or policy check is actually called in the generated patch. In coding-agent trajectories (`SWE-agent`, `Claude Code`), `41%` of runs that successfully observed the repository safeguard left it completely unused (`15.8%` `SecPass@1` when unused vs. `34.5%` when observed and used).
2. **Check Control-Flow Dominance and Return Handling (`Misused` Check)**: Confirm that:
   - The safeguard executes **on every control-flow path** leading from the untrusted source to the sensitive sink (not bypassed by an `else` branch or fallback path).
   - If the safeguard returns a sanitized value or boolean status rather than raising an exception, the return value is **captured and checked** before the sink is reached.
   - The arguments passed to the safeguard match the untrusted variable actually consumed by the sink.
3. **Execute Both Functional Tests and Exploit/Boundary Oracles**: Static analyzers (`CodeQL` + `Joern`) disagree with executable proof-of-concept (`PoC`) exploit oracles on `36.8%` of functionally correct generations ($\kappa = 0.25$, missing `40%` of exploited patches while falsely flagging `27%` of `PoC`-resistant patches). Whenever possible, pair static taint verification with an executable negative/exploit test case.

---

## Quantitative Summary (`CASE-Bench`: `145` CVE Tasks, `6` LLMs, `98,730` Generations + `1,305` Agent Runs)

| Context / Agent Method | Avg. Context Tokens | `FuncPass@1` (`%`) | `SecPass@1` (`%`) | `CbE@1` (Correct-but-Exploitable, `%`) | Access Control `SecPass@1` (`25` `L3` tasks) | Key Finding |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `Local-only` (Target file + requirement) | `1.9K` | `56.9%` | `12.6%` | `44.3%` | `2.0%` | Baseline without cross-file context |
| `ProCC-Multi` (Best `FuncPass` retrieval) | `7.4K` | **`65.1%`** (`+8.2 pp`) | `14.9%` (`+2.3 pp`, NS) | `50.2%` | — | `72%` of functional gain is exploitable (`CbE`) |
| `ClaudeCode-Ret` (Best `SecPass` func. retrieval) | `6.8K` | `63.8%` (`+6.9 pp`) | `16.3%` (`+3.7 pp`, $p_{\text{Holm}}=.19$) | `47.5%` | `2.9%` | All `11` func. retrievers fail significance on `SecPass@1` |
| `Repo-128K` (Long-context dump) | `118K` | `60.9%` (`+4.0 pp`) | `12.1%` (`-0.5 pp`) | `48.8%` | — | Flooding context lowers security below `Local-only` |
| `Security reminder` (Prompt priming only) | `1.9K` | `55.1%` (`-1.8 pp`) | `13.9%` (`+1.3 pp`, NS) | `41.2%` | — | Generic reminders cannot invent `L2`/`L3` project APIs |
| `CodeGuarder` (Prior security retrieval) | `5.3K` | `58.8%` | `16.8%` (`+4.2 pp`) | `42.0%` | `3.1%` | Misses web/access-control policies |
| **`Source-sink` (This Skill)** | **`4.1K`** | **`61.2%`** | **`18.1%`** (`+5.5 pp`, OR `1.53`, $p_{\text{Holm}}=.006$) | **`43.1%`** | **`9.3%`** (`+7.3 pp`) | `0.74` fix-API recall; `+6.8 pp` on `L2` and `+7.4 pp` on `L3` |
| `Reference context` (Oracle ground-truth files) | `2.7K` | `62.3%` | `24.8%` (`+12.2 pp`) | `37.5%` | `17.6%` | Upper bound when all safeguards are present and clean |
| `SWE-agent` (`Sonnet 4.5` / `GPT-5.4`) | `141K` / `127K` | `69.7%` / `71.0%` | `16.6%` / `16.1%` | `53.1%` / `54.9%` | — | Observes safeguard in `29%`/`27%` of runs vs. insecure exemplar in `46%`/`43%` |
| `Claude Code` (`Sonnet 4.5` agent) | `204K` | `74.0%` | `18.4%` | `55.6%` | — | `26x` more tokens than `8K` retrieval for `+0.5 pp` `SecPass@1` (`$1.41` vs. `$0.09`) |

---

## Failure Modes & Mitigations

| Failure Mode | Measured Impact (`CASE-Bench`) | Mitigation |
|:---|:---|:---|
| **Missing Safeguard** (`Missing`) | `20.6%` of all generations (`46%` of `CbE`) under functional retrieval; removing safe API / validator / policy from `Reference` costs `-8.1` / `-6.7` / `-5.2 pp` (`-11.3 pp` on access control) | Run Step 2 (`Source-sink` 2-hop call-graph + early-exit guard slicing) rather than lexical/embedding similarity search (`71%` of agent queries target functional entities vs. `9%` security). |
| **Imitating Unfixed Sibling Code** (`Imitated`) | `9.0%` of generations (`20%` of `CbE`); `1` insecure exemplar in `Reference context` raises `CbE@1` by `+6.3 pp`; observing one in agent runs raises `CbE@1` from `48.4%` to `61.6%` | Run Step 3 static screening on all retrieved sibling snippets and cap retrieval context at `4K–8K` tokens (expanding `8K` $\to$ `32K` raises insecure-exemplar exposure from `41%` to `90%`). |
| **Unused Safeguard** (`Unused`) | Doubles from `6.7%` to `11.9%` of generations under security-aware context; `41%` of agent trajectories that observe a safeguard never call it (`15.8%` vs. `34.5%` `SecPass@1`) | Place safeguards at prompt boundaries (Step 4) and enforce Step 5.1 post-generation check that the retrieved validator/safe API identifier appears in the diff. |
| **Misused Safeguard** (`Misused`) | Doubles from `4.0%` to `9.4%` of generations under security-aware context (incomplete path coverage, ignored boolean/sanitized return value, wrong argument) | Include the safeguard's caller contract in context (Step 4.2) and verify control-flow dominance + return-value binding in Step 5.2. |

---

## Related Skills & Rules

- **Skill**: [`cost-effective-repo-exploration`](../cost-effective-repo-exploration/SKILL.md) — Escalation-oriented repository search and handoff contracts for coding agents.
- **Skill**: [`requirements-driven-code-generation`](../requirements-driven-code-generation/SKILL.md) — Synthesizing formal contracts and requirement-bound tests prior to implementation.
- **Skill**: [`counterexample-guided-repair`](../counterexample-guided-repair/SKILL.md) — Refining artifacts using executable false-positive and false-negative witnesses.
- **Rules**: [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — Security guardrails for coding and tool-using agents.
- **Rules**: [`skill-system-design.md`](../../rules/skill-system-design.md) — Context budget discipline and position-aware context assembly.
