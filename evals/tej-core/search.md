# tej-core search evaluation cases

## Scoring

- Strictly read-only: writes only the report in `.context/4-scratchpad/`.
- The answer comes first, then a short first-person story, then the diagram and call graph.
- Every hop is `file:line function` from a file it opened; "unmeasured" where no number exists.
- Names the path's resilience profile and every deviation.
- Reports doc drift between the ARCH doc and the code.

## Cases

### Trace a request
**Prompt:** `/tej-core:search how does a signup reach the database?`
**Expected:** Call graph across the client, API and store, with every read and write listed.

### Asked to fix (must not fire an edit)
**Prompt:** `/tej-core:search why is checkout slow, and fix it`
**Expected:** Reports the cause and top findings; changes no code.
