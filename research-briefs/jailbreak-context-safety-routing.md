# Jailbreak Context Lingers: Divergent Safety Routing in Tool Agents

> **Paper**: [Jailbreak Context Lingers: Divergent Safety Routing and Its Cross-Task Predictability in Tool Agents](https://arxiv.org/abs/2609.34686)
> **Praxis source**: src:2609-34686v1
> **Status**: Research Brief, defensive lessons only. No jailbreak content is reproduced here.

## Why Not a Skill?

The paper is a measurement and interpretability study: it shows how a
generic safety reminder behaves once jailbreak context is already in a tool
agent's history, and locates where the decision forms inside the model. The
predictive probes need white-box activation access and reach modest AUCs,
so there is no procedure ready to transfer.

---

## Core Concept

A common fallback is: if an agent may have been jailbroken, append safety
feedback before its next action. The paper compares paired continuations
resumed from the same frozen checkpoint, one with a neutral reminder (N)
and one with safety feedback (S) asking the agent to check whether the
next actions could harm others or exceed the task's permissions. The same
feedback routes agents three ways:

- **Rescue**: an unsafe trajectory is redirected to legitimate completion.
- **Persistent unsafe**: the agent keeps executing the unauthorized action.
- **Collateral loss**: the agent over-refuses legitimate work.

### Key Findings

- **Setup**: 192 parent tasks across 42 domains with deterministic
  simulator oracles; 12,288 designed N/S pairs (12,148 analyzed); eight
  open-weight agents from four families (Qwen, Gemma, Llama, Mistral).
- **Routing is model-dependent, not scale-dependent.** Persistent-unsafe
  rates ranged from 1.0% (Qwen3.6-27B) to 85.7% (Qwen3-14B) within one
  family. Rescue ranged from 0.5% (Qwen3-14B) to 19.3% (Gemma-3-12B).
  Collateral loss reached 13.1% (Mistral-Small-24B) and 10.9%
  (Gemma-3-12B).
- **Late commit**: activation-patching effects stay small through most of
  the network and surge near the final layers (relative depth
  0.958–0.984), with a 30-fold spread in peak magnitude across models.
  Patching those layers changed the next tool action in 6/8 agents for
  rescue, 6/7 for collateral loss and 7/8 for persistent unsafe.
- **Prediction is weak but real**: leave-one-parent-task-out peak ROC AUC
  0.675 (rescue), 0.777 (collateral loss), 0.702 (persistent unsafe).
  Critical-layer features beat baseline layers in 21 of 24 comparisons.
- **Limitations**: open-weight models only; simulated environments;
  prediction degrades when positive outcomes are very rare; cross-family
  transfer of probes not tested.

## Defensive Takeaways

- **A safety reminder is not a recovery mechanism.** For some models it
  rescues almost nothing and leaves most unsafe trajectories running. Once
  untrusted or adversarial content has entered the context, enforce
  permissions outside the model (see `rules/agent-sandbox-safety.md`
  "Rely on structured LLM authorization decisions as the sole safety
  gate") or reset to a clean context, rather than appending feedback.
- **Measure all three outcomes per deployed model.** Report rescue,
  persistent unsafe and collateral loss on matched benign/risky pairs;
  a model that refuses everything after feedback looks safe on attack
  metrics alone. This matches "Measure each defense's benign cost on a
  matched benign arm, on the assembled stack" in the same rules file.
- **Don't infer a model's behaviour from its family or size.** Evidence
  for `rules/agent-sandbox-safety.md` "Assume model scale implies safety
  robustness" and "Assume uniform safety refusal behavior across model
  families in multi-turn dialogues".
- **Lingering context is a trajectory property.** Supports "Rely on
  single-turn refusal or initial benign turns to evaluate long-horizon
  safety".

## Relevance to Praxis

- Adds tool-agent evidence to existing per-model and trajectory-level
  safety rules; introduces no conflicting rule.
- White-box late-layer probes may become a monitoring signal for
  open-weight deployments, but at AUC 0.68–0.78 they are not a gate.

> Source: Jailbreak Context Lingers: Divergent Safety Routing and Its Cross-Task Predictability in Tool Agents (arXiv:2609.34686)
