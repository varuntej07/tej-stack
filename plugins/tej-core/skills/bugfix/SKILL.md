---
name: bugfix
description: Fix a bug at its root across every repo in scope, covering the whole class of the bug and the near-miss cases where the fix must not fire, explained to the user before any diff and gated by the tej-core evaluator agent. Use when the user reports a bug, a regression, wrong behavior or an error in a repo set up with tej-core, or says "bugfix" or "fix this properly".
---

# Bugfix

Bug report: the user's message.

**Setup.** Read `.context/tej-core.json` (`repos`, `never_touch`) and
`.claude/rules/project-workflow.md` (where this repo's evidence lives: logs, local databases,
live stores, cloud logs; its suites and evals). If `.context/tej-core.json` is missing, say so in
one line and offer `/tej-core:init` first.

1. **Evidence first.** Gather it from the sources `project-workflow.md` lists, counted the way it
   says (per user, per platform). Never conclude from source alone.
2. Read the subsystem's `.context/1-docs/ARCH-*.md` (lookup table in `CLAUDE.md`).
3. Copy `.context/2-specs/_TEMPLATE-bugfix.md` to `.context/2-specs/BUG-<slug>.md`. The reported
   example is a symptom, not the spec: enumerate the full taxonomy, including the near-miss cases
   where the fix MUST NOT fire, and check every repo in `repos` for the same root cause
   (file:line for each).
4. Reproduce:
   - Test policy allows new tests in this conversation: write the failing regression test FIRST
     and paste its failing output into the spec.
   - Otherwise (or when unsure): never write a test to diagnose. Reproduce by inspection (a
     throwaway script against the real object, log lines, the existing suite) and record it.
5. **STOP and explain before any diff.** Tell it the tej-core way: the plain first-person story
   (what you saw break, how the path works, what went wrong, what you want to do), then the
   symptom, the root cause with file:line, why it is wrong as a class, what should have been
   done, and the proposed fix with preserved and changed behavior. Wait for approval.
   Then fix the root cause for every "must fire" row. No shims, no feature flags, no keyword
   lists over user text, no silent catches, no retry on a FastFail path. If two reasonable fixes
   fail, stop and attack the premise instead of a third tweak.
6. Run the existing suites for touched files and any eval `project-workflow.md` lists. Ask the
   user before builds or launches; the user verifies GUI behavior.
7. Invoke the `tej-core:evaluator` agent with the BUG spec path and recorded output; loop until
   PASSED, then write the BUG spec path as the first line of
   `.context/4-scratchpad/.evaluator-passed`; any later edit needs a fresh PASS.
8. Say "fixed" only when the symptom was observed gone on the real surface; otherwise
   "unverified" and why. Add a lessons-learnt line where `project-workflow.md` keeps them, set
   `status: closing`, run `/tej-core:compound`.
