# LLM Agents for Software and Systems Security (Survey)

> **Paper**: [LLM-Based Agents for Software and Systems Security: Approaches, Applications, and Assessment](https://arxiv.org/abs/2608.28490)
> **Praxis source**: `src:2608-28490v1`

## Why Not a Skill?

This is a comprehensive survey paper. It catalogs and taxonomizes existing work
across agent architectures, memory patterns, action spaces, and security
applications. No single transferable subtask procedure can be extracted —
the value is in the reference taxonomy and the identified research gaps.

---

## Survey Taxonomy (AAA Framework)

### Approach
How agents are built for security tasks:

| Dimension | Categories |
|:----------|:----------|
| **Architecture** | Single agent, multi-agent, hierarchical |
| **Memory** | Working memory, long-term (episodic, semantic, procedural) |
| **Perception** | Code, logs, network traffic, binaries, UI |
| **Reasoning & Planning** | Chain-of-thought, ReAct, tree-of-thought |
| **Action Space** | Tool use, code execution, system commands, API calls |
| **Workflow & Orchestration** | Sequential, parallel, debate, pipeline |
| **Self-Improvement & Learning** | Reflection, experience replay, skill accumulation |

### Application
What security tasks agents are applied to:

- Vulnerability detection & analysis
- Exploit development & analysis
- Penetration testing & red-teaming
- Vulnerability repair & hardening
- Intrusion & threat detection, incident response
- Threat intelligence & security operations (SecOps)
- Other: fuzzing, malware analysis, compliance

### Assessment
How agent performance is measured:

- **Metrics**: Success rate, precision/recall, cost efficiency, time-to-detection
- **Datasets**: CTF challenges, CVE databases, synthetic vulnerability suites
- **Gaps**: Lack of standardized benchmarks, inconsistent threat models,
  limited adversarial evaluation

---

## Key Gaps Identified

1. **Insufficient adversarial evaluation**: Most agent evaluations use static
   attack/defense scenarios, not adaptive adversaries
2. **Memory management**: Long-running security tasks (pentesting, monitoring)
   stress memory systems beyond typical agent evaluations
3. **Multi-agent coordination**: Security tasks often require specialist agents
   (recon, exploit, post-exploit) with tight coordination requirements
4. **Reproducibility**: Security agent evaluations are rarely reproducible
   due to environment dependencies and non-determinism

---

## Relevance to Praxis

- The **memory taxonomy** (working, episodic, semantic, procedural) provides
  vocabulary for categorizing the knowledge types Praxis manages
- The **self-improvement patterns** in security agents (reflection, experience
  replay) map to our existing recursive-improvement framework
- The **assessment gaps** reinforce the importance of behavior-aware verification
  (from HarnessLens) and measured defense correlation (from layered defenses)
- This survey is a useful reference for the `agent-sandbox-safety` rules domain
