# Counterfactually Anchored Evidence Attribution for Multi-Turn Safety Failures

> **Source**: Subramanian, Islam, Khan (Kennesaw State), arXiv:2609.27773, Sep 2026
> **Status**: Research Brief — dataset plus a trained attribution model for localizing which turns and tokens caused a multi-turn guardrail failure

## Why Not a Skill?

The method is a trained model (frozen DeBERTa-v3 turn encoder, cross-turn Transformer, gated fusion, counterfactual consistency loss) on a purpose-built dataset. The transferable parts are the counterfactual labelling thresholds and the evaluation metric, which are too small for a standalone skill and too dependent on the trained model to be a procedure.

## Core Concept

Multi-turn jailbreaks build up over many turns, so a binary safe/unsafe verdict on the whole conversation doesn't tell an operator where to intervene. The paper reframes guardrail analysis as **localization**: which user turns, spans and tokens were causally responsible. Labels are anchored counterfactually: replace a suspected pivot turn with a benign alternative and measure the drop in the validator's unsafe score. A turn is "strong" evidence if the drop is ≥ 0.40 and "weak" if it is between 0.15 and 0.40 (spans: strong ≥ 0.40, weak 0.25–0.40). Decoy spans serve as negative controls.

The evaluation metric penalizes attributions that also light up on risky-sounding benign conversations: utility = deviation drop after removing the top 15% of attributed tokens, minus the false-positive rate on borderline and high-risk benign records.

## Key Findings

- **Dataset**: 1,762 conversations (averaging 14.1 user turns), including hard-benign, false-lead and topic-matched safe "twins". Only 41 (2.3%) are strictly counterfactually validated; the rest use weaker supervision tiers. Generator Qwen2.5-14B, target Llama-3-8B, validator Mistral-7B. Humans marked a mean of 3.35 causal turns per adversarial conversation, so failures are usually spread over several turns.
- **Keyword risk scoring is not attribution**: a lexical surface-risk baseline flagged 94.7% of high-risk *benign* conversations (FPR 0.947), 66.7% of false-lead benign and 37.3% of borderline benign. The proposed model: 0.005, 0.030 and 0.007. Attribution utility 0.504 vs 0.195.
- **Gradient attributions fail on this task**: span-level attribution F1 was 0.878 for the proposed model vs 0.724 for attention, 0.003 for Grad×Input and 0.002 for Integrated Gradients.
- **LLM judges localize poorly**: a prompted Qwen2.5-7B judge got detection F1 0.580 and top-1 pivot hit rate 0.149, vs 0.988 and 0.368 for the trained model. Even the trained model's top-3 hit rate is only 0.552, though a human-marked causal turn appears within its top-5 (±5 turns) in about 84.5% of adversarial cases.
- **Flat or per-turn encoders cannot do it**: turn-independent and flat-conversation ablations scored 0 token F1. Cross-turn context is necessary.
- **Transfer is partial**: on human-authored MHJ jailbreaks detection was weak, but attribution on detected cases held (DD@15 0.495). Removing the attributed tokens changed ShieldGemma's verdict in 90.9% of cases vs 63.6% for surface-risk.
- Limits: synthetic 7B–14B generation, user-turn-only attribution, sparse counterfactual supervision, frontier behaviour unknown.

## Relevance to Praxis

- Strengthens [`agent-sandbox-safety`](../rules/agent-sandbox-safety.md) "DON'T: Rely on single-turn refusal or initial benign turns to evaluate long-horizon safety": causal evidence is spread across about 3 turns on average, and per-turn encoders see none of it.
- Supports "DON'T: Trust style-based safety judges as the sole safety gate" in the same file: keyword risk is dominated by false positives on risky-sounding benign traffic, which also feeds the M6 false-refusal budget.
- The counterfactual-deletion check (replace the pivot, measure the score drop) is the same idea as [`agent-evaluation-quality`](../rules/agent-evaluation-quality.md) "DO: Test evaluators with counterfactual perturbations", applied to incident forensics. See also [`targeted-failure-attribution`](../skills/targeted-failure-attribution/SKILL.md) for decisive-step attribution in agent trajectories and [`blindspot-long-horizon-agent-safety`](blindspot-long-horizon-agent-safety.md).

> Source: Subramanian et al., "Beyond Unsafe Detection: Counterfactually Anchored Evidence Attribution for Multi-Turn LLM Safety Failures" (arXiv:2609.27773)
