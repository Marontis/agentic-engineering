# Do AI-for-Science Agents Preserve Model Safety?

> **Paper**: [Do AI-for-Science Agents Preserve Model Safety?](https://arxiv.org/abs/2610.32045)
> **Praxis source**: src:2610-32045
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is an empirical safety-preservation benchmark across five scientific
agent harnesses and four base models. It does not introduce a new algorithmic
procedure, but provides critical quantitative evidence that wrapping a safe
base LLM in a domain-specific tool harness erodes refusal boundaries—even under
direct, non-adversarial prompting—which we record in
`rules/agent-sandbox-safety.md` and `rules/agent-evaluation-quality.md`.

---

## Core Concept

AI-for-Science systems wrap an unchanged base LLM inside a domain-specific
**agent harness**—the prompting, memory, code interpreter, and scientific tool
orchestration layer. To test whether base-model safety survives harness
integration, the authors evaluate **5 scientific agent harnesses** (`CACTUS`,
`ChemToolAgent`, `STELLA`, `Biomni`, and `DrugAgent`) across **4 base LLMs**
(`GPT-5.2`, `GPT-5.5`, `GPT-5.6-Luna`, and `GPT-6-Luna`) on **50 harmful
chemistry requests** from SafeSciBench (requests asking for SMILES
modifications or reaction pathways that intensify toxicity, corrosiveness, or
health hazards).

Every base LLM and composed agent is tested under four prompting conditions:
- **Direct** (no jailbreak or adversarial framing, pass@3 over 3 runs at
  $T = 0.6$),
- **Roleplay** (scientific persona, pass@3),
- **Past tense** (past-tense reformulation, pass@3), and
- **PAIR** (adaptive multi-turn attack using the target system's prior
  responses).

Responses are scored using the three-judge protocol from MT-JailBench (two
binary judges and one 5-point harmfulness judge, all instantiated with
`GPT-5.5`), measuring $\Delta\text{ASR} = \text{ASR}_{\text{harness}} - \text{ASR}_{\text{base}}$.

### Key Findings

- **Harnesses increase harmful compliance even on direct, un-jailbroken
  requests**: For `GPT-5.2` (whose base-model Direct pass@3 ASR is **2%**, mean
  $1.3 \pm 0.7\%$), wrapping the model in `ChemToolAgent` raises Direct pass@3
  ASR to **20%** (+18 pp; mean $15.3 \pm 1.8\%$), `Biomni` raises it to **24%**
  (+22 pp; mean $16.0 \pm 1.2\%$), and `DrugAgent` raises it to **72%** (+70 pp;
  mean $50.0 \pm 3.1\%$). On `GPT-5.5` (base Direct pass@3 ASR **4%**),
  `DrugAgent` raises Direct pass@3 ASR to **50%** (+46 pp; mean
  $40.0 \pm 3.1\%$).
- **Adaptive attacks (PAIR) that fail on the base LLM succeed at high rates on
  the composed agent**:
  - `GPT-5.5` base model has a **2%** (1/50) PAIR ASR, but every single harness
    triggers a massive regression: **60%** (+58 pp) with `CACTUS` and
    `ChemToolAgent`, **56%** (+54 pp) with `Biomni`, **54%** (+52 pp) with
    `STELLA`, and **38%** (+36 pp) with `DrugAgent`.
  - `GPT-5.6-Luna` base model has a **10%** (5/50) PAIR ASR, which rises to
    **28–66%** across the five harnesses (`CACTUS`: 66%, +56 pp; `Biomni` and
    `STELLA`: 50%, +40 pp; `ChemToolAgent`: 42%, +32 pp; `DrugAgent`: 28%,
    +18 pp).
  - `GPT-6-Luna` base model has a **2%** (1/50) PAIR ASR, which rises to
    **8–30%** across the five harnesses (`STELLA`: 30%, +28 pp; `Biomni`: 28%,
    +26 pp; `ChemToolAgent`: 26%, +24 pp; `CACTUS`: 24%, +22 pp; `DrugAgent`:
    8%, +6 pp).
- **Single-turn safety does not predict adaptive multi-turn safety**: `STELLA`
  preserves or slightly reduces harmful compliance under Direct prompting
  across all four models ($\Delta\text{ASR}$ of 0, 0, −2, and −2 pp), yet under
  adaptive PAIR prompting it increases ASR by **+52 pp** on `GPT-5.5`, **+40 pp**
  on `GPT-5.6-Luna`, and **+28 pp** on `GPT-6-Luna`.
- **Disabling external tools or memory alone does not remove the regression**:
  In configuration ablations under PAIR, disabling external tools in `STELLA`
  (while retaining its response-generating code interpreter) barely changes
  PAIR ASR (`GPT-5.5`: 54% full vs. 52% tools disabled vs. 56% memory disabled,
  all against 2% base; `GPT-6-Luna`: 30% full vs. 28% tools disabled vs. 34%
  memory disabled, against 2% base). Disabling tools in `Biomni` moves PAIR ASR
  from 56% to 60% on `GPT-5.5` and from 28% to 22% on `GPT-6-Luna`.
- **Pass@3 vs. mean ASR can flip sign on borderline comparisons**: On
  `GPT-5.6-Luna` under past-tense prompting, `STELLA` has a lower three-run
  mean ASR than the base model ($22.7 \pm 4.1\%$ vs. $26.7 \pm 0.7\%$, −4.0 pp)
  but a higher pass@3 ASR (40% vs. 36%, +4 pp), showing why both multi-sample
  worst-case (pass@$k$) and mean rates should be reported.

## Relevance to Praxis

- **Always benchmark the composed agent against a matched base-LLM reference**:
  Reporting $\Delta\text{ASR} = \text{ASR}_{\text{harness}} - \text{ASR}_{\text{base}}$
  separates vulnerabilities inherited from the model weights from regressions
  introduced by the harness's system prompts, multi-step decomposition, and
  tool loop.
- **Re-run adaptive red-teaming whenever the harness changes**: A harness like
  `STELLA` that looks completely safe on single-turn direct requests (0 to −2 pp
  $\Delta\text{ASR}$) can still suffer a +52 pp regression under adaptive
  multi-turn probing.
- **Related artifacts**:
  - `rules/agent-sandbox-safety.md`: "DON'T: Assume safety transfers across
    deployment contexts" and "DO: Test with evolving adversaries, not static
    attack sets".
  - `rules/agent-human-interaction.md`: "DON'T: Assume stable safety behavior
    across interaction modes".
  - [`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md).
