# Deconfliction Report: 2026-09-28

Scope: all 8 `rules/` files, all 96 skills, all 155 research briefs. Read-only
audit by three parallel reviewers; findings merged and de-duplicated. Items
marked **(verified)** were spot-checked against the files.

**Pattern.** Almost every conflict has the same cause: a paper's finding from
one setting (one benchmark, one model family, one topology) was written into a
rule as general guidance, and a later paper from a different setting was
written in as general guidance the other way. The fix is usually a scope
condition, not picking a winner.

---

## High

### H1. Editable, unfrozen self-improvement vs bounded, audited evolution
- A: `rules/recursive-improvement.md:11-42`: make the improvement mechanism editable, don't freeze it (HyperAgents, 2603.19461). `skills/recursive-self-improvement-loop/SKILL.md:78,115` (AIDE², 2609.26457): keep changes that raise selection-task scores; on stagnation, "expand editable surface".
- B: `rules/skill-system-design.md:321` (bound mutation scope/magnitude; unconstrained evolution is worse than none), `rules/recursive-improvement.md:442-457` (HyperAgents itself poisoned into `verify=False`, surviving clean generations, 2609.17817), `:240` (no aggregate-only acceptance).
- Why: a newer paper undermines the older rule's evidence *using the same system*.
- Fix: editability only inside a bounded envelope with an immutable negative security testbed; AIDE² step 3 requires security probes; drop "expand editable surface".

### H2. Same-family model pools vs diversity against shared misconceptions (verified)
- A: `rules/multi-agent-coordination.md:252`: restrict pools to one model family, 3–5 models (2609.17306).
- B: `rules/multi-agent-coordination.md:93`: homogeneous debaters converge on shared misconceptions (R²-MAD, 2609.03619); `:31` mixes models (2609.01045); briefs `value-preserving-agentic-architectures.md:35` (2609.03920) and `llm-group-consensus-overstatement.md` (2609.20543).
- Fix: scope 2609.17306 to routing/voting accuracy; any same-family pool used for debate or verification needs a dissent/diversity mechanism.

### H3. Transparent peer auditing vs withholding history from verifiers
- A: `rules/recursive-improvement.md:364`, `rules/multi-agent-coordination.md:154`: transparent channels, mutual monitoring (2609.04170).
- B: `rules/recursive-improvement.md:252-270`: no cumulative history or past outcomes for peer verifiers; collusion in 94% of trajectories (2609.24967).
- Fix: separate roles. Auditors get read-only, out-of-band access with no reward coupling; verifiers get task-scoped context only.

### H4. Broadcast bus vs damping hierarchy (same file)
- A: `rules/multi-agent-coordination.md:244`: replace manager-worker trees with a bus (BusMA, 2609.15054).
- B: `rules/multi-agent-coordination.md:264`: flat/broadcast topologies spread poisoned signals; use hierarchical coordinators (2609.19789); brief `orch-collective-intelligence.md` (2609.11737).
- Fix: BusMA is conditional on trusted inputs; untrusted feeds pass through a damping/cross-check layer before reaching the bus.

### H5. Ledger scaffold recommended for 14B–35B, but the same paper shows a 35B model hurt (verified)
- A: `rules/skill-system-design.md:351`: use file-ledger scaffolds for mid-sized 14B–35B models.
- B: `rules/recursive-improvement.md:380-384`, same paper (2608.26480): Qwen3.6-35B-A3B lost up to 9 points; "always benchmark per model family".
- Fix: add the sparse-MoE / low-active-parameter exception and the benchmark-per-family caveat to `:351`.

### H6. Three prompt optimizers, opposite procedures for the same job
- NPO `skills/iterative-instruction-refinement` (2608.27266) + `rules/skill-system-design.md:146`: one lineage, random minibatches, validation optional.
- ESPO `skills/error-structured-prompt-optimization` (2609.04197) + `rules/recursive-improvement.md:326`: never reflect on random single errors; 4 candidates + bootstrap stability selection, mandatory.
- CASD `skills/corpus-scale-prompt-distillation` (2609.26261): one corpus-wide pass, validation optional.
- Fix: a decision rule. ESPO for small validation sets or bloated prompts; NPO when a strong teacher and large task pool exist; CASD only as a first draft that must pass the acceptance gate (H7).

### H7. Acceptance gates range from "never regress" to "net positive"
- Strict: `skills/controlled-skill-lifecycle-management:79,83` (2609.19680), `rules/recursive-improvement.md:231,446`.
- Loose: `skills/intervention-guided-mas-prompt-optimization:96` (net positive), `skills/fast-tree-search-self-improvement:102`, `skills/knowledge-compounding-loop:165` (beats best score), `skills/dense-rubric-skill-evolution:89-90`, CASD (none).
- Fix: one acceptance gate in the rules (no regressions on previously-correct cases, behavioural evidence, negative security testbed); optimizer skills defer to it.

---

## Data integrity (fix regardless of the conflicts)

| Issue | Location | Status |
|:--|:--|:--|
| Identical stats ("56.05% … 4.33%") in two unrelated papers' skills | `skills/cost-aware-hierarchical-analysis:39-40` (2609.04820) and `skills/cve-history-executable-detection:45-46` (2609.05335) | verified; likely copied into the CVE skill |
| Miscitation: rule cites 2609.08175; text matches the 2609.09646 brief; no 2609.08175 source exists | `rules/skill-system-design.md:321-330` vs `research-briefs/robust-sgpo-harness-evolution.md` | verified |
| "GPT-5.6-Luna +10.6" isn't in the brief, which reports GPT-5.6-Terra +8.0 | `rules/recursive-improvement.md:384` vs `research-briefs/gvs5h-zero-shot-self-orchestration.md:35` | verified |
| "Matching Claude Fable 5" omits that Fable ran single-call without execution while Qwen got up to 10 test rounds | `rules/skill-system-design.md:355` | from brief |
| Golden-dataset threshold 0.95 (diagram, rule) vs 0.98 (code) | `skills/adk-eval-golden-dataset-ci:47,110`, `rules/adk-security-and-evaluation.md:118` | reported |
| Same paper, 23pp vs "up to 21%" | `rules/skill-system-design.md:71` vs `:112` (2608.19993) | reported |
| Broken `../../../../.gemini/config/skills/...` links | agentic-prompt-injection-search, cost-aware-hierarchical-analysis, cve-history-executable-detection, autonomous-research-to-launch-harness | reported |

---

## Medium

| # | Conflict | A | B | Suggested fix |
|:--|:--|:--|:--|:--|
| M1 | Don't optimize prompts with frozen weights vs many prompt-only rules | `recursive-improvement.md:297` (WHALE 2609.00196) | NPO `:163,176`, SkillLift `:407`, RSIAgent `:427`, `skill-system-design.md:146,160` | Add "when weights are trainable" |
| M2 | Change-specific test selection vs full frozen suites | `agent-evaluation-quality.md:59`, `recursive-improvement.md:219` (HarnessLens) | `adk-security-and-evaluation.md:98`, `recursive-improvement.md:446`, `skill-system-design.md:326` | Selected tests while searching; full frozen and security suites at acceptance and deploy |
| M3 | Evidence isn't authorization vs autonomous fix/sanction loops | `agent-human-interaction.md:112` | `adk-workflow-architecture.md:190`, `recursive-improvement.md:271`, `multi-agent-coordination.md:164` | Pre-granted bounded scope counts as the gate; sanction or revocation powers need an explicit grant |
| M4 | Natural language vs typed inter-agent interfaces | `multi-agent-coordination.md:50` (2608.26788, embodied planner) | `:244`, `adk-workflow-architecture.md:18,190`, `recursive-improvement.md:396` | NL payloads inside typed envelopes; scope to planner→controller |
| M5 | RSI "nothing fundamental" bounds it vs RSI is bounded | `recursive-improvement.md:50-59` (2608.20318) | `skill-system-design.md:336` (2609.11873), brief 2609.00137 | Reword: no hardware/data ceiling; still subject to evaluator and difficulty damping |
| M6 | Correlated layer failure vs rules that each add a layer | `agent-sandbox-safety.md:158,181` (2608.28327) | `:365,383,434`, `adk-security-and-evaluation.md:11` | Every new layer passes an end-to-end false-refusal budget |
| M7 | Prompts/skills transfer across models vs benchmark per model | `recursive-improvement.md:176`, `skill-system-design.md:160` | `recursive-improvement.md:380`, briefs 2609.24974, 2609.20804 | "Test on each deployment target before reuse" |
| M8 | Self-verification without external verifiers vs never sole certifier | `skills/self-verification-elicitation:21-23,57-59` (2609.08025) | `recursive-improvement.md:249,292,343` | Frame the skill as a complement to external verification, not a substitute |
| M9 | Optimize against a frozen rubric vs rubric artifacts | `recursive-improvement.md:407` (SkillLift 2609.15396) | `:342`, `agent-evaluation-quality.md:12,120` | Add counterfactual perturbation checks to SkillLift's outer loop |
| M10 | "Revocation propagates immediately" vs revocation is insufficient | `skills/multi-agent-federation-governance:56,85` (PRIMUS 2609.07910) | `skills/auth-revocation-quiescence:35-38` (2609.21284) | PRIMUS step 5 points to the quiescence protocol |
| M11 | Human review happens only if an LLM reviewer prints ESCALATE | `skills/agentic-review-deploy-loop:97,155-164` | `adk-workflow-architecture.md:11`, `agent-sandbox-safety.md:550` | Deterministic path/diff triggers (auth, crypto, CI) force human review |
| M12 | Pick a winner (Bayesian 2×) vs keep both interpretations | `skills/bayesian-backward-disagreement-anchor:53` | `skills/debate-layer-disagreement-analysis:59-60,106` | Classify the disagreement first; Bayesian anchor for factual disputes only |
| M13 | Top-k is fine below 10 skills vs below 30; graph-of-skills truncates by score | `skills/capability-aware-skill-selection:215,223`, `skill-system-design.md:84` | `skills/graph-of-skills-scaling:52,58,107` | Graph-of-skills hands its candidates to BPS set selection |
| M14 | "0% attack success" with no adaptive-adversary caveat | `skills/universal-tool-defense:7,36` | `agent-sandbox-safety.md:158,238,550`; red-teaming briefs (79% evasion) | Qualify as a static-benchmark result; require adaptive red-teaming |

## Low

- Hidden final evaluator (`recursive-improvement.md:87`) vs oracle counterexamples fed to the agent (`:334`, `:163`). Say the search oracle and the final evaluator must be different.
- Speculative pre-execution (`skill-system-design.md:295`, `agent-sandbox-safety.md:80`) vs irreversible actions (`agent-sandbox-safety.md:16,36`). Speculate only on side-effect-free steps.
- "Add reasoning budget" (`recursive-improvement.md:122`) vs runaway loops in mid-sized models (`skill-system-design.md:353`). Add a loop guard.
- No raw rationale to blocking monitors (`agent-sandbox-safety.md:536`) vs guard agents that read intermediate messages (`:383`, `multi-agent-coordination.md:176`). Apply schema-delimited serialization to guard agents too.
- Keep only the last 5 refuted hypotheses (`skills/belief-calibrated-scaffold-optimization:107`) vs a never-reset knowledge layer (`skills/knowledge-compounding-loop:74,169`). Compact refuted hypotheses into principles instead of deleting them.
- Reset context every turn (`skills/ledger-orchestrated-coding-loop:176-196`) vs cumulative witness history (`skills/counterexample-guided-repair:69,112`). Keep witnesses in `notes.md`.
- Repeat runs under noise: 2 runs (SkillAA), 3 (BCO), "multiple" (HarnessLens).
- Internal: `skills/dependency-scoped-plan-validation:80-81` (exactly one replan vs escalate after more than 2); `skills/covert-tool-injection-defense:59` vs `:128` (strip vs flag); `skills/adk-model-armor-interceptor:169` (selective inspection) vs `agent-sandbox-safety.md:253` (sanitize all tool outputs).

## Duplicates (merge or cross-link; they will drift)

Guard agents (`agent-sandbox-safety:383` / `multi-agent-coordination:176`) ·
ground-truth to monitors (`agent-evaluation-quality:42` / `agent-sandbox-safety:312`) ·
PatchBench (`agent-evaluation-quality:85` / `agent-sandbox-safety:357`) ·
FLY-EVAL++ (`agent-evaluation-quality:131` / `agent-sandbox-safety:391`) ·
harness tampering (`agent-evaluation-quality:105` / `agent-sandbox-safety:292`) ·
conversational authentication (`agent-human-interaction:209` / `agent-sandbox-safety:349`) ·
door-in-the-face (`agent-human-interaction:192` / `agent-sandbox-safety:222,333`) ·
rubric artifacts (`agent-evaluation-quality:12,120` / `recursive-improvement:342`) ·
HarnessLens (`agent-evaluation-quality:59` / `recursive-improvement:219`) ·
DoCtOR (`multi-agent-coordination:126` / `recursive-improvement:194`) ·
AgentScope (`multi-agent-coordination:139` / `recursive-improvement:350`) ·
Ostrom governance (`multi-agent-coordination:154` / `recursive-improvement:364`) ·
R²-MAD (`multi-agent-coordination:93` / `recursive-improvement:372`) ·
NLIP (`multi-agent-coordination:65` / `skill-system-design:309`) ·
NPO (`recursive-improvement:163` / `skill-system-design:146`) ·
insufficient vs conflicting evidence (`skill-system-design:192` / `:226`) ·
deterministic steps first (`adk-workflow-architecture:36` / `skill-system-design:363`) ·
typed `finish_task` (`adk-workflow-architecture:190` / `recursive-improvement:396` / `skill-system-design:367`) ·
compensating transactions (`agent-sandbox-safety:36` / `:494`).

---

## This week's papers that bear on these conflicts

From the 2026-09-22 → 09-28 scan (170 NEW candidates). Relevance judged from
titles and abstracts only; ingest these first so the fixes can cite them.

| Paper | Likely bears on |
|:--|:--|
| 2609.24972 RRSI: Regularized Recursive Self-Improvement of Agent Harnesses | H1 |
| 2609.31186 Evolutionary Safety of Recursive Self-Improving AI | H1, M5 |
| 2609.24663 Process-Level Evaluation of Self-Evolving Agents | H7 |
| 2609.22497 The Wisdom of Artificial Deliberative Crowds | H2 |
| 2609.30028 How does Adversarial Influence Scale in Multi-Agent Systems? | H4 |
| 2609.31121 Monitor Jailbreaking / 2609.30217 Instrumental Monitor Evasion | CoT-monitoring rules, M14 |
| 2609.22818 The Price of Safety (memory-poisoning defense overhead) | M6 |
| 2609.26176 Refusing Everything Looks Safe | M6, false-refusal budget |

## Process suggestion

To stop this recurring as more papers come in:
1. Every rule gets a one-line **Scope:** (setting, model class, benchmark) under its heading.
2. The ingest skill gains a deconfliction step: before adding a DO/DON'T, grep existing headings for the same subject and an opposing verb, then either scope both or add a "Tension with" cross-reference.
3. Rerun this audit after each weekly batch.
