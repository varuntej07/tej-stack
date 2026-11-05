# tej-core compound evaluation cases

## Scoring

- Edits only harness files, never application source.
- Updates the ARCH docs the spec lists and removes statements the change made false.
- Turns each new failure mode into one rule line and, where a diff could show it, one evaluator
  line in `project-workflow.md`.
- Archives only specs with every box ticked; reports the unchecked box otherwise.
- Shows a diff summary before syncing shared files across repos.

## Cases

### Closing spec, all boxes ticked
**Prompt:** `/tej-core:compound`
**Expected:** ARCH doc updated, spec moved to `.context/3-log/` with `status: done` and `closed:`.

### Closing spec with an open box (must not archive)
**Prompt:** `/tej-core:compound .context/2-specs/SPEC-export.md`
**Expected:** Spec stays, status back to `in_progress`, names the open box.
