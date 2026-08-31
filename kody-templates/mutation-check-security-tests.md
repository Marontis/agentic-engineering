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
