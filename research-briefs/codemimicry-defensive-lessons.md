# CodeMimicry: Defensive Lessons on Safety Lag in the Code Domain

> **Source**: CodeMimicry: Exploiting Safety Generalization Lag in Large Language Models via Structured Code Completion, [arXiv:2609.39902](https://arxiv.org/abs/2609.39902)
> **Status**: Research Brief, defensive lessons only. The paper presents a
> jailbreak; this brief records what it teaches defenders and deliberately
> omits attack procedures (see the repo's `AGENTS.md`).

## Why Not a Skill?

The paper's contribution is an attack. What transfers is a measurement of
which defenses hold when harmful requests arrive as code-completion inputs,
which matters for coding agents that read untrusted repositories.

## Core Concept

**Safety generalization lag**: safety alignment trained mostly on natural
language transfers poorly to structured code. A request framed as a code
completion task, with the harmful intent carried in code-level side
channels such as comments and docstrings, is refused far less often than
the same request in prose. The authors expect the gap to grow as code
ability improves faster than code-domain safety.

## Key Findings

- **Headline**: 96.25% average attack success on AdvBench (1.51 queries
  on average) and 96.07% on HarmBench (1.46 queries), across eight
  commercial and open models (GPT-4o, GPT-4.1, GPT-5-chat,
  Claude-3.7-Sonnet, Claude-Sonnet-4, Gemini-2.5-Pro, Llama-3.1-70B,
  Llama-3.3-70B-Instruct).
- **Input classifiers largely fail**: Llama Guard and a perplexity filter
  left most attacks through on the tested models; SelfDefend blocked most.
  (Per-model figures were not verified for this brief.)
- **Reasoning-based alignment varies**: on DeepSeek-R1-8B, attack success
  stayed at 94% under SafeChain and 42% under SafePath.
- **Representation-level defenses did best among alignment methods**: on
  Llama-3-8B, Circuit Breaker reduced attack success from 90% to 8%;
  Representation Bending to 38%.
- **Cheap input hygiene helps**: filtering comments and docstrings from the
  input substantially reduced success (exact figure not verified here).
  Adversarial fine-tuning on 500 examples reduced it from 90% to 62%.
- **Limitations stated by the authors**: needs a target with strong code
  generation and instruction following; depends on string-level side
  channels, chiefly comments and docstrings.

## Defensive Takeaways

- **Treat code comments and docstrings in untrusted repositories as
  untrusted instructions.** Coding agents consume them as context; this is
  the same channel the attack uses. Apply `rules/agent-sandbox-safety.md`
  "DO: Sanitize all tool outputs before injecting into agent context" to
  file reads, and consider stripping or quarantining comments when the task
  doesn't need them.
- **Don't rely on a natural-language safety classifier alone for code
  inputs.** Its training distribution is prose. Layer it with a different
  defense class ("DO: Select defense layers from different cost classes",
  "DON'T: Assume stacked defense layers fail independently").
- **Red-team in the code domain.** A model's refusal rate on prose
  benchmarks says little about code-framed requests; add code-completion
  variants to safety evaluations
  ([`taxonomy-driven-red-teaming`](../skills/taxonomy-driven-red-teaming/SKILL.md)).
- **Output-side checks still matter**: when inputs can't be cleaned,
  enforce what the agent may execute or publish at the runtime boundary,
  not by refusal alone.

> Source: CodeMimicry: Exploiting Safety Generalization Lag in Large Language Models via Structured Code Completion (arXiv:2609.39902)
