---
spec: BUG-<slug>
status: draft            # draft | in_progress | closing | done
owner_repos: [<repo>]    # keep only the touched ones
arch_docs: [ARCH-<subsystem>.md]
profile: Resilient       # or FastFail
created: YYYY-MM-DD
---

# BUG: <one-line symptom as the user saw it>

## 0. Evidence (before any theory)
Where it was observed, with ids and timestamps, from the sources in
`.claude/rules/project-workflow.md`.

## 1. Taxonomy (the class, not the reported instance)
| Shape | Example | Today | Wanted | Fix must fire? |
|---|---|---|---|---|
| reported case | | broken | | yes |
| sibling case | | | | yes |
| near miss | | correct | unchanged | MUST NOT |

Sibling check across every repo in scope: does the same root cause live elsewhere? file:line each.

## 2. ASCII block diagram of the failing path
```
```
Mark the broken edge with `X`.

## 3. The story and the root cause
First person, out loud: what you saw break, how the path works, what went wrong, what you want
to do. Then file:line, why it fails, and why the obvious one-line fix would only cover the
reported shape.

## 4. Fix design
- No shims, no silent catches, no feature flags, no keyword lists over user text.
| Call | Profile | Timeout | Retries | Fallback | Cancellation |
|---|---|---|---|---|---|
- Latency and storage read/write impact: before ___ / after ___.

## 5. Reproduction
- Test policy allows it: the failing regression test, written FIRST, with its failing output.
- Otherwise: reproduce by inspection only. Record the exact command and output here.

## 6. Non-obvious edge cases (2-3)
1. ...

## 7. Cross-repo impact and deploy order
...

## 8. Acceptance criteria
- [ ] Root cause fixed for every "must fire" row; every MUST NOT row unchanged.
- [ ] Symptom observed gone on the real surface (or marked "unverified" with the reason).
- [ ] Existing suites for the touched files pass (record command and counts).
- [ ] ARCH doc updated if the fix changed a flow, budget or invariant.
- [ ] `tej-core:evaluator` PASSED.
