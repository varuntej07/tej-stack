# Git, PR and release rules

## Commits

1. Run `git status` in every repo in `.context/tej-core.json` `repos` first. A change to a
   cross-repo contract is one commit per repo; name the others. Never stage a file you did not
   change in this task.
2. Never commit, push, tag or deploy unless the user asked in the current message.
3. No AI attribution trailers unless the user's rules ask for them.

## PR description template

```markdown
## 1. Summary & problem taxonomy
What changed and why. The taxonomy table: each shape, an example, wanted output, including the
near-miss shapes where the change must NOT fire.

## 2. ASCII block diagram & data-flow diff
Before and after diagrams of the touched path, with the changed edge marked.

## 3. Latency / storage budget & resilience profile
Per-stage ms budget before and after; database and storage reads and writes per request.
Profile: FastFail or Resilient, with timeouts, fallback chain and cancellation.

## 4. Cross-repo contract sync
Which contract moved, the contract doc section touched, deploy order, what an older client does.

## 5. Test & eval evidence
Exact commands and their output. Say "unverified" where it is.
```

## Release gates

Before any release or deploy: read the known-issues file and
`.context/2-specs/IN-FLIGHT-AUDIT.md` from the newest entry back and raise every open item that
touches the release. Per-target steps live in `project-workflow.md` under Release.
