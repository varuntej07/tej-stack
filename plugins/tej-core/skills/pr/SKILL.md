---
name: pr
description: Gate the current branch with the tej-core evaluator agent and a duplication review, check commit hygiene, and draft a pull request description to the scratchpad without pushing. Use when the user asks to prepare, draft or check a PR in a repo set up with tej-core, or says "pr" or "ready to open a PR".
---

# PR

Base branch: the one the user names (default `main`).

Never push, open, or comment on a PR yourself; drafting only. The user pushes.

1. `git status --short` and `git log --format='%h %s%n%b' <base>..HEAD` in the repo this session
   runs in, and `git status --short` in every other repo in `.context/tej-core.json` `repos`, to
   catch a cross-repo half that is not committed.
2. Commit hygiene: check every commit message in the range against the commit rules in
   `.claude/rules/` (by default: zero AI trailers such as `Co-Authored-By`, `Claude-Session`,
   "Generated with"). List violations; never rewrite history without the user.
3. Invoke the `tej-core:evaluator` agent on the range (pass the spec path from
   `.context/2-specs/` if one exists) and review the changed files for duplicated or premature
   abstractions. Any REJECTED item blocks the draft: report it and stop.
4. Draft `.context/4-scratchpad/PR-<branch>.md` following the PR template in
   `.claude/rules/git-pr-release.md`: summary and taxonomy, ASCII data-flow diff (before and
   after), latency and storage budget and resilience matrix, cross-repo contract sync with deploy
   order, and test and eval evidence pasted from real runs ("unverified" where none exists). No
   attribution footer unless the repo rules ask for one.
5. Reply with the draft path, the evaluator verdict, and the exact commands the user would run to
   push and open the PR, in the shell `working-style.md` names.
