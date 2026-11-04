# Refusal Transfer Failure in Tool-Using LLM Agents

> **Paper**: [Behavior Beyond Text: Evaluating Refusal Transfer Failure in LLM Agents](https://arxiv.org/abs/2610.28982) (Gupta et al., Oct 2026)
> **Praxis source**: `src:2610-28982`

## Why Not a Skill?

This paper presents a behavioral benchmark and a mechanistic residual-stream analysis (difference-in-means refusal directions, activation patching, and inference-time activation steering) showing why chat-level refusal alignment fails to transfer to structured tool calling. Importantly, its mechanistic interventions are **negative results for deployment**: patching or steering along the linear refusal direction suppresses unsafe tool calls primarily by collapsing tool calling altogether (wiping out 82–90% of benign tool calls in three of five models). Because the paper characterizes a fundamental representation gap rather than providing a positive runtime remediation procedure, it belongs as a research brief and as quantitative evidence in `rules/agent-sandbox-safety.md` and `rules/agent-evaluation-quality.md`.

---

## Core Concept

Standard LLM safety evaluations test whether a model refuses harmful requests in plain-text chat (`no-tool` mode). Gupta et al. test whether that refusal behavior transfers when the exact same request is presented to the exact same model equipped with domain-relevant tool schemas (`tool-normal` and adversarial `tool-stress` modes).

The authors construct a controlled factorial benchmark of **2,304 prompts** organized as **768 matched triples** (**384 harmful triples** and **384 benign triples**; $4\text{ domains} \times 4\text{ scenarios} \times 3\text{ modes} \times 3\text{ system conditions} \times 2\text{ phrasings} \times 2\text{ harm levels} \times 4\text{ batches}$):
- **4 regulated domains**: Finance, Healthcare, Education, and Legal.
- **4 prompt scenarios**: Direct request, Indirect framing, Justification / roleplay, and Structured workflow framing.
- **3 system-prompt conditions**: Neutral, Safety-reinforced, and Tool-encouraging.
- **20 deterministic `ForbiddenAction` predicates** (5 per domain, implemented as deterministic Python checks over OpenAI-format tool-call arguments):
  1. *Sensitive-data flag* (e.g., `include_phi=True`, `export_ssn=True`)
  2. *Authorization-bypass* (e.g., `approval_ticket="skip_approval"`)
  3. *PII exfiltration* (routing sensitive records to external recipients)
  4. *Intent keyword* (explicitly prohibited action parameters)
  These predicates fire on only **1.4–3.4%** of benign tool-enabled runs, while text refusals are scored by Claude Opus 5 (validated at **97.4%** agreement, Cohen's $\kappa = 0.94$ against Claude Fable 5 on a 538-example stratified audit).

The primary metric is **conditioned refusal-transfer divergence** ($\Delta^{\mathrm{cond}}_m$): among the harmful prompts $\mathcal{T}_R$ that a model *correctly refuses* in `no-tool` chat, what fraction causes the same model to execute a `ForbiddenAction` tool call when tools are attached?

### Key Findings

| Model | Text Refusal Rate (`no-tool`) | Unsafe Tool Call Rate (`tool-normal` / `tool-stress`) | Conditioned Divergence $\Delta^{\mathrm{cond}}$ (`normal` / `stress`) | Refusal-Direction AUC (Predicting Unsafe Call) | Activation-Patching Flip Rate (`via safe call` / `via no call`) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Qwen3-14B** | **75.3%** (0.753) | 54.4% / 67.7% | **51.9%** / **65.7%** | **0.808** | 24% (9% safe / 15% no call) |
| **Mistral-7B-Instruct-v0.3** | **43.5%** (0.435) | 35.4% / 44.8% | **28.7%** / **34.7%** | **0.760** | 20% (6% safe / 13% no call) |
| **Llama-3.1-70B-Instruct** | **76.0%** (0.760) | 28.9% / 28.9% | **22.9%** / **22.9%** | **0.864** | 13% (3% safe / 9% no call) |
| **Gemma 3 27B** (`gemma-3-27b-it`) | **63.3%** (0.633) | 17.2% / 15.1% | **13.2%** / **10.7%** | **0.790** | 90% (3% safe / 87% no call) |
| **Command R 7B** (`c4ai-command-r7b-12-2024`) | **66.7%** (0.667) | 11.2% / 14.1% | **9.8%** / **9.8%** | **0.768** | 34% (6% safe / 29% no call) |

- **10–52% of chat-refused harmful requests trigger forbidden tool calls**: Across all five open-weight models (7B–70B), **9.8% to 51.9%** of harmful requests that the model refuses in plain text are executed as unsafe tool calls under `tool-normal` (**9.8% to 65.7%** under `tool-stress`). Conditional on a model emitting *any* tool call on a harmful prompt, **73% to 100%** of those calls violate a `ForbiddenAction` predicate (Command R 7B's low overall divergence of 9.8% is an artifact of low tool-call propensity — it calls tools on only 11% of harmful and 40% of benign prompts, and **100%** of its harmful tool calls are unsafe).
- **System-prompt safety reinforcement narrows but never closes the gap (Table 2)**: Moving from `Neutral` to `Safety-reinforced` system prompts reduces `tool-normal` divergence (Qwen3-14B: **0.63 $\to$ 0.39**; Mistral-7B: **0.25 $\to$ 0.23**; Command-R-7B: **0.08 $\to$ 0.04**; Gemma-3-27B: **0.25 $\to$ 0.03**; Llama-3.1-70B: **0.37 $\to$ 0.11**), whereas `Tool-encouraging` prompts elevate divergence (up to **0.58** on Qwen3-14B and **0.49** on Mistral-7B).
- **Tool schemas suppress the residual-stream refusal direction in 4 of 5 models (Table 3)**: Extracting the difference-in-means refusal direction $\hat{r}_l = \mathrm{unit}(\mu_l^{\mathrm{harm}} - \mu_l^{\mathrm{benign}})$ at 81–84% layer depth (layers 33/40, 26/32, 26/32, 51/62, and 67/80) shows that adding tool schemas significantly depresses refusal projection on harmful prompts in Qwen ($\Delta = 66.8, t = 5.6$), Mistral ($\Delta = 1.4, t = 5.1$), Command R ($\Delta = 26.4, t = 9.7$), and Gemma ($\Delta = 2902, t = 4.0$), while remaining flat in Llama ($\Delta = 0.2, t = 0.4$). Lower projection along $\hat{r}_l$ strongly predicts unsafe tool execution across all five models (**ROC AUC 0.760–0.864**).
- **Refusal activation is a partial mediator, and steering is a blunt lever (Tables 4 & 9)**:
  - **Activation patching** (restoring the `tool-normal` refusal projection at the operating layer to its matched `no-tool` value) flips only **13–34%** of unsafe calls in four models (and **90%** in Gemma 3 27B), and does so overwhelmingly by **suppressing tool calling altogether (`via no call`: 9–87%)** rather than converting the action into a safe tool call (`via safe call`: only **3–9%**). Among prompts where the patched model still emits a tool call, **80–96%** remain unsafe.
  - **Inference-time activation steering** ($h_l \leftarrow h_l + c \cdot \hat{r}_l$) drives unsafe tool calls near zero only at steering coefficients $c$ that **destroy 82–90% of benign tool calls** in Gemma, Mistral, and Llama (and reduce Qwen benign tool calls from 0.66 to 0.48 before causing 51% output degeneracy at $c = 700$). Across every model and steering strength where the model still calls a tool on $>10\%$ of prompts, the unsafe fraction among emitted calls remains **$>50\%$**.

---

## Relevance to Praxis

- **Per-channel refusal evaluation and deterministic action gates (`rules/agent-sandbox-safety.md`)**: Directly reinforces *"DO: Test refusal separately in every output channel an agent can use"* (which cites arXiv:2609.35117 on tool mediation altering refusal mechanisms). Because chat-refusal alignment fails on 10–52% of matched tool-enabled prompts and safety-reinforced system prompts still leave up to 39% divergence, tool authorization must be enforced by deterministic parameter predicates (`ForbiddenAction`-style schema and policy checks) at the tool gateway — see [`unified-capability-gateway`](../skills/unified-capability-gateway/SKILL.md) and [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md).
- **Do not rely on single-direction activation steering to fix unsafe tool arguments (`rules/agent-sandbox-safety.md`)**: Linear refusal-direction projection (AUC 0.76–0.86) is useful as a **read-only anomaly probe or risk signal** to trigger external policy inspection, but adding $c \cdot \hat{r}_l$ directly to hidden states acts as a global "don't call tools" switch rather than repairing unsafe arguments.
