---
name: compile-then-execute-web-agent-gateway
description: >-
  Compile untrusted web-agent tasks offline against a strongly typed Trusted
  Website API contract before running them in an isolated runtime subprocess.
  Eliminates prompt injection from live DOM content while improving WebArena
  task completion through mock-validated Python execution plans and restricted
  error diagnostics. Derived from Baya (arXiv:2611.06039).
source: https://arxiv.org/abs/2611.06039
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Compile-Then-Execute Web Agent Gateway

> **Source**: [Securing Web Agents with the Compile-Then-Execute Paradigm](https://arxiv.org/abs/2611.06039) (Chow et al., 2026) | Praxis: `src:2611-06039v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Building or hardening web agents that interact with third-party websites, SaaS dashboards, e-commerce storefronts, or issue trackers containing untrusted user-generated content (issues, comments, product reviews, forum posts).
- Replacing iterative ReAct browser loops (`Observe DOM -> Think -> Act`) where untrusted website content enters the planner's context window at every step and can hijack control flow.
- Wrapping heterogeneous backend REST APIs and UI-only browser workflows behind a uniform, strongly typed tool gateway so the planning model never touches raw HTML or unvalidated API payloads during compilation.
- Reducing the latency and token overhead of per-step dual-LLM quarantine architectures such as Untrusted Content Masking (UCM) while maintaining structural prompt-injection immunity.

## Overview

Iterative ReAct web agents interleave planning and action inside a shared context window: at each step, the agent reads raw DOM trees or accessibility snapshots from the live website and decides what tool or UI action to invoke next. On the WebAgent Security Benchmark (WASP, `84` attack instances across GitLab and Postmill), standard ReAct browser agents (`ReAct_web`) suffer a `25.5%` aggregate intermediate Attack Success Rate (ASR)—reaching up to `50.0%` on Postmill with `DeepSeek-V4-Flash`—and even API-augmented ReAct agents (`ReAct_web + API`) suffer a `16.2%` aggregate intermediate ASR (`52.8%` on Postmill with `Gemini-3.5-Flash`). Prior analysis of WebArena shows that `81%` of tasks are *Safe* (solvable by a deterministic program compiled entirely from the user request and schema documentation), `19%` are *Safe with Influence* (solvable with fixed control flow plus a narrowly scoped, tool-free data interpretation call at runtime), and `0%` require runtime control-flow replanning from live page content.

**Baya** enforces a **Compile-Then-Execute** gateway architecture across three strict phases:

1. **Trusted Website API Construction (Pre-Task / Offline)**: Wrap website operations $\mathcal{A} = \{f_1, \dots, f_n\}$—both official REST endpoints and trusted Playwright browser routines for UI-only features—behind a formal machine-readable contract $\mathcal{C}(f) = (\Sigma, \mathcal{P}, \mathcal{Q}, \mathcal{E})$.
2. **Sandboxed Compilation & Mock Validation**: Inside a network-isolated compilation sandbox with zero access to the live website or credentials, compile the user's natural-language instruction into an executable Python script and a companion unit-test suite that mocks all API, auth, and data-only LLM calls.
3. **Isolated Execution & Restricted-Diagnostic Replanning**: Execute the compiled Python program in a separate credentialed runtime process. If a runtime error occurs, feed back only the prior code and sanitized, schema-level error diagnostics—never retrieved website content or stored resource values—for up to `3` replanning retries.

Across `581` validated tasks on **WebArena Verified** (`154` GitLab, `171` Shopping, `150` Shopping Admin, `106` Postmill) evaluated over three frontier models (`Claude Sonnet-4.6`, `Gemini-3.5-Flash`, `GPT-5.6-Luna`), Baya achieves a **`77.8%` 3-model average task success rate** (reaching **`81.9%`** with `Claude Sonnet-4.6`, `476/581`), outperforming `ReAct_web + API` (`66.7%`, `+11.1` percentage points) and `ReAct_web` (`55.1%`, `+22.7` pp), and beating UCM on GitLab (`92.9%` vs. `75.3%`, `+17.6` pp) at `82.6%` lower dollar cost (`$0.70` vs. `$4.01`) and `30.3%` lower latency (`327.15 s` vs. `469.04 s`). On **WASP**, Baya achieves **`0.0%` intermediate ASR and `0.0%` end-to-end ASR** (`0/84` attacks across all models and sites).

---

## Step-by-Step Procedure

### Phase 1: Construct the Trusted Website API Contract

Before exposing any target website to the compiler agent, encapsulate its supported operations $\mathcal{A} = \{f_1, \dots, f_n\}$ behind a machine-readable contract $\mathcal{C}(f) = (\Sigma, \mathcal{P}, \mathcal{Q}, \mathcal{E})$:

1. **Define Strongly Typed Signatures ($\Sigma$)**:
   - Specify every operation's input parameters and return values using strongly typed records (such as Python dataclasses) with primitive types, structural constraints, and field-level docstrings.
   - Canonicalize backend query dialect quirks inside the wrapper so the compiler faces a predictable interface. For example, Magento REST APIs encode boolean logic via indexed query parameters (`searchCriteria[filterGroups][0][filters][0][conditionType]`), where filters sharing a `filterGroups` index evaluate as logical `OR` and filters across distinct indices evaluate as logical `AND`. Expose these semantics explicitly in the typed parameter contract rather than requiring raw query-string assembly.

2. **Encode Explicit Preconditions ($\mathcal{P}$)**:
   - Document and validate required authentication tokens or session cookies, identifier formats (such as numeric project ID vs. URL-encoded namespace string), and mandatory prerequisite lookups (for instance, inspecting a configurable product's size and color option IDs before calling an add-to-cart endpoint).

3. **Classify Postconditions & Side Effects ($\mathcal{Q}$)**:
   - Partition every operation in $\mathcal{A}$ into **idempotent reads** (fetching, listing, searching, or paginating resources) versus **stateful mutations** (creating, updating, deleting, voting, or submitting orders).

4. **Map the Structured Error Domain ($\mathcal{E}$)**:
   - Enumerate structured failure modes—HTTP status failures, missing required fields, invalid filter keys, or empty lookup results—and map them to typed exceptions whose diagnostic strings contain only schema-level metadata (status code, parameter name, or result count) and never echo untrusted website payloads.

5. **Bridge UI-Only Capabilities with Trusted Playwright Wrappers**:
   - Where official REST coverage is incomplete—such as Postmill on WebArena, which exposes only `16` REST endpoints covering `33%` of tasks, GitLab personal RSS token generation, Shopping Admin dashboard-only search-term and best-seller tables, or storefront fuzzy search—implement deterministic, headless Playwright browser routines behind the exact same typed contract $\Sigma \to \mathcal{Y}$.
   - Keep CSS selectors, DOM traversal, and page navigation inside the trusted wrapper so untrusted DOM structure never reaches the compiler LLM.

---

### Phase 2: Sandboxed Compilation & Local Mock Validation

Compile the user's task instruction $u$ into an executable Python program inside a strictly isolated compilation environment:

1. **Use Progressive Schema Discovery for Large API Surfaces**:
   - Do not dump large API schemas into the compiler prompt at once (for example, GitLab exposes `1,028` REST endpoints totaling `~1.8 MB` of schema definitions).
   - Provide a compact endpoint catalog paired with site-specific execution rules and interactive search/expand tools so the compiler inspects full type definitions $\mathcal{C}(f)$ only for candidate endpoints relevant to $u$.

2. **Enforce OS Filesystem and Network Isolation During Compilation**:
   - Run the compiler agent inside an OS-level filesystem sandbox restricted to reading approved API schema definitions and reading/writing only its assigned task directory (with zero access to other task directories, credentials, or `.git` metadata).
   - Block all outbound network access to the target website and the public internet during compilation. The compiler must synthesize control flow purely from $u$ and the Trusted Website API contract.

3. **Emit Python Code Instead of Static JSON Plans**:
   - Compile tasks into a restricted Python script (allowing only Python standard-library modules, Trusted Website API calls, shared local deterministic utilities such as `fuzzy_match`, and—when strictly necessary—a constrained data-only LLM helper).
   - In ablations across all four WebArena environments (`Claude Sonnet-4.6`), compiling to Python (`Baya_Code`) achieves `82.4%` macro-average utility versus `66.9%` for structured JSON plans (`Baya_JSON`), gaining `+28.0` pp on Shopping Admin (`81.3%` vs. `53.3%`) and `+22.2` pp on Shopping (`71.3%` vs. `49.1%`) because Python natively expresses loops, pagination, aggregation, date arithmetic, and exception handling.

4. **Constrain Runtime Data-Only LLM Calls**:
   - Instruct the compiler to use deterministic Python filtering and the local `fuzzy_match` utility (`105/627` compiled programs, `16.7%`) first.
   - Allow a runtime LLM call only after deterministic candidate narrowing when subjective semantic judgment over retrieved text is unavoidable (*Safe with Influence* tasks).
   - Enforce three hard constraints on any runtime LLM helper: (a) **zero tool or API access**, (b) **strictly typed output parsing** (such as selecting an ID from a pre-fetched candidate list or returning `"none of these"`), and (c) **pre-fetched candidate bounding** so the runtime LLM can only choose among actions already authorized by the compiled control flow. Across `627` compiled WebArena programs, only `13/627` (`2.1%`) include an LLM call path in code and only `11/627` (`1.8%`) invoke it at runtime—meaning `616/627` (`98.2%`) executions never expose retrieved website content to any LLM at runtime.

5. **Mandate Companion Unit Tests with Full Mocking Before Execution**:
   - Require the compiler to generate a companion unit-test suite alongside the task script that mocks all HTTP requests, authentication tokens, and runtime LLM responses.
   - Verify that the unit tests cover: (a) HTTP status errors and pagination boundaries, (b) empty search results, (c) missing, `null`, or mistyped response fields, (d) unparseable dates or numeric strings, (e) dynamic string-to-numeric ID resolution before mutation calls, and (f) the `"none of these"` fallback branch for any runtime LLM helper.
   - Execute the unit tests inside the offline sandbox and iterate until the test suite passes before promoting the script to runtime execution.

---

### Phase 3: Isolated Execution & Restricted-Diagnostic Replanning

1. **Execute in a Separate Credentialed Subprocess**:
   - Launch a separate Python runtime process outside the compiler sandbox, inject live website credentials and session state, and execute the verified Python script against the target website.

2. **Sanitize Failure Diagnostics for Bounded Replanning**:
   - If the compiled script raises an unhandled exception or contract violation at runtime, allow up to `3` replanning retries in the compiler sandbox.
   - Pass **only** the previously generated code and **restricted error diagnostics** emitted by the Trusted Website API layer: the HTTP status code, the name of a missing required parameter (e.g., `quantity`), the name of an invalid filter field (e.g., `category`), or a result-count summary (`0` results -> `"not found"`).
   - **Never** include stored website resources, successful response payloads, request parameter values derived from live website content, or raw server error bodies in the replanning prompt. This guarantees that an adversary cannot smuggle prompt injections into the compiler via triggered runtime exceptions.

---

## When NOT to Use

- **Open-ended exploratory browsing on unknown domains**: If the agent must navigate arbitrary, previously unseen websites where no Trusted Website API contract or stable Playwright wrapper exists, offline compilation cannot pre-validate operations.
- **Tasks requiring interactive multi-turn visual discovery**: When the high-level action sequence itself genuinely depends on unanticipated visual layout changes that cannot be expressed as conditional branches over typed API responses (`Replan-Needed` tasks).
- **Sub-10-second real-time interactive loops**: Because offline compilation and unit-test verification consume a mean of `327.15 s` and `1.37M` tokens (`$0.6974`) per task for `Baya_Code` (or `82.47 s` and `201.1K` tokens for `Baya_JSON`), use pre-compiled cached scripts for recurring workflows rather than compiling from scratch on latency-critical synchronous user requests.

---

## Related Artifacts

- **Rule**: [Agent Sandbox Safety](../../rules/agent-sandbox-safety.md)
- **Rule**: [ADK Security and Evaluation](../../rules/adk-security-and-evaluation.md)
- **Research Brief**: [Task-Tampering Indirect Prompt Injection](../../research-briefs/task-tampering-indirect-prompt-injection.md)
- **Spec**: [Next.js Public Agent App Spec](../../specs/nextjs-public-agent-app.spec.md)
