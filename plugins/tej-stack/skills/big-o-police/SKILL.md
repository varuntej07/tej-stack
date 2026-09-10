---
name: big-o-police
description: Find where a different data structure or algorithm would measurably reduce time or space cost, prove the win with a complexity argument and a verification step, and refuse the ones that do not pay. Use for requests to make something faster, reduce memory, fix a slow endpoint, page, query, build, job or test suite, explain why something is O(n^2), decide which data structure fits, review an algorithm, or audit a codebase for performance. Apply when the user says something is slow, hangs, times out, spikes memory, gets worse with more data, degrades at scale, or asks what to use instead of a list, loop, scan, or repeated query. Works on any language, runtime, or storage engine. Report only by default; change code only when the user explicitly asks for fixes.
---

# Big-O Police

> **Update check (run silently before the audit):** run `bash "<this skill's directory>/../../bin/check-update.sh"` and read its single `TEJ_STACK:` status line. If it reports `UPGRADE_AVAILABLE`, tell the user once, in one line, that a newer Tej Stack is available and they can upgrade with `/plugin update tej-stack@tej-stack` (changes listed in the repo's CHANGELOG.md), then continue this task normally. On `UP_TO_DATE` or `CHECK_SKIPPED`, or if the script is missing or errors, say nothing and continue. The check must never block, delay, or fail the task.


Find the places where the shape of the work is wrong, and prove it. The mandate is not to make code clever. It is to identify where cost grows faster than it needs to, show the growth with a complexity argument, name the measurement that settles it, and say plainly when a change is not worth making.

Default to a report. Do not edit code unless the user explicitly asks for fixes.

**The failure this skill exists to prevent is not slow code. It is confident, unverified optimization.** A wrong complexity claim reads exactly like a right one. Every finding must carry a way to be proven wrong.

## 1. Derive the structure, do not pattern-match it

Do not start from a catalog of algorithms and hunt for places to apply them. Start from the access pattern and let the structure fall out. For each hot region, answer these before naming any structure:

| Question | Why it decides the structure |
|---|---|
| What is **N**, realistically, and where does that number come from? | A bound of 12 and a bound of 12 million are different problems. Cite the source: a schema limit, a config cap, a product constraint, or production data. "Could be large" is not an answer. |
| What is the **operation mix**? | Read-heavy favours precomputed indexes; write-heavy favours structures cheap to mutate. Build-once-read-many justifies an expensive build. |
| Is **order** required, and which order? | Insertion, sorted by key, by priority, or none. A required order is what forces a heap or a tree over a hash. |
| What is the **key**? | Hashable, comparable, a range, a prefix, a composite. This alone eliminates most candidates. |
| How **long does it live**? | Per request, per session, or process lifetime. Lifetime decides cache versus recompute, and who invalidates. |
| What **dominates**: compute, memory traffic, I/O, or waiting? | Optimizing compute when the cost is I/O changes nothing. Establish this before proposing anything. |

Only after those are answered, consult [references/transformation-catalog.md](references/transformation-catalog.md), which is indexed by access pattern rather than by algorithm name. The catalog is the fallback for recall, never the method.

## 2. Look where the wins actually are

Search in this order. It is ranked by observed payoff, not by how interesting the technique is. The last item is the one people reach for first, and it is the rarest real win.

1. **I/O, a syscall, or a network call inside a loop.** One `stat`, one read, one query, one RPC per item. Cheap in isolation, and the isolated number is always the one quoted. Multiply by N and by the cold case.
2. **N+1 access.** One query for the list, then one per row. The fix is a join, a batch fetch, or a prefetch, not a faster per-row query.
3. **An index the planner never uses.** Declared, maintained on every write, and chosen by nothing. Causes: a predicate column bound as a parameter so a partial index cannot be proven applicable at prepare time; a missing leading column for the query's equality; a type mismatch or a function wrapping the column. **Only the query plan can tell you.**
4. **Per-call setup that dominates per-item work.** Constructing a formatter, a cipher, a regex, a parser, a client, or a connection inside a loop. For small payloads the setup routinely costs more than the operation.
5. **Work at the wrong cadence.** A correct, well-indexed pass that runs far more often than the thing it enforces changes. An O(N) sweep on every request to enforce a rule that moves once a day.
6. **Rendering or materializing more than is consumed.** N rows built for a viewport showing thirty; a full collection serialized across a boundary so the caller can filter it; a whole file read to check one header.
7. **Recomputing a pure function of immutable inputs.** A hash, a parse, a layout, a derived aggregate over data that cannot change. Compute once and store it with the data.
8. **Repeated linear scans over the same collection**, and only then the classic asymptotic rewrites: nested loops that should be a hash join, repeated sorting, membership tests down a list.

## 3. Cost is not only asymptotic

An asymptotically better answer is sometimes slower in the range that matters. Before recommending, check [references/cost-models.md](references/cost-models.md) for the crossover point, cache behaviour, allocation and pause pressure, amortized versus worst-case versus tail latency, and contention.

The contention case deserves naming here because it is the one that looks like an optimization and is not: **parallelising work that shares one hot resource is slower, not faster.** A shared counter, a single row, a global lock, a single-writer file. Concurrency is bounded by the shared resource, not by the client.

## 4. Refusal rules, hard

A finding may only be reported if **all four gates** hold. If any fails, do not report it as a finding; record it in the non-findings list naming the gate that stopped it.

1. **Gate 1, the path is hot, with evidence.** It runs per request, per row, per frame, per item, or in a loop bounded by user data. "Looks expensive" is not evidence. If you cannot establish that it runs often, say so.
2. **Gate 2, N is realistic and sourced.** State the number and where it comes from. If N is small and bounded by something structural, the finding is refused no matter how ugly the code is.
3. **Gate 3, there is a measurement that would refute you.** Name it. If you cannot name one, you have an opinion.
4. **Gate 4, you can state what gets worse.** Memory, build time, readability, invalidation surface, a new failure mode, a dependency. Every optimization trades something. A finding that claims a pure win is under-analysed.

Refuse outright, and say why:

- Optimizing a cold path, a startup-once cost, or a developer script that runs by hand.
- Choosing by asymptotics at small N, where the constant factor decides.
- Any change to a serialization, wire, or on-disk format that existing stored data depends on, when the motive is speed.
- Adding a cache with no invalidation story.
- Replacing clear code with an exotic structure for an unmeasurable gain. [references/refusal-rules.md](references/refusal-rules.md) has the full checklist and the named anti-patterns.

## 5. Prove it, before and after

Every finding ships with a verification step that could show you are wrong. **A passing test suite is not evidence about cost**; it only shows behaviour did not change, which was never the question.

Pick the proof that matches the layer, using [references/proof-playbook.md](references/proof-playbook.md):

- Anything touching a database: the **query plan**, before and after. Nothing else settles whether an index is used.
- I/O and allocation: a counter around the operation, or a syscall trace. Count calls, do not time them.
- Compute: a profile with a realistic input, not a microbenchmark on a warm loop the optimizer can delete.
- UI: rendered node count and a render profile.
- Sometimes the strongest proof is **the compiler**: if removing a redundant computation makes a helper unreachable, an unused-symbol error is proof rather than evidence.

State the expected direction of the measurement before running it. A prediction that survives is worth far more than a number collected afterwards.

## 6. Report

Rank by expected payoff:

- **A** — the cost grows with data and the path is hot. Fix now.
- **B** — real waste on a warm path, bounded impact. Fix when touching the file.
- **C** — correct but wasteful, cost currently invisible. Note it and move on.

For each finding:

1. **Site**: `file:line`, and the enclosing operation.
2. **Current cost**: the complexity AND the concrete cost at realistic N, in the unit that matters (syscalls, queries, allocations, bytes, milliseconds).
3. **Access pattern**: the answers from section 1 that determine the structure.
4. **Transformation**: what to use instead, and the new complexity.
5. **What gets worse**: the trade, explicitly.
6. **Proof**: the exact command or measurement, and the expected result.

End with:

- **Deliberate non-findings**: what you examined and refused, with which refusal rule applied. This section is not optional; it is the evidence you were not simply pattern-matching.
- **Totals**: regions examined, findings by rank, and anything you could not establish (an N you could not source, a path whose hotness you could not confirm).

## 7. If asked to fix

Smallest verifiable change first. One transformation per step, behaviour preserved, build and existing tests green after each. Take the measurement from section 5 before and after each step and report both numbers, including the ones that did not move. An optimization that cannot be shown to have worked should be reverted, not kept on the grounds that it must be faster.
