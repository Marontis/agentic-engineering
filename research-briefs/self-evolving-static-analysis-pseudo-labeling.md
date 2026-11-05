# Self-Evolving Static Analysis via LLM Pseudo-Labeling

> Source: `src:2610-30184` — "Self-Evolving Static Analysis via LLM Pseudo-Labeling" (arXiv:2610.30184, 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Classification: Research Brief (Contextual Knowledge)

This paper is classified as a **research brief** because its evolutionary loop (**SESAA**) is specialized to synthesizing Scala **Joern** Code Property Graph (CPG) static-analysis queries for Python security auditing. However, its unlabeled actor-critic architecture—where an LLM actor evolves deterministic symbolic detectors guided by persistent False-Positive (FP) and False-Negative (FN) tickets issued by a stronger LLM critic without ground-truth labels—provides important empirical evidence for `rules/recursive-improvement.md` and `rules/agent-evaluation-quality.md`.

---

## Problem & Motivation

Deploying LLMs directly as line-by-line code vulnerability scanners over large repositories is prohibitively expensive, non-deterministic, and prone to context-window limits. Conversely, traditional static application security testing (SAST) engines (CodeQL, Semgrep, Bandit) run deterministically at near-zero marginal cost, but their default community rulesets suffer from poor recall and high false-positive rates on project-specific abstractions, while tuning custom rules normally requires labeled ground-truth vulnerability datasets that do not exist for target repositories.

---

## Architecture: Unlabeled Actor-Critic Evolution with Persistent FP/FN Tickets

SESAA (Self-Evolving Static Analysis Agent) compiles expensive frontier-LLM security reasoning offline into human-readable, deterministic **Joern** CPG queries with zero LLM cost at scan time:

1. **ReAct Actor (`Claude Sonnet 5`)**:
   - Starts from an empty query suite ($D_0$) and operates within a 2,000-message budget per generation using workspace tools to inspect target source files, write/edit/delete Scala Joern queries, and execute them against the repository's CPG.
2. **Stronger Pseudo-Labeling Critic (`Claude Opus 4.8`) & Ticket Ledger**:
   - Without access to ground-truth labels, the critic inspects code regions flagged by current queries and samples unflagged code regions.
   - Instead of returning a scalar score, the critic opens persistent, per-finding **FP tickets** (on flagged code it judges benign) and **FN tickets** (on unflagged code where it spots a missed vulnerability pattern).
   - To resolve a ticket, the actor must either modify its Joern queries so the finding disappears/appears, or **contest** the ticket with a concrete technical counter-argument accepted by the critic.
3. **Pseudo-Labeled Fitness Gate**:
   - Candidate query suites $Q$ are scored via a pseudo-labeled fitness function:
     $$F(Q) = \min\!\left(1,\; \sqrt{\hat{p} \cdot \hat{c}}\,(1 + a)\right)$$
     where $\hat{p}$ is the unweighted mean group precision across query/CWE groups (fraction of findings without an open FP ticket), $\hat{c} = |\mathcal{R}_{\text{resolved}}| / (|\mathcal{R}_{\text{resolved}}| + |\mathcal{R}_{\text{open}}|)$ is the share of resolved FN tickets (bootstrapped by CWE-type coverage $\hat{c}_{\text{type}}$ over 14 OWASP classes during cold start), and $a = 0.05 \cdot \min(1, |Q(C)|/10)$ rewards non-trivial rule activity.
   - Across generations, SESAA retains the highest-fitness suite $D^\star$. In production deployments, any candidate rule-suite modification must also comply with `"DO: Pass every self-modification through one acceptance gate"` in [recursive-improvement.md](../rules/recursive-improvement.md).

---

## Key Empirical Findings

### 1. Benchmark Evaluation on OWASP Benchmark for Python (1,230 Test Cases)

Evaluated on the OWASP Benchmark for Python (1,230 test cases: 452 vulnerable, 778 safe across 14 CWE categories), SESAA evolved Joern queries with **zero access to ground-truth labels**:

| Method / Condition | Ground-Truth Labels Used? | Precision | Recall | Mean $F_1$ |
| :--- | :---: | :---: | :---: | :---: |
| Semgrep (community default rules) | No | — | — | 0.19 |
| CodeQL (out-of-the-box community suite) | No | — | — | 0.30 |
| Bandit (default Python scanner) | No | — | — | 0.37 |
| One-shot label-informed Joern baseline | Yes | — | — | 0.69 |
| Best-of-9 label-tuned CodeQL configuration | Yes | — | — | 0.70 |
| **SESAA (`S1`, full critic + FP/FN tickets, $n = 8$ seeds)** | **No** | **0.780** | **0.734** | **0.742 $\pm$ 0.084** (95% CI $[0.671, 0.812]$) |
| SESAA `S2` ablation (no critic, $n = 5$ seeds) | No | 0.642 ($p = 0.075$) | 0.825 | 0.713 |
| SESAA `S3` ablation (no FP tickets, $n = 5$ seeds) | No | — | — | Degraded ($p = 0.091$, Cohen's $d = -0.77 \pm 0.52$, 93% prob. of harm) |

- **Beating label-tuned baselines without labels**: SESAA (`S1`) outperformed out-of-the-box CodeQL (0.30), Semgrep (0.19), and Bandit (0.37) by 37–55 $F_1$ points and beat the best-of-9 label-tuned CodeQL baseline (0.70) on **6 of 8 independent seeds**.
- **Critic ticket validity and collateral over-pruning**: Across 2,158 tickets in 8 `S1` seeds, FP tickets were highly enriched for true false positives (Fisher's exact $p = 1.1 \times 10^{-35}$) and drove targeted repairs ($p = 5.2 \times 10^{-71}$), while pooled FN tickets (159 total) identified genuine misses **61%** of the time (seed mean $70\% \pm 17\%$). However, when the actor edited queries to close FP tickets, **97 of 665** removed findings accidentally pruned true vulnerabilities—illustrating the risk of collateral regression when fixing false positives without a held-out regression anchor.
- **Amortized synthesis cost**: A single `S1` evolution run consumed ~**254M input / 490K output** `Claude Sonnet 5` tokens plus **1.68M input / 213K output** `Claude Opus 4.8` tokens (executing 85 query edits vs. 37 new query creations across 711 tool calls in the committed trajectory), producing deterministic Scala queries that subsequently run at zero LLM cost.

### 2. Proactive Real-World CVE Pilot (`S5`)

To test whether SESAA can discover vulnerability classes *before* a CVE is disclosed, the authors evolved Joern queries on pre-vulnerability repository snapshots across 12 real-world Python projects (36 files, 19 historical CVEs) using a proactive fitness score $F_{\text{proactive}} = \hat{c}_{\text{pattern}} \times (1 - \hat{r}_{\text{fp}})$:

- **53% proactive CVE detection**: The evolved queries flagged **10 of 19 subsequent CVEs (53%, 95% CI $[32\%, 73\%]$)** when run on the commit that introduced the vulnerability—9 of 17 from same-repository detectors and 1 (`pyload`) via cross-repository transfer of rules evolved on `open-webui` and `changedetection.io`.
- **Repository scale bottleneck**: Detections concentrated in smaller repositories (e.g., `picklescan` with 7 files, `mistune` with 4/4 CVEs caught), whereas large codebases (`llama_index` with 3,893 files, `keras`, `MobSF`) yielded **0 catches**, and the proactive fitness metric $F_{\text{proactive}}$ remained largely inert as a selection signal on large repositories.

---

## Why Not a Skill?

SESAA is a heavy, domain-specific offline synthesis pipeline (~255M tokens per run targeting Joern Scala CPG queries) rather than a lightweight, general-purpose agent skill. Its transferable insights—using **persistent, contestable FP/FN critic tickets** instead of scalar self-scores when ground-truth labels are absent, and guarding against **collateral true-positive pruning** (97/665 removed findings) during FP repair—fit directly into `rules/recursive-improvement.md` and `rules/agent-evaluation-quality.md`.

---

## Connections to Praxis

- **Recursive Improvement (`rules/recursive-improvement.md`)**: Shows that in unlabeled environments, pairing a generator agent with a stronger critic that issues persistent, falsifiable FP/FN tickets prevents precision collapse (0.780 vs. 0.642 without critic), but requires regression checks because 14.6% (97/665) of findings removed to satisfy FP tickets were real true positives.
- **Related Skill**: Complements [counterexample-guided-repair](../skills/counterexample-guided-repair/SKILL.md), extending witness-driven refinement from executable ground-truth oracles to stronger-model pseudo-labeled ticket ledgers.
