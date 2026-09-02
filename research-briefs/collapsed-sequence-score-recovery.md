# Wrong Prediction, Right Answer: Recovering Evidence from Collapsed LLM Sequence Scores

> **Paper**: [Wrong Prediction, Right Answer: Recovering Evidence from Collapsed LLM Sequence Scores](https://arxiv.org/abs/2608.31068)
> **Praxis source**: `src:2608-31068v1`

## Why Not a Skill?

Analysis â€” demonstrates that LLM sequence probabilities can collapse even on correct answers, and shows how to recover the underlying evidence signal. Interesting but too narrow for a subtask-level skill.

---

## Core Concept

LLMs can assign low sequence probability to correct answers due to score collapse â€” the product of many token probabilities degrades faster for longer sequences. The actual evidence that the model "knows" the answer is present in the hidden states but masked by the collapsed sequence score.

### Key Insight

Don't trust raw sequence scores as a quality signal. Longer correct answers score worse than shorter incorrect ones purely due to length-based collapse, not due to model uncertainty.

## Relevance to Praxis

- Complements the ag-evidence-triage skill â€” sequence scores alone are unreliable for evidence assessment
- Relevant to the hallucination-mean-shift-probe skill â€” hidden states carry more reliable signal than output probabilities
