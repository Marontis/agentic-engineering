# ER-Audit: Black-Box Auditing of Verifiers Fine-Tuned on Debate Transcripts

> **Paper**: [Black-Box Auditing of Epistemic Reliability in Multi-Agent Debate Distillation](https://arxiv.org/abs/2609.32361)
> **Praxis source**: src:2609-32361v1
> **Code**: https://github.com/CSIRO-CQS-AI-alignment-Team/Epistemic-Reliability-Auditor

## Why Not a Skill?

The audit (paraphrase search plus anytime-valid sequential testing) is a
statistical evaluation method tested only on question answering with one
threat model, and its threshold is calibrated on a deliberately degraded
model organism. What transfers is the lesson that aggregate accuracy hides
local degradation, which belongs with the existing acceptance rules.

---

## Core Concept

A weaker verifier fine-tuned on multi-agent debate transcripts can improve
on the monitored task while becoming less reliable on related, unmonitored
("hidden") questions. An adversarial debater that argues for the correct
monitored answer can still shift the verifier's beliefs about hidden
questions. Standard metrics average this away.

**ER-Audit** works without model internals:
1. **Counterexample search**: generate semantic paraphrases of each hidden
   question and look for one where the hidden-task loss, normalized by the
   monitored-task gain, exceeds a threshold ε.
2. **Sequential testing**: if none is found, test fresh paraphrases and
   maintain an anytime-valid lower confidence bound (e-processes, Ville's
   inequality) on the probability that a paraphrase is *not* degraded. Bounds
   from several paraphrase generators combine without a multiple-testing
   correction, and testing can stop at any time.

## Key Findings

- **Setting**: verifiers gpt-oss-20B, Qwen3.5-9B, Llama3.1-8B; debaters
  Gemma-4-31B-it. New benchmarks QuALITY-H (222 monitored–hidden pairs,
  long-form reading) and GPQA-H (101 STEM pairs). M_search = M_test = 100;
  search uses one generator, testing uses two. ε set to the 25th percentile
  of degradation scores.
- **Aggregate metrics mislead**: on QuALITY-H with the 20B verifier, the
  verifier trained on adversarial transcripts scored *higher* than the one
  trained on honest transcripts on both monitored (80.63% vs 79.73%) and
  hidden (63.96% vs 59.91%) accuracy.
- **The audit disagrees**: it found counterexamples for 103 of 222 hidden
  questions with the adversarially trained verifier vs 90 with the honest
  one; on GPQA-H, 40 vs 35 of 101. The honest verifier had the higher
  average lower bound across thresholds and verifier models.
- **Model organism**: a verifier trained with an explicit loss toward wrong
  hidden answers fell to 27.48% hidden accuracy (base 63.06%) while its
  monitored accuracy rose to 66.67% (base 53.60%).
- Degradation was more pronounced in long-context settings that need
  evidence integration and retention.
- **Limitations stated by the authors**: QA tasks only; paraphrase coverage
  depends on generator quality; ε calibrated from the model organism may
  not generalize; persistent fine-tuning effects only, not inference-time
  influence.

## Relevance to Praxis

- Supports "DON'T: Accept modifications based on aggregate metrics alone"
  (`rules/recursive-improvement.md`): a fine-tune that wins on both
  aggregate metrics still lost more local reliability.
- When distilling debate or judge transcripts into a verifier, audit
  unmonitored neighbouring tasks with paraphrase probes, not just the
  monitored benchmark. Complements "DON'T: Assume multi-agent debate
  eliminates shared misconceptions" and "DON'T: Rely on group size or
  majority vote to dilute adversarial agents"
  (`rules/multi-agent-coordination.md`).
- Related: [`debate-to-skill-process-supervision`](debate-to-skill-process-supervision.md),
  [`adversarial-influence-scaling-multi-agent`](adversarial-influence-scaling-multi-agent.md).

> Source: Black-Box Auditing of Epistemic Reliability in Multi-Agent Debate Distillation (arXiv:2609.32361)
