# Persuasion from Within: Model-Based Insider Attacks in Multi-Agent LLM Debate and Consensus (Defensive Lessons)

> **Source**: [arXiv:2611.28660](https://arxiv.org/abs/2611.28660) — Xuancheng Ju, Yanchao Sun, Furong Hu, Zizhan Zheng (Tulane University, 2026)  
> **Praxis Source ID**: `src:2611-28660v1`  
> **License**: CC BY-NC-SA 4.0  
> **Repository**: Not publicly released at publication

## Why Not a Skill?

Per [`AGENTS.md`](../AGENTS.md) guidance on offensive multi-agent attack papers, this artifact is scoped strictly to defensive resilience, failure-mode characterization, and hardening lessons (omitting attacker persuasion prompt templates and target-manipulation exemplars). Roughly 85% of the manuscript develops a 4-stage model-based insider attack pipeline (generative world model + offline DPO + Turn-PPO + rollouts), while its constructive defense—clean-consistency DPO adversarial training (`Section 3.5`, `Appendix I.2`)—is evaluated on a single backbone (`Qwen3.5-9B`) on `MMLU-Pro` against non-adaptive insiders (`Section 6`). Its primary value for agent engineers lies in documenting why message-level Byzantine filters, confidence/semantic filters, transcript LLM monitors, prompt paraphrasing, and extra deliberation rounds fail against multi-turn belief steering, and how consistency-anchored DPO and non-centralized graph topologies bound insider blast radius.

## Threat Model & Why Turn-Local Defenses Fail

Consider a $T$-round multi-agent system with $B$ honest LLM agents and a single compromised insider ($F = 1$, $N = B + 1$) communicating in natural language without access to honest agents' weights, hidden states, or private scratchpads:
- **Numerical Consensus**: $3$ `Qwen3.5-9B` benign agents with heterogeneous traits (`stubborn`, `suggestible`, `neutral`) + $1$ insider (`Qwen3-4B` policy + `Qwen3.5-4B` generative world model) negotiating integers in $\{0, \dots, 20\}$ over $T = 10$ rounds (`5 seeds × 200 episodes`).
- **Multi-Agent Debate (`MMLU-Pro`)**: $3$ `Qwen3.5-9B` benign agents (`1 suggestible`, `2 neutral`) + $1$ insider debating $10$-way `MMLU-Pro` questions over $T = 3$ rounds (`400` test questions $\times 3$ seeds = `1,200` debates).

Unlike static prompt-based attackers (`Prompt-based`, `Amayuelas-BON`, `Kraidia-BON`, `ToMAP`) or high-episode model-free RL (`P-RL`, `~52k` online episodes), an insider equipped with a **generative world model** trained on logged clean debates (`Qwen3.5-4B` fine-tuned on `138,336` responses from `11,528` debates—with `Table 9` showing **`3,000` logged debates** already matches full-data prediction at `.825` vs. `.827` Round-2+ accuracy and `+.003` planning delta, plus `2,882` [`~3k`] online refinement debates, `~17x` fewer online episodes than `P-RL`) predicts both peer answer switches (**`.655` accuracy on switch turns** vs. `.676` stochasticity ceiling, compared with `.454` for `DCM` latent-belief tracking, `.461` for count-based MLPs, and `.266` for previous-majority baselines; `Table 5`) and peer behavioral personas directly from dialogue history (**`.66` Round-2 and `.71` Round-4+ accuracy with shuffled seat IDs and hidden persona prompts** vs. `.69` and `.72` with known personas; `Table 8`).

Because the insider generates context-plausible rationales and **nudges numeric proposals or option rankings gradually within honest peers' neighborhood bands** before exploiting disagreement, three standard defense classes break down:

| Defense Mechanism | Consensus Rate (`CR`, Clean `.458 ± .089`) | `MMLU-Pro` Benign `Acc.` (Clean `.689 ± .002`) | Primary Failure Mechanism |
|:---|:---|:---|:---|
| **Undefended vs. Model-Based Insider** | **`.140 ± .042`** (vs. `.232–.325` baselines) | **`.254 ± .009`** (vs. `.428 ± .012` `P-RL`, `.535–.601` static/DPO) | Gradual wedge formation across stubborn vs. suggestible peers (`Tables 1–2`). *(Note: §1 prose rounds clean/attacked figures to `46%`/`14%` and `69%`/`25%` vs. `43%` `P-RL`.)* |
| **`W-MSR` ($F = 1$ trimmed outlier filter)** | `.233 ± .036` (Clean `.458 ± .089`) | `.461 ± .007` (Clean `.684 ± .003`) | Drops extreme scalar/vote outliers per round, but the insider stays inside the honest interval (`|x_atk - \bar{x}_hon| ≈ 3.1`) so its messages survive trimming (`Tables 1, 3`). |
| **`CP-WBFT` (logit-probability confidence gate)** | **`.138 ± .007`** (Clean `.715 ± .019`) | `.323 ± .023` (Clean `.679 ± .003`) | Raises clean consensus to `.715`, yet offers **zero protection** against the insider because persuasive rationales carry high token-level confidence (`Tables 1, 3`). |
| **`SAC` ($F = 1$ self-anchored semantic filter)** | **`.137 ± .017`** (**Clean drops to `.251 ± .014`!**) | `.368 ± .010` (Clean `.683 ± .005`) | Filters semantically distant replies; the insider mimics task-relevant reasoning to pass the filter, while `SAC` severely suppresses legitimate cross-agent compromise on clean consensus (`Tables 1, 3`). |
| **Transcript LLM Monitor (`Qwen3.5-9B`)** | — | **`13.0%` (`.130 ± .005`)** detection (**`68.5%`** undetected success) | Flags some honest agent in **`20.5%`** of *clean* debates yet flags the model-based insider in only **`13.0%`** (*below the clean false-alarm rate!*), vs. `58.7%` (`.587 ± .023`) detection on `P-RL` (`Table 2`, `§5.2`). |
| **System-Prompt Paraphrasing (`R1`, `R2`)** | — | `.289 ± .006` (`R1`), `.276 ± .011` (`R2`) | Retains **`89%` and `94%`** of the full accuracy drop without retraining (`Table 17`). |
| **Scaling Population ($B = 4..8$) & Horizon ($H = 10..50$)** | `62%–66%` still unconverged at $H = 50$ (vs. `35%–48%` clean) | — | Adds `+9.10` to `+13.96` rounds to mean convergence time without diluting persistent wedge-splitting (`Table 15`). |

*(Manuscript arithmetic note: in `§5.4` vs. `Appendix J` `Table 20`, single-sample policy progression moves `.610 ± .010` [Base] $\to$ `.571` [+DPO init] $\to$ `.454` [+Turn-PPO] $\to$ `.319 ± .008` [+DPO refinement] $\to$ `.254 ± .009` [+WM planning, $M=8$]; `§5.4` prints rounded deltas `0.290` and `0.066` where exact subtraction of the 3-decimal table means gives `0.610 - 0.319 = 0.291` and `0.319 - 0.254 = 0.065`.)*

## Constructive Defensive Lessons

### 1. Clean-Consistency DPO Adversarial Training (No Ground-Truth Labels Required)
Unlike message filters that inspect incoming peer text in isolation, **adversarial consistency training (`AT`, `Section 3.5`, `Appendix I.2`)** hardens the benign debaters' update dynamics without requiring ground-truth task labels:
1. Run clean baseline debates alongside insider-attacked trajectories on the same unlabeled task contexts.
2. At attacked debate contexts $s_t$ where a benign agent changed its answer relative to its clean-debate answer $y_{\text{clean}}$ at the same round, sample $K = 4$ candidate replies (expanding by up to $+8$ samples if needed).
3. Partition replies into **consistent** ($y^+$, matching $y_{\text{clean}}$) vs. **swayed** ($y^-$, matching a wrong/shifted option) and fine-tune the benign backbone via LoRA (`r = 16`, $\alpha = 32$, $\beta = 0.1$, learning rate $5 \times 10^{-5}$, `2` epochs over `5,652` train / `644` held-out pairs).

On `MMLU-Pro` (`Table 3`), consistency-anchored DPO:
- **Improves clean unattacked debate accuracy** from `.689 ± .002` to **`.713 ± .005`** (`+2.4 pp`), avoiding the clean-consensus penalty of `SAC`;
- **Restores accuracy against the full model-based insider** (trained on an earlier checkpoint) from `.254 ± .009` to **`.688 ± .017`** (`-0.1 pp` below clean baseline);
- **Transfers zero-shot against unseen model-free `P-RL` insiders**, lifting defended accuracy from `.428 ± .012` to **`.681 ± .003`**.

### 2. Graph Topology Isolation & Hub Hardening
Across $6$ communication topologies (`Table 16`, $B = 5$ benign agents, $H = 20$ rounds), insider impact scales directly with topological centrality:
- **High-centrality catastrophe**: Placing a compromised agent at `Star-center` collapses consensus from `.241` to **`.018`** (`-92.5%` relative), and `Complete` all-to-all broadcast drops `.384` to **`.177`**.
- **Peripheral neutralization**: Restricting untrusted/external participants to degree-1 leaf positions neutralizes persuasion completely—at `Path-end`, consensus stays at **`.042` vs. `.026` clean**, and at **`Star-leaf` mediated by a low-sycophancy (`stubborn`) benign hub**, consensus reaches **`.881` vs. `.804` clean (`+7.7 pp`)** because the hub filters peripheral perturbations before relaying to the remaining leaves.

### 3. Cross-Family Backbone Diversity Limits Zero-Shot Transfer
Evaluating the `Qwen3.5-9B`-trained consensus attacker zero-shot across $6$ unseen target LLMs (`Table 13`, $T = 10$, `5 seeds × 200 episodes`) shows strong transfer on `Qwen2.5-32B` (`.955 -> .207`), `Llama-3.1-8B` (`.766 -> .269`), `Mistral-Small-24B` (`.921 -> .288`), and `Mistral-7B` (`.936 -> .473`), parity with prompt attacks on `Qwen2.5-14B` (`.968 -> .527` vs. `.498`), **but sharp degradation on `Gemma-3-12B-IT` (`.941 -> .753`, retaining `80%` of clean consensus)**—confirming that cross-family model diversity (`Gemma` + `Qwen` + `Llama`) disrupts single-surrogate world-model calibration. Across unseen debate domains on the same `Qwen3.5-9B` target, however, zero-shot transfer remains severe (`Table 14`: `TruthfulQA-MC1` `.738 -> .256`, `GPQA-Diamond` `.577 -> .201`, `LogiQA 2.0` `.748 -> .223`, `MedQA` `.840 -> .337`).

## Key Limitations to Keep in Scope

- **Non-adaptive defense evaluation (`Section 6`)**: The insider policy and world model were **not retrained** against `W-MSR`, `CP-WBFT`, `SAC`, or consistency-anchored DPO (`AT`); white-box co-evolution against `AT`-hardened debaters remains an open question.
- **Structured action spaces**: Both benchmarks instantiate discrete final choices (`{0..20}` integers or `A–J` multiple-choice labels) rather than open-ended code diffs or multi-step tool trajectories (where [`similarity-consensus-subtask-aggregation`](../skills/similarity-consensus-subtask-aggregation/SKILL.md) governs non-interactive parallel worker outputs and [`multi-layer-compromise-filtering-and-traceback`](../skills/multi-layer-compromise-filtering-and-traceback/SKILL.md) governs persistent multi-session tool/memory substrates).

## Related Artifacts

- **Rules**: [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md) (*"DON'T: Rely on message filters, transcript LLM monitors, or extra turns to counter learned insider persuasion; train debaters with clean-consistency DPO and leaf-hub topology"*, *"DON'T: Rely on group size or majority vote to dilute adversarial agents"*, *"DO: Aggregate untrusted parallel subtask responses via trimmed nearest-neighbor embedding consensus rather than LLM summarization or confidence scoring"*)
- **Skills**: [`debate-consensus-memory-calibration`](../skills/debate-consensus-memory-calibration/SKILL.md), [`similarity-consensus-subtask-aggregation`](../skills/similarity-consensus-subtask-aggregation/SKILL.md)
