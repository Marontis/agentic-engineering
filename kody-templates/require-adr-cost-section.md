---
name: require-adr-cost-section
description: Enforces that Architecture Decision Records (ADRs) state their negative trade-offs explicitly using a "Bad, and accepted" section.
author: attorn-retrospective
severity: warning
enabled: false
tags: [architecture, documentation, adr]
---

# Require ADR Cost Section

Every Architecture Decision Record (ADR) must explicitly state its costs and trade-offs. An ADR that lists only benefits is incomplete and hides residual risk.

This rule enforces the "Bad, and accepted" section requirement from Attestation-Driven Development (ADD). Writing down the intended negative consequences (e.g., "an upstream that is unreachable now fails reads it could have served from cache") distinguishes a deliberate trade-off from an oversight.

## Instructions

1. Identify when a new ADR (e.g., `docs/adr/*.md`) is added or a major decision is modified.
2. Scan the "Consequences" or "Trade-offs" section of the document.
3. If the document does not contain a "Bad, and accepted" (or equivalent explicit cost/drawback) section, flag the PR.
4. Require the author to list at least one concrete negative consequence or accepted risk of the decision.

## Bad Example

```markdown
# ADR 004: Switch to Redis for Caching

## Decision
We will use Redis for all distributed caching.

## Consequences
- Faster read times
- Shared state across horizontal instances
- Built-in TTL support
```
*(Fails: Only lists benefits. No costs or risks are accepted.)*

## Good Example

```markdown
# ADR 004: Switch to Redis for Caching

## Decision
We will use Redis for all distributed caching.

## Consequences

### Good
- Faster read times
- Shared state across horizontal instances

### Bad, and accepted
- Adds a new infrastructure dependency (Redis cluster) that must be maintained.
- Cache stampede risk on cold starts is heightened; we accept this for now until load requires probabilistic early expiration.
```
*(Passes: Explicitly names the negative trade-offs and accepts them.)*
