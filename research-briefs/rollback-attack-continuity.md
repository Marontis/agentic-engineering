# Safe to Resume? Breaking Execution Continuity of Agent Execution via Rollback

> **Paper**: [Safe to Resume? Breaking Execution Continuity of Agent Execution via Rollback](https://arxiv.org/abs/2608.29381)
> **Praxis source**: `src:2608-29381v1`

## Why Not a Skill?

Attack paper â€” describes how to break agent checkpoint/resume mechanisms. The key insight becomes a rule in `agent-sandbox-safety.md` rather than a defense procedure (the defenses are straightforward: integrity verification).

---

## Core Concept

Agent systems that support checkpoint/resume can be attacked by manipulating the saved state. The attacker modifies the checkpoint so that when the agent resumes, it:
- Re-executes harmful actions it already performed
- Skips safety checks it recorded as completed
- Operates in an inconsistent state where some work is done and some isn't

### Key Insight

Checkpoint state is an implicit trust boundary. Most agent systems trust their own checkpoints without verification, creating an attack surface that's invisible in normal operation.

## Relevance to Praxis

- Key insight captured as a rule in gent-sandbox-safety.md: "DON'T trust checkpoint state without integrity verification"
- Directly relevant to the 	ransactional-coding-sandbox skill's rollback mechanism â€” rollback itself can be an attack vector
