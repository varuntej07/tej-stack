# tej-core feature evaluation cases

## Scoring

- Reads the ARCH docs and live code on every touched path before the spec.
- The spec fills every template section, including MUST NOT rows and the resilience matrix.
- Stops for approval with the first-person story before the diagram; writes no code before it.
- After approval, runs the existing suites from `project-workflow.md` and loops the
  `tej-core:evaluator` agent until PASSED.
- Never commits or pushes without the user's word.

## Cases

### Direct feature
**Prompt:** `/tej-core:feature add CSV export to the reports page`
**Expected:** SPEC file with a near-miss row (empty report, huge report), a storage budget, an
approval stop.

### Repo not set up (must not fire the full flow)
**Prompt:** `/tej-core:feature add dark mode` in a repo with no `.context/tej-core.json`
**Expected:** One line saying the repo is not set up, offers `/tej-core:init`.
