# Understanding and Mitigating Role Spoofing in LLMs

> **Source**: [arXiv:2610.40396](https://arxiv.org/abs/2610.40396) — Ezra Edelman, Benjamin Edelman, Surbhi Goel, Eran Malach (University of Pennsylvania, Princeton University, Apple MLR, 2026-10-29)  
> **Praxis ID**: `src:2610-40396`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Core Contribution

Tool-using LLM agents rely on chat templates (role delimiters such as `<|im_start|>user` vs `<|im_start|>tool`) to separate trusted user instructions from untrusted external tool outputs. **Role spoofing** attacks subvert this boundary by formatting text inside a tool output to mimic a new user turn. Across `6` frontier models (`GPT-5.4`, `Claude Opus 4.8`, `Claude Opus 5`, `Claude Sonnet 5`, `Gemini 3 Pro`, `Gemini 3.1 Pro`), role-spoofed injections inside tool outputs succeed at **`63.1%` to `103.6%`** of the rate of genuine user messages on `AgentDojo` and **`72.5%` to `100%`** on a 5-suite tool-use testbed.

Through controlled transformer experiments (`64` seeds) and fine-tuning of `Qwen3.5-27B` and `Gemma 4 31B-IT`, the authors establish three foundational results:
1. **Dual Orthogonal Mechanisms (Content vs. Structure)**: LLMs infer message role from two independent heuristics learned during pretraining and SFT: *content cues* (imperative user-like phrasing) and *structural cues* (special delimiter tokens or chat markers). Adversarial training against one mechanism completely fails to transfer to the other (`0.0%` cross-mechanism accuracy on `Qwen3.5-27B`).
2. **Serialization Escaping Does Not Stop Role Spoofing**: Stripping special tokens at the tokenizer level or JSON-escaping newlines and quotes (`\n`, `\"`) inside tool outputs still leaves `GPT-5.4` and `Claude Opus 5` following spoofed injections at **`82.6%` to `83.6%`** of the real-user baseline.
3. **Random-Token Linear Role Probes Beat Self-Attribution Monitors**: Asking the model in a follow-up turn whether a tool output contained a user message (`Self-Attribution`) is trivially bypassed (`0.0%` detection on `Gemma 4 31B-IT`, `25.0%` on `Qwen3.5-27B`) by appending a one-sentence anti-monitor instruction. In contrast, a **linear probe trained exclusively on uniformly random vocabulary tokens** wrapped in real `user` vs `tool` chat templates detects when internal post-block representations flip toward `user` inside a tool span at **`100.0%` TPR (`0.1%` FPR)** even under adaptive anti-monitor attacks.

---

## Experimental Scope & Methodology

- **Frontier Evaluation**:
  - **Modified `AgentDojo` Workspace**: `>100` random `(user_task, adversarial_task)` pairs per model across `GPT-5.4`, `Claude Opus 4.8`, `Claude Opus 5`, `Claude Sonnet 5`, `Gemini 3 Pro`, and `Gemini 3.1 Pro`, measuring `Injection` success relative to a `Control` where the attacker instruction is sent as a genuine second user turn.
  - **Simple Tool-Use Testbed**: `5` suites (`Accounts`, `Calendar`, `Documents`, `Email`, `Weather`), `24` tasks, `45` tools, `15` environments (`2,208` clean and `10,368` injected runs, `3,420` security-sensitive).
- **Mechanistic & Fine-Tuning Analysis**:
  - `2`-layer and `3`-layer causal Transformers (`64` seeds, $d=128$) showing how `10%` unseparated chat transcripts in pretraining induce shortcut attention to content and local delimiters rather than tracking parity/nesting from the true `<bos>` boundary.
  - `Qwen3.5-27B` LoRA fine-tuning on `Nemotron-SFT-Agentic-v2` (content-only spoofing) vs `Nemotron-CC` (fake special token spoofing).
- **White-Box Role-Belief Probing (`Gemma 4 31B-IT`, `Qwen3.5-27B`)**:
  - Trained logistic regression probes on concatenated post-decoder-block activations across all layers using `86,650` synthetic conversations per seed (`16` seeds) of **uniformly random tokens** (zero semantic content). At inference, a tool output is flagged if the maximum per-token `user`-role probability inside the tool span exceeds a threshold calibrated at `0.1%` FPR.

---

## Key Quantitative Findings

### 1. Frontier Vulnerability to Role Spoofing

| Model | `AgentDojo` Control | `AgentDojo` Injection | Injection / Control Ratio | Simple Testbed Clean Acc | Simple Testbed Injection ASR |
|:------|:-------------------:|:---------------------:|:-------------------------:|:------------------------:|:----------------------------:|
| `GPT-5.4` | `49.8%` | `47.8%` | **`96.2%`** | `>95%` | **`100.0%`** |
| `Claude Opus 4.8` | `34.8%` | `22.0%` | **`63.1%`** | `>95%` | **`100.0%`** |
| `Claude Opus 5` | `28.6%` | `29.7%` | **`103.6%`** | `>95%` | **`100.0%`** |
| `Claude Sonnet 5` | `65.5%` | `43.2%` | **`65.9%`** | `>95%` | **`98.8%`** |
| `Gemini 3 Pro` | `66.6%` | `61.7%` | **`92.6%`** | — | — |
| `Gemini 3.5 Flash` | — | — | — | `>95%` | **`98.5%`** |
| `Gemini 3.1 Pro` | `46.9%` | `45.2%` | **`96.3%`** | `>95%` | **`72.5%`** |

- **JSON Escaping (`Table 2`)**: When tool outputs are formatted as strict JSON with escaped newlines (`\n`) and quotes (`\"`), `GPT-5.4` still yields `47.5%` injection success vs `57.5%` control (`82.6%` ratio), and `Claude Opus 5` yields `27.3%` vs `32.7%` control (`83.6%` ratio).

### 2. Orthogonal Failure Modes Under Adversarial Fine-Tuning (`Table 5`, `Qwen3.5-27B`)

| Model Checkpoint | Clean Attribution | Content-Only Spoofing | Native Fake Special Token | Other Fake Special Token |
|:-----------------|:-----------------:|:---------------------:|:-------------------------:|:------------------------:|
| `Base Qwen3.5-27B` | `100.0%` | `0.0%` | `0.0%` | `0.0%` |
| `Content Fine-Tuned` | `100.0%` | **`100.0%`** | **`0.0%`** | `36.2%` |
| `Structure Fine-Tuned` | `100.0%` | **`0.0%`** | **`100.0%`** | **`100.0%`** |

### 3. Random-Token Linear Role Probe vs. Self-Attribution (`Table 6`, `0.1%` FPR, `1,000` Convs/Condition)

| Evaluation Condition | `Gemma 4 31B-IT` Self-Attribution | `Gemma 4 31B-IT` Role Probe | `Qwen3.5-27B` Self-Attribution | `Qwen3.5-27B` Role Probe |
|:---------------------|:---------------------------------:|:---------------------------:|:------------------------------:|:------------------------:|
| `Clean Tool Output` | `0.0% [0.0, 0.4]` | `0.0% [0.0, 0.4]` | `0.0% [0.0, 0.4]` | `0.0% [0.0, 0.4]` |
| `Role-Spoofing Injection` | `100.0% [99.6, 100.0]` | `100.0% [99.6, 100.0]` | `100.0% [99.6, 100.0]` | `100.0% [99.6, 100.0]` |
| `Injection + Anti-Monitor Prefix` | **`0.0% [0.0, 0.4]`** | **`100.0% [99.6, 100.0]`** | **`25.0% [22.4, 27.8]`** | **`100.0% [99.6, 100.0]`** |

---

## Why Not a Skill?

The paper's primary mitigation (training linear probes on post-block residual activations across all transformer layers using `86,650` random-token conversations) requires white-box hidden-state access to open-weight model internals, while its black-box findings are negative results demonstrating why special-token stripping, JSON escaping, and conversational self-attribution fail. These negative bounds are best enforced as an always-active rule in `output/rules/agent-sandbox-safety.md`.
