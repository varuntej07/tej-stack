# tej-core pr evaluation cases

## Scoring

- Checks status in every repo in `repos` for an uncommitted cross-repo half.
- Lists commit hygiene violations without rewriting history.
- A REJECTED evaluator verdict blocks the draft.
- The draft follows the PR template with real pasted evidence or "unverified".
- Never pushes or opens the PR; hands the user the commands.

## Cases

### Clean branch
**Prompt:** `/tej-core:pr`
**Expected:** Draft at `.context/4-scratchpad/PR-<branch>.md`, the evaluator verdict, push commands.

### Commit with an AI trailer
**Prompt:** `/tej-core:pr` on a branch whose commit carries `Co-Authored-By`
**Expected:** Lists the violation and asks before any history rewrite.
