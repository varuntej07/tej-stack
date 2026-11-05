# Working style

How the user wants work done in this repo. The tej-core rules (explain-first, design for the
class, done means observed) already load every session; add only what is specific here.

## Approvals
- <Who runs builds, launches and deploys. What needs explicit approval first.>
- Never commit, push, deploy or publish without the user asking in the current message.

## Tests
- Test policy: <normal | TEST FREEZE until ...>. Under a freeze, no new test file, case or
  fixture, and never a test written to diagnose; verify by inspecting the real object and running
  the existing suite. Repairing an existing test is always allowed.

## Commits
- <Message shape, length limit, banned trailers.>

## Shell and style
- <Shell the user runs commands in, so every command you hand over uses its syntax.>
- <Banned punctuation or wording in code, docs and replies.>
