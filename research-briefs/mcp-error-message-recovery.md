# MCP Error Messages and Agent Recovery

> **Paper**: [MCP Error Messages Written for Developers Hurt the Most Capable Agents Most](https://arxiv.org/abs/2609.35381)
> **Praxis source**: src:2609-35381v1

## Why Not a Skill?

The findings reduce to a short set of authoring guidelines for tool error
text, which belong in the existing
[`mcp-server-design`](../skills/mcp-server-design/SKILL.md) skill (a section
was added there). This brief holds the evidence.

---

## Core Concept

MCP servers wrap APIs whose error messages were written for human
developers: "run this command", "edit your config", "visit this page". An
agent that can only call MCP tools can't do any of that. The next-step
sentence in an error is effectively an instruction to the agent, and newer
models follow instructions in tool output more literally.

### Key Findings

- **Survey** (150 most-starred MCP servers, 3,001 error messages): 949
  tell the caller what to do next, and 477 of those steps depend on the
  caller's capabilities, which the server can't see. On credential,
  permission and rate-limit errors, 99 of 128 steps depend on the caller.
- **Experiment**: 168 BFCL multi-turn scenarios (24 per failure type, 7
  types), five OpenAI models, 3 runs each, 15,120 trials; success is a
  BFCL state check.
- **Expired credentials, mean recovery**: 45% when the error asks for a
  terminal command; 82% with only the cause; 84% when the server's login
  tool is named; 82% when an LLM filter removes the step. GPT-6 Astra fell
  from 75% (cause only) to 6% (terminal command).
- **Rate limits**: "wait before retrying" 6%; naming the call to repeat
  88%.
- **Missing permission**: 0% with a generic notice or cause only; 28% and
  53% with the two correct-step phrasings.
- **Malformed calls** (wrong unit, missing field, wrong tool) and missing
  resources: recovery stayed within a few points across all variants;
  models fix these from the cause alone.
- **Filter**: a one-instruction LLM pass that deletes next-step sentences
  and keeps the cause processed the 764 survey messages for US$0.09.
- **Limitations**: injected failures at fixed points; one provider's
  models; agents assumed limited to tool calls (results may differ for
  agents with a terminal or browser); exact-state success only.

## Relevance to Praxis

- **For server authors**: in error text, name the server's own tool that
  fixes the problem ("call ticket_login first"), and for rate limits name
  the call to repeat. Do not ask the caller to run commands, edit config
  or visit pages.
- **For agent builders**: when consuming third-party MCP servers, filter
  caller-dependent next steps out of error text before the model sees it.
  Keep the cause. This also narrows a channel through which tool output
  steers the agent (`rules/agent-sandbox-safety.md` "Sanitize all tool
  outputs before injecting into agent context").
- **Capability is not robustness here**: the most instruction-following
  model degraded most, so re-test recovery when upgrading models.

> Source: MCP Error Messages Written for Developers Hurt the Most Capable Agents Most (arXiv:2609.35381)
