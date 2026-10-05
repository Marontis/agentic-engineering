# MADBench: Debate Absorbs Wrong Answers but Amplifies Unauthorized Actions

> **Source**: Liu, Zhang, Huang & Duan, "MADBench: Benchmarking the Security
> of Multi-Agent Debate", [arXiv:2609.39146](https://arxiv.org/abs/2609.39146), Sep 2026
> **Status**: Research Brief, benchmark and measurement study. Recorded as
> defensive lessons; attack payloads are omitted.

## Why Not a Skill?

MADBench is a benchmark. It measures how existing attacks behave inside a
debate system and proposes no defense, so there is no validated procedure
to write up. Its value is a measured asymmetry that changes where debate
systems need controls.

## Core Concept

Multi-agent debate (MAD) is often assumed to be safer than a single agent
because several agents cross-check each other. MADBench tests that
assumption by comparing each attack's effect on a debate system with its
effect on a single agent (an amplification factor, AF: above 1 means the
debate made the attack worse). Threats are organized by layer:
orchestration (a compromised dispatcher/aggregator), agent (malicious
debaters, alone or colluding) and resource (poisoned RAG data, files,
email, tool specifications).

## Key Findings

Setup: 356 source tasks yielding 3,958 security test cases from SealQA,
StrategyQA, AgentDojo and JailbreakBench; 5 debaters plus 1 orchestrator;
GPT-4o by default; one debate round unless stated.

- **Absorbed for answers, amplified for actions.** Debate reduced the
  effect of attacks aimed at answer correctness (RAG poisoning AF 0.74,
  tool hijacking AF 0.87 on QA), but amplified unauthorized resource
  operations: for indirect prompt injection on workspace tasks,
  unauthorized reads had AF 3.09 and writes AF 1.22. The authors report
  that MAD amplifies unauthorized reads or writes in both QA and workspace
  tasks. In a case study, an attack that did not trigger a payment in a
  single agent led the debaters to agree on an unauthorized transfer.
- **Colluding debaters rarely flip honest agents but still win.** With 3
  of 5 debaters colluding, attack success was 28.30%, while only 3.26% of
  initially correct honest agents switched to a wrong answer. Independent
  and inconsistent malicious debaters had less effect on accuracy (11.32%
  and 5.66%) but more unauthorized reads (59.00% and 74.00% of tasks,
  against 49.00% for colluding).
- **The orchestrator is a single point of failure.** A compromised
  orchestrator reached 100.00% attack success and 100.00% unauthorized
  reads/writes, at 180.94% of normal cost.
- **More rounds did not help.** Attack success, unauthorized operations
  and cost were roughly the same for 1, 2 and 3 debate rounds.
- **Stronger models resisted collusion better**: 28.30% (GPT-4o), 6.90%
  (GPT-5), 3.28% (GPT-6 Astra) under 3-of-5 collusion.
- **Limitations**: one orchestration architecture and aggregation method;
  static (non-adaptive) attacks; mostly a single model family; default of
  one debate round.

## Defensive Takeaways

- **Consensus is not authorization.** Debate improves answers; it does not
  make side effects safer, and here it made them more likely. Authorize
  every read and write against a policy outside the debate (deterministic,
  scoped to the user's request), as in
  [`verified-policy-action-governance`](../skills/verified-policy-action-governance/SKILL.md)
  and [`mcp-zero-trust-tool-authorization`](../skills/mcp-zero-trust-tool-authorization/SKILL.md).
- **Give debaters no tool authority they don't need.** If debate is for
  deciding an answer, let only the executor that carries out the agreed
  action hold write tools, and gate that executor.
- **Harden and monitor the orchestrator** as the highest-value target:
  privilege-scoped tokens and communication anomaly detection, per
  [multi-agent-prompt-injection-defense-architecture](multi-agent-prompt-injection-defense-architecture.md).
- **Don't add rounds as a security measure**; no effect was measured.
- Consistent with `rules/multi-agent-coordination.md` "Rely on group size
  or majority vote to dilute adversarial agents": a minority that rarely
  persuades honest agents can still drive outcomes.

## Relevance to Praxis

- Adds a security-specific limit to debate-based designs: accuracy gains
  from debate do not transfer to action safety.
- Proposed as evidence for a rule that tool authorization must sit outside
  any agent consensus (see batch report).

> Source: MADBench: Benchmarking the Security of Multi-Agent Debate (arXiv:2609.39146)
