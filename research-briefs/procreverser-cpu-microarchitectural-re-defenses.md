# ProcReverser: Defensive Lessons from Multi-Agent Microarchitectural Reverse Engineering

> **Source**: [arXiv:2611.20827](https://arxiv.org/abs/2611.20827) — Guanqi Lyu, Decheng Qiu, Guangyang Zhang, Fei Zhao, Zhaojun Lu, Jiaji He, Yongqiang Lyu (2026; HTML version `arXiv:2611.20827v2`)
> **Praxis Source ID**: `src:2611-20827v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`ProcReverser` automates black-box microarchitectural reverse engineering of closed-source or undocumented RISC-V processors to identify hardware conditions underlying Spectre-class transient-execution attacks (`Spectre-PHT`, `Spectre-BTB`, `Spectre-RSB`, `Spectre-STL`), predictor state persistence, and cache/timing observation channels. Per the offensive-security policy in [`AGENTS.md`](../AGENTS.md), we do not package offensive microarchitectural probing or side-channel discovery pipelines as skills; instead, this brief captures the paper's **hardware mitigation-verification findings across commercial RISC-V silicon** (`XuanTie C910`, `SiFive P550`, and `gem5 RISC-V O3`) and its **defensive harness-engineering lesson on out-of-model `Discriminative Revalidation` (`DR`)** for measurement-driven scientific and verification agents.

---

## System & Evaluation Scope

`ProcReverser` orchestrates five specialized roles in `LangChain 1.4.2` / `LangGraph 1.2.12` (`Python 3.13.5`) backed by a single reasoning model (`Zhipu AI GLM-5.3-Flash` with `reasoning_effort = high`, up to `10` primary plan versions per task attempt and up to `10` program-repair retries per plan):
1. **Stage 1 — Experiment Design (`Designer` + `Reviewer`)**: Formulates hypotheses, experimental controls, and quantitative decision criteria; registers approved predictions before execution when `Discriminative Revalidation` (`DR`) is enabled.
2. **Stage 2 — Program Execution (`Generator` + Remote Executor + `Diagnostician`)**: Compiles C/assembly microbenchmarks (`GCC 12` on `C910`, `GCC 13.3.0` on `P550` with `-O2 -Wall -Wextra`; `Zig 0.16.0` cross-compiler + `Slurm 24.05.1` on `gem5 25.1.0.1`), collects raw measurement batches via SSH/SCP, and diagnoses build or check failures.
3. **Stage 3 — Evidence Review (`DR` Gate + `Analyst`)**: Evaluates raw measurement batches in deterministic Python against preregistered criteria before admitting evidence to the `Analyst`.

The benchmark defines **`26` Spectre-relevant microarchitectural property tasks** across `6` groups (`P1–P4` barrier/instruction transient suppression, `R1–R10` predictor capacity/indexing/aliasing/persistence, `W1–W2` transient window length, `C1–C7` counter/cache/prefetcher/SMT interfaces, `F1` predictor enablement, `S1–S2` post-fault traces and predictor clearing), evaluated across three RISC-V targets (`5` independent attempts per scored task, withholding RTL, simulator configs, and reference answers):
- **`XuanTie C910`** (`Sipeed Lichee Pi 4A`, `T-Head TH1520` 4-core 64-bit SoC): **`16` independently referenced tasks** verified against `OpenC910` RTL (`b91c909`), user manuals, and prior empirical measurements.
- **`gem5 RISC-V O3`** (`25.1.0.1` in `SE` syscall-emulation and `FS` full-system modes): **`20` independently referenced tasks** verified against simulator source code and concealed instance configurations (`6` of `26` tasks excluded where simulator config alone cannot fix program-dependent reference answers).
- **`SiFive P550`** (`HiFive Premier P550`, `ESWIN EIC7700X` 4-core out-of-order SoC): All **`26` tasks** run to assess cross-processor adaptation (`23/26` characterized; `3/26` reported `Undetermined`).

---

## Key Empirical Findings

### 1. Identification Accuracy, Role Specialization, and `Discriminative Revalidation` (`DR`)

Across `5` independent attempts per reference task (`Table IV`), `ProcReverser` (`Five roles + DR`) achieves **`81.3%` `Pass@1` (`65/80` attempts) and `93.8%` `Pass@5` (`15/16` tasks; `W1` fails `0/5`, `R7–R10` pass `3/5` each)** on `XuanTie C910`, and **`83.0%` `Pass@1` (`83/100` attempts) and `100.0%` `Pass@5` (`20/20` tasks; `R10` passes `1/5`)** on `gem5 RISC-V O3`:

| Configuration | `C910` `Pass@1` | `C910` `Pass@5` | `gem5 O3` `Pass@1` | `gem5 O3` `Pass@5` | Mean Plans | Mean Target Execs | Mean Tokens (`M`) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Single agent` | `17.5%` | `37.5%` | `18.0%` | `40.0%` | `7.06` | `75.09` | `3.34` |
| `Single agent + DR` | `22.5%` | `50.0%` | `25.0%` | `45.0%` | `7.83` | `47.66` | `2.87` |
| `Five roles` | `68.8%` | `87.5%` | `72.0%` | `90.0%` | `4.44` | `40.36` | `13.11` |
| **`Five roles + DR`** | **`81.3%`** | **`93.8%`** | **`83.0%`** | **`100.0%`** | **`5.66`** | **`22.55`** | **`12.88`** |

- **Out-of-model `Discriminative Revalidation` (`DR`) lifts accuracy while cutting target executions at zero extra token cost**: Adding the deterministic 4-step Python `DR` gate (`Registration -> Data comparison -> Targeted revision -> Evidence admission`) raises 5-role `Pass@1` by **`+12.5` pp on `C910`** (`10,000`-resample paired bootstrap `95% CI [6.25, 21.25]`) and **`+11.0` pp on `gem5 O3`** (`95% CI [4.00, 18.00]`), while reducing mean target-side program executions by **`36.5%`** (`75.09 -> 47.66`) on single-agent and **`44.1%`** (`40.36 -> 22.55`) on five-role runs *without* increasing mean token usage (`3.34M -> 2.87M` and `13.11M -> 12.88M`).
- **How `DR` prevents false certainty (`C6` hardware prefetching case study on `gem5 O3`)**: Without `DR`, the generated microbenchmark returned only sequential (`6.91` cycles/line) vs. shuffled (`15.78` cycles/line) scan timings across `3` repair rounds, and the `Analyst` falsely reported hardware prefetching as enabled. With `DR` enabled, Python data comparison caught that the preregistered untouched-probe first-access check was missing from raw samples, routed the gap to `Diagnostician -> Generator`, verified across `200`-trial discovery (`3` vs. `2` hits) and confirmation (`2` vs. `3` hits) batches that probe hit rates stayed within the preregistered `<= 5%` non-detection bound, and correctly concluded prefetching was off.
- **Role-specialization compute caveat**: Splitting duties across `5` roles cut target-side executions by `46.3%–52.7%` (`75.09 -> 40.36` and `47.66 -> 22.55`) and lifted `Pass@1` by `+51.3` to `+60.8` pp over a `1`-context single agent, **but consumed `3.9x–4.5x` more LLM tokens (`12.88M–13.11M` vs. `2.87M–3.34M`)** without a token- or sample-matched `PACE` single-agent baseline (see [pace-multi-agent-compute-parity-synthesis](pace-multi-agent-compute-parity-synthesis.md)).

### 2. Per-Implementation Hardware Defense & Barrier Findings Across RISC-V Silicon

Comparing `Table II` (`XuanTie C910`), `Table III` (`gem5 O3`), and `Table V` (`SiFive P550`) demonstrates why software Spectre mitigations and isolation assumptions cannot be generalized from ISA specifications alone:
- **Barrier instructions behave non-uniformly across implementations**:
  - On **`XuanTie C910`** (`P1`), read-ordering fences, `fence.i`, and counter CSR reads suppress load/store-fault transient cache signals, whereas **`fence w,w`, `fence.tso`, and `lr.d` do NOT**. Clearing predictor state (`BHT`, `Ind-BTB`, `BTB`/`L0BTB`) requires privileged M-mode `MCOR` (`0x7c2`, `S2`), while `PHT` training crosses address spaces (`R4, R9`).
  - On **`SiFive P550`** (`P1–P4`), all `9` tested user-mode barriers (`fence rw,rw`, `r,r`, `r,w`, `w,r`, `w,w`, `i,i`, `iorw,iorw`, `fence.tso`, `fence.i`) attenuate transient cache signals across memory-dependence and fault windows, with store-loop cycle costs (`P2`) spanning **`~3` cycles (`fence r,w`), `~10` cycles (`fence w,w`), `~13` cycles (`fence rw,rw`, `r,r`, `w,r`, `fence.tso`), and `~46` cycles (`fence.i`)**; `fence.i` suppresses fault-window cache channels across `0–16` instruction spacings (`P3`), whereas **`fcsr` reads do NOT suppress the fault window (`P4`)** (unlike `gem5 O3` `SE` branch windows where `fcsr`/`fflags`/`frm` reads do suppress wrong-path cache signals).
- **Predictor persistence and user-mode counter/flush restrictions will not eliminate all channels on `P550`**: Even though user-mode `rdcycle`, `rdinstret`, and `cbo.flush` trap on `P550` (`C1–C2`), `perf` cycle counting and L1 set-conflict, direction-prediction, data-TLB, and `~4 MiB` shared LLC channels remain observable (`C1–C3, C7`), post-fault loads leave transient cache traces (`S1`), bidirectional `+64 B` / `-64 B` hardware prefetching is active (`77.9%` ascending and `76.7%` descending first-access hits vs. `4.4%` shuffled across `20 x 512` confirmation trials, differences `73.5` and `72.3` pp, `95% CIs [72.6, 74.3]` and `[71.3, 73.2]`; hot-cache `99.54%–99.66%`, cold-cache `<= 0.01%` at `153`-cycle threshold), and **same-core direction-predictor state (`168–183` branch history window) persists across processes (`R4, R8, R9`) and is NOT cleared by user-mode `fence.i`, `1.024M` interfering branches, or `256 x 200 us` sleep calls (`R5, S2`)**.
- **Blind configuration tracking (`gem5 O3` `R1`)**: When concealed `RAS` depth was changed between `8` and `16` entries, nested-call two-segment linear fits autonomously located return-cost change points at `7.65` and `15.75`, recovering exact `8`- and `16`-entry capacities (`16`-entry `RAS` on `P550`, `12`-entry `RAS` and `16`-entry `L0BTB` with `22`-bit XOR-folded GHR on `C910`).

---

## Defensive & Harness-Design Takeaways

1. **Gate empirical agent conclusions with out-of-model `Discriminative Revalidation` (`DR`)**: Whenever an agent designs experiments or diagnostic probes to infer hidden system properties, enforce a deterministic code gate between raw execution data and the synthesis/reporting LLM: (a) preregister candidate explanations, control comparisons, and quantitative decision thresholds before running probes (rejecting plans whose competing hypotheses yield indistinguishable predictions), (b) evaluate raw measurement batches directly in code, (c) route missing control measurements to program repair rather than letting the analyst rationalize partial data, and (d) emit `Undetermined` (`3/26` on `P550`) when competing explanations remain unresolved.
2. **Validate transient-execution barriers and predictor-clearing sequences per silicon stepping and OS configuration**: Never assume `fence.tso`, `fence w,w`, `fcsr` reads, or `fence.i` uniformly block transient leakage or scrub branch-predictor state across RISC-V cores (`C910` vs. `P550`), and re-run automated microarchitectural regression suites across firmware, kernel (`perf`/`rdcycle`/`cbo.flush` trap), and core configuration updates.

## Related Artifacts

- [`pentest-harness-assurance`](../skills/pentest-harness-assurance/SKILL.md) — Out-of-model receipt grounding (`P1`) and non-destructive claim reduction (`P2`) to `Undetermined` / `needs-review` when evidence is incomplete (`arXiv:2609.22664`).
- [`falsification-gated-memory-evolution`](../skills/falsification-gated-memory-evolution/SKILL.md) — Structured causal hypothesis schemas and empirical falsification gates (`arXiv:2611.14326`).
- [pace-multi-agent-compute-parity-synthesis](pace-multi-agent-compute-parity-synthesis.md) — Accounting for token/cost inflation (`R_token`, `R_sys`) when comparing multi-role workflows against single-agent baselines (`arXiv:2611.17610`).
- [`rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — `"DO: Decompose evaluations into atomic checklist items"` and `"DO: Attribute failed rollouts to environment, task, verifier or policy before training on them"`.
