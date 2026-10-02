# A Theory of Reliable Self-Evolution for Agent Harnesses (Two-Gate Validation)

> **Source**: Cai, Zhang, Nie, Ran, Zheng, Song, Tian, Guo, Xue, arXiv:2609.08175 (v2, 28 Sep 2026)
> **Status**: Research Brief — theory of when a self-evolved harness can be adopted, with one DS-1000 illustration

## Why Not a Skill?

The contribution is a set of theorems (adoption condition, validation rule, performance ceiling, stagnation diagnosis), not a procedure with measured benchmark gains. Its practical content is an acceptance rule, which is rule material: it backs the noise-margin gate in `rules/recursive-improvement.md` ("DO: Pass every self-modification through one acceptance gate") and the harness-evolution entry in `rules/skill-system-design.md` ("DO: Bound the search space of harness self-evolution").

## Core Concept

In harness self-evolution the model is fixed and the agent edits its own prompts, code, tools and orchestration from task failures. A fix can help the failed tasks while hurting previously successful ones. The paper calls adoption **reliable** when the candidate raises expected reward over the full user-task distribution, and splits that change into two parts:

- **Failure-task contribution** `L`: the gain on tasks the current agent fails.
- **Retained-task change** `D`: the mean *absolute* change in expected reward on tasks it already solves.

If `L` is at least a threshold τ and `D` is at most a limit (the paper's δ, an allowed retained-task change, not a noise band), the overall gain is bounded below. Retained tasks may change, so long as failure-task gains outweigh the possible losses.

**Rule 1 (Two-Gate validation)** adopts a candidate only if, on a validation set, the estimated `L` clears τ, the estimated `D` stays within the limit, and the resulting lower bound on overall gain, after subtracting estimation error terms, is positive. Reference data must be refreshed after each adoption.

## Key Findings

- **Reliable adoption**: under the stated assumptions and evaluation conditions, Rule 1 adopts a candidate whose true gain falls below its computed lower bound with probability at most a stepwise error bound; guaranteed gains accumulate across adopted steps without assuming independence between steps.
- **Candidate generation limits progress too**: validation can adopt a qualified modification only if the pool contains one. The paper defines *reachability*, the probability that one generation run produces a qualified modification, and bounds the chance of a reliable update from it.
- **Performance ceiling**: Rule 1 treats the full allowed retained-task change as a possible loss, so near the top it cannot validate further gains; evaluation error lowers the ceiling further. A second rule (**Measured-margin**), which uses the candidate's own measured retained-task losses, can validate improvements past that ceiling. The ceiling therefore depends on how improvement is verified.
- **Validation cost rises near the top**: as expected reward approaches its bound, any level-controlled validation procedure needs worst-case evaluation cost that grows as remaining gains shrink.
- **Diagnosing stalls (DS-1000 illustration)**: three generation processes each produced 96 outputs in 24 pools. Audit runs (56 withheld tasks per context, three fresh runs per agent and task) found that 26–39% of outputs met the target (L ≥ 0.05, D ≤ 0.50), yet only 2 of 288 outputs passed validation on 48 validation tasks per context. One rejected candidate met the target on audit; its validation estimate of L was 0.1458 but the lower bound, 0.0378, fell below 0.05. Stalls can come from too little validation evidence, not only from poor generation.
- **Limitations stated by the authors**: guarantees concern expected reward and average change under the specified task distributions; distribution shift and user responses to updates need extra correction terms.

## Relevance to Praxis

- **Acceptance gate**: Two-Gate is the formal version of "no regression beyond a margin": the library gate's noise margin δ (from repeated baseline runs) and this paper's retained-task limit both allow bounded change on previously-correct tasks, and both require the gain to clear estimation error. The negative security testbed is outside this analysis and stays strict.
- **Repeat runs**: the paper's audit used three fresh runs per agent and task, consistent with the gate's "at least 3 baseline runs" to estimate δ.
- **Stagnation**: on a stall, first check whether validation is simply under-powered, instead of widening the editable surface (see [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md) and `rules/skill-system-design.md` "DON'T: Assume recursive self-improvement is unbounded").
- Related briefs: [`robust-sgpo-harness-evolution`](robust-sgpo-harness-evolution.md), [`process-level-self-evolution-evaluation`](process-level-self-evolution-evaluation.md).
- Caveats: mostly theory; one small DS-1000 illustration with one fixed model; thresholds (0.05, 0.50) are the paper's illustrative choices.

> Source: Cai et al., "A Theory of Reliable Self-Evolution for Agent Harnesses" (arXiv:2609.08175)
