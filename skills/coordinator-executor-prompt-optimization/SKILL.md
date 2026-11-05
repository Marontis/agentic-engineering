---
name: coordinator-executor-prompt-optimization
description: >-
  Decouple multi-agent prompt optimization into a shared team-level
  coordinator prompt and agent-specific executor prompts, using role-aligned
  meta-instructions and a sequential coordinator-first schedule so shared
  handoff and evidence rules stay consistent across agents while local
  execution instructions specialize. Derived from CEPO (arXiv:2610.34722).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Coordinator-Executor Prompt Optimization

> Source: "CEPO: A General Framework for Improving Prompt Optimization in Multi-Agent Systems" — Zhang, Liu, Wang, Yang, Li (arXiv:2610.34722v1, 2026; Praxis `src:2610-34722`)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- You are optimizing natural-language prompts in a multi-agent system (MAS) where $N \ge 2$ specialized agents collaborate sequentially or hierarchically (e.g., planner/retriever/critic/synthesizer pipelines, multi-modal text+vision+table document understanding, predictor+reflector math/code workflows, or master+grounding+vision video agents).
- Applying a standard single-agent prompt optimizer (such as PE2, ProTeGi, OPRO, or MASPO) directly to individual agent prompts causes cross-agent rule drift, contradictory handoff expectations, or prompt bloat that degrades downstream synthesis.
- End-to-end rollout failures mix system-level coordination breakdowns (premature commitment, uncertainty erasure, modality neglect, unstated conflicts between agents) with agent-local execution mistakes (extractive parsing errors, bad code/math formatting, incomplete table reading).
- You want a reusable team-level coordination protocol that can also transfer zero-shot to related tasks sharing the same multi-agent architecture.

## When NOT to Use

- The system is a single-agent pipeline ($N = 1$) with no inter-agent handoffs or shared state (on a 1-agent baseline on MMLongBench-Doc, there is no inter-agent coordination surface to decouple).
- Every agent's prompt is already frozen by external API or compliance constraints and cannot accept either a prepended coordinator block or local prompt edits.
- You have no validation set $\mathcal{D}_{\text{val}}$ or task evaluator $J(\cdot)$ to score candidate prompt updates.

---

## Procedure

### Step 1: Decouple Each Agent's Prompt into Shared Coordinator + Local Executor Components

Instead of treating each agent $A_i$'s prompt $p_i$ as a monolithic optimization target, factor the prompt space of the $N$-agent system $\mathcal{M} = \{A_1, \dots, A_N\}$ into two levels:

1. **Shared Coordinator Prompt ($p_C$)**: A single team-level prompt shared across all agents that governs *what* the system must preserve across handoffs (cross-agent consistency, uncertainty preservation, modality discipline, conflict surfacing, and evidence attribution).
2. **Agent-Specific Executor Prompts ($\{p_E^{(1)}, \dots, p_E^{(N)}\}$)**: Local role instructions for each agent $A_i$ that specify *how* that agent performs its individual subtask given its immediate inputs.
3. **Runtime Composition**: Assemble the effective prompt $\tilde{p}_i$ for agent $A_i$ by prepending the shared coordinator prompt to the agent's local executor prompt:
   $$\tilde{p}_i = p_C \oplus p_E^{(i)}$$
4. **Cold-Start Initialization**: If the existing MAS only defines local role prompts $\{p_E^{(1,0)}, \dots, p_E^{(N,0)}\}$ and has no coordinator prompt, synthesize a concise initial coordinator prompt $p_C^{(0)}$ from the agent descriptions before starting optimization, keeping it focused on shared communication and evidence-handling norms.

### Step 2: Configure Role-Aligned Optimization Meta-Instructions ($\Phi_C$ vs. $\Phi_E$)

Do not use the same reflection/mutation meta-prompt for both levels. Equip the base prompt optimizer $\mathcal{O}$ (e.g., PE2, ProTeGi, OPRO, or MASPO) with level-specific meta-instructions:

1. **Coordinator Meta-Instruction ($\Phi_C$ — "What-To" Team Rules)**:
   - **Failure Attribution Filter**: Before proposing edits to $p_C$, classify every rollout failure on $\mathcal{D}_{\text{train}}$ into four buckets:
     1. *Target-actionable coordination failures*: Cross-agent handoff loss, modality neglect (e.g., text vs. image disagreement), premature commitment when evidence is partial, or silent overwriting of upstream uncertainty.
     2. *Downstream-only failures*: Errors introduced solely by a single terminal formatter after valid upstream handoffs.
     3. *Other-agent-only local execution errors*: Calculation or syntax errors inside one agent's local step.
     4. *Evidence-missing cases*: Upstream retrieval failed to fetch the required page/frame/context; do not rewrite coordination rules to hallucinate missing evidence.
   - **Content Scope**: Update $p_C$ *only* for bucket (1), expressing high-level behavioral norms across six coordination dimensions: uncertainty preservation, modality discipline, evidence handling, handoff clarity, conflict surfacing, and final synthesis.
   - **Length & Format Guardrails**: Enforce a strict length cap of **$< 600$ tokens** on $p_C$ so it does not crowd out local role instructions, and forbid self-referential brevity rules (e.g., do not allow the optimizer to insert meta-text about keeping the prompt short).

2. **Executor Meta-Instruction ($\Phi_E$ — "How-To" Local Execution)**:
   - **Input/Output Isolation**: When optimizing agent $A_i$'s executor prompt $p_E^{(i)}$, inspect **only** target agent $A_i$'s direct input and direct output from the rollout trace, conditioned on the fixed coordinator prompt $p_C^\star$. Do not condition $p_E^{(i)}$ updates on hidden upstream or downstream agent traces that $A_i$ cannot observe at runtime.
   - **Failure Attribution Filter**: Separate target-agent-actionable execution errors (missed fields in $A_i$'s input, malformed intermediate output, failure to follow $p_C^\star$ on $A_i$'s modality) from upstream retrieval misses or downstream synthesis errors.
   - **Structured Operational Format**: Organize each executor prompt $p_E^{(i)}$ into three explicit blocks:
     1. *Task statement* (the agent's exact local role and output contract),
     2. *Core behavior* (domain- and modality-specific constraints), and
     3. *Procedure* (concrete step-by-step operational instructions).

### Step 3: Run Phase 1 — Coordinator-First Optimization

Optimize the shared coordinator prompt $p_C$ first while holding all initial executor prompts $\{p_E^{(1,0)}, \dots, p_E^{(N,0)}\}$ fixed:

1. Evaluate the initial configuration $(p_C^{(0)}, \{p_E^{(i,0)}\}_{i=1}^N)$ on $\mathcal{D}_{\text{val}}$ to establish the baseline score $J_0$.
2. For iteration $t = 1, \dots, T_C$ (typically $T_C = 3$ or $4$):
   - Run the MAS on a minibatch from $\mathcal{D}_{\text{train}}$ and collect multi-agent trajectories and failure examples $\mathcal{F}_{\text{train}}^{(t)}$.
   - Invoke the base optimizer with the coordinator meta-instruction:
     $$p_C^{(t)} = \mathcal{O}\!\left(p_C^{(t-1)},\, \mathcal{F}_{\text{train}}^{(t)},\, \Phi_C\right)$$
   - Evaluate $(p_C^{(t)}, \{p_E^{(i,0)}\}_{i=1}^N)$ on $\mathcal{D}_{\text{val}}$.
3. Select the best-performing coordinator prompt over the validation trajectory:
   $$p_C^\star = \arg\max_{t \in \{0, \dots, T_C\}} J\!\left(p_C^{(t)}, \{p_E^{(i,0)}\}_{i=1}^N;\, \mathcal{D}_{\text{val}}\right)$$

### Step 4: Select High-Leverage Target Executors ($\mathcal{I}$) and Run Phase 2 — Executor Optimization

With $p_C^\star$ frozen, optimize the executor prompts for a selected subset of target agents $\mathcal{I} \subseteq \{1, \dots, N\}$:

1. **Select Target Executor Subset $\mathcal{I}$**:
   - In multi-agent pipelines with a primary bottlenecks (such as MDocAgent's `GENERAL` initial-answer synthesis agent, which integrates multi-modal context before critic review), optimizing the single highest-leverage executor ($|\mathcal{I}| = 1$) often outperforms optimizing all executors sequentially, because sequential changes across many tightly coupled executors can compound distribution shifts (on MMLongBench-Doc, $|\mathcal{I}| = 1$ with `GENERAL` achieves **61.0%**, whereas expanding $|\mathcal{I}|$ to $2, 3, 4, 5$ agents yields $59.7\%, 60.0\%, 57.5\%, 56.9\%$).
   - In compact 2-agent loops (such as MASPO's Predictor + Reflector on math and code), include both agents in $\mathcal{I}$ and alternate short update blocks (e.g., 2 Predictor iterations followed by 2 Reflector iterations).
2. **Optimize Each Selected Executor $i \in \mathcal{I}$**:
   - For iteration $t = 1, \dots, T_E$ (typically $T_E = 3$ or $4$):
     - Collect target-agent input/output failure traces $\mathcal{F}_{i,\text{train}}^{(t)}$ under $(p_C^\star, p_E^{(i,t-1)})$.
     - Generate a candidate executor prompt using the executor meta-instruction:
       $$p_E^{(i,t)} = \mathcal{O}\!\left(p_E^{(i,t-1)},\, \mathcal{F}_{i,\text{train}}^{(t)},\, \Phi_E,\, p_C^\star\right)$$
     - Score $(p_C^\star, p_E^{(i,t)})$ on $\mathcal{D}_{\text{val}}$.
   - Keep the validation-best executor prompt $p_E^{(i,\star)} = \arg\max_{t \in \{0, \dots, T_E\}} J(p_C^\star, p_E^{(i,t)};\, \mathcal{D}_{\text{val}})$.

### Step 5: Gate Every Candidate Prompt Update Before Promotion

Every candidate coordinator prompt $p_C^{(t)}$ and executor prompt $p_E^{(i,t)}$ is a self-modification of the agent harness and must defer to **"DO: Pass every self-modification through one acceptance gate"** in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md):

1. Retain the previous best prompt checkpoint $(p_C^{(0)}, \{p_E^{(i,0)}\})$ in versioned storage before applying any update.
2. Promote a candidate $(p_C^\star, \{p_E^{(i,\star)}\})$ only if it improves validation performance $J(\cdot; \mathcal{D}_{\text{val}})$ without violating the $< 600$-token coordinator budget or regressing parseability/handoff format compliance.
3. If Phase 2 executor updates fail to beat the Phase 1 coordinator-only checkpoint $(p_C^\star, \{p_E^{(i,0)}\})$ on $\mathcal{D}_{\text{val}}$, roll back the executor edits and retain $(p_C^\star, \{p_E^{(i,0)}\})$ (which is guaranteed by $\arg\max_{t \in \{0, \dots, T_E\}}$ inclusion of $t = 0$).

---

## Environment & Model Caveats

- **Consistent Gains Across 11 Benchmarks, 4 Domains, and 4 Base Optimizers**:
  - *Document Understanding (5 benchmarks: MMLongBench-Doc, LongDocURL, PaperTab, PaperText, FetaTab; 10/10/80 document-level train/val/test split; GPT-5.4 optimizer with $T_C = T_E = 3$; GPT-5-mini judge)*:
    - On **MDocAgent** (5 agents: `GENERAL`, `CRITIC`, `TEXT`, `IMAGE`, `SUM`; Qwen-3.5 4B backbone), baseline accuracy is $54.1 / 74.9 / 46.3 / 72.1 / 78.8$ (**65.2** avg); vanilla PE2 reaches $57.9 / 74.4 / 48.1 / 71.4 / 77.8$; **PE2 + CEPO** reaches **$61.0\ (+6.9) / 75.4\ (+0.5) / 53.7\ (+7.4) / 76.4\ (+4.3) / 80.8\ (+2.0)$** (**69.5** avg, **+4.3** over baseline).
    - On **DocAgent** (3 agents: actor, reviewer, reflector; GPT-5-mini backbone), baseline accuracy is $59.5 / 72.9 / 60.0 / 75.6 / 82.0$ (**70.0** avg); **PE2 + CEPO** reaches **$67.4\ (+7.9) / 73.2\ (+0.3) / 62.2\ (+2.2) / 78.3\ (+2.7) / 82.6\ (+0.6)$** (**72.7** avg, **+2.7** over baseline).
    - Across **PE2, ProTeGi, and OPRO** on MDocAgent (Table 8), adding CEPO improves all 15 optimizer–benchmark combinations by **+0.6 to +6.5 points** over the corresponding vanilla optimizer (ProTeGi: $55.5 / 73.5 / 46.6 / 72.7 / 78.4 \to$ ProTeGi + CEPO: $57.9 / 75.4 / 53.1 / 76.7 / 79.2$; OPRO: $57.3 / 73.2 / 46.3 / 70.9 / 78.9 \to$ OPRO + CEPO: $60.4 / 75.2 / 46.9 / 73.0 / 80.0$).
  - *Math & Code Reasoning (5 benchmarks, Table 3: Qwen3-8B 2-agent Predictor+Reflector MAS, MASPO optimizer with GPT-5-mini, $T_C = 4$, $T_E = 4$ per executor)*:
    - Baseline vs. vanilla MASPO vs. **MASPO + CEPO**: AQuA ($83.47 \to 85.56 \to \mathbf{87.01}$, $+3.54$), MATH-500 ($75.10 \to 77.80 \to \mathbf{79.60}$, $+4.50$), AGIEval-MATH ($59.38 \to 61.98 \to \mathbf{62.89}$, $+3.51$), HumanEval-ET ($68.90 \to 73.78 \to \mathbf{74.39}$, $+5.49$), MBPP ($57.26 \to 65.11 \to \mathbf{65.57}$, $+8.31$). Five-benchmark average rises from $68.82$ (baseline) and $72.85$ (MASPO) to **73.89** (**+5.07** over baseline, **+1.04** over MASPO).
  - *Long-Video Understanding (Table 7: LongVideoAgent on LongTVQA+, Qwen2.5-7B master agent + GPT-5-mini grounding and vision agents, PE2 with GPT-5.4, $T_C = T_E = 3$)*:
    - Baseline **60.3** $\to$ vanilla PE2 **63.4** $\to$ **PE2 + CEPO 64.9** (**+4.6** over baseline, **+1.5** over PE2).
- **Scaling with Number of Collaborating Agents**:
  - As agent count grows from 2 to 5 on MMLongBench-Doc (Table S3), vanilla PE2 can destabilize intermediate configurations (dropping 3-agent average accuracy from $53.6$ baseline to $53.2$, and down to $47.5$ on `GENERAL+TEXT+SUM`), whereas CEPO improves every multi-agent team size and scales its gain from **+3.9** (2 agents: $53.0 \to 56.9$), **+4.1** (3 agents avg: $53.6 \to 57.7$), and **+4.5** (4 agents avg: $54.2 \to 58.7$) to **+6.9** (5 agents: $54.1 \to 61.0$).
- **Low-Budget Efficiency & Over-Optimization Ceiling**:
  - Even at a minimal budget of $T_C = 1, T_E = 1$ (2 optimizer calls, 3,120 total LLM calls), CEPO reaches **60.1%** on MMLongBench-Doc, outperforming vanilla PE2 at $T_E = 3$ ($57.9\%$, 10 optimizer calls, 5,714 LLM calls) and $T_E = 6$ ($57.4\%$, 22 optimizer calls, 11,945 LLM calls) at roughly half the compute.
  - Extending optimization beyond $T_C = 3, T_E = 3$ ($61.0\%$, 20 optimizer calls, 11,458 LLM calls) to $T_C = 4, T_E = 4$ (28 optimizer calls, 15,616 LLM calls) degrades test accuracy to **58.6%** due to validation-set overfitting on small splits.
- **Zero-Shot Coordinator Transfer**:
  - A coordinator prompt $p_C^\star$ learned on MMLongBench-Doc transfers zero-shot (without re-optimizing on target datasets) to LongDocURL ($74.8$ vs. $75.4$ in-domain), PaperTab ($49.7$ vs. $53.7$), PaperText ($73.4$ vs. $76.4$), and FetaTab ($79.4$ vs. $80.8$), raising the 4-dataset average from $68.0$ (baseline) to **69.3** (vs. $71.6$ with in-domain optimization).

---

## Failure Modes

- **Swapping or Merging Coordinator and Executor Guidance**: Applying executor-style local guidance to $p_C$ and coordinator-style team guidance to $p_E$ drops MMLongBench-Doc accuracy from **61.0%** to **57.7%** (worse than vanilla PE2's $57.9\%$). Using coordinator guidance for both ($58.1\%$) or executor guidance for both ($59.1\%$) also underperforms role-aligned guidance (**61.0%**).
- **Optimizing Executors Before the Coordinator**: Running sequential Executor-First ($60.7\%$) or alternating Executor-First ($58.2\%$) underperforms Sequential Coordinator-First (**61.0%**) and Alternating Coordinator-First ($60.1\%$), because executors tuned before $p_C$ stabilizes adapt to inconsistent handoff assumptions that are later invalidated.
- **Prompt-Length Inflation Without Structural Separation**: Simply making single-level PE2 prompts as long as CEPO's combined prompt ($1,410$ tokens vs. CEPO's $1,408$ tokens, compared to $226$ baseline and $631$ standard PE2) drops MMLongBench-Doc accuracy from $57.9\%$ to **54.0%** (below the $54.1\%$ unoptimized baseline).
- **Sequential Drift Across Too Many Executors**: Optimizing every agent's executor prompt sequentially in a 5-agent pipeline without freezing low-leverage roles degrades MMLongBench-Doc accuracy from **61.0%** ($|\mathcal{I}| = 1$) to **56.9%** ($|\mathcal{I}| = 5$).

---

## Cross-References

- **Related Rules**:
  - [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — *"DO: Pass every self-modification through one acceptance gate"* and *"DO: Diagnose structural error patterns across the full validation set before mutating prompts"*
  - [`../../rules/multi-agent-coordination.md`](../../rules/multi-agent-coordination.md) — Multi-agent handoff protocols, role delegation, and coordination failure recovery
- **Related Skills**:
  - [`../intervention-guided-mas-prompt-optimization/SKILL.md`](../intervention-guided-mas-prompt-optimization/SKILL.md) — Counterfactual intervention-guided blame assignment for multi-agent prompt optimization (AgentGrad)
  - [`../error-structured-prompt-optimization/SKILL.md`](../error-structured-prompt-optimization/SKILL.md) — Diagnose-Propose-Select single-agent prompt optimization (ESPO)
  - [`../targeted-failure-attribution/SKILL.md`](../targeted-failure-attribution/SKILL.md) — Isolating the decisive error agent and step in multi-agent trajectories (DoCtOR)
