# When Tool Calls Succeed but Workflows Fail: Anomalies at the Agent-Tool Boundary

> **Paper**: [When Tool Calls Succeed but Workflows Fail: Anomalies at the Agent-Tool Boundary](https://arxiv.org/abs/2609.15397)  
> **Praxis source**: `src:2609-15397v1`

## Why Not a Skill?

This paper introduces a formal effect-history model, an empirical survey of 98,291 Model Context Protocol (MCP) tools, and a catalog of external-effect failure modes rather than a single transferable operational procedure. It serves as a foundational architectural reference for designing transactional tool boundaries, compensating actions, and agent runtime contracts.

---

## Core Concept

AI agents executing multi-step workflows frequently externalize state changes through independently supplied tools (e.g. database updates, API requests, cloud provisioning, emails). When workflows encounter retries, speculative branches, concurrency, or partial failures, the state of the external world frequently diverges from the agent runtime's internal session history.

The authors construct an **effect-history model** that formally decouples events occurring in the external world from the runtime's observation of those events. Through this model, they analyze **98,291 tools exposed across registered Model Context Protocol (MCP) servers**, revealing that current tool interfaces expose only coarse, call-level metadata (names, descriptions, parameter schemas) while providing zero primitives for transactional consistency, effect verification, or idempotency.

```
Agent Workflow Execution
       │
       ├── Call 1: provision_database() ──► External World: DB created (ID: db-101)
       │
       ├── Call 2: write_configuration() ──► Error: Timeout / Transient Crash
       │
       ▼ (Agent Retries Call 1 & 2)
       ├── Retry Call 1: provision_database() ──► Anomaly: Duplicate DB created! (db-102)
       │
       ▼ (Workflow Aborts on Failure)
       └── Final State: Workflow marked FAILED, but orphaned external DBs survive & bill!
```

---

## Catalog of 8 External-Effect Boundary Anomalies

The paper catalogs eight recurring structural anomalies that occur at the agent-tool boundary:

| Anomaly | Description | Real-World Impact |
|:---|:---|:---|
| **1. Missing Required Effect** | Tool execution returns `status: 200 OK`, but the external state mutation never materialized. | Downstream nodes crash expecting records that do not exist. |
| **2. Duplicated External Effect** | Automatic runtime retry or speculative execution executes a non-idempotent tool twice. | Duplicate financial charges, duplicate orders, or duplicate VM instances. |
| **3. Surviving Aborted Effect** | Workflow aborts or rolls back an uncommitted branch, but external mutations made by completed tool calls persist. | Orphaned cloud resources, un-reverted database records, leaked draft emails. |
| **4. Committed Effect on Provisional State** | A permanent tool action commits state based on intermediate data from an unverified speculative branch that is later revoked. | Irreversible corruption of external production records. |
| **5. Ghost Read Anomaly** | Agent reads external state that was modified by another concurrent process, acting on stale or invalid assumptions. | Race conditions in multi-agent shared environments. |
| **6. Non-Compensable Blind Commit** | Agent executes an irreversible action without first verifying that a compensating (undo) action exists. | Inability to roll back partial failures in multi-step transactions. |
| **7. Partial Batch Divergence** | A tool handling multi-item operations fails midway without atomicity, leaving the external system in a half-applied state. | Inconsistent inventory or fractured database tables. |
| **8. Out-of-Order Linearization** | Concurrent tool calls complete and serialize in external systems in an order different from the agent's causal reasoning trace. | Sequence inversion errors in state machines. |

---

## Empirical Findings: The MCP Tooling Audit

- **Audit Scale**: 98,291 tools across registered Model Context Protocol (MCP) servers were analyzed against transactional annotation vocabularies.
- **Surface-Level Metadata Only**: While standard OpenAPI fields (name, description, schema) are widely present, **0% of surveyed MCP tools** exposed formal idempotency guarantees, compensation pointers, or staging/provisional semantics.
- **Black-Box Limitations**: The authors prove four mathematical boundary points where black-box tool invocation *cannot* provide consistency guarantees without explicit cooperation from the tool runtime (e.g. idempotency tokens and transactional staging).

---

## Relevance to Praxis & Agent Architecture

- **Rules Contribution to Tool & Sandbox Design**:
  - **DO enforce idempotency keys** on all external side-effecting tool calls (`idempotency_key = hash(session_id, node_name, turn_index)`).
  - **DO pair every mutating tool with an explicit compensating transaction** (undo function) before permitting execution in speculative or multi-step workflows.
  - **DO implement two-phase staging for external effects**: Tools must stage changes in provisional buffers and commit only when the workflow reaches an authoritative terminal state.
- **Connection to ADK Architecture**: Explains why Google ADK 2 employs `LongRunningFunctionTool` with explicit receipt tokens and why human decision gates must be decoupled from volatile process memory.
