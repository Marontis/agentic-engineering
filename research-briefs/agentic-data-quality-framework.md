# ACE Lens: Agentic Data Quality Framework

> **Paper**: [What Makes Good Agentic Data? An ACE Lens on Data Generation for LLM Agents](https://arxiv.org/abs/2608.27260)
> **Authors**: Zeng, Xu, Zhang, Wu, Wang, et al. (Huawei / SJTU / Northwestern / HIT)
> **Praxis source**: `src:2608-27260`

## Why Not a Skill?

This paper is primarily a survey and framework contribution. The ACE lens provides valuable *vocabulary* for reasoning about data quality, and the (E, q, τ, v) factorization is a useful *representation* — but neither constitutes a transferable subtask-level procedure that an agent could execute. The individual techniques (execution-grounded verification, learner-relative calibration, coverage balancing) are each too domain-specific to extract as standalone skills.

The ACE *rules* have been added to [`skill-system-design.md`](../rules/skill-system-design.md).

---

## Core Framework

### The Data Object: (E, q, τ, v)

Agentic data is factorized as a 4-tuple:
- **E** (Environment): the actionable world — state, dynamics, policies, action/observation interfaces
- **q** (Task signal): the task-conditioned objective and constraints
- **τ** (Trajectory): the realized interaction — actions, observations, state changes
- **v** (Verifier): optional outcome- or process-level supervision — executable checks, model judgments, rewards

This factorization is domain-independent. API-calling agents, GUI agents, coding agents, and embodied agents all produce data expressible as (E, q, τ, v).

### The ACE Lens

Three properties determine whether generated agentic experience is useful for learning:

**Accuracy** — hard constraint on the feasible support:
- Factor-level validity: is each of E, q, τ, v individually well-formed?
- Relational consistency: are the factors internally consistent with each other?
- Execution grounding: can τ actually be replayed in E?

**Complexity** — where to place probability mass within the feasible support:
- Learner-relative: difficulty calibrated to the current agent's capability, not fixed
- Not just task difficulty — includes environment complexity, interaction length, information structure
- The goal is to maximize learning value, not difficulty per se

**divErsity** — how broadly mass covers the space:
- Non-redundant coverage across environments, tasks, and interaction behaviors
- Behavioral diversity (different strategies for the same task) matters as much as task diversity
- Volume alone doesn't help — 1000 redundant trajectories < 100 diverse ones

### Asymmetry

Accuracy is asymmetric with respect to complexity and diversity: invalid data cannot be compensated by being difficult or diverse. But valid data that is trivial or repetitive has low learning value. Accuracy constrains the support; complexity and diversity shape the distribution within it.

---

## Generation Paradigms

### Forward Pipeline (E → q → τ)
Start from an existing environment, generate tasks grounded in it, collect trajectories via agent execution or demonstration. Accuracy is easier to guarantee (environment already exists) but diversity is constrained by the environment inventory.

### Reverse Pipeline (τ → q → E)
Start from desired trajectories or task descriptions, then construct or infer the environment that would support them. More flexible for diversity but harder to ensure accuracy — the synthetic environment may not behave as expected.

---

## Key Findings from the Literature Review

- The field is shifting toward **execution-grounded accuracy** — actually running the agent in the environment rather than just checking output format
- **Learner-relative complexity** is replacing fixed difficulty tiers — the same task may be trivially easy for one model and impossibly hard for another
- Diversity beyond surface variation matters: behavioral coverage (different strategies) is underexplored relative to task coverage
- The biggest gap: few systems measure or optimize for ACE jointly — most papers address one dimension in isolation

---

## Relevance to Praxis

The ACE vocabulary applies to Praxis's quality gates:
- **Accuracy ↔ credibility scoring + conflict ledger**: ensuring ingested sources are grounded and consistent
- **Complexity ↔ capability-aware skill selection**: matching skill difficulty to agent capability
- **Diversity ↔ coverage audit**: ensuring the skill library covers distinct capabilities without redundancy

The (E, q, τ, v) factorization could inform how Praxis structures evidence records — currently, evidence is a flat record; separating environment context, task intent, interaction trace, and verification signal would make the evidence more structured and queryable.
