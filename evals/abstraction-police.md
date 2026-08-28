# Abstraction Police evaluation cases

Use raw prompts without telling the agent which duplications exist.

## Scoring

- Sweeps by concept across the tree instead of reviewing files one by one.
- Reads both sites before flagging; never reports a bare search hit as a finding.
- Describes the concrete drift between copies, not just that they look similar.
- Ranks findings A (already drifted or dead), B (at-risk hand-synced contract), C (verbosity).
- Lists deliberate look-alikes it examined and did not flag, with reasons.
- Checks comments and project docs for documented intent before convicting a shape.
- Reports only; does not edit code unless the user explicitly asks for fixes.
- Never proposes changing a frozen serialized format that existing stored data depends on.

## Cases

### Direct whole-repo audit

**Prompt:** `Run an abstraction audit on this repository and tell me what should be unified.`

**Expected:** Concept-driven sweep, ranked findings with file:line sites and drift descriptions, a non-findings list, totals, and no code edits.

### Indirect trigger

**Prompt:** `This codebase grew really fast and a lot of it feels copy-pasted. What would you clean up first?`

**Expected:** Activates the skill, leads with the highest-cost drifted copies rather than style complaints, and explains what each unification prevents.

### Two similar functions

**Prompt:** `formatTime in dashboard.ts and timeAgo in inbox.ts look almost identical. Should they be merged?`

**Expected:** Reads both, reports the exact behavioral drift (rounding, input type, fallbacks), and recommends one home with a deliberate choice about which behavior wins, not a blind merge.

### Boundary: documented duplication

**Prompt:** `audit src/store-a.ts and src/store-b.ts for duplication` where one file's header comment says it deliberately mirrors the other for isolation.

**Expected:** Records the pair as a deliberate non-finding, citing the comment, and at most suggests an anchor so the copies cannot drift silently.

### Boundary: frozen serialized format

**Prompt:** `Our two encrypted stores build their record keys differently. Fix them to match.`

**Expected:** Refuses to silently rewrite the grammar existing stored data was sealed under; proposes freezing the legacy grammar in place and pointing only new writes at the shared builder.

### Negative: not a duplication task

**Prompt:** `Rename this variable to something clearer.`

**Expected:** Does not run an audit; handles the rename directly without invoking the skill's report machinery.

### Negative: coincidental similarity

**Prompt:** `These two 10-line validation functions look the same. Merge them.` where one validates user signup input and the other validates webhook payloads.

**Expected:** Identifies that the copies change for different reasons, declines the merge, and says why coupling them is worse than the duplication.
