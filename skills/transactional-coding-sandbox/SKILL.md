---
name: transactional-coding-sandbox
description: >
  Patterns for fault-tolerant sandboxing of AI coding agents using transactional
  filesystem snapshots and ACID-inspired tool execution. Derived from
  arXiv:2512.12806. Covers command interception policies, snapshot-rollback
  algorithms, SLM-based agent architectures, sandbox-aware prompting,
  and compensating transactions for stateful APIs.
source: https://arxiv.org/pdf/2512.12806
---

# Transactional Coding Sandbox

Skill for wrapping AI coding agent tool calls in atomic transactions with
filesystem snapshot isolation, providing guaranteed rollback when commands fail
or produce inconsistent states.

## Core Problem

Autonomous coding agents (OpenInterpreter, AutoGen, etc.) execute shell commands
directly. They operate as "black box" operators that may generate commands which
are syntactically correct but logically flawed, causing:

- Deletion of critical files (`rm -rf /`)
- Corrupted package states (half-finished `pip install`)
- Security vulnerabilities introduced via code edits
- Inconsistent project states that require manual cleanup

Two existing approaches both fail for headless autonomous agents:

| Approach | Why It Fails |
|:---------|:------------|
| **Lightweight local execution** (subprocess) | No safety, no rollback, no isolation |
| **Full containerization** (Docker, VM) | Startup latency (10s+) breaks the think-act-observe loop; no mid-session rollback |
| **Commercial CLIs** (Gemini CLI) | Requires interactive authentication ("Sign in") — 100% failure rate in headless mode |

## Key Insight

Treat every agent tool call as an **atomic transaction** inspired by database
ACID properties. The environment state is either successfully advanced or
perfectly preserved — never left in a corrupted intermediate state.

### Formal Model

```
S_{t+1} = S_t + ΔC    if execution(C) succeeds     (commit)
S_{t+1} = S_t         if execution(C) fails         (rollback)
```

Where `S_t` is the environment state at time t, and `C` is a tool-call (command)
that maps `S_t → S_{t+1}`.

## Architecture: Two-Layer Safety

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: TOOL-CALL SANDBOXING (pre-execution validation)    │
│                                                              │
│   Command C arrives from agent                               │
│   Policy Engine P(C) classifies:                             │
│                                                              │
│   ├── Safe/Whitelisted → execute directly, bypass snapshot   │
│   │   (git status, ls, cat, pwd, echo)                       │
│   │                                                          │
│   ├── Unsafe/Blacklisted → BLOCK immediately                 │
│   │   (rm -rf /, mkfs, dd if=/dev/zero, chmod -R 777 /)     │
│   │                                                          │
│   └── Uncertain/Requires Checkpoint → trigger Layer 2        │
│       (pip install, sed -i, git checkout, npm install)       │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ Layer 2: FAULT RECOVERY (transactional filesystem checkpoint)│
│                                                              │
│   PREPARE:  S_snap ← SNAPSHOT(S_curr)                        │
│   EXECUTE:  Output ← EXECUTE(C)                              │
│                                                              │
│   if ExitCode ≠ 0:                                           │
│     ROLLBACK: Restore S_curr ← S_snap                        │
│     return ERROR("State Rolled Back")                        │
│   else:                                                      │
│     COMMIT:  Discard S_snap                                  │
│     return Output                                            │
└──────────────────────────────────────────────────────────────┘
```

## Algorithm: Transactional Execution Loop

```python
def transactional_execute(command: str, workspace: Path) -> Result:
    classification = policy_engine.classify(command)

    if classification == "unsafe":
        return Error("Policy Violation: command blocked")

    if classification == "safe":
        return execute(command)

    # classification == "uncertain" → transactional path
    snapshot = create_snapshot(workspace)
    try:
        result = execute(command)
        if result.exit_code != 0:
            restore_snapshot(snapshot, workspace)
            return Error(f"State Rolled Back: {result.stderr}")
        else:
            discard_snapshot(snapshot)
            return result
    except Exception as e:
        restore_snapshot(snapshot, workspace)
        return Error(f"State Rolled Back: {e}")
```

## Command Classification Policy

### Safe (bypass snapshot — reduce latency)

Read-only or low-risk commands that cannot corrupt state:
```
git status, git log, git diff, ls, cat, head, tail, wc,
pwd, echo, env, which, python --version, pip list, pip show,
npm list, node --version, cargo --version, rustc --version
```

### Unsafe (block immediately)

Destructive commands with catastrophic potential:
```
rm -rf /, rm -rf ~, rm -rf ., mkfs.*, dd if=/dev/zero,
chmod -R 777 /, chown -R, shutdown, reboot, kill -9 1,
:(){ :|:& };:, > /dev/sda
```

### Uncertain (trigger transactional checkpoint)

State-modifying commands that may fail or cause inconsistency:
```
pip install, pip uninstall, npm install, npm uninstall,
cargo build, make, cmake, sed -i, git checkout, git merge,
git rebase, apt-get install, brew install, docker run,
python setup.py install, cargo install
```

## Snapshot Implementation

### Current Prototype: shutil Copy

Portable, works everywhere, ~1.8s overhead for 250MB workspace:

```python
import shutil
from pathlib import Path

def create_snapshot(workspace: Path) -> Path:
    snapshot_dir = workspace.parent / f".snapshot_{workspace.name}_{int(time.time())}"
    shutil.copytree(workspace, snapshot_dir, symlinks=True)
    return snapshot_dir

def restore_snapshot(snapshot: Path, workspace: Path) -> None:
    shutil.rmtree(workspace)
    shutil.move(str(snapshot), str(workspace))

def discard_snapshot(snapshot: Path) -> None:
    shutil.rmtree(snapshot)
```

### Production Upgrades: Native CoW Snapshots

| Method | Command | Speed | Requirements |
|:-------|:--------|:------|:-------------|
| **ZFS snapshot** | `zfs snapshot pool/workspace@pre_cmd` | Microseconds | ZFS filesystem |
| **Btrfs snapshot** | `btrfs subvolume snapshot workspace .snap` | Microseconds | Btrfs filesystem |
| **OverlayFS** | `mount -t overlay ...` | Instant | Linux kernel 3.18+ |
| **Git shadow tree** | `git stash` / `git stash pop` | Fast | Git repo |

For the prototype's 14.5% overhead to approach zero, use native filesystem
snapshots. ZFS and Btrfs provide copy-on-write semantics that make snapshot
creation nearly free.

## The SLM Thesis

The paper makes a strong case for **Small Language Models** (1M–10B parameters)
over large LLMs for autonomous agent loops:

### Why SLMs for Agents

| Dimension | LLM (70B+) | SLM (1M–10B) | Agent Advantage |
|:----------|:-----------|:-------------|:----------------|
| **Latency** | Seconds per response (API round-trip) | Sub-second (local inference) | Maintains agent "flow", prevents timeouts |
| **Privacy** | Sends code/configs to cloud API | Runs entirely on-premise | "Air-gapped intelligence" for sensitive codebases |
| **Economics** | $0.03–$0.06 per agent run | Fixed electricity + hardware cost | 10–30× cheaper per token at scale |
| **Edge deployment** | Impossible | Feasible on consumer hardware | Enables fleet-of-agents architecture |

### Mixture of Experts (MoE) for Best of Both Worlds

The paper uses **Minimind-MoE** (~26M total parameters) which decouples:
- **Model capacity** (total parameters → knowledge breadth) from
- **Inference cost** (active parameters per token → speed)

A gating network routes each token to specific expert subsets. Only a fraction
of the network activates per token, achieving large-model reasoning at
small-model cost.

### SLM Limitations to Manage

- Reduced reasoning depth and knowledge breadth
- More prone to hallucination outside training distribution
- Smaller context windows requiring chunking strategies
- May need "hand-off" to larger models for high-level architectural planning

## Sandbox-Aware Prompting

A critical behavioral finding: when the sandbox refuses a destructive command,
current SLMs often enter a **"stubbornness loop"** — retrying the same valid
syntax despite the policy violation, because they interpret the refusal as a
syntax error rather than a boundary constraint.

**Solution**: the system message must explicitly inform the agent it is operating
within a transactional sandbox:

```
You are operating within a transactional sandbox. If a command is refused
with a "Policy Violation" error, this means the command is blocked by the
safety policy — it is NOT a syntax error. Do not retry the same command.
Instead, revise your plan to accomplish the goal without using the blocked
command. Think of policy violations as boundary constraints, not bugs.
```

This transforms the sandbox from a passive safety net into a crude form of
**Reinforcement Learning from Environmental Feedback (RLEF)** — refusals act
as negative reward signals that should trigger logical plan revision.

## Compensating Transactions (Future Direction)

The snapshot approach only works for **local filesystem state**. Real-world agents
interact with stateful external APIs that cannot be "un-done" via filesystem
rollback:

| Action | Compensating Action |
|:-------|:-------------------|
| `terraform apply` (provision EC2 instance) | `terraform destroy` |
| Send email via SMTP | Cannot undo — require pre-send confirmation gate |
| `kubectl apply` (deploy pod) | `kubectl delete` |
| INSERT into production database | DELETE or UPDATE to reverse |
| Create DNS record | Delete DNS record |

The sandbox must evolve from a **passive isolation layer** into an **active
orchestration manager** that understands the inverse function of every API call
it permits. This pattern is known as **Sagas** in distributed systems:

```python
class CompensatingSaga:
    def __init__(self):
        self.actions: list[tuple[Callable, Callable]] = []  # (action, compensate)

    def add_step(self, action: Callable, compensate: Callable):
        self.actions.append((action, compensate))

    def execute(self):
        completed = []
        for action, compensate in self.actions:
            try:
                result = action()
                completed.append((result, compensate))
            except Exception:
                # Reverse all completed actions
                for _, comp in reversed(completed):
                    comp()
                raise
```

## Quantitative Results

| Metric | Value |
|:-------|:------|
| **Command interception rate** | 100% (20/20 blacklisted commands blocked) |
| **Rollback success rate** | 100% (20/20 corrupted states recovered) |
| **Latency overhead** | 14.5% (~1.82s per transaction on 250MB workspace) |
| **Baseline execution time** | 4.69s (direct `pip install`) |
| **Sandboxed execution time** | 6.51s (snapshot + execute + commit/rollback) |
| **Gemini CLI headless success** | 0% (requires interactive "Sign in") |

### The Sandbox Tax Argument

The 14.5% overhead is analogous to ECC memory in servers: you pay a linear
performance cost for data integrity. The cost of NOT paying is exponential —
a hallucinated configuration change bringing down a production database has
essentially infinite recovery cost compared to a 1.8-second verification delay.

```
Cost of safety:   O(n)     — linear time overhead
Cost of failure:  O(2^n)   — exponential recovery (system wipe, manual repair)
```

## Infrastructure Reference (Testbed)

| Component | Implementation |
|:----------|:---------------|
| Virtualization | Proxmox VE 9.0 |
| Agent container | LXC container |
| Inference server | Separate VM with GPU passthrough |
| Network isolation | EVPN/VXLAN via VyOS routers (L3 leaf-spine) |
| Storage | ZFS-backed volumes |
| Model | Minimind-v1-MoE (~26M params) via nano-vllm |

## When to Use This Skill

- Building autonomous coding agents that execute shell commands
- Implementing safety layers for headless CI/CD agent pipelines
- Designing rollback mechanisms for agent-driven infrastructure changes
- Adding fault tolerance to any agent that modifies filesystem state
- Creating policy engines for command classification
- Evaluating SLM vs LLM tradeoffs for agent deployment

## Design Patterns to Extract

1. **Three-tier command classification**: safe/unsafe/uncertain with different
   execution paths to minimize overhead while maximizing safety
2. **Snapshot-execute-commit/rollback loop**: ACID semantics for filesystem
   mutations with pluggable snapshot backends
3. **Sandbox-aware system prompts**: teach the agent what a policy violation
   means so it replans instead of retrying
4. **Compensating transactions**: register inverse operations for external API
   calls to enable cross-service rollback
5. **SLM + MoE for agent loops**: decouple capacity from cost for
   latency-sensitive, high-frequency agent execution

## References

- **Paper**: [Fault-Tolerant Sandboxing for AI Coding Agents](https://arxiv.org/abs/2512.12806) — Boyang Yan (University of Virginia)
- **Code**: https://github.com/yanboyang713/Sandboxing-for-AI-Coding-Agents
- **Praxis source**: `src:fault-tolerant-sandboxing-for-ai-coding-agents-a-transactional-approach-to-safe`
