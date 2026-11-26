---
name: paired-serving-substrate-mas-benchmarking
description: Benchmark multi-agent workflows and serving substrates without load, deadline-truncation, or survivorship confounds by replaying frozen plan-task-arrival schedules across offered loads, reporting submitted-job Effective Quality alongside Evaluated-Only Quality, and computing survivor-matched intersection tail latency.
source: "arXiv:2611.28671"
repository: "https://github.com/masa-cloud/MASSys"
license: "CC BY 4.0"
---

# Paired Serving-Substrate Multi-Agent Benchmarking (`MASSys`)

Use this procedure whenever benchmarking multi-agent workflow topologies (`Star`, `Chain`, `DAG`, `Debate`, `FSM`, `Tool-ReAct`) or comparing multi-agent inference/serving substrates (`vLLM`, `SGLang`, KV-pinned schedulers such as `Continuum`, multi-stage orchestrators such as `ORLA`, or cloud GPU pools) across **3+ project types**: repository coding agents (`SWE-bench`), deep-research and RAG synthesis pipelines, financial/enterprise tool-use workflows, multimodal image-and-text generation pipelines, and interactive CLI/browser assistants.

Multi-agent workflow rankings are **not invariant to the serving substrate**. Even when models, prompts, tasks, and workflow plans are held byte-identical, changing KV-cache memory, CPU contention, serving engine, or arrival rate (`JPS`) routinely **inverts topology rankings** (`Star` flipping `1st -> 4th` against `Chain` `4th -> 1st` in `10/10` blocks under tight KV cache; `Chain` vs. `FSM` reversing across `vLLM`/`SGLang` vs. `Continuum`/`ORLA+vLLM`), hides `28–38 pp` end-to-end quality collapses behind flat scored-subset averages (`Q_eval`), and creates **latency survivorship bias** where a backend shedding `~80%+` of heavy jobs at the deadline appears `273.4 s` *faster* at raw survivor `P95` while actually running `+244.0 s` *slower* on matched surviving jobs (`arXiv:2611.28671`).

Complements [`serving-stack-eval-checklist`](../serving-stack-eval-checklist/SKILL.md) (which audits single-agent local tool-call templates, constrained-decoding loops, and turn-vs-instance pooling before running evals) and [`pace-multi-agent-compute-parity-synthesis`](../../research-briefs/pace-multi-agent-compute-parity-synthesis.md) (which enforces sample/token/cost parity between single-agent and multi-agent baselines).

---

## When to Use This Skill

- Comparing two or more multi-agent topologies (e.g., parallel fan-out `Star` vs. sequential `Chain` or `FSM`) before selecting a production architecture.
- Evaluating LLM serving engines, KV-cache eviction/pinning policies, or multi-model GPU placement strategies under realistic concurrent multi-agent arrival streams.
- Auditing benchmark leaderboards where jobs can time out, hit container/sandbox limits, or fail before scoring.
- Investigating suspicious tail-latency (`P95`/`P99`) "improvements" at higher offered loads (`JPS`) when job completion rates simultaneously drop.

---

## Step-by-Step Procedure

### Step 1: Freeze a Paired `(Plan, Task, Arrival)` Workload Schedule
Never allow online planners, dynamic task samplers, or independent Poisson draws to vary across the serving substrates or resource cells being compared:
1. Pre-generate and freeze each job's **multi-agent execution plan** (role graph, stage dependencies, model bindings, and tool permissions), **task payload**, and **relative arrival offset** $t_j$ for every seed (`>= 3` seeds for load-transition claims).
2. Store the frozen schedule in an immutable manifest (`job_id`, `family`, `topology`, `arrival_offset_s`, `plan_hash`, `seed`) and replay the **exact same manifest** against every `(substrate, hardware_sku, load_jps)` cell.
3. Equal-weight or explicitly stratify task families (`SWE`/sandbox code execution, search/RAG, tool-heavy API chains, multimodal stages) so bursty fan-out graphs and long-context sequential chains exercise prefill, decode, KV retention, and host CPU/tool sandboxes jointly.

### Step 2: Decouple the Arrival Window from Per-Job Deadlines Across a Load Sweep
Single-concurrency (`concurrency = 1`) or quiescent runs hide KV-cache thrashing and fan-out queueing (`Star` `5.0118 ± 0.0804 s` beating `Chain` `6.1803 ± 0.0081 s` in `10/10` blocks under `32 GiB` KV / `max_num_seqs = 16`, then collapsing to `12.4900 ± 0.2018 s` vs. `6.0392 ± 0.0068 s` in `10/10` blocks under `2 GiB` KV / `max_num_seqs = 1`).
1. Sweep at least **three offered-load regimes**: quiescent/low load (e.g., `0.005–0.01 JPS`), knee/moderate load (`0.05 JPS`), and saturation load (`0.10 JPS`).
2. Separate the **job submission window** $W_{\text{submit}}$ (e.g., `1,800 s` Poisson arrivals) from a strictly enforced **per-job wall-clock deadline** $D_{\text{job}}$ (e.g., `1,200 s` from each job's arrival $t_j$), allowing already-admitted jobs up to $W_{\text{submit}} + D_{\text{job}}$ to finish or hit $D_{\text{job}}$ cleanly rather than truncating late arrivals mid-window.
3. Reset engine KV caches, worker pools, and container sandboxes cleanly between cell runs.

### Step 3: Audit Every Unscored Job and Report Both `Q_eff` and `Q_eval`
Conditioning quality solely on jobs that finish and return a score (`Q_eval`) treats deadline-killed and runtime-crashed jobs as invisible—masking severe operational collapse (`SWE-bench` `Q_eval` moving only `64.91% -> 60.71%` [`-4.20 pp`] from `0.05 -> 0.10 JPS` while submitted-job `Q_eff` plunges **`49.33% -> 11.72%` [`-37.61 pp`]**; `PinchBench` `Q_eval` `93.81% -> 89.58%` [`-4.23 pp`] vs. `Q_eff` **`93.81% -> 66.15%` [`-27.66 pp`]**).

For every cell with $N_{\text{submitted}}$ scheduled jobs and $V$ validly scored jobs, classify all $N_{\text{submitted}} - V$ unscored jobs into disjoint buckets and report both quality metrics side by side:

| Metric / Audit Field | Formula / Definition | Operational Meaning |
|:---|:---|:---|
| **Completion Rate (`CR`)** | $N_{\text{exec\_ok}} / N_{\text{submitted}}$ | Share of submitted jobs finishing workflow execution within $D_{\text{job}}$ |
| **Evaluated-Only Quality (`Q_eval`)** | $\frac{1}{V} \sum_{j \in \mathcal{V}} q_j$ | Conditional output quality given execution + evaluator completion |
| **Effective Quality (`Q_eff`)** | $\frac{1}{N_{\text{submitted}}} \sum_{j=1}^{N_{\text{submitted}}} q_j \quad (q_j = 0 \text{ if unscored})$ | **Primary system SLO metric**: end-to-end quality delivered per submitted job |
| **Unscored Attribution** | `deadline_exceeded` vs. `runtime_exec_error` vs. `post_exec_evaluator_fault` | Separates serving overload (`490/492 = 99.59%` in `MASSys`) from harness/Docker evaluator glitches (`2/492 = 0.41%`; re-runnable offline if trajectory artifacts succeeded) |

### Step 4: Eliminate Latency Survivorship Bias via Survivor-Matched Intersection `P95`
Never compare raw `P95` or mean latency across substrates or load levels when completion rates differ by more than `1–2 pp`. When a serving substrate drops heavy multi-stage or multimodal jobs at $D_{\text{job}}$ (e.g., `SGLang` at `4x H200`, `0.10 JPS` timing out `35/39` and `39/44` `PaperBanana` jobs, dropping execution success `95.00% -> 81.26%`), its surviving set contains only short, cheap jobs—making raw survivor `P95` appear to **decrease by `-273.4 s` (`651.1 s -> 377.7 s`)** below backends that actually completed the hard jobs (`vLLM` `814.7 s` at `96.17%` completion; `Continuum` `866.5 s` at `92.51%`).

Compute latency comparisons using **two bias-resistant estimators**:
1. **Matched Surviving-Job Intersection (`ΔP95_matched`)**: For any pair of load levels `(λ_low, λ_high)` or substrates `(A, B)` under the same seed, restrict both latency distributions to the exact intersection of `job_id`s $\mathcal{S}_{A} \cap \mathcal{S}_{B}$ that succeeded within $D_{\text{job}}$ in *both* runs (in `MASSys` `Table 8`, survivor-matched intersection reversed `SGLang`'s apparent `-273.4 s` speedup into a **`+244.0 s` slowdown**, alongside `+152.0 s` on `vLLM` and `+302.9 s` on `Continuum`, positive across all `9/9` backend-seed pairs).
2. **Deadline-Censored Submitted Latency (`P95_censored`)**: Assign every timed-out/failed job $D_{\text{job}}$ (right-censored at the deadline) over all $N_{\text{submitted}}$ jobs so shedding work can never lower reported tail latency.

### Step 5: Attribute Bottlenecks Along the Multi-Agent Critical Path
Because multi-agent DAGs overlap parallel branches and external tool sandboxes, aggregate request-level `TTFT`/`TPOT` cannot explain why `Chain` beats `FSM` on `vLLM` (`291.12 s` vs. `375.52 s`) and `SGLang` (`116.43 s` vs. `127.56 s`) while `FSM` beats `Chain` on `Continuum` (`394.45 s` vs. `480.13 s`) and `ORLA+vLLM` (`294.07 s` vs. `324.82 s`) on the exact same `PinchBench` jobs (`Table 9`).
1. Instrument per-node spans along each job's **critical path**: `(a) scheduler/queue wait`, `(b) prefill + KV-cache load/recompute`, `(c) token decode`, `(d) tool/container sandbox execution`, and `(e) orchestrator handoff overhead`.
2. Report topology winners **conditioned on the target deployment's KV budget, GPU count, and serving scheduler** rather than declaring any multi-agent topology universally faster or higher-quality.

---

## Failure Modes & Environment Caveats

- **Post-execution evaluator flakes conflated with serving failures**: Network-dependent grading steps (such as uncached Docker image pulls after an agent already finished generating its patch) depress `Q_eff` for reasons unrelated to the serving engine. Pre-pull and content-hash all grading containers offline (`serving-stack-eval-checklist` + `Sandman` preflight rules) and log `post_exec_evaluator_fault` separately from `deadline_exceeded`.
- **Small survivor intersections under extreme overload**: If `|\mathcal{S}_A \cap \mathcal{S}_B| / N_{\text{submitted}} < 0.30` at extreme saturation, `ΔP95_matched` reflects only trivial short jobs; treat `Q_eff`, `CR`, and deadline-censored `P95` as primary in that regime and add an intermediate load point around the saturation knee.
- **Unpinned auxiliary multimodal/tool workers**: Co-locating secondary diffusion/vision models (`Qwen-image-2512`) or heavy Docker test runners on shared GPUs/CPUs without recording device contention will shift critical-path blame onto the text LLM engine unless GPU memory and host CPU cgroups are logged per cell.

---

## Related Artifacts

- **Rules**: [`agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) (*"DO: Replay frozen plan-task-arrival schedules across serving substrates and report submitted-job Effective Quality alongside survivor-matched intersection P95"*, *"DON'T: Claim coordination gains over greedy decoding without sample-parity and compute-parity baselines and 6D PACE accounting"*, *"DO: Certify benchmark tasks with reference-pass and empty-fail preflights, lock the verifier's evidence view, and fingerprint baseline bytes before reusing grading sandboxes"*)
- **Skills**: [`serving-stack-eval-checklist`](../serving-stack-eval-checklist/SKILL.md), [`serial-slot-accelerator-command-scheduling`](../serial-slot-accelerator-command-scheduling/SKILL.md)
- **Research Briefs**: [`pace-multi-agent-compute-parity-synthesis`](../../research-briefs/pace-multi-agent-compute-parity-synthesis.md)
