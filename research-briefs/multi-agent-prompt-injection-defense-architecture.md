# Prompt Injection Threat Model and Defense Architecture for Multi-Agent Systems

> **Source**: Paul & Nandy, arXiv:2609.22949, Sep 2026
> **Status**: Research Brief — threat taxonomy plus a four-layer defense evaluated on one 6-agent pipeline with a fixed payload set

## Why Not a Skill?

The four defense layers (message signing, boundary sanitization, privilege-scoped tools, communication anomaly detection) are each already covered in more detail by existing skills and rules (see Relevance). The paper's new contribution is the multi-agent threat taxonomy and a per-category measurement showing which layer stops which vector. The evaluation uses a fixed, non-adaptive payload set, so it supports a rule about *which* layer to place where, not a new procedure.

## Core Concept

Single-model prompt-injection threat models miss the surfaces that only exist when agents talk to each other. The paper lists 14 vectors in 4 categories:

- **Direct (D1–D3)**: instruction override, role impersonation, task hijacking.
- **Indirect via tool outputs (I1–I4)**: document poisoning, API response injection, schema-drift exploitation, tool-metadata poisoning.
- **Inter-agent message passing (M1–M4)**: response poisoning by a compromised agent, context-window pollution (verbose output pushing the system prompt out), format mimicry of system messages, delegation-chain manipulation.
- **Cascading via the orchestrator (C1–C3)**: routing manipulation, result-aggregation poisoning, termination suppression.

The defense sits below the prompt layer, since "system-prompt guardrails fail because they operate at the layer attackers manipulate":

1. **Signed messages with provenance**: Ed25519 signature plus origin agent, generating task and prior contributors on every inter-agent message; unsigned messages are quarantined.
2. **Boundary sanitizers** at every agent interface: schema validation, a lightweight data-vs-directive classifier, and content-length limits.
3. **Privilege-scoped tool tokens** enforced at an API gateway as immutable config, not prompt text.
4. **Communication anomaly detection**: a read-only monitor models expected inter-agent traffic as a directed graph and flags unexpected recipients, volumes or protocol violations.

## Key Findings

Setup: 6-agent financial document pipeline (orchestrator, retrieval, code, analysis, compliance, output) on GPT-4o, Claude 3.5 Sonnet and Llama 3 70B-Instruct; 50 payloads per vector; the **highest** success rate across the three backends is reported.

- **Baseline (system-prompt guardrails only)**: attack success 19% direct, 43% indirect, 31% inter-agent, 28% cascading; 31.2% aggregate. 4 of 6 agents were vulnerable to at least one scope violation; the orchestrator was the target in 8 of 14 vectors.
- **Each layer mainly fixes its own category**: signing cut inter-agent injection from 31% to 2.8% but left indirect injection at 43%; sanitization cut indirect injection from 43% to 9.5% but left inter-agent at 31%; anomaly detection cut cascading from 28% to 4.5%; privilege scoping blocked all privilege-escalation attempts.
- **Combined**: 3.8% / 4.6% / 1.2% / 3.4% by category, 4.2% aggregate (an 86.5% reduction).
- **Overhead**: 3 ms per signature, 12 ms per sanitized transition, zero for privilege scoping, asynchronous anomaly detection; 225 ms total on a 15-message workflow, 4.7% over a 4.8 s baseline. The instruction classifier's false-positive rate was 2.3%.
- **Residual attacks**: unseen direct payloads that slip past the classifier, and adaptive indirect attacks in non-flagged formats. The authors note that adaptive strategies in prior work exceed 85% success against defenses, and that their fixed payload set may understate risk.

## Relevance to Praxis

- Supports [`agent-sandbox-safety`](../rules/agent-sandbox-safety.md) "DO: Select defense layers from different cost classes" and "DON'T: Let agents self-declare their identity": the per-category table shows the layers are complementary, not redundant. Proposed rule for [`multi-agent-coordination`](../rules/multi-agent-coordination.md): sign and provenance-tag inter-agent messages, because boundary sanitization alone leaves inter-agent injection untouched.
- **M14**: this is a static, fixed-payload result. The 4.2% residual must not be quoted as a robustness guarantee without adaptive red-teaming ([`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md), [`self-improving-red-team`](../skills/self-improving-red-team/SKILL.md)).
- **M6**: the paper reports per-layer false positives (2.3%) and latency but no end-to-end false-refusal figure for the stacked system.
- Implementation detail for the layers lives in [`nlip-agent-message-envelope`](../skills/nlip-agent-message-envelope/SKILL.md) (envelopes), [`tainted-message-clean-room-recovery`](../skills/tainted-message-clean-room-recovery/SKILL.md) (recovering from tainted messages), [`mcp-tool-hijacking-defense`](../skills/mcp-tool-hijacking-defense/SKILL.md) (tool metadata poisoning), [`unified-capability-gateway`](../skills/unified-capability-gateway/SKILL.md) (gateway-enforced scope), and [`layered-defense-ensemble`](../skills/layered-defense-ensemble/SKILL.md) (measuring layer correlation).

> Source: Paul & Nandy, "Beyond Single-Model Injection: A Threat Model and Defense Architecture for Prompt Injection in Multi-Agent Systems" (arXiv:2609.22949)
