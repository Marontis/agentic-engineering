# Safety-Bounded SDC-to-MCP Gateway for Medical AI Agents

> **Source**: Gerlach & Fischer, arXiv:2609.31358, Sep 2026
> **Status**: Research Brief — domain integration architecture with deterministic and five-model evaluation
> **Praxis source**: src:2609-31358v1

## Why Not a Skill?

The contribution is an IEEE 11073 SDC–specific integration (medical device state to MCP) evaluated in simulation and one cross-stack loopback path. The reusable idea, exposing state as read-only resources and actions only as bound, non-executing dry-run proposals, is a design pattern that already fits under existing authorization and plan-validation skills. It is not a new general procedure.

## Core Concept

When an agent is connected to systems with physical effects (here ventilators and patient monitors), the gateway, not the model, should fix what the agent can see and what it can cause. The gateway:

- Projects device state into **read-only MCP resources** (`sdc://devices`, `/metrics`, `/alarms`, `/context`, a raw trace view, and the mapping document), with each value labelled mapped / unmapped / unsupported / conflicting via a versioned semantic mapping (SDC-MIE) that makes codes, handles, units, provenance, and policy explicit.
- Exposes only **allowlisted action affordances as dry-run tools**. These check schema, range, target, freshness, and policy, then enter a non-executing lifecycle (proposed → policy_validated → pending_approval → approved/denied/expired). Each proposal binds device, operation, parameters, policy version, MDIB version, freshness, canonical snapshot hash, proposer, and expiry. Approval re-runs policy and current-state checks, and changed, stale, or expired state cannot be overridden. Even `approved` carries `executed=false`.
- Enforces the no-execution invariant at independent layers: config loading rejects write-enabled modes, the consumer contract only allows discovery and snapshot reads, tool result models require dry-run semantics, and tests wrap the adapter with a Set/Activate attempt counter.

## Key Findings

- **No-execution invariant held in every controlled test**: all 14 ordered-event fault cases (unavailable, invalid, stale, delayed, reordered, recovered state) produced expected outcomes; a proposal bound to MDIB version 1 was rejected once version 2 was current; 7/7 tool-policy cases (3 accepted as dry runs, 4 rejected) and 7/7 authorization-lifecycle cases matched, with the zero-operation counter preserved throughout.
- **Five hosted models passed 414/420 (98.6%)** of agent-interpretation cases on enriched resources (Gemini 2.5 Flash, hosted Gemma 4 26B, and hosted Qwen 3.6 27B 84/84; GPT-4.1 mini and GPT-OSS 20B 81/84). No model invented a resource URI or produced a graded unsafe recommendation, boundary bypass, false-negative alarm, or freshness/validity error in that condition. The deterministic baseline passed 28/28 without a model.
- **Representation ablation (GPT-4.1 mini)**: raw normalized snapshot 63/84, generic MCP 75/84, enriched MCP 81/84. The raw arm **invented 15 resource URIs** when no catalogue was exposed. Enrichment's six gains were all canonical-identifier compliance (e.g. `heart_rate` vs "High Heart Rate"), not better alarm recognition, and cost +45.2% serialized context (about 3.24 kB to 4.71 kB).
- **Cross-field inconsistency survives**: GPT-OSS said in prose that no alarm was active but set `active_alarm=true` in all three repetitions. Repeated consistency is not correctness.

Limits (stated): no physical devices or clinical network; the SDCri reference provider's generic codes mapped 0/11; EPR allowlisting is not authentication; stdio transport only; synthetic identities in the approval workflow.

## Relevance to Praxis

- A concrete instance of "the LLM stays outside the trusted boundary": the reachable effect set is fixed by deterministic gateway logic, consistent with `rules/agent-sandbox-safety.md` "DON'T: Rely on structured LLM authorization decisions as the sole safety gate".
- The proposal record's binding to state version plus snapshot hash, with re-validation at approval, is the same idea as lineage-scoped validation in [`dependency-scoped-plan-validation`](../skills/dependency-scoped-plan-validation/SKILL.md) and pre-dispatch checks in [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md).
- Exposing an explicit resource catalogue removed URI invention, which supports the closed-world resolution argument in [`closed-world-tool-hallucination`](closed-world-tool-hallucination.md).
- For per-caller visibility and invocation checks on the MCP side, see [`mcp-zero-trust-tool-authorization`](../skills/mcp-zero-trust-tool-authorization/SKILL.md).

> Source: Gerlach & Fischer, "A Safety-Bounded SDC-to-MCP Gateway for Medical AI Agents" (arXiv:2609.31358)
