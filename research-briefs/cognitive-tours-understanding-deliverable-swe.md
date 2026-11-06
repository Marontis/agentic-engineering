# Cognitive Tours: Making Understanding a Deliverable in AI-Assisted Development

> **Paper**: Storey, M.-A. (2026). *Cognitive Tours: Making Understanding a Deliverable in AI-Assisted Development*. arXiv:2611.08456.
> **Praxis source**: `src:2611-08456v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

As coding agents accelerate code generation, a team's capacity to produce working software outpaces its capacity to understand why the software is structured the way it is. Storey introduces **Cognitive Tours**, a conceptual framework and interactive web prototype (`https://cognitive-tours-demo.vercel.app/`) designed to make **human and shared team understanding an explicit, inspectable deliverable** alongside code and tests.

The paper grounds its design in a **Triple Debt Model of Software Health**:
1. **Technical debt**: Suboptimal code or architecture design choices that increase future implementation cost.
2. **Cognitive debt**: The absence or erosion of a team's shared mental model needed to explain how a system works or predict the impact of changes. Unlike individual developer confusion, cognitive debt is a collective property of the team.
3. **Intent debt**: The loss or absence of clearly articulated goals, domain constraints, and design rationale—including **discarded alternatives and trade-offs**—explaining what the system is for and how it should evolve.

While automated documentation generators (`DeepWiki`, `Code Wiki`, `As-built architecture`) and agent-oriented specification frameworks (`Spec Kit`, `Kiro`, `Lattice`) optimize for speed or agent consumption by having AI write the documentation, they bypass human sensemaking. Cognitive Tours instead enforces **productive friction**: AI agents assist by auditing staleness, detecting architectural drift against git history, and proposing factual graph scaffolding, but **humans are required to author the rationale, curate the narrative stops, and record the "why"**.

## Core Architecture of Cognitive Tours

Cognitive Tours represents a software project's socio-technical knowledge as a persistent spatial graph composed of three primitives:

| Primitive | Role in Preserving Understanding & Intent | Concrete Artifact Examples |
|:----------|:------------------------------------------|:---------------------------|
| **1. Waypoints** | Selected socio-technical landmarks/anchors across the project (deliberately curated, not an exhaustive dump of every file or symbol) | System goals, user needs, features, Architecture Decision Records (ADRs), AI agent instructions (`CLAUDE.md`/`AGENTS.md`), code components, tests, known risks, and **unresolved open questions** |
| **2. Named Untyped Relationships** | Directed edges with free-form human-written labels explaining *why* two waypoints relate on a persistent spatial layout | `"constrains"`, `"motivates"`, `"implements"`, `"mitigates risk in"`, `"supersedes"` |
| **3. Curated Tours & Docent Annotations** | Ordered narrative paths through selected waypoints paired with **docent annotations**—human-written bridge commentary between stops | Onboarding tours, feature-evolution walkthroughs, security/risk review paths, and post-sprint architecture reviews explaining *what matters, what to notice, and why* |

Each waypoint links directly to live repository artifacts (GitHub files, line ranges, commits, issues, or IDE targets) so developers can jump between high-level rationale and concrete source code.

## Human-AI Division of Labor & Read-Only Agent Skills

A central contribution of the paper is its strict **Human-AI Division of Labor** (Section III-B), contrasting Cognitive Tours against seven related paradigms (`CodeTours`, `NotebookLM`, `DeepWiki`/`Code Wiki`, `Spec Kit`/`Kiro`, `Lattice`, `As-built architecture`, and `Diagnostic Legibility`). To prevent agents from turning cognitive tours into unread, AI-generated boilerplate, the system pairs its graph API (`/api/data`) with **four strictly read-only Claude Code skills**:

| Claude Code Skill | Input Sources Inspected | Permitted Agent Output | Enforced Human-in-the-Loop Constraint ("Productive Friction") |
|:------------------|:------------------------|:-----------------------|:--------------------------------------------------------------|
| **`/audit-waypoints`** | `/api/data` waypoints, git history since a target date, and linked repository files | Reports **one staleness or drift finding at a time** (e.g., renamed/deleted files, modified components, or code changes that contradict an existing ADR waypoint) | **Read-only**: Never mutates the graph automatically; waits for the developer to inspect and resolve each finding |
| **`/audit-tours`** | `/api/data` tours, stop sequences, docent annotations, and recent git commits | Identifies tours whose stops or docent commentary have drifted out of sync with recent code changes, presented **one finding at a time** | **Read-only**: Requires the human author to decide how the narrative should be updated |
| **`/suggest-waypoint`** | Recent git commits, file diffs, and existing `/api/data` graph topology | Proposes **only factual fields** (`label`, `type`, `file path`, and candidate `edges`) followed by **Socratic questions** asking the human why the change was made | **Withholds rationale**: Never writes the waypoint description or design rationale; prompts the human to articulate the intent in their own words |
| **`/suggest-tour`** | Existing waypoints, edges, and recent feature/commit clusters | Proposes a candidate **stop order** across relevant waypoints plus Socratic prompts for each transition | **Withholds docent commentary**: Never writes the bridge narrative between stops; the human must explain how the stops connect |

## Longitudinal Self-Use Case Study (6 Months)

Storey reports a six-month longitudinal self-use evaluation while building the Cognitive Tours platform itself with AI coding assistance:
- **Graph scale at evaluation**: `59` waypoints, `73` named edges, and `5` curated tours.
- **Catching silent architectural drift after high-velocity AI coding**: Following a rapid evening coding session with an AI agent that produced **`>20` commits** (`28` commits total since October 20), the author ran `/suggest-waypoint` to reconcile her mental model with what the agent had actually built.
- **Surfacing unrecorded ADR contradictions**: The skill analyzed the `28` commits against the existing `59`-waypoint map and ranked as its **`#1` suggestion** a fundamental architectural shift introduced during the AI session—*"One site and database per team"*—which had never been recorded in the map and **directly contradicted an existing Architecture Decision Record (`ADR 007`) that was still marked `Accepted`**.
- **Sensemaking outcome**: Because `/suggest-waypoint` supplied only the factual file/commit anchors and Socratic prompts rather than auto-generating a summary, it forced the author to confront the architectural divergence, update the superseded ADR status, and explicitly document the rationale for the new per-team isolation model.

## Why Not a Skill?

This paper is a **vision and interactive tool-design paper** reinforced by a single-author qualitative self-use reflection (`59` waypoints, `73` edges, `5` tours across `28` recent commits), rather than a quantitatively benchmarked algorithmic procedure. However, its core design pattern—**restricting documentation-maintenance agents to read-only staleness auditing and factual scaffolding with Socratic prompts, while reserving rationale and narrative authoring for humans to prevent cognitive and intent debt**—provides a concrete governance rule for human-agent workflows. This principle is captured in [agent-human-interaction.md](../rules/agent-human-interaction.md).
