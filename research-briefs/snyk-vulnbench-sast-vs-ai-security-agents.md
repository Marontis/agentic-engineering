# Deterministic SAST vs. AI Security Agents in Snyk VulnBench 2.0

> **Source**: [arXiv:2610.38617](https://arxiv.org/abs/2610.38617) — *How Deterministic SAST and AI Security Agents Divide the Work: Coverage, Harness Policy and Cost in Snyk VulnBench 2.0* (Tal et al., published 2026-10-28)  
> **Praxis ID**: `src:2610-38617`  
> **Tier**: Research Brief
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

Tal et al. introduce **Snyk VulnBench 2.0**, a full-repository benchmark of `20` open-source web applications across Go (`6` apps, `32` vulns), JS/TS (`7` apps, `30` vulns), Python (`5` apps, `34` vulns), and Java (`2` apps, `12` vulns) containing `108` hand-curated, attacker-reachable vulnerabilities (`62` cross-file, `46` same-file; `447` authored taint-flow locations). Evaluating `9` productized configurations (`180` main runs plus `3` supplementary control arms), they find that deterministic SAST (`Snyk Code`, `82.4%` macro recall, `89/108`) and the top AI security agent (`Claude Code /security-review` with `Opus 5 xhigh`, `79.3%` macro recall, `85/108`) are statistically tied overall (McNemar $p = 0.57$) but structurally complementary: `Snyk Code` uniquely finds `16` of their `28` disagreements (excelling at same-file taint, open redirects `11/11`, prototype pollution `6/6`, and path traversal `16/16` in `8` minutes total), while `Opus 5 xhigh` uniquely finds `12` (excelling at cross-file flows `53/62` vs `49/62`, IDOR/mass-assignment authorization flaws `2`–`3/3` vs `0/3`, and `7` live-reproduced zero-day vulnerabilities across third-party libraries and server-to-browser DOM boundaries missed by both `Snyk Code` and the human reference set). Together, the single pair `Snyk Code + Opus 5 xhigh` reaches **`101/108`** (`102/108` after a reference fix)—matching the exact union ceiling of all `7` endpoint-aware tools combined.

## Why Not a Skill?

This paper is an empirical benchmark and diagnostic study of commercial and open-source security scanners (`Snyk Code`, `Claude Code`, `Codex Security`, `DeepSec`) rather than a single algorithmic procedure. Its findings directly inform engineering rules for combining SAST with AI security agents and eliminating agent harness bottlenecks.

## Experimental Scope

- **Benchmark**: `20` web repositories, `108` attacker-reachable vulnerabilities (`62` cross-file, `46` same-file) across `14` CWE classes (XSS `19`, path traversal `16`, command injection `13`, SQLi `13`, etc.).
- **Primary Scoring**: One-to-one Hungarian matching requiring vulnerability class match plus source and sink line accuracy within **$\pm 2$ lines** (`DeepSec` scored separately under localized recall because it omits source/sink role labels).
- **Evaluated Systems**: `Snyk Code 1.1305.1`; `Claude Code 2.1.251 /security-review` (`Opus 5 xhigh`, `Opus 5 medium + Snyk MCP 1.1307.0`, `Sonnet 5 xhigh`); `Codex Security 0.1.24` (`GPT-5.6 Luna`, `Terra`, `Sol` at `xhigh`); `DeepSec 2.3.7` (`Opus 5 xhigh`, `GPT-5.6 Sol xhigh`); plus three supplementary arms (`Opus 5 medium` without MCP, `Opus 5 xhigh` with neutral default audit prompt on `19` apps / `105` vulns, and `3` deterministic SAST repeats).

## Key Quantitative Findings

### 1. Main Configuration Performance (`108` Reference Vulnerabilities)

| Configuration | Macro Recall (95% CI) | Pooled Match (`/108`) | Exact Line (`/108`) | Micro Precision (Scored Classes) | Findings / Matched Vuln | Total Cost (`$` / Matched) | Total Time (`s` / Matched) |
|:--------------|:----------------------|:----------------------|:--------------------|:---------------------------------|:------------------------|:---------------------------|:---------------------------|
| `Snyk Code 1.1305.1` | **82.4%** (`74.0–90.5%`) | **89** | **85** | `20.9%` (`89/425`; **69%** `89/129` in 14 classes) | `4.78` | Deterministic CLI | **8 min** (`5 s`) |
| `Claude Code /security-review` (`Opus 5 xhigh`) | **79.3%** (`71.6–86.7%`) | **85** | **79** | **74.6%** (`85/114`; **81%** `85/105` in 14 classes) | `1.34` | `\$224.27` (`\$2.64`) | `4.2 h` (`177 s`) |
| `Claude Code /security-review` (`Opus 5 med + Snyk MCP`) | **75.2%** (`68.2–82.3%`) | **80** | **74** | **82.5%** (`80/97`) | **1.21** | `\$57.44` (`\$0.72`) | **2.4 h** (`107 s`) |
| `Claude Code /security-review` (`Sonnet 5 xhigh`) | **67.0%** (`57.7–76.2%`) | **73** | **55** | **74.5%** (`73/98`) | `1.34` | `\$39.17` (`\$0.54`) | `3.0 h` (`148 s`) |
| `Codex Security` (`GPT-5.6 Luna xhigh`) | **41.2%** (`26.6–56.5%`) | **45** | `15` | `20.8%` (`45/216`) | `4.80` | `\$21.29` (**\$0.47**) | `3.4 h` (`272 s`) |
| `Codex Security` (`GPT-5.6 Terra xhigh`) | **30.1%** (`19.1–41.9%`) | **35** | `6` | `15.8%` (`35/221`) | `6.31` | `\$46.18` (`\$1.32`) | `4.5 h` (`463 s`) |
| `Codex Security` (`GPT-5.6 Sol xhigh`) | **29.2%** (`18.1–41.1%`) | **34** | `2` | `12.7%` (`34/267`) | `7.85` | `\$745.36` (`\$21.92`) | `8.9 h` (`942 s`) |
| `DeepSec 2.3.7` (`Opus 5 xhigh`, localized) | **37.5%** (`22.6–53.2%`) | **37** | — | `7.1%` (`37/524`) | `14.16` | `\$370.93` (`\$10.03`) | `17.8 h` |
| `DeepSec 2.3.7` (`GPT-5.6 Sol xhigh`, localized) | **2.5%** (`0.0–7.5%`) | **1** | — | `10.0%` (`1/10`; `0` findings in `16/20` runs) | `10.00` | — | Median `4` turns |

### 2. Three Harness Bottlenecks That Dominate Raw Model Capability

1. **Built-In Prompt Policy Suppression (`Claude Code /security-review`, Arm B)**:
   - `/security-review`'s built-in prompt suppresses ReDoS/DoS and requires "extremely high confidence" for open redirect and prototype pollution. On those `20` restricted vulnerabilities, `Opus 5 xhigh` matched only **`9/20`** (`0/3` ReDoS, `5/11` open redirect, `4/6` prototype pollution) vs `Snyk Code`'s **`18/20`**, whereas on the `81` unrestricted non-React/Angular vulnerabilities `Opus 5 xhigh` beat `Snyk Code` **`71/81` vs `67/81`**.
   - Replacing `/security-review` with the neutral default audit prompt (Arm B, `19` apps / `105` vulns) caused the exact same `Opus 5 xhigh` model to jump from **`9/20` to `16/20`** on the restricted classes (McNemar $p = 0.016$) and from **`83/105` to `93/105` overall** (surpassing `Snyk Code`'s `87/105`, with a `98/105` pair union) at **`0.63×` cost, `0.52×` wall time, and `0.84×` tokens** while maintaining precision (`73.2%` vs `74.8%`).
2. **Function-Header Sink Anchoring Offset (`Codex Security`)**:
   - `Codex Security` with `GPT-5.6 Sol` identified **`80/108` vulnerabilities at the file level** (`88/108` by class), but collapsed to **`34/108` at $\pm 2$ lines** (`2/108` exact line) because it anchored sinks on enclosing function or route headers a **median of `6` lines above** the actual sink statement (`39/41` non-source offsets were above the sink). Widening line tolerance from $\pm 2$ to $\pm 10$ lines recovered **`+37` matches for `Sol`**, **`+28` for `Terra`**, and **`+16` for `Luna`**.
3. **Model-Free File Pre-Filter Ceiling (`DeepSec`)**:
   - `DeepSec`'s heuristic pre-scan queued a flow file for only **`56/108`** vulnerabilities (`44/107` sink files: Java `12/12`, JS/TS `23/30`, Go `11/32`, Python `10/34`), capping maximum possible recall at `52%` before the LLM ever ran (`Opus 5` matched `37/56 = 66%` of queued flows).
4. **Equal-Effort MCP Grounding Control (Arm A)**:
   - Running `Opus 5 medium` *without* Snyk MCP matched **`81/108` (`75.6%`)** vs **`80/108` (`75.2%`)** *with* Snyk MCP, proving that reasoning effort (`xhigh` `85` vs `medium` `81`), not MCP grounding, drove the recall gain—though Snyk MCP cut cost by **`27.8%`** (`\$57.44` vs `\$79.60`), wall time by **`14.3%`** (`2.4 h` vs `2.8 h`), tokens by **`40.3%`** (`27.8M` vs `46.6M`), and false-positive review volume from `24` to `17` unmatched findings.
