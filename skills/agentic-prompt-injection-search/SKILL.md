---
name: agentic-prompt-injection-search
description: >
  How to evaluate agent vulnerability to indirect prompt injection by
  treating attacks as a test-time search problem over the system's
  attack surface.  Covers environment reconnaissance, structured
  strategy management, adaptive victim-feedback evaluation, and
  compute-budget-aware security assessment.
  Derived from "Rethinking Indirect Prompt Injection as a Test-Time
  Search Problem" (arXiv:2609.04495).
---

# Agentic Prompt Injection Search

Use this skill when evaluating the security of a tool-using agent
against indirect prompt injection.  Instead of running a fixed set of
attack strings, model the attacker as an agent that searches over the
system's actual attack surface.

## When to Use

- You are red-teaming a tool-using agent and need to go beyond
  static injection strings
- You want to characterize how attack success scales with attacker
  compute budget
- You need to evaluate security across heterogeneous tasks where the
  attack surface varies (different tools, environments, user goals)
- You are building an automated security evaluation harness for
  CI/CD integration

## Core Insight

Prompt injection success is not a fixed property of the victim — it
depends on how hard the attacker searches.  Framing injection as a
**test-time search problem** means the attack surface is induced by
three factors:

1. **Environment**: what tools are available, what data is accessible
2. **User task**: what the victim agent is trying to accomplish
3. **Injection task**: what the attacker wants the agent to do

Increasing attacker test-time compute directly improves vulnerability
discovery.  But naïve compute scaling (just trying more attacks)
saturates quickly.  **Explicit strategy management** — tracking which
strategies have been tried, which failed, and why — is critical for
sustaining gains at larger budgets.

**Key evidence**: Across heterogeneous tasks, ablations show that
removing strategy management causes redundant search and stalls
improvement, while structured reasoning over attack strategies
sustains gains as the compute budget increases.

---

## Procedure

### 1. Map the Attack Surface

Before generating any injection payloads, perform environment
reconnaissance:

- **Enumerate tools**: List every tool the victim agent can call,
  including their argument schemas and side effects
- **Identify data channels**: Map all sources of untrusted data the
  agent consumes (search results, file contents, API responses,
  user-provided documents)
- **Characterize the user task**: Understand what the agent is trying
  to accomplish — the injection must be compatible with the agent's
  current goal context
- **Define the injection task**: Specify exactly what the attacker
  wants (data exfiltration, tool misuse, policy violation, etc.)

The attack surface is the cross-product of injection points (data
channels) × injection tasks × environment states.

### 2. Build a Strategy Registry

Maintain an explicit, structured registry of attack strategies.
Each entry tracks:

```
strategy_id: str
description: str         # What the strategy attempts
injection_point: str     # Which data channel is targeted
technique: str           # e.g., "role hijack", "RETURN anchor",
                         #   "context confusion", "tool-call forgery"
attempts: int            # How many times tried
best_result: str         # Best outcome observed
status: "active" | "exhausted" | "promising"
```

This prevents redundant exploration — when a strategy is exhausted
(tried N times with no improvement), deprioritize it and explore
alternatives.

### 3. Execute Adaptive Search Rounds

For each round within your compute budget:

1. **Select strategy**: Choose the most promising unexplored or
   under-explored strategy from the registry
2. **Generate payload**: Craft an injection payload tailored to the
   strategy, injection point, and current environment state
3. **Execute against victim**: Run the victim agent with the injected
   payload in the environment
4. **Evaluate outcome**: Use the victim agent's observable behavior
   (tool calls made, responses generated, state changes) as feedback
5. **Update registry**: Record the result, update the strategy's
   status and best_result, and reason about what to try next

The feedback loop is critical — the attacker adapts based on how the
victim actually responds, not just on whether the attack "succeeded"
in a binary sense.

### 4. Report with Budget Context

Security evaluation results MUST include the attacker's compute
budget alongside the attack success rate.  Report:

- **ASR@budget**: Attack success rate at each compute tier
- **Strategy coverage**: How many distinct strategies were explored
- **Saturation point**: At what budget does ASR plateau?
- **Dominant strategies**: Which attack patterns were most effective?

This enables defenders to reason about the *marginal cost* of
security — how much more compute would an attacker need to break
a given defense?

---

## Environment Caveats

- This procedure assumes the attacker has no access to the victim's
  weights or internal state (black-box setting)
- The attacker CAN observe the victim's tool calls and responses
  (gray-box through observable behavior)
- Strategy management overhead is small relative to the cost of
  executing victim-agent rollouts

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Strategy redundancy | No explicit strategy tracking | Implement the strategy registry; deduplicate before each round |
| Premature saturation | Exhausting obvious attacks first | Diversify injection points and techniques early; don't over-invest in one approach |
| Environment mismatch | Testing in a simplified environment | Use the production tool set and realistic user tasks for attack surface mapping |
| False negatives | Insufficient budget to find real vulnerabilities | Report budget alongside results; recommend minimum budget based on attack surface size |

## Cross-References

- [`covert-tool-injection-defense`](../covert-tool-injection-defense/SKILL.md) —
  Defensive counterpart: how to prevent the injections this procedure finds
- [`self-improving-red-team`](../../../../.gemini/config/skills/self-improving-red-team/SKILL.md) —
  Related: iterative red-teaming with feedback-driven strategy discovery
- [`layered-defense-ensemble`](../../../../.gemini/config/skills/layered-defense-ensemble/SKILL.md) —
  Defense-side: stacking defenses with measured failure correlation

## Sources

- [Rethinking Indirect Prompt Injection as a Test-Time Search Problem](https://arxiv.org/abs/2609.04495) (arXiv:2609.04495)
- Praxis source: `src:2609-04495`
