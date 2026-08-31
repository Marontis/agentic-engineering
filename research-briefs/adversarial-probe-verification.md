# Adversarial Probes for Privacy-Preserving LLM Verification

> **Paper**: [Not to Break, but to Attest: Adversarial Probes for Privacy-Preserving LLM Verification](https://arxiv.org/abs/2608.27954)
> **Praxis source**: `src:2608-27954v1`

## Why Not a Skill?

The procedures (probe generation, zkSNARK circuit construction, Groth16
verification) require specialized cryptographic infrastructure and direct
model access (logits at minimum, embeddings preferred). These are too
domain-specific for general agent engineering and too infrastructure-heavy
for a subtask-level skill.

---

## Core Concept

Use adversarial-style synthetic probes — not to break the model, but to
detect hidden model changes post-deployment. The probes are designed to
amplify logit drift under selective modifications (backdoors, safety
weakening, capability insertion). The verification is bound to a zkSNARK
(Groth16) for privacy-preserving attestation.

### Key Insight

Hidden model changes (backdoors, safety weakening) are typically **selective**
— the model behaves normally on routine prompts and deviates only on specific
inputs. Standard benchmarks miss these changes. Adversarial-style probes are
designed to sit on high-sensitivity manifolds where even small model changes
produce disproportionate logit drift.

### Probe Families

| Family | Access Required | Sensitivity |
|:-------|:---------------|:-----------|
| Token-based | Black-box + tokenizer | Lower |
| Embedding-based | Gray-box (embedding layer) | Higher |
| Stress probes (MLP/attention) | Hypothesis-driven | Highest |

### Verification Flow

1. **Baseline commitment**: At deployment time, run approved model on
   a hidden probe set and commit responses
2. **Audit challenge**: At audit time, re-run probes on deployed model
3. **Consistency check**: Verify that current responses match committed
   baseline within tolerance
4. **zkSNARK binding**: Wrap the consistency check in Groth16 to prove
   consistency without revealing probes, responses, or model internals

---

## Relevance to Praxis

- The **probe-based integrity verification** concept is relevant to Praxis's
  trust layer: detecting when a source or model has silently changed behavior
- The **commitment + verification** pattern maps to Praxis's change-set
  tracking: commit to a state, then verify consistency later
- For the `agent-sandbox-safety` domain, this provides a model-level
  verification approach that complements the behavioral defenses documented
  in the layered-defense-ensemble skill
- The access-tier model (black-box → gray-box → white-box) for probes
  mirrors the AATM adversary tiers from the layered defenses paper
