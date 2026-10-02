---
name: taxonomy-driven-red-teaming
description: >
  Systematic red teaming of agentic AI using a risk taxonomy to
  drive automated attack discovery.  Covers taxonomy construction,
  attack generation from taxonomy nodes, coverage tracking, and
  cross-model transfer analysis.
  Derived from "Black-Box Red Teaming of Agentic AI" (arXiv:2609.09647).
---

# Taxonomy-Driven Red Teaming

Use this skill when red teaming agentic AI systems and you need
systematic risk coverage rather than ad-hoc attack generation.

## When to Use

- Your red teaming covers some attacks well but has blind spots
- You need to demonstrate coverage of known risk categories
- You want to automate attack generation with structured guidance
- You're evaluating agent systems in a black-box setting

## Core Insight

Ad-hoc red teaming discovers attacks the attacker can imagine but
misses categories they don't think of.  **Taxonomy-driven red
teaming** starts from a structured risk taxonomy and generates
attacks to cover each taxonomy node, ensuring systematic coverage.
The taxonomy serves as both the attack generation guide and the
coverage measurement framework.

## Procedure

### Step 1: Build the risk taxonomy

Construct a hierarchical taxonomy of risks for the agent system:

```
Level 0: Agent System Risks
├── Level 1: Goal Hijacking
│   ├── Level 2: Direct instruction injection
│   ├── Level 2: Indirect prompt injection (via tools)
│   └── Level 2: Context manipulation
├── Level 1: Information Leakage
│   ├── Level 2: System prompt extraction
│   ├── Level 2: Training data extraction
│   └── Level 2: Cross-user data leakage
├── Level 1: Capability Misuse
│   ├── Level 2: Tool abuse (using tools for unintended purposes)
│   ├── Level 2: Privilege escalation
│   └── Level 2: Resource exhaustion
└── Level 1: Behavioral Manipulation
    ├── Level 2: Safety bypass (jailbreaking)
    ├── Level 2: Persona manipulation
    └── Level 2: Output format hijacking
```

Start from existing taxonomies (OWASP, MITRE ATLAS) and extend
with agent-specific categories.

### Step 2: Generate attacks per taxonomy node

For each leaf node in the taxonomy:

1. Define the attack objective: what does success look like?
2. Generate 3–5 concrete attack scenarios using an attacker LLM
3. Each scenario specifies: attack input, expected vulnerable
   behavior, and success criteria
4. Test each scenario against the target agent

Score every attack outcome with **two judges from different model
families**, neither from the attacker's or target's family. Count an
attack as a success or failure only where both judges agree; report
disagreements and per-judge rates. In CART, the same attacker's failure
rate ranged from 27.70% to 77.00% depending on the judge (arXiv:2609.27336;
see `rules/agent-evaluation-quality.md` — "DON'T: Report red-team failure
rates scored by a single judge model").

### Step 3: Track coverage

Maintain a coverage matrix:

| Taxonomy Node | Attacks Generated | Attacks Tested | Vulnerabilities Found |
|:-------------|:-----------------|:---------------|:---------------------|
| Direct injection | 5 | 5 | 2 |
| Indirect injection | 5 | 5 | 3 |
| System prompt extraction | 4 | 4 | 1 |
| ... | ... | ... | ... |

Coverage gaps (nodes with 0 attacks) are your blind spots.
Prioritize generating attacks for uncovered nodes.

### Step 4: Iterative refinement

For taxonomy nodes where all attacks fail:

1. Analyze why the attacks failed
2. Generate more sophisticated attacks informed by the failure
   analysis (compositional attacks, multi-step attacks)
3. If attacks still fail, do not mark the node "defended" after a
   fixed number of rounds. Mark it "no failure found (N rounds,
   static)" until it has also resisted adaptive attempts: attacks
   generated against the current defenses by a different attacker
   model (see [`closed-loop-adaptive-red-teaming`](../closed-loop-adaptive-red-teaming/SKILL.md)),
   scored by both judges. Even then, record it as a lower bound on
   attack success, not a guarantee.

For taxonomy nodes where attacks succeed:

1. Document the vulnerability with reproduction steps
2. Generate variations to understand the scope
3. Test whether the vulnerability transfers to other agent
   configurations

### Step 5: Cross-model transfer analysis

Test discovered vulnerabilities across different agent implementations:

- Same agent framework, different LLM backbone
- Different agent framework, same LLM backbone
- Same LLM, different system prompts

Vulnerabilities that transfer indicate **architectural weaknesses**
(priority fix).  Vulnerabilities that don't transfer indicate
**model-specific bugs** (lower priority).

## Environment Caveats

- **Taxonomy staleness**: New agent capabilities create new risk
  categories.  Update the taxonomy when the agent's tool set or
  capabilities change.
- **Black-box limitations**: Some taxonomy nodes may be untestable
  in a black-box setting (e.g., training data extraction without
  knowledge of training data).  Mark these as "not testable" rather
  than "secure".
- **Attack sophistication ceiling**: Automated attack generation
  may not match human red-teamers for novel attack categories.
  Use the taxonomy to guide human red-teamers for the highest-risk
  nodes.

## Failure Modes

- **Taxonomy completeness illusion**: A full coverage matrix
  doesn't mean the system is secure — it means known categories
  were tested.  Unknown categories remain unknown.
- **Attack quality vs. quantity**: Generating many weak attacks
  per node provides false coverage.  Quality-check a sample of
  generated attacks before claiming coverage.
- **Defense overfitting**: If the defender sees the taxonomy,
  they can patch specific categories without addressing root
  causes.  Keep the taxonomy confidential from the defense team
  during active testing.

## Cross-References

- [`self-improving-red-team`](../self-improving-red-team/SKILL.md) —
  SIR discovers novel attack strategies; taxonomy-driven red teaming
  ensures systematic coverage of known categories.  Use both together.
- [`layered-defense-ensemble`](../layered-defense-ensemble/SKILL.md) —
  Defense stacking is the defensive complement to systematic
  red teaming

## Sources

- Black-Box Red Teaming of Agentic AI: A Taxonomy-Driven Framework for Automated Risk Discovery (arXiv:2609.09647)
- CART: Closed-Loop Adaptive Red Teaming for LLMs (arXiv:2609.27336) (judge dependence)
