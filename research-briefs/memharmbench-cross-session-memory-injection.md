# MemHarmBench: Evaluating Cross-Session Prompt Injection in Memory-Persistent AI Agents

> **Source**: [arXiv:2611.01700](https://arxiv.org/abs/2611.01700) — Zhihua Wang, Yunhao Feng, Yifeng Gao, Rui Pan, Baiheng Zhao, Zixing Chen, Xingjun Ma (2026-11-01)
> **Praxis Source ID**: `src:2611-01700`
> **Category**: Research Brief (Memory-Persistent Agent Security & Cross-Session Prompt Injection Benchmark)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

This paper introduces **MemHarmBench**, a victim-centric benchmark and four-metric empirical evaluation protocol characterizing cross-session prompt injection in file-backed memory-persistent agents (`OpenClaw` and `Claude Code`). Because it provides an evaluation benchmark and factor analysis of vulnerability persistence rather than a standalone defensive algorithm or reusable agent procedure, it is cataloged as a research brief with defensive rule contributions to [`../rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

---

## Core Findings

### 1. Stage-Separated Multi-Stakeholder Threat Model

Unlike single-session prompt injection benchmarks, **MemHarmBench** separates an **exposure session** (where the agent summarizes or processes untrusted external content and updates persistent workspace memory such as `MEMORY.md` or `CLAUDE.md`) from a fresh **trigger session** (where a benign user prompt activates the poisoned memory entry). Across **288 cases** (**8 direct-instruction [DPI]** templates = 96 cases; **16 indirect-content [IPI]** templates = 192 cases across `EML`, `ICS`, `HTML`, `CSV`, `JSON`, `Markdown`, and `Log` formats), the benchmark evaluates **12 harm objectives** across **3 victim categories**:
- **User (`U1`–`U4`)**: Privacy Exfiltration (`U1`), Decision Manipulation (`U2`), Communication Integrity Distortion (`U3`), Workflow Sabotage (`U4`).
- **Workspace/Project Owner (`W1`–`W4`)**: Code/Data/Config Integrity Tampering (`W1`), Secret/Credential Exfiltration (`W2`), Privilege & Policy Weakening (`W3`), Resource Abuse & Unbounded Execution (`W4`).
- **External Stakeholder (`X1`–`X4`)**: Impersonation & Outbound Misrepresentation (`X2`/`X1`), Third-Party Data Exposure (`X2`), Shared-Artifact Contamination (`X3`), Cross-Boundary Service Abuse (`X4`).

### 2. Main Evaluation Across 4 Agent–Model Configurations (3,456 Episodes)

Tables 3 and 7 evaluate `OpenClaw 2026.7.1` and `Claude Code 2.1.228` paired with `GPT-5` and `Gemini-2.5-Flash` across 3 full repetitions (trigger metrics `ASR`, `UTDR`, and `ATAR` are conditioned on exposure-stage retention `PMIR = 1`):

| Agent System | Backbone | Mode | `PMIR` (n / N, %) | Conditional `ASR` (%) | Conditional `UTDR` (%) | Conditional `ATAR` (%) |
|:-------------|:---------|:-----|:------------------|:----------------------|:-----------------------|:-----------------------|
| **OpenClaw** | `GPT-5` | IPI | 480 / 576 (**83.33%**) | **75.00%** (360/480) | 13.33% (64/480) | 6.67% (32/480) |
| **OpenClaw** | `Gemini-2.5-Flash` | IPI | 432 / 576 (**75.00%**) | **76.39%** (330/432) | 17.82% (77/432) | 8.10% (35/432) |
| **Claude Code** | `GPT-5` | IPI | 528 / 576 (**91.67%**) | **62.50%** (330/528) | 12.31% (65/528) | 3.41% (18/528) |
| **Claude Code** | `Gemini-2.5-Flash` | IPI | 480 / 576 (**83.33%**) | **59.38%** (285/480) | 16.04% (77/480) | 3.33% (16/480) |
| **OpenClaw** | `GPT-5` | DPI | 252 / 288 (**87.50%**) | **88.10%** (222/252) | 16.67% (42/252) | 7.14% (18/252) |
| **OpenClaw** | `Gemini-2.5-Flash` | DPI | 240 / 288 (**83.33%**) | **90.00%** (216/240) | 20.00% (48/240) | 7.50% (18/240) |
| **Claude Code** | `GPT-5` | DPI | 264 / 288 (**91.67%**) | **81.82%** (216/264) | 14.77% (39/264) | 3.41% (9/264) |
| **Claude Code** | `Gemini-2.5-Flash` | DPI | 252 / 288 (**87.50%**) | **75.00%** (189/252) | 19.05% (48/252) | 4.76% (12/252) |

- **Stealthy Cross-Session Compromise (`ASR = 1, UTDR = 0, ATAR = 0`)**: Averaged across the 4 configurations under IPI, **55.71%** of `PMIR = 1` episodes execute the attacker's payload while formally completing the user's task (`UTDR = 0`) and generating zero trajectory anomalies (`ATAR = 0`).
- **Silent Integrity & Shared-Artifact Contamination (`W1` & `X3`)**: Both `W1` and `X3` reach **85.18%** conditional IPI `ASR` with **83.42%** (`W1`) and **82.62%** (`X3`) stealthy harm rates, whereas `W4` (Resource Abuse) exhibits the highest trajectory anomaly rate (`ATAR` = **30.66%** vs. `ASR` = **35.43%**).
- **Write-Selective vs. Execution-Selective Harnesses**: `Claude Code` writes injected rules into persistent memory more frequently than `OpenClaw` (`PMIR` **83.33%–91.67%** vs. **75.00%–83.33%** on IPI), but `OpenClaw` executes retained rules at a higher conditional rate (`ASR` **75.69%** vs. **60.94%** on IPI).

### 3. Controlled Factors & Visual IPI Generalization

1. **Exposure-Task Semantic Alignment (`U3`, 120 cases/condition, `GPT-5`, Table 9)**: High semantic alignment between the untrusted carrier document and the injected rule increases `PMIR` by **+30.00 pp** on `OpenClaw` (`30.00%` $\to$ `60.00%`) and **+25.00 pp** on `Claude Code` (`25.00%` $\to$ `50.00%`), raising full-cohort trigger adoption from **20.00% to 45.00%** (`OpenClaw`) and **15.00% to 35.00%** (`Claude Code`). Changing the exposure task to an unrelated goal reduces full-cohort adoption to **5.00%** and **2.50%**.
2. **Persistence Across Intervening Sessions ($d \in \{0, 2, 4\}$, `Claude Code`, Table 10)**: Four intervening benign sessions that legitimately update workspace memory reduce `PMIR` by only **-6.67 pp** (`GPT-5`: `50.00%` $\to$ `43.33%`; `Gemini-2.5-Flash`: `40.00%` $\to$ `33.33%`) and full-cohort adoption by only **-5.00 pp** (`GPT-5`: `35.00%` $\to$ `30.00%`; `Gemini-2.5-Flash`: `25.00%` $\to$ `20.00%`).
3. **Cross-Field Scope Mismatch (`W1`, `Claude Code`, Table 11)**: When the injected `applies_to_record` cue conflicts with the trigger record, `PMIR` drops by **-20.00 pp** (`60.00%` $\to$ `40.00%` on `GPT-5`; `50.00%` $\to$ `30.00%` on `Gemini-2.5-Flash`), yet conditional `ASR` among retained rules remains **62.50%** (`30/48`) and **66.67%** (`24/36**)—showing that agents fail to enforce record-scope predicates at trigger time.
4. **Multimodal Visual IPI (`Claude Code + Claude Haiku 5.5`, 240 cases/condition, Tables 5 & 12)**: Rendering indirect payloads inside PNG images (`Visual injection`) achieves **52.50%** `PMIR` (`126/240`) and **40.00%** full-cohort trigger adoption (`96/240`, **71.43%** conditional `ASR` when `PMIR = 1`), nearly matching `Matched text` (**60.00%** `PMIR`, **42.50%** full-cohort adoption) compared to **2.50%** (`6/240`) on `Clean image` controls.

---

## Relevance to Praxis

- **Memory Write Provenance & Out-of-Band Approval ([`../rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md))**: Because **55.71%** of cross-session IPI compromises produce neither task failure (`UTDR = 0`) nor trajectory anomalies (`ATAR = 0`) at trigger time—and **83.42%** of config/code tampering (`W1`) is completely silent—output task checks and runtime trajectory anomaly monitors cannot substitute for exposure-stage write isolation on `MEMORY.md` / `CLAUDE.md`.
- **Complementary Skills**: Pair with [`mcp-decode-provenance-binding`](../skills/mcp-decode-provenance-binding/SKILL.md) (to taint-tag OCR/image and external file reads) and [`out-of-band-hitl-verification`](../skills/out-of-band-hitl-verification/SKILL.md) (to gate persistent memory/config file modifications).

---

## Key Citations

- **Greshake et al. (2023)** — *Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection* — Foundational indirect prompt injection taxonomy.
- **Debenedetti et al. (2024)** — *AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents* — Single-session tool-use prompt injection benchmark.
