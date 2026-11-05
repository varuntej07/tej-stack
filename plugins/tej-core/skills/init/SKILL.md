---
name: init
description: Set up the tej-core harness in the current repo by reading the code and writing a router CLAUDE.md, rules, living architecture docs, spec templates and the tej-core config, so every later session in this repo starts oriented and the feature, bugfix and evaluator loop works. Use when the user says "set up tej-core", "init", "install the harness here", or starts serious work in a repo that has no .context/tej-core.json. Merges with an existing CLAUDE.md and never overwrites without showing the diff.
---

# Init

Set up tej-core in the repo this session runs in. Read the code; never invent structure.

## 1. Look before writing (read-only)
1. Find the repo root (`git rev-parse --show-toplevel`, else the working directory). If
   `.context/tej-core.json` already exists, say the repo is already set up, offer to refresh the
   ARCH docs with `/tej-core:compound`, and stop.
2. Read what is there: `README*`, any existing `CLAUDE.md`, `AGENTS.md`, `.claude/`,
   `.cursorrules`, docs folders, package manifests (`package.json`, `pyproject.toml`,
   `Cargo.toml`, `go.mod`, `pubspec.yaml`, `pom.xml`, ...), CI workflows, test folders and the
   top two levels of source folders.
3. Group the source into subsystems: one per real boundary (an app, a service, a worker, a
   client, a shared package, a pipeline). Usually 2 to 8. For each, find its entry points and
   follow one real request or job end to end through the code so the ARCH doc is traced, not
   guessed.
4. Ask the user only what the code cannot tell you, in one batch: sibling repos that share
   contracts with this one, folders to never touch, which paths are live turns a person waits on
   (FastFail), and who runs builds and deploys.

## 2. Write the harness
Copy each template from this plugin's `templates/` folder and fill it from what you read. Leave
`<...>` markers only where you truly could not tell, and list those in the final reply.

| Write to | From template | Fill with |
|---|---|---|
| `CLAUDE.md` | [CLAUDE.md](../../templates/CLAUDE.md) | Product paragraph, canonical paths, the subsystem lookup table, the invariants you saw |
| `AGENTS.md` | [AGENTS.md](../../templates/AGENTS.md) | As is (Codex and other agents read it) |
| `.context/tej-core.json` | [tej-core.json](../../templates/tej-core.json) | `repos` (this one plus siblings, forward slashes), `never_touch`, the repo's real `source_extensions`, `fastfail_path_regex` built from the FastFail paths |
| `.claude/rules/project-workflow.md` | [project-workflow.md](../../templates/rules/project-workflow.md) | The real test commands from manifests and CI, evals, log and database locations, release targets |
| `.claude/rules/resilience-profiles.md` | [resilience-profiles.md](../../templates/rules/resilience-profiles.md) | FastFail and Resilient path globs (frontmatter `paths:` too) |
| `.claude/rules/architecture-invariants.md` | [architecture-invariants.md](../../templates/rules/architecture-invariants.md) | Defaults plus any invariant the code or docs already state |
| `.claude/rules/working-style.md` | [working-style.md](../../templates/rules/working-style.md) | Approvals, test policy, commit rules, shell |
| `.claude/rules/git-pr-release.md` | [git-pr-release.md](../../templates/rules/git-pr-release.md) | As is, plus any release gate the repo already documents |
| `.context/1-docs/ARCH-<subsystem>.md` | [_TEMPLATE-ARCH.md](../../templates/context/1-docs/_TEMPLATE-ARCH.md) | One per subsystem: the traced diagram, numbered flow with real file:line, budgets ("unmeasured" when unknown), resilience table, invariants |
| `.context/2-specs/_TEMPLATE-feature.md` | [_TEMPLATE-feature.md](../../templates/context/2-specs/_TEMPLATE-feature.md) | As is |
| `.context/2-specs/_TEMPLATE-bugfix.md` | [_TEMPLATE-bugfix.md](../../templates/context/2-specs/_TEMPLATE-bugfix.md) | As is |
| `.context/2-specs/IN-FLIGHT-AUDIT.md` | [IN-FLIGHT-AUDIT.md](../../templates/context/2-specs/IN-FLIGHT-AUDIT.md) | Current uncommitted work from `git status` |

Also create the empty folders `.context/3-log/` and `.context/4-scratchpad/` (each with a
`.gitkeep`), and add `.context/4-scratchpad/` to `.gitignore`.

Rules while writing:
- `tej-core.json` keeps every key and its whole value on one line; the hooks read it without a
  JSON parser. Escape backslashes in the regex as JSON requires (`\\.` for a literal dot).
- **Existing `CLAUDE.md` or `AGENTS.md`:** never overwrite. Keep every line the user wrote, add
  the missing router sections around it, show the merged diff, and wait for an OK before saving.
  Same for any existing file under `.claude/rules/`.
- When an existing doc line contradicts the code (a file it names is gone, a constant moved),
  keep the line as written, record the drift under Open in `IN-FLIGHT-AUDIT.md`, and name it in
  the report. Never silently rewrite what the user wrote.
- Carry the rules an existing `CLAUDE.md` or `AGENTS.md` already states into the matching
  `.claude/rules/` file, citing where each came from.
- Every file:line in an ARCH doc comes from a file you actually opened. If a section is a guess,
  say "inferred" in that line.

## 3. Report
Explain it the tej-core way: one short first-person paragraph on what you found and what you set
up, then the list of files written, each `<...>` you left for the user, and the next step: "run
`/tej-core:feature` or `/tej-core:bugfix` the next time you build or fix something here". Do not
commit; the user decides.
