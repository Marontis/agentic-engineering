# Render Before Reading: Untrusted Content as Images Against Prompt Injection

> **Paper**: [Render Before Reading: Visual Rendering as a Prompt Injection Defense](https://arxiv.org/abs/2609.36121)
> **Authors**: Zhang, Baroian, van Rijn, Shafran, Tramèr
> **Praxis source**: src:2609-36121v1
> **Status**: Research Brief — defense evaluation

## Why Not a Skill?

The procedure is one step (render untrusted text as typographic images and
send it to a vision-language model), so it does not need a skill. Its value
is in the measurements: where the defense holds, where it costs utility, and
why it works at all, which tells you whether to add it to your stack.

---

## Core Concept

Vision-language models act on instructions written inside an image far less
often than on the same instructions given as text, even when they read the
image text correctly. The paper attributes this to instruction tuning that
teaches imperatives mostly through text. The **Pictionary** defense uses the
gap: trusted inputs (system prompt, user query) stay text; untrusted inputs
(retrieved documents, tool outputs) are rendered as images. This creates an
instruction hierarchy by channel without filtering or paraphrasing.

Threat model: the attacker controls one untrusted channel, has black-box
access, and uses text payloads. Attacks that are images already are out of
scope.

## Key Findings

- **The gap is large but uneven**: across ten VLMs, models were "between 2×
  and 300× less likely" to act on image-rendered instructions than on the
  same text.
- **Static attacks**: DirectInject ASR fell from 75.0% to 0.0% for GPT-5.4
  mini and 17.9% to 0.0% for Claude Haiku; AgentDojo ASR fell from 83.1% to
  41.5% for Gemini 3.1 Pro and 29.2% to 7.7% for GPT-5.4 mini.
- **Adaptive attacks** (union of RL, automated red teaming and human red
  teaming, AgentDojo banking): Claude Haiku 4.5 97.6% → 9.5%, GPT-5.4 mini
  83.3% → 31.0%, Kimi-K2.6 77.8% → 40.0%, but **Gemini 3.1 Flash Lite
  100.0% → 97.8%**. The defense depends on the model.
- **Against three discovered attack templates** (ASR / utility): no defense
  82.1 / 98 vs Pictionary 3.6 / 100 for GPT-5.4 mini; 87.5 / 99 vs 3.6 / 100
  for GPT-5.4; 71.4 / 96 vs 3.6 / 99 for Kimi-K2.6.
- **Utility**: DirectInject loss ≤1.3 points; AgentDojo change between −14.4
  and +9.7 points; τ²-Bench small (Kimi-K2.6 87.2% → 85.9%). **Code editing
  suffers**: on SWE-bench Verified some models lost 9–10 points because OCR
  errors break exact character sequences (Kimi-K2.6 unchanged at 65.0%).
- **Cost**: image input bills at roughly 10× the token cost of the same text,
  but in the paper's agent settings, where system prompts and tool schemas
  dominate context, total serving cost "never more than doubles".
- **Same effect in audio**: GPT-Audio-Mini 27.3% → 1.3%, Qwen3.5-Omni-Plus
  50.5% → 15.8%, consistent with a channel asymmetry rather than a vision
  quirk.
- **The gap is learned, so it can close**: fine-tuning on benign
  image-rendered instructions raised image-channel ASR by 13–19 points.

## Defensive Lessons

1. **Treat this as one layer, not a boundary.** One model stayed ~98%
   compromised under adaptive attack, and future instruction tuning that
   includes image instructions will shrink the gap. Re-measure per model
   and per model version.
2. **Do not render code or exact-match content.** Use it for prose-heavy
   channels (documents, web pages, emails, tool output that the model reads
   rather than copies). Keep diffs, file contents and identifiers as text.
3. **No protection for content that is already visual** (screenshots, PDFs,
   GUI viewports), so computer-use agents get nothing from it.
4. **Measure on the assembled stack.** The paper compares single defenses;
   it does not measure stacking. Apply "DON'T: Assume stacked defense layers
   fail independently" and "DO: Measure each defense's benign cost on a
   matched benign arm, on the assembled stack"
   (`rules/agent-sandbox-safety.md`) before adding it.

## Relevance to Praxis

- Complements text-side defenses such as
  [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md)
  and "DO: Sanitize all tool outputs before injecting into agent context"
  (`rules/agent-sandbox-safety.md`): rendering changes the channel, those
  check content and actions.
- Related multimodal measurements:
  [`multimodal-prompt-injection-eval`](multimodal-prompt-injection-eval.md).

> Source: Zhang et al., "Render Before Reading: Visual Rendering as a Prompt
> Injection Defense" (arXiv:2609.36121)
