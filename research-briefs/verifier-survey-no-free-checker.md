# No Free Checker: A Survey of Verifiers for Robot Policies

> **Paper**: [No Free Checker](https://arxiv.org/abs/2609.09250)
> **Praxis source**: `src:2609-09250v1`

## Why Not a Skill?

Survey â€” comprehensive taxonomy of verifier types for agent/robot policies. No standalone transferable procedures.

---

## Core Concept

There is no universal verifier â€” every verification method trades off along dimensions of coverage, cost, and soundness. The survey categorizes verifiers into formal (sound but narrow), simulation-based (broad but unsound), and learned (cheap but unreliable), and maps when each is appropriate.

### Key Finding

The "no free checker" theorem: no single verifier is simultaneously cheap, broad, and sound. Verification strategy must match the risk profile of the deployment context.

## Relevance to Praxis

- Theoretical backing for the `behavior-aware-verification` skill's selective verification approach
- Informs the `self-verification-elicitation` skill â€” self-verification is a learned verifier with known limitations
