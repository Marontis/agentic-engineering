# MAPL: Training Small Agent Teams From Preferences

> **Paper**: [Improving LLM Collaboration via Multi-Agent Preference Learning](https://arxiv.org/abs/2609.32827)
> **Praxis source**: src:2609-32827v1
> **Status**: Research Brief. Training method for small cooperative multi-agent systems.

## Why Not a Skill?

MAPL is a fine-tuning recipe (multi-agent RLHF with a learned reward
model, or multi-agent DPO) for two-agent teams of 1.7B to 4B models. It
changes weights, needs many extra rollouts, and was tested with
simulated preferences. What transfers to agent builders without a
training pipeline is a small set of lessons about comparators and
preference data.

## Core Concept

When a multi-agent team has no reliable scalar reward, train it from
pairwise preferences. Each iteration samples joint trajectories from
the current agents and from a comparator policy, labels which pair
member is better, keeps a replay buffer of preference pairs that
down-weights older iterations ("lambda-decay"), and updates the agents
either through a learned reward model plus multi-agent GRPO (MARLHF) or
directly (MADPO). Three paradigms are compared: decentralized agents
with a decentralized comparator (Dec-Dec), centralized agents and
comparator (Cen-Cen), and decentralized agents with a centralized
comparator (Dec-Cen).

## Key Findings

Setting: two-agent teams on TL;DR summarization (Qwen3-1.7B),
CoopHumanEval coding (Qwen2.5-Coder-3B), BFCL parallel function
calling and TravelPlanner trips of up to 5 days and 2 cities
(Qwen3-4B-Instruct-2507). In the experiments, preferences are labelled
from oracle rewards ("annotators label their preferences according to
the following oracle rewards"), not by humans.

- **Close to oracle-reward MARL**: the best MAPL configurations reach
  65.8% pass on CoopHE and 76.4% on Travel, and stay within 1% of
  MAGRPO (trained on the oracle reward) on TL;DR score and Travel pass
  rate. MARLHF slightly beat MAGRPO on CoopHE call rate (40.2% vs
  37.9%) and Travel success (13.1% vs 12.5%) under decentralized
  collaboration.
- **A stronger comparator is not better**: scaling a same-family
  comparator from the agents' size to 4x dropped TL;DR scores from
  86.3% to 66.5% (MARLHF) and from 92.9% to 71.8% (MADPO). The authors
  attribute this to a capacity gap: small agents cannot realize the
  behaviour a stronger comparator prefers. A centralized comparator
  for decentralized agents (Dec-Cen) generally did worst, for the same
  reason plus an information gap.
- **Online beats offline preference data**: with the same total data,
  online collection improved BFCL from 7.5% to 14.8% (MARLHF) and from
  3.1% to 15.3% (MADPO); the lambda-decay buffer was best in most
  domains.
- **Critic-free optimization was more stable**: MAGRPO beat the
  actor-critic variants in all four domains.

**Limitations stated by the authors**: substantially more compute than
standard MARL fine-tuning; MADPO performs poorly on harder domains such
as Travel; preference signals get sparser for larger teams and longer
horizons.

## Relevance to Praxis

- **Comparators and teachers should be reachable.** When a team of
  small agents learns from comparisons or demonstrations, a much
  stronger reference can hurt. Match the comparator to what the agents
  can actually produce, and test before scaling it.
- **Collect preferences from the current policy.** Fixed offline
  preference sets cover the joint policy space poorly; refresh them as
  the agents improve.
- Results come from simulated preferences on small open models with
  two agents. Treat them as directional for real human feedback.

> Source: Improving LLM Collaboration via Multi-Agent Preference Learning (arXiv:2609.32827)
