# Project workflow (read by every tej-core skill and the evaluator)

The tej-core skills are generic. Everything specific to this repo lives here, so the skills
never guess. Keep each section short; "none" is a valid answer.

## Evidence sources (bugfix step 1)
Where real behavior is recorded: log files, local databases, live stores, cloud log queries.
How to count (per user, per platform). Read-only access commands.

## Suites (feature step 11, bugfix step 6, evaluator check 9)
| Area | Fast command the evaluator may run | Baseline (known failures) |
|---|---|---|
| | | |

Slow, paid or user-run commands (the evaluator never runs these; it asks for recorded output):

## Evals
| Subsystem | Eval command | Paid? |
|---|---|---|

## Contract doc and in-flight audit
Contract doc for cross-repo shapes: `<path or none>`. In-flight audit:
`.context/2-specs/IN-FLIGHT-AUDIT.md`. Lessons-learnt file: `<path or none>`.

## UI rules (feature step 6)
Whether a clickable HTML mockup is required before approval, and the design tokens to use.

## Release (release skill)
Deploy targets and the command for each, version files that must agree, changelog rule,
known-issues file, release-only checks.

## Sync (compound step 5)
Shared harness files to keep identical across `repos`, and files that are per-repo.

## Evaluator: extra checks
One line per repo-specific check a reviewer could catch in a diff.
