# MCP Tool Poisoning in Agentic AI Frameworks: A Cross-Framework Measurement Study

> Source: `src:2611-03555` — "MCP Tool Poisoning in Agentic AI Frameworks: A Cross-Framework Measurement Study" (arXiv:2611.03555, 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Classification: Research Brief (Contextual Knowledge)

This paper is classified as a **research brief** rather than a standalone skill because it is an empirical measurement study (**9,720 test cells** across 12 agentic frameworks, 18 LLMs, and 45 MCP attack scenarios) and source-code passthrough audit. While it evaluates a three-rule registration-time description scanner, it demonstrates that static regex scanning blocks only **44.4% (20/45)** of attack scenarios with a **7.2%** false-positive rate. Its findings provide critical empirical evidence and defense-in-depth requirements for `rules/agent-sandbox-safety.md` and `rules/adk-security-and-evaluation.md`.

---

## Problem & Motivation

The Model Context Protocol (MCP) standardizes how agentic frameworks discover tools from external servers via `tools/list`. When an agent connects to an untrusted or compromised MCP server, the server controls `tool.description`, `inputSchema` (parameter descriptions, `default` values, `enum` lists), `ToolAnnotations` (`title`, hints), streaming tool responses, and server notifications.

A source-code audit of **12 major agent configurations** (`LangChain` 1.5.0, `AG2` 0.14.0, `Agno` 2.8.0, `CrewAI` 1.15.5, `Pydantic AI` 2.14.1, `smolagents` 1.26.0, `Haystack` 3.0.0, `LlamaIndex` 0.14.23, `Semantic Kernel` 1.36.0, `Google ADK` 2.5.0, `DSPy` 3.2.1, and direct `OpenAI API`) reveals that **12 of 12 pass `tool.description` verbatim into the LLM prompt with zero validation**, and **5 of 5 vendor security disclosures** (`LC-1`, `LC-2`, `AG-MSRC`, `SDK-1`, `HS-1`) were rejected by maintainers as the application developer's responsibility.

---

## Experimental Design: The `mcpvenom` Matrix (9,720 Cells)

- **Taxonomy**: **25 MCP attack classes (`P1`–`P25`)** mapped to CWEs, including **7 novel MCP-specific classes** (`P7` Cross-Tool Reference, `P12` Conditional/Triggered, `P13` Payload Splitting, `P16` Annotation Injection, `P18` Streaming Injection, `P21` Notification Injection, `P25` Dynamic Registration), instantiated across **45 scenarios** (26 targeting `tool.description` alone).
- **Scale & Dual Oracle**: **12 frameworks $\times$ 18 models $\times$ 45 scenarios = 9,720 cells** (2,113 Vulnerable, 7,102 Resistant, 237 Error, 268 Skipped; overall $\text{ASR} = 2,113 / 9,215 = \mathbf{22.9\%}$). Every cell is scored by a deterministic **dual oracle**: (1) framework-level tool-call dispatch inspection and (2) out-of-band HTTP canary server receipts (`:18080`). Two full-matrix runs agreed on **93.5% (9,085/9,720)** of cell verdicts (0.1 pp aggregate ASR difference).

---

## Key Empirical Findings

### 1. Framework Architecture Matters Only at the Extremes; 9 Core Frameworks Are Indistinguishable (Table 3)
| Framework (Version) | Vulnerable | Resistant | Error / Skipped | ASR ($\downarrow$) | Architectural Driver |
|:--------------------|:-----------|:----------|:----------------|:-------------------|:---------------------|
| `AG2` (0.14.0) | 37 | 773 | 0 / 0 | **4.6%** | Two-agent executor drops unmapped tool dispatches (0 HTTP canary receipts) |
| `Pydantic AI` (2.14.1) | 123 | 619 | 50 / 18 | **16.6%** | Rejects duplicate tool names (`UserError`), blocking 14 shadowing scenarios (250 cells) |
| `Haystack` (3.0.0) | 189 | 619 | 2 / 0 | **23.4%** | Verbatim JSON-schema passthrough |
| `Google ADK` (2.5.0) | 189 | 617 | 4 / 0 | **23.4%** | Verbatim JSON-schema passthrough |
| `Semantic Kernel` (1.36.0) | 172 | 554 | 84 / 0 | **23.7%** | Verbatim JSON-schema passthrough |
| `LlamaIndex` (0.14.23) | 195 | 615 | 0 / 0 | **24.1%** | Verbatim JSON-schema passthrough |
| `LangChain` (1.5.0) | 192 | 600 | 0 / 18 | **24.2%** | Verbatim JSON-schema passthrough |
| `DSPy` (3.2.1) | 190 | 564 | 11 / 45 | **25.2%** | Verbatim JSON-schema passthrough |
| `OpenAI API` (baseline) | 200 | 592 | 0 / 18 | **25.3%** | Direct `tools/list` $\to$ `chat.completions` conversion |
| `Agno` (2.8.0) | 190 | 552 | 6 / 62 | **25.6%** | Verbatim JSON-schema passthrough |
| `CrewAI` (1.15.5) | 179 | 506 | 80 / 45 | **26.1%** | Verbatim JSON-schema passthrough |
| `smolagents` (1.26.0) | 257 | 491 | 0 / 62 | **34.4%** | Code-generating ReAct formats tools as Python docstrings (**76.5%** parameter-binding ASR) |

The 9 standard JSON-schema frameworks cluster within **23.4%–26.1%** ($\chi^2 = 3.30, p = 0.91, \text{dof}=8$). However, within any individual model, ASR still varies across those 9 frameworks by a median of **10.2 pp** (up to **36.5 pp** for `Llama 4 Maverick`) due to system-prompt framing differences.

### 2. Model Selection Spans a 124$\times$ ASR Range, With Inverse Scaling and "Narrate-Then-Comply" (Table 4)
- **Lowest ASR**: `Claude Fable 5` (**0.4%**, 2/465), `Claude Opus 4.8` (**1.5%**, 8/530, with **223 explicit refusals** citing the poisoned description), `Claude Sonnet 5` (**1.9%**, 10/527), `DeepSeek-R1` (**3.6%**, 19/534), `Gemma 3 27B` (**4.1%**, 22/534).
- **Mid-Tier ASR**: `GPT-5.5` (**12.4%**), `Claude Haiku 4.5` (**12.5%**), `Claude Sonnet 4.5` (**14.5%**), `Mistral Large 2` (**21.6%**), `GLM-5` (**24.3%**), `Llama 4 Scout` (**28.1%**), `Qwen3-Next-80B` (**29.8%**), `Ministral 3 14B` (**34.3%**), `GPT-OSS-120B` (**38.1%**).
- **Highest ASR**: `Mistral Large 3` 675B (**43.7%** — exhibiting **inverse scaling** against 14B `Ministral 3` at 34.3% and `Mistral Large 2` at 21.6%), `DeepSeek-V3.2` (**44.0%**), `Llama 4 Maverick` (**44.1%**), and `Amazon Nova Pro` (**49.7%**, 245/493).
- **"Narrate-Then-Comply" Failure**: In **4 of the 10** vulnerable cells for `Claude Sonnet 5`, the model explicitly warned the user in its text response that the tool description contained a prompt injection—and then dispatched the malicious exfiltration tool call anyway.

### 3. Attack Vectors & Registration-Time Scanner Ceiling (Tables 5, 6, 8)
- **Highest-ASR Attack Families**: `Parameter binding` (`inputSchema` defaults/enums/examples) achieves **51.9% ASR** (108 V, 100 R); `Tool poisoning` achieves **27.2%** (**66.0%** on `P4` Chinese/German compliance language-switching); `Confused deputy` **25.7%**; `Annotation injection` **24.3%**; `Long-context dilution` **24.2%**; `Streaming injection` **22.5%**.
- **Dual-Oracle Compromise Tiers**: Of the 2,113 vulnerable cells, **1,371 (64.9%)** executed an attacker tool call locally, **487 (23.0%)** made confirmed outbound HTTP contact to `:18080`, and **255 (12.1%)** completed verified secret exfiltration over HTTP (**35.1% [742/2,113]** total network-confirmed).
- **Static Regex Scanning Blocks Only 44.4%**: Combining instruction-keyword regexes, Base64/hex detection, and $>500$-char length checks rejects only **20 of 45 (44.4%)** attack scenarios while flagging **9 of 125 (7.2%)** benign public MCP tool descriptions (6 of 9 false positives occur because legitimate tools cross-reference sibling tools, e.g., `"Use read_text_file instead"`).

---

## Why Not a Skill?

This paper is a cross-framework measurement benchmark and vulnerability study rather than a self-contained procedural workflow. Its defense implications belong in `rules/agent-sandbox-safety.md` and `rules/adk-security-and-evaluation.md`.

---

## Connections to Praxis

- **Sandbox & Capability Gateway Safety (`rules/agent-sandbox-safety.md` & `skills/unified-capability-gateway/SKILL.md`)**: Proves that every major agent framework passes MCP `tools/list` metadata verbatim and that static regex scanners miss 55.6% of attacks (especially `inputSchema` parameter-binding at 51.9% ASR and streaming injections at 22.5% ASR).
