---
name: autonomous-environment-exploration
description: >
  Training-free recursive self-improvement framework for autonomous agent adaptation
  to unfamiliar environments (APIs, CLI tools, OS environments). Coordinates curriculum,
  actor, and verifier agents via broad-then-deep exploration to construct frozen,
  reusable causal memory without model weight updates. Derived from RSIAgent (arXiv:2609.15364).
source: https://arxiv.org/abs/2609.15364
---

# Autonomous Environment Exploration

Use this skill when deploying an LLM agent into a novel or under-documented software environment—such as a new command-line utility, internal API, proprietary operating system interface, or complex sandbox—where pretrained knowledge is incomplete or prone to hallucination.

## When to Use

- Agents bootstrapping within a newly provisioned development container, sandbox, or target platform.
- Unfamiliar or custom command-line tools, APIs, or GUI applications lacking comprehensive documentation.
- Pre-task environment calibration: probing available tools, file system permissions, network limits, and hidden constraints before executing high-stakes user tasks.
- Constructing durable, transferable environment playbooks that can be frozen and shared across agent sessions without model fine-tuning.

## Core Insight

Agents deployed to new environments fail primarily because their pretrained priors do not account for environment-specific nuances: idiosyncratic flag formats, hidden state mutations, subtle failure codes, and environment dependencies. Traditional approaches either rely on manual human prompt engineering or expensive supervised fine-tuning.

**RSIAgent** demonstrates that agents can achieve recursive self-improvement in new environments purely through **autonomous causal memory construction** without updating model weights. By coordinating three specialized agent roles:
1. A **Curriculum Agent** designing progressive exploration tasks
2. An **Actor Agent** executing exploratory tool actions
3. A **Verifier Agent** validating ground-truth consequences and extracting causal triplets `(Condition, Action, Consequence)`

under a **broad-then-deep exploration strategy**, agents uncover environment structures, boundary constraints, and error recovery pathways. On benchmarks such as OSWorld-v2 and Agent's Last Exam, this frozen causal memory enables open-source models (e.g. Kimi-K3, GLM-5.3) to outperform frontier models including GPT-6.

---

## Procedure

```
Unfamiliar Target Environment
              │
              ▼
[Phase 1: Broad Self-Exploration (Breadth Mapping)]
  ├── Identify Top-Level Affordances (--help, man pages, list commands, env vars)
  └── Map Global Topology & Component Surface
              │
              ▼
[Phase 2: Curriculum-Driven Deep Exploration (Depth Probing)]
  ├── Curriculum Agent: Synthesizes Boundary Tasks & Edge Cases
  ├── Actor Agent: Executes Trajectories in Isolated Sandbox
  └── Verifier Agent: Validates Ground Truth & Flags Discrepancies
              │
              ▼
[Phase 3: Causal Triplet Extraction]
  └── Distill Observations into (Precondition, Action, Consequence) Triples
              │
              ▼
[Phase 4: Causal Memory Consolidation & Freezing]
  ├── Deduplicate & Synthesize into Environment Skill Playbook
  └── Freeze Memory for Zero-Shot Reuse by Downstream Task Agents
```

### Step 1: Execute Broad Self-Exploration (Breadth Mapping)

Before executing complex tasks, launch parallel shallow probing runs to map the environment's capabilities:

1. **Introspect Built-ins and Tool Registry**:
   - Query available binaries, scripts, or exposed API endpoints:
     ```bash
     which <tool> || type <tool>
     <tool> --help || <tool> -h || man <tool>
     ```
   - Inspect environment variables, system architecture, shell versions, and user permission boundaries (`whoami`, `uname -a`, `id`).
2. **Catalog Surface Affordances**:
   - Construct an initial inventory of available subcommands, input arguments, and expected output formats.

### Step 2: Formulate Progressive Exploration Curricula

Deploy the Curriculum Agent to generate synthetic, non-destructive exploration scenarios ranked by complexity:

1. **Level 1 (Basic Operational Tasks)**: Read-only queries, status checks, format inspections (e.g., querying system status, parsing sample files).
2. **Level 2 (State Mutation & Inversion)**: Creating temporary resources, validating persistence, and rolling them back (e.g., creating a temp directory, checking permissions, cleaning up).
3. **Level 3 (Boundary Probing & Fault Injection)**: Testing invalid arguments, rate limits, missing dependencies, and timeout behaviors to trigger and capture exact error messages and exit codes.

### Step 3: Run the Actor-Verifier Execution Loop

For each curriculum task:

1. **Actor Execution**:
   - The Actor Agent executes actions step-by-step within a dedicated sandbox or temporary namespace.
   - For every tool call, record:
     - Exact invocation syntax
     - Pre-execution environmental context
     - Full stdout, stderr, and return codes
2. **Verifier Outcome Validation**:
   - The Verifier Agent queries independent ground-truth state (e.g., checking filesystem changes, reading process tables, running verification assertions) rather than trusting model self-reports.
   - If the task failed or produced unexpected side-effects, the Verifier analyzes the error and instructs the Actor to attempt compensating repair actions.

### Step 4: Extract and Formalize Causal Triplets

Convert validated exploration trajectories into structured causal triplets:

```json
{
  "triplet_id": "causal_os_042",
  "condition": {
    "os": "windows",
    "shell": "powershell",
    "prerequisite": "Path contains spaces or special characters"
  },
  "action": {
    "pattern": "& \"$BinaryPath\" @Arguments",
    "avoid": "Direct string interpolation without call operator (&)"
  },
  "consequence": {
    "success_outcome": "Clean execution without parameter splitting",
    "failure_if_ignored": "ParserError: Unexpected token in expression or statement"
  }
}
```

### Step 5: Consolidate and Freeze Causal Memory

1. **Merge Triplet Graph**: Group triplets by tool, error pattern, or subtask type. Eliminate redundant trials.
2. **Synthesize into Frozen Playbook**: Format findings into a standard reference document or skill file (`SKILL.md` or `playbook.json`).
3. **Freeze for Production**: Once generated, freeze this memory. Downstream task-solving agents load it into context as established factual ground truth without additional exploration overhead.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Manifestation | Concrete Mitigation |
|:-------------|:--------|:--------------|:--------------------|
| **Destructive Exploration** | Actor executes unconstrained mutation commands during Level 2/3 probing | File deletion, system lockup, network disconnection | Sandbox isolation: execute in container/scratchdir; prohibit destructive commands (`rm -rf`, system reboots) in curriculum prompts. |
| **Self-Report Verification Bias** | Verifier relies on Actor's self-generated text instead of environment state | Hallucinated task success; corrupt causal memory | Decoupled verification: Verifier must inspect real artifacts, exit codes, and independent check scripts. |
| **Shallow Exploration Trap** | Agent tests only happy-path scenarios, skipping error regimes | Downstream tasks fail when hitting real-world edge cases | Explicit Level 3 fault injection: curriculum must mandate testing invalid inputs and boundary limits. |
| **Causal Memory Bloat** | Storing full raw command logs instead of synthesized triplets | Context window exhaustion; high token overhead | Distill traces into canonical `(Condition, Action, Consequence)` rules and discard raw session transcripts. |

## Cross-References

- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) — Snapshot-and-rollback safety for exploratory action execution.
- [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) — Consolidating raw execution traces into compounding persistent knowledge.
- [`counterexample-guided-repair`](../counterexample-guided-repair/SKILL.md) — Using explicit counterexample witnesses to refine artifact generation.
