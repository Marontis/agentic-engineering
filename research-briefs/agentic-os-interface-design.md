# Agentic OS Interface Design: String and CrabOS

> **Papers**:
> - [String: An Agentic OS Where Every App Is a Markdown File](https://arxiv.org/abs/2608.28027)
> - [CrabOS: An Operating System for Human-AI Co-inhabitation](https://arxiv.org/abs/2608.28165)
> **Praxis sources**: `src:2608-28027v1`, `src:2608-28165v1`

## Why Not Skills? (for String)

String's procedures (SFMD rendering, partial view generation, hint extraction)
are tightly coupled to its specific runtime. The design principles are
valuable but the implementation procedures don't transfer to non-OS contexts.
CrabOS's kernel interface pattern DID produce a skill (`unified-capability-gateway`).

---

## Core Design Principles

### String OS — Four Principles

**P1: Partial Exposure** — The runtime, not the agent, conserves context.
Views are rendered incomplete on purpose. Everything held back stays
addressable. The agent sees only what it needs; the rest is retrievable
via follow-up commands.

**P2: Uniform Surface (Location Transparency)** — An SFMD page is the same
object whether it's an installed app, a local file, or a web page. The
agent drives all surfaces with the same two verbs (`command` and `next`),
never knowing which kind it's talking to.

**P3: Documents as Programs** — An app is a Markdown file. Installation is
copying. Authoring needs no toolchain. Format errors are program bugs and
must be loud.

**P4: Recursive Rendering** — Action output is re-rendered as SFMD, so
results carry the same affordances as pages. The interface composes with
itself.

### CrabOS — Three Principles

**C1: Text Objects as State** — All system state is persisted as natural-
language-readable text objects. No database APIs needed — capabilities emerge
from addressable objects.

**C2: Shared Work Objects** — Humans and AI directly manipulate the same set
of referable work objects. No separate tool-packaging layer for AI.

**C3: Unified Auditable Entry** — Every executor invokes system capabilities
through the same kernel interface (see `unified-capability-gateway` skill).

---

## Comparison

| Dimension | String | CrabOS |
|:----------|:-------|:-------|
| App format | Markdown file | Electron iframe |
| Agent interface | Two verbs (command + next) | Kernel Interface (5-stage pipeline) |
| State model | Rendered views | L0 text objects |
| Trust model | Content-type-based shell restrictions | Subject binding + policy enforcement |
| Composability | Recursive rendering | Object primitives |
| Memory | Implicit in view history | Explicit Memory objects in L0 |

---

## Relevance to Praxis

- **Partial exposure** (P1) is relevant to skill loading — show skill
  descriptions first, load full body on request (progressive disclosure)
- **Uniform surface** (P2) validates our existing design where skills,
  rules, and specs all use the same Markdown format
- **Text objects as state** (C1) validates Praxis's skill graph as
  structured text — queryable, diffable, version-controllable
- **Shared work objects** (C2) is the design goal for MCP server integration
  where multiple agents read from the same Praxis graph
