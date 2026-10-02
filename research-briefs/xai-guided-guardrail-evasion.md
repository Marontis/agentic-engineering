# Decoding Guardrails: XAI-Guided Evasion of Prompt-Injection Classifiers

> **Source**: Outeda, Betarte, Campo & Cravero, arXiv:2609.24801, Sep 2026
> **Status**: Research Brief — exploratory case study (attack/robustness analysis of one classifier)

## Why Not a Skill?

The paper is a vulnerability analysis of one guardrail (Prompt Guard 2, 86M DeBERTa-v2 variant), built mostly on a single DAN-style prompt plus a 200-sample dataset analysis. It shows *that* token attribution makes classifier evasion cheap; it does not give a defensive procedure. The defensive takeaway (treat compact classifiers as lexical filters, not intent detectors) belongs in a rule.

## Core Concept

Compact prompt-injection classifiers sit in front of the target LLM because they are cheap. The authors use Vanilla Gradient and SHAP attributions to see which words drive Prompt Guard 2's INJECTION label, then use that ranking to guide perturbations: token removal, synonym substitution, and LLM-generated clause paraphrases. The classifier's evidence is spread across many tokens, so deleting the top words does not flip it. But confidence-guided synonym and paraphrase edits flip it while the prompt still jailbreaks the downstream model. Explanations meant for transparency lower the attacker's search cost.

## Key Findings

- **Distributed but lexical evidence**: Feature Importance Spread S_D = 0.118 (Vanilla Gradient) and 0.169 (SHAP), meaning importance is spread out rather than concentrated. Both explainers agree on the top word ("Ignore"); Jaccard over the top 18 words is 0.2857 and RBO (p=0.9) is 0.4394.
- **Deletion is inefficient**: flipping the label took 25 saliency-ordered word removals (Vanilla Gradient), 27 (SHAP), or 21 (SHAP, positive-contribution words only). Random order needed more than 50. The target LLM stopped following the jailbreak after 16 removals, 5 steps before the guardrail flipped, so deletion does not produce a working bypass.
- **Synonym substitution works**: 12 greedy, confidence-guided substitutions (24% of the text) moved P(injection) from 0.9994 to 0.4457 (BENIGN). The rewritten prompt still jailbroke Llama 3.1 8B. Choosing synonyms by lowest per-token saliency instead of lowest classifier confidence failed to flip the label after 16 substitutions.
- **Clause paraphrase works**: replacing the first 9 of 11 sentences with LLM paraphrases that avoid the 18 highest-saliency words moved confidence from 0.9994 to 0.3127. That prompt bypassed the guardrail but produced weaker jailbreak outputs (3 of 4 tasks rated Non-Functional by an LLM grader, versus 3 Partial and 1 Functional for the original prompt).
- **Coverage gap at dataset scale**: of 200 sampled injection prompts from xTRam1/safe-guard-prompt-injection, **105 were not detected**. Detected injections concentrate saliency on instruction-override and role-play words ("previous", "instructions", "ignore", "restrict"). Missed ones skew toward information-exfiltration phrasing that lacks those markers.
- **Weaker in Spanish**: a Spanish DAN prompt flipped after 7 substitutions (18% of the text), fewer than the English 12, and still jailbroke the model. The sentence-level paraphrase attack found no bypass for the Spanish prompt.

## Relevance to Praxis

- Extends the `rules/agent-sandbox-safety.md` entry "DON'T: Rely on compact guardrail classifiers without repetition compression or entropy monitoring" (Overflip, 2609.15013). That entry covers repetition attacks; this paper shows plain synonym substitution also flips the same classifier class. Repetition compression alone is insufficient.
- Supports deconfliction item **M14**: a 0%-ASR claim from a static benchmark does not survive an attacker who can query confidence scores. Pair with "DO: Test with evolving adversaries, not static attack sets" in `rules/agent-sandbox-safety.md` and the `skills/self-improving-red-team/SKILL.md` procedure.
- For injection defense on tool outputs, prefer structural controls such as `skills/pre-execution-action-auditing/SKILL.md` and `skills/verified-policy-action-governance/SKILL.md`, which do not depend on a lexical classifier recognizing the attack.
- Do not expose guardrail confidence scores or attribution maps to untrusted callers: the successful attacks used confidence as their search signal.
- Limits: one classifier, one hand-picked English prompt and one Spanish prompt for the perturbation experiments, and LLM-graded jailbreak usefulness. Treat the percentages as illustrative, not as population rates.

> Source: Outeda et al., "Decoding Guardrails: XAI-Guided Perturbation Analysis of Prompt Injection Detection" (arXiv:2609.24801)
