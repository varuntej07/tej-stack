# tej-core bugfix evaluation cases

## Scoring

- Gathers evidence from the sources in `project-workflow.md` before any theory.
- The taxonomy includes sibling cases and at least one MUST NOT near miss.
- Explains before the diff: first-person story, then root cause with file:line, then the fix.
- Under a test freeze, reproduces by inspection and writes no new test.
- Says "fixed" only when the symptom was observed gone; otherwise "unverified".

## Cases

### Reported instance of a class
**Prompt:** `/tej-core:bugfix dates show a day early for users in Sydney`
**Expected:** Taxonomy covers every timezone shape (positive and negative offsets, DST edges), a
near miss where UTC users must stay unchanged, explanation before any diff.

### Two failed fixes
**Prompt:** `still broken after both fixes`
**Expected:** Stops tuning and questions the premise instead of a third tweak.
