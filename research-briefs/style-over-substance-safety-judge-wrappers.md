# Style Over Substance: Content-Invariant Wrappers Flip Safety-Judge Verdicts

> **Paper**: [Style Over Substance: Content-Invariant Wrappers Flip LLM Safety-Judge Verdicts](https://arxiv.org/abs/2609.08236)
> **Praxis source**: src:2609-08236

## Why Not a Skill?

This paper demonstrates an attack on LLM-as-a-judge safety evaluators, not a defensive procedure. The finding (stylistic wrappers flip verdicts without changing content) is a documented pitfall, not a reusable procedure.

---

## Core Concept

LLM safety judges evaluate whether model outputs are harmful. This paper shows that content-invariant stylistic wrappers — changes to formatting, tone, or framing that preserve the actual content — can flip safety-judge verdicts from "harmful" to "safe" or vice versa. The attack surface is the judge's reliance on surface-level stylistic cues rather than semantic content analysis.

### Key Finding

- **Primary Result**: Content-invariant wrappers (e.g., academic framing, formal tone, structured formatting) can flip safety-judge verdicts without changing the underlying content semantics.
- **Secondary Result**: This vulnerability affects both proprietary and open-weight LLM judges, suggesting it's a fundamental limitation of current safety evaluation architectures rather than a model-specific bug.

## Relevance to Praxis

- **LLM-as-a-judge fragility**: Directly relevant to the `rubric-artifact-bias-in-llm-judges` brief and the `harness-tampering-audit` skill. Safety judges in self-improvement loops can be gamed by stylistic manipulation.
- **Rule candidate**: DO verify safety judge robustness against content-invariant stylistic transformations before deploying in automated evaluation loops.
- **Defense direction**: Multi-judge panels with diverse prompting styles (as in `debate-consensus-memory-calibration`) may mitigate single-judge stylistic vulnerability.
