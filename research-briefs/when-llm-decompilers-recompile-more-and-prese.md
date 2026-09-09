# When LLM Decompilers Recompile More and Preserve Less

> **Paper**: [When LLM Decompilers Recompile More and Preserve Less](https://arxiv.org/abs/2609.05370)
> **Praxis source**: src:2609-05370

## Why Not a Skill?

This paper is an empirical benchmark evaluation exposing a fundamental gap in LLM decompilation metrics. It introduces Decompile-Diverge as a testing oracle, but the oracle itself is a specialized fuzzing+driver-synthesis pipeline tightly coupled to compiled binary analysis—not a transferable subtask-level procedure for agent workflows. The key contribution is the *finding* (recompilability ≠ behavioral fidelity) rather than a reusable procedure.

---

## Core Concept

LLM-based decompilers produce clean, idiomatic C code that recompiles and passes shipped tests at high rates—but this metric is misleading. A function may recompile and pass every shipped test yet diverge on other legitimate inputs, and a disclosed vulnerability may disappear from the decompiled output with no visible trace. The paper proposes Decompile-Diverge, a behavioral comparison oracle that synthesizes drivers, grows fuzzing corpora from reference binaries, and reruns decompiled code on the same inputs to detect behavioral divergence.

### Key Finding

- **Primary Result**: Across eight decompiler systems in nine configurations, candidates that pass every shipped test still diverge from the original on Decompile-Diverge's input corpus: **4.9% overall, up to 13% for a single system**. On 300 real GitHub library functions and 287 CVE-grounded functions, the strongest refinement LLM lifts Ghidra's build rate from 75% to 90%, while its behavioral Matched rate *falls* from 74% to 62%.
- **Secondary Result**: On disclosed vulnerabilities, up to **10% exhibit Crash Absence**—the vulnerability silently disappears from the decompiled output. Source-level analysis traces divergence to introduced fields, types, callees, and guards that replace the visible unknowns traditional tools leave behind.

## Relevance to Praxis

- **Metric skepticism for agent evaluation**: Recompilability and test-passing are proxy metrics that can reward the wrong behavior. This same pattern applies to agent harness evaluation—passing shipped tests doesn't guarantee behavioral fidelity. Relevant to the `harness-tampering-audit` and `behavior-aware-verification` skills.
- **Fuzzing-based behavioral oracles**: The Decompile-Diverge approach (synthesize drivers → fuzz → compare behaviors) is a pattern applicable to verifying agent-generated code transformations.
- **Silent failure modes**: The "Crash Absence" finding—where critical behavior silently disappears without visible error—mirrors the silent failures documented in agent self-improvement loops.
