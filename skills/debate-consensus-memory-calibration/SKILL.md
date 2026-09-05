---
name: debate-consensus-memory-calibration
description: >
  Calibrate multi-agent debate (MAD) systems against shared misconceptions
  and majority skew using experience memory retrieval and dynamic confidence
  reweighting. Derived from R^2-MAD (arXiv:2609.03619).
---

# Debate Consensus Memory Calibration

Use this skill when designing or deploying multi-agent debate (MAD) systems,
agent ensembles, or peer-review reflection loops to prevent premature groupthink,
error amplification, and herd behavior.

## When to Use

- You run multi-agent debate or collaborative reflection loops where multiple
  agents critique and refine each other's outputs.
- Agents display **shared misconceptions**: when a majority of agents start
  with an erroneous premise, subsequent debate rounds amplify the error
  instead of correcting it.
- Unweighted consensus voting fails because the vocal or confident majority
  overrules a minority agent that actually holds the correct insight.
- You have an archive or historical memory of past debate trajectories and outcomes.

## Core Insight

Standard Multi-Agent Debate relies on peer discussion to converge on truth.
However, empirical analysis shows that when an initial cohort shares a biased
concept prior, the debate acts as an echo chamber—reinforcing the error across
rounds (peer skew).

Yu et al. (arXiv:2609.03619) identify that peer discussion alone is insufficient
without grounding external to the current round. The $R^2$-MAD architecture
resolves this through two coupled mechanisms:
1. **Debate-State-Aware Retrieval**: Dynamically monitors consensus entropy.
   When consensus is high, or when divergence suggests a deadlock, the system
   queries an experience memory of verified past debates to inject calibrated
   counter-evidence.
2. **Confidence-Weighted Peer Influence**: Replaces unweighted averaging with
   reliability estimation derived from past trajectory performance, modulating
   each agent's influence on the group belief.

---

## Procedure

### Step 1: Measure Round-Level Consensus Entropy

At the end of each debate round $t$, compute the agreement distribution across
all participating agents:

1. **Stance Vector**: Extract the categorical decision or key factual assertion
   $a_i^{(t)}$ from each agent $i \in \{1, \dots, N\}$.
2. **Consensus Entropy ($H$)**:
   $$H(t) = -\sum_{c \in \mathcal{C}} p(c) \log p(c)$$
   where $p(c)$ is the fraction of agents supporting conclusion $c$.
3. **Trigger States**:
   - **Premature Convergence** ($H(t) < \tau_{\text{low}}$ early in debate):
     High risk of shared misconception.
   - **Deadlock / High Dispersal** ($H(t) > \tau_{\text{high}}$ across consecutive rounds):
     Agents lack grounding evidence to resolve conflicts.

### Step 2: Query Experience Memory with State-Aware Filtering

When a trigger state is detected, retrieve grounding records from an indexed
memory of past verified solutions:

1. **Context Query Construction**: Concatenate the initial prompt with the
   contested claims from round $t$.
2. **State-Conditioned Filtering**:
   - For *premature convergence*: Specifically retrieve historical cases where
     an apparent majority conclusion turned out to be an edge-case failure.
   - For *deadlock*: Retrieve verified exemplars that establish the decisive
     discriminative rule between the conflicting perspectives.
3. **Inject Invariant Prior**: Inject the retrieved case into the prompt of
   round $t+1$ as an external anchor:
   `"Prior Invariant Evidence: In similar past evaluations, hypothesis X failed due to Y. Account for this in your next argument."`

### Step 3: Compute Reliability Weights for Peer Aggregation

Do not treat all peer arguments equally. Compute an agent's influence weight
$w_i^{(t)}$ using historical accuracy and evidence citation fidelity:

1. **Factual Grounding Score ($S_{\text{ground}}$)**: Proportion of claims in
   agent $i$'s argument backed by retrieved evidence vs. unsupported assertions.
2. **Historical Reliability ($R_i$)**: Track rolling accuracy of agent $i$ on
   verified past tasks.
3. **Modulated Weight**:
   $$w_i = \frac{\exp(R_i \cdot S_{\text{ground}} / T)}{\sum_j \exp(R_j \cdot S_{\text{ground}} / T)}$$
4. **Weighted Synthesis**: Pass the weighted arguments to the aggregator/judge
   agent, ensuring higher weight is assigned to well-grounded arguments even if
   in the numerical minority.

### Step 4: Early Stopping with Grounding Criterion

Terminate debate only when:
- Consensus is reached ($H(t) \le \tau_{\text{low}}$), **AND**
- The winning position explicitly incorporates the retrieved grounding evidence
  without unaddressed counter-examples.

---

## Environment Caveats

- **Cold-Start Memory**: In new domains without existing debate histories,
  initialize the experience memory using curated specification templates or
  few-shot benchmark solutions.
- **Context Overhead**: Avoid injecting entire debate histories. Store and
  retrieve concise rationale-outcome pairs (e.g., `<Contested Proposition, Failure Root Cause, Verified Resolution>`).

---

## Failure Modes

- **Memory Contamination**: Storing unverified debates in the experience memory
  can cause self-reinforcing hallucinations. Only write to the experience memory
  when an outcome is verified by external tool execution, test suites, or ground truth.
- **Echo Chamber via Over-Retrieval**: Injecting identical past evidence into
  all agents can suppress diverse exploration. Assign distinct retrieved facets
  to different debate participants.

---

## Cross-References

- [`rag-evidence-triage`](../rag-evidence-triage/SKILL.md) —
  Classifying retrieved evidence as sufficient or conflicting before injection.
- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md) —
  Identifying the decisive erroneous agent in multi-agent failures.
- [`counterexample-guided-repair`](../counterexample-guided-repair/SKILL.md) —
  Refining artifacts using compact negative witnesses.

---

## Sources

- **Paper**: [Remember and Reweight: Enhancing Multi-Agent Debate with Experience Memory and Confidence Estimation](https://arxiv.org/abs/2609.03619) (arXiv:2609.03619)
- **Praxis source**: `src:2609-03619`
