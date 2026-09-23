# {NAME}: Roadmap

> One milestone at a time. Each ends with its checks passing and a human checkpoint.
> Status: [ ] not started · [~] in progress · [x] done

## M0: Walking skeleton [ ]
Goal: tooling and pipeline green, no features.
- [ ] `{install}` succeeds from a clean clone
- [ ] `{test}` runs (one smoke test); `{typecheck}`, `{lint}`, `{build}` pass
- [ ] CI runs the above on every push/PR
- [ ] {Data seam: `{Repository}` interface + mock adapter returning typed fixtures}
- [ ] App shell, theme tokens, fonts, custom 404
- [ ] README: what it is, how to run it

Out of scope: any domain logic or feature UI.

## M1: Domain core [ ]
Goal: every rule in the spec as pure functions with tests, before any feature UI.
- [ ] Tests written first and seen failing, then passing: {R-… list}
- [ ] Each boundary case tested from both sides
- [ ] Trap data present and covered by a test
- [ ] README: short explanation of the trickiest rules

Out of scope: UI beyond what's needed to exercise the rules.

## M{n}: {User-visible slice} [ ]
Goal: {one sentence a user would recognise}.
Rules: {R-… IDs}
- [ ] {Pass/fail check, e.g. "Filters survive refresh and browser back"}
- [ ] {Empty/error state check}
- [ ] {Accessibility/responsive check specific to this slice}

Out of scope: {what's tempting but belongs to a later milestone}.

## Later
- {Surfaces and ideas not in v1, one line each with why they were deferred}

## Changelog
- {date}: Roadmap created by grill-spec.
