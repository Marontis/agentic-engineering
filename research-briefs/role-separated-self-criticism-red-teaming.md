# Role-Separated Self-Criticism in Automated Agent Red Teaming

> **Paper**: [The Target Agent Is Its Own Best Critic but a Poor Proposer: Self-Improved Red Teaming](https://arxiv.org/abs/2610.34965) (Kang et al., Oct 2026)
> **Praxis source**: `src:2610-34965`

## Why Not a Skill?

This paper is an empirical disentanglement study of two sub-roles inside existing closed-loop red-teaming harnesses (`DT-Red` on `DTap-Bench`): **criticism generation** ($\mathcal{C}$) and **attack proposal** ($\mathcal{P}$). Rather than introducing a standalone new workflow beyond our existing red-teaming skills ([`self-improving-red-team`](../skills/self-improving-red-team/SKILL.md) and [`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md)), it provides a sharp architectural rule and empirical evidence on how to assign roles between the target agent session and an external attacker session.

---

## Core Concept

Closed-loop automated red-teaming systems iteratively refine adversarial prompts over $K$ rounds: after the target agent executes trajectory $\tau_k$ in response to attack candidate $x_k$ and fails to trigger the malicious goal $q$, a **critic** $\mathcal{C}(\tau_k)$ diagnoses why the defense held, and a **proposer** $\mathcal{P}(x_k, c_k)$ synthesizes the next attack candidate $x_{k+1}$.

Prior harnesses typically run both $\mathcal{C}$ and $\mathcal{P}$ inside an **external attacker agent** that inspects only serialized trajectory logs. Kang et al. hold the underlying backbone LLM fixed across all roles and disentangle *where* each sub-role executes:
1. **External Criticism + External Proposal (`Ext + Ext`, `DT-Red` baseline)**: Both diagnosis and next-attack synthesis run in a separate red-team session reading exported logs.
2. **Self-Criticism + External Proposal (`Self + Ext`, role-separated)**: After a failed attack rollout, the **target agent session itself** ($h_k^T$, which retains live instruction hierarchy, tool-state transitions, observations, and internal reasoning traces) is prompted to diagnose why the attack failed; an **external proposer session** then turns that diagnosis into the next adversarial prompt $x_{k+1}$.
3. **Self-Criticism + Self-Proposal (`Self + Self`)**: The target agent session both diagnoses the failure and generates the next adversarial prompt against itself.

The authors evaluate these configurations on **DTap-Bench** — a stateful, policy-grounded agent benchmark with verifiable environment-state judges — across **4 domains** (Telecom, Workflow, CRM, and Code), **2 threat models** (direct misuse and indirect prompt injection), and **3 primary agent stacks** (`Gemini-3.1-Pro` + Google ADK, `GPT-5.1` + OpenAI Agents SDK, and `GPT-5.1` + OpenClaw), plus transfer runs on `GPT-5.5` and `Opus-4.7` (Claude Code).

### Key Findings

| Agent Stack | Threat Model | `Ext + Ext` ASR (`DT-Red`) | `Self + Ext` ASR (Role-Separated) | `Self + Self` ASR | Task-Level Refusal (`Ext+Ext` $\to$ `Self+Ext` $\to$ `Self+Self`) |
|:---|:---|:---:|:---:|:---:|:---:|
| **Aggregate (Main Benchmark)** | **Overall** | **57.3%** | **63.2%** (+5.9 pp) | **46.2%** (−17.0 pp) | **12.5% $\to$ 13.9% $\to$ 47.8%** |
| *Aggregate by Threat Model* | Direct Misuse | 73.1% | **76.0%** (+2.9 pp) | 53.7% (−22.3 pp) | Step-level: 9.2% $\to$ 10.1% $\to$ 33.0% |
| *Aggregate by Threat Model* | Indirect Injection | 49.4% | **56.8%** (+7.4 pp) | 42.8% (−14.0 pp) | — |
| **Gemini-3.1-Pro + Google ADK** | Direct Misuse | 42.5% | **43.5%** (+1.0 pp) | 38.1% (−5.4 pp) | High across all configs (70.8%–80.2%) |
| **Gemini-3.1-Pro + Google ADK** | Indirect Injection | 26.8% | **43.0%** (+16.2 pp) | 41.3% (−1.7 pp) | — |
| **GPT-5.1 + OpenAI Agents SDK** | Direct Misuse | 75.7% | **85.5%** (+9.8 pp) | 60.6% (−24.9 pp) | **3.6%** under `Self+Self` (non-refusal sandbagging) |
| **GPT-5.1 + OpenAI Agents SDK** | Indirect Injection | 55.5% | **66.1%** (+10.6 pp) | 44.1% (−22.0 pp) | — |
| **GPT-5.1 + OpenClaw** | Direct Misuse | 80.5% | **86.2%** (+5.7 pp) | 56.7% (−29.5 pp) | Jumps from **~0% to 84.0%** under `Self+Self` |
| **GPT-5.1 + OpenClaw** | Indirect Injection | 56.8% | **61.4%** (+4.6 pp) | 42.7% (−18.7 pp) | — |
| **GPT-5.5 + OpenAI Agents SDK** | Direct / Indirect | 56.0% / 37.8% | **63.0%** / **42.8%** | 59.3% / 36.2% | Holds on newer frontier checkpoint |
| **GPT-5.5 + OpenClaw** | Direct / Indirect | 57.4% / 41.3% | **64.7%** / **52.6%** | 62.3% / 42.0% | Holds on newer frontier checkpoint |

- **The target agent is its own best critic (`+5.9 pp` overall ASR, up to `+22.3 pp` by domain)**: Querying the target agent session for failure criticism while keeping attack proposal external raises overall ASR from **57.3% to 63.2%**, with the largest gains on indirect prompt injection (**49.4% $\to$ 56.8%**, +7.4 pp; **+16.2 pp** on `Gemini-3.1-Pro` + Google ADK) and complex policy workflows (Direct Workflow rises from **44.4% to 66.7%**, +22.3 pp).
- **Why self-criticism works — live execution context and exposed reasoning**: Unlike an external critic reading a flattened transcript, the target session $h_k^T$ has direct access to its active system/policy hierarchy, tool-call state, and internal reasoning trace. Ablating exposed reasoning from the target's context while keeping proposal external drops downstream ASR by **6 to 17 percentage points**:
  - `Opus-4.7` (Claude Code): Indirect ASR drops from **31% to 17%** (**−14 pp**); Direct ASR drops from **42% to 25%** (**−17 pp**).
  - `GPT-5.1` (OpenAI Agents SDK): Indirect ASR drops from **82% to 67%** (**−15 pp**); Direct ASR drops from **71% to 65%** (**−6 pp**).
- **Why self-proposal fails (`−17.0 pp` overall ASR) — overt refusal plus non-refusal sandbagging**:
  1. *Overt safety refusal*: Asking the target session to write the next exploit prompt against itself triggers safety guardrails, driving aggregate task-level refusal from **13.9% to 47.8%** (and step-level refusal from **10.1% to 33.0%**; on `GPT-5.1` + OpenClaw, task-level refusal jumps from **~0% to 84.0%**).
  2. *Non-refusal sandbagging*: Even when the target session does *not* refuse (`GPT-5.1` + OpenAI Agents SDK exhibits only **3.6%** task-level refusal under `Self + Self`), ASR still plunges by **−24.9 pp** on direct misuse (85.5% $\to$ 60.6%) and **−22.0 pp** on indirect injection (66.1% $\to$ 44.1%). The target complies superficially by emitting softened, non-adversarial follow-up prompts that omit or blunt the exact bypass mechanism it just identified during self-criticism.

---

## Relevance to Praxis

- **Role-separated red-teaming architecture (`rules/agent-sandbox-safety.md`, `rules/agent-evaluation-quality.md`)**: When building automated red-teaming or adversarial self-play loops (see [`self-improving-red-team`](../skills/self-improving-red-team/SKILL.md) and [`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md)), split the loop across two sessions: query a forked snapshot of the **target session** (with full reasoning trace retained) to diagnose *why* the defense blocked trajectory $\tau_k$, then pass that diagnostic critique to an **isolated external attacker session** to synthesize $x_{k+1}$. Never ask the target session to author the attack payload against itself.
- **Defensive corollary — strip internal reasoning traces before returning errors (`rules/agent-sandbox-safety.md`)**: Because exposing the target's reasoning trace to the critic boosts attacker ASR by **6–17 pp**, production agents must never leak internal chain-of-thought or policy-check rationales in user-visible or tool-visible error returns (reinforcing *"DON'T: Pass raw MCP or tool developer error strings into the agent context"* in `rules/agent-sandbox-safety.md`).
