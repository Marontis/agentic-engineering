---
name: covert-tool-injection-defense
description: >
  How to defend against covert indirect prompt injection through tool
  outputs.  Covers output sanitization, return-anchor detection,
  user-framing separation, and runtime alignment checks.
  Derived from "Will the User Ever Know?" (arXiv:2608.30362).
---

# Covert Tool Injection Defense

Use this skill when building tool-augmented agents that consume
external data (search results, API responses, web content) and you
need to prevent injected instructions from hijacking agent behavior
without the user noticing.

## When to Use

- Your agent calls external tools (web search, APIs, file reads)
  and incorporates their output into its reasoning
- You're building a defense layer for a ReAct-style agent loop
- You need to distinguish between covert attacks (user doesn't notice)
  and overt attacks (user would notice the deviation)

## Core Insight

Traditional prompt injection research focuses on whether the attack
*succeeds* (the agent does the wrong thing).  This misses a critical
dimension: **covertness**.  An attack is covert when the agent
completes the malicious action AND returns a plausible-looking
response to the user, so the user never realizes anything went wrong.

The ICoA (Indirect Covert Attack) framework achieves covert success
through two mechanisms:
1. **User framing**: The injected payload frames itself as coming
   from the user's perspective, making the agent treat it as a
   legitimate request
2. **RETURN anchor**: A directive that forces the agent to produce
   a normal-looking response after executing the malicious action,
   hiding the attack from the user

**Evidence**: Existing defenses (detection, prompting, runtime
alignment) fail against covert attacks — detection catches overt
attacks but misses covert ones because the agent's visible behavior
appears normal.

## Procedure

### Step 1: Separate tool output from agent context

Never inject raw tool output directly into the agent's reasoning
context.  Instead:

1. **Quarantine zone**: Tool outputs go into a marked section of the
   prompt that the agent is instructed to treat as untrusted data
2. **Role separation**: Tool outputs should never appear in the
   "user" role — they should be in a distinct "tool_result" role
   that the model treats differently
3. **Escaping**: Strip or escape any instruction-like patterns from
   tool outputs before injection

### Step 2: Detect return anchors

A return anchor is any instruction in tool output that directs the
agent to produce a specific response to the user.  Scan for:

- Directives like "respond to the user with...", "tell the user...",
  "return the following..."
- Instructions that reference the user's original query and provide
  a scripted answer
- Any content that attempts to set the agent's final response

These are almost never legitimate in tool output.

### Step 3: Detect user-framing attacks

Watch for tool output that impersonates the user's voice:

- First-person instructions ("I want you to...", "Please also...")
- References to the user's original query reformulated as a new request
- Content that blurs the boundary between "what the tool returned"
  and "what the user asked"

### Step 4: Runtime action-text alignment

After the agent decides on an action but before executing it:

1. Compare the agent's stated reasoning with its actual tool calls
2. Flag divergences where the agent says "I'm searching for X" but
   the tool call does Y
3. Check whether the action sequence deviates from the user's
   original intent

### Step 5: Post-execution audit

After the agent produces its final response:

- Verify that every claim in the response traces to a tool result
  or the user's query
- Check whether the agent performed any tool calls not explained
  in its reasoning chain
- Flag responses where the agent's visible output looks normal but
  its tool-call log shows unexpected actions

## Environment Caveats

- **API-only models**: If you can't inspect the agent's internal
  reasoning (chain-of-thought), focus on tool-call auditing and
  output sanitization.  You can still detect covert attacks from
  the action log.
- **Multi-tool agents**: The attack surface scales with the number
  of tools.  Each tool output is a potential injection vector.
  Prioritize sanitization for tools that return user-generated
  content (search, web scraping, email).
- **Streaming responses**: If the agent streams its response to
  the user while still executing tools, a covert attack may
  complete before the audit catches it.  Consider buffering
  the response until execution is complete.

## Failure Modes

- **Sanitization bypasses**: Simple regex-based sanitization can
  be evaded with encoding tricks, unicode substitutions, or
  split-instruction patterns.  Use semantic detection, not just
  pattern matching.
- **Over-sanitization**: Aggressively stripping content from tool
  outputs can break legitimate functionality.  Calibrate the
  sanitization to flag suspicious patterns for review rather than
  silently removing content.
- **Detection-only defense**: Detecting an injection after the
  fact doesn't help the user if the malicious action already
  executed.  The defense must be preventive (quarantine + action
  alignment), not just detective.

## Cross-References

- [`browser-agent-http-sandbox`](../browser-agent-http-sandbox/SKILL.md) —
  HTTP-layer interception catches network-based injection attempts
  that this skill handles at the content layer
- [`layered-defense-ensemble`](../layered-defense-ensemble/SKILL.md) —
  Tool injection defense is one layer; combine with others but
  remember defense layers correlate

## Sources

- Will the User Ever Know? Covert Indirect Prompt Injection Attacks on Tool-Using LLM Agents (arXiv:2608.30362)
