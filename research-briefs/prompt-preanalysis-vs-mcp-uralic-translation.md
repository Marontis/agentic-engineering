# Prompt Pre-Analysis vs. Live MCP Tool Calling: Deterministic Linguistic Tools Across 31 Open-Weight LLMs

> **Source**: [arXiv:2611.19439](https://arxiv.org/abs/2611.19439) — Iaroslav Chelombitko, Mika Hämäläinen (*Do Rule-Based Tools Help LLMs Translate Endangered Uralic Languages in the Prompt or over MCP?*, Metropolia University of Applied Sciences & Neapolis University Paphos, Nov 2026)
> **Praxis Source ID**: `src:2611-19439v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is a `62,920`-record empirical evaluation comparing deterministic pre-execution prompt injection (`inject`) against live Model Context Protocol (`MCP`) tool calling (`mcp`, `mcp_coarse`, `mcp_rich`) across `31` open-weight instruction-tuned models (`0.6B–27.8B`) on low-resource Uralic machine translation (`68` 6-way parallel literary sentences; `816` expert-linguist adequacy and error-taxonomy judgments on `Qwen3.8-27B`). Rather than introducing a new multi-step agent procedure, it establishes sharp empirical failure boundaries for exposing deterministic lookup/analyzer tools over `MCP` to open-weight models—informing tool-delivery and schema-design rules in [`rules/skill-system-design.md`](../rules/skill-system-design.md).

---

## Experimental Design (`§3–§4`, `Appendices A–F`)

Using deterministic finite-state morphological analyzers, constraint grammars, inflectors, and bilingual dictionaries from `GiellaLT` / `UralicNLP` (which parse **`91.1%`** of `Udmurt` word tokens and **`95.4%–98.5%`** of `Komi-Zyrian` [`kpv`], `Moksha` [`mdf`], `Erzya` [`myv`], and `Finnish` tokens, ruling out parser coverage failures), the study evaluates **`7` controlled conditions** (`Table 1`, `bf16`, greedy decoding, `32,768` context, `vLLM`):

1. **`zeroshot`**: Translation instruction + source sentence only.
2. **`mcp_prompt` (control)**: Adds the `mcp` tool-use system prompt (*"your own knowledge ... may be unreliable"* + 3-step workflow) **without** attaching tool schemas, isolating prompt-framing overhead from tool calling.
3. **`inject` (`6`-tool surface) & `inject_rich` (`13`-tool surface)**: Pre-computes every source word's lemma, morphological reading, and dictionary gloss deterministically and appends them directly to the user message—requiring zero tool-call generation from the LLM.
4. **`mcp` (`6` per-word tools), `mcp_coarse` (`1` whole-sentence tool), & `mcp_rich` (`13` tools adding sentence glossing, ISO language-code resolution, and inflected-form dictionary search)**: Attaches live `UralicMCP` tool schemas so the model decides when and what to look up (`10` models `0.6B–27.8B` across all bidirectional pairs; `21` additional models on `kpv`, including `4` function-calling specialists; `62,920` released run records).

---

## Key Quantitative Findings (`§5–§6`, `Appendices A–G`)

### 1. Expert Adequacy & Error Shift on the Sole Reliable Open-Weight Caller (`Qwen3.8-27B`, `Tables 2–3`, `816` Judgments)

| Source Language ($\to$ English, $68$ sents each) | English Gloss Coverage (`inject`) | `zeroshot` Accepted (`Wholesale Repl.`) | `inject` Accepted (`Wholesale Repl.`) | `mcp` Accepted (`Wholesale Repl.`) |
|:-------------------------------------------------|:---------------------------------:|:---------------------------------------:|:-------------------------------------:|:----------------------------------:|
| **`Komi-Zyrian` (`kpv`)** | `80.3%` | `8 / 68` (`11.8%`; `39` repl.) | `17 / 68` (`25.0%`; `10` repl.) | **`23 / 68` (`33.8%`; `9` repl.)** |
| **`Moksha` (`mdf`)** | `73.9%` | `1 / 68` (`1.5%`; `48` repl.) | **`11 / 68` (`16.2%`; `21` repl.)** | **`11 / 68` (`16.2%`; `26` repl.)** |
| **`Erzya` (`myv`)** | `78.5%` | `0 / 68` (`0.0%`; `54` repl.) | **`11 / 68` (`16.2%`; `24` repl.)** | **`11 / 68` (`16.2%`; `25` repl.)** |
| **`Udmurt` (`udm`, no English dict side)** | **`0.0%`** (lemmas + tags only) | `4 / 68` (`5.9%`; `42` repl.) | `4 / 68` (`5.9%`; `41` repl.) | **`10 / 68` (`14.7%`; `23` repl.)** |
| **Total (`272` sentences / condition)** | — | **`13 / 272` (`4.8%`)** | **`43 / 272` (`15.8%`)** | **`55 / 272` (`20.2%`)** |

*Note*: Condition-level `chrF++` correlated with expert acceptance at Pearson $r = 0.98$ and Spearman $\rho = 0.90$ (`Table 6`). Where English dictionary glosses reached `73.9%–80.3%` of tokens, `inject` slashed hallucinated `Wholesale replacement` errors (`39/48/54 -> 10/21/24`), shifting residual errors to local `Lexical substitution` (`10/6/9 -> 16/12/11`) and `Participant/referent` errors (`3/2/1 -> 9/8/10`). Where the dictionary lacked an English target side (`Udmurt`, `0%` glosses), morphological tags and lemmas alone gave **zero `inject` gain** (`4 -> 4`).

### 2. Why Live `MCP` Fails Across the `31`-Model Open-Weight Roster while `inject` Succeeds Universally (`§6`, `Tables 4–5, 7–9`)

- **`45.2%` (`14/31`) of open-weight models never emit a single MCP tool call (`57.6%` silent records overall, `Table 4 & Table 7`)**:
  - `9/31` models fail all three capability probes (`direct call instruction`, `exhaustive vLLM tool-call parser search`, and `full sweep`), including **every `Gemma-3` checkpoint (`1B`, `4B`, `12B`, `27B` = `0%`)**, `EuroLLM-1.7B/9B`, `OLMo-2-7B`, `c4ai-command-r7b`, and `watt-tool-8B`—whereas `Qwen3` calls at `96%–100%` from `1.7B` (`97%`) and `4B` (`96%`) to `27.8B` (`100%`, `8B` at `46%`), and `Mistral-7B-v0.3` (`0%`) vs `Ministral-8B` (`100%`) shows **family post-training—not model parameter count—governs tool use** (further noting `vLLM` parser mismatches silently yield `0` calls unless matched per model, e.g., `qwen3_xml` / `llama3_json`, and `bf16` call rates are optimistic relative to `4-bit`/`8-bit` deployments).
  - `2/31` (`Hammer2.1-1.5b`, `Hammer2.1-3b`) emit malformed call syntax unreadable by any `vLLM` parser, and `3/31` (`Qwen3-0.6B`, `Mistral-7B-v0.3`, `Phi-4-mini` on main splits) pass isolated probes but stay silent zero-shot.
- **Function-calling specialists fail prose synthesis**: `Hammer2.1-3b` and `xLAM-2-1b-fc-r` emit raw tool-call syntax as their final user answer—leaving **no prose translation in `42.4%` and `17.2%` of outputs** (vs `4.3%` for general instruction models, `§6`).
- **`57.5%` of live MCP calls pass wrong or unsupported ISO language codes (`315,910` calls, `Table 8`)**: Only **`42.5%`** (`11.5%–74.5%` per model; even `Qwen3.8-27B` sent `23.5%` unsupported codes) matched the source language's toolkit code (`kpv`, `mdf`, `myv`, `udm`); **`49.1%`** named an unsupported code (`en` sent `74,449` times; guessing `kv`, `kom`, `komi-zyrian`, `kz`, `kmz`, `kmm` before `kpv`) and **`8.4%`** named a supported *wrong* language (`26,630` calls sent `koi` Komi-Permyak on Komi-Zyrian text), causing **`52.4%` of all MCP calls to return empty results**.
- **`inject` wins across `10/10` models, whereas `mcp` and `mcp_prompt` degrade smaller callers (`Appendix A`, `Tables 5 & 11`)**:
  - Pre-computed `inject` improved `chrF++` on **`10 of 10` models** in `kpv`, `mdf`, and `myv` (`+1.2` to `+8.4` pts; mean `+5.5`, `+4.7`, `+4.9` pts; paired bootstrap significant in **`25/30` cells with `0` significant losses**).
  - Under live `mcp` on `kpv -> eng`, **3 of the 4 reliable callers degraded** (`Qwen3-4B` `-11.8` pts [`17.4 -> 5.7`], `Mistral-Nemo-12B` `-3.2` pts, `Llama-3.1-8B` `-0.4` pts; `10`-model mean `-1.3` to `-2.2` pts), and the `mcp_prompt` control *without* tools cost **`-1.4` to `-4.3` `chrF++`** into English (`98.1% -> 89.3%` well-formed).
  - Collapsing `6` per-word tools into `1` coarse sentence tool (`mcp_coarse`) yielded **`0.0` median change** (`30` cells up, `29` down), whereas adding server-side ISO code resolution and inflected-form lookup (`mcp_rich`) lifted reliable callers by **`+7.0` `chrF++`** across `4` cells.
- **Target-generation ceiling (`English -> Uralic`, `Tables 5, 9, 12`)**: Every condition failed (`2.0–5.4` `chrF++`, below the `9.3–10.8` random-sentence floor; `mcp` dropped well-formed target text from `72.0%` to `42.5%` with `22.9%` wrong-language and `13.1%` zero-shot / `9.2%` `mcp` repetition loops), proving analyzer/dictionary tools cannot substitute for an absent target-language generation prior.

---

## Relevance to Praxis

- **Rules**: [`rules/skill-system-design.md`](../rules/skill-system-design.md) — establishes when deterministic pre-analysis prompt injection beats live `MCP` tool calling on `<= 27B` open-weight models, mandates server-side alias/context binding instead of free-text ISO/code arguments, and requires `mcp_prompt` no-tool controls in MCP evaluations.
- **Related Artifacts**: [`mcp-server-design`](../skills/mcp-server-design/SKILL.md), [`decoupled-interface-action-repair`](../skills/decoupled-interface-action-repair/SKILL.md), [`mcp-granite-tool-granularity`](mcp-granite-tool-granularity.md), and [`mcp-hallucination-boundary-guards`](../skills/mcp-hallucination-boundary-guards/SKILL.md).
