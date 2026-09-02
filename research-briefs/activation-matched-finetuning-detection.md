# Detecting Hidden LLM Behaviors via Activation-Matched Finetuning

> **Paper**: [Detecting Hidden Behaviors in LLMs via Activation-matched Finetuning](https://arxiv.org/abs/2609.00351)
> **Praxis source**: src:2609-00351v1

## Why Not a Skill?

Offline model weight inspection and security audit technique; key rule captured in 
ules/agent-sandbox-safety.md.

---

## Core Concept

Backdoors, sleeper-agent triggers, and sandbagging behaviors remain dormant under benign inputs. Activation-matched finetuning detects these latent behaviors without knowing the trigger in advance: given a suspect model and a benign anchor model, the anchor is finetuned to match suspect activations on benign prompts. Prompts that elicit anomalous activation residuals isolate dormant backdoors.

## Relevance to Praxis

- Emphasizes the need for activation residual auditing when integrating open-weights models into agent systems.
