# Multilingual Persuasive Jailbreak Evaluation (IndicSafeEval)

> **Paper**: [IndicSafeEval: Safety Robustness of Large Language Models under Multilingual Persuasive Jailbreak Attacks](https://arxiv.org/abs/2609.03781)  
> **Praxis source**: `src:2609-03781`

## Why Not a Skill?

*IndicSafeEval* introduces an empirical red-teaming benchmark, taxonomy, and evaluation dataset (7,200 adversarial prompts) measuring safety robustness under multilingual persuasion across Indian languages. Because it is an evaluation study and dataset rather than an operational runtime procedure, it is maintained as a research brief informing agent safety testing and multilingual guardrails.

---

## Core Concept

Safety alignment and red-teaming evaluations for LLMs and autonomous agents are overwhelmingly conducted in English. However, real-world deployment across global user bases exposes models to low-resource and non-English interactions where safety alignment frequently degrades.

IndicSafeEval explores the intersection of **multilingual transfer** and **human-like persuasive framing**, constructing an evaluation framework across:
- **Languages**: Hindi, Bengali, Marathi, and Punjabi (covering Indo-Aryan language families with distinct scripts and tokenizations).
- **Persuasion Strategies (6 types)**: Logical appeal, emotional framing, authority posturing, hypothetical/fictional scenario nesting, deceptive role-play, and urgency framing.
- **Risk Dimensions (10 categories)**: Hate speech, dangerous activities, cybersecurity vulnerabilities, financial fraud, illegal goods, harassment, privacy breaches, and institutional harm.

```
       Adversarial Prompt Composition (7,200 Prompts)
┌─────────────────────────┐     ┌─────────────────────────┐
│ 10 Harm Categories      │  +  │ 6 Persuasive Strategies │
│ (Cyber, Bio, Fraud, etc)│     │ (Urgency, Authority, etc)
└────────────┬────────────┘     └────────────┬────────────┘
             │                               │
             ▼                               ▼
       ┌───────────────────────────────────────────┐
       │ 4 Non-English Languages (Indic Scripts)   │
       │ (Hindi, Bengali, Marathi, Punjabi)        │
       └─────────────────────┬─────────────────────┘
                             │
                             ▼
                Black-Box LLM Vulnerability Audit
```

### Key Findings

1. **The Multilingual Alignment Gap**: Safety guardrails tuned primarily on English corpus data exhibit sharp performance degradation when queries are translated or formulated directly in non-Latin scripts. Models that reliably refuse harmful English requests frequently comply when the identical request is framed in Bengali or Marathi.
2. **Persuasion Amplification**: Persuasive psychological framing (especially authority posturing and hypothetical role-play) acts as an exploit multiplier in non-English contexts, bypassing safety classifiers that look for explicit harmful keywords.
3. **Category Vulnerability Variance**: Risk categories vary dramatically in vulnerability: cybersecurity exploits and financial fraud information showed significantly higher jailbreak success rates under persuasive framing compared to physical violence prompts.

---

## Relevance to Praxis

- **Multilingual Red-Teaming**: Automated agent red-teaming workflows (such as `self-improving-red-team`) must incorporate multilingual paraphrasing and persuasive framing into their mutation operators to prevent blind spots.
- **Guardrail Localization**: Input/output guardrails in agent gateways cannot rely on English-language semantic filters; they must operate on cross-lingual representations or enforce pre-translation normalization before safety classification.
