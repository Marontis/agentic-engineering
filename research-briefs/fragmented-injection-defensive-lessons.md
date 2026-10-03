# Fragmented Indirect Prompt Injection: Defensive Lessons

> **Paper**: [Divide and Inject: Can Agents Reconstruct an Indirect Prompt Injection from Fragments?](https://arxiv.org/abs/2609.36576)
> **Praxis source**: src:2609-36576v1
> **Status**: Research Brief, defensive lessons only. Attack construction,
> payloads and optimization details are deliberately omitted.

## Why Not a Skill?

The paper is an attack study and evaluates no defenses. What transfers is
a threat-model correction for defenders: an injected objective need not
appear anywhere as a complete instruction.

---

## Core Concept

Instead of one explicit injected instruction, the adversarial objective is
split into incomplete fragments spread through long retrieved content, and
the agent's own ability to gather and combine information assembles them.
No single fragment looks like an instruction, so defenses that look for an
explicit directive in one piece of text have nothing to match.

### Key Findings

- **Setup**: seven models; three tool environments (Email, GitHub,
  Slack), three benign tasks and 27 task-objective pairs per environment.
- **Adaptive fragmentation works; naive fragmentation doesn't**: macro ASR
  61.4% with adaptation at 8k filler tokens, versus 5.1% for long-context
  fragmentation without adaptation. Baselines: a Trojan-Hippo-style attack
  32.8%, AgentVigil 30.0%, TAP 26.3%.
- **Large spread across models**: ASR 8.6% (GPT-5.6-Luna), 58.0%
  (GPT-4.1), 61.7% (Ministral-3-14B), 65.4% (GPT-5.1), 71.6%
  (Qwen-3.6-27B), 72.8% (Muse-Glimmer-30B), 91.4% (Gemma-4-31B).
- **Attacks don't look like failures**: benign tasks were still completed
  49.4% of the time under attack.
- **No defenses were evaluated.** Limitations: seven models, three
  environments, black-box query access assumed during attack optimization.

## Defensive Takeaways

- **Don't rely on per-chunk injection detectors.** A detector that scores
  each document or tool output alone cannot see an objective that only
  exists after combination. Treat such classifiers as one layer (see
  `rules/agent-sandbox-safety.md` "Treat compact prompt-injection
  classifiers as intent detectors, or expose their scores").
- **Authorize at the action, not the content.** Whatever the agent
  reconstructs, it has to act through a tool call. Checks that tie each
  call and argument to the user's request catch the result regardless of
  how it was assembled: [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md),
  [`poisoned-skill-tool-call-authorization`](../skills/poisoned-skill-tool-call-authorization/SKILL.md),
  and deterministic permission enforcement below them.
- **Add fragmented and long-context cases to red-team suites**, alongside
  explicit injections, and report per model: one model's 8.6% says
  nothing about another's 91.4%. Use evolving rather than static attack
  sets ("Test with evolving adversaries, not static attack sets").
- **Task completion is not a health signal.** About half of attacked runs
  still completed the user's task, so monitor side effects and tool calls,
  not only task outcome.

## Relevance to Praxis

- Extends the indirect-injection threat model used by the sandbox rules;
  conflicts with no existing rule.
- Strengthens the case for action-level authorization over content
  filtering as the primary injection defense.

> Source: Divide and Inject: Can Agents Reconstruct an Indirect Prompt Injection from Fragments? (arXiv:2609.36576)
