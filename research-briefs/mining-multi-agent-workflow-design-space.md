# Mining the Design Space of Multi-Agent Workflows

> **Paper**: [Mining the Design Space of Multi-Agent Workflows](https://arxiv.org/abs/2610.31709)
> **Praxis source**: src:2610-31709
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is an empirical design-space mining study over 28,568 multi-agent
workflows that establishes three statistical design principles (avoiding
uncoordinated `Star`-first fan-out, preferring persistent `SharedMemory`
blackboards over conversational `Debate`, and investing in sub-topological
prompt specificity and placeholder routing). These quantitative decision
criteria directly govern workflow architecture and are captured as rules and
evidence in `rules/multi-agent-coordination.md` rather than a standalone
procedure.

---

## Core Concept

Manual multi-agent studies typically compare 3–5 hand-crafted topologies with
fixed prompts, while automated workflow optimizers (like AFlow or ADAS) discard
over 95% of evaluated architectures to return a single task-specific winner
$W^\star$. To turn discarded search trajectories into a statistical testbed,
the authors build a two-phase pipeline:

1. **Full-Trace Sampling Phase**: Repurposes the MCTS-based AFlow optimizer
   (`GPT-5.4` optimizer at $T = 0$; worker and hub calls using `GPT-5.4-mini`
   and `GPT-5.4-nano`, capped at $\le 20$ LLM calls per workflow) over **6
   composable operator primitives**:
   - `Sequential` (47.2% of corpus workflows): single-agent linear chaining,
   - `Star` (44.5%): isolated parallel workers followed by one-shot aggregation,
   - `Debate` (22.3%): all-to-all peer proposal exchange and revision,
   - `SharedMemory` (20.8%): blackboard-style sequential reading and appending
     to one persistent shared document,
   - `DebateWithModerator` (11.8%): multi-round debate with a moderator hub,
   - `StarWithCoordinator` (8.8%): multi-round fan-out with a coordinator hub.
   Retaining all $N = 20$ MCTS rounds across $K = 5$ runs on **26
   deterministically verified, tool-free Enigmata reasoning tasks** (20
   instances per bundle, 1,701 completed search traces) yields **28,568
   executable workflow–task–performance triplets** (`graph.py` + `prompt.py` +
   exact verifier score and cost).
2. **Sandboxed Analysis Phase**: Partitions the corpus strictly at the **AFlow
   search level** into train (69.4%, $n = 19,822$), validation (15.0%), and
   held-out test (15.6%, $n = 4,468$) splits inside a leakage-controlled
   sandbox that strips search hashes and MCTS round indices. Across **300
   AutoResearch feature-mining trials** optimizing an $L_0$-penalized
   validation objective $\mathcal{F}(\phi, \psi, \kappa) = R^2_{D_{\text{val}}} - \lambda \|\phi\|_0$,
   70 candidate contrasts are generated and tested on the 13 predictable
   puzzles passing a pre-test LightGBM surrogate gate ($R^2 > 0.05$, Spearman
   $\rho > 0.30$ on $D_{\text{val}}$).

### Key Findings

- **Principle 1 (Entry-Point Topology): `Star`-first fan-out hurts reasoning
  ($\Delta = -0.045$)**: Workflows that begin with an isolated `Star` operator
  (parallel workers solving independently before one-shot aggregation) perform
  worse than alternative entry topologies on 7/13 train puzzles (0/13 strictly
  positive; median $\Delta = -0.036$, Wilcoxon $p_{\mathrm{W}} = 0.008$) and on
  held-out test searches (**median $\Delta = -0.045$**, $p_{\mathrm{W}} = 0.038$,
  9/12 overall sign agreement $p_{\mathrm{B}}^\cap < 0.001$, 9/10 conditional
  sign replication $p_{\mathrm{B}}^{\mathrm{tr}} = 0.011$). The penalty holds
  even when controlling for compute (`Star` $\times$ compute: test median
  $\Delta = -0.041$, $p_{\mathrm{W}} = 0.038$): uncoordinated initial fan-out
  amplifies reasoning errors that a one-shot aggregator cannot reconcile
  without peer verification.
- **Principle 2 (Communication State): Persistent `SharedMemory` outperforms
  conversational `Debate` ($\Delta = +0.135$)**: Workflows using blackboard-style
  `SharedMemory` (where workers sequentially read and append to a persistent
  written document) outperform workflows without it on 10/13 train puzzles
  (0/13 negative; median $\Delta = +0.072$, $p_{\mathrm{W}} = 0.002$) and 6/10
  held-out test puzzles (**median $\Delta = +0.135$**, $p_{\mathrm{W}} = 0.011$,
  9/10 sign agreement $p_{\mathrm{B}}^\cap < 0.001$; when used as the entry
  operator `SM 1st`, test median $\Delta = +0.143$, $p_{\mathrm{W}} = 0.030$).
  `SharedMemory` achieves the highest corpus-wide mean accuracy of all six
  operators (**0.23**, vs. **0.18** for `Debate` and **0.16** for `Star`),
  curbing lossy multi-round conversational message passing.
- **Principle 3 (Sub-Topological Prompt Structure): Prompt specificity and
  placeholder routing match macro-topology gains ($\Delta = +0.118$)**:
  Parsing `graph.py` topology features alone plateaus at validation
  $R^2 = 0.521$ (8 features), whereas jointly parsing `prompt.py` lifts
  validation $R^2$ to **0.638** (27 features). Above-median prompt template
  specificity (`mean chars` in `prompt.py`) yields positive gains on 11/13
  train puzzles (median $\Delta = +0.073$, $p_{\mathrm{W}} = 0.002$) and
  held-out test searches (**median $\Delta = +0.118$**, $p_{\mathrm{W}} = 0.002$,
  13/13 sign agreement $p_{\mathrm{B}}^\cap < 0.001$), while explicit `{name}`
  context-routing placeholders (`#placeh.`) yield train median $\Delta = +0.102$
  and held-out test median **$\Delta = +0.059$** ($p_{\mathrm{W}} = 0.003$,
  11/13 sign agreement).
- **Structured `mini`/`nano` workflows beat one-shot `GPT-5.4` on iterative
  constraint propagation**: Multi-agent compositions using only
  `GPT-5.4-mini`/`nano` lift mean accuracy over one-shot `GPT-5.4` from
  $0.100 \to 0.891$ (max $1.000$) on NaturalLanguageNavigation,
  $0.033 \to 0.359$ on MagicSquare, and $0.467 \to 0.849$ on StackPermutation.

## Relevance to Praxis

- **Anchor multi-agent state in a persistent shared document**: Prefer
  blackboard-style `SharedMemory` over all-to-all conversational `Debate`
  ($\Delta = +0.135$, mean accuracy 0.23 vs. 0.18), and avoid starting
  reasoning workflows with uncoordinated `Star` fan-out ($\Delta = -0.045$).
- **Optimize `prompt.py` context-routing placeholders alongside `graph.py`**:
  Sub-topological prompt specification explains an additional +0.117 validation
  $R^2$ ($0.521 \to 0.638$) and delivers held-out gains ($\Delta = +0.118$)
  comparable to choosing the communication topology itself.
- **Retain full search trajectories during automated harness evolution**:
  Splitting train/val/test at the search level over all evaluated nodes
  (including failures) enables statistically valid design-principle mining.
- **Related artifacts**:
  - `rules/multi-agent-coordination.md`: "DON'T: Default to a fixed multi-agent
    topology" and "DO: Anchor communication to persistent ledgers, not
    ephemeral agents".
  - [`coordinator-executor-prompt-optimization`](../skills/coordinator-executor-prompt-optimization/SKILL.md)
    and [`intervention-guided-mas-prompt-optimization`](../skills/intervention-guided-mas-prompt-optimization/SKILL.md).
