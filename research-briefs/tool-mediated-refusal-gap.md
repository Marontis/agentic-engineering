# Tool Mediation Lowers and Weakens Refusal

> **Paper**: [Tool Mediation Alters Refusal Mechanisms in Large Language Models](https://arxiv.org/abs/2609.35117)
> **Praxis source**: src:2609-35117v1
> **Status**: Research Brief. Mechanistic and behavioural measurement study.

## Why Not a Skill?

The paper measures and explains a gap; it does not propose a defense
procedure. What transfers is an evaluation requirement (test refusal
through the tool interface you deploy) and a threat-model fact (tool
exposure alone erodes refusal), both of which belong in rules.

## Core Concept

The same harmful AgentHarm intent is rendered in five matched,
cumulative conditions: a conversational reference (free text, no
tools), agentic framing (a tool-use system prompt, no tools), two
tool-exposure conditions (seven generic tools plus the intent's target
function are visible, the model is still told to answer in prose), and
tool action (an explicit directive to call the tool). Refusal falls as
the request moves toward tool use, and the fall starts at **exposure**,
before the model is told to act.

Harm stays decodable inside the model in both channels. What changes is
the conversion of harm into refusal: at matched harm readouts the tool
channel applies a higher refusal threshold, and its refusal is easier to
break.

## Key Findings

Setting: eight open-weight instruction-tuned models (Qwen3-8B/32B,
Llama-3.1-8B/70B, Ministral-3-8B, Gemma-4-12B/31B, gpt-oss-20b),
8B to 70B, thinking modes disabled; AgentHarm public test behaviors,
prompts with tool hints filtered out, three directive phrasings per
intent. Tool-channel compliance is parsed from tool calls; the
conversational channel is judged by Qwen3Guard-Gen-4B.

- **Refusal drop (Table 2)**: reference to tool action, refusal falls
  in all eight models by 15.5 to 84.4 points. Examples: Llama-3.1-8B
  0.941 to 0.096; Qwen3-32B 0.968 to 0.295; Llama-3.1-70B 0.892 to
  0.607; Gemma-4-12B 0.935 to 0.780 (smallest drop).
- **Framing alone does little**: agentic framing changed refusal by
  -0.024 to +0.082, mostly not significant.
- **Exposure is enough to start the drop**: tool exposure accounts for
  35-88% of the final drop with the regular agentic prompt, and 23-62%
  when the instruction to emit tool calls is stripped.
- **Conversational scores don't rank tool behaviour**: conversational
  refusal is near-saturated and tightly clustered while tool-action
  refusal spans most of the unit interval; the two orderings correspond
  only weakly.
- **Different thresholds, same harm signal**: a conversational harm
  direction reaches AUROC 0.758-0.913 on tool-mediated representations
  (0.732-0.941 the other way), but among the least-harmful third of
  intents the refusal-rate difference between channels is 0.43-0.98; the tool threshold sits inside the harmful-intent
  distribution in all eight models, the conversational one below it in
  five of eight.
- **Partly distinct circuitry**: in all seven dense models, ablating a
  channel's own selected neurons reduces its harm projection more than
  ablating the other channel's neurons or a matched random set.
- **Tool refusal is more brittle (Table 4, GCG, same budget, prompts
  refused in both channels, 8-12 per model)**: broken within 40 steps
  in the tool channel versus the conversational channel: Qwen3-8B 92%
  vs 25%, Qwen3-32B 92% vs 8%, Llama-3.1-8B 83% vs 0%, Llama-3.1-70B
  100% vs 0%, Ministral-3-8B 100% vs 92%, Gemma-4-12B 20% vs 0%,
  Gemma-4-31B 25% vs 0%. Directional ablation shows the same ordering
  (the authors call this suggestive).
- **Replication on privacy**: on a smaller PrivacyLens evaluation of
  authorization violations the refusal drop also appears, though its
  size differs by model and is not significant for gpt-oss-20b.

**Limitations stated by the authors**: open-weight models only, no
reasoning modes; mechanistic results do not carry over cleanly to the
MoE model; different compliance criteria per channel (parser vs LLM
judge); AgentHarm may not reflect real deployments; the origin of the
gap (pretraining, tuning, safety or tool-use training) is unknown.

## Relevance to Praxis

- **Evaluate refusal through the deployed tool interface.** A
  conversational safety score says little about whether the same model
  will execute the request once the tool is visible. Run red-team and
  refusal suites with the real tool schemas exposed (see
  `skills/closed-loop-adaptive-red-teaming/SKILL.md`, which already runs
  tool-using targets against mock tools).
- **Exposure is itself a risk factor.** Showing a model a capable tool
  lowers refusal before any instruction to use it. This supports
  exposing only the tools a task needs, but tool hiding is not access
  control: enforcement stays server-side (rules/agent-sandbox-safety.md,
  "Treat tool hiding, specialist prompts or roster delegation as access
  control").
- **Don't rely on model refusal as the boundary for tool actions.** Tool
  refusal is weaker at baseline and breaks under smaller perturbations;
  authorization and action gates have to sit outside the model.
- Evidence for rules/agent-sandbox-safety.md, "Assume safety transfers
  across deployment contexts".

> Source: Tool Mediation Alters Refusal Mechanisms in Large Language Models (arXiv:2609.35117)
