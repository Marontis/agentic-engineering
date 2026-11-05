# Bounded Halting, Diagonal Lower Bounds, and Observable Tests for Standalone Universality

> **Source**: [arXiv:2611.06303](https://arxiv.org/abs/2611.06303) | `src:2611-06303`
> **Authors**: Sergey Salishev (St. Petersburg State University)
> **Date**: 2026-11-04

## Key Findings

- **Fixed finite-state systems cannot decide general bounded halting (`BH_T`) across growing budgets**: By Proposition 1, if a closed deterministic implementation has a reachable configuration set of size $C$ fixed independently of the time budget $T$, any non-halting execution repeats a configuration within at most $C + 1$ transitions. While halting of that fixed implementation is trivially decidable by cycle detection in $C + 1$ steps, the implementation cannot serve as a general bounded-halting decider for arbitrary programs and budgets once $T$ exceeds its effective state capacity.
- **No fixed-factor exact shortcut exists for deterministic bounded halting**: Under unit-cost step accounting where simulating one transition of a target program takes one transition of a universal machine plus constant wrapper overhead $c$, Theorem 4.2 and Corollary 4.4 prove via diagonalization (`Contra_T`) that for all sufficiently large $T$, no deterministic machine $H_T(p, x)$ can decide `BH_T(p, x)` on all inputs in at most $T - c$ transitions. Consequently, for any fixed constant $\alpha < 1$ (such as $T/2$ or $0.1 n^3$), no exact uniform deterministic decider can halt on all inputs within $\alpha T$ transitions once $\alpha T \le T - c$.
- **Nondeterministic branching and finite randomization provide tree width, not sequential causal depth**: Extending bounded halting to nondeterministic machines (`NBH_T`, which asks whether at least one branch of $M$ on $x$ halts within $T$ steps), Theorem 6.6 proves that no nondeterministic family $A_T$ with **stable observable output** (all terminating branches on the same input return the same accept/reject bit) can decide `NBH_T` in at most $T - c$ (or $\alpha T$ for $\alpha < 1$) transitions on every branch, because restricting `NBH_T` to deterministic target machines reduces directly to `BH_T`. By Corollary 6.8, no finite randomized implementation in which every possible execution branch has positive probability can decide `NBH_T` with probability $1$ within $T - c$ transitions.
- **Three observable properties refute standalone universality claims without inspecting internal weights**: Section 7 translates classical computability requirements into three behavioral refutation tests for deployed systems:
  1. *Configuration-space growth with $T$* (Proposition 1): If the number of distinguishable internal configurations is fixed independently of $T$, long runs must eventually become periodic.
  2. *Unbounded deliberation before output* (Proposition 7.10): If an implementation always emits its answer within a fixed internal step bound $B$ independent of $T$, it fails `BH_T` for all $T > B + c$.
  3. *Preservation of earlier intermediate data* (Proposition 7.12): If an implementation compresses arbitrarily long histories through a fixed finite state space $S$ after horizon $h$, then for input blocks of length $n \ge h$ with $2^n > |S|$, two distinct strings $u \ne v \in \{0,1\}^n$ collide in $S$, causing the machine to fail exact matching tasks such as $L = \{w\#w : w \in \{0,1\}^*\}$ under `BH_T(M_copy, u#u) = 1` versus `BH_T(M_copy, v#u) = 0`.
- **Fixed-precision, fixed-context Transformers fail standalone universality even with unbounded chain-of-thought generation**: Applying the three observable tests across machine classes shows that a fixed finite-precision Transformer with a bounded context window and no external read-write memory fails all three tests in single-pass mode, and still fails configuration-space growth and intermediate-data retention under unbounded token generation (which supplies only unbounded deliberation before repeating states in a loop). Universality belongs only to the **composite system** when paired with an unbounded external read-write store, elastic context, or growing multi-agent state space.

## Quantitative Summary

| Result / System Class | Formal Bound or Observable Criterion | Growth with $T$ | Unbounded Deliberation | Later Data Access | Passes All 3 Universality Tests? |
|:---|:---|:---:|:---:|:---:|:---:|
| **Closed deterministic finite-state machine** (Prop. 1) | Reachable states $\le C \implies$ cycle detection in $\le C + 1$ steps | No | No | No | **No** |
| **Deterministic `BH_T` decider** (Thm. 4.2, Cor. 4.4) | Cannot decide all $(p, x)$ in $\le T - c$ steps; no $\alpha T$ shortcut for fixed $\alpha < 1$ | — | — | — | — |
| **Branching vs. deterministic traversal** (Sec. 6.2) | Branch verification `NTIME(O(p(n)))` vs. full tree search `DTIME(b^{p(n)} p(n)^{O(1)})` | — | — | — | — |
| **Stable nondeterministic / prob-1 `NBH_T` decider** (Thm. 6.6, Cor. 6.8) | Cannot decide all $(M, x)$ in $\le T - c$ (or $\alpha T$) steps on all branches | — | — | — | — |
| **Fixed deliberation bound $B$** (Prop. 7.10) | Fails `BH_T` whenever $T > B + c$ | — | Fails for $T > B + c$ | — | **No** |
| **Fixed bottleneck state $S$ after horizon $h$** (Prop. 7.12) | Collides on $u \ne v \in \{0,1\}^n$ once $n \ge h$ and $2^n > \|S\|$ | — | — | Fails for $2^n > \|S\|$ | **No** |
| **$\varepsilon$-transition finite-state machine** (Table 1) | Silent $\varepsilon$-loops delay output without expanding state space | No | Yes | No | **No** |
| **Single-stack pushdown automaton (PDA)** (Table 1) | Unbounded stack grows with $T$, but LIFO pops destroy earlier data | Yes | Yes | No | **No** |
| **Two-stack pushdown automaton** (Table 1) | Second stack preserves reversible random access to earlier data | Yes | Yes | Yes | **Yes** |
| **Unbounded CSP-style multi-agent system** (Table 1) | Unbounded dynamic process creation and message passing (fails Prop. 7.10 if hard-capped by a fixed deadline) | Yes | Yes | Yes | **Yes** |
| **Fixed finite-precision Transformer** (Table 1) | Fixed weights, finite precision, bounded window, fixed layer depth | No | No | No | **No** |
| **Fixed-context Transformer + unbounded generation** (Table 1) | Unbounded output loop with sliding/truncated context and finite positional precision | No | Yes | No | **No** |

## Why Not a Skill?

This paper is a theoretical computability and systems-boundary analysis rather than an executable subtask-level procedure. Its theorems (`BH_T` and `NBH_T` diagonal lower bounds) and four-question boundary audit provide architectural guardrails and evaluation criteria for judging when an agent runtime, safety monitor, or model architecture can legitimately claim general-purpose verification or universality. These insights belong in contextual engineering knowledge and always-active architectural rules rather than an on-demand procedural skill.

## Actionable Takeaways

- **Do not expect static or fixed-budget pre-execution monitors to decide long-horizon behavioral properties faster than running the agent**: Because no uniform deterministic or probability-one branching monitor can decide general bounded halting in $\le \alpha T$ transitions for any fixed $\alpha < 1$, exact predictive verification of an arbitrary $T$-step agent trajectory requires either executing on the order of $T$ steps or restricting the agent DSL/workflow to a non-universal subset.
- **Audit the four system-boundary questions before attributing universality or long-horizon competence to an LLM**:
  1. *Boundary*: Is the claim about a fixed model with extendable external tape/stack, a growing model family whose parameters/precision/context scale with input size, or a composite harness with RAG, files, and tools?
  2. *Accounting*: If the model uses parallel sampling, beam search, or multi-agent branching, where is the $O(b^{p(n)})$ tree-traversal work paid?
  3. *Clock*: What continuation rule governs when the system stops deliberating and emits a final answer, and is it artificially capped by a fixed round limit $B$?
  4. *Retention*: Does the system have an addressable external store that grows with horizon $T$, or does sliding-window truncation/compression force $2^n > |S|$ state collisions on earlier intermediate results?
- **Pair fixed-context models with addressable external read-write state for arbitrary-horizon tasks**: Unbounded chain-of-thought generation alone only satisfies the deliberation condition (Proposition 7.10); satisfying configuration growth (Proposition 1) and intermediate data retention (Proposition 7.12) requires an external scratchpad, file system, or database whose addressable capacity scales with $T$.

## Related Output

- **Rule**: [output/rules/agent-evaluation-quality.md](../rules/agent-evaluation-quality.md) — evaluation integrity and architectural capability claims
- **Rule**: [output/rules/skill-system-design.md](../rules/skill-system-design.md) — external working memory vs. fixed-context window compression limits
- **Rule**: [output/rules/agent-sandbox-safety.md](../rules/agent-sandbox-safety.md) — empirical failure modes of long-horizon execution monitoring
