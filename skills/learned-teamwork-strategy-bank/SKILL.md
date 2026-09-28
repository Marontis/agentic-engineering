---
name: learned-teamwork-strategy-bank
description: >
  Learn a small, frozen bank of reusable teamwork strategies (roles,
  conversational phases, participation, information flow, synthesis) for
  a fixed heterogeneous team of LLM agents from a few training problems,
  using member-driven reflective mutation, cross-problem validation
  probes, a source-leakage audit, and coverage-greedy selection. At
  inference, run every strategy, have each produce a checkable
  certificate, and let one judge select among them.
  Derived from "Self-Organizing Agent Teams Learn to Reason Together"
  (arXiv:2609.22682).
source: https://arxiv.org/abs/2609.22682
---

# Learned Teamwork Strategy Bank

Use this skill when you have a fixed roster of different models that
each solve different subsets of a reasoning task, and fixed protocols
(voting, debate, Mixture of Agents) are not getting more out of the
team than routing to its best member would.

## When to Use

- A heterogeneous team (different vendors or families) where members'
  independent answers are complementary but none is reliably right
- Reasoning tasks where a correct answer can be assembled from partial
  derivations (one member finds the invariant, another fixes a count)
- You have a small labelled training set (15–25 problems was enough in
  the paper) and want a protocol that transfers unchanged to new
  benchmarks
- Debate is collapsing correct minority answers into wrong consensus

## Core Insight

**Learn how the team works together, not only who answers.** A strategy
is a short program of conversational phases. Each phase fixes who
participates, for how many rounds, whether results stay local or are
summarized to everyone, and which role prompts apply. Letting one member
rewrite these strategies after reading the team's own transcripts
produces organizations that let agents challenge, repair, and synthesize
partial reasoning into answers no member produced alone.

**Evidence** (math/physics team: o3-mini, Claude Sonnet 4, DeepSeek-V3;
bank learned from 15 AIME-2024 problems; means over 3 seeds):

- 5-benchmark average **66.7%** vs best member 48.8%, Mixture of Agents
  57.3%, self-consistency (K = 10) 55.4%, compute-matched linearization
  (o3-mini replaying the same strategies) 58.7%, debate 52.7%.
- Exceeds **routing-oracle coverage** (perfect per-problem selection
  over members' independent answers) on average: 66.7% vs 59.0%. AIME
  2026: 71.2%, +13.4 over the oracle. Pool coverage 75.2%.
- Heterogeneity matters: a homogeneous team (three o3-mini copies
  running the same learned strategies) averaged 56.0%.
- Knowledge/logic team (Gemini-2.5-Flash, Llama-4-Maverick, GPT-4.1;
  25 GPQA problems): best average accuracy (72.8%) but **below** the
  routing oracle (79.6%) even though pool coverage was 87.9%. Selection,
  not generation, was the bottleneck. On BBEH the homogeneous team led
  (58.7% vs 56.0%).
- Across 8 benchmarks, demonstrability (how often a 10-model panel
  prefers a correct over an incorrect team certificate) tracked
  improvement over the best member (Spearman ρ = 0.90, p = 0.005).

---

## Procedure

### 1. Fix the Roster and Define the Strategy Language

Pick a fixed team of models with complementary strengths and headroom on
the task (saturated models hide teamwork gains). Represent each strategy
as:

- a shared teamwork prompt (norms for the whole team)
- persistent per-agent role prompts
- an ordered list of phases, each with: participating subset, number of
  rounds, information flow (`local`: only participants see turns;
  `summary`: after the phase one participant summarizes and the summary
  goes to everyone), a phase prompt, and optional per-agent phase
  prompts

Start from a simple baseline strategy: independent solutions, two rounds
of debate-like exchange, majority vote.

### 2. Run Member-Driven Reflective Mutation Per Training Problem

Designate the member with the best training accuracy as reflector. For
each training problem keep an archive of candidate strategies and their
executions. For a fixed number of rounds (paper: 6 rounds, up to 3
candidates per round):

1. The reflector reads prior strategies, full team transcripts,
   per-member answers, outcomes, and validation results.
2. It chooses which archived strategy to build on and proposes targeted
   edits to roles, phases, or synthesis rules. Blind model identities
   during reflection. Roles should come from observed behaviour (e.g.
   "Agent 2 catches overlooked claims" becomes a final-auditor role).
3. The whole team executes the candidate on the source problem, and the
   transcript and outcome go back into the archive.

### 3. Validate Transfer and Screen for Leakage

- When a candidate solves its source problem, freeze it and run it on
  several other training problems (paper: 5 "validation probes"). Write
  the results back to the archive.
- Run a separate source-dependence audit on every field of every
  candidate. Reject strategies that encode answer values, problem-
  specific facts, or source-derived solution recipes. The strategy must
  describe how to collaborate, not what the answer is.

### 4. Build the Bank Coverage-Greedily, Then Freeze

Select up to about ten strategies greedily by added training-set
coverage (problems solved that the bank did not already solve). Freeze
the bank. No further reflection or controller at test time.

Before adopting the bank, apply the repo's acceptance gate (see
`rules/recursive-improvement.md`). Coverage-greedy selection is a search
heuristic, not a regression check.

### 5. Deploy: Run All Strategies, Produce Certificates, Judge Once

For each new problem, run every strategy in the bank. Each run outputs a
**certificate**: a short, self-contained reasoning trace meant to be
checked step by step, not a bare answer. A single judge receives the
problem and all certificates in one prompt, audits each for specific
local defects without re-solving, and picks the best-supported answer.

### 6. Measure Against the Right Baselines

Report, per benchmark:

- best single member
- compute-matched single-agent control (the best member executing the
  same strategies at about the team's budget)
- homogeneous team (copies of the best member under the same bank)
- **routing-oracle coverage** over members' independent answers
- team **coverage** (any correct certificate) vs team **accuracy**

If coverage is well above accuracy, invest in selection (clearer
certificate formats, better judge) before more generation.

---

## Environment Caveats

- Gains depend on demonstrability. Where correct reasoning is hard to
  tell from plausible errors, the team generates correct certificates
  but fails to select them (the knowledge/logic team stayed below the
  routing oracle).
- Cost scales with bank size × team size × rounds at inference. Compare
  against compute-matched controls, not a single call.
- The strongest member serves as both reflector and judge in the paper.
  That concentrates bias in one model; consider a judge from outside the
  roster when a diverse panel is available.
- Transfer was shown within reasoning domains (AIME → other years, HMMT,
  TheoremQA-physics; GPQA → MMLU-Pro, BBEH). It is untested for
  tool-using or long-horizon agent tasks.

## Failure Modes

| Failure Mode | Trigger | Mitigation |
|:--|:--|:--|
| Consensus overwrites a correct minority | Debate-style rounds converge on a wrong majority | Learned audit phases that resurface overlooked claims; judge audits certificates, not votes |
| Strategy leaks the answer | Reflector writes problem facts into prompts | Source-dependence audit (Step 3) plus cross-problem validation |
| Overfit strategy | Helps only its source problem | Validation probes and coverage-greedy selection (Steps 3–4) |
| Generation–selection gap | High pool coverage, low final accuracy | Improve certificate legibility and the judge; track coverage vs accuracy (Step 6) |
| Illusory team gain | Team beats best member only by selecting among members' answers | Compare against routing-oracle coverage and a homogeneous-team control |

## Cross-References

- [`debate-layer-disagreement-analysis`](../debate-layer-disagreement-analysis/SKILL.md): classifying disagreement before resolving it
- [`bayesian-backward-disagreement-anchor`](../bayesian-backward-disagreement-anchor/SKILL.md): resolving factual disputes
- [`intervention-guided-mas-prompt-optimization`](../intervention-guided-mas-prompt-optimization/SKILL.md): prompt-level MAS optimization
- [`semantic-aware-multi-agent-delegation`](../semantic-aware-multi-agent-delegation/SKILL.md): task routing across agents
- `rules/multi-agent-coordination.md`: "Assume multi-agent debate eliminates shared misconceptions"; "Preserve minority viewpoints in agent voting and consensus"; "Expand candidate model pools with arbitrary heterogeneous architectures"

## Sources

> Pappu, Suzgun, Kwon, Bianchi, El, Kochenderfer, Cao & Zou,
> "Self-Organizing Agent Teams Learn to Reason Together"
> (arXiv:2609.22682), Sep 2026.
