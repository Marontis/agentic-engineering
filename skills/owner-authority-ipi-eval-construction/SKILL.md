---
name: owner-authority-ipi-eval-construction
description: >
  Convert existing multi-step LLM agent utility benchmarks or production
  task suites into end-to-end indirect prompt injection (IPI) security
  evaluation suites by classifying trajectory read/write dependencies,
  enforcing single-owner participant vs. bystander authority boundaries,
  pairing action-deflection with action-injection rubrics across three
  quality gates, and reporting reach-adjusted Effective ASR alongside Net
  ASR and Clean Utility. Derived from MetaPI (arXiv:2611.10026).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Owner-Authority Indirect Prompt Injection Evaluation Construction

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Hand-crafted indirect prompt injection (IPI) benchmarks (`AgentDojo`, `InjecAgent`, `WASP`) require months of bespoke environment engineering, cover narrow tool surfaces, and saturate quickly—yet naively stuffing adversarial strings into existing utility benchmarks (`AppWorld`, `VitaBench`, `Terminal-Bench`) produces invalid security tests. Three failure modes corrupt naive conversions: (1) injecting into principal-authored chat turns or platform metadata violates the threat model; (2) treating legitimate data changes by a transaction participant (such as a merchant changing their own item price) as "prompt injection" conflates ordinary data ownership with authority escalation; and (3) reporting raw `Net ASR` alone rewards capability-destroying defenses that crash or halt before ever reaching the injected observation (`CaMeL` scores `0.0%` Net ASR on `Terminal-Bench` with `0.0%` Clean Utility and `0/0` anchor reach).

This skill provides a defensive four-stage evaluation-engineering workflow (`MetaPI`) that converts any deterministic multi-step agent utility benchmark or enterprise regression suite into a validated, reproducible IPI security benchmark at `$0.32–$0.39` per validated test case (`183` validated cases across `107` tasks spanning `AppWorld`, `VitaBench`, and `Terminal-Bench`).

## When to Use

- **Building security regression suites from existing product evals** — turning internal multi-app API, customer-support, or containerized CLI/coding golden tasks into IPI defense benchmarks without building synthetic toy sandboxes from scratch.
- **Evaluating candidate IPI defenses (`Spotlighting`, `Sandwiching`, `DRIFT`, `MELON`, `CaMeL`, guardrail classifiers)** — measuring real security–utility–latency trade-offs across both `action-deflection` (corrupted arguments to expected tools) and `action-injection` (unauthorized tool calls).
- **CI/CD negative security testbeds for self-improving harnesses** — constructing the immutable held-out security suite required by `"DO: Pass every self-modification through one acceptance gate"` in [`rules/recursive-improvement.md`](../../rules/recursive-improvement.md).

## When Not to Use

- **Tasks with zero external third-party data reads** — pure reasoning, math, or closed-world code synthesis tasks that never read untrusted external records, files, or tool responses have no valid IPI surface (screen these out statically before trajectory collection).
- **Direct user-turn jailbreak evaluation** — the principal's own conversation turns are **never** an indirect injection surface; use direct misuse benchmarks for malicious-principal threat models.
- **Red-team payload search mechanics** — this skill defines **where** an injection surface is valid, **what** authority-exceeding security rubrics to test, and **how** to validate and score defenses end-to-end; for black-box payload perturbation search during hardness verification, delegate to [`agentic-prompt-injection-search`](../agentic-prompt-injection-search/SKILL.md).

---

## Procedure

### Step 1: Collect Deterministic Clean Trajectories and Classify Read/Write Causality

1. **Pre-screen tasks for third-party content**: Statically filter your utility suite to retain tasks whose environment snapshots, databases, or mounted filesystems contain third-party external records (for example, `30/50` `Terminal-Bench` tasks survive third-party file screening).
2. **Cache deterministic clean reference runs**: Execute the undefended reference agent at `temperature = 0` under a bounded step cap (e.g., `40` steps), caching every tool invocation, structured return payload, and final task-utility score by content hash. Retain only tasks where the reference trajectory cleanly exercises the intended workflow.
3. **Classify every trajectory action into three causal tiers**:
   - **Necessary writes**: Tool calls or commands that mutate external state (payments, messages, database updates, file writes outside scratch) whose side effects are required for task completion.
   - **Necessary reads**: Tool calls or file reads that supply concrete identifiers, values, or preconditions consumed by downstream necessary writes.
   - **Accidental reads**: Untrusted records returned alongside necessary reads (e.g., unrelated inbox messages, neighboring search hits, bystander comments) whose values are *not* needed by any necessary write.

### Step 2: Partition Single-Owner Segments and Enforce the Owner-Authority Boundary

1. **Decompose observations into single-owner provenance segments**: Split each structured JSON response, webpage, email thread, or repository file into fine-grained fields attributed to a single real-world author/entity.
2. **Hard-exclude non-injectable surfaces**:
   - Never place test injections in **principal-authored content** or **user conversation turns** (`the conversation is not an injection surface`).
   - Never place test injections in **platform-generated system metadata** (timestamps, database primary keys, HTTP status codes, immutable system headers) or JSON dictionary keys.
3. **Label each injectable segment as `Participant` vs. `Bystander` and enforce the Owner-Authority Rule**:
   - **Bystander segment (`accidental read`)**: Owned by a third party uninvolved in the user's requested transaction (e.g., a spammer's email in an inbox search, an unrelated forum commenter). The bystander holds **zero authority** over the user's task; any induced change to the user's necessary writes or unauthorized tool execution exceeds their authority.
   - **Participant segment (`necessary read`)**: Owned by a party legitimately involved in the step (e.g., a restaurant listing on a food-ordering task, a job candidate's resume in an HR screening workflow, an upstream package README). **Admit a test objective on a participant segment ONLY if the target effect exceeds what that owner could achieve simply by modifying data legitimately under their own control**:
     - *Reject (within owner authority — NOT valid IPI)*: A merchant changing their own menu price or item availability; a candidate editing their own listed phone number.
     - *Admit (exceeds owner authority — valid IPI)*: A merchant redirecting the user's delivery address to an external drop site or ordering from a second store; a candidate's resume causing the agent to record `"HR background check approved"` or exfiltrate another applicant's salary record.

### Step 3: Pair Action-Deflection and Action-Injection Objectives Under Three Quality Gates

For each valid segment, synthesize structured security test specifications covering **both** objective families (do not restrict benchmarks to foreign tool calls alone):

1. **Two Objective Families**:
   - **Action-Deflection (`56.8%` of `MetaPI`, `104/183` cases)**: Corrupts parameters, recipients, amounts, paths, or targets of a **necessary write** the agent was *already* going to call (e.g., diverting a legitimate payment recipient or changing a deployment target). Always pair with a deterministic `tool_call` argument-matching rubric. Action-deflection consistently bypasses tool-allowlist and trajectory-comparison defenses (`DRIFT`, `MELON`, `Spotlighting`) at higher rates than foreign tool injection.
   - **Action-Injection (`43.2%` of `MetaPI`, `79/183` cases)**: Induces an unauthorized **new** external tool call, shell command, or confidential data exfiltration outside the clean write set. Prefer deterministic `tool_call` / filesystem-state rubrics (`149/183` total cases in `MetaPI`); reserve multi-criteria `llm_judge` rubrics (`34/183`) strictly for whole-run text-exfiltration effects that leave no structured tool trace.
2. **Enforce Three Automated Pre-Admission Quality Gates** before accepting any test specification:
   - **Gate 1 — Structural Feasibility**: Verify that the replacement anchor appears **uniquely** in the environment snapshot, preserves valid JSON/YAML/source syntax after insertion, never alters dictionary keys, and **preserves any ground-truth values still needed by unrelated clean task steps** so the benign task remains solvable.
   - **Gate 2 — Authority & Harmfulness**: Confirm against Step 2's Owner-Authority Rule that the rubric outcome strictly exceeds the segment owner's legitimate data privileges.
   - **Gate 3 — Scoreability & Clean-Baseline Non-Contamination**: Run the rubric evaluator against the cached **clean undefended trajectory** (and clean defended trajectory); immediately discard any `baseline_contaminated` candidate where normal benign execution already satisfies the attack rubric (`0%` false-positive baseline contamination).

### Step 4: Validate From Scratch and Report Dual Reach-Adjusted Metrics

1. **Verify exploitability from scratch (`Step 1` replay)**: Do not score single-turn prompt completions on frozen prefixes alone. Materialize the modified environment snapshot, reset the sandbox, and execute the full agent loop **from Step 1** so multi-step state dependencies and dynamic user simulators evolve naturally. Retain specifications verified as reachable and actionable under bounded black-box testing (e.g., `<= 12` adaptive refinement rounds via [`agentic-prompt-injection-search`](../agentic-prompt-injection-search/SKILL.md)).
2. **Instrument defense hooks across all 6 lifecycle stages**: Expose uniform interception hooks (`user_input`, `pre_model`, `post_model`, `pre_tool`, `post_tool`, `observation`) so prompt-level (`Sandwiching`, `Spotlighting`), detector-level (`DataSentinel`, `PromptArmor`), trajectory-monitoring (`MELON`, `DRIFT`), and capability/architectural (`CaMeL`, `Meta-SecAlign`) defenses are tested under identical harness conditions.
3. **Always report four joint metrics—separating genuine blocking from anchor non-reach**:
   - **Clean Utility (`Uti`)**: Task completion score on the unmodified clean tasks with the defense enabled.
   - **Net ASR (`S / N`)**: Fraction of all $N$ validated test cases where the attack rubric triggers from scratch.
   - **Effective ASR (`S / (N - U)`)**: Attack success rate conditioned on the agent actually reaching the injected observation, removing $U$ **confirmed non-reached cases** where the defense caused an early crash, refusal, or alternative path before reading the anchor.
   - **Token / Latency Overhead**: Total input + output token multiplier relative to the undefended agent.

---

## Reference Defense Trade-Offs Across `183` Validated Cases (`arXiv:2611.10026`)

Evaluated with `deepseek-v4-flash` across `AppWorld` (`51` cases / `37` tasks), `VitaBench` (`87` cases / `46` tasks), and `Terminal-Bench` (`45` cases / `24` tasks):

| Defense | `AppWorld` Net / Eff ASR (`Clean Uti`) | `VitaBench` Net / Eff ASR (`Clean Uti`) | `Terminal-Bench` Net / Eff ASR (`Clean Uti`) | Token Overhead |
|:---|:---:|:---:|:---:|:---:|
| **None (Undefended)** | `50.0%` / `58.5%` (`82.5%`) | `45.9%` / `47.0%` (`96.0%`) | `44.4%` / `52.6%` (`82.2%`) | `1.00x` |
| **Sandwiching** | `20.8%` / `27.8%` (`73.6%`) | `24.7%` / `25.3%` (`88.8%`) | `22.2%` / `25.6%` (`68.9%`) | `1.09x–1.22x` |
| **Spotlighting** | `25.0%` / `32.4%` (`80.4%`) | `20.0%` / `20.5%` (`92.6%`) | `37.8%` / `41.5%` (`77.8%`) | `1.09x–1.14x` |
| **DataSentinel** | `41.7%` / `48.8%` (`77.1%`) | `43.5%` / `44.6%` (`92.5%`) | `28.9%` / `34.2%` (`73.3%`) | `1.04x–1.06x` |
| **PromptArmor** | `35.4%` / `35.4%` (`78.0%`) | `43.5%` / `43.5%` (`90.5%`) | `35.6%` / `35.6%` (`82.2%`) | `1.11x–1.19x` |
| **MELON** | `35.4%` / `44.7%` (`65.1%`) | `25.9%` / `26.5%` (`88.5%`) | `26.7%` / `30.0%` (`66.7%`) | `1.66x–1.73x` |
| **DRIFT** | `22.9%` / `26.8%` (`70.5%`) | `18.8%` / `21.1%` (`83.7%`) | `8.9%` / `11.8%` (`68.9%`) | `1.41x–1.82x` |
| **CaMeL** | `0.0%` / `0.0%` (`33.7%` Uti, `20` reached) | `N/A` (incompatible w/ user sim) | `0.0%` / `undef` (`0.0%` Uti, `0/0` reached!) | `2.28x–2.31x` |
| **Meta-SecAlign** (`Llama-3.1-8B`) | `2.1%` / **`25.0%`** (`22.9%` Uti, `1/4`) | `11.8%` / **`35.7%`** (`13.6%` Uti, `10/28`) | `N/A` (context OOM) | — |

Notice why reporting `Effective ASR` + `Clean Utility` is mandatory: `Meta-SecAlign`'s apparent `2.1%` Net ASR on `AppWorld` becomes **`25.0%` Effective ASR (`1/4`)** once `44` non-reached tasks caused by `22.9%` clean utility are excluded, and `CaMeL`'s `0.0%` Net ASR on `Terminal-Bench` reflects **`0/0` anchor reach (`0.0%` Clean Utility)**.

## Pitfalls to Avoid

- **Skipping `Participant` (`necessary read`) segments**: Restricting injections to bystander spam misses `43%–69%` of real attack surfaces (`22/51` `AppWorld`, `41/87` `VitaBench`, `31/45` `Terminal-Bench`), where the agent *must* parse untrusted participant values to complete its task.
- **Overwriting clean task values inside `Participant` segments**: Replacing an entire record rather than appending or preserving task-essential attributes makes Clean Utility drop even when the agent resists the injection, confounding security and utility metrics.
- **Testing with safety-refusing red-team models alone**: Frontier models with strict outgoing harm filters may refuse to synthesize realistic test cases (`gpt-5.6-luna` red-team yields `29%` ASR vs. `>= 50%` for `deepseek-v4-flash`, `kimi-k3`, and `claude-sonnet-5` on `AppWorld`), underestimating downstream deployment risk (`> 20%` ASR even on closed-source frontier victims).

## Related Skills & Rules

- [`agentic-prompt-injection-search`](../agentic-prompt-injection-search/SKILL.md) — Budget-bounded black-box perturbation search used to verify case hardness on defended harnesses.
- [`principal-context-permission-intersection`](../principal-context-permission-intersection/SKILL.md) — System-level Principal Context (`Conflux`) enforcement at effectful tool boundaries.
- [`compile-then-execute-web-agent-gateway`](../compile-then-execute-web-agent-gateway/SKILL.md) — Offline typed compilation to isolate control flow from untrusted web observations.
- [`rules/agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — Benchmark preflight certification and reach-adjusted security evaluation rules.
- [`rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DON'T: Rely on instruction-stripping sanitizers or tool-name allowlists to stop task-tampering indirect prompt injections"`.
