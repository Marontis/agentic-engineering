---
name: description-only-injection-detection
description: >
  Detect indirect prompt injection vulnerabilities from API/tool
  descriptions alone, without executing or observing tool outputs.
  Covers description parsing, injection surface identification,
  and trust-boundary analysis.
  Derived from "No-Box Vulnerability Analysis" (arXiv:2609.10854).
---

# Description-Only Injection Detection

Use this skill when evaluating whether tools or APIs are safe to
connect to an LLM agent, based solely on their descriptions.

## When to Use

- You're adding a new tool/API to an agent's toolkit
- You can't test the tool in a sandbox before deployment
- You want to pre-screen tool descriptions for injection risk
- You're building an automated tool onboarding pipeline

## Core Insight

Most indirect prompt injection defenses focus on runtime detection
(analyzing tool outputs after execution). **Description-only
analysis** shifts detection left: by analyzing the tool's
description, parameter schema, and documented behavior, you can
identify injection surfaces *before* the tool is ever called.
Tools whose descriptions indicate they return user-generated
content, support templating, or aggregate external data are
high-risk by construction.

## Procedure

### Step 1: Parse the tool description

Extract structured information from the tool's API description:

| Field | What to Extract |
|:------|:---------------|
| **Input parameters** | Which parameters accept free-text? |
| **Output format** | Does the output contain user-generated content? |
| **Data sources** | Does the tool aggregate external/third-party data? |
| **Templating** | Does the tool support string interpolation or templates? |
| **Caching** | Does the tool return cached responses from other users? |

### Step 2: Identify injection surfaces

Score each extracted field for injection risk:

- **High risk**: Tool returns content authored by other users
  (e.g., search results, forum posts, emails, shared documents)
- **Medium risk**: Tool returns structured data that may contain
  user-authored metadata (e.g., filenames, commit messages, titles)
- **Low risk**: Tool returns only system-generated data with no
  user-authored content (e.g., timestamps, system metrics)

### Step 3: Trust-boundary analysis

Map where trust boundaries are crossed:

1. **Agent → Tool**: Is the agent sending sensitive context
   (system prompt, user data) to the tool?
2. **Tool → External**: Does the tool fetch from sources the
   agent operator doesn't control?
3. **External → Agent**: Does uncontrolled external content
   flow back into the agent's context?

If all three are true, the tool is an **injection conduit** —
external attackers can plant instructions that reach the agent.

### Step 4: Generate risk assessment

For each tool, produce a risk card:

```
Tool: web_search
Injection Surface: HIGH
  - Returns user-generated content (web pages)
  - Content flows directly into agent context
  - No sanitization described in API docs
Trust Boundary Crossings: 3/3
Recommendation: REQUIRE output sanitization before
  injecting results into agent context
```

### Step 5: Prescribe mitigations

Based on risk level:

| Risk | Mitigation |
|:-----|:-----------|
| **High** | Mandatory output sanitization, content truncation, instruction-data separation |
| **Medium** | Output type checking, metadata-only extraction, length limits |
| **Low** | Standard monitoring, no special handling needed |

## Environment Caveats

- **Incomplete descriptions**: Many tool APIs have minimal docs.
  When the description is ambiguous, assume high risk.
- **Dynamic tools**: Tools that change behavior based on context
  (e.g., plugins, user-installed extensions) can't be fully
  assessed from static descriptions.
- **Composed tools**: When tools are chained, the injection
  surface is the union of all tools in the chain.

## Failure Modes

- **False negatives**: A tool description says "returns structured
  JSON" but the JSON values contain user-generated text.  Always
  check value origins, not just format.
- **Description drift**: Tool behavior changes but description
  doesn't update.  Re-assess periodically.
- **Over-blocking**: Rejecting all tools that touch user content
  makes the agent useless.  Use mitigations, not blanket bans.

## Cross-References

- [`covert-tool-injection-defense`](../covert-tool-injection-defense/SKILL.md) —
  Runtime defense for tool output injection; this skill provides
  the pre-deployment complement
- [`browser-agent-http-sandbox`](../browser-agent-http-sandbox/SKILL.md) —
  HTTP-layer sandboxing; description-only detection identifies
  which tools need sandboxing

## Sources

- No-Box Vulnerability Analysis: Description-only Detection of Indirect Prompt Injection (arXiv:2609.10854)
