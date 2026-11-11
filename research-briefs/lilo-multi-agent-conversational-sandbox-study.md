# Lilo: A Multi-Agent Conversational Sandbox for Children's Digital Communication

> **Source**: [arXiv:2611.14260](https://arxiv.org/abs/2611.14260) — Ofri Elbaum, Amit Malik, Tomer Malkevich, Zohar Elyoseph, Adir Solomon, Rotem Dror, Oshrat Ayalon (2026)
> **Praxis Source ID**: `src:2611-14260v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper presents an exploratory, single-session uncontrolled user study ($N = 28$ Israeli children aged `9–11`, `M = 9.9`) evaluating **Lilo**, a Hebrew WhatsApp-style multi-agent role-play sandbox for practicing responses to mild online peer conflict and exclusion. Per [`AGENTS.md`](../AGENTS.md), domain-specific child-HCI educational interventions with small uncontrolled pre–post self-report samples do not yield general-purpose software-engineering skills or universal quantitative guardrails. However, the system's **five-agent orchestration architecture**—specifically its **asymmetric context visibility**, **non-escalating safety interception**, **sequential intra-turn peer conditioning**, and **boundary between practice sandboxes and live real-conflict advisors**—provides clean architectural patterns for multi-persona simulation and pedagogical/training sandboxes alongside [`scaffolding-mas-clinical-training`](./scaffolding-mas-clinical-training.md).

---

## System Architecture: Five Coordinated `Claude 3.7 Sonnet` Agents in One Group Chat

`Lilo` embeds a child participant inside a simulated school WhatsApp group alongside two peer personas (`Sagi`, `Reut`) and an in-thread reflective coach (`Lilo`), coordinated behind the scenes by a hidden `Orchestrator Agent` and a post-session `Feedback Agent`:

1. **`Orchestrator Agent` (Hidden Turn Router, Difficulty Controller & Safety Interceptor)**:
   - **Dynamic Difficulty De-Escalation (`4` levels)**: Starts peer friction at `Intense` and steps down through `Hard -> Medium -> Low` only after observing **`2–3` consecutive constructive responses** from the child, ensuring social resolution is earned rather than automatic.
   - **`Stop–Think–Act` Traffic-Light Routing (`Red / Yellow / Green / None`)**: Classifies each child turn to govern whether and how the mentor `Lilo` intervenes—`Red` (impulsive/insulting escalation -> pause and reframe), `Yellow` (hesitant/avoidant or partial attempt -> Socratic nudge), `Green` (empathetic/constructive boundary-setting -> brief reinforcement), or `None` (stay silent so peer dialogue flows naturally).
   - **Real-Time Safety Interception**: Flags severe profanity, self-harm cues, or abusive outbursts *before* peer agents process the turn.
2. **Peer Agents (`Sagi` — stubborn/blunt instigator; `Reut` — sensitive/ambivalent bystander-target)**:
   - Conditioned on current orchestrator difficulty level (`Intense`..`Low`) and colloquial pre-adolescent Hebrew register constraints.
   - **Sequential Intra-Turn Conditioning**: When both peers speak following a child message, the second peer agent receives the first peer's newly generated reply before responding, preventing contradictory or redundant parallel reactions.
   - **Silence Auto-Trigger (`60` seconds)**: If the child remains inactive for `60` seconds, the orchestrator triggers `1` naturalistic peer-to-peer exchange to keep the social scene alive without pressuring the user directly (`4` auto-triggers observed across `265` difficulty-labeled turns).
3. **Mentor Agent (`Lilo` — in-chat reflective coach)**:
   - Capped at **`<= 60` words** per turn; uses Socratic prompts and perspective-taking cues rather than scripting exact replies for the child to copy.
4. **Asymmetric Context Filtering (Core Sandbox Invariant)**:
   - **Mentor Invisibility to Peers**: `Sagi` and `Reut` **never see `Lilo`'s coaching messages** in their context windows, keeping the simulated social conflict diegetic even though `Lilo` appears inline in the child's group-chat UI.
   - **Quarantined Abusive Turns**: When the safety interceptor flags an offensive/abusive message from the child, the UI marks the bubble with a red warning background, **withholds the message from `Sagi` and `Reut`** (so simulated peers never reciprocate abuse or spiral), routes directly to a `Lilo` `Red` coaching intervention, and **retains the blocked turn in the full audit log** for the post-session `Feedback Agent` and adult facilitators.

---

## Key Empirical Findings ($N = 28$ Children Aged `9–11`)

Across `N = 28` participants (`17` girls [`61%`], `11` boys [`39%`], mean age `9.9`), technical/completion filtering yielded `n = 26` complete interaction logs, `n = 26` paired pre–post surveys (`24` overlapping both), and `17/28` semi-structured exit interviews coded to thematic saturation (`68.6%` raw inter-coder agreement, Cohen's $\kappa = .63$):

### 1. Session Engagement & Traffic-Light Telemetry (`n = 26` Logs)
- **Session Duration & Volume**: Mean session duration was **`17.8` minutes** (median `16.8`, max `31.4`), generating **`936` total messages** across sessions: `261` child messages (`28%`; mean `10.0`, median `9` per child), `270` `Sagi` (`29%`), `224` `Reut` (`24%`), and `181` `Lilo` (`19%`).
- **Difficulty Progression & Early Friction**: Across `265` difficulty-labeled turns (`85` `Intense`, `52` `Hard`, `81` `Medium`, `47` `Low`) and `181` traffic-light mentor turns (`83` `Green` [`46%`], `71` `Yellow` [`39%`], `27` `Red` [`15%`]), **`20/27` (`74%`) of all `Red` impulsive/escalatory turns occurred at the initial `Intense` difficulty stage**, confirming that friction concentrates at initial provocation before mentor scaffolding takes hold.

### 2. Pre–Post Self-Efficacy Gains vs. Flat Harm-Recognition Scores (`n = 26` Surveys, 1–7 Likert)

| Measure (1–7 Likert, Wilcoxon Signed-Rank) | Pre Mean (`SD`) | Post Mean (`SD`) | Statistic (`W`, `p`) | Interpretation |
|:---|:---:|:---:|:---:|:---|
| **Personal Coping Self-Efficacy** (*knowing how to respond when targeted*) | `4.85` (`1.57`) | **`5.77` (`1.18`)** | **`W = 11.0`, `p = .001`** | Significant gain (`+0.92`) in perceived ability to handle direct friction |
| **Bystander Response Self-Efficacy** (*knowing how to intervene for a peer*) | `4.58` (`1.53`) | **`5.38` (`1.47`)** | **`W = 9.0`, `p = .006`** | Significant gain (`+0.80`) in perceived ability to support excluded peers |
| **Identifying Unpleasant Behavior** (*recognizing when chat crosses a line*) | `2.50` (`1.39`) | `2.23` (`1.50`) | `W = 49.0`, `p = .314` (NS) | No significant shift—children already recognized overt rudeness; the bottleneck was **action repertoire**, not detection |

Post-session acceptability ratings (`1–7`) were high for perceived helpfulness to other children (`M = 6.54`, `SD = 0.76`), desire to use again (`6.46`, `0.81`), recommending to friends (`6.38`, `0.90`), and classroom integration (`6.38`, `1.10`), while **end-of-session summary feedback scored lowest (`M = 5.38`, `SD = 1.30`)** compared to in-the-moment `Lilo` coaching.

### 3. Bidirectional Realism Failures & The Sandbox-vs.-Live-Advisor Boundary (`17` Interviews)
- **Persona Credibility Breaks in Both Directions**: Children flagged realism breaches along three axes—**linguistic register** (overly formal/textbook phrasing or punctuation), **persona consistency** (`Sagi` softening too abruptly once the difficulty counter stepped down), and **social conduct** (peers being either too harsh *or* unnaturally polite/apologetic for `9–11`-year-olds).
- **Safe Practice Sandbox $\neq$ Live Conflict Copilot**: Participants valued `Lilo` specifically because no real peer's feelings or school reputation were at stake (`"safe place to try things out"`), and authors warn strongly against porting an automated coach directly into **live children's messaging threads**, where real-time AI mediation risks surveillance harm, social stigma, over-reliance, and uncalibrated advice in genuinely high-risk bullying situations.

---

## Transferable Design Patterns for Multi-Agent Training Sandboxes

1. **Partition context windows asymmetrically between role-play actors and coaching agents**: Hide mentor/evaluator turns and safety-quarantined user outbursts from simulated peer personas so the scene never breaks character or escalates toxicity, while preserving every raw turn in the audit/debrief stream.
2. **Condition multi-persona replies sequentially within a single user turn**: When multiple simulated participants react to one user message, pass Agent 1's generated reply into Agent 2's prompt before decoding to prevent repetitive pile-ons or mutually inconsistent reactions.
3. **Deliver coaching inline at high-friction turns rather than deferring to post-session summaries**: `74%` (`20/27`) of `Red` escalations happened during initial `Intense` provocation, and inline `<= 60`-word Socratic nudges were rated substantially higher than post-session `Feedback Agent` reports (`5.38/7`).

---

## Related Artifacts

- **Rules**:
  - [`agent-human-interaction.md`](../rules/agent-human-interaction.md) — Progressive disclosure, response granularity adaptation, and human-in-the-loop boundaries
  - [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md) — Context scoping and orchestrator-mediated multi-agent state isolation
- **Research Briefs**:
  - [`scaffolding-mas-clinical-training`](./scaffolding-mas-clinical-training.md) — Multi-agent role-play and mentor scaffolding for clinical interview training
  - [`how-a-chatbots-response-style-shapes-a-classr`](./how-a-chatbots-response-style-shapes-a-classr.md) — Multi-agent simulation of conversational response-style effects in educational settings
