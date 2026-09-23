# Harness-Zero: Harness Distillation via Agent-as-Harness

**Source**: Ye et al., "Harness-Zero: Harness Distillation via
Agent-as-Harness" (arXiv:2609.24974), Sep 2026.

## Key Findings

- Agent harness gains are tied to the harness at deployment; best
  harness varies across domains, instances, and models
- Harness distillation transfers harness-induced behaviors into model
  weights via agent-as-harness (a harnessing agent corrects student
  responses before execution)
- With specialized harness removed at deployment, Harness-Zero improves
  base model success from 23.3% to 44.3%, exceeding the 41.7% with
  harness still attached
- 82.3% average recovery of harness-induced behaviors across 28 patterns
  in knowledge work, tool use, and science domains
- Agent-as-harness outperforms code-as-harness for frontier LLMs

## Relevance to Agentic Engineering

Harness-Zero demonstrates that the best harness behaviors can be
internalized into model weights, eliminating harness dependency at
deployment. The agent-as-harness pattern (using a harnessing agent to
translate guidance into training demonstrations in the target harness's
action space) is a novel approach to skill transfer.

## Why Not a Skill?

Training-pipeline-specific: requires fine-tuning infrastructure to
internalize harness behaviors. The insight about agent-as-harness vs
code-as-harness is valuable context, but the procedure isn't
transferable without a fine-tuning setup.

> Source: arXiv:2609.24974
