---
name: mutation-check-security-tests
description: Enforces that security tests are mutation-checked to ensure they actually fail when the control is disabled.
author: attorn-retrospective
severity: error
enabled: false
tags: [security, testing, attestation]
---

# Mutation Check Security Tests

A mutation check that passes means the test is wrong, not that the code is safe. 
Security tests must be explicitly mutation-checked (e.g., disabling the control to confirm the test fails) before they are trusted.

This rule enforces the verification layer from Attestation-Driven Development (ADD). A test named for a property it cannot verify is worse than none because it converts "unverified" into "verified".

## Instructions

1. Identify when a new security-critical test is added or modified.
2. Check if the PR description or test comments indicate that the test was mutation-checked (i.e., the developer verified the test fails if the security control is removed).
3. If there is no evidence of a mutation check, prompt the developer to verify the test against its own mutation.
4. Ensure test doubles reproduce the relevant behavior (context-awareness, timing) of the real implementation so mutation checks are accurate.

## Bad Example

```go
func TestAuthzControl(t *testing.T) {
    // Adds test, but race window is smaller than goroutine start-up.
    // The test always passes, even if the Authz control is deleted!
    result := checkAuthz("user", "resource")
    assert.True(t, result.Allowed)
}
```
*(Fails: The reviewer should ask "Did you confirm this test fails if `checkAuthz` is hardcoded to return true?")*

## Good Example

```go
func TestAuthzControl(t *testing.T) {
    // MUTATION CHECKED: Verified that test fails when policy evaluator is bypassed.
    result := checkAuthz("user", "resource")
    assert.True(t, result.Allowed)
}
```
*(Passes: The developer has explicitly attested to mutation checking the test.)*

## When mutation is not applicable

Not every load-bearing property is expressible as a single-process source
mutation. Two classes recur:

- **Concurrency invariants** — e.g. "concurrent writers serialize; no update is
  lost." The guarantee emerges from a lock serializing threads, not from any one
  function body; the mutants a scoped run leaves alive are orchestration glue an
  outcome assertion cannot see.
- **Isolation invariants** — e.g. "the sandbox guest has no network interface"
  or "each run restores pristine state." The property is an *absent* config line
  or an emergent boundary; there is nothing in a function to mutate.

For these, do **two** things — never just one:

1. **Do not fake a mutation pass.** Labeling an unmutatable property "verified"
   (via a `construction`/skip stamp) converts an unproven invariant into false
   assurance — the exact failure this rule exists to stop.
2. **Do not silently drop it either.** Discharge it on a *behavioral basis*: run
   the bound test as a baseline (pass = discharged), record a written rationale
   for why mutation does not apply, and **count it separately** from
   mutation-verified claims. Same name, different *kind* of assurance — say which.

> Origin: attorn-retrospective — concurrency and microVM-isolation claims that no
> function-scope mutation could indict, discharged behaviorally and counted apart
> rather than mislabeled as verified.
