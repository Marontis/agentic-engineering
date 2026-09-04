---
name: counterexample-guided-repair
description: >
  Multi-turn artifact refinement using compact false-positive and false-negative
  counterexample witnesses from an executable oracle, followed by targeted robustness
  probing. Derived from A-CEGIS (arXiv:2609.02892).
source: https://arxiv.org/abs/2609.02892
---

# Counterexample-Guided Repair

Use this skill when designing agent self-correction loops for formal, executable, or
syntactically constrained artifacts (e.g., regular expressions, SQL queries, code snippets,
JSON schemas, deterministic routing rules).

## When to Use

- Refining generated code, regexes, SQL, or grammars after initial validation fails
- Replacing unhelpful natural language critique ("your code has bugs, please fix") with
  concrete, minimal counterexample witnesses
- Tracking multi-turn repair trajectories to detect regressions (when fixing one test
  breaks a previously passing test)
- Validating whether a repaired solution is truly sound via targeted boundary probing
  rather than trusting finite test suites

## Core Insight

Generic self-reflection ("look at what you generated and fix it") performs poorly in
code and formal artifact synthesis: on 30 benchmark tasks, generic self-correction
solved only **26.7%** of tasks, and error-only feedback solved only **23.3%** (Badrinarayan
& Parthasarathy, 2026).

In contrast, **counterexample-guided refinement (CEGIS)** provides minimal, concrete
witnesses:
1. **False Positives**: Inputs accepted by the candidate artifact that should have been rejected.
2. **False Negatives**: Inputs rejected by the candidate artifact that should have been accepted.

Presenting concrete witnesses to the agent lifted task resolution to **90.0% within 4 turns**
with an average of **2.7 turns to success**. Crucially, finite test sets can be satisfied
by accidental heuristic solutions; adding post-repair **targeted boundary probing** ensures
robust semantic correctness (reaching 76.7% robust verified success).

---

## Procedure

### 1. Construct Executable Test Harness

For any formal artifact generation task, assemble a dual test set:
- **Positive test pool ($P$)**: Inputs that must be accepted/matched/returned.
- **Negative test pool ($N$)**: Inputs that must be rejected/excluded/unmatched.
- Construct tests programmatically using boundary seed mutations (character insertions,
  boundary deletions, off-by-one substitutions, null-byte / edge strings).

### 2. The Multi-Turn Diagnostic Loop

Execute an iterative refinement loop bounded by a maximum turn budget (default $T=4$):

```
Turn t = 1..T:
    1. Agent generates candidate artifact A_t.
    2. Oracle evaluates A_t against active test suite (P_active, N_active).
    3. Compute pass rate and identify witness failures:
       - FP_witnesses = {x in N_active | A_t(x) is ACCEPT}
       - FN_witnesses = {x in P_active | A_t(x) is REJECT}
    4. If |FP| == 0 and |FN| == 0:
       Proceed to Step 4 (Targeted Robustness Probe).
    5. Construct Compact Feedback Prompt:
       - Pick 1-2 minimal False Positives and 1-2 minimal False Negatives.
       - Include previous candidate A_t and exact failing inputs.
       - Instruct agent: "Modify A_t so that it rejects FP witnesses and accepts FN witnesses without breaking previously working cases."
```

### 3. Detect and Penalize Regressions

During multi-turn repair, monitor regression metrics across turns:
- **Regression Event**: An input $x$ that passed under candidate $A_{t-1}$ now fails under $A_t$.
- **Regression Penalty**: When a regression occurs, explicitly surface the regressed case in
  the next turn's prompt: `"Warning: your edit fixed witness W1 but regressed on previously passing input X. Maintain both properties."`

### 4. Targeted Robustness Probing (Post-Convergence Gate)

Passing all cases in $P \cup N$ does not prove full equivalence. Before committing the
artifact:

1. **Synthesize targeted probe inputs**: Apply semantic mutations to positive and negative
   seeds (e.g., doubling repetitions, inserting unicode spaces, reversing branches).
2. **Execute probe suite**: Run candidate $A^*$ against 20–50 targeted boundary probes.
3. **Outcome**:
   - If all probes pass: mark artifact as **Robustly Solved**.
   - If a probe fails: inject the failing probe as a new counterexample witness and resume
     one additional repair turn.

---

## Environment Caveats

- **Witness Minimality**: Always provide the *shortest* failing witness string or simplest
  input. Verbose or complex counterexamples overwhelm agent working memory and distract
  from the core syntax defect.
- **Oracle Reliability**: The oracle evaluator must be deterministic and execute with
  full-match semantics (e.g., in regex, ensure `re.fullmatch` rather than `re.search` to
  prevent accidental prefix-matching).

## Failure Modes

- **Overfitting to witnesses**: The agent writing a brittle hard-coded condition or regex
  branch matching only the literal witness string (e.g., `(pattern)|(literal_witness)`).
  Countermeasure: explicitly forbid literal witness inclusion in instructions, and use the
  Targeted Robustness Probe to catch branch hacks.
- **Oscillation loops**: Alternating between fixing false positives and creating false
  negatives across consecutive turns. Countermeasure: retain cumulative history of all
  previously seen witnesses in the prompt context.

## Cross-References

- [`deterministic-span-editing`](../deterministic-span-editing/SKILL.md) — Precise targeted code and configuration repair.
- [`behavior-aware-verification`](../behavior-aware-verification/SKILL.md) — Selecting verification tests based on proposed modifications.
- [`requirements-driven-code-generation`](../requirements-driven-code-generation/SKILL.md) — Contract-bound test synthesis before implementation.

## Sources

- **Paper**: [COUNTEREXAMPLES AS FEEDBACK FOR AGENT SELF-CORRECTION](https://arxiv.org/abs/2609.02892) — Badrinarayan, Parthasarathy (2026)
- **Praxis source**: `src:2609-02892v1`
