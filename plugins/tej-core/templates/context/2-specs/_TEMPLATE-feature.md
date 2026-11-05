---
spec: SPEC-<slug>
status: draft            # draft | approved | in_progress | closing | done
owner_repos: [<repo>]    # keep only the touched ones
arch_docs: [ARCH-<subsystem>.md]
profile: Resilient       # or FastFail, per path
created: YYYY-MM-DD
---

# SPEC: <feature name>

## 0. The story and the class it belongs to
First person, out loud: the pain, how it works now, what you want to do, why it should work.
Then the class, not the instance:

| Shape | Example input | Wanted output | Fires? |
|---|---|---|---|
| core case | | | yes |
| near miss 1 | | unchanged behavior | MUST NOT |
| near miss 2 | | unchanged behavior | MUST NOT |

## 1. ASCII block diagram
```
[client] --transport--> [handler] --> [service] --> [store / provider]
```
Mark every new or changed box and edge with `*`.

## 2. End-to-end data flow
1. `<exact path:function>` ...

## 3. Latency and storage budget
| Stage | Budget ms | Measured or "unmeasured" | Reads | Writes | Cache |
|---|---|---|---|---|---|
User-perceived total before vs after: ___ ms vs ___ ms.

## 4. Resilience matrix
| Call | Profile | Timeout / first-byte deadline | Retries | Fallback chain | Cancellation | Failure copy |
|---|---|---|---|---|---|---|
| | FastFail | | 0 | | | |
| | Resilient | | 1-2, backoff + jitter, 429/5xx only | | | |

## 5. Non-obvious edge cases (2-3, traced with their read and latency cost)
1. ...

## 6. Cross-repo impact
- Contracts touched: ...
- Deploy order: ...
- What an older installed client does: ...

## 7. UI (if any)
- Clickable HTML mockup link: ...

## 8. Verification plan
- Existing suites and evals from `.claude/rules/project-workflow.md`: ...
- Test policy from `.claude/rules/working-style.md`: ...

## 9. Acceptance criteria
- [ ] Core case works, observed on the real surface (not inferred).
- [ ] Every MUST NOT row above verified unchanged.
- [ ] Latency budget met; numbers recorded in section 3.
- [ ] Resilience matrix implemented as written; no retry on a FastFail path.
- [ ] ARCH doc(s) updated; contract doc updated if a contract moved.
- [ ] `tej-core:evaluator` PASSED.
