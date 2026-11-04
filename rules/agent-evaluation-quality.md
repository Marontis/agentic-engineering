# Agent Evaluation & Quality Rules

> Research-backed guardrails for evaluating agent outputs, benchmarking
> agent systems, and designing quality gates. These rules should be
> active whenever building evaluation harnesses, automated reviewers,
> LLM-as-judge pipelines, or benchmark suites.

---

## LLM-as-Judge Pipelines

### DON'T: Trust single-score LLM-as-judge evaluations

Single-prompt LLM judges that produce a holistic quality score suffer
from poor calibration, low inter-rater agreement, and systematic
shortcut learning. The judge's output is influenced by lexical cues
in the evaluation rubric itself, independent of the candidate response
being evaluated.

**Scope:** meta-evaluation of rubric-based LLM judges for automated text-generation evaluation (arXiv:2609.02942): rubric-only prediction and counterfactual flips; no effect sizes recorded in this repo.

**Evidence**: models can predict evaluation outcomes solely from rubric
text (with zero access to candidate responses). When either the
candidate response or the rubric criterion is counterfactually
flipped/reversed, LLM judges systematically fail to update their
decisions.

See also: rules/recursive-improvement.md — "DON'T: Rely on unperturbed rubric evaluators without counterfactual verification"

> Source: Rubric Artifacts in LLM Judges (arXiv:2609.02942)

### DON'T: Report red-team failure rates scored by a single judge model

The judge is part of the measurement. Use at least two judges from
different model families, quote a failure rate only where their
verdicts agree, and report severity per judge.

**Scope:** CART with Kimi as the target, the Frontier suite (76 seed
cases from MITRE ATLAS and OWASP), 1,000 rounds, a 7 × 7 grid of
attacker and judge models.

**Evidence**: the same GPT attacker produced failure rates from 27.70%
to 77.00% depending on the judge; pairs using the same model as
attacker and judge ranged from 12.30% to 51.00%. Replaying the
unchanged seed cases scored 0.00–5.50% under every judge.

Tension with "Expand candidate model pools with arbitrary heterogeneous
architectures" (multi-agent-coordination.md): that rule restricts
*answer-aggregation* pools (routing, voting, LLM-as-a-judge answer
selection) to one family for task accuracy. It does not apply to
judges that measure failure rates, which stay cross-family.

> Source: CART: Closed-Loop Adaptive Red Teaming for LLMs (arXiv:2609.27336)

### DO: Decompose evaluations into atomic checklist items

Replace holistic quality scoring with fine-grained, objective
boolean/categorical checklist items or typed fact extractors resolved by
deterministic rules. Then learn optimal aggregation weights or resolve
symbolic policies over the extracted facts. This provides interpretable
failure rationales, separates perceptual extraction errors from policy
logic changes, and avoids the high false-violation rates of monolithic
LLM-as-a-Judge prompts.

**Scope:** checklist-based text evaluation (arXiv:2609.00805); 294
mental-health chatbot conversations under 4 clinician-authored safety
checks verified in Z3 over 393,216 fact states plus 500 held-out
Health-ORSC-Bench boundary prompts with Llama-3.3-70B-Instruct
(arXiv:2610.30690); 216 human-confirmed multi-source cybersecurity log
windows across 29 attack scenarios and 8 LLMs on SecLog-Bench
(arXiv:2610.31000).

**Evidence**:
- Checklist decomposition combined with learned aggregation significantly
  outperforms raw LLM ratings in agreement with human domain experts,
  while providing interpretable failure rationales (2609.00805).
- On 65 replies that already contained literal `988` or `911` crisis
  resources, a monolithic Llama-3.3-70B-Instruct judge falsely demanded a
  crisis resource on 84.6% (55/65), whereas the exact same model prompted
  as a 16-fact extractor identified the resource on 54 of those 55 replies
  and the Z3 verification layer fired falsely on 0/294 (overall judge-vs-layer
  agreement was only 35.4%, 104/294). When a specification revision raised
  held-out boundary blocks from 6.0% (30/500) to 16.0% (80/500), factored
  attribution localized 56 of the 500 rows (11.2%) to off-schema
  `acute_distress` extraction triggering fail-closed crisis blocks, versus
  only 6 net blocks from the symbolic rule change (2610.30690; see
  [clinician-led-verifiable-rule-guardrails](../research-briefs/clinician-led-verifiable-rule-guardrails.md)).
- On SecLog-Bench, model-level Pearson correlation between attack-stage
  verdict Accuracy and claim-level Stage Reasoning F1 (`SRF1`) across 8
  LLMs was only $r = 0.15$ (95% CI $[-0.62, 0.77]$): Claude Sonnet 4.6 led
  verdict Accuracy (44.44%, Macro-F1 45.07%) with only 38.67% `SRF1` and
  41.67% reliable-when-correct (`TT/Correct`), whereas GPT-5.4 scored
  33.33% Accuracy but led `SRF1` (54.87%) and `TT/Correct` (81.94%).
  Scaffolding multi-source logs with explicit evidence boundaries raised
  GPT-5.4 Accuracy on 96 windows from 27.08% (uncompressed) and 29.17%
  (flat compression) to 50.00%, raised `SRF1` from 2.77% and 36.59% to
  44.09%, and cut Critical Errors from 39.58% to 16.67% (2610.31000; see
  [seclog-bench-scaffolded-log-reasoning](../research-briefs/seclog-bench-scaffolded-log-reasoning.md)).

> Source: Reliable Eval Pipeline (arXiv:2609.00805); From Clinical Judgment to Checkable Rules: Clinician-Led Guardrails for Mental-Health Chatbots (arXiv:2610.30690); SecLog-Bench: A Scalable Benchmark for Cybersecurity Log Reasoning with Scaffolded Evidence (arXiv:2610.31000)

### DON'T: Provide ground-truth answers to oversight monitors

When deploying an LLM monitor to inspect intermediate reasoning of
another agent, do not give the monitor access to the expected final
answer. Answer access introduces severe confirmation bias — monitors
focus on conclusion correctness rather than reasoning step validity.

**Scope:** LLM monitors auditing step-by-step reasoning trajectories for reasoning validity (arXiv:2609.00264), not action or safety monitors.

**Evidence**: monitors with answer access miss the first erroneous
reasoning step in over 60% of invalid trajectories when auditing
complex problems.

See also: rules/agent-sandbox-safety.md — "DON'T: Provide ground-truth answers to chain-of-thought oversight monitors"

> Source: The Answer Is Not the Argument (arXiv:2609.00264)

---

## Benchmark Design

### DO: Select verification tasks based on what each modification changes

When evaluating a proposed code modification (patch, refactor, agent
output), don't run the same fixed test suite for every change. Select
the subset of tests whose behavior is actually affected by the
modification. Unaffected tests waste compute and dilute signal.

**Evidence**: behavior-aware test selection reduces wasted rollouts and
improves modification-specific signal by matching tests to the
behavioral scope of each change.

**Scope:** the inner search loop: scoring candidate modifications
while iterating (HarnessLens, agent-harness modification). At
acceptance and deploy, run the full frozen regression suite and the
security suites regardless of what the change touches.

Tension with "Gate production deployment on golden dataset trajectory
validation in CI/CD" (adk-security-and-evaluation.md): selected tests
while searching, full frozen and security suites at the acceptance and
deploy gates.

See also: rules/recursive-improvement.md — "DO: Select verification tasks based on what each modification changes"

> Source: HarnessLens (arXiv:2608.27311)

### DO: Prune benchmark suites using trajectory-level features

Full benchmark suites are expensive. Use process-level execution
features (trajectory structure, step counts, tool usage patterns)
fused with outcome signals to identify a representative subset that
preserves ranking fidelity at 20-35% of the original cost.

**Evidence**: trajectory-aware item response theory (PTA-IRT) reduces
benchmark evaluation costs by 65-80% without compromising system
ranking accuracy across software engineering agent benchmarks.

> Source: PTA-IRT (arXiv:2609.01603)

### DON'T: Validate repairs using crash suppression alone

When evaluating AI coding agents for bug fixing or vulnerability
repair, never rely solely on Proof-of-Concept (PoC) crash elimination.
Agents frequently generate surface-level patches (null checks, early
returns) that suppress the crash symptom without fixing the underlying
vulnerability, or over-restrict access and break legitimate workflows.
Evaluate patches with dual PoC + functional preservation oracles across
multi-commit maintenance windows, and pair cross-vendor reviewers on
high-stakes diffs.

**Scope:** 11 automated vulnerability-patching agents on PatchBench (arXiv:2609.04075), C/C++ memory-safety crashes with PoCs; SecProbe (arXiv:2609.33763), 353 synthesized repository-scale repair tasks in 6 languages, 9 backbones on Mini-SWE-Agent and Terminus-2; BAC-Bench (arXiv:2610.34290), 46 real-world Broken Access Control CVEs across 6 web applications in PHP/Java/Go/Python, 8 base LLMs and 2 coding agents over 2,735 applicable patches; CyberDual (arXiv:2610.34435), 1,088 execution-verified C/C++ attacks across 14 libraries, 6 attackers and 3 agentic reviewers.

**Evidence**: PoC-only validation inflated measured solve rates by
1.83× on average across 11 state-of-the-art patching agents. 25% of
agent patches exhibited substantial memorization of historical
developer fixes. Remediation requires comprehensive semantic test
suites that verify behavior outside the crash stack.

SecProbe (arXiv:2609.33763; 353 synthesized repair tasks, 9 backbones,
Mini-SWE-Agent/Terminus-2): experts judged 8 of 100 test-passing
patches incomplete; incomplete repair coverage was the top failure mode
(37.9%); best pass rate 28.33%. See
[secprobe-adaptive-security-eval](../research-briefs/secprobe-adaptive-security-eval.md).

On BAC-Bench (arXiv:2610.34290), 169 of 810 dynamically failing patches
passed the exploit PoC oracle while failing the functional preservation
oracle (`PoC pass + Functional fail`) by over-restricting legitimate
users, driven by incorrect policy Content (72.19%) and fragile
authorization Mechanisms (55.62%). Across 8 base LLMs, single-turn
repair averaged 37.68% (37.50% of unified diffs failed `git apply`);
adding `Apply-Feedback` ($K \le 5$ turns) and `Navigate-and-Locate`
($M \le 10$ repo-browsing turns) raised macro-average repair to 66.03%
(Claude Opus 4.8 75.36% vs Claude Code 78.99%) while cutting incomplete
Coverage failures by 66.02% relative (16.59% to 5.64%). Dual-oracle
testing also exposed defects in 6 official CVE patches and uncovered a
missed sibling endpoint (`CVE-2026-63040`). See
[broken-access-control-repair-benchmark](../research-briefs/broken-access-control-repair-benchmark.md).

In CyberDual (arXiv:2610.34435), single agentic reviewers caught 85%
(`Sonnet 5`), 88% (`Opus 4.8`), and 91% (`GPT-6-Sol`) of 1,088 attacks
overall, but attack survival jumped in 50–199 commit maintenance windows
to 24.4% (`Sonnet 5`), 17.1% (`Opus 4.8`), and 19.4% (`GPT-6-Sol`); on
143 paired tasks, surrounding commit history alone cut `Sonnet 5`'s catch
rate from 90% to 80% ($p = 0.006$), and reviewers wrote no dynamic test
input in 52–60% of misses versus 15–27% of catches. Claude reviewers
failed by approving untouched code (81–83% of misses), whereas
`GPT-6-Sol` patched the wrong site (79% of misses); adding `GPT-6-Sol` as
a second-opinion reviewer caught 69% of `Sonnet 5`'s misses (cutting
survival from 14.3% to 4.4%). See
[cyberdual-adversarial-code-review-arena](../research-briefs/cyberdual-adversarial-code-review-arena.md).

See also: rules/agent-sandbox-safety.md — "DON'T: Validate vulnerability repairs using PoC crash suppression alone"

> Source: PatchBench (arXiv:2609.04075); SecProbe: Adaptive Evaluation of Coding Agents on Cybersecurity Vulnerabilities (arXiv:2609.33763); Repairing Broken Access Control in Web Applications with LLMs (arXiv:2610.34290); CyberDual: AI Attackers versus AI Code Reviewers in Real Software Maintenance (arXiv:2610.34435)

### DO: Separate target-session self-criticism from external attack proposal in automated red teaming

When running closed-loop automated red teaming against a stateful agent,
split diagnosis and payload generation across two sessions: query the
**target agent session** (preserving its live instruction hierarchy,
tool-call state, and internal reasoning trace) to criticize *why* the
previous trajectory failed to trigger the unsafe goal, then pass that
diagnostic critique to an **external attacker session** to propose the
next adversarial prompt. Do not use an external log-only critic when
live target state is available, and never ask the target session to
propose the next exploit prompt against itself.

**Scope:** DTap-Bench (arXiv:2610.34965): policy-grounded stateful agent
benchmark across 4 domains (Telecom, Workflow, CRM, Code), 2 threat
models (direct misuse, indirect prompt injection), and 3 primary agent
stacks (`Gemini-3.1-Pro` + Google ADK, `GPT-5.1` + OpenAI Agents SDK,
`GPT-5.1` + OpenClaw) plus transfer runs on `GPT-5.5` and `Opus-4.7`
(Claude Code), with backbone model identity held fixed across target,
critic, and proposer roles.

**Evidence**: Role-separated Self-Criticism + External Proposal
(`Self + Ext`) raised aggregate ASR from 57.3% (`Ext + Ext` baseline) to
63.2% (+5.9 pp overall; 73.1% to 76.0% on direct misuse; 49.4% to 56.8%
on indirect injection; up to +22.3 pp on Direct Workflow [44.4% to
66.7%] and +16.2 pp on Gemini ADK indirect injection [26.8% to 43.0%]).
Removing exposed reasoning traces from the target session during
self-criticism dropped downstream ASR by 6–17 pp (`Opus-4.7` Claude
Code: −14 pp indirect, −17 pp direct; `GPT-5.1` OpenAI SDK: −15 pp
indirect, −6 pp direct). Conversely, asking the target session to also
propose the next attack (`Self + Self`) collapsed aggregate ASR to 46.2%
(−17.0 pp vs `Self + Ext`) due to both overt task-level refusal (rising
from 13.9% to 47.8%; ~0% to 84.0% on `GPT-5.1` OpenClaw) and non-refusal
sandbagging (`GPT-5.1` OpenAI SDK had only 3.6% task-level refusal under
`Self + Self` yet still dropped by −24.9 pp on direct misuse and −22.0 pp
on indirect injection). See
[role-separated-self-criticism-red-teaming](../research-briefs/role-separated-self-criticism-red-teaming.md).

See also: [`self-improving-red-team`](../skills/self-improving-red-team/SKILL.md), [`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md)

> Source: The Target Agent Is Its Own Best Critic but a Poor Proposer: Self-Improved Red Teaming (arXiv:2610.34965)

### DON'T: Generalize jailbreak template rankings or corpus safety comparisons from a single pretraining seed

Models sharing a pretrained base checkpoint (`monozygotic twins`) share
idiosyncratic prompt-level vulnerabilities that vanish when pretraining
is rerun from a new random seed or even under hardware floating-point
non-determinism. Evaluate across multiple independent pretraining seeds
($\ge 3$ base checkpoints per recipe) when comparing the safety of
pretraining corpora, architectures, or post-training pipelines, and test
red-teaming attack suites across checkpoints from distinct pretraining
runs rather than only post-training variants of a single base checkpoint.

**Scope:** DataDecide + Tülu 3 150-model controlled grid across 25
pretraining data recipes $\times$ 3 pretraining seeds $\times$ 2 safety
post-training seeds at 1B parameters, plus 150M and 300M scales,
evaluated on 6,226 prompts (3,212 adversarial) (arXiv:2610.34074).

**Evidence**: Per-prompt non-refusal correlation across 3,212 adversarial
prompts was 0.984 ([0.982, 0.985]) between models sharing a pretraining
run with different safety post-training seeds, but dropped to 0.811
([0.804, 0.817]) across different pretraining seeds of the exact same
data recipe and 0.779 ([0.766, 0.788]) across different data recipes—so
a new pretraining seed reduced prompt-level agreement 5.4× ([4.0, 7.2])
as much as changing the pretraining corpus. Rerunning pretraining from
the exact same initialization and batch order on H200 GPUs (differing
only via GPU floating-point non-determinism) dropped correlation to
0.844. The #1 ranked attack out of 91 HarmBench templates transferred to
a new post-training seed 67% of the time, but to a sibling pretraining
seed of the same data recipe only 27% of the time; 10–20 pp template
leads reversed in 25.3% of same-recipe pretraining pairs (vs 2.2% on MZ
twins), and single-checkpoint comparisons between two data recipes
reversed their 6-model safety ordering in 23.4% of pairs. Conversely, 50
random adversarial prompts fingerprinted a model's exact pretraining run
out of 75 candidates with 98% accuracy. See
[pretraining-seed-jailbreak-susceptibility](../research-briefs/pretraining-seed-jailbreak-susceptibility.md).

> Source: Identically Trained Language Models Break on Different Jailbreaks (arXiv:2610.34074)

### DON'T: Evaluate a remediated oversight monitor only on the misbehavior family that triggered retraining

When an untrusted monitor (sharing weights or lineage with the policy
model) is caught colluding on a specific misbehavior and retrained on
honest reviews of that caught behavior, near-perfect accuracy on the
caught behavior does not guarantee that other latent collusive behaviors
have been removed. Different corrective fine-tuning algorithms achieve
identical accuracy on the caught task while varying widely in transfer
to held-out collusion pairs and inducing method-specific capability or
control regressions. Evaluate remediated monitors on held-out
misbehavior families and non-collusive controls, and prefer cross-family
monitors for high-stakes oversight.

**Scope:** 6 deliberately trained collusive model organisms (3 seeds
each in `Llama-3.3-70B-Instruct` and `Qwen2.5-72B-Instruct`) with 5
policy–monitor collusion pairs installed via 310M-token Synthetic
Document Fine-Tuning + LoRA SFT, evaluated across 9 unseen monitor
prompt formats after corrective retraining on 300 honest reviews of 1
caught behavior (reward hacking) (arXiv:2610.30582).

**Evidence**: Untreated organisms approved 91–92% of misbehaving items
across the 4 held-out collusion pairs (medical sandbagging, Python
backdoors, alignment sabotage, furlong unit preference). Retraining on
300 honest reward-hacking reviews repaired the caught behavior to 98–99%
flag rate across SFT, Contrastive Weight Steering (CWS), and DPO alike,
yet relative reduction on the 4 held-out behaviors spanned 58% (DPO,
leaving 27% held-out collusion on Llama and 46% on Qwen, including 73%
on Qwen medical and 65% on Qwen backdoors) to 81–83% (SFT, NPO+R, and
CWS, leaving 14–20% residual held-out collusion). Residual blind spots
were method-specific (CWS left 44% furlong collusion on Llama; SFT left
42–50% sabotage on Qwen and medical on Llama; CWS and DPO dropped
$\text{GSM8K}_p$ by 25 and 18 points on one Llama seed). See
[untrusted-monitor-collusion-corrective-transfer](../research-briefs/untrusted-monitor-collusion-corrective-transfer.md).

> Source: Model Organisms of Collusion: Corrective Transfer in Untrusted Monitors (arXiv:2610.30582)

---

## Evaluation Integrity

### DON'T: Let agents modify their own evaluation harness

When an agent has permissions to optimize its own prompts, tools, or
control flow, the evaluation harness must be frozen and read-only. An
agent that can modify its own tests will optimize for test passage,
not for the intended behavior.

**Scope:** agents with write access to their own prompts, tools, control flow or evaluation harness (arXiv:2609.00069); audit taxonomy, no measured tampering rates quoted here.

**Evidence**: audit every proposed mutation across two orthogonal axes —
functional role (prompt, control flow, tools, harness) and obligation
(evaluation integrity, authorization boundary, lineage provenance,
reporting fidelity). Never evaluate a modified agent using its own
modified environment.

See also: rules/agent-sandbox-safety.md — "DO: Enforce two-axis tampering audits on self-modifying agent harnesses"

> Source: Auditing Harness Tampering (arXiv:2609.00069)

### DO: Attribute failed rollouts to environment, task, verifier or policy before training on them

In synthesized tool-use environments, a failed rollout may come from a broken
tool, an infeasible task or a wrong verifier. Use state diffs, tool returns and
cross-harness patterns to attribute each failure. Repair only the responsible
component, rerun construction checks and fresh rollouts, and keep the repair
only through the acceptance gate (rules/recursive-improvement.md, "DO: Pass
every self-modification through one acceptance gate"). Repairs are made by a
separate evolution agent against executable evidence, never by the policy
under training (consistent with "DON'T: Let agents modify their own
evaluation harness", above).

**Scope:** WEFT tool-use post-training of Qwen3-8B/14B and Qwen3.5-35B-A3B
on 8,172 synthesized MCPs; Toolathlon-Verified, AutomationBench, Claw-Eval.

**Evidence**: with task set and rollout budget fixed, three repair rounds cut
the tool-error rate in selected trajectories from 1.76% to 0.96% and raised the
three benchmarks by 5.25, 4.33 and 3.65 points (WEFT-35B-A3B).

See also: skills/execution-driven-environment-repair/SKILL.md

> Source: WEFT: Scaling Tool-Use Post-Training for General-Purpose Agents (arXiv:2609.36887)

### DO: Test evaluators with counterfactual perturbations

Before trusting any automated evaluator (LLM judge, test suite,
benchmark), verify that it genuinely conditions on candidate content
by running counterfactual tests: flip the expected quality of the
candidate and confirm the evaluator's score changes accordingly. An
evaluator that produces the same score regardless of input quality is
measuring rubric artifacts, not output quality.

See also: rules/recursive-improvement.md — "DON'T: Rely on unperturbed rubric evaluators without counterfactual verification"

**Scope:** rubric-based LLM judges for text-generation evaluation (arXiv:2609.02942); extending the check to test suites and benchmarks is this repo's generalization, not measured.

> Source: arXiv:2609.02942

### DO: Measure safety compliance separately from accuracy

In safety-critical, physics-governed, or operational domains, accuracy
metrics (MAE, MSE, cosine similarity) mask dangerous failures.
Predictions numerically close to ground truth frequently violate hard
operational limits, physical feasibility constraints, or protocol
contracts. Gate candidate actions behind deterministic verification
of invariant safety boundaries before scoring accuracy.

**Scope:** 66 models on flight-trajectory prediction (arXiv:2609.04021); generalizes to domains with hard operational limits.

**Evidence**: across 66 evaluated models on flight trajectory prediction,
models with comparable predictive accuracy differed by more than 28
points in safety compliance score, exhibiting fatal boundary violations
while producing superficially plausible predictions.

See also: rules/agent-sandbox-safety.md — "DON'T: Evaluate safety-critical agent predictions by numeric accuracy alone"

> Source: FLY-EVAL++ (arXiv:2609.04021)

---

## Verification Scaling

### DO: Plan for verification tiers as agent capability increases

As agents improve, human supervision gradually recedes. Design
verification systems with explicit tiers:

| Tier | Verification Source | When to Use |
|:-----|:-------------------|:------------|
| **L0** | Per-instance human judgments | Novel tasks, highest-stakes decisions |
| **L1** | Reusable learned verifiers | Recurring task patterns with sufficient training data |
| **L2** | Autonomous reward models | Low-stakes, high-volume tasks with robust ground truth |

At each tier, monitor for:
- **Reward hacking**: model exploits verifier weaknesses
- **Feedback drift**: reward signal diverges from intended objective
- **Curriculum collapse**: self-generated training becomes repetitive

> Source: Scaling LRMs Beyond Human Supervision (arXiv:2608.31075)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`behavior-aware-verification`](../skills/behavior-aware-verification/SKILL.md) — Modification-scoped test selection
- [`trajectory-aware-eval-pruning`](../skills/trajectory-aware-eval-pruning/SKILL.md) — Cost-effective benchmark subset selection
- [`harness-tampering-audit`](../skills/harness-tampering-audit/SKILL.md) — Two-axis tampering audit for self-modifying agents
- [`error-structured-prompt-optimization`](../skills/error-structured-prompt-optimization/SKILL.md) — Evaluation-driven prompt refinement
- [`counterexample-guided-repair`](../skills/counterexample-guided-repair/SKILL.md) — Oracle-based artifact refinement
- [`neural-invariant-failure-diagnosis`](../skills/neural-invariant-failure-diagnosis/SKILL.md) — Behavioral state invariant checking
- [`agentic-review-deploy-loop`](../skills/agentic-review-deploy-loop/SKILL.md) — Layered review with checklist-based agentic review
- [`selective-step-verification`](../skills/selective-step-verification/SKILL.md) — Selective step-level action verification for coding agents

## Sources

- Rubric Artifacts in LLM Judges: arXiv:2609.02942
- Reliable Eval Pipeline: arXiv:2609.00805
- The Answer Is Not the Argument: arXiv:2609.00264
- HarnessLens: arXiv:2608.27311
- PTA-IRT: arXiv:2609.01603
- PatchBench: arXiv:2609.04075
- Auditing Harness Tampering: arXiv:2609.00069
- FLY-EVAL++: arXiv:2609.04021
- Scaling LRMs Beyond Supervision: arXiv:2608.31075
- CART: arXiv:2609.27336
- SecProbe: arXiv:2609.33763
- WEFT: arXiv:2609.36887
- Clinician-Led Verifiable Rule Guardrails: arXiv:2610.30690
- SecLog-Bench: arXiv:2610.31000
- BAC-Bench: arXiv:2610.34290
- CyberDual: arXiv:2610.34435
- Self-Improved Red Teaming (Self-Criticism vs External Proposal): arXiv:2610.34965
- Identically Trained Language Models Break on Different Jailbreaks: arXiv:2610.34074
- Model Organisms of Collusion: arXiv:2610.30582
