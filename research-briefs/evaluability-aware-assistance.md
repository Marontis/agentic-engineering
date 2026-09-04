# ProSE: Evaluability-Aware Assistance under Bounded Rationality

> **Paper**: [Propose to Learn, Learn to Propose: Evaluability-Aware Assistance under Bounded Rationality](https://arxiv.org/abs/2609.02242)
> **Praxis source**: src:2609-02242v1

## Why Not a Skill?

Theoretical planning framework and formal problem definition (ProSE) for human-in-the-loop assistance rather than an autonomous subtask procedure.

---

## Core Concept

AI assistants collaborate by proposing candidate edits, plans, or designs for human users to evaluate. Existing methods assume users can reliably evaluate any proposal. Under human bounded rationality, evaluating complex proposals is cognitively expensive. ProSE models proposals simultaneously as task interventions and as active learning probes. In ProSE-Plan, a depth-2 Bayes-adaptive planner balances proposal acceptance likelihood against the information gain of learning the user's latent preferences.

### Key Finding

- **Divergence of Objectives**: Highly acceptable proposals and informative preference probes rarely coincide. Planners that only optimize for immediate acceptance systematically converge to suboptimal long-term outcomes.
- **Probe-Commit Dynamic**: Explicitly planning exploratory proposals when evaluation costs are low significantly improves downstream task alignment.

## Relevance to Praxis

- Informs interactive agent workflows (such as plan approval gates): agents should present structured, easily inspectable choices to human users to reduce cognitive evaluation fatigue while eliciting intent.
