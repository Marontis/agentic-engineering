# CUA-Sandbox: Shared Runtimes, Private State Capsules for Agent RL Environments

> **Paper**: [CUA-Sandbox: Efficient Environments for Computer-Use Agent Reinforcement Learning](https://arxiv.org/abs/2609.32750)
> **Authors**: Yan, Jiao, Liu et al. (A*STAR, HKUST, NUS, NTU and others)
> **Praxis source**: src:2609-32750v1
> **Status**: Research Brief — systems paper on environment infrastructure

## Why Not a Skill?

The contribution is an environment system for computer-use agent training
(web apps, desktop apps), not an agent-side procedure. Building it requires
per-application resource contracts and routing for databases, files and
sessions. The design principles are worth knowing when you run many agent
environments in parallel; the implementation is application-specific.

---

## Core Concept

Standard practice gives each parallel environment its own container with a
fully initialized application stack, paying the memory and start-up cost
each time. CUA-Sandbox separates **mutable state** from **reusable
initialized processes**:

- **State capsules** hold a trajectory's private state: authoritative
  (databases, files), derived (caches, indexes) and ephemeral (IPC,
  displays), as an immutable base plus private copy-on-write deltas.
- **State-scoped bindings** route each environment's requests to its own
  data branch, namespace and endpoint while processes are shared.
- **Transactional lifecycle**: reset, clone and fork act on capsules. A
  transition freezes routes, drains in-flight work, stages the successor and
  publishes the new binding atomically, so no request runs against a mix of
  old and new state.

Resources that cannot be shared safely fall back to private backends.

## Key Findings

- At 8 concurrent environments: throughput 2.22× (WebArena), 6.20×
  (VisualWebArena), 3.08× (OSWorld) vs Docker; memory 4.5×, 9.2×, 3.2× lower.
  At 16 environments throughput gains were 2.45×, 3.52× and 5.14×.
- Preparation time fell from 68.85 s to 25.68 s (WebArena) and 6.964 s to
  0.633 s (VisualWebArena).
- Agent scores were equal to or above Docker; GPT-5.6-Terra was +0.54 to
  +3.33 points across the three benchmarks, and the benefit carried through
  SFT and on-policy RL.
- **Atomic publication matters**: publishing bindings directly produced
  mixed-generation execution in 100/100 stress trials; the full protocol
  produced none.
- Without copy-on-write, creation latency rose 77× and fork latency 88× on a
  3.6 GB capsule, and the storage delta grew from 0.11 MiB to 3.67 GiB.

## Relevance to Praxis

- Reset and fork are transactions. Any environment pool that reuses
  processes across episodes must make state switches atomic, or episodes
  silently read another episode's state, which corrupts rewards and evals.
  The 100/100 mixed-generation result is the warning.
- Same family as "DO: Snapshot before uncertain commands" and "DO: Prefork
  sandbox environments on predicted execution branches"
  (`rules/agent-sandbox-safety.md`), and
  [`transactional-coding-sandbox`](../skills/transactional-coding-sandbox/SKILL.md),
  [`speculative-sandbox-scheduler`](../skills/speculative-sandbox-scheduler/SKILL.md),
  [`high-fanout-sandbox-memory-compression`](../skills/high-fanout-sandbox-memory-compression/SKILL.md).
- Shared processes weaken isolation between environments. That is acceptable
  for training on benign benchmark apps; it is not a containment boundary
  for untrusted or adversarial agents (see "DON'T: Use application-layer
  tripwires or PID signals as the containment boundary for a rogue agent",
  `rules/agent-sandbox-safety.md`). The paper does not evaluate security
  isolation.
- Limits stated by the authors: maximum environment density and broader
  write workloads not yet characterized.

> Source: Yan et al., "CUA-Sandbox: Efficient Environments for Computer-Use
> Agent Reinforcement Learning" (arXiv:2609.32750)
