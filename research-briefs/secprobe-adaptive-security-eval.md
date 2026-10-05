# SecProbe: Adaptive Evaluation of Coding Agents on Vulnerability Repair

> **Paper**: [SecProbe: Adaptive Evaluation of Coding Agents on Cybersecurity Vulnerabilities](https://arxiv.org/abs/2609.33763)
> **Authors**: Luo, Huang, Guo et al. (Notre Dame and others)
> **Praxis source**: src:2609-33763v1
> **Status**: Research Brief — benchmark and evaluation method (defensive: repair, not exploitation)

## Why Not a Skill?

The adaptive loop (IRT fit → information gap → select or synthesize tasks) is
a benchmark-construction method that needs a multi-agent task synthesizer,
a validator and a large evaluation budget. The transferable parts, IRT-based
task selection and "test-passing is not secure", are already covered by
[`trajectory-aware-eval-pruning`](../skills/trajectory-aware-eval-pruning/SKILL.md)
and the repair-validation rules. This brief records the numbers.

---

## Core Concept

Agents receive a repository with injected vulnerabilities and must patch it
so that functional tests pass **and** security tests block the exploitation
samples. Instead of a fixed suite, SecProbe fits a Bayesian 2-parameter IRT
model after each batch, finds the ability range where agents cluster but
available tasks give little information, and either selects existing tasks
at that difficulty or has five specialist LLM agents synthesize new ones.
A deterministic validator (completeness, reference-implementation scoring,
test isolation, reproducibility) accepts tasks, with up to 10 repair rounds.

## Key Findings

- **Pool**: 353 accepted tasks, 6 languages, 151 CWE types, 1,285
  vulnerability instances; 98.0% of tasks touch multiple files and 33.9% of
  vulnerabilities span files. Human rating 4.40/5, 92% acceptance.
- **Agents are far from reliable**: best configuration (GLM-5.3 on
  Terminus-2) passed 28.33%; GPT-5.6 Sol 25.21–26.06%; small models
  (GPT-5.4-mini, Mistral Small 4) below 12%. Nine backbones, two harnesses
  (Mini-SWE-Agent, Terminus-2).
- **Why repairs fail**: incomplete repair coverage 37.9%, wrong
  diagnosis/localization 22.9%, missed application constraints 20.6%,
  regressions 9.5%.
- **Tests are not enough**: of 100 test-passing patches reviewed by experts,
  8 were judged incomplete. An LLM judge agreed with tolerance on 88.4%
  (312/353) of patch reviews; 11.6% needed expert review.
- **Adaptive selection is cheaper**: reaching the target information gap
  needed 244 synthesized tasks vs 328 (random) and 346 (one-shot), i.e.
  25.6% and 29.5% fewer. On held-out models, adaptive selection reached
  ability RMSE ≤ 0.15 with 140 tasks vs 181 (random) and 194 (fixed order).
- **Difficulty control works**: pass rate 44.0% / 27.3% / 13.3% for
  easy / medium / hard.
- **Rankings were stable** across IRT specifications (Spearman ρ =
  0.96–0.98 vs the reference 2PL model).
- **Cost**: about $0.64 per synthesized task; about $5,000 to evaluate all
  353 tasks × 9 models × 2 harnesses.

## Relevance to Praxis

- Further evidence for "DON'T: Validate repairs using crash suppression
  alone" (`rules/agent-evaluation-quality.md`): a passing functional test
  suite missed 8 of 100 incomplete security patches, and incomplete coverage
  was the top failure mode. Require exploit-blocking security tests plus
  review.
- Evidence that adaptive, IRT-based selection keeps an eval informative as
  agents improve and fixed tasks leak into training data; see
  "DO: Prune benchmark suites using trajectory-level features"
  (`rules/agent-evaluation-quality.md`).
- Do not read a SecProbe pass as a deployment guarantee: the paper itself
  says synthetic vulnerabilities do not represent all deployed software.
- Related: [`patchbench-vulnerability-patching-evaluation`](patchbench-vulnerability-patching-evaluation.md),
  [`pipeline-dependent-cybersecurity-benchmarks`](pipeline-dependent-cybersecurity-benchmarks.md),
  [`metrics-failure-vuln-repair`](metrics-failure-vuln-repair.md).

> Source: Luo et al., "SecProbe: Adaptive Evaluation of Coding Agents on
> Cybersecurity Vulnerabilities" (arXiv:2609.33763)
