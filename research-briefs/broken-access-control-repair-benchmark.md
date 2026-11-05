# BAC-Bench: Repairing Broken Access Control in Web Applications with LLMs

> **Paper**: [Repairing Broken Access Control in Web Applications with LLMs: An Empirical Benchmark Study](https://arxiv.org/abs/2610.34290) (Liu et al., Oct 2026)
> **Praxis source**: `src:2610-34290`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is an empirical benchmark study (`BAC-Bench`) and a four-dimensional diagnostic taxonomy comparing eight base LLMs, two lightweight repair scaffolds (`Apply-Feedback` and `Navigate-and-Locate`), and two commercial coding agents (`Claude Code` and `Codex`) on 46 real-world Broken Access Control (BAC) vulnerabilities. Its primary contributions are quantitative benchmark findings — showing that repository navigation and diff-application feedback close nearly the entire gap between single-turn LLMs and full commercial coding agents, and characterizing why access-control patches fail even when they apply cleanly — which directly enrich our vulnerability-repair and evaluation rules in `rules/agent-evaluation-quality.md` and `rules/agent-sandbox-safety.md` alongside [`authorization-closure-repair`](../skills/authorization-closure-repair/SKILL.md).

---

## Core Concept

Unlike local memory-safety crashes (where the bug and fix reside near a stack trace), **Broken Access Control (BAC, CWE-284 / OWASP A01)** is a relational, repository-level design flaw: repairing a missing or incomplete permission check requires discovering how a specific application encodes principals, roles, resources, and custom authorization helpers across multiple architectural layers.

Liu et al. build **BAC-Bench**, a reproducible Dockerized benchmark of **46 real-world BAC CVEs** across **6 open-source web applications** and **4 programming languages**:
- **OpenEMR** (PHP — hybrid ACL + RBAC via `phpGACL` `AclMain::aclCheckCore`)
- **Nextcloud Server** (PHP — hybrid DAC + ACL + RBAC middleware/controllers)
- **XWiki Platform** (Java — hierarchical ACL + group document rights)
- **Apache InLong** (Java — RBAC + tenant/group ownership checks)
- **Usememos** (Go — RBAC session/resource ownership checks)
- **BookWyrm** (Python — RBAC + ActivityPub privacy/permission decorators)

Every benchmark task pairs two executable dynamic oracles in an idempotent sandbox:
1. **PoC Validation Oracle (Vulnerability Closure)**: Replays the exploit using honeytokens and database-state assertions to verify that unauthorized access is blocked.
2. **Functional Validation Oracle (Preservation)**: Runs targeted authorized user workflows to ensure the patch does not trivially pass the PoC by breaking the endpoint or over-restricting legitimate users.

To diagnose *why* patches fail beyond binary test outcomes, the authors introduce a **4-Dimensional BAC Repair-Strategy Framework** (validated via blinded human audit by three PhD security researchers across 108 failing patches / 432 cells at **96.3% agreement, Cohen's $\kappa = 0.926$**):
- **Position** ($\kappa = 0.955$): Architectural layer (Presentation, Control, Business, Data, or Cross-Cutting Authorization) and placement along the vulnerable execution path.
- **Coverage** ($\kappa = 1.000$): Ratio $k/n$ of vulnerable code units sharing the same root cause that receive a structural check ($k = n$ complete vs. $k < n$ incomplete).
- **Mechanism** ($\kappa = 0.874$): How the check is implemented — ① *Standard mechanism reuse* or ② *Reliable project-native mechanism* (Success) vs. ③ *Fragile substitute mechanism* or ④ *Mechanism implementation failure* (Failure).
- **Content** ($\kappa = 0.781$): Whether the enforced policy predicate (actor, resource, privilege level, ownership binding) is `Correct` (Success) vs. `Partially correct` or `Incorrect` (Failure).

### Key Findings

| Model / Agent | Single-Turn Base (File-Restricted) Effective Repair | `+ Apply-Feedback (AF)` ($K \le 5$ diff-check turns) | `+ AF + Navigate-and-Locate (NL)` ($M \le 10$ repo-browse turns) | Commercial Agent Effective Repair |
|:---|:---:|:---:|:---:|:---:|
| **Claude Code** (`v2.1.160`, Opus 4.8) | — | — | — | **78.99%** |
| **Codex** (`v0.139.0`, GPT-5.5) | — | — | — | **76.81%** |
| *Commercial Agent Macro-Average* | — | — | — | **77.90%** |
| **Claude Opus 4.8** | 30.43% (42.03% apply) | 56.52% (96.38% apply) | **75.36%** (+44.93 pp) | — |
| **GPT-5.5** | **60.87%** | 65.94% (100.0% apply) | **73.19%** (+12.32 pp) | — |
| **Qwen3.7-Max** | 38.41% | 55.80% | **71.01%** (+32.60 pp) | — |
| **Gemini 3.5 Flash** | 30.43% | 44.20% | **64.49%** (+34.06 pp) | — |
| **GLM-5.2** | 41.30% | 51.45% | **63.77%** (+22.47 pp) | — |
| **DeepSeek-V4 Pro** | 36.23% | 47.83% | **62.32%** (+26.09 pp) | — |
| **MiMo-V2.5 Pro** | 26.09% | 42.75% | **60.14%** (+34.05 pp) | — |
| **Kimi K2.7-Code** | 37.68% | 44.93% | **57.97%** (+20.29 pp) | — |
| **8-Model Macro-Average** | **37.68%** (62.50% apply) | **51.18%** (96.11% apply) | **66.03%** (93.39% apply) | — |

- **Two minimal scaffolds nearly close the base-to-agent gap (`37.68%` $\to$ `66.03%`)**:
  - In single-turn repair (even when given the exact files modified by the official developer patch), 8 frontier LLMs average only **37.68%** effective repair (PoC pass **42.75%**, Functional pass **49.46%**) because **37.50%** of generated unified diffs fail `git apply` due to hallucinated line numbers and hunk headers (Claude Opus 4.8's single-turn applicability is only **42.03%**).
  - Adding **`Apply-Feedback` (AF)** ($K \le 5$ turns returning `git apply --check` diagnostics) raises macro-average patch applicability from **62.50% to 96.11%** (+33.61 pp) and effective repair to **51.18%** (+13.50 pp) — see [`deterministic-span-editing`](../skills/deterministic-span-editing/SKILL.md).
  - Adding **`Navigate-and-Locate` (NL)** ($M \le 10$ turns where the model inspects the repository directory tree and requests sibling files before patching) lifts macro-average effective repair to **66.03%** (+28.35 pp over single-turn base; PoC pass **72.37%**, Functional pass **78.35%**). With `AF + NL`, **Claude Opus 4.8 reaches 75.36%** (within **3.63 pp** of Claude Code's **78.99%**) and **GPT-5.5 reaches 73.19%** (within **3.62 pp** of Codex's **76.81%**), without shell execution or dynamic test feedback during generation.
- **4-Dimensional failure breakdown across 2,735 applicable patches (810 dynamically failing; Tables 7 & 8)**:
  - Overall failure prevalence ranks **Content (23.44%) > Mechanism (18.21%) > Coverage (10.60%) > Position (6.00%)**.
  - Repository navigation (`AF` $\to$ `AF + NL`) sharply reduces failures across every dimension by letting models see existing project-native authorization helpers and sibling endpoints: **Coverage failures drop by 66.02% relative** (16.59% $\to$ 5.64%), **Mechanism failures by 57.69%** (27.16% $\to$ 11.49%), **Position failures by 52.93%** (9.27% $\to$ 4.36%), and **Content failures by 42.05%** (31.57% $\to$ 18.30%).
  - Among dynamically failing patches (Table 8):
    - *PoC fail + Functional pass* ($N = 588$, under-blocking): driven by **Content failures (81.12%)** and **incomplete Coverage (45.92%)**.
    - *PoC pass + Functional fail* ($N = 169$, over-blocking legitimate users): Position (8.88%) and Coverage (9.47%) are usually right, but **Content (72.19%)** and **Mechanism (55.62%)** fail — proving that PoC-only validation falsely credits over-restrictive patches that break production functionality.
    - *Both fail* ($N = 53$): dominated by **Mechanism implementation failures (84.91%)**.
- **LLM patches expose flaws in official human CVE fixes and uncover a 3-year zero-day (`CVE-2026-63040`)**:
  - 6 official developer patches in the wild had latent defects caught by dual-oracle analysis (e.g., OpenEMR `CVE-2022-4505` used `if (!array_search(...))` in PHP, treating index `0` as falsy and locking out legitimate users; OpenEMR `CVE-2023-2946` checked non-existent ACO `'prescriptions'` instead of `'rx'`; Usememos `CVE-2022-4684`, `CVE-2022-4802`, and `CVE-2022-4803` had incomplete coverage/position).
  - On Apache InLong `CVE-2023-31066`, LLMs equipped with repository navigation patched not only `delete` but also the sibling `forceDelete` method that the 2023 official developer patch missed — discovering a 3-year-old zero-day vulnerability (**assigned CVE-2026-63040**).

---

## Relevance to Praxis

- **Dual-oracle validation for access-control repairs (`rules/agent-evaluation-quality.md`, `rules/agent-sandbox-safety.md`)**: Extends *"DON'T: Validate repairs using crash suppression alone"* (`PatchBench` / `SecProbe`) to access-control vulnerabilities: **169 of 810** failing patches in `BAC-Bench` passed the exploit PoC oracle while breaking authorized user workflows (`PoC pass + Functional fail`) due to wrong policy content (72.19%) or fragile mechanisms (55.62%). Always pair exploit-closure PoCs with authorized-user preservation tests.
- **Repository context discovery before access-control patching**: Because authorization conventions (`phpGACL` ACO names, project-native middleware decorators, sibling CRUD endpoints) cannot be inferred from the vulnerable file alone, providing read-only repository navigation (`Navigate-and-Locate`) cuts incomplete-coverage failures by **66.02%** and mechanism failures by **57.69%** (complementing [`authorization-closure-repair`](../skills/authorization-closure-repair/SKILL.md) and [`cost-effective-repo-exploration`](../skills/cost-effective-repo-exploration/SKILL.md)).
