---
name: decoupled-interface-action-repair
description: >
  Decouple an agent's semantic action commitment (which operation and typed
  arguments are intended) from its interface-specific realization (MCP JSON
  schema vs CLI command/flags), preserve validated semantic commitments when
  a tool call fails surface decoding or validation, and run targeted local
  realization repair instead of re-invoking full trajectory replanning. Also
  includes MICA matched-state probing to diagnose whether tool-use failures
  stem from capability presentation, realization grammar, or feedback format.
  Derived from "Matched Capabilities, Different Behaviors: A Controlled Study
  of MCP and CLI Interfaces for Language Agents" (arXiv:2610.34298).
source: https://arxiv.org/abs/2610.34298
---

# Decoupled Interface Action Realization and Targeted Repair (DART & MICA)

Use this skill when an interactive language agent accesses capabilities through
structured tool calls (MCP) or command-line interfaces (CLI) and suffers from
surface realization failures (quoting errors, JSON schema mismatches, missing
containers), unstable retry behavior that discards valid semantic decisions, or
unexplained performance/cost shifts when switching between MCP and CLI.

## When to Use

- An agent selects the right operation and arguments semantically, but fails
  surface decoding or schema validation (e.g., POSIX single-quote escaping on
  CLI strings like `18''x18''` or flat vs nested `arguments` keys in MCP JSON).
- Ordinary error-recovery prompts cause the model to abandon a valid semantic
  action and pick a worse action on retry.
- You are comparing or migrating between MCP and CLI tool interfaces and need
  to separate capability packaging differences from model-facing representation
  effects (`Φ` presentation, `R` realization, `Ψ` feedback).
- You want to cut retry token waste in multi-step tool trajectories without
  expanding the agent's action authority or modifying downstream execution
  safeguards.

---

## Core Insight

Model-facing interface representation is part of the closed-loop decision
environment, not a passive transport layer. Even when MCP and CLI are generated
from the exact same semantic action contract $\mathcal{C}_t$ and share the same
downstream validator $V$, compiler $K$, and execution engine $E$, they induce
different action selections, failure stages, and recovery trajectories.

Across 6 models (`Qwen3-4B`, `Qwen3-8B`, `Qwen3-14B`, `Qwen3-32B`,
`DeepSeek-v4-Flash`, `Gemini-2.5-Flash`) and 3 interactive environments
(ALFWorld, WebShop, ScienceWorld; 2,004 paired episodes total):

- **Widespread early trajectory divergence**: 1,889 of 2,004 paired MCP–CLI
  episodes (94.3%) exhibit structured consequential divergence $t^\star$,
  beginning near the start of interaction.
- **Model- and environment-dependent reversals**: On `Qwen3-14B`, MCP trails
  CLI by 36.6 score points on ALFWorld (20.1 vs. 56.7) and uses 54.9k more
  tokens per task (296.8k vs. 241.9k, increasing model calls from 46.9 to
  57.1 per task), but beats CLI by 4.9 points on WebShop (64.4 vs. 59.5) while
  using 35.0k fewer tokens per task (48.1k vs. 83.1k, cutting calls from 14.2
  to 9.6 and tokens/call from 4.26k to 3.23k).
- **Component non-additivity (MICA $2 \times 2 \times 2$ probes)**: Across 338
  source states and 21,632 sampled responses, realization $R$ drives local
  realization-failure shifts of up to 84.4 percentage points
  (ALFWorld/`Qwen3-32B`, where switching only realization from MCP to CLI
  raises realization failure from 1% to 87% under MCP presentation and 0% to
  89% under CLI presentation) and 72.9 points (ScienceWorld/`Qwen3-4B`), while
  three-way $\Phi \times R \times \Psi$ interactions shift admission given
  decoding by up to 37.8 percentage points (WebShop/`Qwen3-14B`).
- **Commitment-preserving repair (DART)**: Separating semantic commitment
  from surface realization improves `Gemini-2.5-Flash` benchmark score in all
  6 evaluated benchmark–interface settings and reduces MCP token cost in all
  3 environments:

| Environment | CLI Score $\Delta$ | MCP Score $\Delta$ | CLI Tokens/Task $\Delta$ | MCP Tokens/Task $\Delta$ |
|:------------|:-------------------|:-------------------|:-------------------------|:-------------------------|
| ALFWorld | +1.5 | +9.0 | −0.8k | −27.1k |
| WebShop | +0.8 | +4.4 | +4.8k | −11.2k |
| ScienceWorld | +6.7 | +5.3 | +1.6k | −4.3k |

Across the six settings, 71–100% of triggered DART interventions are admitted
on the first realization, and 3 of the 4 interventions that proceed to a
preserving-correction opportunity are admitted after a single correction.

---

## Procedure

### Phase 1: Factorize the Interface Contract (MICA Boundary)

1. **Define a canonical semantic action contract $\mathcal{C}_t$**:
   Represent every state-local capability as a tuple
   $\mathcal{C}_t = \{(u, \Sigma_u, \mathcal{V}_u(s_t), \Gamma_u) \mid u \in \mathcal{U}_t\}$,
   where $u$ is the canonical operation identifier (e.g., `alfworld.move`),
   $\Sigma_u$ specifies its normalized typed arguments, $\mathcal{V}_u(s_t)$ is
   its state-local admissible argument domain, and $\Gamma_u$ is its native
   execution binding.
2. **Factorize the model-facing interface into three exchangeable blocks**:
   For interface $I \in \{\text{MCP}, \text{CLI}\}$, separate:
   - **Presentation ($\Phi_I$)**: How available operations, argument types, and
     state constraints are rendered in the prompt.
   - **Realization ($R_I = (\rho_I, D_I)$)**: The required output container and
     syntax $\rho_I$ (e.g., `<tool_call>{"name": ..., "arguments": {...}}</tool_call>`
     vs. `<command>bench ... --flag 'value'</command>`) and the parser/decoder
     $D_I$ that maps raw text $y_t^I$ to a normalized semantic action
     $\hat{a}_t^I = (u_t, v_t) \in \mathcal{A}_{\mathcal{C}_t}(s_t) \cup \{\bot\}$.
   - **Feedback ($\Psi_I$)**: How execution outcomes $\omega_t$ and validation
     failure diagnostics $f_t$ are formatted back into the conversation history.
3. **Verify round-trip conformance before deployment**:
   Ensure every registered semantic action $a = (u, v)$ satisfies both
   round-trip decoding equivalence and identical native compilation:
   ```
   D_MCP(Render_MCP(a)) ≡_sem a ≡_sem D_CLI(Render_CLI(a))
   K_{C_t}(D_MCP(y_MCP)) = K_{C_t}(a) = K_{C_t}(D_CLI(y_CLI))
   ```

### Phase 2: Localize Interface Sensitivity with MICA Probes (Diagnostic)

When diagnosing why an agent underperforms on a specific interface:

1. **Sample matched decision contexts**: Freeze a set of representative
   environment states $s_t$ and canonical semantic interaction histories $h_t$.
2. **Run the $2 \times 2 \times 2$ factorial probe ($\xi = (\xi_\Phi, \xi_R, \xi_\Psi) \in \{\text{MCP}, \text{CLI}\}^3$)**:
   Render prior actions and observations from the canonical semantic ledger
   into each of the 8 component combinations (`MMM`, `MMC`, `MCM`, `MCC`,
   `CMM`, `CMC`, `CCM`, `CCC`) and draw repeated samples (e.g., 8 draws at
   $T = 0.6$) per state.
3. **Compute component main and interaction effects**:
   Measure three local metrics per condition:
   - **Realization failure rate**: $1 - (n_{t,\text{dec}}^I / n_t^I)$, the
     fraction of draws failing to decode into a registered semantic proposal.
   - **Semantic admission rate**: The fraction of decoded proposals accepted by
     the shared validator $V(s_t, \hat{a}_t^I) = 1$.
   - **Semantic-action entropy**:
     $H_t^I = -\sum_a \hat{p}_t^I(a \mid \text{dec}) \log_2 \hat{p}_t^I(a \mid \text{dec})$.
   If realization failure dominates under a specific $\xi_R$ while admission
   remains high once decoded, deploy DART (Phase 3) at the realization
   boundary rather than changing the underlying tool set.

### Phase 3: Run Error-Triggered Commitment-Preserving Repair (DART)

Keep the ordinary single-call policy active during normal execution. Activate
the DART controller **only** on eligible triggers: retryable, policy-owned
failures where the environment state $s_t$ is confirmed unchanged (surface
decoding errors, schema validation rejections, or retryable backend rejections)
and at least 2 model calls remain in the episode call budget $B_{\text{call}}$.

#### Step 1: Elicit and Validate a Canonical Semantic Commitment

Issue a selection-only request (`Invoke(selection, x, f, C)`) that temporarily
supersedes the MCP/CLI surface rules and instructs the model to output a single
canonical JSON object with keys `schema_id` and `arguments` grounded in the
active contract $\mathcal{C}_t$:

```json
{
  "schema_id": "webshop.click",
  "arguments": {
    "target": "18''x18''"
  }
}
```

- Decode the response via `DecodeSelection(z, C)`.
- If decoding fails ($\bar{a} = \bot$) or shared semantic validation fails
  ($\neg V_{\mathcal{C}_t}(\bar{a})$), **release** immediately to the ordinary
  retry policy.
- Otherwise, bind the validated semantic commitment $c_t = (\kappa_t, \bar{a}_t)$,
  where $\kappa_t = \kappa(\mathcal{C}_t)$ is the contract identity and
  $\bar{a}_t = (\bar{u}_t, \bar{v}_t)$ fixes the operation and every normalized
  typed argument.

#### Step 2: Realize the Fixed Commitment in the Target Interface

Issue an initial realization request (`Invoke(realization, x, c_t, I)`)
supplying the validated commitment $c_t$ and the target interface contract $I$:

> *"Realize the validated semantic commitment below using the assigned
> interface response contract above. Preserve the operation and every typed
> argument exactly. Do not select a different action. Return only the required
> interface expression."*

Check the **Preservation Gate** (`Preserves(y, c_t, C, I)`):
1. The active contract is unchanged: $\kappa_{\text{current}} = \kappa_t$.
2. The surface output $y$ decodes to the exact committed operation and
   normalized arguments: $D_I(y) \equiv_{\kappa_t} \bar{a}_t$.
3. The committed action remains valid: $V(s_t, \bar{a}_t) = 1$.

If all three hold, admit $D_I(y)$ and execute it in the shared runtime.

#### Step 3: Run One Commitment-Preserving Surface Correction (If Needed)

If the initial realization $y$ fails the preservation gate while $c_t$ remains
valid ($\text{Valid}(c_t, \mathcal{C}_t)$) and at least 1 call remains in
$B_{\text{call}}$:

1. Extract the public failure diagnostic $f' = \text{PublicFailure}(y, D_I(y), c_t)$
   (e.g., lost literal apostrophes or invalid container keys).
2. Issue at most **one** preserving-correction request
   (`Invoke(correction, x, c_t, y, f', I)`):
   > *"Correct the failed realization using the assigned interface response
   > contract above. Preserve the committed operation and every typed argument
   > exactly. Correct only its interface expression. Return only the required
   > interface expression."*
3. Re-check `Preserves(y', c_t, C, I)`. If admitted, execute $D_I(y')$;
   otherwise, release to the ordinary retry policy.

---

## Environment Caveats

- **Unchanged-state precondition is mandatory**: Never run commitment-preserving
  repair if the failed tool call partially mutated external state. DART assumes
  rejected proposals do not consume an environment transition.
- **Treat the failed raw string as ungrounded**: In Step 1 (Prompt S3),
  explicitly instruct the model that *"the failed text does not establish an
  original latent intent"*—the semantic commitment must be chosen and validated
  against the current public contract $\mathcal{C}_t$, not blindly scraped from
  the broken string.
- **Budget accounting**: Semantic selection, initial realization, and preserving
  correction consume 2 to 3 model calls on triggered steps. Despite this per-trigger
  cost, DART lowers total episode tokens under MCP across all three environments
  by preventing cascading multi-turn retry loops.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Retry abandons a good plan | Standard retry prompt re-opens action selection after a syntax error | Lock $c_t = (\kappa_t, \bar{a}_t)$ first, then restrict repair to surface expression (Steps 1–3) |
| Silent argument corruption | CLI quote stripping turns `'18''x18'''` into `18x18` without a parser crash | Enforce `Preserves`: check $D_I(y) \equiv_{\kappa_t} \bar{a}_t$ on every normalized argument before execution |
| Stale commitment execution | Environment state or contract changes during async retry | Verify $\kappa_{\text{current}} = \kappa_t$ and $V(s_t, \bar{a}_t) = 1$ in the preservation gate |
| Infinite repair loops | Repeatedly asking the model to fix a complex flag syntax | Cap preserving correction at 1 attempt after initial realization, then release to fallback |
| Confounding interface benchmarks | Comparing CLI vs MCP with different tool granularities or validators | Build both surfaces from a shared $\mathcal{C}_t$ and verify round-trip equivalence (Phase 1) |

## Cross-References

- [`deterministic-span-editing`](../deterministic-span-editing/SKILL.md):
  separates semantic field-change intent from deterministic file-span
  application in declarative configuration editing.
- [`counterexample-guided-repair`](../counterexample-guided-repair/SKILL.md):
  uses compact executable-oracle witnesses to guide multi-turn artifact repair.
- [`mcp-vs-cli-tool-integration-analysis`](../../research-briefs/mcp-vs-cli-tool-integration-analysis.md):
  complementary 14-dimension architectural analysis of when to deploy CLI vs
  MCP across trust and governance boundaries.
- `rules/agent-sandbox-safety.md`: "DON'T: Put steps the calling agent can't
  execute in tool error text".
- `rules/skill-system-design.md`: "DO: Keep deterministic steps in code and
  explicit graph edges; delegate to LLMs only for reasoning".

> Source: Matched Capabilities, Different Behaviors: A Controlled Study of MCP
> and CLI Interfaces for Language Agents (arXiv:2610.34298), Oct 2026. Praxis
> source: src:2610-34298
