---
name: compound
description: Self-healing harness update after a tej-core feature or bugfix that refreshes the architecture docs, turns new failure modes into rules and evaluator checks, updates the in-flight audit, archives finished specs and syncs shared harness files across repos. Use after a spec reaches status closing, or when the user says "compound" or "update the docs and rules".
---

# Compound

Spec: the one the user names (default: every spec in `.context/2-specs/` with `status: closing`).

Edit only harness files (`.context/`, `.claude/rules/`), never application source.

1. **ARCH docs.** For each spec, update the `.context/1-docs/ARCH-*.md` it lists: block diagram,
   numbered flow, budget table (measured numbers replace "unmeasured"), resilience section and
   invariants. Remove statements the change made false. Keep the five-section structure.
2. **New failure modes.** Any edge case or failure the work uncovered becomes one rule line in the
   right `.claude/rules/*.md`, and, if a reviewer could catch it in a diff, one line in the
   evaluator section of `.claude/rules/project-workflow.md`. One line each, no essays.
3. **In-flight audit.** Update `.context/2-specs/IN-FLIGHT-AUDIT.md` (shipped, uncommitted,
   pushed but undeployed, open, with dates).
4. **Archive.** A spec whose acceptance boxes are all ticked moves to `.context/3-log/` with
   `status: done` and a `closed: YYYY-MM-DD` line. A spec with an unchecked box stays, status back
   to `in_progress`, and you report which box.
5. **Sync repos.** When `.context/tej-core.json` lists more than one repo, compare the shared
   harness files `project-workflow.md` names (by default `.context/1-docs/`, the spec templates,
   `IN-FLIGHT-AUDIT.md`, `resilience-profiles.md`, `git-pr-release.md`) across them with `cmp`.
   When they differ, take the copy edited in this session (or the newer mtime), show the user the
   diff summary, and copy it over. Never sync `3-log/`, `4-scratchpad/`, `settings.local.json`,
   or the repo-specific `CLAUDE.md` and rules the file marks as per-repo.
6. **Memory hygiene.** If `forbid_project_memory` is true, list this project's memory folder under
   `~/.claude/projects/`. It should hold only a short `MEMORY.md` pointer to the in-repo harness.
   Report any other file and propose where its content belongs; move it only with the user's OK.
7. Reply with a short list: docs updated, rules added, specs archived, files synced, memory
   findings.
