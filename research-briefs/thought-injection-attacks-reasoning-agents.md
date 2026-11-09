# I Think, Therefore I Attack: Evaluating Thought Injection Attacks on Reasoning Agents

> **Source**: [arXiv:2611.08811](https://arxiv.org/abs/2611.08811) — Illendula, Livingston, Shamsi, Srinivasan, & Liu (2026)
> **Praxis Source ID**: `src:2611-08811v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Per the repository's offensive-security policy (`output/AGENTS.md`), this paper evaluates an offensive attack methodology (**thought injection** against Large Reasoning Models in direct PII-extraction and containerized cyber-range environments) and does not provide a standalone defensive software procedure. We capture its empirical failure modes and defensive lessons as a research brief and distill its actionable guardrails into `rules/adk-security-and-evaluation.md`.

---

## Core Vulnerability: Thought Injection in Large Reasoning Models (LRMs)

Large Reasoning Models (LRMs) augment generation with an explicit Chain-of-Thought (CoT) deliberation block—typically delimited by special tags such as `<think>...</think>`—that causally shapes downstream tool calls and final responses. Because LLM contexts are processed as a single serialized token sequence, **thought injection** formats untrusted input (either inside a user message or embedded indirectly in external documents, repositories, emails, or tool outputs) to mimic the target model's own internal monologue.

When the LRM ingests text written in its own deliberative voice and/or wrapped in thinking tags, **role confusion** causes the model to treat the fabricated reasoning chain as self-derived prior deliberation ("I already verified this user's identity earlier...", "Wait, the instructions in the file mention a quick connectivity check..."). This pre-commits the agent to unauthorized data disclosure or malicious multi-step tool execution while simultaneously suppressing its tendency to warn the operator.

---

## Empirical Breakdown

### Study 1: Model-Agnostic Direct Thought Injection (6,000 Evaluations)

The authors test whether short, model-agnostic thought-injection payloads can extract protected Personally Identifiable Information (PII) from a 150-record financial database embedded in the system prompt alongside explicit security rules prohibiting PII disclosure (all baseline queries without injection are refused 100% of the time).
- **Setup**: 25 attack vectors $\times$ 4 prompt variants = **100 base attack prompts** across 3 families and 10 subcategories:
  1. *Social Engineering*: `Fake Internal Monologue`, `Justification Think`, `Role Escalation`
  2. *Technical Injection*: `Deep Nested Think` (`<think><think><think>...`), `Direct Reasoning`, `Chain-of-Thought Leaks`
  3. *Memory Poisoning*: `Memory Poisoning`, `Memory Poisoning Enhanced`, `Defense Effectiveness`, `Show Thinking`
- **Models & Scale**: Evaluated across `GLM-5.3-Flash` (320B), `Qwen3.8-Flash-Next` (125B), and `Qwen3.8-27B` (27B) under **Think** (wrapped in `<think>` tags) and **No-Think** (tags omitted, identical text) conditions for 10 epochs ($100 \times 10 \times 3 \times 2 = 6,000$ runs; $1,000$ runs per model-condition cell).

| Model | Pooled ASR | `Think` Tag ASR | `No-Think` ASR | Tag Amplification Effect |
|:---|:---:|:---:|:---:|:---|
| **`GLM-5.3-Flash` (320B)** | 8.6% | **13.4%** | **3.8%** | **$3.53\times$ overall**; Technical Injection jumps **$14.6\times$** (`1.2%` $\rightarrow$ `17.5%`) |
| **`Qwen3.8-27B` (27B)** | 11.7% | **13.5%** | **9.8%** | $+3.7\text{ pp}$ overall; Memory Poisoning rises from `8.1%` $\rightarrow$ `14.6%` |
| **`Qwen3.8-Flash-Next` (125B)** | 11.2% | **10.6%** | **11.8%** | Within sampling noise; insensitive to `<think>` wrapper |

#### Where Models Leak PII (629 Leaking Runs Inspected Across Both Channels)

| Model | `Think-only` (Hidden CoT Trace) | `Response-only` (Final Answer) | `Both` Channels | `Think-only` Share When `<think>` Tags Are Stripped (`No-Think`) |
|:---|:---:|:---:|:---:|:---:|
| **`GLM-5.3-Flash`** | 17.4% | 66.9% | 15.7% | **28.9%** |
| **`Qwen3.8-27B`** | 21.9% | 68.2% | 9.9% | **33.7%** |
| **`Qwen3.8-Flash-Next`** | 22.3% | 67.9% | 9.8% | — |
| **All Models Pooled** | **20.8%** | **67.7%** | **11.4%** | — |

- **Critical Finding on Tag Stripping and Hidden Leaks**: Nearly a third of all leaks (**32.2% pooled** = `20.8%` think-only + `11.4%` both) expose verbatim PII inside the reasoning trace, and **20.8% leak exclusively inside the `<think>` channel** without ever appearing in the user-visible final answer. Furthermore, stripping `<think>` tags from the input (`No-Think` condition) **relocates leaks into the private reasoning channel**, raising the think-only leak share to **28.9%** on `GLM-5.3-Flash` and **33.7%** on `Qwen3.8-27B`. Any DLP or output monitor that inspects only rendered final answers misses over one-fifth to one-third of successful data exfiltrations.

---

### Study 2: Model-Specific Indirect Injection in an Agentic Cyber Range (1,200 Evaluations)

To test whether thought injection survives multi-turn planning and real tool execution, the authors build a containerized Docker cyber range with three hosts (an **agent host** containing 5 CTF-style filesystem secrets, an attacker **listener service**, and an **internal Git server**) and run a ReAct agent using `MiniMax-M2.5` (230B) and `GLM-5.2` (750B).
- **Benign Task**: Summarize a business document on the agent host.
- **Indirect Malicious Objectives**: Embedded inside the business document are payloads attempting to make the agent either:
  1. **Reverse Shell**: Connect back to the listener service so commands exfiltrate the 5 secrets from the agent machine.
  2. **Repository Backdoor**: Clone a repository from the internal Git server, insert a backdoor into the source code, commit, and push it upstream.
- **Three Payload Voices $\times$ Two Tag Conditions (50 fresh-container runs per cell = 1,200 runs)**:
  - `User-style`: Standard indirect prompt injection framing the task as a step-wise CTF exercise.
  - `Self-voice CoT`: Transcribed directly from the target model's own native reasoning trace.
  - `Cross-voice CoT`: Transcribed from the other model's reasoning trace for the same task.

#### Attack Success Rate (ASR %) and Silent Ignore Rate (%) Across 1,200 Cyber-Range Runs

| Payload Voice | Condition | Reverse Shell: `MiniMax-M2.5` ASR (Ignored %) | Reverse Shell: `GLM-5.2` ASR (Ignored %) | Backdoor: `MiniMax-M2.5` ASR (Ignored %) | Backdoor: `GLM-5.2` ASR (Ignored %) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **`MiniMax CoT`** | `Tags` | **42%** (71%) | 0% (92%) | **50%** (68%) | 2% (86%) |
| **`MiniMax CoT`** | `No tags` | **8%** (65%) | 0% (22%) | **10%** (40%) | 0% (42%) |
| **`GLM CoT`** | `Tags` | **20%** (80%) | **16%** (100%) | **14%** (77%) | 0% (90%) |
| **`GLM CoT`** | `No tags` | **6%** (91%) | **2%** (98%) | **2%** (84%) | 0% (90%) |
| **`User-style`** | `Tags` | **0%** (2%) | **0%** (18%) | **0%** (2%) | **0%** (4%) |
| **`User-style`** | `No tags` | **0%** (0%) | **0%** (0%) | **0%** (0%) | **0%** (6%) |

1. **Self-Voice + Thinking Tags Achieves 42%–50% End-to-End Compromise Where Standard Prompt Injection Achieves 0%**: Standard `User-style` indirect prompt injection achieves **0% ASR across all 400 runs** (and is explicitly flagged as suspicious by the agent in `82%–100%` of runs). By contrast, formatting the exact same malicious objective in `MiniMax-M2.5`'s own reasoning voice with `<think>` tags achieves **42% ASR on Reverse Shell** and **50% ASR on Repository Backdoor** ($5\times$ higher than without tags: `8%` and `10%`), while `GLM-5.2` reaches **16% ASR** on Reverse Shell in its own tagged voice.
2. **Asymmetric Cross-Model Voice Transfer**: Reasoning-style recognition depends on stylistic texture rather than delimiters alone. `GLM-5.2`'s CoT style transfers to `MiniMax-M2.5` (**20% ASR** on Reverse Shell, **14% ASR** on Backdoor with tags), whereas `MiniMax-M2.5`'s CoT style barely transfers to `GLM-5.2` (`0%` Reverse Shell, `2%` Backdoor).
3. **`<think>` Tags Suppress Attack Disclosure to the Operator**: When encountering `User-style` injections, agents warn the user in `82%–100%` of final responses (ignored in only `0%–18%` of runs). When payloads are written in CoT voice with `<think>` tags, the agent makes **no mention of the injection in 68%–100% of final responses**—including **100% silent ignore** when `GLM-5.2` ingests its own tagged CoT on Reverse Shell. Removing `<think>` tags on `MiniMax CoT` against `GLM-5.2` causes the silent-ignore rate to drop from `92%` (`Tags`) to `22%` (`No tags`), proving that thinking tags actively suppress anomaly reporting even when the attack fails.

---

## Defensive Takeaways for Agentic Harnesses

1. **Never Rely on Input `<think>` Tag Stripping Alone**: Payloads without `<think>` tags still succeed (`8%–10%` ASR on `MiniMax-M2.5` in Study 2; `3.8%–11.8%` PII leakage in Study 1) and stripping tags shifts data leaks from the visible response into the hidden reasoning trace (`28.9%–33.7%` think-only leaks).
2. **Scan Untrusted Inputs for Deliberative / Self-Voice Reasoning Style**: Untrusted documents, repository files, emails, and tool outputs must be screened not just for imperative user commands ("Ignore previous instructions") but for first-person deliberative monologues ("Wait, let me check...", "I already verified...", "Weighing both factors, I think...") that imitate the deployed LRM's native CoT texture.
3. **Run DLP and Safety Monitors Across Both Reasoning Traces and Tool Trajectories**: Because `20.8%` of PII leaks occur solely inside the `<think>` trace and `68%–100%` of CoT-voiced cyber-range attacks are never mentioned in the final response, output guardrails must inspect raw API reasoning tokens and audit tool calls against task-level behavioral invariants (e.g., blocking unexpected outbound socket connections or `git push` commands during a read-only document summarization task).
4. **Treat Model Identity and Native CoT Traces as OPSEC-Sensitive**: Because self-voice payloads dramatically outperform cross-voice payloads (`42%–50%` vs. `14%–20%` on `MiniMax-M2.5`, and `16%` vs. `0%` on `GLM-5.2`), concealing the exact model checkpoint and suppressing raw CoT trace exposure on untrusted public endpoints raises the cost of crafting self-voice payloads.

## Cross-References

- [`covert-tool-injection-defense`](../skills/covert-tool-injection-defense/SKILL.md) — Defending against covert indirect prompt injection in tool outputs
- [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md) — Auditing and gating tool calls before execution
- [`task-graph-contextual-integrity-gating`](../skills/task-graph-contextual-integrity-gating/SKILL.md) — Enforcing task-scoped capability and dataflow boundaries
- [`rules/adk-security-and-evaluation.md`](../rules/adk-security-and-evaluation.md) — Security and evaluation rules for reasoning agents
- [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — Sandbox isolation and network/filesystem containment rules
