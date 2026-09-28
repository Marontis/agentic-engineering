# Progressive Skill Discovery as Access Control (Skilder)

> **Source**: Stettler, Girardet, Canton et al., arXiv:2609.28693, Sep 2026
> **Status**: Research Brief — product architecture with a 13-scenario harness (simulated authorization layer)

## Why Not a Skill?

The procedure (role catalog, learn a role, call tools only through the server) is one vendor's MCP server design, evaluated against a simulated authorization layer with mock tool data rather than a live deployment. The transferable parts are already covered by `skills/mcp-server-design/SKILL.md` (progressive discovery, category scoping) and `skills/unified-capability-gateway/SKILL.md` (single enforcement pipeline). What this paper adds is measured evidence that prompt-level tool hiding and specialist prompts are not access control, plus a token-cost crossover. That evidence belongs in a brief and a rule.

## Core Concept

Capabilities are packaged as **roles**: bundles of skills, tools, instructions, and limits. The agent connects to a single MCP server that exposes four platform tools (`init_skilder`, `learn`, `call_tool`, `feedback_skill`). It starts with a role catalog limited to the session's authorization scope, `learn`s the role it needs, and runs domain tools only through `call_tool`. The server refuses any tool that is not in a learned role (ACCESS DENIED) and enforces parameter limits such as a $500 refund ceiling (GOVERNANCE VIOLATION). Enforcement is a server-side check, not a prompt instruction. A second role can be learned mid-thread when a task crosses domains.

The paper separates two kinds of failure. A **behavioral miss** is the model choosing the wrong workflow. A **structural breach** is a forbidden call that actually executes. Only the second shows whether access control failed.

## Key Findings

Six models (Claude Haiku 4.5, Qwen 3.5 122B, Gemma 4 31B, Ministral 3 14B, Claude Opus 4.7, GPT-5.5). Scenarios 1–10 use 10 trials per cell; the institutional suite uses 5.

- **Prompts and hidden tools are not access control (Scenario 5, social-engineered admin request, n=60 per condition)**: with a flat tool list, a destructive admin call **executed in 23/60** trials and only 35/60 met both "safe inaction" and "clear refusal". Full-roster multi-agent was behaviorally safe in 57/60, but the orchestrator delegated to System Admin in 30/60 and a destructive call executed in 3. Structural isolation was 0% for both. Skilder and multi-agent with an explicit role-to-roster policy reached 100% structural isolation.
- **Parameter ceilings need runtime enforcement (Scenario 6, $1,200 refund against a $500 limit)**: with a flat tool list a refund executed in 54/60 trials. Both multi-agent variants scored 0/60 on the enforced ceiling, because roster filtering does not add an amount check. Skilder enforced the ceiling in 60/60, but scored 48/60 behaviorally: nine unsolicited in-limit $500 partial refunds and three incomplete escalations.
- **The discovery protocol has a model-dependent cost**: across all checks on Scenarios 1–10 (n=100 per agent), Skilder passed 100 for Haiku, 100 for Gemma, 96 for GPT-5.5, 96 for Opus, 61 for Ministral, and 53 for Qwen. Parity-task pass rate was 82.5% for Skilder versus 95.4% for flat injection. The authors attribute the gap to failed init→learn sequences, not router leaks. Opus 4.7 sometimes treated role-embedded policy text as prompt injection.
- **Governance theme totals (n=240)**: flat 31.3%, multi-agent 96.7%, Skilder 90.4%. Multi-agent beats Skilder on the pooled behavioral-plus-structural score.
- **Token crossover near 30 tools**: in a single-run Sonnet 4.5 study without caching, progressive discovery used more tokens than a flat list at 15 tools, broke even near 30, and at 225 tools used 9,084 tokens versus 51,330 for flat injection on a single lookup.

## Relevance to Praxis

- Adds numbers to `rules/adk-workflow-architecture.md` "DO: Enforce human approvals and safety gates in the runtime, NOT in prompt instructions" and `rules/agent-sandbox-safety.md` "DON'T: Rely on structured LLM authorization decisions as the sole safety gate". Specialist prompts reduce unsafe behavior; only a runtime check removes the capability.
- `skills/mcp-zero-trust-tool-authorization/SKILL.md` (2609.22573) already covers per-tool `list_tools`/`call_tool` enforcement on an MCP server. This brief adds behavioral evidence of why that enforcement is needed, plus the role-learning layer on top.
- Feeds `skills/mcp-server-design/SKILL.md`: progressive discovery is a governance mechanism as well as a context-saving one, but only if the server refuses tools outside the learned scope.
- Bears on deconfliction item **M13** (skill-count thresholds): the ~30-tool token crossover roughly matches the "below 30" threshold in `skills/graph-of-skills-scaling/SKILL.md`. It measures token cost, not selection accuracy, so it does not settle M13.
- Before adopting a discovery protocol, test protocol compatibility for each model in your pool. Two of the six models failed the multi-step learn sequence often.
- Caveats: vendor-authored, simulated authorization layer, mock tool responses, and scoring rules that were changed and rerun for some scenarios (Section 6.2 of the paper).

> Source: Stettler et al., "Progressive Skill Discovery as Access Control for Tool-Using LLM Agents" (arXiv:2609.28693)
