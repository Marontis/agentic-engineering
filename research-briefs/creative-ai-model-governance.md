# Creative AI Model Governance: Storage, Circulation, and Learning

> **Paper**: [Govern the Model, Not Only the Data: Storage, Circulation, and Learning in Creative AI](https://arxiv.org/abs/2609.03800)  
> **Praxis source**: `src:2609-03800`

## Why Not a Skill?

This paper articulates socio-technical governance principles, legal-consensual frameworks, and institutional design patterns for creative AI data commons and federated training. Because it establishes policy foundations rather than an executable coding-agent procedure, it is maintained as a research brief informing knowledge base governance and asset provenance.

---

## Core Concept

Technological solutions such as federated learning are frequently promoted as privacy-preserving panaceas because raw data remains on local devices while only model weights are transmitted. However, the authors demonstrate that federated training inverts the democratic ethos of the federated social web: it decentralizes computational burden while centralizing ownership and control of the resulting trained model in the hands of the orchestrator.

The authors examine three distinct layers at which creative communities steward intellectual and cultural assets:
1. **Storage**: Hosting data, raw media, and artifacts on decentralized or community-controlled infrastructure.
2. **Circulation**: Licensing, syndication, sharing protocols, and access control.
3. **Learning (The Missing Governance Layer)**: Training model weights, fine-tuning representations, and deploying downstream generative capabilities.

Creator governance currently exists at the storage and circulation layers, but abruptly halts at the learning layer: creators may consent to data ingestion, yet possess zero institutional oversight or ownership over how the resulting model weights are commercialized, federated, or deployed.

```
       Three Layers of Creative Community Stewardship
┌─────────────────────────────────────────────────────────────┐
│ 1. Storage      │ Decentralized storage, artist trusts, IPFS│ (Governed)
├─────────────────┼───────────────────────────────────────────┤
│ 2. Circulation  │ Creative Commons, syndication, API access │ (Governed)
├─────────────────┼───────────────────────────────────────────┤
│ 3. Learning     │ Weight updates, fine-tuning, federation   │ ⚠️ UNGOVERNED GAP
└─────────────────────────────────────────────────────────────┘
```

### Four Design Principles for a Model Commons

To close this governance gap, the authors propose four foundational design principles:
1. **Govern the Model, Not Only the Corpus**: Community control must extend to checkpoint weights, deployment permissions, and downstream fine-tuning licenses, rather than ending at raw dataset access.
2. **Legibility at Contribution**: Terms governing model usage, capability boundaries, and attribution mechanisms must be explicitly legible to creators at the exact moment of data ingestion.
3. **Refusal as a First-Class State**: The system must provide mechanical support for irrevocable opt-out, selective unlearning, and weight pruning without requiring complete retraining from scratch.
4. **Accountable Open Stewardship**: Stewardship decisions regarding model fine-tuning, compute allocation, and commercial licensing must occur in open, publicly auditable registries.

---

## Relevance to Praxis

- **Governed Agent Memory**: Mirrors the core principles of Praxis's `governed-knowledge-graph` skill: data provenance, attribution claims, and deletion rights must be first-class metadata attached to every ingested node.
- **Skill Provenance**: Rules and skills extracted from proprietary or community corpora require explicit attribution headers and verifiable source hashes.
