---
name: feature
description: Plan a new feature as a spec, stop for the user's approval, then build it, gate it with the tej-core evaluator agent, and refresh the architecture docs. Use when the user asks to build, add or plan a feature, capability, integration or workflow in a repo set up with tej-core, or says "feature", "spec this", or "plan and build".
---

# Feature

Feature request: the user's message.

**Setup.** Read `.context/tej-core.json` (`repos` in scope, `never_touch` folders you must never
read or edit) and `.claude/rules/project-workflow.md` (this repo's suites, evals, contract doc,
in-flight audit and UI rules). If `.context/tej-core.json` is missing, say so in one line and
offer `/tej-core:init` first. Specs live in the `.context/2-specs/` of the repo this session runs
in.

## Phase 1: Understand (read-only)
1. Map every path the feature touches to its doc with the lookup table in `CLAUDE.md`. Read each
   `.context/1-docs/ARCH-*.md` in full, plus the contract doc `project-workflow.md` names when a
   cross-repo contract is involved.
2. Read the live code on every touched path in every repo in `repos`. Check the in-flight audit
   (`.context/2-specs/IN-FLIGHT-AUDIT.md`) for overlapping uncommitted or undeployed work.
3. Test the idea against "what if the user asks something I did not anticipate?": prefer one
   generic primitive (capability as data) over a hardcoded vertical codepath.

## Phase 2: Spec
4. If a `*_PLAN.md` for this work already exists at a repo root, THAT file is the deliverable:
   revise it in place with a Context section, add the template's sections, and point a short
   `SPEC-<slug>.md` stub (frontmatter plus acceptance boxes) at it. Otherwise copy
   `.context/2-specs/_TEMPLATE-feature.md` to `.context/2-specs/SPEC-<slug>.md` and fill every
   section: taxonomy with MUST NOT rows, ASCII block diagram, numbered data flow with exact paths,
   latency and storage read/write budget, FastFail or Resilient matrix per call, 2-3 traced
   non-obvious edge cases, cross-repo impact and deploy order, and the evals that apply.
5. A change to a latency-critical path states the user-perceived latency impact. If
   `architecture-invariants.md` forbids a regression there, stop and report instead of planning.
6. UI: if `project-workflow.md` asks for a mockup, build a clickable HTML mockup in the app's own
   tokens and put its link in the spec.
7. Review the spec for duplicated abstractions and over-engineering; fold findings in.
8. **STOP.** Present it the tej-core way: the plain first-person story first (the pain, how it
   works now, what you want to do, why it works), then the spec path, the diagram and the matrix.
   Wait for the user's explicit approval. No code before it. Set `status: approved` only then.

## Phase 3: Build (after approval)
9. Set `status: in_progress`. Implement surgically across the repos the spec names, the server
   side first when a contract moves. No formatters, no feature flags, no shims, no silent catches.
10. Failure-injection coverage: add the tests the spec lists only if the repo's test policy allows
    it in this conversation; otherwise inject failures by inspection (a throwaway script against
    the real object, a forced deadline) and record the output.
11. Run the existing suites for touched files and the evals `project-workflow.md` lists. Ask the
    user before anything long-running, paid or launching.
12. Invoke the `tej-core:evaluator` agent with the spec path and the recorded command output. Fix
    every required item and re-run it until it returns PASSED. Do not argue with a FAIL; satisfy
    it or show the user why the rule does not apply.
13. Tick the acceptance boxes that are truly met, update the ARCH docs, set `status: closing`,
    then run `/tej-core:compound`. Never commit or push without the user's word.
