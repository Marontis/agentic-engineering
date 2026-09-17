# ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents

> **Paper**: [ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents](https://arxiv.org/abs/2609.17523)
> **Praxis source**: `src:2609-17523v1`
> **Primary topic**: Agent Self-Improvement & Harness Engineering

## Why Not a Skill?

This paper introduces a full research workspace architecture and dual-loop self-improvement paradigm coupling harness engineering with model training. Because it requires joint infrastructure for live model reinforcement learning and application-level workspace management, it represents a system-level architecture rather than a modular agent skill.

---

## Core Concept

Scientific research agents must continuously adapt as experimental contexts, research domains, and researcher requirements evolve. Traditional systems either treat the agent as a static model behind fixed prompts or attempt end-to-end model fine-tuning without updating the surrounding execution harness.

**ScienceBuddy** introduces the **Recursive-in-Recursive Self-Improvement** paradigm, which formally decouples harness evolution from model learning:

```
Researcher Requests & Feedback
              │
              ▼
┌────────────────────────────────────────────────────────┐
│  Inner Recursion: Harness Evolution (Model Fixed)      │
│  ├── Refines prompt templates and skill documents      │
│  ├── Adapts evaluation rubrics and verification gates  │
│  └── Expands tool registry & memory indices            │
└─────────────────────────────┬──────────────────────────┘
                              │ Shapes Curated Training Data
                              ▼
┌────────────────────────────────────────────────────────┐
│  Outer Recursion: Model Reinforcement Learning         │
│  ├── Trains model parameters under evolved harness     │
│  └── Expands model reasoning frontiers                 │
└─────────────────────────────┬──────────────────────────┘
                              │ Creates New Harness Demands
                              ▼
                 Continual Discovery Loop
```

### Key Findings

- **Harness Evolution Shapes Experience**: Evolving harness tools and verification rubrics before initiating model weight updates produces significantly higher quality training trajectories and prevents shortcut learning.
- **Model Learning Drives Harness Expansion**: As model reasoning capacity expands through outer RL, existing harness abstractions become bottlenecks, creating clear signals for the next cycle of harness adaptation.
- **Benchmark Performance Across Task Families**: Evaluated across four scientific domain families (literature synthesis, hypothesis generation, experimental design, and mathematical reasoning), demonstrating continual adaptation through researcher collaboration.

## Relevance to Praxis

- Validates the separation of agent harness evolution (rules, skills, memory) from base model capabilities.
- Directly supports [`reference-trajectory-harness-evolution`](../skills/reference-trajectory-harness-evolution/SKILL.md) and [`belief-calibrated-scaffold-optimization`](../skills/belief-calibrated-scaffold-optimization/SKILL.md).
