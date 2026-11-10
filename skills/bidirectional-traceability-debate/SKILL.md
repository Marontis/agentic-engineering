---
name: bidirectional-traceability-debate
description: >
  Recover requirement-to-code trace links across full repositories by routing
  between lexical retrieval, single-pass full-repository tracing, and symmetric
  Trace/Non-Trace swap debate based on artifact evidence locality and human
  review budgets. Derived from Rethinking Requirement-to-Code Traceability
  (arXiv:2611.09162).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Bidirectional Requirement-to-Code Traceability Debate

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

> **Source**: [Rethinking Requirement-to-Code Traceability Through Single-Agent and Multi-Agent Approaches](https://arxiv.org/abs/2611.09162) — Sarthak Banerjee, Sallam Abualhaija, Domenico Bianculli, Lionel Briand (2026) | Praxis: `src:2611-09162v1`

## When to Use

- Recovering candidate trace links between natural-language requirements (use cases, `shall` statements, compliance specs, or feature tickets) and source files across a codebase.
- Change impact analysis, regulatory audit preparation, test-to-requirement coverage verification, or legacy system reverse engineering where missing a true link (false negative) is costlier than reviewing extra candidates ($F_2$-prioritized workflows).
- Replacing top-$K$ embedding RAG pipelines when requirements describe user-visible behavior at an abstract domain level while implementation is scattered across controllers, data-access objects, validators, or delegated helper classes.
- Cutting human analyst validation effort (`Pred / CAND`) below exhaustive recall-oriented sweeps without suffering the one-way recall collapse of sequential author-critic pipelines.

## Core Insight

Standard Retrieval-Augmented Generation (RAG) pipelines for requirement-to-code traceability (such as `LiSSA`) pre-filter repositories to top-$K$ embedding neighbors ($K=20$) before invoking an LLM classifier. Across three standard Java benchmarks (`eTour`, `iTrust`, `Dronology`), embedding retrieval alone imposes a hard **macro-average recall ceiling of `59.5%`** (`80.5%` on `eTour`, `53.1%` on `iTrust`, and `44.8%` on `Dronology`), permanently discarding `134/286` true links in `iTrust` and `217/393` true links in `Dronology` before reasoning begins.

Bypassing top-$K$ retrieval with full-repository context unlocks **`80.9%` macro-average recall** (`+38.6 pp` over RAG `LiSSA-5` at `42.3%`), **but** choosing between single-agent and multi-agent verification depends on two structural principles:
1. **One-way sequential refinement (`Corrector`: `Tracer -> Critic -> Author`) only prunes candidates**—raising precision (`17.8% -> 26.9%`) at the cost of **`-14.4 pp` recall (`80.9% -> 66.5%`)** because a critic examining only proposed files can never rescue true links missed in the initial pass.
2. **Symmetric opposing-mandate set swapping (`Debater`) makes both false positives and false negatives recoverable**: running a `Trace Debater` and `Non-Trace Debater` in parallel, swapping their partitions so the `Trace Debater` re-examines rejected files (`non_trace_files`) while the `Non-Trace Debater` challenges proposed files (`trace_files`), and resolving disputes via a `Judge` achieves the highest overall $F_2$ (**`50.8%`** conservative / **`49.5%`** recall-oriented vs. `46.8%` / `46.3%` single-agent `Tracer` and `41.5%` `LiSSA-5`) while shrinking human validation review sets by **`30%–50%`** relative to recall-oriented `Tracer`.

---

## Step-by-Step Procedure

### Step 1: Audit Artifact Evidence Locality to Route the Architecture

Before running repository-wide link recovery, inspect a small sample (`10–15`) of requirements and source files along three axes—**vocabulary overlap**, **identifier/comment fidelity**, and **implementation scattering**—and route to the lightest sufficient architecture:

1. **Direct Lexical Alignment + Tight Token Budget -> Top-$K$ Embedding RAG**:
   - Use embedding pre-filtering ($K \approx 20$) *only* when requirements explicitly name implementation entities, classes, or UI widgets (as in `eTour`, where `65%` [`37/57`] of requirements echo class vocabulary and embedding retrieval reaches `80.5%` recall at `4.67%` candidate review cost).
   - Do **not** use top-$K$ embedding retrieval when requirements are abstract `shall` statements or multi-step workflows scattered across architectural layers (`92%` [`97/105`] scattered in `iTrust`), where lexical similarity misses `47%–55%` of ground-truth files.

2. **Explicit Role Naming + Reliable Code Comments + Exhaustive Recall Mandate -> Single-Agent Full-Repository `Tracer` (`P2`)**:
   - When source files follow consistent architectural naming conventions (e.g., `*Action`, `*DAO`, `*Bean`, `*Loader`, `*Validator`) and carry accurate class/method documentation (e.g., `216/226` Javadoc-documented files in `iTrust`), feed the full repository into a single-pass `Tracer` under a recall-oriented prompt (`P2`).
   - Single-pass `Tracer (P2)` achieves the highest raw recall (**`80.9%` macro-avg**: `87.3%` `eTour`, `85.7%` `iTrust`, `69.7%` `Dronology`), leaving only `19.1%` of true links unrecovered when human analysts can afford to inspect `7.16%–16.96%` (`12.80%` avg) of candidate pairs.

3. **Indirect, Delegated, or Conflicting Evidence + Bounded Human Review Budget -> Symmetric Bidirectional `Debater`**:
   - Route to the 3-agent `Debater` workflow whenever:
     - Implementation behavior is distributed across indirect helper delegations, interfaces (`I*`), or cross-package message handlers where single-pass tracing misses multi-hop participants;
     - Source comments are sparse, stale, untranslated, or misleading relative to method bodies (e.g., legacy mistranslated Javadocs or generic class names like `Tourist.java` implementing multiple use cases); or
     - Engineering review bandwidth requires cutting candidate links by **`30%–50%`** compared to `Tracer (P2)` while preserving higher recall and $F_2$ than conservative single-pass tracing.

---

### Step 2: Assemble Full-Repository Evidence Context and Prompt Framing

1. **Pack Complete Repository Context Deterministic-Order**:
   - Present the target requirement $r \in \mathcal{R}$ alongside the repository source files $\mathcal{C} = \{c_1, \dots, c_m\}$ (full source when within model context window; otherwise module-grouped batches or signature + docstring + call-target views with deterministic ordering and `temperature = 0`).
   - Require every agent output to reference exact repository file paths from $\mathcal{C}$ and cite concrete code evidence (method bodies, field reads/writes, DAO queries, event dispatches, or interface implementations) rather than file names alone.

2. **Select Conservative (`P1`) vs. Recall-Oriented (`P2`) Task Framing Explicitly**:
   - **Conservative (`P1`)**: Instruct agents to link a file *only* when code directly implements core behaviors of $r$. Use when analyst review budgets are strictly capped (`3.02%–6.79%` of candidate pairs under `Debater P1`, macro $F_2 = 50.8\%$, $P = 35.8\%$, $R = 60.2\%$).
   - **Recall-Oriented (`P2`)**: Instruct agents to include both direct implementations and supporting/participating structural dependencies (beans, loaders, validators, shared state handlers) so peripheral true links are surfaced (`Debater P2`: macro $R = 71.0\%$, $F_2 = 49.5\%$).

---

### Step 3: Execute Symmetric Bidirectional Debate (`Debater`, 1 Swap Cycle)

Never wire multi-agent traceability as a one-way `Tracer -> Critic -> Author` chain (`Corrector`), which structurally starves the critic of visibility into unchosen files. Instead, execute **three stages with one symmetric swap cycle**:

1. **Stage A — Parallel Opposing-Mandate Partitioning**:
   - **`Trace Debater` (Inclusion Mandate)**: Scans $(r, \mathcal{C})$ to identify all candidate `trace_files` $T_0 \subseteq \mathcal{C}$ with per-file implementation rationales, placing remaining files in `non_trace_files` $N_0 = \mathcal{C} \setminus T_0$.
   - **`Non-Trace Debater` (Exclusion Mandate)**: Independently scans $(r, \mathcal{C})$ under the opposing mandate—identifying files `non_trace_files` $N'_0 \subseteq \mathcal{C}$ whose responsibilities are unrelated, purely infrastructural, or belong to sibling features, and recording `trace_files` $T'_0 = \mathcal{C} \setminus N'_0$ with exclusion/inclusion justifications.

2. **Stage B — Cross-Partition Set Swap & Rebuttal (1 Cycle)**:
   - Swap the two agents' outputs so **both false negatives and false positives are contested**:
     - The **`Trace Debater`** inspects the `Non-Trace Debater`'s `non_trace_files` ($N'_0$) to **rescue false negatives**—arguing with concrete call-chain, state-mutation, or data-model evidence whenever a delegated helper, validator, or DAO was prematurely excluded.
     - The **`Non-Trace Debater`** inspects the `Trace Debater`'s `trace_files` ($T_0$) to **prune false positives**—challenging superficial keyword matches, boilerplate utilities, or misleading comments that do not actually execute $r$'s behavior.
   - Cap deliberation at **one swap cycle** ($N_{\text{cycles}} = 1$) to bound multi-agent token amplification and prevent over-pruning consensus drift.

3. **Stage C — Evidence-Weighing `Judge` Resolution**:
   - Pass the requirement $r$, the initial partitions, and both rebuttal transcripts to a neutral **`Judge`** agent.
   - Instruct the `Judge` to evaluate **code-body behavior over comment claims** when evidence conflicts (e.g., retaining a file whose method body implements $r$ despite a stale/mistranslated header comment, and rejecting a file whose comment mentions $r$'s domain noun while its methods implement a different workflow) and emit the final verified trace set $\hat{T}(r) \subseteq \mathcal{C}$ with short audit rationales for human review.

---

### Step 4: Pre-Screen Underspecified System-Wide Constraints

Before or immediately after running automated recovery, flag **underspecified cross-cutting requirements**—e.g., generic architectural or serialization rules such as *"All message data shall be serializable"* or *"All timestamps shall use UTC"* (which constituted `7%` [`4/57`] of `Dronology` requirements, such as `RE77` linking to `76/184` files where single-pass `Tracer P1` found `2` true positives and missed `74` false negatives).
- Route system-wide invariants to deterministic AST/type-hierarchy queries (e.g., finding all classes implementing `Serializable` or importing message schemas; see [`cost-effective-repo-exploration`](../cost-effective-repo-exploration/SKILL.md)) rather than relying on semantic requirement-to-file reasoning.

---

## Failure Modes & Guardrails

| Failure Mode | Mechanism Observed (`arXiv:2611.09162`) | Guardrail |
|:-------------|:----------------------------------------|:----------|
| **Embedding Retrieval Truncation** | Top-20 cosine similarity drops `46.9%` of true links on `iTrust` and `55.2%` on `Dronology` when requirements omit class identifiers. | Bypass top-$K$ embedding pre-filtering whenever repository source or structural summaries fit in context. |
| **One-Way Critic Recall Collapse (`Corrector`)** | A critic reviewing only `Tracer`'s proposed links cannot inspect $\mathcal{C} \setminus T_0$, dropping macro recall from `80.9%` to `66.5%` (`-14.4 pp`). | Always pair FP critique with symmetric FN rescue over `non_trace_files` (`Debater`). |
| **Comment-Body Contradictions** | Legacy or machine-translated comments (`eTour`) mislead conservative single-pass agents into rejecting true implementations or accepting unrelated classes. | Instruct the `Judge` to prioritize executable method bodies, field accesses, and call targets over comments. |
| **Over-Pruning on Sparse/Implicit Codebases** | On `Dronology` (only `92/184` files have class comments, `30` `I*` interfaces), `Debater (P2)` cuts human review by `50%` (`1,499 -> 752`) at `-19.3 pp` recall (`69.7% -> 50.4%`). | Use single-pass `Tracer (P2)` when comments are sparse and missing any link is unacceptable; use `Debater` when review budgets are constrained. |
| **Repository Context Window Overflow** | Very large monorepos exceed single-call context windows even at `128K–1M` tokens. | Partition the repository into cohesive package/subsystem slices (via [`agentic-requirements-reverse-engineering`](../agentic-requirements-reverse-engineering/SKILL.md)), run `Debater` per slice, and merge `Judge`-approved links. |

## Related Artifacts

- [`agentic-requirements-reverse-engineering`](../agentic-requirements-reverse-engineering/SKILL.md) — Extracting structured requirement hierarchies from legacy codebases when explicit requirement specifications do not yet exist.
- [`requirements-driven-code-generation`](../requirements-driven-code-generation/SKILL.md) — Forward-direction specification decomposition and contract-bound test synthesis prior to writing code.
- [`cost-effective-repo-exploration`](../cost-effective-repo-exploration/SKILL.md) — Escalation-oriented AST and grep exploration for large repositories exceeding single-window budgets.
- [`debate-consensus-memory-calibration`](../debate-consensus-memory-calibration/SKILL.md) — Preventing shared-misconception convergence in multi-agent deliberation.
- Rule companion: [multi-agent-coordination.md](../../rules/multi-agent-coordination.md)
