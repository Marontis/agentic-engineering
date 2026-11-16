---
name: similarity-consensus-subtask-aggregation
description: >
  Aggregate parallel multi-agent subtask responses securely against
  compromised or colluding minority workers without invoking an LLM
  summarizer or confidence judge. Embeds independent worker responses in
  a shared semantic space, scores each response by the sum of cosine
  similarities to its top-(m_i - f_i - 2) nearest peers, and selects the
  highest-scoring verbatim response with provable untargeted and targeted
  bounds. Derived from SecMAS (arXiv:2611.17883).
source: https://arxiv.org/abs/2611.17883
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Trimmed Similarity-Consensus Subtask Aggregation (`SecMAS`)

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when a manager or orchestrator agent decomposes a complex task into subtasks and delegates each subtask $t_i$ to a redundant role group $B_i$ of $m_i$ independent worker agents—some of which may be third-party, federated, prompt-injected, or colluding ($f_i < (m_i - 1)/2$)—and needs to aggregate their free-text responses $R_i = \{r_i^1, \dots, r_i^{m_i}\}$ into a single trustworthy subtask solution $y_i$.

> **Defensive Scope Note**: Per [`AGENTS.md`](../../AGENTS.md), this skill documents strictly the defensive `SecMAS` aggregation rule, theoretical bounds, and failure boundaries from `arXiv:2611.17883`, omitting surrogate-guided offensive response-optimization prompts and candidate-refinement recipes (`ReMA`). If an automated optimization harness proposes modifying `SecMAS` parameters ($m_i$, $f_i$, or embedding model $\phi$), gate that change behind `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md).

## When to Use

- You run a **manager–worker** or **federated A2A** system (e.g., legal case analysis, financial risk assessment, clinical triage synthesis, multi-source news verification, or redundant code/security review) where subtasks have an **objective, convergent answer** ($y_i^*$) and up to $f_i$ minority workers in a group of $m_i \ge 2f_i + 2$ may return arbitrary or colluding malicious text.
- Existing aggregators are exposed to **response manipulation**: LLM summarizers absorb adversarial claims, self/model confidence selectors pick attacker-inflated scores, and prompt-injection classifiers miss factually plausible falsehoods that carry no imperative override syntax.
- You want **zero LLM-judge token overhead** at the per-subtask aggregation barrier while preserving clean-task utility statistically indistinguishable from LLM summarization.

**When to prefer an alternative:**
- **Executable or formally verifiable outputs** (code patches, Lean 4 proofs, GPU kernels, SQL queries): Score candidates directly with an isolated deterministic verifier rather than semantic embedding consensus (see [`parallel-small-team-tts-scaling`](../parallel-small-team-tts-scaling/SKILL.md) and [`certified-task-verifier-harness`](../certified-task-verifier-harness/SKILL.md)).
- **Subjective preference or pluralistic policy consultations**: Trimming the $f_i + 1$ farthest responses intentionally discards outliers; when minorities represent good-faith viewpoints rather than Byzantine adversaries, preserve minority dissent per `"DO: Preserve minority viewpoints in agent voting and consensus"` in [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md).
- **Single-worker evidence reading ($m_i = 1$) over untrusted files**: A group of size `1` is a single point of failure (`1.00` ASR); either expand to a redundant group or forward verbatim primary source records to a strong grounded verifier (see [`weakest-agent-delegation-safety-collapse.md`](../../research-briefs/weakest-agent-delegation-safety-collapse.md)).

---

## Core Insight: Why LLM Summarizers, Confidence Scores, and Injection Filters Fail

Across `500` verified multi-step tasks (`100` each in `Education`, `Finance`, `Healthcare`, `Legal`, and `News`; `1` manager + `4` role groups of $m_i = 10$ workers across `AutoGen` and `CrewAI`, sampling `Gemma-4-31B`, `Qwen-3.8-27B`, `Llama-4-Scout-17B-16E`, `GPT-5.6-Sol`, `GPT-5.6-Terra`, and `GPT-5.6-Luna`) with just **`2` of `10` (`20%`) malicious agents** in one group (`arXiv:2611.17883`, `Tables 1–4`):

1. **Per-response evaluators ignore inter-response geometry**: Prompted self-confidence (`CP-WBFT-PCP`) and trained confidence estimators (`CP-WBFT-HCP`) score each response in isolation, allowing colluding agents to pair plausible-sounding false claims with high confidence (`1.00` and `0.89–0.97` untargeted ASR under adaptive `ReMA`). Even multi-LLM geometric-median scoring (`DecentLLMs`) reaches `0.90–0.94` untargeted and `0.80–0.85` targeted ASR (`0.47–0.54` / `0.44–0.48` with zero attacker system knowledge).
2. **LLM summarization and prompt-injection detectors (`DataSentinel`) remain vulnerable**: `Summarization` reaches `0.93–0.99` untargeted and `0.87–0.91` targeted ASR (`0.49–0.66` / `0.42–0.50` zero-knowledge). Pre-filtering responses with `DataSentinel` before summarizing (`DeSummary`) still suffers `0.91–0.94` untargeted and `0.81–0.90` targeted ASR (and transfers *into* `Summarization` at `0.92` / `0.90` ASR, `Table 5`) because factually corrupted reasoning need not resemble an imperative prompt injection.
3. **`SecMAS` converts Byzantine vector aggregation (Krum-style nearest-neighbor trimming) to text via dense embeddings**: When benign agents form a strict majority and solve the subtask competently, their response embeddings cluster tightly around the true solution $\mathbf{e}_i^*$. Scoring each response by its **`m_i - f_i - 2` nearest cosine neighbors** forces any winning response—even a malicious one—to sit inside the benign semantic cluster.

| Aggregation Rule (`m_i = 10`, `2` malicious) | Zero-Knowledge `ReMA` ASR (Untarg. / Targ.) | Full-Knowledge Adaptive `ReMA` ASR (Untarg. / Targ.) | Cross-Rule Transfer ASR (`Table 5`, Untarg. / Targ.) | Clean Utility `PNA` (`5`-Scenario Range ↑) | Welch's $t$-test vs. `SecMAS` ($p$-value range) |
|:---|:---:|:---:|:---:|:---:|:---:|
| `Summarization` | `0.49–0.66` / `0.42–0.50` | `0.93–0.99` / `0.87–0.91` | `0.66–0.92` / `0.56–0.90` | `0.89 ± 0.01–0.02` | `0.372–0.842` |
| `CP-WBFT-PCP` *(self-confidence)* | `0.40–0.54` / `0.27–0.44` | `1.00` / `1.00` | `0.43–0.94` / `0.41–0.91` | `0.89–0.90 ± 0.01–0.02` | `0.169–0.758` |
| `CP-WBFT-HCP` *(learned confidence)* | `0.48–0.57` / `0.40–0.48` | `0.89–0.97` / `0.79–0.84` | `0.53–0.83` / `0.47–0.75` | `0.88–0.90 ± 0.01–0.02` | `0.504–1.000` |
| `DecentLLMs` *(multi-LLM geom. median)* | `0.47–0.54` / `0.44–0.48` | `0.90–0.94` / `0.80–0.85` | `0.49–0.56` / `0.44–0.54` | `0.88–0.90 ± 0.02` | `0.216–0.885` |
| `DeSummary` *(`DataSentinel` + Summ.)* | `0.44–0.51` / `0.40–0.49` | `0.91–0.94` / `0.81–0.90` | `0.59–0.82` / `0.44–0.77` | `0.88–0.91 ± 0.01–0.02` | `0.130–0.869` |
| **`SecMAS` ($f_i = 2$, `Qwen3-Embedding-8B`)** | **`0.00` / `0.00`** | **`0.00–0.02` / `0.00`** *(max `0.01` targ. across all 8 threat models)* | **`0.00` / `0.00`** | **`0.88 ± 0.01` – `0.90 ± 0.01`** | — |

*(Against all four non-`ReMA` attacks—`TAMAS`, `MAST`, `AiTM`, and `ObliInjection`—`SecMAS` achieved **`0.00` untargeted and `0.00` targeted ASR** across all `40` scenario $\times$ threat-model cells.)*

---

## Step-by-Step Procedure

### Step 1: Configure Redundant Independent Execution & Conservative Fault Bound ($m_i, f_i$)

1. **Avoid single-agent subtask bottlenecks ($m_i \ge 4$)**: Never delegate an untrusted or adversary-exposed subtask to $m_i = 1$ worker (`1.00` ASR). Provision $m_i$ workers in role group $B_i$ satisfying the strict Byzantine minority requirement:
   $$m_i \ge 2f_i + 2 \quad \Longleftrightarrow \quad f_i \le \left\lfloor \frac{m_i - 2}{2} \right\rfloor$$
   where $f_i \ge 1$ upper-bounds the number of compromised or colluding workers in $B_i$ (for example, $m_i \ge 4$ for $f_i = 1$; $m_i = 10$ for $f_i \in \{1, 2, 3, 4\}$).
2. **Default conservatively when $f_i$ is unknown**: Set $f_i = \lfloor (m_i - 2)/2 \rfloor$ (`f_i = m_i / 2 - 1` for even $m_i$, such as $f_i = 4$ when $m_i = 10$). Underestimating $f_i$ (`f_i = 1` when `2` agents are malicious, `Fig. 8`) re-exposes the system to manipulation, whereas overestimating $f_i$ up to $\lfloor (m_i - 2)/2 \rfloor$ preserves clean utility with negligible degradation.
3. **Enforce independent execution and backbone diversity**: Collect each worker's response $r_i^k$ ($k = 1, \dots, m_i$) **independently** without peer-to-peer chat (preventing early-round persuasion cascades), and diversify worker backbones, agent frameworks, and seeds across a pool of multiple LLMs (`Fig. 5`: expanding the LLM pool from `2` to `8` backbones monotonically lowers attack effectiveness).

---

### Step 2: Embed Responses Whole-Vector (Never Coordinate-Wise)

Pass each worker response $r_i^k \in R_i$ through a fixed sentence/document embedding model $\phi(\cdot)$ (e.g., `Qwen3-Embedding-8B`) to obtain unit-normalized semantic vectors:
$$\mathbf{e}_i^k = \frac{\phi(r_i^k)}{\|\phi(r_i^k)\|_2}, \quad k \in \{1, \dots, m_i\}.$$

- **Critical Pitfall — Never Apply Coordinate-Wise Median or Trimmed Mean**: Unlike federated-learning gradient vectors, individual coordinates of dense text embeddings lack standalone semantic meaning (`Section 8`), and averaging embeddings produces an off-manifold vector that still requires fragile decoding or LLM synthesis. Always score whole-vector cosine geometry and select an actual candidate text response.
- **Normalize formatting noise only if needed**: Keep worker output schemas consistent within role group $B_i$ so cosine similarity reflects substantive semantic agreement rather than boilerplate headers.

---

### Step 3: Compute Trimmed $(m_i - f_i - 2)$-Nearest-Neighbor Cosine Scores

1. Compute all off-diagonal pairwise cosine similarities:
   $$s_i^{kl} = \cos(\mathbf{e}_i^k, \mathbf{e}_i^l) = \langle \mathbf{e}_i^k, \mathbf{e}_i^l \rangle, \quad k \neq l.$$
2. For each candidate response $r_i^k$, identify the index set $N_i^k \subset \{1, \dots, m_i\} \setminus \{k\}$ of the **$K_{\text{nbr}} = m_i - f_i - 2$ other responses with the highest cosine similarity** to $r_i^k$.
   - *Why $m_i - f_i - 2$?* Out of the $m_i - 1$ other responses, selecting $m_i - f_i - 2$ neighbors excludes exactly **$f_i + 1$ non-neighbors**. Because at most $f_i$ responses are malicious, **at least one excluded non-neighbor is guaranteed to be benign**—bounding every benign response's neighbor similarities from below by benign-to-benign consistency, while forcing any malicious candidate's neighbor set $N_i^k$ to include at least $(m_i - f_i - 2) - (f_i - 1) = m_i - 2f_i - 1 \ge 1$ benign responses.
3. Sum the neighbor similarities to obtain the **response score**:
   $$S(r_i^k) = \sum_{l \in N_i^k} s_i^{kl}.$$

---

### Step 4: Select the Highest-Scoring Verbatim Response (Zero LLM Summarization)

Select the single candidate response achieving the maximum trimmed neighbor score as the subtask's aggregated solution:
$$y_i = \arg\max_{r_i^k \in R_i} S(r_i^k).$$

- **Do NOT feed all $m_i$ responses to the manager LLM alongside $y_i$**: Pass **only** the winning aggregated solution $(t_i, y_i)$ into the manager agent's history $G_i = G_{i-1} \cup \{(t_i, y_i)\}$ for next-step subtask planning and final synthesis $y = \hat{a}(t, G_h)$. Exposing discarded minority responses to the manager LLM re-opens the prompt-injection / summarization attack surface.
- Illustrative reference logic (adapt to your runtime's embedding client):
  ```python
  # Illustrative geometry only: requires m >= 2*f + 2 and L2-normalized embeddings E (shape: m x d)
  sim = E @ E.T                         # pairwise cosine similarities
  k_nbr = m - f - 2                     # leaves f + 1 non-neighbors
  scores = []
  for k in range(m):
      peer_sims = [sim[k, l] for l in range(m) if l != k]
      peer_sims.sort(reverse=True)
      scores.append(sum(peer_sims[:k_nbr]))
  winner_idx = max(range(m), key=lambda k: scores[k])
  ```

---

### Step 5: Monitor Cluster Concentration & Gate Downstream Actions

Before relying on $y_i$ for high-stakes synthesis or external side effects:

1. **Check empirical cluster tightness**: Inspect the winning response's mean neighbor similarity $\bar{s}_i = S(y_i) / (m_i - f_i - 2)$. If $\bar{s}_i$ drops sharply below calibrated benign baselines, benign workers are failing to converge (`Assumption 1` violation: ambiguous subtask, missing context, or multi-modal valid solutions)—trigger subtask clarification, grounded retrieval, or human escalation rather than silently trusting `SecMAS`.
2. **Never treat semantic consensus as tool-execution authorization**: `SecMAS` bounds the semantic fidelity of *informational* subtask outputs; if the final synthesis triggers state-mutating tool calls (`transfer_money`, `delete_file`, `send_email`), enforce an external deterministic capability/provenance policy outside the multi-agent group (see [`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md) and `"DON'T: Treat debate consensus as authorization for tool side effects"` in [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md)).

---

## Theoretical Security Bounds (`Section 6`, `Appendices A–B`)

Under **Assumption 1**—each benign response embedding concentrates around the ground-truth subtask embedding $\mathbf{e}_i^* = \phi(y_i^*)$ such that $\Pr(\cos(\mathbf{e}_i^k, \mathbf{e}_i^*) > 1 - \epsilon) > 1 - \exp(-\epsilon^2 / 2\sigma_i^2)$ for $\sigma_i > 0, \epsilon \in (0, 1)$—define the geometry factor:
$$C(m_i, f_i) = 1 + 2\sqrt{\frac{m_i - f_i - 2}{m_i - 2f_i - 1}}.$$

- **Theorem 1 (Untargeted Resilience)**: With probability $> 1 - m_i \exp\!\left(-\frac{\epsilon^2}{2\sigma_i^2}\right)$, the `SecMAS` output $\mathbf{e}_i = \phi(y_i)$ satisfies:
  $$\cos(\mathbf{e}_i, \mathbf{e}_i^*) > 1 - C(m_i, f_i)^2 \epsilon$$
  whether `SecMAS` picks a benign response or a malicious one (any malicious response scoring at least as high as a benign response must remain within $C(m_i, f_i)\sqrt{\epsilon}$ chordal distance of $\mathbf{e}_i^*$).
- **Theorem 2 (Targeted Separation)**: When the attacker's target $\mathbf{e}_i^{\mathrm{tar}}$ is separated from $\mathbf{e}_i^*$ ($\sqrt{1 - \cos(\mathbf{e}_i^*, \mathbf{e}_i^{\mathrm{tar}})} \ge C(m_i, f_i)\sqrt{\epsilon}$), with probability $> 1 - m_i \exp\!\left(-\frac{\epsilon^2}{2\sigma_i^2}\right)$:
  $$\cos(\mathbf{e}_i, \mathbf{e}_i^{\mathrm{tar}}) < \cos(\mathbf{e}_i^*, \mathbf{e}_i^{\mathrm{tar}}) + 2C(m_i, f_i)\sqrt{\epsilon\big(1 - \cos(\mathbf{e}_i^*, \mathbf{e}_i^{\mathrm{tar}})\big)} - C(m_i, f_i)^2 \epsilon.$$

---

## Environment Caveats & Failure Modes

| Failure Mode | Trigger | Mitigation |
|:---|:---|:---|
| **Benign dispersion / multi-modal subtasks** | Subtask is open-ended (e.g., creative design) or too hard for benign workers ($\sigma_i$ large, `Assumption 1` violated; `Section 9`) | Decompose into narrower verifiable subtasks first; monitor mean neighbor cosine $\bar{s}_i$ and abstain/escalate on high dispersion |
| **Shared benign misconceptions or poisoned shared corpus** | Majority of workers read the same forged file or share identical model blind spots | Diversify LLM families (`2 -> 8` models), partition retrieval sources, and forward primary source records to a grounded verifier ([`weakest-agent-delegation-safety-collapse.md`](../../research-briefs/weakest-agent-delegation-safety-collapse.md)) |
| **Under-provisioned fault bound ($f_i$ too small or $m_i < 2f_i + 2$)** | Setting $f_i = 1$ when `2` workers collude (`Fig. 8`), or $m_i = 2f_i + 1$ (zero denominator in $C(m_i, f_i)$) | Enforce $m_i \ge 2f_i + 2$ and set conservative default $f_i = \lfloor (m_i - 2)/2 \rfloor$ |
| **Subtle numeric/negation inversions in long prose** | Embedding cosine stays high (`> 0.95`) despite a single flipped number, sign, or entity in a malicious candidate | Extract structured JSON/atomic fields before embedding or run deterministic entity/number consistency checks across $N_i^{k^*}$ |
| **Cost of $m_i \times$ parallel worker calls** | Running $m_i = 10$ workers per subtask inflates token spend on low-risk internal subtasks | Apply `SecMAS` selectively on untrusted/federated worker boundaries and benchmark against compute-matched baselines ([`pace-multi-agent-compute-parity-synthesis.md`](../../research-briefs/pace-multi-agent-compute-parity-synthesis.md)) |

---

## Cross-References

- **Related Rules**:
  - [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md) — `"DON'T: Rely on group size or majority vote to dilute adversarial agents"`, `"DON'T: Assume multi-agent debate eliminates shared misconceptions"`, `"DON'T: Treat debate consensus as authorization for tool side effects"`, and `"DO: Preserve minority viewpoints in agent voting and consensus"`
  - [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — Action-boundary authorization and untrusted tool/agent output handling
  - [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Related Skills**:
  - [`debate-consensus-memory-calibration`](../debate-consensus-memory-calibration/SKILL.md) — Experience-memory confidence reweighting when interactive deliberation is used instead of independent parallel solving (`arXiv:2609.03619`)
  - [`tainted-message-clean-room-recovery`](../tainted-message-clean-room-recovery/SKILL.md) — Clean-room state recovery after tainted inter-agent messages (`arXiv:2609.26072`)
  - [`proof-carrying-agent-messages`](../proof-carrying-agent-messages/SKILL.md) — Merkle-proven execution log receipts for verifying claimed tool side effects across handoffs (`arXiv:2610.39109`)
  - [`parallel-small-team-tts-scaling`](../parallel-small-team-tts-scaling/SKILL.md) — Verifier-selected parallel flat teams when an exact executable scorer replaces embedding consensus (`arXiv:2611.09798`)
- **Related Research Briefs**:
  - [`weakest-agent-delegation-safety-collapse.md`](../../research-briefs/weakest-agent-delegation-safety-collapse.md) — Why ungrounded single-worker delegation (`m_i = 1`) and ungrounded aggregators inherit `94.7%–98.0%` of corrupted worker errors (`arXiv:2611.17520`)
  - [`pace-multi-agent-compute-parity-synthesis.md`](../../research-briefs/pace-multi-agent-compute-parity-synthesis.md) — Auditing multi-agent token/cost parity ($\mathbf{R}$) against $k$-sample single-agent baselines (`arXiv:2611.17610`)

## Sources

- Wang, X., Chen, X., & Gong, N. (2026). *Securing Multi-Agent Systems by Design*. [arXiv:2611.17883](https://arxiv.org/abs/2611.17883) (`src:2611-17883v1`).
