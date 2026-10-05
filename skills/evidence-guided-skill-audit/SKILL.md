---
name: evidence-guided-skill-audit
description: >
  Pre-screen third-party agent skill packages (instructions, code and
  resources) for malicious behavior with a small local model: extract
  security evidence deterministically, infer the declared purpose and
  expected capabilities, then have the model adjudicate each behavior
  against that purpose. A triage step before provenance checks and
  runtime containment, not an admission gate on its own.
  Derived from "SKILLLITE: Evidence-Guided Malicious Skill Auditing with
  Compact LLMs" (arXiv:2609.36879).
source: https://arxiv.org/abs/2609.36879
---

# Evidence-Guided Skill Audit

Use this skill when you vet agent skills from outside your organization
(marketplaces, public repos, other teams) and want a cheap, local,
explainable verdict per package before anyone installs it.

## When to Use

- Onboarding third-party skills into an agent's skill library or plugin set
- Re-auditing an installed skill library after an upstream update
- You need the audit to run on a compact local model (cost, privacy, or
  air-gapped review) rather than a frontier API
- A plain LLM "is this skill malicious?" prompt gives unstable or
  unexplained verdicts

## Core Insight

A security-sensitive operation (reading a file, opening a network
connection, running a command) is often legitimate in isolation and only
malicious relative to what the skill claims to do. Small models fail when
asked to find those behaviors and judge them in one pass. Split the work:
deterministic analyzers find the behaviors, the model states what the
skill is for, and the model then only answers whether each grounded
behavior is necessary for that purpose.

**Evidence** (arXiv:2609.36879, Gemma4:e4b as the auditing model):

- F1 0.905 on MalSkillBench (3,944 malicious + 4,000 benign skills),
  0.966 on SkillTrustBench (2,863 malicious + 1,643 benign real
  packages) and 0.807 on MASB (157 malicious + 299 benign behaviorally
  confirmed wild skills). On MalSkillBench the strongest baselines
  reached F1 0.850 (Tencent AI-Infra-Guard) and 0.764 (Cisco Skill
  Scanner, LLM mode).
- 27.4 s per skill on MalSkillBench and 19.4 s on MASB, which the
  authors report as 3.5x and 4.9x faster than the strongest baseline.
- Across Qwen3.5:9B, DeepSeek-R1:8B, Mixtral-8x7B and Gemma4:e4b, the
  pipeline improved F1 over direct zero-shot auditing in all 15
  model-benchmark configurations, by 9.2 to 73.6 percentage points.
- Ablation on SkillTrustBench: removing evidence extraction dropped F1
  to 0.485, removing intent analysis to 0.451, removing evidence
  synthesis to 0.743 (full pipeline 0.966).
- Residual errors are mostly false negatives (FNR 0.132 / 0.039 / 0.263
  against FPR 0.051 / 0.050 / 0.048 on the three benchmarks): behavior
  that looks consistent with the declared purpose, or that only appears
  at runtime.

**Caveat**: this is a static auditor evaluated against fixed benchmarks.
Iterative attackers who can query a deployed scanner drive it to near-zero
detection; see
[`skill-scanner-evasion-defensive-lessons`](../../research-briefs/skill-scanner-evasion-defensive-lessons.md).
Treat the verdict as triage.

---

## Procedure

### 1. Extract security evidence deterministically

Run non-LLM analyzers over every file in the package (instructions,
scripts, resources), covering four evidence classes:

| Class | Examples |
|:------|:---------|
| General security patterns | local file access, network activity, system command execution, permission changes |
| Language-aware code analysis | process invocation, network APIs, environment-variable access, dynamic execution |
| Concealed payloads | encoded payloads, hidden helper logic, payloads split across files, obfuscated execution |
| Agent-specific control signals | instructions that bypass approval or the sandbox, hijack control flow, or auto-confirm actions |

Analyze the package as a whole: behavior split across files is a known
blind spot of per-file review.

### 2. Infer declared purpose and expected capabilities

Give the compact model only the skill's specification (name,
description, instructions) and ask for structured output:
`declared_purpose` and `expected_capabilities` (the capabilities a
legitimate implementation of that purpose would reasonably need). Do this
before the model sees the evidence, so the expected capabilities are not
rationalized from what the code does.

### 3. Synthesize a grounded evidence report

For each finding record: the observed behavior, the source artifact
(file and location), the supporting snippet, surrounding context, and an
evidence-strength label. Attach the risk context: the declared purpose,
the expected capabilities, and any policy that applies (for example
"skills may not contact hosts outside the allowlist").

### 4. Adjudicate against the purpose

Ask the model, per finding:

1. **Functional necessity**: is this capability reasonably required by
   the declared purpose?
2. **Benign counterevidence**: does source-grounded evidence give a
   credible justification?
3. **Critical agentic risks** (approval or sandbox bypass, control-flow
   hijack, auto-confirmation): require direct, risk-specific
   counterevidence; general plausibility is not enough.

Output JSON with the suspicious-evidence review, benign counterevidence,
any abuse chain, `is_malicious`, a 0-100 confidence and reasoning. Keep
the report with the package for human review.

### 5. Route the verdict

- **Malicious**: reject; record the report.
- **Benign**: the package goes on to provenance and lineage checks
  (rules/skill-system-design.md, "Validate skill provenance before adding
  to library") and, for library admission, the acceptance gate in
  rules/recursive-improvement.md ("Pass every self-modification through
  one acceptance gate": no regression beyond a noise margin δ estimated
  from repeated baseline runs; the negative security testbed is strict,
  zero tolerance). See [`skill-evolution-defense`](../skill-evolution-defense/SKILL.md)
  Step 2.
- **Either way**, run admitted skills under runtime containment: the
  expected capabilities from Step 2 are a natural capability scope to
  enforce at execution time.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Purpose-consistent malice | Exfiltration hidden inside a capability the purpose legitimately needs | Enforce the Step 2 capability scope at runtime (egress allowlists, per-task scopes); static audit cannot see it |
| Runtime-only behavior | Payload fetched or assembled at execution time | Sandboxed execution with interception, e.g. [`universal-tool-defense`](../universal-tool-defense/SKILL.md) |
| Scanner used as an oracle | Submitter resubmits revisions until the verdict flips | Rate-limit and log resubmissions; do not return verdict detail to submitters |
| Payload in natural language | Malicious instruction in prose, so pattern analyzers find nothing | Keep the agent-specific control-signal class and the intent comparison; never pass a package on "no code findings" alone |
| Per-file review | Behavior split across files | Build the evidence report over the whole package (Step 1) |

## Cross-References

- [`skill-evolution-defense`](../skill-evolution-defense/SKILL.md): provenance, sandbox testing and admission for skills entering a library
- [`description-only-injection-detection`](../description-only-injection-detection/SKILL.md): the analogous pre-screen for tool and API descriptions
- [`skill-scanner-evasion-defensive-lessons`](../../research-briefs/skill-scanner-evasion-defensive-lessons.md): why any scanner must sit in front of other controls

> Source: SKILLLITE: Evidence-Guided Malicious Skill Auditing with Compact LLMs (arXiv:2609.36879)
