# tej-core init evaluation cases

## Scoring

- Reads manifests, CI and source before writing; every ARCH file:line points at a file it opened.
- Writes every file in the init table, with `tej-core.json` keys one per line.
- Never overwrites an existing `CLAUDE.md`, `AGENTS.md` or rule file; shows the merge and waits.
- Asks only what the code cannot answer, in one batch.
- Reports in the tej-core voice (first-person paragraph first) and lists every `<...>` left.
- Does not commit.

## Cases

### Fresh repo
**Prompt:** `set up tej-core here` (a small web app with no CLAUDE.md)
**Expected:** 2 to 4 ARCH docs traced from real entry points, real test commands in
`project-workflow.md`, `.context/4-scratchpad/` gitignored.

### Existing CLAUDE.md
**Prompt:** `/tej-core:init` (repo with a hand-written CLAUDE.md)
**Expected:** Keeps every existing line, adds the router sections, shows the diff, waits for OK.

### Already initialized (must not fire)
**Prompt:** `init tej-core` (repo already has `.context/tej-core.json`)
**Expected:** Says it is set up, offers `/tej-core:compound`, writes nothing.
