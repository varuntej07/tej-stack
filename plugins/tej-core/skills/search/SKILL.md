---
name: search
description: Read-only investigation across every repo in scope that answers a question about the code and writes a call graph, latency and storage audit, resilience gaps and doc drift to the scratchpad. Use when the user asks how something works, where a value comes from, why a path is slow, or says "search", "trace this", or "investigate" in a repo set up with tej-core. Never edits code.
---

# Search

Investigate: the user's question.

Strictly read-only: no edits to any tracked file, no builds, no git writes. The only file you
write is the report. Read `.context/tej-core.json` for `repos` and never read a `never_touch`
folder.

1. Use the `CLAUDE.md` lookup table to pick the `.context/1-docs/ARCH-*.md` docs; read them first
   so the search starts from the documented design, then verify every claim against live code.
2. Search every repo in `repos`. Follow the call across every boundary (IPC, REST, websockets,
   queues, databases, object storage).
3. Write `.context/4-scratchpad/SEARCH-<slug>.md` with:
   - **Answer first**: the direct answer or number in the first lines.
   - **The story**: a short first-person paragraph of how the path works, in plain words.
   - **ASCII block diagram** of the path found.
   - **Call graph**: ordered `file:line function` hops, one per line, with the transport at each
     boundary.
   - **Latency and storage audit**: every timeout, deadline, cache and database or storage read
     and write on the path, with file:line; "unmeasured" where no number exists.
   - **Resilience gaps**: the path's profile (FastFail or Resilient, from
     `resilience-profiles.md`) and every deviation (retry on a FastFail path, missing timeout,
     missing fallback, swallowed cancellation, cause-dropping catch).
   - **Doc drift**: anything the ARCH doc says that the code contradicts.
4. Reply with the answer, the report path and the top three findings. Do not fix anything.
