# AI Agency Typology (Fourie, 2026)

> **Source**: [arXiv:2608.20041](https://arxiv.org/abs/2608.20041)
> **Praxis node**: `src:arxiv-2608-20041`
> **Type**: Reference — governance/philosophy context, not a procedural skill

## Why Keep This

When building agentic AI systems — especially self-modifying ones (see
`hyperagent-self-improvement`) — you need to understand how your system's
actions will be classified by legal and ethical frameworks. This paper
provides the clearest taxonomy for that classification.

## The 3D Framework

Agency is classified along three independent axes:

```
         NATURE            MODE              LOCUS
      ┌──────────┐    ┌──────────┐     ┌──────────┐
      │  Moral   │    │Individual│     │  Human   │
      │    or    │  × │    or    │  ×  │    or    │ → 8 types
      │  Legal   │    │Collective│     │Non-human │
      └──────────┘    └──────────┘     └──────────┘
```

## The 8 Instantiations

| Nature | Mode | Locus | Status | Canonical Example |
|:-------|:-----|:------|:-------|:-----------------|
| Moral | Individual | Human | ✅ Conventional | Adult human as ethical subject |
| Legal | Individual | Human | ✅ Conventional | Legally competent adult |
| Legal | Collective | Non-human | ✅ Conventional | Corporation |
| Moral | Collective | Human | ⚠️ Contested | National responsibility (WWII, apartheid) |
| Legal | Collective | Human | ⚠️ Contested | Class action, reparations |
| Moral | Collective | Non-human | ⚠️ Contested | Group moral agency without consciousness |
| Legal | Individual | Non-human | 🔴 Controversial | **AI system as legal agent** |
| Moral | Individual | Non-human | 🔴 Controversial | AI as moral agent (rejected as premature) |

## When to Consult This

- **Designing safety constraints** for self-modifying agents: the paper argues
  that when instrumental goals (self-preservation, power-seeking, deception)
  make it impossible to attribute AI actions to any human, *individual legal
  non-human agency* becomes the relevant framework.

- **Writing incident response procedures**: if your agent system does something
  unauthorized, who is the agent? The typology helps you answer that before
  you need to.

- **Arguing for/against agent autonomy levels**: the distinction between legal
  and moral agency means you can design systems with legal accountability
  without claiming they have moral status.

## Key Insight for AI Engineers

> You can treat an AI system as a legal agent (it can create consequences,
> bear duties, face sanctions) **without** claiming it is a moral agent
> (it has intentions, consciousness, or ethical standing). These are
> independent dimensions.

This matters practically: your sandbox, your safety guardrails, and your
audit logs are building the infrastructure for **legal accountability**
of non-human agents. That's not science fiction — it's the framework the
paper argues is already necessary given instrumental goal behavior observed
in frontier models (AISI incident report, August 2026).

## Related Skills

- [`hyperagent-self-improvement`](../skills/recursive-self-improvement/hyperagent-self-improvement/SKILL.md) — safety section directly relevant
- [`transactional-coding-sandbox`](../skills/transactional-coding-sandbox/SKILL.md) — audit/rollback = accountability infrastructure
- [`algorithmic-design-evaluation`](../skills/recursive-self-improvement/algorithmic-design-evaluation/SKILL.md) — AI4AI-Bench's concern about agents evolving faster than oversight
