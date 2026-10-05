# AgentXploit: Defensive Lessons from Repository-to-Runtime Agent Audits

> **Source**: AgentXploit: Autonomous Repository-to-Runtime Red-Teaming for AI Agents, [arXiv:2609.31318](https://arxiv.org/abs/2609.31318), Sep 2026
> **Status**: Research Brief, defensive lessons only. The paper describes an
> autonomous auditing tool; this brief records what it teaches defenders and
> deliberately omits attack procedures (see the repo's `AGENTS.md`).

## Why Not a Skill?

The paper's procedure is an offensive auditing agent for authorized
white-box pre-deployment testing. Turning that into a step-by-step skill
here would amount to an exploitation playbook. What transfers to agent
builders is the defensive side: which weakness patterns recur in agent
codebases, and why finding them takes both code analysis and runtime
testing.

## Core Concept

AI agents combine two attack surfaces: **adversarial content** that changes
what the agent does with its tools (prompt injection steering tool use), and
**conventional software flaws** in the code around the model (path
traversal, command execution, SQL injection, SSRF, unsafe evaluation). The
dangerous paths usually cross both: untrusted content reaches a tool
argument, and the tool's own validation doesn't match what actually executes.

## Key Findings

- **Benchmark**: AgentXploit-Bench, 72 reproducible vulnerabilities across
  12 open-source agent systems and frameworks, drawn from public CVEs and
  security issues (not new disclosures; the paper reports no remediation
  status).
- **End-to-end audit success**: 59.3% across three runs, versus 38.4% for a
  Codex baseline (46.3% token-matched). On AgentDojo with injection points
  given: 79.2% versus 52.7% for AgentVigil.
- **Discovery and exploitation are separate problems**: analysis alone
  recovered 71.8% of ground-truth attack paths, and 69.0% of failures
  happened during analysis. Given an oracle specification of the path,
  exploitation succeeded 88.0% of the time, versus 59.3% end to end. On the
  13 indirect paths (where untrusted content must be consumed first) the
  auditor reached 59.0% versus 28.2% for Codex.
- **Three recurring root causes**:
  1. **Credentials crossing component boundaries**: a configured API key
     attached to URLs that were validated for scheme but not for whether the
     destination should receive it.
  2. **Validation and execution on different representations**: checking
     one form of an operation (e.g. a command's first token) while executing
     another (a full shell string) leaves an interpretation gap.
  3. **Trusting retrieved external content**: documents and tool responses
     influencing sensitive operations without a check on whether they
     should.
- **Limitations stated by the authors**: 72 instances in 12 projects; the
  indirect-path (13) and mutation (20) subsets are small; attack-path
  recovery was manually adjudicated; candidate precision was audited on one
  repository only; one model family; training-data contamination can't be
  ruled out.

## Defensive Takeaways

- **Validate what you execute.** Validate and execute the same structured
  operation (an argument vector, a parsed URL with a destination
  allowlist), never a string re-interpreted later. This is the authors'
  main mitigation, and it matches
  [`verified-policy-action-governance`](../skills/verified-policy-action-governance/SKILL.md)
  (bounded records, deterministic checks).
- **Bind credentials to destinations.** Attach credentials only to
  allowlisted destinations, with least-privilege scopes, so injected or
  redirected requests can't carry them. See
  [`mcp-zero-trust-tool-authorization`](../skills/mcp-zero-trust-tool-authorization/SKILL.md).
- **Treat tool outputs and retrieved documents as untrusted input to every
  later tool call**, per `rules/agent-sandbox-safety.md` "Sanitize all tool
  outputs before injecting into agent context".
- **Test both layers before release.** Static review of the repository and
  runtime testing of the deployed agent each miss findings the other
  catches (71.8% path recovery vs 88.0% oracle exploitation). Pair code
  review with adaptive runtime red-teaming
  ([`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md))
  under the controls in
  [`pentest-harness-assurance`](../skills/pentest-harness-assurance/SKILL.md).
- **A low attack-success rate on one benchmark is not a security
  property.** The same paper's numbers move by tens of points between
  benchmarks and access levels; see `rules/agent-sandbox-safety.md`
  "Measure open privilege alongside attack success and utility".

## Relevance to Praxis

- Adds a concrete root-cause list for agent codebases to the sandboxing
  rules: most of these failures are conventional input-validation bugs that
  agents make reachable, not model failures.
- Supports the existing rules on deterministic authorization and on
  treating tool outputs as untrusted; it introduces no rule that conflicts
  with them.

> Source: AgentXploit: Autonomous Repository-to-Runtime Red-Teaming for AI Agents (arXiv:2609.31318)
