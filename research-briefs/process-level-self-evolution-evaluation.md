# Process-Level Evaluation of Self-Evolving Agents (EvoPathBench)

> **Source**: Lin, Liu, Bai et al., arXiv:2609.24663, Sep 2026
> **Status**: Research Brief — benchmark plus mechanism analysis of acceptance gates

## Why Not a Skill?

The contribution is a benchmark (1,800 ordered streams over trading tasks) and an empirical study of ten memory and skill-evolution methods. The evaluation protocol is reusable: freeze artifacts at each checkpoint, re-test the same capability on held-out episodes, and difference against a non-evolving baseline and a state-off run. But it is a measurement design, not an agent procedure. Its most actionable result concerns acceptance gates, which is rule material (deconfliction item H7).

## Core Concept

Endpoint scores hide how capabilities change during self-evolution. EvoPathBench holds the base model, tools, and executor fixed. It lets memories, skills, or workflows evolve over five update opportunities per stream, and freezes a read-only copy at each checkpoint K0–K5 for testing on held-out episodes that never feed updates. Three stream templates measure three capabilities:

- **Accumulation** (learning generalization): near-distribution vs transfer held-out episodes.
- **Interference** (capability retention): the focal capability is learned by K2 and retested at K5 after three unrelated updates.
- **Reversal** (rule adaptation): the learned relation flips after K3, and the method must revise it.

Two paired differences attribute the gains. **CEG** is the evolving method minus a non-evolving baseline on the same path, episode, and seed. **SUE** is the same run with the artifact switched off at test time, which shows whether the gain actually depends on the artifact. Retention is reported as mean loss and as **CVaR** over the worst 10–20% of paths.

## Key Findings

Backbones: Qwen3.8-Max and Kimi-K3. The run consumed 1.838 billion tokens in total.

- **Near gains often do not transfer**: SkillOpt and SkillGrad gain on near-distribution episodes (CEG_N 0.763 and 0.555) but fall below baseline on transfer episodes (CEG_T −0.273 and −0.383). SkillBoost is best on both (1.597 and 0.537) and has the largest state-use effect (SUE 1.238).
- **Forgetting sits in the tail**: SkillOpt forgets on fewer paths than baseline (20.8% vs 23.6%) but has the largest mean loss (1.454) and worst-10% CVaR (12.666). SkillBoost has the best backward transfer (+0.863) yet still declines on 21.3% of trajectories. For every method, CVaR_0.1 is well above the mean loss.
- **No reliable rule adaptation**: no revision effect (REV_1, REV_2) remains significant after Holm correction. Single-Evidence Memory has the highest REV_2 (0.716) despite negative generalization.
- **Candidate selection is the bottleneck, not generation**: going from 1 to 4 candidates raised the best-candidate gain by +0.496 but widened the selection gap by +0.163.
- **Safeguarded (not strict) acceptance gates trade harmful commits for missed improvements (Table 5)**: going from open to safeguarded acceptance (require improvement and limit regressions) cut harmful commits from **12.4% to 6.2%** and raised precision from 9.3% to 29.5%. It also raised missed improvements from **0.0% to 16.5%**, cut capture of available gain from **69.0% to 47.2%**, and cut recall from 52.9% to 41.9%. Agreement between selection-time validation and held-out outcome was essentially unchanged (56.9% open, 55.8% safeguarded). The authors conclude that safeguards add stability mainly by accepting fewer updates, not by identifying better candidates.
- **Regression limits can block needed revisions**: in a worked SkillBoost reversal example (Appendix), the candidate that improved most on the new regime regressed on pre-change tasks, and the candidate with the best all-task mean degraded on the new task. The paper notes that strict regression limits can reject rules better suited to the new environment.
- **More tokens do not guarantee better evolution**: SkillBoost reached the highest CEG (0.802) at 2.39× SkillOpt's tokens for a 45.5% larger gain. Context-only replay used the most tokens (141.61M) with negative CEG.
- **Evolved skills transfer across models, depending on the receiver**: skills from Qwen3.8-Max gave Qwen3.8-27B +1.96 CEG (SkillBoost) versus +2.19 for SFT, but only +0.03 for Qwen3.5-9B.

## Relevance to Praxis

- **Deconfliction H7 (acceptance gates)**: this is the first measurement in the repo of what a safeguarded gate (require improvement, limit regressions) costs. It supplies a trade-off rather than a winner: the safeguard lowered harmful commits but missed about one in six real improvements, and validation predicted held-out outcomes only ~56% of the time under either gate. The paper did not test a stationary vs non-stationary split. The library's gate ("DO: Pass every self-modification through one acceptance gate" in `rules/recursive-improvement.md`) uses a noise margin δ estimated from repeated baseline runs, with the negative security testbed always strict.
- Strengthens `rules/recursive-improvement.md` "DON'T: Accept modifications based on aggregate metrics alone". Aggregate scores hid tail forgetting on a minority of paths, so report CVaR as well as mean.
- The frozen-checkpoint, state-off, and paired-baseline protocol can be combined with `skills/stable-skill-evolution/SKILL.md` and `skills/staged-capability-registration/SKILL.md` to evaluate any artifact-evolution loop.
- Bears on **M7** (transfer across models): transfer worked for some receivers and not others. Within one family, Qwen3.8-Max skills gave Qwen3.8-27B +1.96 CEG but Qwen3.5-9B only +0.03 (and Qwen3.5-4B +0.27), so stronger-to-weaker transfer is not guaranteed even in-family. This is recorded in the Scope of `rules/skill-system-design.md` "DO: Evolve skills with stronger models, deploy to weaker ones" and supports "test on each deployment target before reuse".
- Caveats: one domain (simulated and real trading), two backbones, five update opportunities per stream.

> Source: Lin et al., "Beyond Endpoint Performance: Process-Level Evaluation of Self-Evolving Agents" (arXiv:2609.24663)
