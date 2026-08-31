---
name: browser-agent-http-sandbox
description: >
  Patterns for sandboxing browser-using AI agents (BUAs) at the HTTP layer
  rather than the UI layer. Derived from ceLLMate (arXiv:2512.12594).
  Covers agent sitemaps, policy selection/instantiation, HTTP interception,
  ambient authority restriction, and prompt injection defense.
source: https://arxiv.org/pdf/2512.12594
---

# Browser Agent HTTP Sandbox

Skill for building security frameworks around browser-using AI agents (BUAs)
that interact with websites through clicks, scrolling, typing, and navigation.

## Core Problem

BUAs operate via low-level UI primitives (`click(x, y)`, `type()`, `scroll()`).
Writing security policies at the UI level is fundamentally broken because of the
**semantic gap**: the same `click(246, 1023)` can mean "add to cart" or "transfer
funds" depending on page state, resolution, and DOM structure. You cannot
enumerate all action sequences that reach a dangerous browser state.

## Key Insight

All side-effecting UI operations ultimately produce **HTTP requests** to the
website backend. HTTP requests are semantically meaningful — `POST
/checkout/place-order` has an unambiguous meaning regardless of how the user/agent
arrived there. Sandboxing at the HTTP layer bridges the semantic gap.

## Architecture: Three-Phase Workflow

```
┌──────────────────────────────────────────────────────────┐
│ Phase 1: REGISTRATION (developer-time)                   │
│                                                          │
│   Web Developer publishes:                               │
│   ├── Agent Sitemap (HTTP endpoint → semantic action)    │
│   └── Policy Library (allow / deny / condition rules)    │
│                                                          │
│   Hosted at well-known URL on the domain (like robots.txt)│
└──────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│ Phase 2: POLICY INSTANTIATION (per-task, at runtime)     │
│                                                          │
│   Given user prompt → LLM predicts:                      │
│   ├── Target domains (e.g., amazon.com, gmail.com)       │
│   └── Least-privilege policy subset per domain           │
│                                                          │
│   User confirms via consent dialog → policies freeze     │
└──────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│ Phase 3: POLICY ENFORCEMENT (continuous, per-request)    │
│                                                          │
│   Every outbound HTTP request is intercepted:            │
│   ├── Matched against fast authorization lookup table    │
│   ├── Allow (read-only / in-scope)                       │
│   ├── Deny (out-of-scope / exfiltration)                 │
│   └── Condition (evaluate JS function with runtime args) │
│                                                          │
│   Unmatched domains → default-deny                       │
└──────────────────────────────────────────────────────────┘
```

## Agent Sitemap

The agent sitemap is the paper's most distinctive contribution. It is a
machine-readable JSON document that maps HTTP endpoints to semantic actions.
Website developers publish it at a well-known URL, analogous to `robots.txt`
or Content Security Policy headers.

### Sitemap Entry Structure

```json
{
  "semantic_action": "PlaceOrder",
  "description": "Submit the final purchase request to complete the transaction",
  "url": "https://www.amazon.com/checkout/p/*/spc/place-order*",
  "method": "POST",
  "body": {},
  "args": {
    "totalAmount": {
      "type": "number",
      "source": {
        "type": "dom",
        "url": "https://www.amazon.com/checkout/p/*",
        "selector": "#subtotals-marketplace-table li:nth-child(4) .order-summary-line-definition"
      }
    }
  }
}
```

Key properties:
- **Matching data**: HTTP method + URL pattern to identify the request
- **Semantic data**: unique `semantic_action` name + natural language `description`
- **Args**: security-relevant parameters and how to extract them at runtime
  (from request body or DOM via CSS selectors)
- **DOM stability**: use `sitemap-id` attributes for refactoring-resilient
  selectors: `<span sitemap-id="cart-total">` → `[sitemap-id="cart-total"]`

### Sitemap Construction

For frameworks with route definitions (Rails, Django, Express), the route table
provides a natural foundation: each route specifies the HTTP endpoint, and the
controller/handler defines the semantic meaning. A GitLab sitemap was built from
51 Rails project API routes.

## Policy Specification

Policies define constraints over semantic actions from the sitemap.

### Policy Types

| Effect | Behavior | Example |
|:-------|:---------|:--------|
| `allow` | Unconditionally permit the action | `view_shopping_cart` |
| `deny` | Unconditionally block the action | `delete_account` |
| `condition` | Evaluate a JavaScript function at runtime | `purchase_amount_leq` |

### Conditional Policy Example

```json
{
  "name": "purchase_amount_leq",
  "effect": "condition",
  "actions": ["PlaceOrder"],
  "condition": {
    "name": "allowPurchaseIfAmountLeq",
    "parameters": {
      "maxAmount": { "type": "number", "description": "Maximum allowed purchase amount." }
    },
    "args": ["totalAmount"]
  },
  "description": "Allow purchase if total amount is ≤ ${maxAmount}."
}
```

```javascript
export default function allowPurchaseIfAmountLeq(params, args) {
  const { maxAmount } = params;
  const { totalAmount } = args;
  if (typeof totalAmount !== "number" || typeof maxAmount !== "number") {
    return false;  // fail closed
  }
  return totalAmount <= maxAmount;
}
```

### Composite Policy (per-session output)

```json
{
  "domain": "amazon.com",
  "selected_policies": {
    "view_shopping_cart": {},
    "purchase_amount_leq": { "maxAmount": 50 }
  },
  "allowed_domains": [
    "m.media-amazon.com",
    "images-na.ssl-images-amazon.com",
    "*.amazon-adsystem.com"
  ]
}
```

## Policy Selection via LLM

The policy selector operates only on **trusted context** (user prompt +
pre-defined policies) — never on untrusted page content. This makes it immune
to prompt injection by design.

Two-step process:
1. **Domain prediction**: given user prompt, predict target domains
2. **Policy selection**: per domain, select minimal sufficient policy subset

### Benchmark Results (from paper)

| Model | Retail (149 tasks) | Travel (36) | Version Control (24) |
|:------|:-------------------|:------------|:---------------------|
| claude-opus-4-5 | 99.32% | 100% | 95.83% |
| gemini-2.5-pro | 97.32% | 97.22% | 100% |
| gpt-5.1 | 96.64% | 94.44% | 95.83% |

Common failure modes:
- **Object confusion**: mistaking a wishlist for a shopping cart
- **Over-permissiveness**: selecting extra policies beyond what's needed
- **Over-restrictiveness**: omitting required policies for multi-step tasks

## HTTP Interception Implementation

In Chromium, three interception layers exist:

| Layer | Mechanism | Tradeoff |
|:------|:----------|:---------|
| OS/Network | Host firewall, proxy, VPN filtering | Authoritative but coarse-grained |
| Browser core | Chromium source modification | Strongest mediation, hardest to deploy |
| Browser extension | Chrome `webRequest` / CDP `Fetch.requestPaused` | Deployable, rich visibility, requires no malicious co-extensions |

The prototype uses a Chrome extension. The fast authorization lookup table
compiles policies into per-request allow/deny/function decisions at session start.

### Performance

- **Memory overhead**: ~11 MB per session
- **Latency overhead**: 7.25–15% per HTTP request
- **Blocked all prompt injection attacks** in the WASP benchmark

## Stateful Policies

Support "allow PlaceOrder **once**" by tracking request counters via Chrome
extension local storage. Without statefulness, an agent could exploit the
`$50 limit` by placing two `$49` orders.

## Freshness Guarantees

Conditional policies can evaluate stale DOM values if the agent acts faster than
the page updates (e.g., changing cart quantity before the total refreshes). The
framework enforces sequential action execution and throttles rapid state-changing
instructions to ensure argument freshness.

## Threat Model

- **Attacker**: controls untrusted portions of trusted domains (GitHub issue
  titles, Amazon product reviews) — not the domain itself
- **Attack vectors**: prompt injection (optimization-based and optimization-free),
  TOCTOU attacks, branch steering, cross-domain redirects
- **Defense**: default-deny on unmatched domains; permission level freezes after
  user confirmation; never interprets UI state for security decisions

## When to Use This Skill

- Building or hardening a browser automation agent (Playwright, Puppeteer, CDP)
- Designing policy/permission systems for agentic web interactions
- Implementing HTTP-layer guardrails for any agent that touches the web
- Creating agent sitemap specifications for your web application
- Defending against prompt injection in browser agents

## References

- **Paper**: [ceLLMate: Sandboxing Browser AI Agents](https://arxiv.org/abs/2512.12594) — Meng, Feng, Shumailov, Fernandes (UC San Diego)
- **Code**: https://cellmate-sandbox.github.io
- **Praxis source**: `src:cellmate-sandboxing-browser-ai-agents`
