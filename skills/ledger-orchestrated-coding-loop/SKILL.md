---
name: ledger-orchestrated-coding-loop
description: >
  Implement a multi-turn coding agent loop using a decoupled filesystem ledger
  (plan, notes, tasks, code), a structural code-ban on ideation, active note compaction,
  and programmatic subprocess execution test vetoes. Prevents runaway reasoning loops
  in mid-sized models and grounds completion in empirical test outcomes.
  Derived from GVS5H (arXiv:2608.26480).
---

# Ledger-Orchestrated Coding Loop

Use this skill to orchestrate code generation and repair across multiple invocations
of the same base model without conversational context bloat or reasoning runaway loops.

## When to Use

- Deploying mid-sized models (14B–35B) on complex, algorithmic coding problems
- A single-turn model burns reasoning tokens endlessly or loops in self-verification without emitting code
- Multi-turn conversation histories cause context saturation, KV cache bloat, or attention degradation
- You have executable sample test cases (stdin/stdout or unit tests) that can serve as an objective ground-truth oracle
- You want to maximize coding accuracy from cheaper, self-hosted, or mid-tier models (e.g., Qwen-27B, GPT-Terra) before escalating to expensive frontier models

## Core Insight

Monolithic long-context chat histories poison multi-turn coding agents: models fixate on earlier failed attempts, and ungrounded self-deliberation often collapses into infinite verification loops (e.g., a 27B model repeating edge-case checks thousands of times until hitting token limits).

The **Ledger-Orchestrated Coding Loop** decouples coordination from context:
1. **Durable File Ledger**: State persists in a shared directory (`plan.md`, `notes.md`, `tasks.json`, `solution.py`). Every worker is invoked in a clean, zero-shot context containing only the current task, high-level plan, compact notes, and current code artifact.
2. **Structural Code-Ban on Ideation**: The first worker is strictly forbidden from writing code, forcing pure algorithmic complexity analysis ($O(N \log N)$ vs $O(N^2)$) and mathematical reductions in prose.
3. **Active Memory Compaction**: Workers are required to rewrite `notes.md` to under ~800 words, dropping disproven or obsolete hypotheses.
4. **Programmatic Execution Veto**: Candidate solutions are executed in a subprocess against public sample tests. If tests fail, the harness programmatically overrides the manager's `done` signal and forces another repair iteration.

---

## The Four-Role Architecture

```
                      ┌────────────────────────────────────────┐
                      │        Shared Filesystem Ledger        │
                      │  task.md  plan.md  notes.md  sol.py    │
                      └──────────────────┬─────────────────────┘
                                         │
 1. PLAN          [Primary Manager] ─────┴─► Writes plan.md & initial tasks.json
                                         │
 2. IDEATE        [Worker: Ideation] ────┴─► Analyzes complexity (NO CODE) -> notes.md
                                         │
 3. CURATE        [Primary Manager] ─────┴─► Prunes tasks.json, picks ONE next task
                                         │
                  ┌──────────────────────┴─────────────────────┐
                  ▼                                            ▼
 4. EXECUTE   [Worker: Task]                              [Exit / Finalize]
              Rewrites solution.py                             ▲
              Compacts notes.md (<800w)                        │
                  │                                            │
                  ▼                                            │
 5. VERIFY    [Subprocess Test Runner]                         │
              Runs solution.py against sample tests            │
                  │                                            │
                  ├─ Passed all tests ──► Manager: "done" ─────┘
                  │
                  └─ FAILED tests ──────► FORCED VETO: Overrides "done",
                                          injects failure case, forces repair
```

---

## Step-by-Step Procedure

### Step 1: Initialize the Filesystem Ledger

Create a dedicated workspace directory for each task instance and initialize five tracking files:

```bash
mkdir -p workspace/run_<task_id>
touch workspace/run_<task_id>/{task.md,plan.md,notes.md,tasks.json,solution.py}
```

Write the raw problem statement to `task.md`.

### Step 2: Seed Plan & Initial Task Decomposition (`primary_plan`)

Prompt the model in Manager mode to produce an overarching 3–6 sentence strategy and 3–6 concrete, non-overlapping task items:

```markdown
You are the PRIMARY orchestrator of a team of expert competitive programmers.
Given a problem, produce a short overarching plan to solve it, then a task list.
Respond with EXACTLY these sections:
### PLAN
<3-6 sentence strategy>
### TASKS
<3-6 bullet tasks, each a concrete unit of work>
```

Save the `PLAN` section to `plan.md` and parse the bullet tasks into `tasks.json`.

### Step 3: Enforce Code-Banned Ideation (`ideation_worker`)

Call a fresh model instance with the problem and `plan.md`. **Crucially, enforce a negative constraint forbidding code blocks:**

```markdown
You are the FIRST WORKER. Do NOT solve the problem and do NOT write any code.
Identify the core difficulty, list 2-3 DISTINCT candidate approaches (different
algorithms, data structures, or reductions), analyze worst-case time/space complexity,
and note pitfalls for each. Describe approaches in prose only -- absolutely no code blocks.
Respond with EXACTLY:
### NOTES
<your algorithmic analysis and complexity bounds>
### NEXT
<bullet list of distinct approaches to try next>
```

Append the analysis to `notes.md`. This prevents early commitment to brute-force $O(N \cdot M)$ scans before considering range queries or dynamic programming.

### Step 4: Curate the Task List (`primary_manage`)

The Manager reads `plan.md`, `notes.md`, `solution.py`, the current task list, and the latest worker outcome. It:
1. Marks completed tasks as `[done]`
2. Drops redundant or superseded items
3. Folds in new proposals from the previous worker
4. Selects **exactly one** next task to assign
5. Sets `STATUS: continue` or `STATUS: done`

### Step 5: Execute Bounded Task with Active Memory Compaction (`worker`)

Spawn a fresh worker instance. The input payload contains *only*:
- `PROBLEM`: Raw text from `task.md`
- `PLAN`: Content of `plan.md`
- `NOTES`: Content of `notes.md`
- `CURRENT CODE`: Content of `solution.py`
- `TASK`: The single task selected in Step 4

Prompt the worker with an explicit output contract:
- `### CODE`: Complete, self-contained Python program.
- `### NOTES`: **Rewritten notes file under ~800 words.** Instruct the worker to fold in findings, keep what still matters, and delete anything superseded or disproven.
- `### NEXT`: Bullet list of remaining steps or checks.
- `### STATUS`: `solved` or `continue`.

If the worker hits the generation token limit (`finish_reason == length`), trigger a fast helper call to summarize the partial thought into `notes.md` rather than discarding the compute.

### Step 6: Subprocess Execution Verification & Veto (`run_samples`)

Whenever `solution.py` is written, execute it in a clean OS subprocess against public stdin/stdout sample cases:

```python
import subprocess, sys

def run_sample_tests(solution_path, sample_tests):
    for test in sample_tests:
        try:
            res = subprocess.run(
                [sys.executable, solution_path],
                input=test["input"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if res.returncode != 0 or res.stdout.strip() != test["expected"].strip():
                return {
                    "passed": False,
                    "first_failure": {
                        "input": test["input"][:500],
                        "expected": test["expected"][:300],
                        "got": res.stdout.strip()[:300],
                        "stderr": res.stderr.strip()[:300]
                    }
                }
        except subprocess.TimeoutExpired:
            return {"passed": False, "timeout": True}
    return {"passed": True}
```

**The Critical Veto Rule**:
If `run_sample_tests` returns `passed: False`, the harness **programmatically overrides** any `STATUS: done` produced by the Manager:
- Force `status = "continue"`
- Inject the first failing test case (input, expected, got) into the manager's next prompt
- Mandate a fix-or-switch task

---

## Anti-Patterns & Failure Modes

### 1. Context Accumulation (Chat History Bloat)
* **Anti-Pattern**: Appending every manager turn, worker thought, and execution error into an ongoing multi-turn chat transcript.
* **Why It Fails**: Attention dilution causes the model to fixate on earlier buggy code structures and repeat hallucinated proofs.
* **Fix**: Reset context every turn. Workers receive only the curated `notes.md` (<800 words) and current `solution.py`.

### 2. Runaway Deliberation Loops
* **Anti-Pattern**: Setting generation caps to 128k–250k on smaller reasoning models without turn limits.
* **Why It Fails**: Smaller models (14B–35B) often lack calibrated stopping criteria and repeat edge-case interrogations thousands of times without producing code.
* **Fix**: Enforce per-round output bounds and multi-turn iteration limits (e.g., max 10 rounds). Let the manager force intermediate progress onto disk.

### 3. Deliberation-Induced Regressions on Brittle Models
* **Anti-Pattern**: Applying extensive ideation and multi-worker deliberation to small MoE models (e.g., Qwen3.6-35B-A3B) without baseline fallback.
* **Why It Fails**: The ideation stage can talk the model *out* of correct, optimal algorithms into flawed "simpler" implementations.
* **Fix**: If the worker repeatedly fails sample tests after trying an approach, force a reset to a fresh baseline implementation without prior notes.

---

## Verification & Metrics

Measure the effectiveness of the ledger loop using three metrics:
1. **Pass@1 Gain**: $\Delta = \text{Managed Pass@1} - \text{Single-Call Pass@1}$.
2. **Rescue Rate**: Percentage of single-call failures caused by truncation/empty output that are successfully resolved by the manager arm.
3. **Token Efficiency Ratio**: Additional accuracy gained per token spent relative to upgrading to the next model tier.
