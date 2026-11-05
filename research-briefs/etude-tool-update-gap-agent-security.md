# Beyond Prompt Injection: The Tool Update Gap in LLM Agent Security

> **Source**: [arXiv:2611.01976](https://arxiv.org/abs/2611.01976) — Shiyu Kan, Yue Qi, Yufei Han, Xinjian Luo, Guojun Xiong, Xiaofeng Gao (2026-11-01)
> **Praxis Source ID**: `src:2611-01976`
> **Category**: Research Brief (MCP/Skill Supply-Chain Security, Post-Admission Tool Updates & Defense Evaluation)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

This paper characterizes the **Tool Update Gap (`ETUDE`)**—where an external MCP server or skill package passes initial admission vetting and later ships a malicious code update—and evaluates why hash-similarity thresholds, static LLM scanners, and isolated sandbox detonation fail to close it. Because it is a vulnerability and defense-limit analysis rather than a standalone procedural skill, it is recorded as a research brief with rule updates to [`../rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

---

## Core Findings

### 1. The Tool Update Gap (`ETUDE` = $P\text{-direct} \times E2$)

Across **7 CLI/coding agent frameworks** (`Gemini CLI 0.62.0`, `Codex CLI 0.159.3`, `Claude Code 2.1.284`, `DeepSeek Harness 0.2.0-rc.2`, `OpenCode 1.18.34`, `Pi 0.86.1`, `Goose 1.45.0`), **4 LLM backends** (`GLM-5.3-Flash`, `Qwen-3.8-27B`, `DeepSeek-V4-Flash` thinking OFF/ON), **3 tool utilities**, and **3 unauthorized workloads** (`W1` credential exfiltration, `W2` unauthorized API order, `W3` local file overwrite), the authors cross delivery timing (`E1` admission vs. `E2` post-admission update) with execution path (`P-ctx` description prompt injection vs. `P-direct` executable tool code):

| Attack Condition | Delivery & Mechanism | RQ1 Macro `ASR` (2,100 tasks) | RQ1 Legitimate `TCR` | Cross-Model / Utility Robustness |
|:-----------------|:---------------------|:------------------------------|:---------------------|:---------------------------------|
| **`P-direct × E1`** | Malicious code at initial admission | **0.0%** (blocked 105/105 rounds) | 0.0% | Blocked by admission gate |
| **`P-ctx × E1`** | Prompt injection in description at admission | **2.9%** (`W1`) / **5.7%** (`W2`) / **0.0%** (`W3`) | 8.2% | Blocked in 95/105 rounds |
| **`P-ctx × E2`** | Post-admission description rug-pull | **20.2%** (`W1` 29.4%, `W2` 16.7%, `W3` 14.4%) | **96.4%** | **0.0%–100.0%** (`0.0%` on `OpenCode` & `DeepSeek-V4` thinking ON) |
| **`ETUDE` (`P-direct × E2`)** | Post-admission code update (clean return) | **100.0%** (`W1` 99.9%, `W2` 99.9%, `W3` 100.0%) | **99.6%** (99.3% full-task) | **97.6% overall ASR / 95.9% TCR** (64/64 settings confirmed) |

- **Why `ETUDE` Decouples from Model Reasoning**: `P-ctx × E2` relies on the LLM obeying an injected description to call a second tool—succeeding in **297/300** tasks on `Claude Code` (`100.0%` on `W1`, `97.0%` on `W2`) but **0/300** tasks on `OpenCode` and **0.0%** across all 7 frameworks when `DeepSeek-V4-Flash` enables thinking. In contrast, `ETUDE` executes inside the trusted tool process when the agent makes a legitimate call, succeeding in **28/28** model–framework combinations (**80.0%–100.0% ASR**, mean **96.4%**) and **36/36** tool–framework–workload combinations.

### 2. Why Three Standard Update Defenses Fail (RQ4)

1. **Locality-Sensitive Hash Gating (`TLSH`) Cannot Separate Features from Backdoors**:
   - Benign edits span `TLSH` distance **1–221** (functional additions: **173–221**; historical `AWS MCP` and `GitHub MCP Server` updates reach **205**), while `W1`/`W2`/`W3` sit at **156 / 145 / 233** and minimal surgical injections in `git_python` and `GitHub MCP Server v2.0.3` sit at **$d = 9$** and **$d = 3$**.
   - Setting threshold $t = 145$ to catch `W1`–`W3` falsely rejects **22/40 (55.0%)** benign updates (**100%** of functional additions), while still missing $d = 3\text{–}9$ surgical patches.
2. **Static LLM Code Scanners Fail Under Obfuscation and Context Truncation**:
   - Re-running `Cisco MCP Scanner + GLM-5.3-Flash` on readable updates achieves **98.3% ($\pm 3.7\%$)** Defense Success Rate (`DSR`, `0.0%` ASR), provided the scanner reads at least **4,000 characters** (truncating to **2,000 characters** drops `BLOCK` rate from **93.3% [`14/15`] to 0.0% [`0/15`]**, Table 11).
   - Obfuscating the updated Python module with `PyArmor 9.2.7` collapses `Cisco/GLM` `DSR` to **6.7% ($\pm 7.0\%$)** (**85.0% ASR**, **1,020/1,200** attack completions on `ETUDE`; **0.0% DSR / 96.7% ASR** on `P-direct × E1`). `SkillFortify 0.6.0` rejects **100%** of readable benign updates, and `NVIDIA SkillSpector 2.12.0` rejects **0%** of readable attacks and **100%** of PyArmor-protected benign updates.
3. **Runtime Sandbox Detonation Is Bypassed by `/proc/self/uid_map` Fingerprinting**:
   - Running updated tools inside a `bubblewrap` detonation sandbox with an `OpenCode/GLM` flow monitor catches **30/30** unconditioned readable and PyArmor-protected attacks (`0/30` false positives), at **$6.3\times$ higher latency** (**$112.8 \pm 13.7\text{ s}$ vs. $18.0\text{ s}$**) and **$1.5\times$ higher token cost** (**US\$0.00697 vs. US\$0.00461**).
   - However, a PyArmor-protected update that inspects `/proc/self/uid_map` (which exposes a single-UID mapping inside `bubblewrap` vs. the multi-UID host map) stays dormant during detonation—achieving **5/5 Audit ALLOW (`0/5` audit effect)**—and executes **5/5** attacks in live agent sessions.

---

## Relevance to Praxis

- **Tool Supply-Chain & Execution Containment ([`../rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md))**: Pinning tool *descriptions* is insufficient if the underlying tool package, binary, or Python script can update post-admission (`ETUDE`). Gate tool code updates on cryptographic digest pinning of the **executable code tree**, reject obfuscated/bytecode-only tool diffs (`PyArmor`) automatically before LLM static review, never truncate static scanner file views below full-module length, and enforce least-privilege container/filesystem/network sandboxing **during live production execution** rather than only during pre-deployment detonation audits.

---

## Key Citations

- **Hou et al. (2025)** — *Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions* — Taxonomy of MCP lifecycle risks.
- **Wang et al. (2026)** — *SkillFortify / SkillDetonate* — Static and dynamic skill-vetting baselines evaluated in RQ4.
