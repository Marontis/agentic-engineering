# Gradient-Based Jailbreak Detection in Multi-Turn Dialogue

> **Source**: Sheta, Deuja, Masoudi, Fang, "Does the Unsafe Gradient Survive a Conversation? On the Fragility of Gradient-Based Jailbreak Detection in Multi-Turn Dialogue", [arXiv:2609.36849](https://arxiv.org/abs/2609.36849), Sep 2026 (LAMPS '26)
> **Status**: Research Brief, defensive evaluation study. Read from the PDF
> (no HTML version).

## Why Not a Skill?

The paper does not propose a deployable detector. Its Context Window
Scanner (score sliding windows of user turns with GradSafe, take the
maximum) is deliberately minimal and needs white-box gradients. The value is
in how the evaluation changes once benign data is realistic.

## Core Concept

GradSafe scores a prompt by the cosine similarity between the gradient it
induces (paired with a compliance token, on safety-critical parameters) and
a fixed unsafe reference direction. It was validated on single prompts. The
authors apply it to conversations before generation, over user turns only,
with windows of W turns (W = 1 scores each turn alone; full history is the
other extreme).

**Setting**: Llama 3.1 8B Instruct (main) and Qwen2.5-7B-Instruct; 537
human-authored multi-turn jailbreaks (MHJ); 149 successful automated
Crescendo conversations (of 200 HarmBench objectives, 74.5% success);
benign sets of 2,000 WildChat conversations length-matched to MHJ and 183
synthetic conversations generated with Gemini 2.5 Pro; Llama Guard 3 as an
external baseline under the same user-turn-only protocol.

## Key Findings

- **Synthetic benign data makes the detector look solved.** With W = 3,
  ROC-AUC was 0.9836 against synthetic benign conversations and 0.7614
  against WildChat.
- **Thresholds do not transfer.** The synthetic best-F1 threshold flagged
  8.74% of synthetic benign conversations and 90.85% of WildChat ones.
- **Shorter windows beat more context (on Llama).** AUC fell from 0.8101 at
  W = 1 to 0.7362 at W = 7; full history scored 0.7376. The W = 1 advantage
  over W = 3 was 0.0487 (95% CI 0.0329–0.0643). It held on conversations of
  seven or more turns (W = 1: 0.8622, full history: 0.7411) and for every
  tactic group. The authors attribute it to benign turns diluting the
  gradient.
- **Attack family matters.** On successful Crescendo conversations, W = 1
  AUC was 0.5018 (indistinguishable from random) and W = 3 was 0.3050, below
  random: the user turns score lower than ordinary benign traffic. Llama
  Guard 3 scored 0.1478 at W = 3 on the same set (prompt-only, which is
  narrower than its intended use).
- **Model matters.** On Qwen2.5-7B-Instruct every setting scored
  0.5545–0.5908, and the ordering reversed (full history best). The Llama
  threshold transferred to Qwen gave 38.8–82.9% false positives.
- **Simple fixes did not help.** Contrastive baselines, benign-subspace
  removal and a multi-turn reference direction all scored below the plain
  W = 3 baseline.
- **Scope stated by the authors**: separability study, not a blocking
  system; no attacker optimizing against the gradient score; one signature
  per model; WildChat contains some adversarial-looking text, kept on
  purpose.

## Relevance to Praxis

- Strong evidence for calibrating any safety detector on realistic,
  length-matched benign traffic, per target model, and for reporting the
  false-positive rate at the deployed threshold (see
  rules/agent-sandbox-safety.md, "Measure each defense's benign cost on a
  matched benign arm, on the assembled stack").
- A prompt-only detector can miss context-building attacks entirely,
  because the unsafe content appears only in the response. In agents that
  act on the response, pair input scoring with action-level gates.
- Context length is a detector-specific design choice: on Llama, adding
  turns diluted this input detector, while trajectory-level evaluation of
  agent behavior remains necessary
  ([blindspot-long-horizon-agent-safety](blindspot-long-horizon-agent-safety.md)).
  The two are different measurement targets, not a contradiction.
- Per-model behavior differs, consistent with
  [door-in-the-face-model-refusals](door-in-the-face-model-refusals.md).

> Source: Does the Unsafe Gradient Survive a Conversation? On the Fragility of Gradient-Based Jailbreak Detection in Multi-Turn Dialogue (arXiv:2609.36849)
