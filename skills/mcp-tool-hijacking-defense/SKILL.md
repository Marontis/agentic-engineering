---
name: mcp-tool-hijacking-defense
description: >
  Defend MCP-connected agents against semantic supply-chain hijacking
  where attacker-controlled tool metadata and outputs steer agent
  behavior. Covers the two-stage A2M attack model (Attraction →
  Manipulation), metadata vetting, trace-aware output sanitization,
  and runtime isolation.
  Derived from "A2M: Trace-Optimized Agent Hijacking in the MCP
  Ecosystem" (arXiv:2609.26761).
source: https://arxiv.org/abs/2609.26761
---

# MCP Tool Hijacking Defense (A2M)

Use this skill when building or auditing agent systems that connect to
third-party MCP tool servers, and you need to defend against semantic
supply-chain attacks through metadata manipulation and adversarial
tool outputs.

## When to Use

- Agent connects to one or more third-party MCP tool servers
- Tool selection relies on semantic matching against tool descriptions
- Tool outputs are injected back into agent context for further
  reasoning
- You need to assess or harden against tool-level supply-chain risk

## Core Insight

MCP agents select tools via semantic matching against server-provided
metadata, creating a **semantic supply-chain risk**. A2M demonstrates
a two-stage black-box attack: the **Attraction phase** optimizes tool
metadata (name, description) to increase invocation probability; the
**Manipulation phase** uses execution traces to refine adversarial
tool returns that steer agents toward attacker-desired outcomes.

**Evidence**: On LiveMCPBench, direct attacks achieve 93.6%
macro-average malicious tool invocation rate, 32.4× token cost
amplification (Cognitive DoS), and 74.4% mean attack success across
information exfiltration, environment integrity compromise, and
reasoning derailment. Attacks transfer cross-model at 63.6%
invocation rate without re-optimization.

---

## Procedure

### 1. Understand the Attack Surface

The attack has two distinct phases:

**Attraction Phase** (metadata poisoning):
1. Attacker registers a malicious MCP tool server
2. Tool metadata (name, description, parameter schemas) is optimized
   to maximize semantic similarity with legitimate tool queries
3. The agent's tool selection mechanism preferentially invokes the
   attacker's tool over legitimate alternatives
4. No prompt injection required — the attack operates through the
   tool registry itself

**Manipulation Phase** (output poisoning):
1. Once invoked, the malicious tool returns adversarial outputs
2. Outputs are refined using execution traces from prior invocations
3. Four attack scenarios: Information Exfiltration, Cognitive Denial
   of Service, Environment Integrity Compromise, Reasoning Derailment
4. Adversarial returns are designed to steer the agent's subsequent
   reasoning toward attacker-desired outcomes

### 2. Implement Metadata Vetting

Before allowing any MCP tool into the agent's registry:

1. **Pin tool descriptors**: Store a cryptographic hash of each
   tool's metadata (name, description, parameter schema) at
   registration time
2. **Detect metadata drift**: Re-hash on each connection and reject
   tools whose metadata has changed without explicit re-approval
3. **Semantic similarity screening**: Flag tools whose descriptions
   are suspiciously similar to existing legitimate tools — this is the
   Attraction phase's primary vector
4. **Namespace isolation**: Prevent tool name collisions across
   different MCP servers; reject shadowing attempts

### 3. Implement Runtime Output Isolation

After tool invocation, before injecting output into agent context:

1. **Output type enforcement**: Validate that tool outputs conform to
   the declared return schema; reject unexpected fields
2. **Content boundary marking**: Wrap tool outputs in clear delimiters
   that the agent's system prompt treats as untrusted data
3. **Output size limits**: Cap return payload size to prevent
   Cognitive DoS (32.4× token cost amplification observed)
4. **Instruction detection**: Scan tool outputs for embedded
   instructions, role-play prompts, or context-switching patterns
   before injection

### 4. Implement Trace-Aware Monitoring

The Manipulation phase uses execution traces to refine attacks:

1. **Do NOT expose full execution traces** to tool servers — this
   provides the signal for trace-optimized manipulation
2. **Minimize information in error messages** returned to tools
3. **Monitor tool invocation patterns**: Flag tools that are
   consistently selected over established alternatives
4. **Track output influence**: Measure whether a tool's output causes
   disproportionate changes in agent reasoning direction

### 5. Implement Selection Hardening

1. **Prefer registered-first tools**: When multiple tools match a
   query, prefer tools with longer registration history
2. **Diversity penalty**: If a new tool's description is >90% similar
   to an existing tool's, require explicit human approval
3. **Invocation frequency monitoring**: Alert when a recently
   registered tool captures >50% of invocations in a category
4. **Cross-model consistency**: If the same tool produces different
   selection patterns across models, investigate

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Metadata optimization bypasses screening | Attacker iteratively refines descriptions | Semantic similarity screening + registration age preference |
| Cross-model transfer | Attack transfers at 63.6% without re-optimization | Model-agnostic defenses (output isolation, metadata pinning) |
| Cognitive DoS via token amplification | 32.4× cost increase from verbose adversarial returns | Output size limits per tool invocation |
| Trace-optimized manipulation | Attacker uses execution traces to refine outputs | Minimize trace exposure to tool servers |
| Legitimate tool displacement | Screening blocks useful new tools | Human approval path for high-similarity tools |

> Source: Li et al., "A2M: Trace-Optimized Agent Hijacking in the
> MCP Ecosystem" (arXiv:2609.26761), Sep 2026.
