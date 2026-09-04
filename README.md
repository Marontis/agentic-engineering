# Agentic Engineering

Research-backed rules, skills, and spec templates for building LLM agent systems -- distilled from 105 arXiv papers and counting.

> **What this is**: A curated knowledge base of transferable procedures, design rules, and decision frameworks for agent engineering. Every rule cites its evidence. Every skill describes a reusable procedure you can drop into your agent workflows.

> **What this isn't**: A framework, library, or SDK. This is *knowledge*, not code. Load it into your AI coding assistant's context (rules, skills) or use the spec templates when starting a new project.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Quick Start

**For AI coding assistants** (Antigravity, Claude Code, Cursor, etc.):

1. Copy `rules/` into your project's `.agents/rules/` (or equivalent) -- they'll be active during every session
2. Copy `skills/` into your project's `.agents/skills/` -- they'll be retrieved on-demand when relevant
3. Fill in a `specs/` template when starting a new project in a covered domain

**For humans**: Browse the rules for decision criteria and pitfalls, read the skills for step-by-step procedures, or start from a spec template to map out your design space.

---

## What's Inside

### Rules (Always Active)

Concise, evidence-backed guardrails. Load these so your agent applies them automatically during every coding session.

| Rules File | Domain |
|:-----------|:-------|
| [`agent-sandbox-safety`](rules/agent-sandbox-safety.md) | Sandbox design, command classification, network policy, capability gateway, defense composition, checkpoint integrity, deployment context, adversarial testing, tool output safety, GitOps span editing, harness tampering audit, blind CoT monitoring, hook security, multi-turn refusal variance, dependency-scoped plan lineage |
| [`skill-system-design`](rules/skill-system-design.md) | Skill authoring, selection, library management, skill evolution, training data quality, evidence triage, library integrity, hallucination detection, prefix-preserving context assembly, persistent agent architecture, procedural families, operational know-how distillation, speculative macro commit |
| [`recursive-improvement`](rules/recursive-improvement.md) | Self-modification architecture, change classification, evaluation, instruction refinement, targeted reflection, verification, multi-day autonomous loops, joint harness-weight optimization, reference trajectory evolution, error-structured prompt optimization (ESPO), counterexample-guided repair, rubric artifact bias, neural invariant diagnosis, belief-calibrated scaffold optimization |

### Skills (On-Demand)

Transferable, subtask-level procedures. Each skill has a `SKILL.md` with when-to-use criteria, a step-by-step procedure, environment caveats, and failure modes.

#### Agent Sandboxing & Security

| Skill | Source Paper |
|:------|:------------|
| [`browser-agent-http-sandbox`](skills/browser-agent-http-sandbox/SKILL.md) | ceLLMate (arXiv:2512.12594) |
| [`speculative-sandbox-scheduler`](skills/speculative-sandbox-scheduler/SKILL.md) | SpecBox (arXiv:2607.23933) |
| [`transactional-coding-sandbox`](skills/transactional-coding-sandbox/SKILL.md) | Fault-Tolerant Sandboxing (arXiv:2512.12806) |
| [`unified-capability-gateway`](skills/unified-capability-gateway/SKILL.md) | CrabOS (arXiv:2608.28165) |
| [`layered-defense-ensemble`](skills/layered-defense-ensemble/SKILL.md) | Layered LLM Defenses (arXiv:2608.28327) |
| [`covert-tool-injection-defense`](skills/covert-tool-injection-defense/SKILL.md) | Covert Indirect Prompt Injection (arXiv:2608.30362) |
| [`skill-evolution-defense`](skills/skill-evolution-defense/SKILL.md) | EvoSkill Injection (arXiv:2608.30429) |
| [`self-improving-red-team`](skills/self-improving-red-team/SKILL.md) | SIR Red-teaming (arXiv:2608.30207) |
| [`deterministic-span-editing`](skills/deterministic-span-editing/SKILL.md) | Minimal-Diff GitOps Remediation (arXiv:2609.00227) |
| [`harness-tampering-audit`](skills/harness-tampering-audit/SKILL.md) | Auditing Harness Tampering (arXiv:2609.00069) |
| [`dependency-scoped-plan-validation`](skills/dependency-scoped-plan-validation/SKILL.md) | PlanFence (arXiv:2609.03340) |
| [`black-box-trajectory-risk-monitoring`](skills/black-box-trajectory-risk-monitoring/SKILL.md) | Web Agent Key-Step Monitoring (arXiv:2609.02057) |

#### Self-Improvement & Evaluation

| Skill | Source Paper |
|:------|:------------|
| [`hyperagent-self-improvement`](skills/recursive-self-improvement/hyperagent-self-improvement/SKILL.md) | HyperAgents (arXiv:2603.19461) |
| [`algorithmic-design-evaluation`](skills/recursive-self-improvement/algorithmic-design-evaluation/SKILL.md) | AI4AI-Bench (arXiv:2608.20318) |
| [`targeted-failure-attribution`](skills/targeted-failure-attribution/SKILL.md) | DoCtOR (arXiv:2608.28264) |
| [`behavior-aware-verification`](skills/behavior-aware-verification/SKILL.md) | HarnessLens (arXiv:2608.27311) |
| [`agent-working-memory-eval`](skills/agent-working-memory-eval/SKILL.md) | Measure Before You Manage (arXiv:2608.31057) |
| [`reference-trajectory-harness-evolution`](skills/reference-trajectory-harness-evolution/SKILL.md) | HarnessEvolve (arXiv:2609.00829) |
| [`trajectory-aware-eval-pruning`](skills/trajectory-aware-eval-pruning/SKILL.md) | PTA-IRT Benchmarking (arXiv:2609.01603) |
| [`error-structured-prompt-optimization`](skills/error-structured-prompt-optimization/SKILL.md) | ESPO (arXiv:2609.04197) |
| [`counterexample-guided-repair`](skills/counterexample-guided-repair/SKILL.md) | A-CEGIS (arXiv:2609.02892) |
| [`neural-invariant-failure-diagnosis`](skills/neural-invariant-failure-diagnosis/SKILL.md) | AgentScope (arXiv:2609.02371) |
| [`belief-calibrated-scaffold-optimization`](skills/belief-calibrated-scaffold-optimization/SKILL.md) | BCO (arXiv:2609.01861) |

#### Skill Evolution & Knowledge

| Skill | Source Paper |
|:------|:------------|
| [`knowledge-compounding-loop`](skills/knowledge-compounding-loop/SKILL.md) | WikiSkill (arXiv:2608.27454) |
| [`iterative-instruction-refinement`](skills/iterative-instruction-refinement/SKILL.md) | NPO (arXiv:2608.27266) |
| [`skill-design-methodology`](skills/skill-design-methodology/SKILL.md) | Break It Down, Pass It On (arXiv:2608.20274) |
| [`capability-aware-skill-selection`](skills/capability-aware-skill-selection/SKILL.md) | Optimal Skill Selection (arXiv:2608.19993) |
| [`policy-centroid-routing`](skills/policy-centroid-routing/SKILL.md) | Policy-Centroid Routing (arXiv:2608.30757) |
| [`governed-knowledge-graph`](skills/governed-knowledge-graph/SKILL.md) | MAGG Governed KGs (arXiv:2608.28642) |
| [`agentic-data-cracking`](skills/agentic-data-cracking/SKILL.md) | Token-Efficient Data Reasoning (arXiv:2608.31082) |
| [`prefix-preserving-context-assembly`](skills/prefix-preserving-context-assembly/SKILL.md) | ContextPipe (arXiv:2609.00749) |
| [`persistent-agent-migration`](skills/persistent-agent-migration/SKILL.md) | Enoch Persistent Agents (arXiv:2609.00546) |
| [`requirements-driven-code-generation`](skills/requirements-driven-code-generation/SKILL.md) | WiseSpec (arXiv:2609.00568) |
| [`procedural-family-skill-consolidation`](skills/procedural-family-skill-consolidation/SKILL.md) | SkillGLoW (arXiv:2609.02217) |
| [`speculative-macro-commit`](skills/speculative-macro-commit/SKILL.md) | Speculative Macro Commit (arXiv:2609.03236) |

#### Retrieval & Evidence

| Skill | Source Paper |
|:------|:------------|
| [`rag-evidence-triage`](skills/rag-evidence-triage/SKILL.md) | Knowing Before Answering (arXiv:2608.27661) |
| [`hallucination-mean-shift-probe`](skills/hallucination-mean-shift-probe/SKILL.md) | Hallucination Mean Shift (arXiv:2608.28930) |
| [`rag-hallucination-repair`](skills/rag-hallucination-repair/SKILL.md) | RAG Hallucination Repair (arXiv:2608.29307) |
| [`cost-effective-repo-exploration`](skills/cost-effective-repo-exploration/SKILL.md) | Cost-Effective Repo Exploration (arXiv:2608.29675) |

### Spec Templates (Project Kickoff)

Structured decision frameworks to fill in when starting a new project. Each template surfaces research-backed decision points with evidence notes.

| Template | Domain |
|:---------|:-------|
| [`agent-sandbox.spec`](specs/agent-sandbox.spec.md) | Designing agent execution sandboxes |
| [`skill-library.spec`](specs/skill-library.spec.md) | Designing skill memory systems for LLM agents |
| [`self-improving-agent.spec`](specs/self-improving-agent.spec.md) | Designing self-modifying agent systems |

### Research Briefs

Papers that provide valuable context but don't produce standalone skills:

| Brief | Why It's Here |
|:------|:-------------|
| [`ai-agency-typology`](research-briefs/ai-agency-typology.md) | Legal vs moral agency framework for AI accountability |
| [`agentic-data-quality-framework`](research-briefs/agentic-data-quality-framework.md) | ACE lens for assessing agentic training data quality |
| [`planner-controller-decoupling`](research-briefs/planner-controller-decoupling.md) | Architectural pattern for real-time agent systems |
| [`agent-control-cycle-benchmark`](research-briefs/agent-control-cycle-benchmark.md) | Evaluation taxonomy for iterative agent control |
| [`agentic-os-interface-design`](research-briefs/agentic-os-interface-design.md) | Interface principles from String and CrabOS |
| [`knowledge-conditioned-topology`](research-briefs/knowledge-conditioned-topology.md) | Dynamic multi-agent collaboration topologies |
| [`llm-agents-security-survey`](research-briefs/llm-agents-security-survey.md) | Comprehensive reference for agent security domains |
| [`adversarial-probe-verification`](research-briefs/adversarial-probe-verification.md) | Model integrity verification via adversarial probes |
| [`scaling-lrms-beyond-supervision`](research-briefs/scaling-lrms-beyond-supervision.md) | L0–L4 ladder for scaling LRMs beyond human oversight |
| [`entropy-space-theory`](research-briefs/entropy-space-theory.md) | Information-theoretic framework for deep learning |
| [`science-sandbox-benchmark`](research-briefs/science-sandbox-benchmark.md) | Sandboxed evaluation of AI scientific reasoning |
| [`baitbench-reward-hacking`](research-briefs/baitbench-reward-hacking.md) | Benchmark for agent reward hacking with planted shortcuts |
| [`apiflow-dependent-workflows`](research-briefs/apiflow-dependent-workflows.md) | Agent survival on long dependent API chains |
| [`agentlogs-cloud-agent-traces`](research-briefs/agentlogs-cloud-agent-traces.md) | Real-world traces from GitHub's cloud coding agent |
| [`knowledge-gated-agent-tasks`](research-briefs/knowledge-gated-agent-tasks.md) | Separating knowledge gaps from execution gaps |
| [`ideation-arena-research-eval`](research-briefs/ideation-arena-research-eval.md) | Elo-style evaluation of LLM-generated research ideas |
| [`content-ecosystem-ranking-effects`](research-briefs/content-ecosystem-ranking-effects.md) | How ranking optimization degrades content ecosystems |
| [`ai-text-detection-token-filtering`](research-briefs/ai-text-detection-token-filtering.md) | When token filtering helps/fails AI text detection |
| [`collapsed-sequence-score-recovery`](research-briefs/collapsed-sequence-score-recovery.md) | Recovering evidence from collapsed LLM sequence scores |
| [`hidden-state-divergence-tracking`](research-briefs/hidden-state-divergence-tracking.md) | Detecting reasoning drift via hidden-state trajectories |
| [`multi-solver-disagreement-rewards`](research-briefs/multi-solver-disagreement-rewards.md) | Disagreement-based rewards for self-evolving curricula |
| [`judge-panel-deliberation`](research-briefs/judge-panel-deliberation.md) | Multi-reward panel deliberation for compact LLM judges |
| [`deployment-dependent-safety`](research-briefs/deployment-dependent-safety.md) | Safety behavior changes with deployment context |
| [`rollback-attack-continuity`](research-briefs/rollback-attack-continuity.md) | Breaking agent execution via checkpoint manipulation |
| [`mcts-coding-agent`](research-briefs/mcts-coding-agent.md) | MCTS-based action selection for coding agents |
| [`ontology-learning-scale`](research-briefs/ontology-learning-scale.md) | When bigger models help (and don't) for ontology learning |
| [`searchwiki-active-seeking`](research-briefs/searchwiki-active-seeking.md) | Wiki-structured knowledge building during information seeking |
| [`test-time-prompt-calibration`](research-briefs/test-time-prompt-calibration.md) | Calibration-aware test-time prompt tuning |
| [`harness-of-harness-autonomous-development`](research-briefs/harness-of-harness-autonomous-development.md) | Multi-day autonomous development with continual improvement |
| [`agent-factory-workflow-optimization`](research-briefs/agent-factory-workflow-optimization.md) | Automated optimization of multi-agent topologies and models |
| [`checklist-aggregation-eval-pipeline`](research-briefs/checklist-aggregation-eval-pipeline.md) | Decomposed checklist aggregation for reliable LLM evals |
| [`drift-aware-llm-routing`](research-briefs/drift-aware-llm-routing.md) | Routing across model portfolios under shared budgets and drift |
| [`quantum-federated-learning-aggregation`](research-briefs/quantum-federated-learning-aggregation.md) | Stable aggregation for quantum neural network parameters |
| [`assistant-ideal-self-concept`](research-briefs/assistant-ideal-self-concept.md) | Post-training self-concept elicitation and value stability |
| [`cot-monitoring-answer-bias`](research-briefs/cot-monitoring-answer-bias.md) | Measuring bias when oversight monitors have answer access |
| [`recursive-self-improvement-criticality`](research-briefs/recursive-self-improvement-criticality.md) | Criticality thresholds in dynamical self-improvement systems |
| [`verbal-reinforcement-learning-taxonomy`](research-briefs/verbal-reinforcement-learning-taxonomy.md) | Taxonomy of natural language feedback across agent lifecycles |
| [`byzantine-placement-decentralized-fl`](research-briefs/byzantine-placement-decentralized-fl.md) | Adversarial node placement in decentralized federated learning |
| [`embodied-vla-skill-orchestration`](research-briefs/embodied-vla-skill-orchestration.md) | Proposal-validation-recovery runtime for embodied VLA agents |
| [`predictive-coding-boundary-optimization`](research-briefs/predictive-coding-boundary-optimization.md) | Boundary-first inference schedules in predictive coding |
| [`rank-heterogeneous-federated-lora`](research-briefs/rank-heterogeneous-federated-lora.md) | Federated LoRA under client rank heterogeneity |
| [`activation-matched-finetuning-detection`](research-briefs/activation-matched-finetuning-detection.md) | Unsupervised dormant backdoor detection via activation residuals |
| [`joint-harness-weight-optimization`](research-briefs/joint-harness-weight-optimization.md) | Alternating harness search and weight updates (WHALE) |
| [`workload-aware-column-imprint-joins`](research-briefs/workload-aware-column-imprint-joins.md) | Real-time edge query processing with workload-aware column imprints |
| [`attention-sensitivity-dissociation`](research-briefs/attention-sensitivity-dissociation.md) | Dissociating attention proxies from behavioral in-context learning |
| [`hookpry-lifecycle-hook-vulnerabilities`](research-briefs/hookpry-lifecycle-hook-vulnerabilities.md) | Exploiting and sandboxing agent lifecycle hook update vectors |
| [`repo-to-skill-distillation`](research-briefs/repo-to-skill-distillation.md) | Distilling GitHub repos into operational skills for autonomous agents |
| [`rubric-artifact-bias-in-llm-judges`](research-briefs/rubric-artifact-bias-in-llm-judges.md) | Demonstrating rubric-only prediction and counterfactual judge failures |
| [`door-in-the-face-model-refusals`](research-briefs/door-in-the-face-model-refusals.md) | Sequential request retreat effects across model provider families |
| [`reliable-enterprise-agent-deployment`](research-briefs/reliable-enterprise-agent-deployment.md) | Scale AI framework for enterprise agent reliability and guardrails |
| [`flowbalance-verifier-grounded-self-improvement`](research-briefs/flowbalance-verifier-grounded-self-improvement.md) | Verifier-grounded trajectory balance preventing mode collapse |
| [`potential-guided-policy-optimization`](research-briefs/potential-guided-policy-optimization.md) | Anchor-state potential differences for multi-turn agent credit |
| [`conflict-driven-model-merging`](research-briefs/conflict-driven-model-merging.md) | Resolving parameter conflicts via preference optimization on merge defects |
| [`evaluability-aware-assistance`](research-briefs/evaluability-aware-assistance.md) | Balancing proposal acceptance against latent preference learning |
| [`apex-procedural-experience-distillation`](research-briefs/apex-procedural-experience-distillation.md) | Hierarchical experience and test-time RL for deep research agents |
| [`post-training-ternarization-qwen3`](research-briefs/post-training-ternarization-qwen3.md) | Capability retention and kernel overheads of 1.58-bit model conversion |
| [`growpage-dynamic-kv-budgeting`](research-briefs/growpage-dynamic-kv-budgeting.md) | On-demand dynamic page budgeting for long-output reasoning serving |
| [`paper-code-discrepancy-detection`](research-briefs/paper-code-discrepancy-detection.md) | Dual-detection multi-agent verification for paper-code discrepancies |
| [`hybrid-micro-level-agent-personalization`](research-briefs/hybrid-micro-level-agent-personalization.md) | Prompt conditioning on Bloom cognitive complexity and learner profiles |
| [`civilization-framework-sovereign-agent-communication`](research-briefs/civilization-framework-sovereign-agent-communication.md) | Sovereign-anchored asynchronous store-and-forward agent collaboration |
| [`reflect-sql-multi-stage-reflection`](research-briefs/reflect-sql-multi-stage-reflection.md) | Multi-stage decoupled reflection loops for enterprise text-to-SQL |


---

## How This Was Made

Every artifact traces back to a specific paper and was produced through a systematic pipeline:

1. Papers ingested and indexed via [Praxis](https://github.com/Marontis/praxis)
2. Each paper analyzed through the [skill-design-methodology](skills/skill-design-methodology/SKILL.md) checklist
3. Papers with transferable subtask-level procedures became **skills**
4. Decision criteria and quantitative pitfalls became **rules**
5. Design spaces with multiple valid configurations became **spec templates**
6. Papers without actionable procedures became **research briefs**

The selection criteria: a paper produces a skill only if it describes a procedure that (a) operates at the subtask level, (b) could appear in 3+ different project types, and (c) is written as natural language, not executable code.

---

## Contributing

Found a paper that should be here? Open an issue with the arXiv link and a brief note on what transferable procedure you see in it.

---

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
