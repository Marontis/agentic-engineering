# Knowledge-Conditioned Topology for Multi-Agent Systems

> **Paper**: [When Evidence Shapes Collaboration: Knowledge-Conditioned Topology Generation for Multi-Agent Systems](https://arxiv.org/abs/2608.27984)
> **Praxis source**: `src:2608-27984v1`

## Why Not a Skill?

The procedures (evidence-driven topology generation, curriculum learning for
topology training, knowledge-grounded verification) are tightly coupled to
a training pipeline with specific model architecture requirements (topology
decoder, curriculum optimizer). These don't decompose into transferable
subtask procedures for general agent engineering.

---

## Core Concept

Instead of using a fixed multi-agent topology (chain, star, debate), dynamically
generate the collaboration topology based on evidence retrieved from a knowledge
graph. The topology decoder receives the task query + retrieved evidence and
outputs which agents should communicate with which other agents.

### Key Components

1. **Evidence-Driven Topology Generation**: Query a KG, retrieve relevant
   evidence, and condition the topology on that evidence. Different evidence
   produces different collaboration structures.

2. **Curriculum Learning Framework**: Train the topology generator using
   progressively harder tasks. Start with simple topologies and gradually
   increase complexity as the model improves.

3. **Dynamic Inference and Execution**: At inference time, generate the
   topology on-the-fly based on the current task and evidence, then execute
   the multi-agent workflow according to that topology.

4. **Knowledge-Grounded Verification**: Use the KG evidence to verify agent
   outputs — check whether the generated answer is consistent with the
   retrieved knowledge.

---

## Relevance to Praxis

- The **evidence-conditioned topology** pattern is interesting for Praxis's
  own graph traversal: the structure of the search could adapt based on what's
  found, rather than following a fixed traversal pattern.
- **Knowledge-grounded verification** has direct parallels to Praxis's conflict
  detection: both use structured knowledge to validate outputs.
- The **curriculum learning** approach could inform how Praxis progressively
  introduces complexity in skill evolution (simple skills first, then compound).
