# Ajar: Measuring Open Privilege in Agent Defenses

> **Source**: Sharma, Jiang, Lin & Chen, arXiv:2609.26900, Sep 2026
> **Status**: Research Brief — evaluation metric and measurement study (AgentDojo, 5 defenses)

## Why Not a Skill?

Ajar is an evaluation instrument added onto an existing benchmark. It generates labelled "unneeded call" tests and scores defenses on them. The lesson for Praxis is an evaluation criterion (report a third axis), not a procedure an agent executes.

## Core Concept

Agent-security benchmarks score a tool-call defense on two numbers: how many injected attacks succeed and how much benign utility survives. Both measure only what the agent actually did. A defense can do well on both "while holding open a transfer, a deletion or a broad read that no task needed". Ajar measures that **open privilege** directly. For each benign task it takes the reference solution and, at every decision point, builds candidate calls the task does not need (off-path tools, argument faults, attacker-seeded calls). It then asks the defense whether it would allow each one. Scores:

- **Over-Privilege Leakage (OPL)**: harm-weighted fraction of unneeded calls allowed. Weights by reversibility and reach: reversible self-scoped 1, reversible third-party 3, irreversible self-scoped 9, irreversible with funds or third parties 27.
- **Sufficiency**: fraction of required calls allowed.
- **Over-restriction**: calls the task was entitled to make but was denied.
- **Attack admission**: attack sinks the defense would allow.

## Key Findings

- **Scale**: 10,471 tests from 3,551 unique (task, tool, arguments) triples over 97 AgentDojo tasks; 609 planted attacks. Only 27.0% of labels are validated directly by the host benchmark; Ajar asserts the rest.
- **Defenses leave very different amounts of privilege open** (deciding model Sonnet-5): Permission Assistant OPL **0.0810**, CaMeL **0.0895**, Progent **0.1026**, AC4A **0.1113**, Claude Code Auto mode **0.3009**. Reference points: argument-exact oracle 0.0020, tool-name allowlist **0.3551**, allow-all 1.0.
- **OPL cannot be predicted from utility**: "Two of the defenses we measure leak by amounts that differ by less than 0.009 and yet differ by 37 points of benign task completion". Benign-completion cost ranged from 0.0 pp (Progent, Sonnet-5) to −46.4 pp (AC4A, Haiku-4.5).
- **Tightness bought with over-restriction**: CaMeL denied 41.5% (Sonnet-5) of entitled calls; Permission Assistant denied 8.8% and still leaked less.
- **Attack success no longer separates defenses**: AgentDojo's `important_instructions` attack "does not succeed against our undefended agent", so a defended rate of zero shows no regression, not protection. Attack admission still ranged from 16/609 (CaMeL) to 46/609 (AC4A), and was 74/581 for Auto mode.
- **The deciding model matters**: switching Sonnet-5 to Haiku-4.5 loosened three of four defenses (Permission Assistant 0.0810 → 0.1289) and lowered sufficiency.
- **Runtime narrowing helps**: freezing Progent's initial policy (no update on tool results) raised OPL 1.56× (Sonnet-5) and 1.24× (Haiku-4.5) with sufficiency almost unchanged.
- **Model-based verdicts are not deterministic**: 91.2–98.1% verdict agreement across repeated runs, so defenses adjacent in a ranking can swap places. One run does not settle an OPL comparison.
- **Harm weights change magnitude, not ranking much**: Kendall's τ vs default weighting 0.673 (unweighted) to 0.927 (base-4).
- **Limits**: replayed reference traces, not live agents; only candidate calls from the environment, the reference solution and planted injections; no latency or token cost reported.

## Relevance to Praxis

- **M14 (0% attack success without an adaptive-adversary caveat)**: independent support for qualifying `universal-tool-defense`. Low or zero ASR on a benchmark whose attacks already fail against the undefended agent is not evidence of tightness.
- **M6 (false-refusal budget)**: over-restriction is the agent-level counterpart of false refusal, and it moves independently of leakage. A layer-by-layer false-refusal budget should be paired with a leakage metric so neither is gamed (deny-all scores OPL 0; allow-all scores sufficiency 1).
- Supports argument-level authorization over tool-name allowlists (tool-name allowlist leaks 0.3551): see [`mcp-zero-trust-tool-authorization`](../skills/mcp-zero-trust-tool-authorization/SKILL.md), [`runtime-resource-authorization-bounds`](../skills/runtime-resource-authorization-bounds/SKILL.md), [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md).
- The frozen-Progent result is in tension with frozen-policy designs such as [`verified-policy-action-governance`](../skills/verified-policy-action-governance/SKILL.md) (ActGov, 2609.24446): a policy frozen without runtime narrowing must be argument-level tight from the start and scored on OPL before it is frozen. Recorded as a Tension line under `rules/agent-sandbox-safety.md` "DO: Confine the LLM to bounded record extraction and authorize against a verified, frozen policy".
- Complements brief [`red-teaming-auto-mode-blocking-monitors`](red-teaming-auto-mode-blocking-monitors.md), which reports a separate weakness of the same Auto-mode classifier.

> Source: Sharma et al., "Ajar: Measuring Open Privilege in Agent Defenses" (arXiv:2609.26900)
