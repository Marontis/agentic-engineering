# CounterSteer: Activation Steering on Tool-Result Spans Against Indirect Prompt Injection

> **Source**: Russinovich, "CounterSteer: Suppressing Indirect Prompt
> Injection with Activation Steering", [arXiv:2609.36570](https://arxiv.org/abs/2609.36570), Sep 2026
> **Status**: Research Brief, inference-time defense for self-hosted
> open-weight models (five models, 8B to about 106B parameters).

## Why Not a Skill?

The method needs white-box access to the served model's residual stream,
per-model fitting (about 1-2.3 hours, mostly evaluation) and a serving
stack that can edit activations on tagged spans. Most teams using hosted
APIs cannot run it. What transfers widely is where it fails, and how the
paper separates a detector from a defense.

## Core Concept

Fit a direction in the residual stream from paired episodes that differ
only in whether an embedded instruction is followed (difference in means,
not a discriminative probe). At serving time, during prefill only,
subtract that direction from every token inside tool-result spans at a few
layers, with a norm-preserving rotation. User turns and decoded tokens are
untouched. No extra model calls or tokens are added; prefill latency was
0.181 s versus 0.182 s unsteered.

## Key Findings

- **Headline**: held-out attack success fell from 0.21-1.00 undefended to
  0.00-0.17, and AgentDojo compromise from 0.10-0.49 to 0.006-0.079, at
  93-100% typography-normalized benign utility.
- **Against other inference-time defenses** (AgentDojo, gpt-oss-20b):
  CounterSteer compromise 0.091 at 90.6% benign utility; CachePrune 0.216
  at 88.7%; PromptGuard-2 0.205 at 100.0%; AGRI 0.062 at 78.0%; PIGuard
  0.011 at 58.2%. Fine-tuned SecAlign had 90.4% benign utility. The
  defenses with lower compromise paid in utility or required retraining.
- **Adaptive attackers**: an AutoDojo attacker reaching 0.67-0.73
  undefended was held to 0.175 and 0.188 on the two primary models.
  White-box gradient attacks through the exact deployed vector compromised
  at most 2 of 52 episodes. Replaying the successful LLMail-Inject texts
  (2,052 episodes) went from 128/2052 undefended to 0/2052 on gpt-oss-20b.
- **Parameter manipulation is the open gap.** When the injection changes a
  tool argument rather than taking over the task, a framing search cracked
  13/18 samples (3/18 for tool hijack). The paper reports that every
  inference-time defense it measured shares this weakness; fine-tuned
  SecAlign held the same search to 1/18. Mechanistically, the decision
  was not linearly decodable before generation but was at the point the
  value is emitted: the model quotes the injected value and adopts it
  through its own reasoning.
- **Detection is not defense.** A direction that separated attacks cleanly
  left attack success unchanged under steering (0.299 versus 0.303): it
  encoded the outcome, not the cause. Only a causal (steering) test showed
  which directions work.
- **Costs**: benign utility 94.1-94.4% on the primary models; instruction
  following on steered content degraded unevenly (IFEval -15.2 pp at the
  deployed dose on gpt-oss-20b; GSM8K unchanged).

## Relevance to Praxis

- **Compose with argument provenance.** The author describes CounterSteer
  as an instructional-takeover component, not a complete solution, to be
  composed with argument-provenance controls. The same holds for any
  model-side injection defense: check that each sensitive tool argument
  traces to the user's request or trusted data, deterministically and
  outside the model. See
  [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md),
  [`necessary-tool-evidence-path`](../skills/necessary-tool-evidence-path/SKILL.md)
  and `rules/agent-sandbox-safety.md` "Audit agent tool invocations
  against localized evidence spans before dispatch".
- **Validate probes causally.** A probe or classifier that separates
  attacks on held-out data can still be useless as a lever. This adds to
  `rules/agent-sandbox-safety.md` "Treat compact prompt-injection
  classifiers as intent detectors, or expose their scores".
- **Measure benign cost on instruction-following, not only task
  success**, per `rules/agent-sandbox-safety.md` "Measure each defense's
  benign cost on a matched benign arm, on the assembled stack".
- Related: [active-adaptation-preventative-steering](active-adaptation-preventative-steering.md)
  (steering as a training-time defense).

> Source: CounterSteer: Suppressing Indirect Prompt Injection with Activation Steering (arXiv:2609.36570)
