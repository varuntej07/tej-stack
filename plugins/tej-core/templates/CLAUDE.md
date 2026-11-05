# <Project name> (router)

<One paragraph: what this product is, who uses it, and the one thing every description of it
must lead with.> This file only routes; detail lives in `.claude/rules/` and `.context/1-docs/`.

## Canonical paths

| Repo | Path | Remote |
|---|---|---|
| <this repo> | `<absolute path>` | `<owner/repo>` |

Never read, edit or cite: <stale clones, decoys; also listed in `.context/tej-core.json`>.

## STOP: Before planning or editing any file, read its ARCH doc

All under `.context/1-docs/`. Subsystem lookup:

| Paths | Read first |
|---|---|
| `<src/area/>` | `ARCH-<subsystem>.md` |

Always-on rules: `.claude/rules/` (`architecture-invariants.md` holds the hard constraints;
`project-workflow.md` holds this repo's suites, evals, evidence sources and release steps).

## Core micro-invariants

- **Done means the symptom is observed gone** on the real surface; otherwise say "unverified".
- **Trace the path, never trust a comment.** Empty results and healthy must never look identical.
- **Failures keep their cause.** Every error the user sees says why.
- <The two or three invariants this codebase has been burned by.>

## Working style

- Explanations open as a first-person, out-loud cofounder story (pain, how it works now, the
  idea, why it works), then every required section below in full.
- Plans: ASCII block diagrams, data flow, latency and storage read/write budgets, 2-3
  non-obvious traced edge cases, the FastFail or Resilient matrix.
- <Who runs builds and deploys; what needs approval; commit message rules.>

## tej-core skills

| Skill | Does |
|---|---|
| `/tej-core:feature` | ARCH read, `SPEC-<slug>.md`, approval stop, build, evaluator loop, compound |
| `/tej-core:bugfix` | Taxonomy incl. must-not-fire cases, explain first, root-cause fix, evaluator, compound |
| `/tej-core:search` | Read-only call graph + latency/resilience audit to `.context/4-scratchpad/` |
| `/tej-core:pr` | Evaluator + duplication review, commit hygiene, PR draft to scratchpad |
| `/tej-core:release` | Multi-repo preflight scorecard; asks before any build, tag, push or deploy |
| `/tej-core:compound` | Updates ARCH docs, rules, in-flight audit, archives specs |
