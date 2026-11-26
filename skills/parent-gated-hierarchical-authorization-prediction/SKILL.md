---
name: parent-gated-hierarchical-authorization-prediction
description: Predict structurally consistent batch permission proposals over multi-parent capability DAGs from sparse historical user decisions using ancestor-masked Transformer attention, shortest-path depth encodings, and parent-gated chain-rule probability recursion. Use when pre-populating personalized permission onboarding dialogs, enterprise workspace capability bundles, IDE/CLI tool-consent batches, or IoT/mobile delegation scopes without ancestor-consistency violations.
source: "Structure-Aware Transformers for Hierarchical Authorization in Personal AI Agents (arXiv:2611.32018)"
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Parent-Gated Hierarchical Authorization Prediction (`PATH`)

When onboarding users or configuring multi-domain agents across hundreds of fine-grained permissions, prompting for every capability individually causes severe consent fatigue, while coarse all-or-nothing domain toggles grant excessive ambient authority. Learning personalized batch permission proposals from partial historical user decisions introduces three structural traps:
1. **Independent node classifiers violate ancestor consistency**: Predicting each permission node independently frequently assigns a higher grant probability to a child action (e.g., *send external email* or *execute payment*) than to one of its required parent scopes (e.g., *access mail account* or *view billing*), producing `5.7%–11.9%` structural violation rates (`arXiv:2611.32018`, `Tables 1–4`).
2. **Post-hoc probability clipping degrades ranking calibration**: Truncating child probabilities after training (`IC(post)`) restores hierarchy consistency only by degrading area under the ROC curve (`0.8801 -> 0.8427` in `Simulation 1`, `0.6867 -> 0.6571` in `Simulation 3`, and dropping real-data F1 from `0.3596` to `0.2997`).
3. **Tree-only architectures break on cross-domain `AND`-gate capabilities**: Real agent capabilities form a **directed acyclic graph (`DAG`)** rather than a tree—for example, *auto-pay invoice from email* requires both *email read* and *payment execution* parents (`52` multi-parent nodes with up to `5` parents in `Simulation 1`; `5` strict cross-domain `AND`-gate nodes in `Simulation 3`, where `HMCN-F` still suffers a `0.1421` violation rate).

This skill implements the **Parent-Gated Hierarchical Authorization Transformer (`PATH`, `arXiv:2611.32018`)** workflow: encoding the permission catalog as a rooted multi-parent DAG, restricting self-attention strictly to structural ancestors, predicting conditional per-node gate probabilities, and multiplying parent marginal probabilities in topological order to guarantee **`0.0000` structural violations** for every input and threshold while learning solely from observed historical decisions.

## When to Use

Apply this procedure across any software or agent system that proposes multi-capability permission sets over hierarchical scopes:
- **Personal AI assistants** (`400+` cross-app permissions across email, calendar, health, finance, messaging, and files) pre-populating a reviewable permission bundle from a few initial preference answers.
- **Enterprise workspace & SaaS agent onboarding** proposing role-tailored read/write/admin scopes across multi-parent cloud, CRM, and ticketing APIs.
- **IDE and CLI coding-agent permission profiles** recommending project-start capability bundles (workspace read $\to$ test runner $\to$ package install $\to$ git push) from developer preferences.
- **Mobile, smart-home, and IoT delegation interfaces** suggesting device-capability hierarchies where multi-device automations depend on multiple parent subsystem grants.

Do **not** use predicted authorization probabilities to silently auto-approve irreversible runtime side effects without human confirmation, and do **not** treat static pre-session grant predictions as valid after a user withdraws or narrows scope mid-session (use [`authorization-closure-repair`](../authorization-closure-repair/SKILL.md) and [`dual-obligation-approval-auditing`](../dual-obligation-approval-auditing/SKILL.md) for live mid-session revocation and execution auditing).

## Core Insight

Under the hard ancestor-consistency invariant ($Y_j \le \min_{p \in \mathrm{Pa}(j)} Y_p$), a child capability can be authorized only if **all** of its parent capabilities are authorized. Instead of asking a flat classifier to rediscover DAG monotonicity from sparse (`65%–83%` missing) observations, factorize marginal authorization probabilities directly along the DAG (`arXiv:2611.32018`, `§2.2–§2.5`):
1. Fuse user profile covariates, learned node identity embeddings, and **shortest-path root-distance embeddings** at the input layer.
2. Apply an **ancestor-only causal attention mask** so node $j$ attends exclusively to $\mathrm{Anc}(j) \cup \{j\}$, blocking descendant and sibling leakage while letting multi-parent nodes aggregate context across every required parent branch.
3. Interpret each node's sigmoid head output $q_{ij} \in (0, 1)$ as a **local conditional gate** given satisfied parents, and compute marginal authorization probabilities recursively via $\hat{p}_{ij} = q_{ij} \prod_{p \in \mathrm{Pa}(j)} \hat{p}_{ip}$ ($\hat{p}_{i0} = 1$). Because $q_{ij} \in (0, 1)$, $\hat{p}_{ij} \le \hat{p}_{ip}$ holds **identically** for every parent $p \in \mathrm{Pa}(j)$ and every decision threshold $\tau \in (0, 1)$—driving structural violations to **`0.0000`** while improving F1 (`0.7560` vs. `0.7011` `HMCN-F(post)` and `0.6981` `C-HMCNN` on strict cross-parent `AND` gates; `0.4060` vs. `0.2864–0.3596` on real user permission data).

## Step-by-Step Procedure

### Step 1: Compile a Verified Permission DAG and Shortest-Path Structural Depths

1. **Construct the rooted capability DAG $G = (V_0, E)$**:
   - Introduce a virtual root node $0$ representing baseline session engagement ($\hat{p}_{i0} \equiv 1$), and add `1..m` capability nodes spanning coarse domain gates, intermediate resource scopes, and leaf tool actions (`V_0 = {0, 1, ..., m}`).
   - Add a directed edge $p \to j$ whenever capability $j$ structurally requires parent permission $p$ (`Pa(j)`). Explicitly include **multi-parent (`AND`-gate) edges** whenever a capability crosses domains (e.g., a workflow action reading from domain $A$ and mutating domain $B$ must list both $A$ and $B$ in $\mathrm{Pa}(j)$).
   - Verify acyclicity via topological sort before training or deployment, and fix a canonical topological ordering $(0, v_1, \dots, v_m)$ so every $p \in \mathrm{Pa}(j)$ precedes $j$.
2. **Compute shortest-path depth indices and ancestor closures**:
   - For every node $j \in V$, compute its **shortest-path distance** $s_j \in \{1, \dots, S_{\max}\}$ from virtual root $0$ via breadth-first search (handling multi-parent diamonds deterministically via minimum hop count rather than longest path).
   - Precompute the transitive ancestor set $\mathrm{Anc}(j)$ for every node $j \in V$.

### Step 2: Build Fused User-Node-Depth Tokens and the Ancestor-Only Attention Mask

1. **Encode user profile and sparse historical context into $u_i \in \mathbb{R}^{d_h}$**:
   - Map structured user covariates $x_i \in \mathbb{R}^p$ (such as declared role, privacy posture, domain preferences, or onboarding survey responses; exclude raw sensitive secrets) through a lightweight two-layer MLP (`p -> 128 -> 128` with `ReLU` and `0.1` dropout in the reference `PATH` configuration).
2. **Form per-node input tokens $t_{ij}^{(0)} \in \mathbb{R}^{d_h}$**:
   - Combine the user embedding $u_i$, a trainable capability-node embedding $e_j \in \mathbb{R}^{d_h}$, and a trainable shortest-path depth embedding $d_{s_j} \in \mathbb{R}^{d_h}$ additively:
     $$t_{ij}^{(0)} = u_i + e_j + d_{s_j}$$
3. **Enforce the binary ancestor-only attention mask $M \in \{0, 1\}^{m \times m}$**:
   - Set $M_{jk} = 1$ if and only if $k \in \mathrm{Anc}(j) \cup \{j\}$, and mask all other entries ($M_{jk} = 0 \implies -\infty$ pre-softmax logit) across every pre-norm Transformer encoder layer (`2` layers, `4` heads, `d_h = 128`, `FFN = 512` `GELU`, dropout `0.1`).
   - Do **not** use unmasked full self-attention over the permission graph: allowing node $j$ to attend to descendants or unrelated branches leaks downstream state and breaks top-down causal semantics.

### Step 3: Compute Conditional Gates and Parent-Gated Chain-Rule Marginal Probabilities

1. **Predict local conditional gate probabilities**:
   - Project each final encoder state $h_{ij} = t_{ij}^{(L)}$ through a shared linear head with sigmoid activation:
     $$q_{ij} = \sigma(w^\top h_{ij} + b) \in (0, 1)$$
   - Treat $q_{ij}$ as the user's conditional willingness to grant node $j$ *given that all parent permissions in $\mathrm{Pa}(j)$ are already granted*.
2. **Propagate marginal probabilities in topological order**:
   - Initialize $\hat{p}_{i0} = 1$. Traversing $(v_1, \dots, v_m)$ in topological order, compute:
     $$\hat{p}_{ij} = q_{ij}^{\alpha} \prod_{p \in \mathrm{Pa}(j)} \hat{p}_{ip}$$
     with $\alpha = 1$ by default (`arXiv:2611.32018`, `Eq. 6` & `Appendix C.1`).
   - Verify numerically in `float32` (or log-probability space $\log \hat{p}_{ij} = \alpha \log q_{ij} + \sum_{p \in \mathrm{Pa}(j)} \log \hat{p}_{ip}$ for deep DAGs with depth $> 8$ or high fan-in) to avoid underflow while preserving $\hat{p}_{ij} \le \min_{p \in \mathrm{Pa}(j)} \hat{p}_{ip}$ up to floating-point precision.

### Step 4: Train on Observed Decisions Only and Audit Missingness Regimes

1. **Apply observed-node masked Binary Cross-Entropy (`BCE`)**:
   - Record an observation mask $o_{ij} \in \{0, 1\}$ marking only capabilities the user was explicitly asked about (plus deterministic zero propagation to descendants of explicitly denied parents when enforced by the UI).
   - Minimize masked `BCE` strictly over observed entries (`arXiv:2611.32018`, `Eq. 8`):
     $$\mathcal{L}(\theta) = -\frac{1}{n}\sum_{i=1}^n \sum_{j=1}^m o_{ij}\Big[y_{ij}\log \hat{p}_{ij} + (1 - y_{ij})\log(1 - \hat{p}_{ij})\Big]$$
   - **Never impute unobserved permissions ($o_{ij} = 0$) as `0` (denied)**: with `65%–83%` unobserved entries, zero-imputation conflates unasked capabilities with explicit refusals and collapses recall.
2. **Audit selection bias when observations are not Missing at Random (`MAR`)**:
   - By `Theorem 1` and `Corollaries 1–2` (`arXiv:2611.32018`, `§3.2`), masked empirical risk minimization converges to the observed-data Bayes target $\nu_j(x) = \mathbb{P}(Y_j = 1 \mid X = x, O_j = 1)$, which equals the true user preference $\eta_j(x) = \mathbb{P}(Y_j = 1 \mid X = x)$ when $O_j \perp Y_j \mid X$ (`MAR`, `d_2(\nu, \eta) = 0`), with excess risk scaling inversely with minimum observation propensity $\pi_{\min} = \min_j \inf_x \pi_j(x) > 0$.
   - When historical prompts are collected adaptively (e.g., asking mostly about suspicious or high-friction actions), include small uniform exploration probes during onboarding so $\pi_{\min}$ stays bounded away from zero and `MNAR` gap $d_2(\nu, \eta)$ can be audited directly.
3. **Optional cold-start synthetic profile augmentation**:
   - When real labeled onboarding cohorts are small (e.g., `N <= 200` users across `400+` nodes), generate diversity-constrained synthetic user cohorts conditioned on real feature marginals and enforce ancestor-consistent label propagation (`Simulation 3` & `§5`), keeping all real held-out evaluation splits strictly isolated from synthetic generation prompts.
   - *(Transparency note on `arXiv:2611.32018` real-data split reporting: `§5` reports splitting the `201` Wu et al. `2026` participants into `150` real training + `500` synthetic augmentation = `650` training users and `51` held-out test users, whereas the verbatim `ChatGPT 5.5` prompt reproduced in `Appendix C.5.2` states `51` real training participants and a `150`-person test set over `373` leaf definitions inside the `447`-node DAG. Always log exact train/test split counts in code manifests.)*

### Step 5: Surface Predictions as Evaluable Human Batch Proposals Behind Runtime Gates

1. **Render structured, inspectable permission bundles—never silent grants**:
   - Threshold $\hat{p}_{ij} \ge \tau$ (calibrating $\tau$ on validation F1 / false-grant cost rather than assuming `0.5` is optimal across imbalanced catalogs) to pre-populate a **grouped tree/DAG review checklist** showing each proposed capability alongside its parent domain gates, and highlight high-uncertainty boundary nodes ($\hat{p}_{ij}$ near $\tau$) for explicit human inspection (`ProSE` evaluability principle).
   - Map conservative user choices cleanly: in `arXiv:2611.32018` (`§5`), only `"Yes, always share"` was encoded as `1`, while `"Ask every time"`, `"Depends"`, and `"Never"` were mapped to `0` so persistent batch grants default conservative.
2. **Bind approved bundles to task/context scope and runtime enforcement**:
   - Store human-confirmed grants with task/resource scope (`residual-auth-state-preservation`), enforce them deterministically outside the LLM at tool dispatch, and pass any periodic retraining or threshold update of the `PATH` recommender through `"DO: Pass every self-modification through one acceptance gate"` (`output/rules/recursive-improvement.md`).

## Empirical Performance & Failure Modes Avoided

| Setting (`arXiv:2611.32018`) | Nodes / Missing Rate | `PATH` AUC / F1 / Viol. | Best Flat or Post-Hoc Baseline | Key Takeaway |
|:---|:---|:---|:---|:---|
| **`Sim 1`** (Independent user prefs, `100` reps, `Table 1`) | `171` nodes (`52` multi-parent), `65%` missing | **`0.9013`** / `0.5276` / **`0.0000`** | `IC`: `0.8801` / `0.4282` / `0.0570` (`IC(post)` AUC drops to **`0.8427`**); `CC`: `0.8420` / **`0.5334`** / `0.0000` | Beats all baselines on AUC ($p < 10^{-4}$) with zero violations while `IC(post)` loses `3.74` AUC pts. |
| **`Sim 2`** (Correlated latent prefs $c=0.5$, `Table 2`) | `171` nodes, `65%` missing | **`0.8828`** / `0.4989` / **`0.0000`** | `HMCN-F`: `0.8695` / `0.4150` / `< 10^-4`; `C-HMCNN`: `0.8691` / `0.4166` / `0.0000` | Preserves top ranking accuracy under correlated cross-domain user factors ($p < 10^{-4}$). |
| **`Sim 3`** (LLM synthetic cohort + `5` cross-parent `AND` gates, `Table 3`) | `167` nodes, `83.04%` missing | **`0.7692`** / **`0.7560`** / **`0.0000`** | `HMCN-F`: `0.7474` / `0.7182` / **`0.1421`** (`post`: `0.7380` / `0.7011`); `C-HMCNN`: `0.7217` / `0.6981` | Tree/feedforward hierarchy baselines suffer `14.21%` violations or `-5.5` F1 pts on multi-parent `AND` gates. |
| **Real User Permissions** (Wu et al. `2026` + `500` synthetic aug., `Table 4`) | `447` nodes (`8` domains, `65` scenarios), `78.18%` missing | `0.6773` / **`0.4060`** / **`0.0000`** | `C-HMCNN`: **`0.6778`** / `0.2864` / `0.0000`; `IC`: `0.6687` / `0.3596` / **`0.1129`** (`post` F1 **`0.2997`**) | Matches top AUC while lifting F1 by **`+10.3` to `+12.0` pts** over consistent baselines (`HMCN-F` `0.3019`, `C-HMCNN` `0.2864`). |

- **Optimization caveat (`Appendix B.3`)**: While `Theorem S.1` bounds the expected optimization gap of decreasing-stepsize `Adam` at $O(1/(k+1))$ under local smoothness and Polyak-Łojasiewicz conditions, fixed-learning-rate bias-corrected `Adam` (`lr = 10^-3`, weight decay `10^-4`) used in practice requires validation early stopping to prevent overfitting on sparse real cohorts.
- **Multiplicative depth attenuation**: Deep DAG chains ($S_{\max} \gg 6$) multiply many factors in $(0, 1)$, naturally pushing deep leaf marginals downward; calibrate per-depth or validation-optimal thresholds and adjust $\alpha \le 1$ only if deep leaves suffer systematic under-proposal on validation splits.

## Cross-References

- **Related Skills**:
  - [`authorization-closure-repair`](../authorization-closure-repair/SKILL.md) — Deterministic mid-conversation dependency-closure invalidation when a user revises or revokes a previously granted scope
  - [`dual-obligation-approval-auditing`](../dual-obligation-approval-auditing/SKILL.md) — Four-witness runtime auditing of both `Refusal Safety` and `Bounded Authorization Completeness` after a user approves or rejects a batch proposal
  - [`residual-auth-state-preservation`](../residual-auth-state-preservation/SKILL.md) — Task- and resource-bound grant lifetimes preventing stale stored approvals from replaying out of context
  - [`counterfactual-privilege-role-induction`](../counterfactual-privilege-role-induction/SKILL.md) — Sandbox counterfactual `do(m)` necessity pruning to construct minimal tool-permission catalogs
- **Related Rules**:
  - [`output/rules/agent-human-interaction.md`](../../rules/agent-human-interaction.md) — `"DO: Design proposals for evaluability, not just acceptability"`, `"DO: Present structured, inspectable choices at approval gates"`, `"DON'T: Treat agent output as implicit authorization"`, and `"DON'T: Let a stored user approval outlive the context it was granted in"`
  - [`output/rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DON'T: Rely on structured LLM authorization decisions as the sole safety gate"` and `"DO: Verify both denied-effect suppression and bounded approval completion across decision, call, dispatch, and native-state witnesses"`
  - [`output/rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`

## Sources

- **Primary Paper**: *Structure-Aware Transformers for Hierarchical Authorization in Personal AI Agents* (`PATH`, `arXiv:2611.32018`, Praxis source `src:2611-32018v1`)
- **Real-Data Benchmark Referenced**: Wu et al. (`2026`), contextualized personal AI agent permission preferences (`ai-agent-permissions`, `201` participants, `8` domains, `65` scenarios, `447` permission nodes)
