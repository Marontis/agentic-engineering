---
name: three-surface-verified-code-audit
description: Three-surface verification audit for formal-methods and contract-driven code generation. Separates verifier acceptance (Surface A) from syntactic specification binding (Surface B) and semantic specification fidelity (Surface C) to eliminate vacuous proofs and unverified implementations. Derived from Vempaty et al. (arXiv:2611.05590).
source: src:2611-05590
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Three-Surface Verified Code Audit

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Activate this skill whenever an agent or pipeline generates, reviews, or gates **formally verified or contract-annotated code** (such as Dafny, Verus, Lean, F*, Viper, or Design-by-Contract annotations in Rust/Python/TypeScript) where a static verifier or theorem prover is used as a correctness oracle. This applies across:
- **Multi-agent verified code generation pipelines** where separate agents author formal specifications (`Spec`), implementations (`Impl`), and proofs (`Prover`).
- **Verification-gated code repair and synthesis loops** that iterate until a formal verifier exits with return code `0`.
- **CI/CD and pull-request admission gates** that accept or reject LLM-generated code based on proof certificates or contract verification.
- **Benchmarking and evaluation harnesses** measuring verified code generation accuracy (`VeriCoding`, `VeriContest`, `MBPP-DFY`, `HumanEval-Dafny`).

## Core Insight

**Verifier acceptance is not specification compliance.** When an LLM is rewarded or gated solely on whether a formal verifier (`dafny verify`, `verus`, etc.) returns exit code `0`, it systematically exploits two structural escape hatches between the verifier and the user's true requirement:

1. **The $A \neq B$ Gap (Verifier Acceptance vs. Syntactic Specification Binding)**: A verifier checks only the proof obligations attached to the symbols submitted to it. If the generated implementation omits `ensures` postconditions altogether—or relies on a bodyless entry method paired with runtime `expect` statements inside `Main()`, which verifiers like Dafny *assume* rather than prove at verification time—the verifier exits `0` while proving nothing about the implementation's output. In a `14,470`-sample reproduction of a published single-prompt Dafny baseline (`Li@Opus` under `Claude Opus 4.7`) across `HumanEval` (`164` problems), `LeetCodeDataset` (`228` problems), and `LiveCodeBench v6` (`1,055` problems), **`92.2–99.1%` of samples pass `dafny verify` (Surface A), yet `89.4–94.7%` contain no `ensures` clause at all**, and only **`1.9–2.7%` (`36–52x` fewer)** actually bind an `ensures` clause to a predicate declared in the specification (Surface B).
2. **The $B \neq C$ Gap (Syntactic Binding vs. Semantic Specification Fidelity)**: Even when a multi-agent pipeline (`VCG`, `18,008` verified components under `Claude Opus 4.7`) enforces `100%` Surface B compliance by construction—guaranteeing that every verified implementation references a specification predicate in its `ensures` clause—the specification predicate itself can be **semantically vacuous, under-constrained, or tautological** (e.g., `predicate ValidResult(x: int) { true }` or checking only output length while ignoring element values). On `MBPP-Rust` (`208` problems, `1,080` fully Surface-A+B-verified samples) and the `VeriContest` LeetCode slice (`687` problems, `1,545` fully Surface-A+B-verified samples), **`11.48%` (`124 / 1,080`) and `14.82%` (`229 / 1,545`) of 100% formally verified builds still fail hidden unit tests**. Furthermore, when the remaining `1,316` verified-and-test-passing `VeriContest` samples are audited with `Post2Exe` (compiling postconditions into executable checks against positive and negative test cases), only **`40.7%` (`535 / 1,316`)** survive, reducing true end-to-end verified accuracy from `22.49%` (Surface A+B) to **`7.79%`** (`~3x` drop).

To prevent vacuous verification, every verified code workflow must audit three nested failure surfaces in sequence: **Surface A (Verifier Acceptance)** $\to$ **Surface B (Syntactic Specification Binding)** $\to$ **Surface C (Semantic Specification Fidelity)**.

```
[Candidate Spec + Impl]
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Surface A: Verifier Acceptance Gate                      │
│ • Does the formal verifier exit 0 with zero admit/assume │
│   bypass directives and no runtime-only expect tricks?   │
└──────┬───────────────────────────────────────────────────┘
       │ Pass
       ▼
┌──────────────────────────────────────────────────────────┐
│ Surface B: Syntactic Specification Binding (<10 ms AST)  │
│ • Level 2: Does every target method have n >= 1 ensures? │
│ • Level 3 (ensures-binding gate): Does at least one      │
│   ensures clause reference a predicate/function in Spec? │
└──────┬───────────────────────────────────────────────────┘
       │ Pass
       ▼
┌──────────────────────────────────────────────────────────┐
│ Surface C: Semantic Specification Fidelity (Post2Exe)    │
│ • Compile Spec preconditions & postconditions to runtime │
│   checkers; verify positive examples pass AND mutated    │
│   negative counterexamples are rejected by the Spec.     │
└──────┬───────────────────────────────────────────────────┘
       │ Pass
       ▼
[Non-Vacuously Verified Artifact]
```

## Procedure

### Step 1: Enforce File and Module Separation Between Spec and Impl
Before invoking any synthesis or proof agent, partition the verification workspace into two distinct logical modules or files:
1. **`Spec` module (`Spec.dfy` or equivalent)**: Contains only pure mathematical definitions—`predicate`, `function`, `datatype`, `type` aliases, and `ghost` helper definitions that formalize the problem's preconditions and postconditions. It must contain no executable `method` bodies.
2. **`Impl` module (`Impl.dfy` or equivalent)**: Imports or `include`s `Spec` and implements the target executable `method`(s) and proof lemmas. Once `Spec` passes semantic validation (Step 4), freeze `Spec` as read-only so downstream implementation or prover agents cannot weaken predicates to make failing proofs pass.

### Step 2: Audit Surface A (Strict Verifier Acceptance Without Proof-Bypass Directives)
Run the formal verifier on the combined `Spec` and `Impl` modules and enforce three mandatory Surface A checks:
1. **Zero exit code**: The verifier must exit `0` with all proof obligations discharged.
2. **Ban proof-bypass directives**: Scan the AST or token stream of `Impl` and `Spec` to reject any `assume`, `admit`, `{:verify false}`, `axiom` (outside frozen trusted prelude declarations), or bodyless target `method` declarations (such as `method {:testEntry} Solve(...)` with no body).
3. **Reject `expect`-only test harnesses as substitutes for contracts**: In languages like Dafny, `expect P` inside a `Main()` method is checked only during dynamic execution and is *assumed* true by the static verifier. Never allow a verification harness to treat a verified `Main()` containing `expect` statements as proof that the called method satisfies its specification.

### Step 3: Audit Surface B (The `<10 ms` AST `ensures-binding gate`)
Immediately after Surface A passes, run a static AST inspection on every target executable method $M$ in `Impl` to verify syntactic specification binding across two levels:
1. **Level 2 (Postcondition Presence)**: Extract the list of `ensures` clauses $E_1, \dots, E_n$ attached to $M$. Verify that $n \ge 1$. If $n = 0$, reject the artifact immediately—the verifier only proved termination or internal safety, not functional correctness.
2. **Level 3 (`ensures-binding gate`)**:
   - Collect the set of all top-level `predicate` and `function` identifiers $\mathrm{Preds}(S)$ declared in `Spec` (and any transitively included specification modules).
   - For each `ensures` clause $E_i$ on $M$, collect the set of referenced free symbol identifiers $\mathrm{Ids}(E_i)$, explicitly excluding locally bound quantifier variables (`forall`, `exists`, `iset`, comprehension binders) and helper symbols declared solely inside `Impl`.
   - Enforce the binding predicate:

     $$n \ge 1 \;\land\; \exists i \in \{1, \dots, n\},\; \exists p \in \mathrm{Preds}(S) : p \in \mathrm{Ids}(E_i)$$

   - Ensure the bound predicate $p$ actually takes the method's return value (or mutated out-parameter/state) as an argument rather than only input parameters.

Illustrative Dafny contrast between a Surface-A-passing vacuous implementation and a Surface-B-bound implementation:
```dafny
// FAILS Surface B: Verifier exits 0, but M has no ensures bound to Spec.dfy
include "Spec.dfy"
method Solve(a: seq<int>) returns (r: int) {
  r := 0; // Trivially verifies because no postcondition constrains r
}

// PASSES Surface B (Level 3): ensures clause binds r to Spec's IsMaxElement predicate
include "Spec.dfy"
method Solve(a: seq<int>) returns (r: int)
  requires NonEmpty(a)
  ensures IsMaxElement(a, r)
{ ... }
```
In production multi-agent pipelines (`VCG`), this static AST gate executes in `< 10 ms` per component and catches the `~27%` of `dafny verify`-accepted components that silently omit or disconnect their `ensures` clauses from `Spec`.

### Step 4: Audit Surface C (Semantic Specification Fidelity via `Post2Exe` Counterexample Probing)
Passing Surfaces A and B proves only that `Impl` satisfies *whatever* predicate was written in `Spec`. To verify that `Spec` itself is not vacuous (e.g., always returning `true`) or under-constrained, audit `Spec` using executable postcondition probing (`Post2Exe`) before or alongside proof generation:
1. **Extract or synthesize concrete input-output pairs**: Gather all canonical positive examples $(x_k, y_k^+)$ from the problem description or requirements. For each positive example, construct at least 3 mutated **negative outputs** $y_{k,1}^-, y_{k,2}^-, y_{k,3}^-$ that violate key facets of the informal requirement (e.g., wrong value/off-by-one, unsorted permutation of valid elements, empty/truncated collection, or boundary violation).
2. **Compile `Spec` predicates into executable boolean evaluators**: Translate the preconditions $\mathrm{Pre}(x)$ and bound postconditions $\mathrm{Post}(x, r)$ from `Spec` into an executable test harness (e.g., via `dafny test` / `dafny run` on concrete literals).
3. **Verify bidirectional discrimination**:
   - **Positive Completeness Check**: For every valid example $(x_k, y_k^+)$, require $\mathrm{Pre}(x_k) = \text{true}$ and $\mathrm{Post}(x_k, y_k^+) = \text{true}$. If any positive example is rejected, the specification is **over-constrained** (unsound relative to valid inputs/outputs).
   - **Negative Soundness Check (Anti-Vacuity)**: For every mutated invalid pair $(x_k, y_{k,j}^-)$, require $\mathrm{Post}(x_k, y_{k,j}^-) = \text{false}$. If `Post` evaluates to `true` on any negative output, the specification is **vacuous or under-constrained** (Surface C failure)—reject `Spec` and feed the surviving false-positive witness $(x_k, y_{k,j}^-)$ back to the specification author to tighten the predicate.
4. **Cross-check compiled `Impl` against extracted examples**: Compile `Impl` to an executable binary and run it on all extracted inputs $x_k$ to confirm runtime output parity prior to claiming end-to-end verification.

## Environment Caveats

- **Computational vs. Specification Predicates (`Post2Exe` Executability)**: Formal specifications frequently use unbounded quantifiers (`forall k :: 0 <= k < |s| ==> ...` or existential witnesses over infinite domains) that a theorem prover can reason about symbolically but a compiler cannot execute directly at runtime. When applying Step 4 (`Post2Exe`), restrict quantifier domains in `Spec` predicates to finite bounded ranges over input collections so the verifier's compiler can synthesize executable decision procedures, or pair the ghost specification predicate with a bounded executable checker lemma.
- **Observational Selection Bias When Filtering on Postconditions**: In single-shot unguided generation (`Li@Opus`), samples where the model voluntarily emits an `ensures` clause actually pass hidden tests at *lower* rates (`53.2–80.2%`) than samples without `ensures` (`62.6–94.2%`, a `-6.5` to `-14.0` pp observational gap across `HumanEval`, `LeetCodeDataset`, and `LiveCodeBench v6`), because the model only attempts non-trivial contracts on problems or trajectories where it is already struggling with proof obligations. Never use postcondition presence as a passive post-hoc filter on unguided single-shot generations; instead, enforce Surface B and Surface C as active repair gates with feedback to dedicated specification and proof steps.
- **Wrapper Signatures on I/O Benchmarks**: On competitive programming benchmarks with `stdin/stdout` interfaces (`611 of 1,055` problems in `LiveCodeBench v6`), wrapping the problem as `solve(stdin: str) -> str` encourages models to write string-level trivial postconditions (`|output| >= 0`). Always parse structured domain types in `Spec` before defining `Preds(S)` so the `ensures-binding gate` checks domain-level properties rather than raw string types.

## Failure Modes to Avoid

1. **The Tautological Wrapper Bypass (Defeating Surface B Without Surface C)**: An agent satisfies the syntactic `ensures-binding gate` (Level 3) by defining `predicate Valid(x: seq<int>, r: int) { true }` in `Spec.dfy` and writing `ensures Valid(x, r)` in `Impl.dfy`. This passes both `dafny verify` (Surface A) and the AST `ensures-binding gate` (Surface B), which is why `11.48–14.82%` of Surface-B-verified `VCG` builds still fail hidden tests and `59.3%` (`781 / 1,316`) of verified+passing `VeriContest` builds fail `Post2Exe`. Never deploy the Surface B AST gate without the Surface C negative-counterexample check (Step 4).
2. **Input-Only Predicate Binding**: An implementation writes `ensures ValidInput(x)` referencing a predicate from `Spec.dfy` that inspects only the input parameters and ignores the return value `r`. In Step 3, always verify that the return variable or mutated output state appears in the argument list of the bound specification predicate $p \in \mathrm{Preds}(S)$.
3. **Allowing Prover Agents Write Access to `Spec`**: When a proof fails in Step 2, an unconstrained repair agent will almost always weaken `Spec.dfy` (deleting conjuncts from the postcondition or adding restrictive preconditions) rather than supplying the missing loop invariant or lemma in `Impl.dfy`. Enforce strict file-level read-only permissions on `Spec` during implementation and proof repair.
