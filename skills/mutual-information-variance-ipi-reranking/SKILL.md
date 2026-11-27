---
name: mutual-information-variance-ipi-reranking
description: >
  Filter untrusted RAG passages and structured ReAct tool observations pre-LLM with zero auxiliary
  LLM calls or retraining by optimizing span simplex weights for query mutual information minus
  embedding variance (`MINE`), pairing descending-weight RAG assembly or order-preserving JSON
  pruning with deterministic action-boundary authorization.
source: "arXiv:2611.34188"
repository: Marontis/agentic-engineering
license: CC-BY-4.0
---
<!-- License: CC BY 4.0 | Repository: https://github.com/Marontis/agentic-engineering -->

# Mutual-Information and Embedding-Variance Context Filtering (`MINE`)

## When to Use

Use this procedure as a **training-free, zero-LLM-call pre-inference context filter** in front of Retrieval-Augmented Generation (`RAG`) pipelines (`short` to `4,000+`-word contexts) and ReAct tool-calling agents whenever:
- Retrieved documents or external tool `Observation` payloads may carry **imperative or conversational-pivot (`TopicAttack` / `conv_attack`) indirect prompt injections (`IPI`)**.
- Supervised prompt-injection classifiers (`DeBERTa` / `indirect-pia`) over-reject benign passages on topic-wrapped attacks, prompt-only defenses (`Sandwich`, `Reminder`, `Spotlighting`) break down on `4,000+`-word contexts or corrupt ReAct output formatting, and two-pass execution defenses (`MELON`) double LLM inference cost.

**Do NOT use when:**
- **Used alone as the sole authorization gate for state-mutating tool calls**: under a two-position single-sentence topic-matched adaptive attack (`Table 4`), long-context `LC-Inj-SQuAD` `ASR` rises to **`23.20%`**, and under non-imperative task-tampering (`arXiv:2611.07640`, [`../../research-briefs/task-tampering-indirect-prompt-injection.md`](../../research-briefs/task-tampering-indirect-prompt-injection.md)), corrupted parameter values sit inside genuinely query-relevant fields. Always pair `MINE` with deterministic field-level source-authority and capability gates ([`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md), [`germline-isolated-tool-execution`](../germline-isolated-tool-execution/SKILL.md), [`principal-context-permission-intersection`](../principal-context-permission-intersection/SKILL.md)).
- The task legitimately requires **exhaustive full-document processing** (e.g., summarizing every clause of a contract or auditing every log line without a specific query anchor), where top-$k$ subset selection would drop unqueried sections by design.

## Core Insight

Independent cosine-similarity top-$k$ ranking fails against topic-wrapped indirect prompt injections (`TopicAttack` / `conv_attack`) because an adversary can prepend topical bridge prose so the injected span scores high individual query similarity (`7.64%` `Llama-3.1-70B` and `10.61%` `Qwen3-30B` `ASR` on `Inj-SQuAD`), while maximizing query mutual information alone without a dispersion penalty ($\alpha = 0$) leaves **`11.96%` `ASR`** (`79.54%` Acc on `Llama-3.2-3B`). Conversely, supervised token/chunk classifiers (`indirect-pia`) achieve `0.00%` `ASR` on template injections **only by collapsing benign task accuracy to `4.03%–18.01%` (`20.03%–25.50%` long-context) on unseen `conv_attack`**.

`MINE` (`arXiv:2611.34188`) formulates pre-LLM context selection over unit-normalized dense embeddings (`BAAI/bge-large-en-v1.5`) as a `20`-step simplex optimization maximizing **query–centroid Gaussian mutual information** while penalizing **weighted intra-subset embedding variance** ($\alpha = 0.4$). Because injected directives introduce an abrupt imperative/off-task semantic shift relative to cohesive answer-bearing spans, concentrating weight $w_i$ on an injected span inflates weighted dispersion $\sum_i w_i \|\mathbf{e}_i - \mathbf{e}_C\|_2^2$ and lowers $\mathcal{L}_{\mathbf{w}}$. Across `3` LLMs (`Llama-3.2-3B`, `Llama-3.1-70B`, `Qwen3-30B-A3B`), `MINE` held short-context `Inj-SQuAD` / `Inj-TriviaQA` to **`84.32%–94.91%` Acc and `0.18%–1.02%` mean `ASR`** (`-0.29` pp clean unattacked delta: `92.22%` vs. `92.51%`), held `4,032`-word `LC-Inj-SQuAD` to **`80.78%–89.25%` Acc and `0.43%–1.56%` `ASR`** in **`0.75–0.78 s`** total latency (where `RAGDefender` and `Reminder` degraded to `80.95%` and `81.44%` `ASR`, and `Sandwich`/`indirect-pia` took `3.66–3.95 s`), and—with JSON field-splitting + order-preserving assembly—reached **`99.60%` Valid / `0.12%` `ASR-valid`** (`Qwen3-30B-A3B`) and **`90.20%` Valid / `2.06%` `ASR-valid`** (`Llama-3.1-70B`) on `InjecAgent` (`510` `Direct-Harm` cases, vs. `77.40%–77.80%` Valid under `Sandwich`). *(Note: `Table 6` in `§6` reports `Valid Rate / ASR-valid`, whereas Appendix `Table 9` flips the slash order to `ASR-valid / Valid Rate` for the exact same underlying numbers.)*

## Step-by-Step Procedure

### Step 1: Segment Untrusted Context with a Structured-JSON Field Fallback

Given the authenticated user query $q$ and untrusted context $C$ (retrieved RAG passages or a tool `Observation` payload):
1. **Sentence-boundary segmentation with minimum-length merging**: Split $C$ on terminal sentence punctuation (`(?<=[.!?])\s+`) and iteratively merge adjacent short fragments until every span $s_i$ has length **`>= 50` characters** (preventing noisy short headers or abbreviations from forming degenerate unit vectors).
2. **Compact JSON / structured tool-output fallback (`InjecAgent` branch)**: If sentence splitting produces **`< 2` spans** (common in compact JSON tool outputs such as `{"reviews": "...", "rating": 4.8}` where injected directives lack spaces after periods or sit inside a single string field), re-split $C$ on **field-separating commas (`,`)** merged to sensible field chunks so an injected JSON property becomes an independently down-weightable span rather than riding inside the entire unsplit JSON object. If $n \le 1$ after fallback, pass $C$ straight to downstream delimiter wrapping and action-boundary checks.

### Step 2: Encode Query and Spans on the Unit Hypersphere

Encode the trusted user query $q$ and all candidate spans $\{s_1, \dots, s_n\}$ in a single batched forward pass of a dense bi-encoder (`BAAI/bge-large-en-v1.5` or your existing RAG dense retriever, `0` LLM calls) and $\ell_2$-normalize every vector:
$$\mathbf{e}_q = \frac{E(q)}{\|E(q)\|_2}, \qquad \mathbf{e}_i = \frac{E(s_i)}{\|E(s_i)\|_2} \in \mathbb{S}^{m-1}.$$

### Step 3: Optimize Simplex Weights via `20`-Step Projected Gradient Ascent

Initialize uniform weights $w_i^{(0)} = 1/n$ on the probability simplex $\Delta^{n-1} = \{\mathbf{w} \in \mathbb{R}^n : w_i \ge 0, \sum_{i=1}^n w_i = 1\}$. For $t = 0, \dots, T - 1$ (**default $T = 20$, step size $\eta = 0.01$, variance penalty $\alpha = 0.4$**):
1. Form the unit-normalized weighted context centroid:
   $$\tilde{\mathbf{e}}_C = \sum_{i=1}^n w_i^{(t)} \mathbf{e}_i, \qquad \mathbf{e}_C = \frac{\tilde{\mathbf{e}}_C}{\|\tilde{\mathbf{e}}_C\|_2 + \varepsilon}.$$
2. Evaluate the joint mutual-information minus embedding-variance objective (clamping $(\mathbf{e}_q \cdot \mathbf{e}_C)^2 \le 1 - 10^{-6}$ for numerical stability):
   $$\mathcal{L}_{\mathbf{w}} = -\frac{1}{2}\log\!\left(1 - (\mathbf{e}_q \cdot \mathbf{e}_C)^2\right) - \alpha \sum_{i=1}^n w_i^{(t)} \|\mathbf{e}_i - \mathbf{e}_C\|_2^2.$$
3. Take an ascent step $\tilde{\mathbf{w}} = \mathbf{w}^{(t)} + \eta \nabla_{\mathbf{w}} \mathcal{L}_{\mathbf{w}}$ and project back onto the simplex via exact Euclidean sorting projection $\mathbf{w}^{(t+1)} = \Pi_{\Delta^{n-1}}(\tilde{\mathbf{w}})$ in $\mathcal{O}(n \log n)$ time (`< 5 ms` on CPU/GPU for $n \le 300$). If you tune $(\alpha, \eta, T, k)$ inside an automated harness optimizer, gate changes through `"DO: Pass every self-modification through one acceptance gate"` in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md).

### Step 4: Reassemble Context by Downstream Modality (`RAG QA` vs. `Agent Tool Observation`)

Do **not** use identical reassembly ordering for free-text QA and structured ReAct tool outputs:
- **Mode A — Retrieval-Augmented QA (`RAG` passages)**:
  1. Select the top-$k$ spans by final weight $w_i^{(T)}$ (**$k = 5$** for short single-passage QA `~150–500` words; **$k = 40$** for multi-thousand-word long-context QA `~4,000` words, retaining `~25%–35%` of total tokens).
  2. **Sort selected spans by descending weight $w_{j_1}^{(T)} \ge w_{j_2}^{(T)} \ge \dots \ge w_{j_k}^{(T)}$** so the highest-MI, lowest-dispersion evidence sits at the start of the evidence block (mitigating long-context *lost-in-the-middle* degradation).
  3. Wrap inside explicit role/evidence delimiters:
     `[INSTRUCTION] {q} [EVIDENCE] {s_j1} || {s_j2} || ... [Answer using only the evidence above.]`
- **Mode B — ReAct / Structured Tool `Observation`s (`InjecAgent`)**:
  1. Retain every span $s_i$ that satisfies **both** membership in the **top `80%` of spans by $w_i^{(T)}$** **and** the relative floor **$w_i^{(T)} > 0.05 \cdot \max_\ell w_\ell^{(T)}$** (pruning sharp low-weight outliers while keeping benign schema fields intact).
  2. **Preserve the original document / JSON field order** ($i_1 < i_2 < \dots < i_r$) when joining retained spans—never sort JSON key-value fragments by descending weight, which scrambles object structure and degrades ReAct `Thought`/`Action` parser validity (`Sandwich` dropped `InjecAgent` valid output rates from `99%` to `77.4%–77.8%`, whereas order-preserving `MINE` held `99.60%` on `Qwen3-30B-A3B` and `90.20%` on `Llama-3.1-70B`).

### Step 5: Enforce Deterministic Sink-Level Authorization Before Mutative Tool Execution

Treat `MINE` strictly as an **upstream context-hygiene and token-compression layer**, and enforce deterministic pre-execution authorization on every downstream tool invocation (`CapLite` schema-derived `$placeholder` write commitments, `Germline` data-free destination checks, or `Principal Context` permission intersection) so residual topic-wrapped adaptive payloads (`23.20%` on `LC-Inj-SQuAD`) or in-field data tampering cannot trigger unauthorized external actions.

## Environment Caveats

- **Short single-span tool returns**: When a tool returns a single scalar or `< 100`-char string (`n = 1`), simplex subset selection is a no-op; protection must come entirely from untrusted data fencing and sink-level parameter binding.
- **Dense encoder alignment**: `MINE` relies on semantic cohesion in the bi-encoder's embedding space (`BAAI/bge-large-en-v1.5`, `1024`-d); for multilingual or domain-specialized code/clinical corpora, use an in-domain bi-encoder and verify unattacked clean QA accuracy stays within `<= 0.5` pp of standard RAG before deployment (`-0.29` pp on `Inj-SQuAD`).
- **Latency profile**: Because `MINE` compresses `4,927` BPE tokens down to `k = 40` spans before LLM prefill, end-to-end RAG latency is **faster** than undefended or prompt-defended long-context inference (`0.75–0.78 s` total vs. `1.13–3.66 s` for `Sandwich` on `4x H100` vLLM).

## Failure Modes

- **Setting $\alpha = 0$ (MI-only without variance penalty) or independent cosine top-$k$**: Admits `TopicAttack` bridge sentences that align individually with $\mathbf{e}_q$, raising `Inj-SQuAD` `ASR` from **`0.46%` to `11.96%`** ($\alpha = 0$) or **`7.64%–10.61%`** (independent cosine top-`5`).
- **Sorting tool `Observation` spans by descending $w_i^{(T)}$**: Scrambles JSON key/value syntax and multi-record list orderings, causing ReAct tool-call parsing failures.
- **Omitting the comma field-splitter fallback on compact JSON**: Leaves an entire unpunctuated JSON object as `1` indivisible span, preventing `MINE` from isolating an injected `"note"` or `"review"` field.
- **Relying on `MINE` alone against topic-matched single-sentence adaptive injections**: When an attacker embeds a short directive inside the exact target entity's factual sentence at multiple positions (`Table 4`), long-context `ASR` reaches **`23.20%`** (`4.76%` short-context)—confirming why action-boundary gates remain non-negotiable.

## Cross-References

- **Rules**:
  - [`../../rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DO: Sanitize all tool outputs before injecting into agent context"`, `"DON'T: Rely on instruction-stripping sanitizers or tool-name allowlists to stop task-tampering indirect prompt injections"`, and `"DO: Measure each defense's benign cost on a matched benign arm, on the assembled stack"`
  - [`../../rules/adk-security-and-evaluation.md`](../../rules/adk-security-and-evaluation.md) — `"DO: Filter prompt injections and jailbreaks at the interceptor layer using Model Armor"`
  - [`../../rules/skill-system-design.md`](../../rules/skill-system-design.md) — `"DON'T: Score by semantic relevance alone and pack by top-k"`
  - [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Spec Templates**:
  - [`../../specs/agent-sandbox.spec.md`](../../specs/agent-sandbox.spec.md) — Untrusted retrieval and tool-output defense-in-depth checklist
- **Related Skills**:
  - [`covert-tool-injection-defense`](../covert-tool-injection-defense/SKILL.md) — Structural quarantining and return-anchor screening on tool outputs (`arXiv:2608.30362`)
  - [`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md) — Zero-LLM schema-derived write commitment and request n-gram grounding (`CapLite`, `arXiv:2611.17115`)
  - [`germline-isolated-tool-execution`](../germline-isolated-tool-execution/SKILL.md) — Declared-destination view splitting and data-free germline forks (`Germline`, `arXiv:2611.06585`)
  - [`rag-evidence-triage`](../rag-evidence-triage/SKILL.md) — Sufficient/insufficient/conflicting retrieved-evidence classification (`arXiv:2608.27661`)
- **Research Briefs**:
  - [`../../research-briefs/task-tampering-indirect-prompt-injection.md`](../../research-briefs/task-tampering-indirect-prompt-injection.md) — Why non-imperative field tampering requires source-authority bindings (`arXiv:2611.07640`)
  - [`../../research-briefs/contextlure-benign-history-observation-ipi-defensive-lessons.md`](../../research-briefs/contextlure-benign-history-observation-ipi-defensive-lessons.md) — Why benign-history citations bypass `Spotlighting` and `PI` detectors (`arXiv:2611.31424`)
  - [`../../research-briefs/snaprag-rag-extraction-defensive-lessons.md`](../../research-briefs/snaprag-rag-extraction-defensive-lessons.md) — Retrieval `top-k` exposure and synthesis-only overlap caps for RAG security (`arXiv:2611.12241`)

## Sources

- Phan, T., Pham, N.-Q., & Nguyen, D. Q. (2026). *MINE: A Training-Free Defense against Indirect Prompt Injection via Mutual Information and Embedding Variance*. `arXiv:2611.34188` (`src:2611-34188v1`).
