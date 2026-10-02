# MCP-GRANITE: Tool-Interface Granularity for MCP-Based Agents

> **Source**: Paschalides, Symeonides, Pallis & Dikaiakos, arXiv:2609.24161, Sep 2026
> **Status**: Research Brief — controlled benchmark (granularity as the only varied factor)

## Why Not a Skill?

The paper is a benchmark measuring one design variable, how functionality is split into MCP tools. The takeaway is a design heuristic for MCP server authors, so it has been added to the existing [`mcp-server-design`](../skills/mcp-server-design/SKILL.md) skill ("Monolithic Single Tool" anti-pattern and a checklist item) instead of becoming a new skill.

## Core Concept

The domain logic and data store stay the same; only the tool schemas change, across four levels:

- **L4**: 8–10 fine-grained primitives (`set_device`, `read_sensor`)
- **L3**: about 4 task-class tools (`set_room_mode`, `manage_automation`)
- **L2**: 2 tools split by read/write (`*_query`, `*_control`)
- **L1**: one monolithic tool, with the operation passed as an argument

81 multi-step scenarios over 9 IoT domains (easy 1–2 calls, medium 4–5, hard 9–10), 9 small local models (268M–20.9B, quantized, on one T4), full factorial of **8,748 runs** against deterministic FastMCP mock servers.

## Key Findings

- **Middle granularity wins**: task completion L4 0.42, **L3 0.49**, L2 0.42, L1 0.36. The paper reports L3 as +16.4% over L4 and +33.6% over L1. L3 was best for **8 of 9** models (Mistral-Nemo preferred L4, 0.50 vs 0.48).
- **The bottleneck is argument construction, not tool selection**: argument accuracy L4 0.20, **L3 0.40**, L2 0.38, L1 0.26. Tool-selection F1 peaks at L2 (0.71), but that does not produce the best completion.
- **Monolithic tools fail badly**: the zero-tool-call rate (the model gives up without calling anything) is 10.2% at L4, 10.7% at L3, 14.6% at L2 and **28.2% at L1**.
- **Interface design matters more than size here**: model size vs task completion ρ = 0.285 (p = 0.458, not significant); size vs latency ρ = 0.946. Llama3.2 (3.2B) reached overall TC 0.58 vs GPT-OSS (20.9B, 3.6B active) 0.34, and the paper states a 3.2B model at the right granularity beats a 20.9B one at the wrong one.
- **Schema-violation failures depend on the model**: error rate 55.6% for GPT-OSS and 52.8% for xLAM-2 vs 0.0% for Llama3.2 and Hermes3. The authors partly blame aggressive quantization.
- **Limits**: small quantized local models only, mock servers, IoT domains, no fine-tuning, and quantization confounds size effects. The results have not been shown to hold for frontier models or for clients that use progressive tool discovery.

## Relevance to Praxis

- Extends [`mcp-server-design`](../skills/mcp-server-design/SKILL.md). That skill already warns against 1:1 endpoint-to-tool mapping (the L4 end). This paper adds evidence against the other end, the single "do everything" tool with an operation argument.
- Complements brief [`closed-world-tool-hallucination`](closed-world-tool-hallucination.md): larger argument schemas are where small models fail, so schema-level validation matters most at L1/L2.
- Decision heuristic for edge or small-model deployments: group tools by task class (about 4 per server surface) and keep each tool's arguments simple. Re-benchmark granularity per target model (see M7 in the deconfliction report).

> Source: Paschalides et al., "MCP-GRANITE Benchmark: GRANularity Interface TEsting for MCP-Based LLM Agents" (arXiv:2609.24161)
