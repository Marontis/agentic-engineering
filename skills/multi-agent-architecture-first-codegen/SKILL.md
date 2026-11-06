---
name: multi-agent-architecture-first-codegen
description: >
  Governed four-phase multi-agent software architecture lifecycle
  (Requirement Definition, Architecture Design, Validation & Assurance,
  Delivery & Evolution) that inserts an explicit, traceable architectural
  layer between requirements and code generation. Combines schema-bound
  generator agents, standards-grounded evaluator/challenger agents,
  stage-filtered RAG knowledge retrieval, deterministic traceability rules,
  and lock-and-advance human approval gates. Derived from TimeArch
  (arXiv:2611.06921).
source: https://arxiv.org/abs/2611.06921
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Multi-Agent Architecture-First Code Generation (TimeArch)

> **Source**: [TimeArch: A Multi-Agent Approach for Software Architecture Design](https://arxiv.org/abs/2611.06921) (`src:2611-06921v1`, Waseem et al., Tampere University, University of Jyväskylä & Aimbition Oy, ECSA 2026 Industry Track)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when building or evolving non-trivial software systems where moving directly from informal prompts to code ("vibe coding") causes architectural erosion, undocumented quality-attribute tradeoffs, overengineering, or broken traceability between stakeholder requirements, Architecture Decision Records (`ADRs`), API/data contracts, and implementation.

## When to Use

- Greenfield system design or brownfield modernization where multiple quality attributes, integrations, and stakeholder constraints must be balanced before writing code
- Multi-agent software engineering pipelines that need an explicit, auditable architecture layer (`SRS` $\to$ `SAD` $\to$ `AAR` $\to$ `FAP`) prior to code synthesis
- Enforcing `Generator -> Evaluator/Challenger -> Human Architect` lock-and-advance governance gates over system decomposition and `ADRs`
- Detecting architectural drift and technical debt during iterative feature delivery

## Core Insight

Prompt-to-code workflows embed architectural decisions implicitly inside generated source files without evaluating design alternatives, quality-attribute tradeoffs, or component data ownership. Over multi-stage development, this missing architectural layer leads to **architectural erosion**—where the implemented system diverges from stakeholder constraints and non-functional requirements.

**TimeArch** operationalizes established software architecture standards—**SEI Attribute-Driven Design (`ADD 3.0`)**, **ISO/IEC 25010** quality models, **ISO/IEC/IEEE 29148** and **INCOSE** requirements criteria, **ISO/IEC/IEEE 42010** architecture description, **ATAM** (Architecture Tradeoff Analysis Method), and the **AWS Well-Architected Framework**—through a **four-phase governed multi-agent lifecycle** (`28` task-specialized prompts across generator, critic, checklist-verification, tradeoff/overengineering challenger, and refinement agents) backed by stage-filtered RAG knowledge grounding, deterministic cross-artifact traceability checks, bounded schema retries (at most `1` reinforced schema retry on parse failure), and a **lock-and-advance human approval protocol**.

---

## Procedure: The Four-Phase Governed Architecture Lifecycle

### Phase 1: Requirement Definition & Architectural Driver Extraction

1. **Ingest Heterogeneous Inputs into Schema-Bound Requirement Elements**: Extract functional requirements, non-functional requirements (`NFRs`), system constraints, assumptions, external integrations, actors, business rules, and stakeholder concerns from raw inputs (documents, `SRS`/`BRD` files, structured forms, or segmented transcripts).
2. **Normalize NFRs to ISO/IEC 25010 Quality Attributes**: Map every non-functional requirement and stakeholder concern to explicit **ISO/IEC 25010** quality attributes (e.g., performance efficiency, security, reliability, maintainability, portability) and derive the prioritized **Architectural Drivers** that will shape system structure.
3. **Run the Requirement Critic Agent (`ISO/IEEE 29148` + `INCOSE` + `ATAM` Soundness)**: Before any design generation begins, invoke a dedicated **Requirement Critic Agent** to audit extracted requirements and architectural drivers against **ISO/IEC/IEEE 29148**, **INCOSE** writing rules, and **ATAM**-style soundness criteria. The critic must output structured verdicts:
   - `severity` level
   - `violated_rule_code` and explicit rationale
   - Concrete `suggested_rewrite` for ambiguous, unverifiable, or conflicting requirements
4. **Gate 1 (Requirement Lock)**: Verify deterministically that every architectural driver links to at least one requirement, resolve or explicitly accept critical critic findings, and lock the **Software Requirements Specification (`SRS`)** baseline via human architect approval.

### Phase 2: Attribute-Driven Architecture Design (`ADD 3.0`) & Overengineering Critique

1. **Ground Design Generation in Stage-Filtered RAG Chunks**: Assemble the execution context from the locked Phase 1 `SRS`, validated architectural drivers, and top-$k$ curated architectural guidance chunks filtered by framework, category, and lifecycle stage (`ADD 3.0`, `ISO/IEC/IEEE 42010`, `4+1 View Model`, `Domain-Driven Design`, `AWS Well-Architected Framework`). Expose retrieved guidance chunks alongside generated artifacts so reviewers can audit provenance.
2. **Synthesize Candidate Architecture Views and Contracts**: Using task-decomposed design prompts (never a single monolithic prompt) and schema-bound structured outputs, generate:
   - **Architectural Style & System Decomposition**: Candidate styles with explicit comparative justification, logical and component views, and **process and deployment views** (give explicit view-specific prompting to process and deployment views so they match the detail of logical/component views).
   - **Data Ownership & API Contracts**: Explicit per-component data ownership maps (preventing shared-table coupling), interface schemas, and cross-cutting concern strategies (authentication, observability, error handling, row-level security).
3. **Invoke the Tradeoff & Overengineering Evaluator (Challenger Agent)**: Run a dedicated evaluator agent that critiques the candidate architecture against quality attributes and constraints, explicitly **flags overengineering risks** (unnecessary microservices, premature distributed state, or unjustified infrastructure complexity), and drafts **Architecture Decision Records (`ADRs`)** capturing considered alternatives and trade-off rationale.
4. **Validate Diagram Syntax Deterministically**: If generating `Mermaid` architecture diagrams, run a deterministic syntax validator on node identifiers and edge labels (quoting labels containing parentheses or special characters) before rendering or exporting.

### Phase 3: Validation, Assurance (`ATAM`), and Focused Patch Refinement

1. **Execute ATAM-Grounded Quality & Risk Assessment**: Evaluate the candidate architecture package for quality-attribute satisfaction, sensitivity points, tradeoff points, and architectural risks. Generate a structured **Risk Register** with explicit mitigation notes and an **Architecture Assessment Report (`AAR`)**.
2. **Run Deterministic Traceability & Checklist Verification**:
   - **Deterministic Traceability Rules**: Programmatically verify completeness and bidirectional links across the persistence store—confirming that **every architectural driver traces back to at least one requirement**, **every ADR references at least one architectural driver**, and **every component/API contract maps to an approved driver or requirement**.
   - **Checklist Verification Agent & Focused Patch Refinement**: When the checklist verification agent identifies a gap on a specific item, invoke a **Refinement Agent** to generate a **focused patch** that repairs only the failing checklist item while preserving the rest of the validated artifact (avoiding full-document regeneration drift).
3. **Enforce Bounded Schema Retries**: If an agent call fails transient network execution, retry up to a fixed cap; if an output fails structured schema parsing, invoke the agent **at most once more** with reinforced structured-output instructions, and mark the run failed if the second attempt fails (never loop open-endedly).
4. **Gate 3 (Architecture Baseline Lock)**: Require all deterministic traceability rules to pass, all critical evaluator verdicts to be addressed, and the human architect to explicitly approve and lock the **Software Architecture Document (`SAD`)** and **Full Architecture Package (`FAP`)**. Record any subsequent stage unlock in an immutable audit log.

### Phase 4: Architecture-Aligned Delivery & Brownfield Evolution Monitoring

1. **Compile Implementation Guidance & Conformance Contracts**: Translate the locked architecture baseline (`SAD`, `ADRs`, data ownership map, API schemas) into explicit implementation constraints and module boundary rules for downstream coding agents or developers.
2. **Verify Implementation Conformance & Detect Drift**: During iterative feature delivery or brownfield evolution, run reverse-engineering, gap-analysis, and **architectural drift detection** agents to compare proposed code changes and current repository structure against the locked architecture baseline—flagging unauthorized cross-component dependencies, violated data ownership, or unrecorded technical debt before merge.
3. **Route Models by Task Role**: Assign lighter, fast models to short syntax checks and utility calls, default structured models to stage artifact generation, and strong reasoning models to cross-stage consolidation, `ATAM` tradeoff critique, and validation.

---

## Environment Caveats

- **Repeatability of LLM Quality Scores**: Across repeated runs on identical inputs, LLM evaluator quality scores and risk severity ratings exhibit variance and occasionally shallow explanations. Rely on **deterministic structural/traceability checks**, **schema-bound checklists**, and **human approval gates** as the authoritative pass/fail barrier rather than raw scalar LLM quality scores.
- **Large Requirement Sets & Audio Intake**: Long audio recordings can suffer segmentation boundary errors during intake, and very large requirement sets increase Requirement Critic latency; chunk intake recordings along topic boundaries and batch requirement critic passes by functional domain.
- **Brownfield Drift Sensitivity**: Automated drift detection in legacy brownfield repositories is sensitive to missing or outdated baseline documentation; run the reverse-engineering agent first to establish a verified current-state baseline before scoring drift.

---

## Related Rules, Skills & Specs

- [`agent-human-interaction.md`](../../rules/agent-human-interaction.md) — Presenting structured, evaluable artifacts at human approval gates and reserving human review for architectural judgment
- [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md) — Generator-evaluator-human orchestration and role-matched model assignment
- [`requirements-driven-code-generation`](../requirements-driven-code-generation/SKILL.md) — Decomposing task prompts into formal contracts and requirement quality checks at the single-task level
- [`nextjs-public-agent-app.spec.md`](../../specs/nextjs-public-agent-app.spec.md) — Full-stack application architecture specification template
