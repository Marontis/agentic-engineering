---
name: counterfactual-privilege-role-induction
description: >
  Induce compact, least-privilege tool-role masks for multi-tool LLM agents
  before session startup using active sandbox counterfactual interventions,
  variational information-bottleneck role compression, and Stackelberg
  blast-radius pruning over tool data-flow reachability graphs. Derived from
  PRISM (arXiv:2611.11539).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Counterfactual Privilege Role Induction

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill to replace flat full-catalog tool exposure or frequency-mined
RBAC roles with **causally minimal, blast-radius-bounded pre-session role
masks** across MCP gateways, coding/incident-triage agents, customer-service
agents, and multi-API enterprise assistants.

## When to Use

- An agent runtime connects to dozens of tools (`20–100+` endpoints across
  MCP servers or internal APIs) where read, write, outbound-communication,
  and code-execution surfaces coexist.
- You can replay representative benign tasks inside a **resettable,
  side-effect-isolated sandbox** before deploying role policies to production.
- Frequency-based role mining (`RoleMiner`), static schema graphs, or LLM-only
  policy synthesis either retain exploratory high-risk tools (such as shell
  or outbound messaging) or fracture the catalog into dozens of brittle per-task
  allow-lists.
- You want pre-session tool scoping enforced *before* untrusted data-plane
  content enters context, paired with server-side invocation enforcement.

## Core Insight

**Observational tool-call frequency measures agent habit, not causal task
necessity.** Under full tool access, capable LLMs routinely invoke convenient
high-privilege shortcuts—for example, calling `terminal.execute` in **31%** of
full-access log-triage rollouts when read-only `cloud.read_file` already
suffices. Observational role mining mistakes those exploratory habits for
required permissions, whereas static schema reachability misses creative
multi-tool substitutions (`67.5%` recall).

Inducing least-privilege roles requires three coupled stages:
1. **Interventional necessity (`do(m)`)**: Actively mask tool subsets in a
   resettable sandbox to learn a monotone predictor $f_\phi(\tau, m)$ of task
   success when tools are *withheld*, separating necessary tools from
   replaceable habits.
2. **Information-bottleneck role compression**: Compress task trajectories into
   a small discrete codebook of binary role masks $m^{(z)} \in \{0, 1\}^M$ at
   the rate-distortion curvature knee—amortizing the sandbox budget without
   additional live rollouts—and train a **task-text-only pre-session router**
   $g_\omega(z \mid \tau)$ so untrusted runtime tool outputs cannot steer role
   selection.
3. **Stackelberg blast-radius pruning**: Prune each role mask over a
   schema-plus-trace tool reachability graph $G = (\mathcal{T}, E)$ to minimize
   worst-case single-entry compromise reach into high-risk sinks, sampling
   structurally diverse candidate masks for human security review.

**Verified Evidence** (`325` tasks, `160` tools across `AgentDojo`, `τ-bench`,
and `ToolEmu`; `4` backbones: `GPT-4o`, `Claude-3.5-Sonnet`, `Llama-3.1-70B`,
`Qwen2.5-72B`):
- Retains **78.2%** task success vs. **79.4%** under `FullAccess` ($p = 0.21$,
  statistically indistinguishable; cross-backbone SD `2.1` percentage points)
  while cutting granted tools per role by **78.3%** (`45.7 -> 9.9` tools across
  `6.7` induced roles).
- Reduces worst-case single-point compromise blast radius from **100.0%**
  (`FullAccess`), **58.6%** (`RoleMiner`), and **33.8%** (`Progent`) to
  **15.9%** ($p < 0.01$), and shrinks attacker lateral reach from **7.9** hops
  to **1.6** hops (`12.9 min` end-to-end induction time across `32` parallel
  sandboxes).
- On `486` `AgentDojo` indirect prompt-injection test cases, reduces successful
  high-risk attacker tool executions from **58.2%** (`FullAccess`) and **20.5%**
  (`Progent`) to **6.1%**—without inspecting data-plane payloads at runtime.

---

## Step-by-Step Procedure

### Step 1: Partition the High-Risk Tool Set and Prepare Resettable Sandboxes

1. Classify every tool $t_j \in \mathcal{T}$ (`j = 1..M`) into one of four
   effect classes from its schema and documentation: `read`, `write`,
   `outbound`, or `execute`.
2. Define the **high-risk sink set** $\mathcal{H} \subseteq \mathcal{T}$ as the
   union of `write`, `outbound`, and `execute` tools (in PRISM's evaluation,
   two annotators achieved Cohen's $\kappa = 0.84$, marking `39.4%` of `160`
   tools as high-risk).
3. Wrap the benchmark or staging task suite $\mathcal{D}_{\mathrm{train}}$ in a
   deterministic or resettable sandbox so tool subsets can be hard-masked via
   `do(m)` (ungranted tools $m_j = 0$ are hidden from tool listings and blocked
   at the dispatcher) with automated task-completion grading $Y \in \{0, 1\}$.

### Step 2: Estimate Monotone Counterfactual Necessity via Active `do(m)` Rollouts

Rather than ablating tools one at a time ($O(|\mathcal{D}| \cdot 2^M)$), fit a
parametric **counterfactual necessity model** $f_\phi(\tau, m) \in [0, 1]$
(self-attention over tool embeddings gated by binary mask $m$, conditioned on
frozen task embedding $\tau$) within an intervention budget $B$ (`~512`
sandbox rollouts per domain):

1. **Collect reference full-access traces**: Run each training task once under
   $m = \mathbf{1}$ to record baseline completion $Y$, observed tool usage, and
   single-tool knockout marginals on used tools.
2. **Actively acquire high-uncertainty, sparse, high-risk masks**: In rounds,
   select the next `(task, mask)` pair maximizing predictive entropy weighted
   toward high-risk retention and mask sparsity:
   $$(\tau^\star, m^\star) = \arg\max_{(\tau, m)} \mathbb{H}[f_\phi(\tau, m)] \cdot \Big(1 + \eta |\{j : m_j = 1, t_j \in \mathcal{H}\}|\Big) \cdot \Big(1 + \kappa (1 - \|m\|_1 / M)\Big)$$
   Default hyperparameters: high-risk weight $\eta = 2.0$, sparsity weight
   $\kappa = 1.0$. Execute $(\tau^\star, m^\star)$ in the resettable sandbox to
   obtain ground-truth $y \in \{0, 1\}$.
3. **Enforce monotonicity and marginal calibration during training**: Optimize
   binary cross-entropy plus a partial-order monotonicity penalty over sampled
   comparable mask pairs $m \preceq m'$:
   $$\Omega_{\mathrm{mono}}(\phi) = \mathbb{E}_{m \preceq m'}\!\left[\max\!\big(0, f_\phi(\tau, m) - f_\phi(\tau, m')\big)^2\right]$$
   alongside an $L_2$ calibration term anchoring single-tool necessity
   $f_\phi(\tau, \mathbf{1}) - f_\phi(\tau, \mathbf{1}_{-j})$ to empirical
   leave-one-out knockouts. On `5,312` ground-truth `(task, mask)` pairs, this
   reaches **88.7%** 1–2 tool removal accuracy and **81.4%** sparse-mask
   (`20–40%` tools retained) accuracy (**0.941** AUROC) in `512` rollouts
   (`7.6 min`), outperforming frequency mining (`66.8%` / `55.4%`, `0.712`
   AUROC) and matching `6,144`-rollout Shapley sampling (`83.5%` / `75.3%`) at
   `<10%` of the wall-clock cost (`83.2 min`).

### Step 3: Induce Discrete Roles at the Information-Bottleneck Knee and Train a Pre-Session Router

Compress continuous per-task necessity into $K$ reusable operational roles
without running additional sandbox rollouts:

1. **Optimize the privilege-penalized variational IB objective**: Encode full
   training trajectories $x = (\tau, a_{1:T}, o_{1:T})$ into discrete role
   latents $Z \in \{1, \dots, K_{\max}\}$ (`K_max = 24`) paired with binary
   role masks $m^{(z)} \in \{0, 1\}^M$ (Gumbel-Softmax + straight-through
   estimator with vector-quantized codebook updates), using $f_\phi$ as a
   differentiable task-success surrogate:
   $$\mathcal{L}_{\mathrm{IB}} = I(Z; X) - \beta\, \mathbb{E}_{\tau, q_\psi}\!\big[\log f_\phi(\tau, m^{(Z)})\big] + \lambda\, \mathbb{E}_{q_\psi}\!\big[\|m^{(Z)}\|_1 + \rho \|m^{(Z)} \odot \mathbb{1}_{\mathcal{H}}\|_1\big]$$
   Keep the high-risk sparsity multiplier in $\rho \in [1, 5]$ (default
   $\rho = 3.0$; values $> 5$ flatten blast-radius gains while degrading task
   success).
2. **Select the role count $k^\star$ automatically via rate-distortion
   curvature**: Sweep $\beta$ over a log-spaced grid (`20` values in
   `[0.1, 50]`), plot role-assignment entropy $R = H(Z)$ against predicted
   failure distortion $D = \mathbb{E}_\tau[1 - f_\phi(\tau, m^{(z)})]$, and pick
   the maximum-curvature knee $\beta^\star = \arg\max_\beta \frac{|R''(D)|}{(1 + R'(D)^2)^{3/2}}$
   with effective role count $k^\star = \lceil 2^{H(Z)|_{\beta=\beta^\star}} \rceil$
   (typically `6–8` roles for `30–70` tools).
3. **Distill a task-text-only pre-session router $g_\omega(z \mid \tau)$**:
   Because full trajectories $x$ do not exist before execution—and runtime tool
   outputs are untrusted—train a lightweight classifier $g_\omega(z \mid \tau)$
   to predict the encoder's modal role assignment **strictly from the initial
   trusted task specification $\tau$** (`94.6%` role-assignment accuracy; `0.8`
   pp TSR gap vs. an oracle trajectory router).
4. **Apply conservative intersection fallback on ambiguous tasks**: At session
   start, if $\max_z g_\omega(z \mid \tau) < \delta$, grant only the
   **intersection** $m^{(z_1)} \odot m^{(z_2)}$ of the top-2 predicted roles and
   require explicit out-of-band confirmation before enabling any tool in the
   symmetric difference (triggers in **6.8%** of sessions).

### Step 4: Prune Worst-Case Blast Radius over the Tool Reachability Graph

Causal compression alone can still leave multi-hop data-flow chains from an
untrusted read tool into high-risk sinks (`27.3%` blast radius without pruning):

1. **Build the hybrid tool reachability graph $G = (\mathcal{T}, E)$**: Add a
   directed edge $(t_u, t_v) \in E$ whenever:
   - *Static schema match*: a return field of $t_u$ shares a normalized JSON
     Schema type or semantic identifier tag with a required input parameter of
     $t_v$; or
   - *Empirical trace provenance*: in the Step 2 reference traces, a string
     literal (`>= 6` characters) returned by $t_u$ appears verbatim inside a
     subsequent argument to $t_v$ above frequency threshold $\theta$.
   (Across `200` audited `(mask, entry)` pairs, this hybrid graph covered
   **93.8%** of empirically reached tools while overestimating reach by only
   `0.7` tools on average.)
2. **Evaluate defender-first Stackelberg blast radius**: For any candidate role
   mask $m$ and single compromised data-plane entry tool $e$ (`m_e = 1`), let
   $\mathrm{Reach}(e, m)$ be the nodes reachable from $e$ in the induced
   subgraph $G[\{t_j : m_j = 1\}]$. Score the mask by its worst-case high-risk
   reachability fraction:
   $$\mathrm{BR}(m) = \max_{e : m_e = 1} \frac{|\mathrm{Reach}(e, m) \cap \mathcal{H}|}{|\mathcal{H}|}$$
   subject to the role's causal utility floor
   $\mathbb{E}_{\tau \sim \mathcal{D}_z}[f_\phi(\tau, m)] \ge 1 - \epsilon$
   ($\epsilon \in [0.22, 0.38]$ trades TSR `79.1% -> 76.4%` against BR
   `21.8% -> 14.2%`).
3. **Sample diverse near-optimal role candidates for security sign-off**: When
   multiple incomparable masks satisfy the utility floor (e.g., read-plus-ticket
   vs. query-api-plus-webhook), train a Trajectory-Balance GFlowNet over
   sequential bit-flip actions with reward
   $R(m) = \exp\!\big(\frac{1}{T}[\alpha \bar{f}_\phi(m) - \gamma \mathrm{BR}(m) - \lambda \|m\|_1]\big)$
   to present `3–5` structurally distinct masks per role (mean pairwise Jaccard
   distance **0.68** vs. **0.19** under greedy pruning).
4. **Gate role-catalog deployment and re-induction**: Treat every newly induced
   or updated role codebook as a security-critical configuration change—follow
   `"Pass every self-modification through one acceptance gate"` in
   [`recursive-improvement.md`](../../rules/recursive-improvement.md) by
   verifying both benign task-completion retention and worst-case $\mathrm{BR}(m)$
   reduction on held-out tasks before promoting the role catalog, and enforce
   the resulting masks server-side via
   [`mcp-zero-trust-tool-authorization`](../mcp-zero-trust-tool-authorization/SKILL.md).

```json
{
  "role_id": "log_triage_incident_reporter",
  "granted_tools": [
    "cloud.list_buckets", "cloud.read_file", "logs.query_range",
    "logs.get_trace", "metrics.read_series", "tracker.create_issue"
  ],
  "pruned_exploratory_tools": ["terminal.execute", "slack.post_message"],
  "high_risk_granted": ["tracker.create_issue"],
  "predicted_task_success": 0.91,
  "blast_radius_fraction": 0.048
}
```

---

## Ablation Reference

| Variant | Task Success (%) | Roles Induced | Blast Radius (%) | Necessity Acc (`Acc_{1/2}`) | Candidate Diversity |
|:--------|:----------------:|:-------------:|:----------------:|:---------------------------:|:-------------------:|
| **Full PRISM** | **78.2** | **6.7** | **15.9** | **88.7%** | **0.68** |
| w/o Causal Intervention (observational freq.) | 69.5 | 10.8 | 31.2 | 66.8% | 0.61 |
| w/o Active Sampling (uniform `do(m)`) | 76.9 | 7.1 | 20.1 | 85.2% (`2x` rollouts) | 0.65 |
| w/o Information Bottleneck ($K$-means on $f_\phi$) | 77.6 | 13.1 | 22.8 | 88.7% | 0.64 |
| w/o Stackelberg Layer (IB masks directly) | 77.8 | 6.7 | 27.3 | 88.7% | 0.52 |
| w/o GFlowNet Sampling (greedy bit-drop) | 77.4 | 6.7 | 18.6 | 88.7% | 0.19 |

---

## Environment Caveats

- **Pre-session tool-set granularity, not argument-level DLP**: Role masks
  decide *which tools* exist in a session (`m_j \in \{0, 1\}`), not *which
  parameter values* are safe inside an authorized high-risk tool. If a task
  legitimately requires `email.send` or `tracker.create_issue`, pair pre-session
  role masks with deterministic parameter canonicalization and taint-gated
  review (see [`provenance-capability-grants`](../provenance-capability-grants/SKILL.md)
  and [`untrusted-model-deterministic-policy-taint-hitl`](../../research-briefs/untrusted-model-deterministic-policy-taint-hitl.md)).
- **Requires a resettable staging/sandbox oracle**: Active `do(m)` interventions
  (`~512` rollouts, `~3.6 h` serial or `7.6 min` at `32`-way parallelism) assume
  side-effect-isolated mocks or snapshots and reliable task-completion grading.
  Noisy LLM-judged environments (`ToolEmu`) degrade necessity accuracy (`84.3%`
  vs. `91.2%` on `AgentDojo`) and widen blast radius (`23.6%` vs. `15.9%` mean).
- **Natural-language credential laundering across tool calls**: Static-plus-literal
  reachability graphs capture `93.8%` of empirical flows but miss edges (`7/200`
  audited pairs) where the LLM paraphrases or re-encodes a secret read from one
  tool before passing it to another. Add semantic taint edges between sensitive
  read sources and outbound sinks when paraphrased exfiltration is in scope.
- **Catalog drift**: Adding, removing, or changing tool schemas invalidates rows
  of $G$ and mask indices in $f_\phi$; warm-start incremental interventions on
  modified neighborhoods rather than reusing stale masks silently.

## Failure Modes

| Failure Mode | Trigger | Mitigation |
|:--|:--|:--|
| Exploratory habit retention | Mining roles from observational traces without `do(m)` interventions | Run active `do(m)` rollouts (Step 2); removing causal interventions doubles BR (`15.9% -> 31.2%`) and drops TSR (`78.2% -> 69.5%`) |
| Runtime router hijacking | Feeding intermediate tool outputs into the role selector $g_\omega$ | Restrict $g_\omega(z \mid \tau)$ strictly to initial trusted task text $\tau$ before any external read executes (Step 3.3) |
| Over-penalized high-risk collapse | Setting high-risk multiplier $\rho > 5$ in the IB loss | Keep $\rho \in [1, 5]$ (`3.0` default) and use $\epsilon \in [0.22, 0.38]$ in Step 4 to control utility vs. BR |
| Ambiguous multi-domain prompt | Task spans two induced roles with low router confidence ($\max_z g_\omega < \delta$) | Intersect top-2 role masks and gate symmetric-difference tools on explicit user confirmation (Step 3.4) |
| Client-only mask enforcement | Filtering tool schemas in the prompt without blocking `tools/call` server-side | Bind the selected role mask to a scoped session credential verified by the MCP server (`mcp-zero-trust-tool-authorization`) |

## Cross-References

- [`mcp-zero-trust-tool-authorization`](../mcp-zero-trust-tool-authorization/SKILL.md) — server-side `list_tools` and `call_tool` enforcement for the induced role permissions
- [`principal-context-permission-intersection`](../principal-context-permission-intersection/SKILL.md) — runtime intersection of caller permissions with untrusted context provenance
- [`provenance-capability-grants`](../provenance-capability-grants/SKILL.md) — fine-grained capability and taint enforcement for arguments inside authorized high-risk tools
- [`mcp-tool-hijacking-defense`](../mcp-tool-hijacking-defense/SKILL.md) — defending tool discovery and routing against poisoned MCP metadata
- [`untrusted-model-deterministic-policy-taint-hitl`](../../research-briefs/untrusted-model-deterministic-policy-taint-hitl.md) — why deterministic capability monitors and approval budgets remain needed for in-role high-risk tools
- [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — always-active sandbox and tool-privilege rules
- [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"Pass every self-modification through one acceptance gate"` when promoting newly induced or updated role codebooks

## Sources

> Yang Luo, Qingni Shen, Tairui Wang, Jiajun Li & Zhonghai Wu, "PRISM: Causal
> Counterfactual Minimization of Agent Tool Privileges via Information
> Bottleneck Role Induction" (arXiv:2611.11539), Nov 2026.
