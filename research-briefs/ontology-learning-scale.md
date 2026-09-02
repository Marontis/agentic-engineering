# When Does Bigger Help? A Controlled Study of LLM Scale for Ontology Learning

> **Paper**: [When Does Bigger Help? A Controlled Study of LLM Scale for Ontology Learning](https://arxiv.org/abs/2608.31118)
> **Praxis source**: `src:2608-31118v1`

## Why Not a Skill?

Empirical study â€” controlled study of how model scale affects ontology extraction tasks. Findings are informative but not procedural.

---

## Core Concept

Bigger LLMs don't uniformly improve ontology extraction. Scale helps for relation extraction (detecting that two concepts are related and how) but not for taxonomy induction (organizing concepts into hierarchies). The finding challenges the assumption that scaling improves all knowledge extraction tasks.

### Key Finding

Taxonomy induction requires structural reasoning (parent-child relationships, is-a hierarchies) that doesn't improve with scale the way pattern matching does. Relation extraction benefits from scale because larger models have seen more diverse relation patterns.

## Relevance to Praxis

- Informs how Praxis builds its SkillGraph â€” relation extraction between sources is scale-sensitive, but the graph's hierarchical organization is not
- Relevant to the governed-knowledge-graph skill's entity/relation type induction step
