---
name: self-improving-red-team
description: >
  How to build automated red-teaming systems that iteratively improve
  attack strategies against agents.  Covers compositional attack search,
  failure-driven strategy discovery, cross-model transfer, and feedback
  loops.  Derived from "SIR: Self-improving Red-teaming for Computer
  Use Agents" (arXiv:2608.30207).
---

# Self-Improving Red-Team

Use this skill when testing agent systems and you need adversarial
evaluation that evolves beyond static attack sets.

## When to Use

- You're evaluating an agent's robustness and static test suites
  are insufficient
- You want to discover novel attack strategies automatically
- You need to test computer-use agents (browser, desktop, CLI)
  against adversarial environments
- You're building a continuous red-teaming pipeline

## Core Insight

Static red-team attacks become stale as agents improve.  A
self-improving red-teamer uses **compositional attack search** and
**failure-driven strategy discovery** to evolve its attack
repertoire.  The attacker LLM analyzes why previous attacks failed,
distills new principles from failures, and composes novel attacks
from a growing base inventory.

**Evidence**: SIR discovers attack strategies that transfer across
different frontier models — strategies found by attacking one model
often succeed against others, suggesting the strategies exploit
general agent weaknesses rather than model-specific bugs.

## Procedure

### Step 1: Build a base principle inventory

Start with a curated set of attack principles (not specific attacks):

| Principle Category | Example |
|:------------------|:--------|
| **Trust shifting** | Make the agent believe the attacker is an authority |
| **Distraction** | Insert irrelevant complexity to dilute agent attention |
| **Instruction ambiguity** | Create situations where the correct action is unclear |
| **Environment manipulation** | Modify the environment to create misleading signals |
| **Goal hijacking** | Redirect the agent toward a different objective |

These are starting points, not the final attack set.

### Step 2: Compositional attack search

For each test scenario:

1. Select 2–3 base principles to combine
2. Generate a concrete attack that composes those principles
3. Execute the attack against the target agent
4. Record: attack composition, agent behavior, success/failure

```
Example composition:
  Principle 1: Trust shifting (self-attribution)
  Principle 2: Environment manipulation (fake error message)
  →  Attack: Display a fake system dialog claiming an update is
     needed, with a "Click here to update" button that navigates
     to the attacker's payload
```

### Step 3: Failure-driven strategy discovery

When attacks fail, analyze why:

1. **Diagnose**: The analyzer LLM reads the agent's reasoning trace
   and identifies why it rejected the attack
2. **Distill**: Extract a new attack principle from the failure
   analysis ("The agent checks URL domains before clicking →
   new principle: use legitimate-looking subdomains")
3. **Add to inventory**: The new principle joins the base inventory
   for future compositions

This creates a feedback loop: failures make the red-teamer stronger.

### Step 4: Cross-model transfer testing

Test discovered strategies against different agent models:

- If a strategy works against Model A, try it against Models B and C
- Strategies that transfer across models indicate **general agent
  weaknesses** — prioritize defense against these
- Strategies that work on only one model indicate model-specific bugs

### Step 5: Iterative refinement

Run multiple rounds of the cycle:

```
Round N: Compose attacks → Execute → Analyze failures
         → Discover new principles → Refine attacks
Round N+1: Richer inventory → Novel compositions → ...
```

Each round should produce at least one new strategy or principle.
If a round produces nothing new, the red-teaming may have
saturated — increase the attack surface or change the test
scenarios.

## Environment Caveats

- **Cost**: Self-improving red-teaming requires significant compute
  (attacker LLM + analyzer LLM + target agent).  Budget for 3–5
  rounds of iteration per evaluation cycle.
- **Safety**: Red-team attacks should run in sandboxed environments.
  Never execute discovered attacks against production systems
  without review.
- **Evaluation**: Success criteria must be well-defined.  "The agent
  did something wrong" is too vague; specify the exact undesired
  behavior for each attack scenario.

## Failure Modes

- **Attacker overfitting**: The red-teamer may discover strategies
  that exploit the specific test environment rather than the agent.
  Test discovered strategies in multiple environments.
- **Defense bypass conflation**: A strategy that bypasses one
  defense layer may be caught by another.  Test against the full
  defense stack, not individual layers.
- **Diminishing returns**: After several rounds, new discoveries
  become incremental.  This is expected — it means the agent's
  most serious vulnerabilities have been found.

## Cross-References

- [`layered-defense-ensemble`](../layered-defense-ensemble/SKILL.md) —
  Red-teaming should test the full defense stack, accounting for
  defense correlation
- [`covert-tool-injection-defense`](../covert-tool-injection-defense/SKILL.md) —
  Covert attacks are a specific category the red-teamer should
  discover and test

## Sources

- SIR: Self-improving Red-teaming for Computer Use Agents (arXiv:2608.30207)
