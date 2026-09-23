---
name: selection-invariant-agent-communication
description: >
  Prevent privacy leakage through inter-agent message form by
  constraining the post-authorization representation kernel with a
  selection-invariant communication compiler (SICC). Ensures emitted
  transcripts reveal no information beyond the authorized view.
  Derived from "Selection-Invariant Communication Compilers for
  Privacy-Aware Multi-Agent LLM Workflows" (arXiv:2609.26076).
source: https://arxiv.org/abs/2609.26076
---

# Selection-Invariant Agent Communication (SICC)

Use this skill when building multi-agent workflows where intermediate
messages could leak private state through the *form* of authorized
content, not just its *content*.

## When to Use

- Multi-agent system exchanges intermediate results between agents
- Agents hold private state that must not leak to downstream agents
- Authorization determines WHAT may be sent but not HOW it is
  expressed
- You need formal privacy guarantees on inter-agent communication

## Core Insight

After authorization fixes what information may be released, a
**selection channel** remains: the choice among semantically valid
realizations of the authorized content can reveal private state. For
example, choosing between "the result is 42" and "forty-two is the
answer" may correlate with private context. Surface-disjoint and
length-matched controls do NOT eliminate this channel. SICC constrains
the **post-authorization representation kernel** rather than
prescribing templates.

**Evidence**: Across 132 AgentLeak communication replays and 100
executable LangGraph tasks, deterministic SICC retains complete
protocol utility without positive excess-gain signal.

---

## Procedure

### 1. Identify the Selection Channel

1. Map all inter-agent communication points in your workflow
2. For each message, identify: (a) what authorization permits to be
   sent, (b) what private state the sending agent holds
3. Check: given the authorized content, could the message's **form**
   (word choice, structure, ordering) vary based on private state?
4. If yes → a selection channel exists at this point

### 2. Define the Authorization Boundary

1. For each communication point, define an explicit authorization
   function that determines the **complete authorized view** — the
   maximal information that may be released
2. The authorization function should be external to the sending
   agent (not embedded in the agent's prompt)
3. Document what is IN the authorized view vs. what is private

### 3. Apply the Selection-Invariant Constraint

For each authorized message, ensure the representation satisfies the
selection invariant:

1. **Deterministic mode**: Use a requirement-indexed canonical form —
   a deterministic mapping from (authorized content, message
   requirements) to a single output form. Any deterministic generator
   satisfying the invariant is valid
2. **Randomized mode**: If form variety is needed, use independently
   public-randomized generation — randomness must be independent of
   private state
3. The constraint operates on the **representation kernel** (the
   space of valid realizations), not on specific templates

### 4. Compose with a Dependency-Safe Utility Gate

1. After SICC generates the message, pass it through a
   **dependency-safe utility gate** that checks:
   - Does the message serve the downstream task's information needs?
   - Does it satisfy protocol-level requirements (format, fields)?
2. The gate should NOT have access to the sender's private state
3. Reject messages that fail utility requirements; regenerate under
   the same invariant constraint

### 5. Verify the Compositional Guarantee

The full guarantee requires all three layers:
1. **Authorization**: fixes what may be released
2. **Public-only form generation**: SICC constrains how it's expressed
3. **Dependency-safe utility gate**: ensures task utility

If any layer is missing, the guarantee does not hold.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Selection channel persists | Surface-disjoint or length-matched controls used instead of SICC | Apply full representation-kernel constraint |
| Utility loss from canonical forms | Deterministic mode produces suboptimal messages | Use requirement-indexed forms that preserve protocol needs |
| Authorization embedded in agent prompt | Agent can be prompted to override authorization | Externalize authorization boundary from agent |
| Private-state-aware randomization | Randomness correlated with private state | Use independently public randomization only |
| Missing utility gate | Protocol-incompatible messages pass through | Compose SICC with dependency-safe gate |

> Source: Xu et al., "Selection-Invariant Communication Compilers for
> Privacy-Aware Multi-Agent LLM Workflows" (arXiv:2609.26076),
> Sep 2026.
