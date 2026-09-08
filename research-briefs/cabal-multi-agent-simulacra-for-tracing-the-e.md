# CABAL: Multi-Agent Simulacra for Tracing the Effects of Collusive Bidding in Peer Review

> **Paper**: [CABAL: Multi-Agent Simulacra for Tracing the Effects of Collusive Bidding in Peer Review](https://arxiv.org/abs/2609.05227)
> **Praxis source**: `src:2609-05227v1`
> **Primary topic**: Agent Security Findings & Swarm Governance

## Why Not a Skill?

This paper is a survey or critical review that synthesizes existing knowledge across a broad domain. It provides valuable taxonomies and design heuristics, but does not introduce a standalone procedural workflow transferable as an agent subtask.

---

## Core Concept

Recent reports during the AAAI-27 review cycle highlight the risk of reviewers coordinating bids for reciprocal assignment advantage. Prior work treats bidding, reviewer assignment, and review manipulation as separate stages, leaving the lifecycle effects of collusive bidding unclear. Real-world analysis is further constrained by typically unobservable collusive intent and the lack of counterfactuals for the same conference. Motivated by this gap, we introduce \alg, an end-to-end multi-agent simulacra framework for studying reviewer assignment integrity by holding the conference environment fixed and configuring LLM-driven reviewer agents with honest or collusive policies. We further develop an affinity-guided collusive bidding strategy that uses mutual reviewer-paper affinities to construct collusion rings and select target papers, producing expertise-consistent rather than arbitrarily targeted attacks. Controlled experiments show that collusive bidding more than doubles target-paper capture and that assigned colluders score target papers about two points higher than honest co-reviewers, while conference-wide effects remain comparatively modest. Evaluated bid-phase detectors provide only limited evidence of collusion: in a fixed-triplet detector stress test, native positive-bid graphs are confounded by benign affinity, while a Very-High-only diagnostic view enables precise but low-coverage local recovery.

### Key Findings

- **Primary Result**: See abstract for qualitative findings.

## Relevance to Praxis

- Relevant to agent self-improvement loops and harness engineering.
- Documents security findings relevant to multi-agent trust.
