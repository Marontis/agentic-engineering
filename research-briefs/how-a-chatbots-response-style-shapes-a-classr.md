# How a Chatbot's Response Style Shapes a Classroom

> **Paper**: [How a Chatbot's Response Style Shapes a Classroom: A Multi-Agent Simulation of Students Consulting AI](https://arxiv.org/abs/2609.05018)
> **Praxis source**: src:2609-05018

## Why Not a Skill?

This paper is a simulation study examining how different chatbot response styles affect student psychological states over time. It provides empirical findings about AI dependency dynamics but no transferable subtask-level procedure for agent design.

---

## Core Concept

The paper builds a virtual classroom with 20 student agents that interact through rule-based chats and, when stressed, consult either a friend or a counselor AI (Gemini 2.5 Flash). Each agent carries five state variables (stress, happiness, self-reliance, AI dependence, sociability). The counselor is given six response styles via system prompts: affirming, listening, solution-oriented, reality-redirecting, inciting, and blaming. A second LLM call acts as an evaluator that converts each consultation into parameter updates without seeing the style prompt.

### Key Finding

- **Primary Result**: Affirming and listening styles increase AI dependence and reduce self-reliance over 15-50 simulated days. Solution-oriented and reality-redirecting styles maintain higher self-reliance.
- **Secondary Result**: Ablation confirms that chatbot response style, not mere availability of AI consultation, drives the divergence in student psychological trajectories. The no-AI control group shows different but not necessarily better outcomes.

## Relevance to Praxis

- **Agent response design**: When building conversational agents, response style has measurable downstream effects on user dependency. Solution-oriented responses preserve user autonomy better than affirming/empathetic defaults.
- **Multi-agent simulation methodology**: The five-variable state model with LLM-as-evaluator pattern is a reusable simulation architecture for studying emergent multi-agent dynamics.
