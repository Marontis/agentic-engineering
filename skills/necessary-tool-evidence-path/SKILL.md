---
name: necessary-tool-evidence-path
description: >
  Supervise and optimize agent tool-use trajectories using Necessary
  Tool-Evidence Paths (NTEP). Eliminates redundant tool calls, aligns
  pre-call intents with explicit evidence gaps, and verifies post-call
  observation extraction before progressing reasoning. Derived from
  Long et al. (arXiv:2609.03493).
---

# Necessary Tool-Evidence Path (NTEP)

Use this skill to optimize tool-using agents (vision-language, code, or
web-browsing agents) so that every tool invocation acquires verifiable,
non-redundant evidence required to solve the task.

## When to Use

- An agent executes multiple tool calls per turn (e.g., search, grep, view,
  curl, crop) but frequently produces off-target or redundant queries.
- Tool-calling accuracy is high on final outcomes but wasteful in intermediate
  steps (inflated token consumption, high API costs, unnecessary latency).
- The agent calls a tool, gets the relevant output in the observation, but
  fails to extract or ground the necessary fact before calling another tool.
- You need a structured reward or validation gate for evaluating whether a
  proposed tool call is strictly necessary.

## Core Insight

Standard agent reinforcement learning evaluates tool usage primarily based on
**final answer correctness**. This leaves intermediate evidence acquisition
severely under-supervised, causing two pervasive failures:
1. **Redundant / Off-target invocations**: The agent invokes tools when the
   required evidence is already present in context or repeats identical queries.
2. **Observation extraction failure**: The agent calls an appropriate tool,
   receives the data, but ignores or misinterprets the observation.

Long et al. (arXiv:2609.03493) demonstrate that decomposing trajectories into
a **Necessary Tool-Evidence Path (NTEP)** resolves both failures:
- Supervised alignment of the **pre-call intent** with a concrete evidence gap.
- Verification of **post-call observation alignment** (did the returned data
  satisfy the stated gap?).
- A **non-repeated-goal regularizer** that explicitly penalizes revisiting
  already-satisfied evidence targets.

In an 8B-parameter instantiation (NTEP-8B) across seven multi-modal and search
benchmarks, this fine-grained supervision substantially increases search
accuracy while pruning wasteful invocations.

---

## Procedure

### Step 1: Formulate the Pre-Call Intent Contract

Before dispatching any tool call, require the agent to declare an explicit
contract:

1. **Target Evidence Gap**: What specific missing fact, symbol, or property
   is unknown?
2. **Candidate Tool & Arguments**: Which tool is uniquely positioned to retrieve
   this exact piece of evidence?
3. **Necessity Gate**: Verify whether this information is already present in
   working memory or prior tool outputs. If yes, abort the tool call and use
   local reasoning.

```markdown
<!-- Intent Contract Template -->
[Evidence Gap]: Need definition of `extract_patch_slice` in repo
[Current State]: Function referenced in `engine.py:42`, not defined in file
[Selected Tool]: grep_search(Query="def extract_patch_slice", SearchPath="src/")
[Necessity Check]: PASS (not in context)
```

### Step 2: Extract & Align Post-Call Observation

Once the tool execution returns:

1. **Information Extraction**: Isolate the exact slice or tokens that answer
   the declared `[Evidence Gap]`. Discard boilerplate or noisy observation
   scaffolding.
2. **Alignment Verification**: Confirm that the extracted fact directly matches
   the target gap. If the tool returned empty results or an error, mark the goal
   as **Unsatisfied** and adjust query arguments rather than repeating the same
   call.
3. **Commit to Working Memory**: Record the verified fact into the agent's
   state ledger before formulating the next thought.

### Step 3: Enforce Non-Repeated Goal Tracking

Maintain an explicit ledger of satisfied evidence goals across the rollout:

```python
# Conceptual Goal Ledger
satisfied_goals = set()

def evaluate_tool_proposal(pre_call_intent):
    goal_key = normalize_goal(pre_call_intent.evidence_gap)
    if goal_key in satisfied_goals:
        # Non-repeated-goal penalty
        raise RedundantToolCallError(
            f"Evidence gap '{goal_key}' was already satisfied at step {satisfied_goals[goal_key].step}. "
            "Reuse context instead of issuing a duplicate call."
        )
```

- When the agent attempts to call a tool for an existing goal, trigger an
  immediate reflection check.
- Deduplicate across semantic variations (e.g., searching for `"config.py"` when
  `"config.json"` was already located and inspected).

### Step 4: Prune Unproductive Branches

If an evidence goal remains unsatisfied after 2 attempts with varying arguments:
- Escalate to alternative tools (e.g., switch from exact keyword grep to
  file tree exploration).
- If no alternative tool exists, record the evidence as unavailable and proceed
  with best-effort reasoning or solicit clarification.

---

## Environment Caveats

- **Overhead vs. Token Cost**: Emitting verbose pre-call contracts can add
  prompt tokens. For simple, single-step lookups, use a 1-line prefix
  `Intent: <gap>` instead of a multi-field block.
- **Dynamic Tool Chains**: When exploratory steps are genuinely speculative
  (e.g., fuzzing or exploring unfamiliar code trees), allow the agent to tag
  the step as `[Intent: Exploratory]` with a capped budget of 2–3 actions before
  requiring an evidence check.

---

## Failure Modes

- **Fictitious Alignment**: The agent claims a tool observation answered the
  goal when it actually returned irrelevant text. Mitigate by checking that the
  subsequent reasoning step quotes or directly references the tool output.
- **Over-constraining Exploratory Tasks**: Setting the necessity threshold too
  strictly can freeze agents working on ill-defined tasks. Ensure the
  un-satisfied goal mechanism permits fallback query reformulations.

---

## Cross-References

- [`cost-effective-repo-exploration`](../cost-effective-repo-exploration/SKILL.md) —
  Escalation patterns for codebase search.
- [`speculative-macro-commit`](../speculative-macro-commit/SKILL.md) —
  Batching recurring tool sequences once the evidence path is established.
- [`agent-working-memory-eval`](../agent-working-memory-eval/SKILL.md) —
  Managing extracted evidence in bounded context windows.

---

## Sources

- **Paper**: [Making Every Tool Call Count: Necessary Tool-Evidence Path Rewards for Agentic Vision-Language Models](https://arxiv.org/abs/2609.03493) (arXiv:2609.03493)
- **Praxis source**: `src:2609-03493`
