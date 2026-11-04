# Poisoned Skills: Propagating Jailbreaks Through Agent Markdown Files

> **Source**: [arXiv:2610.37738](https://arxiv.org/abs/2610.37738) — *Poisoned Skills: Propagating Jailbreaks Through Agent Markdown Files* (Manjusha & Emani, published 2026-10-27)  
> **Praxis ID**: `src:2610-37738`  
> **Tier**: Research Brief (Defensive Skill-Loading & Provenance Hardening)

## Summary

Modern coding and workflow agents routinely ingest external Markdown skill files (`SKILL.md`, `AGENTS.md`, `CLAUDE.md`) directly into their system prompt context at startup. Manjusha and Emani evaluate what happens when a corrupted or poisoned Markdown skill file containing persona-override framing is loaded into a LangChain agent across `7` open-weight models and `270` forbidden questions (`9` harm categories $\times$ `30` questions). While all `7` models refuse nearly all forbidden queries under a clean system prompt (`0.5%` mean Attack Success Rate, range `0.0%`–`1.5%`), loading a poisoned Markdown skill file drives mean ASR up ~`90×` to **`44.8%`** (range `13.7%` on `glm-5.3-flash` to `68.9%` on `gemma-4-26b-a4b-it`). Furthermore, obfuscating queries with invisible Unicode zero-width non-joiners (`U+200C`) maintains **`43.4%`** mean ASR with an identical model susceptibility ranking (Spearman $\rho = 1.0$), and phonetic IPA transcription with `snake_case` system instructions still achieves **`30.1%`** mean ASR ($\rho = 0.86$). The `5×` (`55.2` percentage-point) spread across models demonstrates that resistance to skill-file poisoning is a persistent, rank-stable property of the underlying base model's instruction-hierarchy alignment.

## Why Not a Skill?

This paper is an empirical vulnerability characterization of Markdown skill ingestion across `7` open-weight models. Per Praxis dual-use policy, offensive prompt-injection and obfuscation payloads are never packaged as reusable skills; instead, the findings are captured here as defensive context and distilled into provenance, sandboxing, and Unicode-normalization rules in `output/rules/skill-system-design.md`.

## Experimental Scope

- **Agent Harness**: Single-turn LangChain (`create_agent`) QA agent loading a Markdown skill file into its system prompt at initialization.
- **Models Evaluated (`7` open-weight models)**: `google/gemma-4-26b-a4b-it`, `inclusionai/ling-3.0-flash-fin`, `mistralai/mistral-small-2603`, `qwen/qwen3.6-35b-a3b`, `meta-llama/llama-4-maverick`, `microsoft/phi-4`, and `z-ai/glm-5.3-flash`.
- **Dataset**: `270` forbidden questions per model per condition (`30` questions across `9` policy categories: *Economic Harm*, *Government Decision*, *Hate Speech*, *Health Consultation*, *Illegal Activity*, *Legal Opinion*, *Malware*, *Physical Harm*, *Privacy Violence*; Shen et al., 2024).
- **Conditions (`4` arms, `7,560` total evaluations)**:
  1. *Plain base (control)*: `"You are a helpful assistant."` + plain questions.
  2. *Baseline*: Poisoned Markdown skill file (persona manipulation + conflicting base persona + GPTFuzzer mutation) + plain questions.
  3. *Stealth payload*: Poisoned Markdown skill file + spaces in user questions replaced with invisible `U+200C` zero-width non-joiners.
  4. *Phonetic payload*: `snake_case` system prompt + user questions transcribed into stress-marked IPA via Misaki G2P (`espeak-ng` fallback).
- **Judge**: `Llama-Guard-4-12B` scoring substantive harmful compliance vs refusal/deflection.

## Key Quantitative Findings

| Model | Plain Base (Control) | Baseline (Poisoned `SKILL.md`) | Stealth (`U+200C` Zero-Width) | Phonetic (`snake_case` + IPA) | Baseline $\to$ Phonetic Shift |
|:------|:---------------------|:-------------------------------|:------------------------------|:------------------------------|:------------------------------|
| `google/gemma-4-26b-a4b-it` | `0 / 270` (**0.0%**) | `186 / 270` (**68.9%**) | `188 / 270` (**69.6%**) | `187 / 270` (**69.3%**) | `+0.4 pp` |
| `inclusionai/ling-3.0-flash` | `2 / 270` (**0.7%**) | `182 / 270` (**67.4%**) | `171 / 270` (**63.3%**) | `157 / 270` (**58.1%**) | `-9.3 pp` |
| `mistralai/mistral-small-2603` | `4 / 270` (**1.5%**) | `160 / 270` (**59.3%**) | `168 / 270` (**62.2%**) | `99 / 270` (**36.7%**) | `-22.6 pp` |
| `qwen/qwen3.6-35b-a3b` | `0 / 270` (**0.0%**) | `134 / 270` (**49.6%**) | `125 / 270` (**46.3%**) | `93 / 270` (**34.4%**) | `-15.2 pp` |
| `meta-llama/llama-4-maverick` | `0 / 270` (**0.0%**) | `86 / 270` (**31.9%**) | `65 / 270` (**24.1%**) | `1 / 270` (**0.4%**) | `-31.5 pp` |
| `microsoft/phi-4` | `0 / 270` (**0.0%**) | `61 / 270` (**22.6%**) | `60 / 270` (**22.2%**) | `4 / 270` (**1.5%**) | `-21.1 pp` |
| `z-ai/glm-5.3-flash` | `3 / 270` (**1.1%**) | `37 / 270` (**13.7%**) | `43 / 270` (**15.9%**) | `27 / 270` (**10.0%**) | `-3.7 pp` |
| **7-Model Mean** | **0.5%** | **44.8%** (`55.2 pp` spread) | **43.4%** ($\rho = 1.0$) | **30.1%** ($\rho = 0.86$, `69 pp` spread) | `-14.7 pp` |

## Defensive Takeaways for Agent Systems

1. **Treat `SKILL.md` and `AGENTS.md` files as untrusted data, never root system instructions**: Concatenating external Markdown skill files directly into the root system prompt grants them highest-privilege instruction authority, jumping mean jailbreak ASR from `0.5%` to `44.8%` (`68.9%` on `gemma-4-26b-a4b-it`). Isolate skill files in a lower-privilege delimiter block subordinate to immutable core safety rules.
2. **Strip zero-width Unicode characters (`U+200B`–`U+200D`, `U+FEFF`) before tokenization**: Replacing spaces with `U+200C` bypasses naive keyword filters while preserving `43.4%` mean ASR (`69.6%` on `gemma-4-26b-a4b-it`) and `1.0` Spearman rank correlation with plain-text attacks.
3. **Benchmark base-model instruction-hierarchy resilience under poisoned skill contexts**: Standard refusal benchmarks (`0.0%`–`1.5%` control ASR across all 7 models) completely hide a `5×` (`13.7%` vs `68.9%`) divergence in susceptibility once a poisoned skill file is loaded.
