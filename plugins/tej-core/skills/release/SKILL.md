---
name: release
description: Production release preflight across every repo in scope that inspects working trees, undeployed changes, tests, evals, versions and changelogs, prints a pass or fail scorecard, and asks before any build, tag, push or deploy. Use when the user asks to release, ship, cut a version, deploy, or check whether something is ready to go out, in a repo set up with tej-core.
---

# Release

Release target: what the user names (default: everything in scope).

This skill only inspects and reports until the user says go. Read
`.claude/rules/git-pr-release.md` (gates and release flows) and the release section of
`.claude/rules/project-workflow.md` (targets, version files, deploy commands, known-issues file)
first.

**a) Working trees.** `git status --short` and `git log origin/main..HEAD --oneline` in every
repo in `.context/tej-core.json` `repos`. Flag every uncommitted or unpushed file.

**b) Pushed but undeployed.** Read the known-issues file and the in-flight audit
(`.context/2-specs/IN-FLIGHT-AUDIT.md`), newest entries first, and raise open ones before anything
else. Classify each change since the last deploy by the deploy target it needs, per
`project-workflow.md`. Ask the user before querying any live system to see what is actually
serving; never guess what is live.

**c) Tests and evals for modified subsystems.** Map changed paths to subsystems (the `CLAUDE.md`
lookup table). For each, the existing suite subset and the evals `project-workflow.md` lists.
Paid or long evals: list them and ask; do not start them.

**d) Version and changelog.** Every version file the release section names agrees, the changelog
has the entry the repo requires, and any release-only checks listed there pass.

**e) Scorecard.** Print one table: gate, repo, status (PASS / FAIL / NEEDS USER), evidence. Then
list the exact commands for each outward step (build, commit, tag, push, deploy) in deploy order
(server first, then workers, then clients, unless the rules say otherwise) and ASK the user
before running any of them.
