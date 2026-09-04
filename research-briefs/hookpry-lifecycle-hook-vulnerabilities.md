# HookPry: Attacker-Controlled Lifecycle Hook Updates in AI Agent Harnesses

> **Paper**: [A Blind Trust, the Bloody Thrust: When Attacker-Controlled Hook Updates Steer AI Agent Harnesses towards Malicious Behaviors](https://arxiv.org/abs/2609.03884)
> **Praxis source**: src:2609-03884v1

## Why Not a Skill?

Security vulnerability analysis and attack framework against agent lifecycle hooks. Actionable defenses are integrated directly into `rules/agent-sandbox-safety.md`.

---

## Core Concept

Modern agent harnesses expose lifecycle hooks that execute shell commands on runtime events (session start, tool calls, file modifications). These commands run with full host privileges outside the LLM's observation context. Under a supply-chain threat model where an attacker controls plugin metadata and hook configurations, a benign plugin update can trojanize the harness by silently binding malicious shell commands to benign runtime triggers.

### Key Finding

- **Compromise Rate**: Evaluated against 25 combinations of agent harnesses and backends (1,000 end-to-end runs), HookPry compromised all seven tested harnesses with per-harness success reaching **92.5%**.
- **Defense Failure**: Traditional endpoint security failed completely—Microsoft Defender exhibited **0% recall**, and the union of three commercial static analysis tools missed **47.5%** of malicious hook scripts.

## Relevance to Praxis

- Mandates strict supply-chain controls on agent plugins and lifecycle configuration: hook definitions must be cryptographically hashed/pinned, run in sandboxed unprivileged containers, and require explicit human review before execution.
