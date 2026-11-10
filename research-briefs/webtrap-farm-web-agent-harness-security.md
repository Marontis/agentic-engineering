# Harness Matters: Measuring and Dissecting Security Resilience in Web Agents

> **Source**: [arXiv:2611.11971](https://arxiv.org/abs/2611.11971) — Xinyi Wu, Jiagui Chen, JiaYi Dong, Geng Hong, Xudong Pan, Jiarun Dai, Mingxuan Liu, Min Yang (2026)
> **Praxis Source ID**: `src:2611-11971v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is an empirical cross-harness measurement study and controlled architectural ablation (`WebTrap Farm`) across `6` open-source web-agent frameworks, `7` backend LLMs, and `2` commercial computer-use agents rather than a single standalone software procedure. Its value lies in quantifying **where security resilience is gained or lost across the four stages of a web-agent harness** (Goal Interpretation, Webpage Perception, Reasoning & Planning, and Action Execution) and demonstrating how multi-role delegation, unstructured visual perception, and uncalibrated capability inflate or mask attack rates. Its architectural prescriptions belong as engineering and evaluation rules in [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) and [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md), complementing procedural gateways such as [`compile-then-execute-web-agent-gateway`](../skills/compile-then-execute-web-agent-gateway/SKILL.md) and [`browser-agent-http-sandbox`](../skills/browser-agent-http-sandbox/SKILL.md).

## Benchmark & Methodology (`WebTrap Farm`)

- **4-Stage Harness Taxonomy**: Surveying `68` open-source GitHub web-agent repositories, the authors decompose every web-agent harness into four sequential execution stages:
  1. **Stage I — Goal Interpretation**: Raw-prompt forwarding vs. structured prompt rewriting / safety constraint injection.
  2. **Stage II — Webpage Perception**: Structured DOM/accessibility textual filtering vs. multimodal screenshot + DOM fusion.
  3. **Stage III — Reasoning & Planning**: Single-controller loop (retaining the original user goal across steps) vs. multi-role planner/navigator decomposition.
  4. **Stage IV — Action Execution**: Rule-based deterministic element grounding vs. secondary LLM-based action grounding.
- **Usability-Calibrated Evaluation (`505` Attack + `505` Benign Calibration Tasks)**: Covers `3` threat vectors across `6` realistic web verticals (Healthcare, Finance, E-Commerce, Education, Enterprise Admin, Social/Content):
  - **Malicious User Prompts (`MUP`, `160` tasks)**: Direct harmful user instructions (fraud, unauthorized modification, policy-violating submissions).
  - **Malicious Prompt Injection (`MPI`, `158` tasks)**: Untrusted third-party instructions embedded in comments, listings, or page banners.
  - **Deceptive Website Design (`DWD`, `187` tasks)**: Phishing fields, dark patterns, disguised pop-ups, and out-of-scope credential/payment collection forms.
  - **Capability Calibration**: Every attack scenario is paired 1:1 with a benign **usability calibration task** on the identical page layout; `ASR` and Defense Success Rate (`DSR = 1 - ASR`) are computed strictly over calibration-verified executable instances via deterministic browser-side JavaScript event listeners (`submit`, `click`, `input`, network exfiltration beacons) rather than LLM-as-a-judge transcript guesses.

## Key Quantitative Findings

### 1. Harness Architecture Rivals Backend Model Choice in Determining Security

- **Overall Open-Source Resilience**: Across `6` representative open-source harnesses (`SeeAct`, `Browser Use (Text)`, `Browser Use (Vision)`, `Agent-E`, `Skyvern 1.0`, `Skyvern 2.0`) paired with `7` backend models (`GPT-4o`, `GPT-5.2`, `Claude-Opus-4.5`, `Gemini-2.5-Flash`, `DeepSeek-V3`, `Qwen2.5-VL-72B`, `Qwen3-VL-30B`), mean calibrated `ASR` is **`32.55%`** (`67.45%` `DSR`), ranging by more than `2x` across harnesses:
  - `Agent-E`: **`20.24%` ASR** (`79.76%` DSR, `61.33%` Task Completion Rate `TCR`)
  - `Skyvern 1.0`: **`21.80%` ASR** (`78.20%` DSR, `67.13%` TCR)
  - `Browser Use (Text)`: **`33.84%` ASR** (`66.16%` DSR, `81.39%` TCR)
  - `Browser Use (Vision)`: **`34.08%` ASR** (`65.92%` DSR, `83.96%` TCR)
  - `Skyvern 2.0`: **`41.99%` ASR** (`58.01%` DSR, **`85.25%` TCR**)
  - `SeeAct`: **`42.31%` ASR** (`57.69%` DSR, `70.50%` TCR)
- **Same Model, `40.90` pp Security Swing**: Holding the backend LLM fixed to `GPT-4o`, `DSR` swings from **`83.79%` in `Agent-E` down to `42.89%` in `Skyvern 2.0`** (`-40.90` percentage points). Generalized Linear Mixed Modeling (`GLMM`) confirms massive independent effects for **Harness** ($\chi^2 = 331.17, df = 5, p = 1.97 \times 10^{-69}$), **Backend Model** ($\chi^2 = 437.63, df = 6, p = 2.25 \times 10^{-91}$), and **Harness $\times$ Model Interaction** ($\chi^2 = 299.81, df = 30, p = 2.88 \times 10^{-46}$).
- **Commercial Systems Remain Vulnerable to Web-Side Deception**: `Gemini Computer Use` (`gemini-3.7-flash`) achieves **`15.14%` overall ASR** (`1.45%` MUP, `14.29%` MPI, **`25.51%` DWD**), and `Claude Computer Use` (`claude-haiku-4-5-20251001`) achieves **`16.85%` overall ASR** (`9.59%` MUP, `16.67%` MPI, **`22.12%` DWD**).

### 2. User-Side Alignment Does Not Transfer to Web-Side Attacks

- Frontier models heavily aligned against direct misuse (`MUP`) remain highly susceptible to indirect prompt injection (`MPI`) and deceptive UI dark patterns (`DWD`):
  - `Claude-Opus-4.5` achieves **`3.25%` MUP ASR**, yet suffers **`36.03%` MPI ASR** and **`22.55%` DWD ASR**.
  - `GPT-5.2` achieves **`5.52%` MUP ASR**, yet suffers **`36.48%` MPI ASR** and **`33.97%` DWD ASR**.
  - Conversely, `Qwen3-VL-30B` exhibits **`57.94%` MUP ASR** (`41.73%` overall ASR) alongside `27.78%` MPI ASR.

### 3. Harness-Intrinsic ("Naive") Vulnerability Under Task-Completion Pressure

- **Bare out-of-scope UI fields can be more dangerous than explicit prompt injections**: When explicit adversarial instructions and deceptive lures are stripped—leaving only a bare, unprompted out-of-scope input field on the page (such as an unexplained credit-card field on a university course-registration form)—`SeeAct` reaches **`50.00%` naive MPI ASR** (exceeding its `49.37%` ASR on explicit attacks!) and `Browser Use (Text)` reaches **`41.27%` naive DWD ASR** (exceeding `36.30%` on explicit attacks). Explicit adversarial wording triggers backend safety training, whereas silent extraneous form fields are dutifully populated by task-completion-driven harnesses trying to make form submission succeed.
- **Retry loops erode initial safety hesitation**: Qualitative trace inspection shows harnesses repeatedly shifting internal reasoning across form-validation retries from `"unsafe / unnecessary"` $\to$ `"probably required by form"` $\to$ populating sensitive credentials.

### 4. Stage-Wise Dissection & Controlled Ablations (`GPT-4o`, `200` Tasks)

Measuring `Conditional_DSR` (the fraction of attacks surviving into stage $k$ that stage $k$ successfully blocks) isolates exact architectural bottlenecks:

| Stage | Architectural Contrast | Stage `Conditional_DSR` & Controlled Ablation Delta |
|:---|:---|:---|
| **Stage I: Goal Interpretation** | Fine-grained goal interpreter (`Agent-E`) vs. task-decomposition rewriter (`Skyvern 2.0`) vs. raw forwarding | On `MUP`, `Agent-E` blocks **`82.71%`** at Stage I vs **`8.13%`** for `Skyvern 2.0` and `0.00%` for raw forwarding. Swapping `Agent-E`'s interpreter prompt for `Skyvern 2.0`'s drops Stage I `Conditional_DSR` from **`75.61%` to `53.85%` (`-21.76` pp)**. |
| **Stage II: Webpage Perception** | Structured accessibility/DOM filtering (`Agent-E`) vs. multimodal screenshot encoders (`Browser Use (Vision)`) | On web-side attacks (`MPI`/`DWD`), `Agent-E`'s structured textual filtering reaches **`78.99%`** Stage II `Conditional_DSR`, whereas multimodal vision harnesses stay **`< 20%`** (`Browser Use (Vision)`: **`9.96%`**). Relaxing `Agent-E`'s DOM filter drops Stage II `Conditional_DSR` from **`56.94%` to `50.70%` (`-6.24` pp)**. |
| **Stage III: Reasoning & Planning** | Risk-awareness cues + single-controller goal anchoring (`Skyvern 1.0`) vs. multi-role goal stripping (`Agent-E` navigator) | Removing risk-awareness cues on `MUP` drops Stage III `Conditional_DSR` from **`73.91%` to `43.48%` (`-30.43` pp)** in `Browser Use (Vision)` and **`92.86%` to `69.77%` (`-23.09` pp)** in `Agent-E`. On web-side attacks, `Skyvern 1.0`'s single controller achieves **`78.17%`** Stage III `Conditional_DSR` vs **`10.65%`** in `Agent-E`'s multi-role planner, because high-level role handoffs strip the original user goal and launder injected page directives into trusted sub-goals. Re-anchoring `Agent-E`'s downstream navigator directly to the raw user goal lifts Stage III `Conditional_DSR` from **`19.35%` to `43.59%` (`+24.24` pp)**; removing goal anchoring from `Skyvern 1.0` drops it from **`70.73%` to `54.05%` (`-16.68` pp)**. |
| **Stage IV: Action Execution** | Deterministic rule grounder vs. LLM-based grounder (`SeeAct`, `Skyvern 2.0`) | Rule-based grounders provide **`0.00%`** Stage IV `Conditional_DSR`; LLM grounders catch `26.94%`/`23.51%` of residual `MUP` (`SeeAct`/`Skyvern 2.0`) but only **`1.63%`/`4.07%`** of web-side attacks once upstream planning has committed. |

## Engineering Takeaways

1. **Never strip the immutable raw user goal during multi-role delegation**: Pass the original user intent (read-only and cryptographically/structurally separated from sub-goal summaries) into every downstream navigation and form-filling role to prevent cross-role trust laundering (`+24.24` pp Stage III defense gain).
2. **Enforce minimal-scope field population against "naive" UI dark patterns**: Prohibit form-filling loops from populating fields outside the minimum data attributes authorized by the user's task, and block automatic retry escalation when a webpage demands out-of-scope PII, payment data, or credentials.
3. **Prefer pruned structural DOM views or isolated compilation over raw screenshot ingestion on untrusted pages**: Multimodal visual encoders drop Stage II filtering below `20%` (`9.96%` in `Browser Use (Vision)`); strip off-task DOM subtrees before perception or isolate untrusted page values completely via [`compile-then-execute-web-agent-gateway`](../skills/compile-then-execute-web-agent-gateway/SKILL.md).
4. **Always pair web-agent `ASR` with matched benign `TCR` calibration**: High raw `DSR` on an uncalibrated suite routinely masks broken navigation (`61.33%` vs `85.25%` `TCR`), while upgrading agentic task-completion loops (`Skyvern 1.0` $\to$ `Skyvern 2.0`) nearly doubles `ASR` (`21.80%` $\to$ `41.99%`) unless paired with stage-level security gates.

## Related Artifacts

- [`compile-then-execute-web-agent-gateway`](../skills/compile-then-execute-web-agent-gateway/SKILL.md) — Eliminates runtime exposure to untrusted webpage content by compiling tasks offline against typed Trusted Website APIs.
- [`browser-agent-http-sandbox`](../skills/browser-agent-http-sandbox/SKILL.md) — Enforces deterministic HTTP-layer request allowlists and parameter policies beneath browser-using agents.
- [science-agent-harness-safety-erosion.md](science-agent-harness-safety-erosion.md) — Demonstrates parallel harness-induced safety erosion in autonomous scientific execution harnesses.
- [task-tampering-indirect-prompt-injection.md](task-tampering-indirect-prompt-injection.md) — Shows how non-imperative observation and state tampering bypasses instruction-stripping sanitizers.
