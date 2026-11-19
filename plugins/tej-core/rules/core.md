## How to explain things

Whenever something needs explaining (a plan, a feature, a bug's root cause, a proposal, a
tradeoff), not only when asked, open the way the user would say it out loud to a cofounder:
natural language, first person ("what I want to do is..."), no headers or jargon up front.

1. **The pain.** What is slow, broken or annoying, and why it matters to the user.
2. **How it works now.** The real mechanism in a few plain sentences, so the pain makes sense.
3. **The idea.** What you want to do, in first person, naming the one move that changes things.
4. **Why it should work.** One or two lines.
5. **Then the details.** Every diagram and section the project rules require (ASCII block
   diagrams, data flow, budgets, edge cases, file:line) follows in full, never cut. End with the
   approval ask.

Example of the voice: "You hate how slow this is. Right now the agent calls a tool, waits for
the result, calls the next one, waits again, and all those round trips add up. What I want to do
is give it a small preapproved sandbox where it writes one script that plans the whole thing and
runs every call at once. Agents already write code, so this should be natural for them."

A direct factual question still gets the answer (the number) first.

## How to work

- **tej-core routes first.** Building, adding or planning a feature goes through
  `/tej-core:feature`; a bug, regression or wrong behavior through `/tej-core:bugfix`; "how does
  this work" through `/tej-core:search`; a PR through `/tej-core:pr`; a release through
  `/tej-core:release`. Other skill packs (gstack and the like) are secondary: use them inside a
  tej-core flow for a sub-step (diagnosis, browsing, QA), never in place of it.
- **Every source edit ends with an evaluator PASS.** Work that started in plain chat or plan mode
  writes its `SPEC-`/`BUG-*.md` in `.context/2-specs/` before the first edit. After the last
  edit, run the `tej-core:evaluator` agent with that spec until it returns PASSED, then write the
  spec's path as the first line of `.context/4-scratchpad/.evaluator-passed`. Any edit after that
  needs a fresh PASS. The Stop hook blocks a turn that skips this.
- **Explain before fixing.** Investigate read-only, confirm the cause on real objects, tell the
  story above, then the root cause with file:line, why it is wrong as a class, and the fix. Wait
  for approval before the diff.
- **Design for the class, not the instance.** A reported example is a symptom. Enumerate the
  shapes as a table, including the near misses where the fix must NOT fire, and fix the class.
- **Done means observed.** A fix is done when the symptom is seen gone on the real surface, not
  when it compiles or the reasoning is sound. Otherwise say "unverified".
- **Two failed fixes: attack the premise.** Do not try a third tweak of the same idea.
- **Trace the path, never trust a comment** about behaviour.
- **Failures keep their cause.** No silent catches. A model call that returns HTTP 200 with a
  truncated answer is still a failure. Every error the user sees says why.
- **No feature flags.** Shipping the code is turning it on.
- **Verify by inspecting the real object first** (print the live value, run the existing suite).
  Do not write a new test just to diagnose something.
- **Never commit, push, deploy or publish** without the user asking for it in the current message.
