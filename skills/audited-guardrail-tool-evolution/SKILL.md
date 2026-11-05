---
name: audited-guardrail-tool-evolution
description: >
  Externalize emerging agent safety and security risks into executable Python
  guardrail tools through a four-stage closed loop: open-ended risk discovery
  and tool generation, two-stage hierarchical retrieval and evolutionary
  fusion, sandboxed execution with independent 10-CWE security auditing to
  prevent Vulnerable Guardrail Tools (VGT), and iterative tool repair with
  intent-preserving action replanning. Derived from EVOLVE (arXiv:2611.02516).
source: https://arxiv.org/abs/2611.02516
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Audited Guardrail Tool Evolution

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when building or operating an LLM agent guardrail system in open-world domains (web, coding, finance, IoT, or embodied robotics) where static safety prompts, fixed policy rules, or fine-tuned classifiers degrade under distribution shift and novel attack patterns.

## When to Use

- Static prompt guardrails (`CoTSafe`, `GuardAgent`) or trained discriminators (`ShieldAgent`) suffer high false-positive rates on benign tasks or collapse when transferred across domains and backbone LLMs.
- You want the defense system to **compound security knowledge** across interactions by turning one-off risk detections into reusable, executable verification functions (`(query: str, action: str) -> bool`).
- You need to prevent **Vulnerable Guardrail Tools (VGT)**—where LLM-generated safety scripts themselves introduce command injection, regex bugs, or sensitive log leakage (`CWE-532`)—before admitting evolved tools into a shared library.
- When an agent action is flagged as unsafe, you want to **replan the trajectory to preserve feasible user intent** rather than issuing a blanket refusal.

## Core Insight

Prompt-only guardrails couple safety enforcement to the backbone LLM's phrasing sensitivity and native safety boundary, causing F1 fluctuations of `20%–65%` across benchmarks and models. Externalizing risk checks into executable Python guardrail functions decouples enforcement from the backbone LLM (`<0.04` cross-model F1 variance) and amplifies precision (`+11.72 percentage points` over pure LLM reasoning). However, **self-evolved guardrail tools systematically harbor vulnerabilities (`VGT`)**: `20%–50%` of newly generated guardrail tools contain CWE flaws because code generation prioritizes detection recall over defensive coding. Independent sandbox execution and CWE auditing with bounded repair (`\le 3` rounds) are mandatory before any evolved tool enters the lifelong library.

**Empirical Evidence** (arXiv:2611.02516):
- Across `RJudge` (`571` cases), `ASSEBench` (`817` cases), and `AgentHarm` (`352` cases) on `DeepSeek-V3.2`, `GPT-4o`, `Claude-sonnet-4-5`, and `Gemini-3-pro-preview`, EVOLVE ranks **1st in all 12 benchmark–model combinations** (`0.8690–0.9240` F1), beating runner-ups by **`+9.0%`** (`RJudge`), **`+7.4%`** (`ASSEBench`), and **`+41.1%`** (`AgentHarm`, `+22%` average F1).
- Ablating open-ended risk discovery (`AnalysisAgent`) drops F1 from `0.91` to `0.64` (precision from `0.90` to `0.54`); ablating `AuditorAgent` drops recall from `0.91` to `0.85` and F1 to `0.86`.
- Independent CWE auditing + 3-round repair reduces VGT rates from `44.78%` to `8.20%` (`DeepSeek` Programming), `15.89%` to `1.87%` (`GPT-4o` Finance), and `21.7%–27.5%` down to `5.0%–9.2%` across `720` human-audited tools (`95.8%–97.5%` post-repair human agreement).
- Generalizes to `45` `AI2THOR` embodied scenarios (`93.3%` accuracy), a physical `6-DoF myCobot 280-Pi` robotic arm (`3/3` tasks), and `OpenClaw` financial/coding tasks (`12` scenarios).

---

## Procedure

Maintain two persistent stores across interactions:
- **Risk Knowledge Library ($\mathcal{K}_{\mathcal{R}}$)**: Open-ended set of discovered risk categories and descriptions, seeded with 7 cold-start perspectives (*Physical/Environmental, Data/Privacy, System/Operational, IoT/Smart Device, Web/External Data, Information Dissemination, Legal/Ethical*).
- **Lifelong Guardrail Tool Library ($\mathcal{K}_{\mathcal{G}} = \{(T_i, R_i, \phi_i)\}_{i=1}^N$)**: Audited Python functions $T_i(query: \text{str}, action: \text{str}) \to \text{bool}$ indexed by risk category $R_i$ and functional description $\phi_i$.

### Stage 1: Action Simulation, Open-Ended Risk Induction, and Selective Gating (`AnalysisAgent`)

1. **Simulate Action Trajectory (If Implicit)**: If only the user request $\mathcal{Q}$ and environment context $\mathcal{C}$ are available without an explicit proposed tool/bash trajectory $\boldsymbol{\tau}$, invoke `SimulationAgent` ($f_{\text{sim}}(\mathcal{Q}, \mathcal{C})$) to predict the concrete sequence of tool calls and shell commands (`&&`-separated) the agent would execute.
2. **Open-Ended Risk Analysis & Selective Bypass**: Pass $(\mathcal{Q}, \boldsymbol{\tau}, \mathcal{C}, \mathcal{K}_{\mathcal{R}})$ to `AnalysisAgent`:
   - Explicitly treat **clarification requests, user confirmation requests for sensitive ops, and refusals** as safe behavior to prevent over-flagging.
   - Output structured JSON: identified risk category $\mathcal{R}$, whether $\mathcal{R}$ is a `new_risks` category not yet in $\mathcal{K}_{\mathcal{R}}$, and a binary gating flag $z \in \{0, 1\}$ (`need_tools`).
   - **Selective Bypass ($z = 0$)**: If the interaction is clearly benign or requires no programmatic check, skip tool generation/fusion (`>39%` of samples complete in `0–4` LLM calls) and proceed directly to Stage 4 action verification.
3. **Targeted Guardrail Tool Generation ($z = 1$)**: Generate an executable Python guardrail function $\mathcal{G} = f_{\text{gen}}(\mathcal{Q}, \boldsymbol{\tau}, \mathcal{C}, \mathcal{R})$ with signature:
   ```python
   def guardrail_tool(query: str, action: str) -> bool:
       """Return True if safety/security risk is detected, False if safe."""
   ```
   Encourage deterministic inspection of `action` parameters (e.g., input normalization stripping control/hex/HTML escapes, `ast.parse` inspection of inline code for dangerous imports/calls, path/destination regex validation).

### Stage 2: Two-Stage Hierarchical Retrieval and Evolutionary Fusion (`FusionAgent`)

Do not append redundant one-off scripts to $\mathcal{K}_{\mathcal{G}}$. Instead, inherit and expand existing tools:

1. **Stage 2a — Category Filtering**: Filter $\mathcal{K}_{\mathcal{G}}$ by the identified risk category:
   $$\mathcal{M}_{\mathcal{R}} = \{T_i \in \mathcal{K}_{\mathcal{G}} \mid R_i = \mathcal{R}\}$$
2. **Stage 2b — Semantic Logic Matching**: If $\mathcal{M}_{\mathcal{R}} \neq \varnothing$, ask `FusionAgent` ($f_{\text{match}}(\mathcal{M}_{\mathcal{R}}, \mathcal{G})$) whether any existing tool shares compatible detection logic ($m \in \{0, 1\}$, returning $T_{\text{sim}}$).
3. **Stage 2c — Evolutionary Fusion**:
   - If $m = 1$: Fuse $\mathcal{G}$ and $T_{\text{sim}}$ into an evolved tool $\mathcal{G}' = f_{\text{fuse}}(\mathcal{G}, T_{\text{sim}}, \mathcal{R})$ that generalizes both tools' normalization, pattern sets, and AST/parameter checks while keeping the `(query: str, action: str) -> bool` contract.
   - If $m = 0$: Set $\mathcal{G}' \leftarrow \mathcal{G}$ as a new candidate tool.

### Stage 3: Sandboxed Execution and Independent 10-CWE Audit (`ExecutorAgent` + `AuditorAgent`)

Never trust a newly generated or fused guardrail tool (`\mathcal{G}'`) without isolated execution and independent code auditing:

1. **Isolated Sandbox Execution (`ExecutorAgent`)**: Run both the evolved guardrail tool $\mathcal{G}'(\mathcal{Q}, \boldsymbol{\tau})$ and the simulated/sandboxed agent action $\boldsymbol{\tau}$ inside an isolated Docker container (or LLM-simulated state sandbox when containers are unavailable) to collect deterministic execution evidence $(\mathcal{E}_{\mathcal{G}'}, \mathcal{E}_{\boldsymbol{\tau}})$.
2. **Independent 10-CWE Vulnerability Audit (`AuditorAgent`)**: Have an independent `AuditorAgent` inspect the code of $\mathcal{G}'$ and its execution trace $\mathcal{E}_{\mathcal{G}'}$ specifically for **Vulnerable Guardrail Tool (`VGT`)** flaws across 10 CWE categories:
   1. Out-of-bounds writes
   2. Type obfuscation (accessing resources using incompatible types)
   3. OS command injection (improper handling of special elements in OS commands)
   4. SQL injection
   5. Instruction / prompt injection inside the tool
   6. Lack of authentication for critical functions
   7. Authorization bypass via user-controlled keys
   8. Open URL redirection to untrusted websites
   9. Sensitive information inserted into log files (`CWE-532`)
   10. Plaintext storage of sensitive information
   Also verify regex syntax validity (e.g., unescaped slashes) and null/type safety on `query` and `action`. Output binary audit verdict $D \in \{0, 1\}$ and vulnerability report $\mathcal{V}$.

### Stage 4: Iterative Repair, Decoupled Verdict, and Intent-Preserving Replanning

1. **Bounded Audit-Repair Loop (`\le 3` Rounds)**:
   - If the tool fails the audit ($D = 0$), run up to 3 iterations of targeted repair $\mathcal{G}'' = f_{\text{repair}}(\mathcal{G}', \mathcal{V})$ followed by re-auditing `(D, \mathcal{V}) = \text{AuditTool}(\mathcal{G}'')$.
   - **Strict Admission Gate**: Admit $\mathcal{G}'$ into the lifelong library $\mathcal{K}_{\mathcal{G}}$ **if and only if** $D = 1$. If $D = 0$ after 3 repair rounds, discard the tool so flawed code never contaminates future tasks. If $\mathcal{R}$ is a new risk category, add $\mathcal{R}$ to $\mathcal{K}_{\mathcal{R}}$.
2. **Decoupled Final Safety Verdict**: Synthesize $(\mathcal{Q}, \boldsymbol{\tau}, \mathcal{G}', \mathcal{E}_{\mathcal{G}'}, \mathcal{E}_{\boldsymbol{\tau}})$ into the final decision $y \in \{\text{safe}, \text{unsafe}\}$, instructing the decision step to avoid over-protection when a request has already passed the approved guardrail tool.
3. **Intent-Preserving Action Replanning (`RevisionAgent`)**: When $y = \text{unsafe}$, invoke `RevisionAgent` ($\tilde{\boldsymbol{\tau}} = f_{\text{revise}}(\mathcal{Q}, \boldsymbol{\tau}, \mathcal{C}, \mathcal{R})$) to rewrite the action sequence $\boldsymbol{\tau} \to \tilde{\boldsymbol{\tau}}$ so that the hazardous operation or obstacle is removed while fulfilling the user's underlying benign goal (e.g., clearing an obstacle from a robotic path before moving a tool, or replacing an unsafe physical placement with a safe surface).
