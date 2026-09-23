# Agentic Engineering

Research-backed rules, skills, and spec templates for building LLM agent systems -- distilled from 305+ arXiv papers and counting.

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
| [`agent-sandbox-safety`](rules/agent-sandbox-safety.md) | Sandbox design, command classification, network policy, capability gateway, defense composition, checkpoint integrity, deployment context, adversarial testing, tool output safety, GitOps span editing, harness tampering audit, blind CoT monitoring, hook security, multi-turn refusal variance, dependency-scoped plan lineage, dialogue authentication decoupling, semantic patch validation, input tree perturbation, constructive agent host obligations, guard-agent topologies, deterministic safety constraint gates, guardrail repetition instability, dynamic resource acquisition bounds, pre-execution action auditing, agent-tool boundary contracts, universal tool anomaly filtering, trajectory-level multi-turn safety |
| [`skill-system-design`](rules/skill-system-design.md) | Skill authoring, selection, library management, skill evolution, training data quality, evidence triage, library integrity, hallucination detection, prefix-preserving context assembly, protocol-aware context trimming, persistent agent architecture, procedural families, operational know-how distillation, speculative macro commit, code embedding functional retrieval gap, standardized semantic envelopes |
| [`recursive-improvement`](rules/recursive-improvement.md) | Self-modification architecture, change classification, evaluation, instruction refinement, targeted reflection, verification, multi-day autonomous loops, joint harness-weight optimization, reference trajectory evolution, error-structured prompt optimization (ESPO), counterexample-guided repair, rubric artifact bias, neural invariant diagnosis, belief-calibrated scaffold optimization, swarm commons governance, debate consensus calibration, surrogate-guided bilevel rubric evolution, autonomous environment exploration and frozen causal memory |
| [`adk-workflow-architecture`](rules/adk-workflow-architecture.md) | Graph DAG orchestration, deterministic runtime gates, zero-token policy routing, default fallback edges, lifecycle callback interceptors, Memory Bank vs RAG separation, long-running tool receipts, universal resumption |
| [`adk-security-and-evaluation`](rules/adk-security-and-evaluation.md) | Model Armor prompt injection guards, Sensitive Data Protection (SDP) PII de-identification, A2A mutual agent authentication & Agent Card verification, AP2/UCP cryptographic commerce tokens, CI/CD golden dataset trajectory validation, multi-criteria LLM-as-a-Judge rubrics |
| [`agent-evaluation-quality`](rules/agent-evaluation-quality.md) | Output evaluation, benchmarking, quality gates, pass/fail rubrics, trajectory verification |
| [`agent-human-interaction`](rules/agent-human-interaction.md) | Work presentation, feedback solicitation, cognitive load management, structured reviews |
| [`multi-agent-coordination`](rules/multi-agent-coordination.md) | Multi-agent topology, role delegation, communication protocols, coordination failure recovery, intent-regularized bus communication, intra-family model candidate selection |

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
| [`nlip-agent-message-envelope`](skills/nlip-agent-message-envelope/SKILL.md) | NLIP Agent Protocol Standard (arXiv:2609.04135) |
| [`auth-revocation-quiescence`](skills/auth-revocation-quiescence/SKILL.md) | Auth Revocation for Long-Running Agents (arXiv:2609.21284) |
| [`auto-formalization-safety-guarantee`](skills/auto-formalization-safety-guarantee/SKILL.md) | MAGS Auto-Formalization Safety (arXiv:2609.19391) |
| [`residual-auth-state-preservation`](skills/residual-auth-state-preservation/SKILL.md) | ResidualAuth (arXiv:2609.08062) |
| [`prime-power-federation-governance`](skills/prime-power-federation-governance/SKILL.md) | PRIMUS (arXiv:2609.07910) |
| [`taxonomy-driven-red-teaming`](skills/taxonomy-driven-red-teaming/SKILL.md) | Black-Box Red Teaming of Agentic AI (arXiv:2609.09647) |
| [`multi-agent-federation-governance`](skills/multi-agent-federation-governance/SKILL.md) | PRIMUS Federation Identity (arXiv:2609.07910) |
| [`description-only-injection-detection`](skills/description-only-injection-detection/SKILL.md) | No-Box Vulnerability Analysis (arXiv:2609.10854) |
| [`high-fanout-sandbox-memory-compression`](skills/high-fanout-sandbox-memory-compression/SKILL.md) | High-Fanout Sandbox Memory (arXiv:2609.11294) |
| [`adk-model-armor-interceptor`](skills/adk-model-armor-interceptor/SKILL.md) | Google Cloud Model Armor & SDP Interceptors |
| [`runtime-resource-authorization-bounds`](skills/runtime-resource-authorization-bounds/SKILL.md) | AcquireBound (arXiv:2609.14744) |
| [`pre-execution-action-auditing`](skills/pre-execution-action-auditing/SKILL.md) | ActGuard (arXiv:2609.14987) |
| [`agentic-prompt-injection-search`](skills/agentic-prompt-injection-search/SKILL.md) | Test-Time Injection Search (arXiv:2609.04495) |
| [`security-context-composition`](skills/security-context-composition/SKILL.md) | CONTINUITY Security-Context Contracts (arXiv:2609.05269) |
| [`cve-history-executable-detection`](skills/cve-history-executable-detection/SKILL.md) | The History Is the Detector (arXiv:2609.05335) |
| [`macos-reverse-engineering`](skills/macos-reverse-engineering/SKILL.md) | Jonathan Levin (*OS Internals*) & Patrick Wardle (*TAOMM*) |
| [`universal-tool-defense`](skills/universal-tool-defense/SKILL.md) | Universal Tool Defenses (arXiv:2609.16098) |
| [`mcp-tool-hijacking-defense`](skills/mcp-tool-hijacking-defense/SKILL.md) | A2M MCP Hijacking (arXiv:2609.26761) |
| [`selection-invariant-agent-communication`](skills/selection-invariant-agent-communication/SKILL.md) | SICC Privacy-Aware MAS Comms (arXiv:2609.26076) |
| [`tainted-message-clean-room-recovery`](skills/tainted-message-clean-room-recovery/SKILL.md) | ESC-CR Tainted Message Recovery (arXiv:2609.26072) |

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
| [`debate-consensus-memory-calibration`](skills/debate-consensus-memory-calibration/SKILL.md) | R^2-MAD (arXiv:2609.03619) |
| [`reward-hacking-immunization`](skills/reward-hacking-immunization/SKILL.md) | HackProbe (arXiv:2609.04665) |
| [`intervention-guided-mas-prompt-optimization`](skills/intervention-guided-mas-prompt-optimization/SKILL.md) | AgentGrad (arXiv:2609.08572) |
| [`temporal-workflow-graph-compilation`](skills/temporal-workflow-graph-compilation/SKILL.md) | ReActNet (arXiv:2609.05774) |
| [`offline-trajectory-tool-use-learning`](skills/offline-trajectory-tool-use-learning/SKILL.md) | AgentBrew (arXiv:2609.05837) |
| [`debate-layer-disagreement-analysis`](skills/debate-layer-disagreement-analysis/SKILL.md) | Layered Disagreement Analysis (arXiv:2609.08016) |
| [`self-verification-elicitation`](skills/self-verification-elicitation/SKILL.md) | Self-Verification via RL (arXiv:2609.08025) |
| [`static-dynamic-verification-gap-measurement`](skills/static-dynamic-verification-gap-measurement/SKILL.md) | Beyond Static Guarantees (arXiv:2609.10762) |
| [`bayesian-backward-disagreement-anchor`](skills/bayesian-backward-disagreement-anchor/SKILL.md) | Bayesian Backward Reasoning (arXiv:2609.11709) |
| [`adk-eval-golden-dataset-ci`](skills/adk-eval-golden-dataset-ci/SKILL.md) | Google ADK Golden Dataset & Trajectory CI/CD |
| [`dense-rubric-skill-evolution`](skills/dense-rubric-skill-evolution/SKILL.md) | SkillLift (arXiv:2609.15396) |
| [`agentic-review-deploy-loop`](skills/agentic-review-deploy-loop/SKILL.md) | AI-Native SDLC Playbook (Review, deploy, and maintain stages) |
| [`autonomous-research-to-launch-harness`](skills/autonomous-research-to-launch-harness/SKILL.md) | AutoLR Research-to-Launch Harness (arXiv:2609.04871) |
| [`autonomous-environment-exploration`](skills/autonomous-environment-exploration/SKILL.md) | RSIAgent (arXiv:2609.15364) |
| [`fast-tree-search-self-improvement`](skills/fast-tree-search-self-improvement/SKILL.md) | SIFT (arXiv:2609.19526) |
| [`recursive-self-improvement-loop`](skills/recursive-self-improvement-loop/SKILL.md) | AIDE² (arXiv:2609.26457) |
| [`corpus-scale-prompt-distillation`](skills/corpus-scale-prompt-distillation/SKILL.md) | CASD (arXiv:2609.26261) |
| [`world-model-trust-gating`](skills/world-model-trust-gating/SKILL.md) | Dual-Frontier (arXiv:2609.26293) |
| [`serving-stack-eval-checklist`](skills/serving-stack-eval-checklist/SKILL.md) | Serving Stack Confounds (arXiv:2609.26693) |

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
| [`attribution-guided-skill-graph-update`](skills/attribution-guided-skill-graph-update/SKILL.md) | SkillAA (arXiv:2609.20455) |
| [`controlled-skill-lifecycle-management`](skills/controlled-skill-lifecycle-management/SKILL.md) | FINSKILLOPS (arXiv:2609.19680) |
| [`semantic-aware-multi-agent-delegation`](skills/semantic-aware-multi-agent-delegation/SKILL.md) | SAIGE (arXiv:2609.19759) |
| [`prefix-preserving-context-assembly`](skills/prefix-preserving-context-assembly/SKILL.md) | ContextPipe (arXiv:2609.00749) |
| [`protocol-preserving-context-trimming`](skills/protocol-preserving-context-trimming/SKILL.md) | Protocol-Preserving Context Trimming (arXiv:2609.16461) |
| [`persistent-agent-migration`](skills/persistent-agent-migration/SKILL.md) | Enoch Persistent Agents (arXiv:2609.00546) |
| [`requirements-driven-code-generation`](skills/requirements-driven-code-generation/SKILL.md) | WiseSpec (arXiv:2609.00568) |
| [`grill-spec`](skills/grill-spec/SKILL.md) | Multiple-choice interview → spec, ADRs, milestone roadmap, AGENTS.md for maintained projects; example by [alexziskind1](https://gist.github.com/alexziskind1/fe55f03892f3fe1d6d8cf6065c631bb8) + WiseSpec, ProSE |
| [`procedural-family-skill-consolidation`](skills/procedural-family-skill-consolidation/SKILL.md) | SkillGLoW (arXiv:2609.02217) |
| [`speculative-macro-commit`](skills/speculative-macro-commit/SKILL.md) | Speculative Macro Commit (arXiv:2609.03236) |
| [`procedural-graph-evolution`](skills/procedural-graph-evolution/SKILL.md) | Procedural Graphs (arXiv:2609.09153) |
| [`graph-of-skills-scaling`](skills/graph-of-skills-scaling/SKILL.md) | SE-GoS (arXiv:2609.08228) |
| [`stable-skill-evolution`](skills/stable-skill-evolution/SKILL.md) | SkillAdam (arXiv:2609.08944) |
| [`ledger-orchestrated-coding-loop`](skills/ledger-orchestrated-coding-loop/SKILL.md) | Zero-Shot Self-Orchestration (arXiv:2608.26480) |
| [`adk2-agent-orchestration-patterns`](skills/adk2-agent-orchestration-patterns/SKILL.md) | Google Cloud Tech / ADK 2 Orchestration |
| [`adk-async-long-running-tool-resumption`](skills/adk-async-long-running-tool-resumption/SKILL.md) | Google ADK VibeStudio (Async Tool Resumption & Call ID Matching) |
| [`adk-lifecycle-callback-interceptors`](skills/adk-lifecycle-callback-interceptors/SKILL.md) | Google ADK VibeStudio (Lifecycle Callbacks & Interceptors) |
| [`adk-a2a-agent-federation`](skills/adk-a2a-agent-federation/SKILL.md) | Google ADK & Agent Runtime (A2A Protocol & Agent Cards) |
| [`adk-a2ui-dynamic-widgets`](skills/adk-a2ui-dynamic-widgets/SKILL.md) | Google ADK & A2UI (Declarative Widgets & Action Dispatch) |
| [`adk-eventarc-reactive-trigger`](skills/adk-eventarc-reactive-trigger/SKILL.md) | Google Cloud Eventarc & ADK (Event-Driven Reactive Pipelines) |
| [`adk-mcp-multimodal-tool-interception`](skills/adk-mcp-multimodal-tool-interception/SKILL.md) | Google ADK & MCP (Multimodal Tool Interceptors & Callbacks) |
| [`intent-driven-sdlc-planning`](skills/intent-driven-sdlc-planning/SKILL.md) | AI-Native SDLC Playbook (Intent → Spec → Plan upstream pipeline) |
| [`mcp-server-design`](skills/mcp-server-design/SKILL.md) | MCP Server Best Practices & Progressive Discovery |

#### Retrieval & Evidence

| Skill | Source Paper |
|:------|:------------|
| [`rag-evidence-triage`](skills/rag-evidence-triage/SKILL.md) | Knowing Before Answering (arXiv:2608.27661) |
| [`hallucination-mean-shift-probe`](skills/hallucination-mean-shift-probe/SKILL.md) | Hallucination Mean Shift (arXiv:2608.28930) |
| [`rag-hallucination-repair`](skills/rag-hallucination-repair/SKILL.md) | RAG Hallucination Repair (arXiv:2608.29307) |
| [`cost-effective-repo-exploration`](skills/cost-effective-repo-exploration/SKILL.md) | Cost-Effective Repo Exploration (arXiv:2608.29675) |
| [`necessary-tool-evidence-path`](skills/necessary-tool-evidence-path/SKILL.md) | NTEP (arXiv:2609.03493) |
| [`cost-aware-hierarchical-analysis`](skills/cost-aware-hierarchical-analysis/SKILL.md) | Cost-Aware Hierarchical Analysis (arXiv:2609.04820) |

### Spec Templates (Project Kickoff)

Structured decision frameworks to fill in when starting a new project. Each template surfaces research-backed decision points with evidence notes.

| Template | Domain |
|:---------|:-------|
| [`agent-sandbox.spec`](specs/agent-sandbox.spec.md) | Designing agent execution sandboxes |
| [`skill-library.spec`](specs/skill-library.spec.md) | Designing skill memory systems for LLM agents |
| [`self-improving-agent.spec`](specs/self-improving-agent.spec.md) | Designing self-modifying agent systems |
| [`adk-agentic-workflow.spec`](specs/adk-agentic-workflow.spec.md) | Designing multi-agent graph workflows with Google ADK 2 |
| [`adk-multi-agent-a2a.spec`](specs/adk-multi-agent-a2a.spec.md) | Designing distributed multi-agent systems with A2A Protocol |
| [`adk-enterprise-deployment-gke.spec`](specs/adk-enterprise-deployment-gke.spec.md) | Production containerized ADK deployment on GKE & Eventarc |
| [`adk-eval-quality-gate.spec`](specs/adk-eval-quality-gate.spec.md) | Designing golden datasets, trajectory assertions & CI/CD gates |
| [`adk-a2ui-declarative-interface.spec`](specs/adk-a2ui-declarative-interface.spec.md) | Designing rich agentic interfaces with A2UI dynamic widgets |

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
| [`patchbench-vulnerability-patching-evaluation`](research-briefs/patchbench-vulnerability-patching-evaluation.md) | Diagnostic benchmark revealing 1.83× inflation in PoC-only vulnerability repair evals |
| [`swarm-emergent-cheating-and-whistleblowing`](research-briefs/swarm-emergent-cheating-and-whistleblowing.md) | Ostrom commons governance and spontaneous whistleblowing in 100-agent research swarms |
| [`conversational-false-authentication`](research-briefs/conversational-false-authentication.md) | Identifying model-issued pseudo-credentials (MIPC) and conversational false authentication |
| [`alcatraz-anchored-tree-rule-defense`](research-briefs/alcatraz-anchored-tree-rule-defense.md) | Rule-tree input perturbation achieving superior security across 33 open-weight models |
| [`environment-evolution-terminal-agents`](research-briefs/environment-evolution-terminal-agents.md) | Off-policy difficulty scaling along three axes yielding +14.4 to +18.0 pts on Terminal-Bench 2.1 |
| [`dalek-constructive-agent-machine`](research-briefs/dalek-constructive-agent-machine.md) | Von Neumann constructive machine architecture and host contracts for self-evolving agents |
| [`value-preserving-agentic-architectures`](research-briefs/value-preserving-agentic-architectures.md) | Architectural topologies and dedicated guard-agent patterns for value-preserving MAS |
| [`safety-constrained-evaluation-protocol`](research-briefs/safety-constrained-evaluation-protocol.md) | FLY-EVAL++ protocol revealing 28-point safety divergence under identical prediction accuracy |
| [`multilingual-persuasive-jailbreak-evaluation`](research-briefs/multilingual-persuasive-jailbreak-evaluation.md) | IndicSafeEval benchmark examining multilingual transfer and persuasive framing vulnerabilities |
| [`creative-ai-model-governance`](research-briefs/creative-ai-model-governance.md) | Closing the governance gap between data storage, circulation, and federated learning |
| [`execretrieval-code-embedding-functional-gap`](research-briefs/execretrieval-code-embedding-functional-gap.md) | Diagnostic benchmark revealing dense code retrievers prefer near-clone buggy code 91.5–99.4% of the time |
| [`collective-preference-inference-evaluation`](research-briefs/collective-preference-inference-evaluation.md) | Collective-centric evaluation of preference inference preserving consensus and minority voice |
| [`when-llm-decompilers-recompile-more-and-prese`](research-briefs/when-llm-decompilers-recompile-more-and-prese.md) | Behavioral divergence in LLM decompilers despite high recompilability |
| [`refuse-without-refusal-a-structural-analysis`](research-briefs/refuse-without-refusal-a-structural-analysis.md) | Rationale-only safety tuning reduces false refusals without harming safety |
| [`repeat-after-me-black-box-adaptive-visual-pro`](research-briefs/repeat-after-me-black-box-adaptive-visual-pro.md) | Black-box visual prompt injection achieving 80%+ ASR on open-weight VLMs |
| [`dcfa-dual-view-causal-inspired-attribution-fo`](research-briefs/dcfa-dual-view-causal-inspired-attribution-fo.md) | Dual-view causal dependency graphs for multi-agent failure attribution |
| [`how-a-chatbots-response-style-shapes-a-classr`](research-briefs/how-a-chatbots-response-style-shapes-a-classr.md) | Multi-agent classroom simulation of chatbot response style effects |
| [`mabpd-multi-agent-bias-probing-detection-via`](research-briefs/mabpd-multi-agent-bias-probing-detection-via.md) | Training-free multi-agent bias detection via structured argument debate |
| [`building-a-research-software-catalog-with-a-c`](research-briefs/building-a-research-software-catalog-with-a-c.md) | Silent failures in coding-agent-built research software catalogs |
| [`simulated-deliberation-representation-challen`](research-briefs/simulated-deliberation-representation-challen.md) | Challenges in AI-simulated democratic deliberation representation |
| [`style-over-substance-safety-judge-wrappers`](research-briefs/style-over-substance-safety-judge-wrappers.md) | Content-invariant wrappers flipping LLM safety-judge verdicts |
| [`multimodal-resource-exhaustion-vlm-attacks`](research-briefs/multimodal-resource-exhaustion-vlm-attacks.md) | Cross-modal resource-exhaustion attacks on vision-language models |
| [`pipeline-dependent-cybersecurity-benchmarks`](research-briefs/pipeline-dependent-cybersecurity-benchmarks.md) | Pipeline choices swinging cybersecurity benchmark scores by 80+ points |
| [`autofyn-non-parametric-expert-iteration`](research-briefs/autofyn-non-parametric-expert-iteration.md) | Non-parametric expert iteration updating persistent state, not weights |
| [`gvs5h-zero-shot-self-orchestration`](research-briefs/gvs5h-zero-shot-self-orchestration.md) | Zero-shot ledger scaffold matching frontier models via test execution |
| [`ai-paper-review-arms-race`](research-briefs/ai-paper-review-arms-race.md) | Adversarial co-evolution dynamics in AI scholarly publishing |
| [`threat-model-coverage-gap-safety-eval`](research-briefs/threat-model-coverage-gap-safety-eval.md) | Threat-model coverage gap in automated vs human safety evaluation |
| [`cs-guard-guardrail-benchmark`](research-briefs/cs-guard-guardrail-benchmark.md) | Guardrail weakness for code generation security |
| [`watermarks-without-verification`](research-briefs/watermarks-without-verification.md) | AI text watermarking gap under EU AI Act |
| [`active-adaptation-preventative-steering`](research-briefs/active-adaptation-preventative-steering.md) | Temporal dynamics of active safety adaptation |
| [`residual-auth-revocable-delegation`](research-briefs/residual-auth-revocable-delegation.md) | Authorization state preservation under delegation revocation |
| [`proof-carrying-cognition`](research-briefs/proof-carrying-cognition.md) | Reality-settled verification gap framework |
| [`arbitrary-cipher-attacks`](research-briefs/arbitrary-cipher-attacks.md) | Cipher-encoded jailbreaks without fine-tuning |
| [`multimodal-prompt-injection-eval`](research-briefs/multimodal-prompt-injection-eval.md) | Cross-modal prompt injection on agentic frameworks |
| [`self-evolving-consistency-gap`](research-briefs/self-evolving-consistency-gap.md) | Goal drift in long-horizon self-evolving agents |
| [`robust-sgpo-harness-evolution`](research-briefs/robust-sgpo-harness-evolution.md) | Search-space control for agent harness evolution |
| [`verifier-survey-no-free-checker`](research-briefs/verifier-survey-no-free-checker.md) | Coverage-cost-soundness trade-offs in policy verifiers |
| [`agent-audit-lifecycle-trust`](research-briefs/agent-audit-lifecycle-trust.md) | Full-lifecycle trust evaluation framework |
| [`inference-time-governance-taxonomy`](research-briefs/inference-time-governance-taxonomy.md) | Feasibility taxonomy for inference-time AI governance |
| [`sae-scientist-bench`](research-briefs/sae-scientist-bench.md) | Autonomous SAE interpretability research benchmark |
| [`trace-causal-exploration`](research-briefs/trace-causal-exploration.md) | Synthesized rewards for causal reasoning agents |
| [`driftnet-prompt-injection-detection`](research-briefs/driftnet-prompt-injection-detection.md) | Dual-head trajectory transformer for injection detection |
| [`terminal-agent-rl-long-horizon`](research-briefs/terminal-agent-rl-long-horizon.md) | RL for terminal agents on long-horizon tasks |
| [`scaffolding-mas-clinical-training`](research-briefs/scaffolding-mas-clinical-training.md) | Multi-agent scaffolding for clinical interview training |
| [`debate-to-skill-process-supervision`](research-briefs/debate-to-skill-process-supervision.md) | Capability-bound process supervision via debate |
| [`semverbench-version-constraint`](research-briefs/semverbench-version-constraint.md) | LLM semantic versioning comprehension benchmark |
| [`orch-collective-intelligence`](research-briefs/orch-collective-intelligence.md) | Organizational principles for embodied AI collective intelligence |
| [`opendiscoverytrace-ai-scientist`](research-briefs/opendiscoverytrace-ai-scientist.md) | Process traces for evaluating AI scientist workflows |
| [`data-efficient-language-modeling`](research-briefs/data-efficient-language-modeling.md) | Survey of data efficiency techniques for LM training |
| [`adk2-orchestration-three-pillars`](research-briefs/adk2-orchestration-three-pillars.md) | Architectural pillars and decision matrix for ADK 2 graph, collaborative, and dynamic workflows |
| [`overflip-guardrail-repetition-instability`](research-briefs/overflip-guardrail-repetition-instability.md) | Repetition-induced label flips in guardrail models |
| [`agent-tool-boundary-anomalies`](research-briefs/agent-tool-boundary-anomalies.md) | Structural failures and semantic divergence when tool calls succeed |
| [`a-structured-debate-mixture-of-agents-framewo`](research-briefs/a-structured-debate-mixture-of-agents-framewo.md) | Structured debate MoA framework for clinical diagnostic support |
| [`a-verifier-guided-explainable-reasoning-frame`](research-briefs/a-verifier-guided-explainable-reasoning-frame.md) | Verifier-guided explainable reasoning with gold-anchored QLoRA and RLVR |
| [`aria---an-agentic-framework-for-autonomous-te`](research-briefs/aria---an-agentic-framework-for-autonomous-te.md) | Autonomous agentic testing framework for infotainment systems |
| [`cabal-multi-agent-simulacra-for-tracing-the-e`](research-briefs/cabal-multi-agent-simulacra-for-tracing-the-e.md) | Multi-agent simulacra modeling collusive bidding cartels in peer review |
| [`from-language-models-to-world-acting-systems`](research-briefs/from-language-models-to-world-acting-systems.md) | Progress and boundary limits of world-acting agentic AI |
| [`rise-recursive-improvement-via-self-extrapola`](research-briefs/rise-recursive-improvement-via-self-extrapola.md) | Recursive improvement via self-extrapolating policy distillation |
| [`blindspot-long-horizon-agent-safety`](research-briefs/blindspot-long-horizon-agent-safety.md) | Trajectory-level safety benchmark evaluating delayed emergence of failures across 2,500+ multi-turn runs |
| [`sciencebuddy-recursive-harness-evolution`](research-briefs/sciencebuddy-recursive-harness-evolution.md) | Recursive-in-recursive self-improvement coupling inner harness evolution with outer model RL |
| [`algoevo-agentic-algorithm-discovery`](research-briefs/algoevo-agentic-algorithm-discovery.md) | Self-evolving agentic search with design skill hubs and hierarchical experience trees |
| [`busma-multi-agent-bus-substrate`](research-briefs/busma-multi-agent-bus-substrate.md) | Shared bus communication substrate with 4 explicit communicative intents and chair convergence |
| [`stellar-colosseum-agent-harness`](research-briefs/stellar-colosseum-agent-harness.md) | Many-agent harness for long-horizon mathematical proofs integrated into Antigravity Teamwork |
| [`evoontology-self-evolving-ontology`](research-briefs/evoontology-self-evolving-ontology.md) | MCP-encapsulated ontology layer with attribution-guided typed edits for data agents |
| [`world-model-science-metastable-dynamics`](research-briefs/world-model-science-metastable-dynamics.md) | Dynamical diagnostics, error avalanches, and metastable belief basins in long-horizon agents |
| [`mas-model-pool-selection`](research-briefs/mas-model-pool-selection.md) | Empirical model pool selection showing intra-family candidate pools outperform heterogeneous mixes |
| [`thinkflow-latent-conversational-memory`](research-briefs/thinkflow-latent-conversational-memory.md) | Self-evolving probabilistic continuous latent memory overcoming explicit text bottlenecks |
| [`pentestchain-cost-aware-mcp-pentesting`](research-briefs/pentestchain-cost-aware-mcp-pentesting.md) | Cost-aware, MCP-orchestrated penetration testing cascade with local SLM and MCP threat model |
| [`mist-mid-training-cybersecurity-llms`](research-briefs/mist-mid-training-cybersecurity-llms.md) | Domain adaptation via synthetic mid-training flows preserving general reasoning |
| [`trusting-trust-revisited-poisoned-benchmarks`](research-briefs/trusting-trust-revisited-poisoned-benchmarks.md) | Thompson's "Trusting Trust" applied to self-modifying coding agents via poisoned benchmarks |
| [`red-teaming-auto-mode-blocking-monitors`](research-briefs/red-teaming-auto-mode-blocking-monitors.md) | Red-teaming production pre-execution action blocking monitors (Auto Mode in Claude Code, Codex Guardian) |
| [`inference-engine-fingerprinting-and-escape`](research-briefs/inference-engine-fingerprinting-and-escape.md) | Practical inference engine fingerprinting and to-the-bare-metal sandbox escapes via output tokens |
| [`contagion-multi-agent-trading-systems`](research-briefs/contagion-multi-agent-trading-systems.md) | Adversarial signal propagation and topology damping across multi-agent financial stacks |
| [`he-guardrail-encrypted-jailbreak-defense`](research-briefs/he-guardrail-encrypted-jailbreak-defense.md) | HE-based guardrail feasibility for encrypted LLM inference |
| [`sol-pi-recursive-harness-scaling`](research-briefs/sol-pi-recursive-harness-scaling.md) | Recursive self-improvement at the harness layer with 44-49% token reduction |
| [`harness-value-planning-vs-verification`](research-briefs/harness-value-planning-vs-verification.md) | Quantifying planning vs verification value in agent harnesses |
| [`vehicle-voice-command-authorization`](research-briefs/vehicle-voice-command-authorization.md) | Safety-critical LLM authorization benchmark with 2-3 False Executes per 161 scenarios |
| [`foundation-model-operating-system`](research-briefs/foundation-model-operating-system.md) | Vision for FM virtualization analogous to VM abstraction |
| [`closed-world-tool-hallucination`](research-briefs/closed-world-tool-hallucination.md) | 5-class tool hallucination taxonomy with MCP-specific attack surfaces |
| [`micro-collaborative-rag-poisoning`](research-briefs/micro-collaborative-rag-poisoning.md) | Distributed false claims across multiple retrieved documents |
| [`llm-group-consensus-overstatement`](research-briefs/llm-group-consensus-overstatement.md) | Agent groups 34-44pp more consensual than humans, mostly on wrong answers |
| [`empirical-harness-design-study`](research-briefs/empirical-harness-design-study.md) | 176-setting component-level harness comparison across 4 models |
| [`ddpo-jailbreak-defense`](research-briefs/ddpo-jailbreak-defense.md) | Dynamic deep prompt optimization for input-adaptive jailbreak defense |
| [`metrics-failure-vuln-repair`](research-briefs/metrics-failure-vuln-repair.md) | Standard metrics fail to capture repair quality in vulnerability repair |
| [`coding-agents-kernel-exploits`](research-briefs/coding-agents-kernel-exploits.md) | Evaluating coding agent capability on kernel exploit generation |
| [`emergent-collusion-long-horizon`](research-briefs/emergent-collusion-long-horizon.md) | 94% collusion rate in long-horizon multi-agent peer verification |
| [`silent-sabotage-state-triggered-backdoors`](research-briefs/silent-sabotage-state-triggered-backdoors.md) | Internal state triggered backdoor attacks on LLM-powered robotic systems |
| [`vacs-value-aligned-shielding`](research-briefs/vacs-value-aligned-shielding.md) | Four-layer value-aligned compositional shielding for multi-agent reasoning |
| [`zerogate-trust-fast-paths`](research-briefs/zerogate-trust-fast-paths.md) | Trust-preserving fast paths with ActionPass revalidation contracts |
| [`akasicmem-governed-enterprise-memory`](research-briefs/akasicmem-governed-enterprise-memory.md) | Authorization continuity via transitive lineage in enterprise agent memory |
| [`harness-zero-distillation`](research-briefs/harness-zero-distillation.md) | Harness distillation via agent-as-harness into model weights |
| [`growing-harness-specialist-agents`](research-briefs/growing-harness-specialist-agents.md) | Failure-guided harness growth reducing LLM calls by 76-92% |
| [`indirect-tipping-social-attack`](research-briefs/indirect-tipping-social-attack.md) | Stepping-stone equilibria as social attack surface in agent populations |
| [`contrastive-epistemic-decoding`](research-briefs/contrastive-epistemic-decoding.md) | Zero-shot sycophancy mitigation via dual forward-pass conformity isolation |

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
