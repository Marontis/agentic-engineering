# Dalek: A Constructive Agent Machine

> **Paper**: [Dalek: A Constructive Agent Machine](https://arxiv.org/abs/2609.03546)  
> **Praxis source**: `src:2609-03546`

## Why Not a Skill?

*Dalek* establishes theoretical foundations and machine-level closure for self-maintaining, self-reproducing, and self-evolving agents, adapting John von Neumann's 1948 self-reproducing automata architecture to LLM-driven execution environments. Because it formalizes complete computational machine models rather than an on-demand subtask procedure, its host contracts and heredity boundaries are codified as architectural rules in `rules/agent-sandbox-safety.md`.

---

## Core Concept

Modern autonomous agents frequently perform self-modification, runtime tool synthesis, and recursive scaffolding refinement. However, existing implementations lack a rigorous formal closure: self-modifications are often ad-hoc prompt overwrites or unbounded code generation without explicit boundaries, identity invariants, or hereditary rules.

*Dalek* introduces a closed constructive machine for AI agents built from three primitives:
1. **Actors**: Autonomous entities possessing internal state and executable logic.
2. **Messages**: Structured information units passed between actors.
3. **Channels**: Controlled communication routes governing interaction.

### Von Neumann's Hereditary Core in Agent Form

Drawing directly from John von Neumann's 1948 theory of self-reproducing automata, Dalek separates the constructive core into four interdependent components:
- **Self-Description**: An explicit, serialized model of the agent's architecture, dependencies, state schema, and behavioral policies.
- **Constructor**: A capability producer (composed of an LLM and a compiler/harness) that reads descriptions and constructs executable actor instances.
- **Copier**: A mechanism that duplicates the self-description without execution, preserving lineage integrity.
- **Controller**: An execution scheduler that coordinates reproduction, mutation gating, and lifecycle transitions.

### The Four Host Obligations

To realize safe, bounded self-evolution, Dalek proves that any host substrate (OS, sandbox, container) must satisfy four structural host obligations:

1. **Host Boundary**: An inviolable isolation perimeter that prevents unmediated escape into host infrastructure.
2. **Construction Language**: A formalized domain-specific or safe general-purpose language through which new actor organs and capabilities are compiled and verified.
3. **Admissible Transitions**: An explicit state machine of allowable agent state mutations, forbidding undefined or non-deterministic transition states.
4. **Rule Heredity**: Descendant agents or evolved iterations MUST inherit the baseline safety constraints and governance rules of their parent lineages; an agent cannot evolve away its own supervisory contracts.

---

## Relevance to Praxis

- **Evolution Sandboxing**: Provides the formal framework for autonomous skill generation and recursive agent improvement, ensuring that newly synthesized tools or modified prompts inherit system safety invariants.
- **Agent Lineage Tracking**: Praxis change sets (`chg:...`) and source capture trees directly implement the hereditary self-description and provenance tracking demanded by constructive agent machines.
