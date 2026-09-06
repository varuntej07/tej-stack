# Proof playbook

Every finding needs a measurement that could show it is wrong. This file is how to get one, per layer, in a way that does not depend on the language.

**State the expected result before measuring.** A prediction that survives is evidence. A number collected first and explained afterwards is a story.

**Prefer counting to timing.** Counts (queries, syscalls, allocations, comparisons, rendered nodes) are deterministic and survive a noisy machine. Timing is the fallback when nothing countable represents the cost.

---

## 1. Anything touching a database

The query plan is the only thing that settles whether an index is used. Schema inspection cannot, and neither can reading the query.

| Engine | Command |
|---|---|
| SQLite | `EXPLAIN QUERY PLAN <query>` |
| PostgreSQL | `EXPLAIN (ANALYZE, BUFFERS) <query>` |
| MySQL / MariaDB | `EXPLAIN FORMAT=JSON <query>`, or `EXPLAIN ANALYZE` |
| SQL Server | `SET SHOWPLAN_ALL ON`, or the actual execution plan |
| Oracle | `EXPLAIN PLAN FOR <query>` then `DBMS_XPLAN.DISPLAY` |
| MongoDB | `db.c.find(...).explain("executionStats")` |
| Elasticsearch | `_search` with `"profile": true` |
| Document/KV stores | The provider's request metrics: consumed units, scanned versus returned |

Read for: **SCAN versus SEARCH**, the index name, whether it says covering, a sort or temp b-tree that should not be there, and rows examined versus rows returned. A large gap between examined and returned is the signal, regardless of engine.

Reproduce the plan cheaply: create an in-memory or scratch database, apply the **real DDL copied from the source**, and run `EXPLAIN` on the real query text. This takes seconds and needs no production access. Copy the DDL rather than retyping it — a retyped schema is a different schema.

Two traps that make an index silently unusable, both invisible in review:

- **A partial index whose predicate column is supplied as a bound parameter.** Applicability is decided when the statement is prepared, before the value is known, so the index cannot be proven to apply. Writing the predicate as a literal fixes it. Confirm with a plan.
- **A function or cast wrapping an indexed column** (`WHERE lower(email) = ?`, an implicit type coercion). The index on the raw column no longer applies.

For N+1: count statements per operation, do not time them. Most ORMs and drivers have a query log or a statement counter. Expect the count to be constant with respect to row count; if it grows with rows, it is N+1 no matter how fast each one is.

## 2. I/O and syscalls

Count the calls. Timing hides the pattern; the count is the finding.

- Instrument the wrapper: a counter incremented on every call, printed per operation.
- System-level: `strace -c -f` (Linux), `dtruss` (macOS), Process Monitor (Windows), filtered to the operation.
- File and network layers usually expose counters already: open file handles, requests sent, bytes read.

Expected result: a count that is constant per operation, not proportional to the number of items. **Beware the warm-cache number.** A metadata call is microseconds warm and can be far worse cold or with a filesystem filter or scanner in the path; measure or reason about the cold case explicitly.

## 3. Compute

- Use the runtime's sampling profiler on a realistic workload. Look for self time, and for a frame that appears once per item where it should appear once per batch.
- Confirm the hot path is genuinely hot before optimizing it. A profile that does not show the function is a refusal, not an inconvenience.
- Microbenchmarks: vary the input, consume the result so it cannot be eliminated, separate warm-up, and report the distribution rather than the mean.
- If the runtime exposes operation counts (comparisons, iterations), assert on those instead of time.

## 4. Allocation and memory

- Allocation counters or an allocation profiler, per operation. Expected result: allocations constant per operation rather than per item.
- Peak resident memory before and after, on the same realistic input.
- In collected runtimes, watch collection count and pause time, not only throughput.
- For a suspected leak, take two heap snapshots separated by a full cycle of the operation and diff by retained size.

## 5. UI and rendering

- **Count rendered nodes**, not milliseconds: the count is the finding and it is stable across machines.
- Component profilers show which subtrees re-rendered and why. Expected result after memoization: siblings do not re-render when one row's state changes.
- Check that a memoized component's props are referentially stable; memoization with fresh closures per render is a no-op, and the profiler shows it plainly.
- For a virtualized list, assert that mounted rows stay bounded as the collection grows. That is the property; frame time is a proxy for it.

## 6. Concurrency

- Throughput as a function of worker count. If it flattens or falls, you have found the shared bottleneck. Report the curve, not a single number.
- Contention and retry counters: transaction conflicts, lock waits, pool exhaustion.
- Tail latency, not the mean. Contention shows in p99 long before it shows in the average.

## 7. The compiler and the type system as proof

The strongest evidence is often not a measurement.

- Remove a redundant computation and the helper it used becomes unreachable: an **unused symbol or unused import error is proof** that the call site is gone, stronger than any assertion.
- Delete a field and let the compiler enumerate every reader.
- Narrow a type so the wasteful path stops type-checking.
- Where a language has no such feedback, a temporary assertion that the expensive function is never called during the operation serves the same purpose. Remove it afterwards.

## 8. What is not proof

- **A passing test suite.** It shows behaviour did not change, which was never the question.
- **The code looks simpler.** A readability argument is legitimate on its own terms; it is not evidence about cost.
- **A benchmark of a different N** than the one sourced in refusal rule 2.
- **A single wall-clock reading** on a shared, thermally variable machine.
- **The absence of a complaint.** Nobody reports a page that is slow only with a large account.
