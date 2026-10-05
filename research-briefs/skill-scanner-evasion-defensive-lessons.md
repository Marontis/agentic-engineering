# Malicious-Skill Scanners Under Iterative Evasion: Defensive Lessons

> **Sources**:
> SkillDRE: Dual-Stage Red-Team Evolution of Agent Skills via Pre-Execution and Runtime Feedback, [arXiv:2609.32400](https://arxiv.org/abs/2609.32400), Sep 2026;
> Pretext: Defeating Malicious Skill Detection Frameworks for AI Agents, [arXiv:2609.39607](https://arxiv.org/abs/2609.39607), Sep 2026
> **Status**: Research Brief, defensive lessons only. Both papers are attack
> papers; this brief deliberately omits how the malicious skills are built
> or revised (see the repo's `AGENTS.md`).

## Why Not a Skill?

Both papers describe attacker loops that revise a malicious skill until
scanners pass it. Writing that up as a procedure would be an evasion
playbook. What transfers is the defender's side: which detector designs
fail under iteration, and what to put behind them.

## Core Concept

Third-party agent skills (instructions, code and resources in one package)
are vetted today by a **pre-execution scanner** (static rules plus LLM
review of each file) and sometimes a **runtime defense**. Both papers show
that if an attacker can query the deployed detector repeatedly, the
detector becomes the attacker's optimization signal, and pass rates climb
within a handful of rounds.

## Key Findings

**SkillDRE** (SkillsBench, 249 skills and 94 tasks; scanner SkillScan with a
Qwen3.5-397B backend; runtime defense SkillSonar; victims DeepSeek-V4-Pro,
GLM-5.2, Qwen3.5-397B, Gemini-3.7-Flash; Codex harness):

- Average attack success 45.28% (per victim 43.78–46.99%), against
  0.00–9.00% for prior skill-attack baselines, with **0% SkillScan
  detection** of the final packages versus 97.34–100% for baselines.
- Scanner acceptance came fast: 3.23 rounds on average; 84.34% of
  task–skill pairs accepted by round 5 and 95.18% by round 10.
- Benign task accuracy moved only −3.58 to +2.14 points, so utility checks
  would not flag the skill.
- Scanner-clean alone was not enough for the attacker (34.54–37.35% success
  before runtime feedback); runtime feedback alone left 79.92% detection.
  Joint feedback from both layers is what broke the pair, so testing the
  layers separately overstates their combined strength.
- Limitations: four victims, one benchmark, fixed attacker model, 30 + 10
  round budgets, about half the targets (125 of 249) human-validated,
  72.29% of targets exfiltration-related.

**Pretext** (NVIDIA SkillSpector v2.2.3; detector backends qwen3t, glm,
gpt-oss; 12 trojan behavior types; 5 replicates):

- Against a frozen detector, evasion reached 96.7% (qwen3t), 63.2% (glm)
  and 70.5% (gpt-oss).
- The deterministic layer (regex, AST, taint, YARA) flagged only 5.6% of
  final-generation skills: it matches code patterns, and the payload moved
  into natural language.
- Per-file LLM review misses behavior split across files.
- When the detector also adapted (co-evolution), false-negative rates stayed
  at 47–78% while false positives rose to 18–20% (glm), 30–40% (qwen3t) and
  50–62% (gpt-oss): tightening the detector mostly bought false alarms.

## Defensive Takeaways

- **A skill scanner is a triage filter, not an admission gate.** Admit
  third-party skills on provenance and lineage
  (rules/skill-system-design.md, "Validate skill provenance before adding to
  library"), and assume some malicious skills pass the scanner.
- **Constrain what an admitted skill can do at execution time**: tight
  capability scopes per task, sandboxed execution where every action is
  intercepted, and egress limits. See
  [universal-tool-defense](../skills/universal-tool-defense/SKILL.md),
  [verified-policy-action-governance](../skills/verified-policy-action-governance/SKILL.md)
  and [skill-evolution-defense](../skills/skill-evolution-defense/SKILL.md).
- **Do not give submitters unlimited scanner queries or verdict detail.**
  Both attacks relied on repeated access to the deployed detector's output.
  Rate-limit and log resubmissions, and watch for many near-identical
  revisions of one package (same lesson as rules/agent-sandbox-safety.md,
  "Treat compact prompt-injection classifiers as intent detectors, or expose
  their scores").
- **Review skills as a package, not file by file.**
- **Red-team the assembled pipeline with an adaptive attacker**
  ([closed-loop-adaptive-red-teaming](../skills/closed-loop-adaptive-red-teaming/SKILL.md)),
  and score false positives on benign skills alongside detection.

## Relevance to Praxis

- Supports existing rules on provenance, adaptive red-teaming and not
  exposing detector scores; introduces a proposed scope note that
  pre-execution scanners are not sufficient as the sole skill gate.

> Source: SkillDRE (arXiv:2609.32400); Pretext (arXiv:2609.39607)
