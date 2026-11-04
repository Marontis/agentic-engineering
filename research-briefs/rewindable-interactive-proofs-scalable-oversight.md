# Efficient Scalable Oversight via Rewinding (Rewindable Interactive Proofs)

> **Source**: [arXiv:2610.40535](https://arxiv.org/abs/2610.40535) — *Efficient Scalable Oversight via Rewinding* (Guan et al., published 2026-10-29)  
> **Praxis ID**: `src:2610-40535`  
> **Tier**: Research Brief

## Summary

Scalable oversight protocols face a fundamental trade-off: **Multi-Agent Debate** requires at least one truthful prover and blows up honest prover compute exponentially with rounds, whereas **cryptographic proofs (SNARGs)** eliminate the truthful-prover assumption using a single prover but incur heavy cryptographic hashing and Merkle-commitment overhead and cannot verify black-box human/oracle queries without formalizing the oracle as a circuit. Guan et al. resolve both limitations by introducing **Rewindable Interactive Proofs (RIPs)**, exploiting a capability natural to hosted AI runtimes: the verifier controls the prover's execution environment and can **checkpoint and rewind** the prover's state across branches so post-rewind answers cannot depend on queries made on sibling branches. Compiling Interactive Oracle Proofs (IOPs) into RIPs verifies any $\varepsilon$-robust oracle Boolean circuit $C^O$ of size $N' = S + n + m$ with $q_C$ oracle gates at soundness error $2^{-\sigma}$ using only $O(\sigma \min\{q_C, 1/\varepsilon\})$ verifier oracle queries, $\widetilde{O}(\sigma(n + m + 1/\varepsilon))$ online verifier time, and linear $O(\sigma N') + \widetilde{O}(\sigma/\varepsilon)$ prover time—with *zero* cryptographic assumptions (statistical soundness against unbounded provers) and *zero* truthful-prover assumptions.

## Why Not a Skill?

This paper is a complexity-theoretic and cryptographic foundation study operating over Boolean circuits (`oversight-rip` in Rust using Binius/Ligero/Flock polynomial IOPs). As the authors explicitly note in Section 6.4, their experiments treat saving and restoring model state as zero-cost and evaluate synthetic Boolean circuits (sparse-view MNIST majority gates and BLAKE3 compression circuits) rather than natural-language LLM agent trajectories. It provides theoretical context and architectural principles for state-rewinding oversight rather than a directly applicable LLM prompt/code skill.

## Experimental Scope

- **Theoretical Protocol**: Compiler from Interactive Oracle Proofs (TensorSwitch / HyperPlonk / Ligero sumcheck + polynomial commitment) to Rewindable Interactive Proofs (RIPs) over $\varepsilon$-robust oracle circuits $C^O$. Also proves exact soundness equivalence between $p$-prover MIPs and single-prover RIPs ($\epsilon_{\text{RIP}} = \epsilon_{\text{MIP}}$).
- **Experiment 1 (`oversight-rip` on MNIST Majority Oracle Circuits)**: Rust implementation timed single-threaded on AWS Graviton4 cores at soundness error $\le 2^{-40.53}$ (target $2^{-40}$). Evaluates majority-vote circuits calling $q_C \in \{2^8, 2^{10}, \dots, 2^{26}\}$ sparse 6-pixel MNIST oracle views (59.4% base accuracy) across the first `50` MNIST test images with robustness $\varepsilon \ge 1/8$ (median robustness `0.30`–`0.32`).
- **Experiment 2 (Flock BLAKE3 IOP Compiled to RIP vs SNARG)**: Compares standard Flock SNARG prover times (with Merkle tree commitments and 128-bit offline grinding security) against the RIP-compiled prover (no Merkle commitments, on-demand FFT row evaluation, $2^{-42.4}$ to $2^{-42.9}$ online interactive soundness) across witness sizes from $2^{22}$ to $2^{34}$ bits ($2^8$ to $2^{20}$ BLAKE3 compressions; median of `3` runs on 1 Graviton4 core).

## Key Quantitative Findings

### 1. MNIST Majority Oracle Circuit Scaling (`Table 1`, Soundness $\le 2^{-40.53}$)

| Circuit Oracle Gates ($q_C$) | Verifier Oracle Queries | Direct Circuit Eval Time | Verifier Online Time Multiple | Prover Time Multiple |
|:-----------------------------|:------------------------|:-------------------------|:------------------------------|:---------------------|
| $2^8$ (`256`) | `76` | `0.064 μs` | `6,976×` (`0.45 ms`) | `4,809×` |
| $2^{10}$ (`1,024`) | `74` | `0.238 μs` | `2,081×` | `1,635×` |
| $2^{12}$ (`4,096`) | `75` | `0.936 μs` | `558×` | `567×` |
| $2^{14}$ (`16,384`) | `75` | `3.73 μs` | `172×` | `237×` |
| $2^{16}$ (`65,536`) | `76` | `14.9 μs` | `46.2×` | `117×` |
| $2^{18}$ (`262,144`) | `76` | `59.6 μs` | `13.4×` | `79.5×` |
| $2^{20}$ (`1,048,576`) | `76` | `238.3 μs` | `3.97×` | `64.8×` |
| $2^{22}$ (`4,194,304`) | `76` | `953.1 μs` | `1.17×` | `60.9×` |
| $2^{24}$ (`16,777,216`) | `78` | `3.83 ms` | **0.39×** | `59.2×` |
| $2^{26}$ (`67,108,864`) | **80** (`840,000×` fewer) | `15.51 ms` | **0.12×** (`1.9 ms`) | **58.8×** (`0.9 s`) |

- **Crossover Point**: Verifier online runtime becomes strictly faster than direct circuit evaluation above **~`7 million` oracle gates** (reaching `0.12×` direct evaluation time and `840,000×` fewer oracle queries at $q_C = 2^{26}$), while prover overhead stabilizes at `~59×` (`0.9 s`).

### 2. BLAKE3 Prover Speedup: RIP vs. Cryptographic SNARG (`Table 2`)

| Witness Size (bits) | BLAKE3 Compressions | Flock SNARG Prover | RIP Prover (Rewound) | Prover Speedup |
|:--------------------|:--------------------|:-------------------|:---------------------|:---------------|
| $2^{22}$ | $2^8$ (`256`) | `89.9 ms` | `46.7 ms` | **1.92×** |
| $2^{24}$ | $2^{10}$ (`1,024`) | `101.6 ms` | `54.7 ms` | **1.86×** |
| $2^{26}$ | $2^{12}$ (`4,096`) | `153.9 ms` | `86.9 ms` | **1.77×** |
| $2^{28}$ | $2^{14}$ (`16,384`) | `480.1 ms` | `223.7 ms` | **2.15×** |
| $2^{30}$ | $2^{16}$ (`65,536`) | `1.23 s` | `694.2 ms` | **1.77×** |
| $2^{32}$ | $2^{18}$ (`262,144`) | `4.81 s` | `2.66 s` | **1.81×** |
| $2^{34}$ | $2^{20}$ (`1,048,576`) | `19.8 s` | `10.6 s` | **1.86×** |

## Architectural Requirements for Rewind-Based Oversight

When applying state-rewinding verification to AI agents:
1. **No Un-Rewound Side Channels**: The prover must not write to any external memory, file, or network state that persists across a state restore; otherwise a dishonest prover can detect which branch was queried first and adapt its subsequent answers.
2. **Deterministic Random-Tape Checkpointing**: The saved checkpoint must include the prover's PRNG seed / sampling tape so that deterministic prefixes are reproduced identically up to the branching query.
