---
name: budgeted-facility-sandbox-snapshots
description: >
  Offline budgeted facility-location memory-snapshot planning, two-pass
  additive dependency profiling, and AST-guided asymmetric initialization-cost
  routing for low-latency AI coding sandboxes executing unseen scripts.
  Derived from "Readie: Low-Latency Code Sandboxes for AI Agents"
  (arXiv:2611.22171).
source: https://arxiv.org/abs/2611.22171
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Budgeted Facility-Location Sandbox Snapshots

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when building or operating isolated code-execution sandboxes (`gVisor`, Firecracker microVMs, CRIU/container memory checkpoints, or notebook/REPL executors) for AI agents that generate and run **previously unseen scripts** importing diverse, multi-turn library stacks (`NumPy`, `pandas`, `PyTorch`, `Transformers`, `OpenCV`, `scikit-learn`) under a bounded host disk/memory cache budget.

## Core Problem & Insight

Across `6,833` recorded multi-turn coding and data-science agent sessions, agents import **new packages after turn 1 in `30.8%` of sessions**, continuing to introduce unseen dependencies until turn **`3.7`** on average. Existing sandbox provisioning strategies fail on at least one axis:

- **On-demand base images (`python:3.12` + `pip install`)**: Pay full download, extraction, bytecode compilation, and module initialization on every cold request (`13.9 s` `p50`, `57.5 s` `p99`; pulling an uncached custom container layer with `pandas`, `PyTorch`, and `NLTK` over `1 Gbit/s` takes `17.4 s`, of which `15.0 s` is layer download/extraction).
- **Single shared fat image (`Colab` / `Kaggle Python`)**: Eliminates `pip install` downloads, but every fresh interpreter still loads and executes modules from disk (`2.74–7.28 s` from source—`56–70%` bytecode compilation—and still `1.00–2.80 s` from ahead-of-time bytecode, vs. **`0.29–0.42 s`** when restoring a post-import memory snapshot for `pandas`, `torch`, or `nltk`).
- **Exact per-request / per-function memory snapshots**: Require knowing the exact import set in advance and explode storage (`1,308` distinct snapshots / `279 GB` across `Readie`'s test + OOD sets; `1,306` snapshots / `351 GB` to cover `90%` of `9,325` clustered planning requests), causing frequent remote object-store cache misses (`2.44 s` `p50` under a `15 GB` host budget).
- **Frequency-only or Jaccard-cluster snapshot heuristics**: Ignore the **asymmetric cost** between fast linear memory restoration ($\alpha \approx 0.0031\text{ s/MB}$) and slow disk residual imports ($t_p$): a cluster union carrying `PyTorch` penalizes every lightweight `pandas` script that restores it, while missing `PyTorch` on an ML script incurs a `14.8 s` disk import penalty.

The fix is to **learn a compact portfolio of `30–65` memory-state snapshots** from historical or LLM-synthesized scripts by modeling exact restore-plus-residual initialization time and solving **budgeted facility location** offline, then routing each unseen script online via AST import extraction to whichever planned snapshot minimizes total expected initialization latency.

---

## Procedure

### Step 1: Profile Additive Per-Package Cost Metadata in Isolated Two-Pass Runs

Do not profile packages in a single dirty interpreter or sum standalone package import times (which double-counts shared transitive dependencies like `numpy` across `pandas`, `scikit-learn`, and `seaborn`):

1. **Pass 1 (Transitive Closure Discovery)**: For each candidate package $p \in P$ observed in historical workloads, import $p$ inside a fresh interpreter over the shared read-only root filesystem and record every module added to `sys.modules` to obtain its transitive dependency closure $\overline{\{p\}}$.
2. **Pass 2 (Marginal Disk Import Time $t_p$ & Memory Footprint $m_p$)**: Drop the OS page cache, start a second fresh interpreter, import all transitive dependencies $\overline{\{p\}} \setminus \{p\}$ *first*, and only then measure:
   - **$t_p$**: Wall-clock disk import time of $p$ itself once its dependencies are already resident.
   - **$m_p$**: Marginal growth in anonymous resident memory (`RssAnon`) added by $p$.
3. **Calibrate Snapshot Restore Slope ($\alpha$)**: Checkpoint and restore `~50` snapshots spanning varying package closures (`0–800 MB`), take the median across `>= 5` restores per snapshot, and fit the linear restore model:

   $$T_{\mathrm{restore}}(c) = t_{\mathrm{base}} + \alpha \sum_{p \in D_c} m_p$$

   (On `gVisor` + `python:3.12`, $t_{\mathrm{base}} = 0.32\text{ s}$ and $\alpha = 0.0031\text{ s/MB}$.)
4. **Quarantine Import-Side-Effect Packages**: Identify packages that monkey-patch global interpreter state, alter numeric precision/backends, or mutate unrelated modules on `import`. Exclude them from snapshot candidate sets $D_c$ during offline planning so requests with $p \in D_c \setminus D_r$ never inherit silent side effects; import them on disk post-restore only when $p \in D_r$.

### Step 2: Construct the Candidate Set & Asymmetric Initialization Cost Matrix

Given a representative planning corpus $R$ of historical and/or LLM-synthesized scripts (`~10K–15K` scripts across target task domains):

1. Extract each script's imported package set $r$ and expand its transitive closure $D_r = \overline{r}$.
2. Restrict candidate snapshots $C_{\mathrm{cand}}$ to the **distinct transitive closures** $\{D_r : r \in R\}$ observed in the planning corpus (`15,299` scripts collapse to a few thousand distinct closures), avoiding the $2^{|P|}$ exponential power set.
3. For every request closure $D_r$ and candidate snapshot closure $D_c$ (with memory footprint $S(c) = \sum_{p \in D_c} m_p$), compute the **asymmetric initialization latency**:

   $$T(r, c) = t_{\mathrm{base}} + \alpha \sum_{p \in D_c} m_p + \sum_{p \in D_r \setminus D_c} t_p$$

   Notice the two opposing terms: adding packages to $D_c$ increases restore cost $\alpha S(c)$ for *every* request routed to $c$ (even when $p \notin D_r$), whereas omitting $p$ charges residual disk-import time $t_p$ *only* on requests requiring $p$.

### Step 3: Solve Budgeted Facility Location via Greedy Marginal-Gain Selection

Formulate snapshot selection under host snapshot storage budget $B$ (MB) as an asymmetric **budgeted facility location** problem:

$$\min_{C \subseteq C_{\mathrm{cand}}} \mathcal{F}(C) = \sum_{r \in R} \min_{c \in C} T(r, c) \quad \text{s.t.} \quad \sum_{c \in C} S(c) \le B$$

Solve iteratively using greedy budgeted facility location ($O(KN^2)$ time, $O(N^2 + NP)$ space for $N$ distinct closures, $P$ packages, and $K$ chosen snapshots):
1. Initialize $C \leftarrow \emptyset$ and current per-request cost $u(r) \leftarrow t_{\mathrm{base}} + \sum_{p \in D_r} t_p$ (cold disk import from the shared read-only rootfs).
2. At each iteration, evaluate all remaining candidates $c \in C_{\mathrm{cand}} \setminus C$ that fit in the remaining storage budget ($S(c) \le B - \sum_{c' \in C} S(c')$) and compute total latency reduction $\Delta(c) = \sum_{r \in R} \max\bigl(0,\, u(r) - T(r, c)\bigr)$.
3. Add the candidate $c^\star$ maximizing $\Delta(c) > 0$ (or run optional budgeted `k-medoids` swap refinement if offline build time permits, though greedy alone stays within `7%` on planning and `9%` on held-out validation while running `2.1x` faster: `139 s` vs. `299 s` on `15,299` requests). Stop when no fitting candidate reduces total initialization time.
4. Choose $B$ at the validation-curve knee (e.g., `10 GB` yielding `33` snapshots alongside `5 GB` of shared read-only disk packages = `15 GB` total host footprint). Build each selected snapshot offline by booting a clean container over the read-only fat rootfs, importing $D_c$, and checkpointing memory state to local NVMe/RAM disk.

> **Why Not MILP, Knapsack, or Jaccard Clustering?** Exact `MILP` (`CBC`) fails to resolve within `1 hour` even at `100` data points; `greedy knapsack` ranks closures once without updating coverage and wastes budget on overlapping snapshots (`2.2x` higher latency than greedy facility location); and `agglomerative Jaccard` takes cluster unions that bloat snapshots with rarely used packages (`12.7x` vs. `22x` initialization speedup).

### Step 4: Route Unseen Scripts Online by Minimum $T(r, c)$ & Pin Multi-Turn Sessions

When an agent submits code for execution:
1. **Static AST Import Extraction**: Parse the submitted code's AST to extract top-level and function-scoped `import` / `from ... import` targets $r$, and map them to their precomputed closure $D_r$. (For `p_unknown` absent from the read-only rootfs, append expected `pip` install + import overhead, which cancels across candidates when constant.)
2. **Minimum-Latency Snapshot Selection**: Pick $c^\star = \arg\min_{c \in C} \bigl(\alpha S(c) + \sum_{p \in D_r \setminus D_c} t_p\bigr)$. Crucially, **do not route by maximum package overlap or exact superset containment**: a `32 MB` snapshot missing `matplotlib` (`0.9 s` restore + `0.8 s` residual = `1.7 s`) beats an exact-superset snapshot that also holds unused `PyTorch` (`3.0 s` restore + `0 s` residual = `3.0 s`).
3. **Isolated CoW Restore + Residual Load**: Clone $c^\star$ into a fresh isolated sandbox (`gVisor` user-space kernel + private network namespace + in-memory CoW filesystem overlay atop the shared read-only rootfs, with **zero host filesystem sharing**), import only the residual packages $D_r \setminus D_{c^\star}$ from the read-only rootfs, execute the payload, and return serialized outputs.
4. **TTL Session Affinity for Multi-Turn Agents**: Keep the executor warm under a bounded session TTL keyed by `session_id` so subsequent turns reuse in-memory variables and newly imported packages (`30.8%` of trajectories add imports across turns `2–4`); if a later turn pivots to a heavy uncached stack (`torch` + `transformers`) on a stateless call, re-route to the matching snapshot.

---

## Quantitative Reference Profile (`arXiv:2611.22171`)

| Evaluation Regime (`gVisor` `8`-core / `8 GB` sandboxes) | No Snapshots (`pip`) | Shared Fat Image (`Kaggle`) | Per-Request Snapshots | `Readie` (Learned Portfolio) | Key Gain |
|:---------------------------------------------------------|:--------------------:|:---------------------------:|:---------------------:|:----------------------------:|:---------|
| **In-Distribution Test (`15 GB` budget, `1,535` reqs\*)** | `7.31 h` init (`13.9 s` p50) / `9.85 h` E2E | `2.07 h` init (`3.75 s` p50) / `4.73 h` E2E | `0.98 h` init (`2.44 s` p50, `8 GB` LRU) / `3.88 h` E2E | **`0.33 h` init (`0.60 s` p50, `4.22 s` p99; `33` snaps) / `2.96 h` E2E** | **`22x` / `6.3x` / `3x` faster init; `1.3–3.3x` faster E2E** |
| **Unconstrained Storage (`1,535` reqs\*)** | — | — | `0.23 h` init / `3.13 h` E2E (`1,308` snaps, `279 GB`) | **`0.22 h` init / `2.48 h` E2E (`61` snaps, `20 GB`)** | **Matches exact oracle at `14x` less storage** |
| **Out-of-Distribution (`832` unseen-agent reqs, `15 GB`)** | `4.59 h` init (`14.9 s` p50) / `6.28 h` E2E | `1.40 h` init (`3.48 s` p50) / `3.74 h` E2E | `0.87 h` init (`2.54 s` p50, oracle) / `1.69 h` E2E | **`0.43 h` init (`0.65 s` p50, `1.86 s` mean) / `1.07 h` E2E** | **`2x` faster than hypothetical per-request oracle** |
| **`3` Agent Benchmarks (`DA-Code`, `DSBench`, `InfiAgent`, `1,084` tasks)** | — | `1.23 h` init / `4.40 h` E2E (benchmark images) | — | **`0.14 h` init / `3.35 h` E2E** (`InfiAgent`: `0.40 -> 0.02 h` init, `0.40 -> 0.03 h` E2E) | **`9.1x` faster init (`16x` short tasks); `1.3x` (`13x`) E2E** |
| **`8` Data-Science Domain Groups (Cost-Model Breakdown)** | `52,882 s` cold start | — | — | **`2,596 s` total (`255 s` [`9.8%`] residual imports)** | **`18–22x` per domain (`20x` overall, `4.6–5.6%` of cold)** |

*\*Manuscript note: `Table 1` sums the test split to `1,559` requests across the `7` sources, whereas `§6.2` and `Figure 9` evaluate `1,535` test requests.*

---

## Environment Caveats & Failure Modes

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| **Silent cross-request state or RNG/PRNG cloning** | Checkpointing initialized PRNG seeds, TLS state, or background threads before snapshot capture | Reseed `random`, `numpy.random`, `torch`, and OS entropy pools inside the executor wrapper immediately upon snapshot restore before running user code, and never share live process memory across tenants |
| **Monkey-patching / import side effects** | Snapshot includes a package in $D_c \setminus D_r$ that patches `ssl`, `asyncio`, `matplotlib` backends, or `numpy` warnings on import | Maintain an import-side-effect denylist during Step 1; exclude flagged packages from snapshot closures and import them post-restore only when explicitly requested |
| **Rootfs drift invalidating memory checkpoints** | Updating underlying shared `Kaggle Python` disk layers without rebuilding memory snapshots | Pin snapshots cryptographically to the exact immutable read-only rootfs digest (`OverlayFS` lowerdir) they were checkpointed against |
| **Dynamic `importlib` / subprocess imports missed by AST** | Agent script invokes `__import__()`, `importlib.import_module()`, or shell CLI tools not visible in Python AST | Fall back to lightweight prompt/task-domain priors or session-sticky containers, while keeping the shared read-only fat rootfs mounted beneath every snapshot so missed modules still load locally without network `pip` pulls |

## Cross-References

- [`speculative-sandbox-scheduler`](../speculative-sandbox-scheduler/SKILL.md) — Complementary: `SpecBox` hides sandbox boot latency *during* LLM token generation via intent routers and Markov prefetching, whereas this skill shrinks sandbox initialization *after* unseen code arrives (`0.60 s` `p50`) via budgeted facility-location memory snapshots
- [`serial-slot-accelerator-command-scheduling`](../serial-slot-accelerator-command-scheduling/SKILL.md) — Complementary multi-node parallel/serial GPU command scheduling once sandboxes are running
- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) — Complementary intra-session pre-command filesystem rollback for state-mutating shell commands
- [`high-fanout-sandbox-memory-compression`](../high-fanout-sandbox-memory-compression/SKILL.md) — Complementary LLM KV-cache shared-prefix deduplication across parallel sandbox branches
- [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — Mandatory container/kernel isolation (`gVisor` / microVM) and network allowlist boundaries

## Sources

- [Readie: Low-Latency Code Sandboxes for AI Agents](https://arxiv.org/abs/2611.22171) (`arXiv:2611.22171`, `src:2611-22171v1`)
