# Replay Fidelity in LLM Agent Evaluation: Randomness, Hidden State, and Test Oracles in AppWorld

> **Source**: [arXiv:2611.11216](https://arxiv.org/abs/2611.11216) — You Liu, Quanchao Lu (2026)
> **Praxis Source ID**: `src:2611-11216v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

As the authors state explicitly, this work is a bounded historical replay audit of `71` failing AppWorld `0.1.0` trajectories (`284` primary fixed-code replay attempts plus targeted mechanism probes and a `12`-case BFCL pilot) rather than a new replay-certification framework or failure-localization method. Complementary operational procedures for black-box trace capture and sealed offline replay already reside in [`sealed-replayable-agent-audit-log`](../skills/sealed-replayable-agent-audit-log/SKILL.md). This brief captures the empirical findings on how replay eligibility shifts drastically across validation contracts, hidden RNG/credential state, and in-process test-oracle side effects, backing concrete evaluation-integrity rules in [agent-evaluation-quality.md](../rules/agent-evaluation-quality.md).

---

## Audit Scope & Experimental Design

Debugging, root-cause attribution, and counterfactual intervention benchmarks for multi-turn tool-using agents routinely filter trajectories by whether recorded tool calls replay deterministically. Starting from all `147` official `GPT-4o-2024-05-13` ReAct executions in AppWorld `0.1.0` (data bundle `0.1.3`: `76` successes, `71` failures across `32` failure-bearing task families), the authors audit all `71` failure trajectories across `284` primary isolated replay runs (`2` fresh network-disabled processes per policy, `2` CPUs, `4 GB` RAM, `60 s` per-cell timeout, `120 s` outer watchdog):

- **Declared Replay (`N`)**: Initializes the environment with AppWorld's declared task seed (`123`) once at startup.
- **Interaction-Reseeded Replay (`C`)**: Additionally calls `random.seed(123)` immediately before every recorded interaction cell—matching an undocumented internal reseeding step in AppWorld's trajectory-extraction script.
- **Validation Contract Ladder**:
  - `O`: Exact printed cell output text equality across all steps.
  - `D_pre`: Byte-for-byte equality across all `12` archived pre-oracle SQLite delta files.
  - `V`: Native evaluator endpoint verdict equality (overall pass/fail flag plus passed, failed, and total assertion counts).

---

## Key Empirical Findings

### 1. Replay Eligibility Depends Strongly on Both Reconstruction Control and Validation Target

| Validation Contract | Declared `N` Admitted | Reseeded `C` Admitted | `C - N` Admission Gap | Primary Failure Driver Under `N` |
|:--------------------|:----------------------|:----------------------|:----------------------|:---------------------------------|
| **`O AND D_pre AND V`** (Strict) | **`42/71` (`59.2%`)** (`21/32` families, `58.33%` macro) | **`68/71` (`95.8%`)** (`30/32` families, `92.71%` macro) | **`26` cases** | Unpinned RNG consumption across multi-login token minting (`>=2` logins: `N = 1/30` vs. `C = 27/30`) |
| **`D_pre AND V`** (State + Verdict, continuing past text mismatch) | **`66/71` (`93.0%`)** (`4` different, `1` unknown) | **`70/71` (`98.6%`)** (`0` different, `1` unknown) | **`4` cases** | `24` of `25` early `N` token-expiry output mismatches still reach identical DB deltas + verdicts when remaining fixed code executes |
| **`V` Only** (Endpoint Verdict) | **`70/71` (`98.6%`)** (`1` unknown) | **`70/71` (`98.6%`)** (`1` unknown) | **`0` cases** | Endpoint test assertions completely mask both output drift (`26` cases) and persistent DB row drift (`4` cases) |

- **Concentrated cohort skew**: Traces with `<=1` login pass `41/41` under both `N` and `C`, whereas traces with `>=2` logins drop to **`1/30`** under `N` vs. **`27/30`** under `C`. Similarly, long trajectories (`>=20` interactions) shift from **`4/24` to `21/24`**, and multi-app workflows shift from **`0/20` to `18/20`**. Filtering a debugging benchmark under `N` with strict `O AND D_pre AND V` silently discards `89%–100%` of multi-login and multi-app failures!

### 2. Three Forms of Hidden State Escape Transcript & Endpoint Checks

1. **Materialized SQLite Row Divergence Masked by `O` and `V` (`4/4` residual cases)**:
   - On the `4` `N` trajectories (spanning `2` task families) where `D_pre` diverges despite matching `O` and `V`, sorting and hashing table rows across all `12` SQLite connections before oracle execution proves that **phone table rows and password-reset codes genuinely differ in `4/4` cases** across both repetitions—ruling out benign SQLite serialization order artifacts.
2. **Unserialized Python RNG Stream Position (`e85d92a_2` continuation witness)**:
   - On a `65`-interaction trajectory (`20` logins, `1,365` API requests) where **both `N` and `C` satisfy `O AND D_pre AND V`** and share identical pre-probe sorted SQLite table hashes, executing one identical continuation call (`send_password_reset_code`) returns `HTTP 200` and identical printed text under both policies yet writes **divergent post-call Spotify/Gmail database rows in `2/2` pairs**. Explicitly synchronizing `random.seed(20261107)` immediately before the probe eliminates the row divergence in `2/2` pairs—proving that `O AND D_pre AND V` does not certify counterfactual branch equivalence unless RNG stream state is checkpointed.
3. **In-Memory Authentication Manager State (`JWT` token aliasing under `C`)**:
   - AppWorld tracks logged-out tokens in an in-memory blacklist omitted from SQLite deltas. Because `C` resets `random.seed(123)` at a frozen simulated clock before each interaction, `20` separate logins mint **only `1` distinct JWT** (`current == shared`), whereas `N` mints **`20` distinct JWTs** (`current != shared`). Calling `logout(current)` followed by `show_account(shared)` and `create_playlist(..., shared)` succeeds (`HTTP 200`, `+1` playlist row) under `N` but fails (`HTTP 401`, `0` rows) under `C` across `2/2` natural pairs (`10/12` closeout runs complete, `2` infrastructure-censored). Per-step reseeding fixes transcript replay at the cost of introducing synthetic token-aliasing bugs for counterfactual branching.

### 3. In-Process Test Oracles Corrupt Post-Oracle State Exports (`68 -> 58` False Drop)
- Running AppWorld's native test oracle in the same Python process rebinds shared SQLAlchemy/ORM model classes back to baseline input-database directories. Consequently, exporting database deltas *after* calling the oracle falsely drops strict replay admission from **`42 -> 35`** under `N` and **`68 -> 58`** under `C` (**`10` falsely rejected `C` cases** across `4` task families: `3` phone, `6` venmo, `1` supervisor).
- Retaining references to the original pre-oracle output-cache trackers prior to oracle invocation restores **`10/10`** affected cases (`22/24` attempts complete, `2` control attempts resource-censored) with zero row mutations.

### 4. External Boundary Check (`BFCL` Pilot)
- Across a `12`-case (`24`-attempt) pilot on `bfcl-eval 2025.12.17` (`Qwen3-8B-FC`), fixed-action replay produced **`0` discrepancies** across `254` decode events, `196` tool returns, and `114` public filesystem snapshot groups, while a `2`-attempt `cwd` probe confirmed that public-root-only snapshots still miss private working-directory state unless explicitly captured.

---

## Engineering Takeaways

- **Report a replay contract ladder (`V`, `D_pre AND V`, `O AND D_pre AND V`)** rather than a single "deterministic replay rate," and verify whether excluded traces disproportionately drop multi-auth or long-horizon cohorts.
- **Snapshot persistent state *before* invoking test oracles—or isolate test oracles in child processes**—so verifier teardown/ORM rebinding never pollutes exported episode diffs.
- **Serialize PRNG state and in-memory auth/session registries at branch checkpoints** before running counterfactual step interventions (see [`sealed-replayable-agent-audit-log`](../skills/sealed-replayable-agent-audit-log/SKILL.md) and [agent-evaluation-quality.md](../rules/agent-evaluation-quality.md)).
