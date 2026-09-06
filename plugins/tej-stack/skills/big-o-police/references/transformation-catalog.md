# Transformation catalog

Indexed by **access pattern**, not by algorithm name, so it is reachable from a description of the problem rather than from already knowing the answer. Language and runtime neutral: names differ (`Set`, `HashSet`, `dict`, `map[T]struct{}`, `unordered_set`), the shape does not.

Every entry gives the signal that selects it, the change in cost, the constant-factor caveat, and the failure mode of applying it wrongly. **Read the caveat before recommending.** Most bad optimizations in this catalog are correct transformations applied where the caveat bites.

---

## Membership, dedup, and difference

**Signal:** `if x in collection`, `collection.contains(x)`, `.indexOf(x) >= 0`, or a nested loop asking whether an element of A appears in B.

| From | To | Cost | Caveat |
|---|---|---|---|
| Linear scan of an array or list | Hash set | O(n) → O(1) per lookup | Building the set is O(n) and allocates. For one lookup, the scan wins. Break-even is roughly two to three lookups. |
| Nested loop intersection or difference | Build a set from the smaller side, scan the larger | O(n·m) → O(n+m) | Build from the **smaller** side; getting this backwards keeps the memory cost and loses the win. |
| Set of small dense integers | Bitset | O(1), memory /64 | Only for dense ranges. Sparse ids waste enormous space. |
| Membership where a false positive is tolerable | Bloom filter or similar | Large memory saving | Requires an exact fallback path. Never use where a false positive is a correctness bug. |
| Repeated string comparison of a bounded vocabulary | Interning, then identity compare | O(len) → O(1) | Interning table grows unboundedly if keys are user-supplied. |

**Failure mode:** replacing a scan over 8 config entries with a set. Refusal rule 2.

---

## Grouping, joining, and lookups by key

**Signal:** two nested loops matching records; repeatedly searching a collection for the item whose id matches; the same `find` inside a loop over another collection.

| From | To | Cost | Caveat |
|---|---|---|---|
| Nested-loop join | Hash join: index one side by key, stream the other | O(n·m) → O(n+m) | Needs memory for the indexed side. If one side is huge and the other tiny, index the tiny one. |
| Repeated `find`/`filter` by the same key inside a loop | Build the index once outside the loop | O(n) per lookup → O(1) | The index goes stale if the collection mutates inside the loop. |
| Sorted inputs joined by key | Merge join | O(n+m), no extra memory | Only if genuinely sorted by the join key already; sorting to enable it costs O(n log n). |
| Grouping by a derived key | Single pass into a map of key to bucket | Multiple passes → one | Watch key collisions from a lossy derivation. |

---

## Ordering, top-K, and selection

**Signal:** sorting to read only the first few; sorting inside a loop; re-sorting after each insert; "the largest", "the most recent N".

| From | To | Cost | Caveat |
|---|---|---|---|
| Full sort to take K | Bounded max/min heap of size K | O(n log n) → O(n log k) | Only pays when k ≪ n. At k ≈ n a sort is faster and simpler. |
| Full sort to find one element by rank | Quickselect / nth_element | O(n log n) → O(n) average | Worst case O(n²) on adversarial input; use an introselect variant if input is untrusted. |
| Sorting inside a loop | Sort once outside, or maintain order incrementally | O(n² log n) → O(n log n) | Incremental maintenance shifts cost to writes. Check the operation mix. |
| Repeated "insert and keep sorted" | Balanced tree or skip list | O(n) insert → O(log n) | Higher constant and worse locality than an array. For small n, an array insert wins outright. |
| Priority-ordered processing | Heap / priority queue | O(n) scan for min → O(log n) | Heaps are not stable and give no order beyond the top. |

---

## Ranges, prefixes, and repeated aggregates

**Signal:** summing, counting, or maxing over a sub-range repeatedly; recomputing an aggregate over the same data after small changes.

| From | To | Cost | Caveat |
|---|---|---|---|
| Recomputing a range sum per query | Prefix sums | O(n) per query → O(1) | Static data only. Any update invalidates the whole array. |
| Range aggregate over mutating data | Fenwick tree (sums) or segment tree (general) | O(n) → O(log n) both | Real implementation cost. Justify with query volume, not elegance. |
| Immutable range min/max | Sparse table | O(1) query, O(n log n) build | Build cost and memory; idempotent operations only. |
| Aggregate recomputed after each append | Running accumulator | O(n) per append → O(1) | Floating point drifts when accumulated incrementally; recompute periodically if exactness matters. |

---

## Sequences, windows, and scanning

**Signal:** an inner loop that re-examines elements the outer loop already passed; "for each element, look at the previous k"; substring or subarray search.

| From | To | Cost | Caveat |
|---|---|---|---|
| Recomputing over a sliding window | Sliding window with incremental update | O(n·k) → O(n) | Needs an invertible aggregate. Max is not invertible; use a monotonic deque. |
| Pair search over a sorted sequence | Two pointers | O(n²) → O(n) | Requires sorted input and a monotonic predicate. |
| "Next greater/smaller element" | Monotonic stack | O(n²) → O(n) | Easy to get the strict-versus-non-strict comparison wrong; state which you mean. |
| Repeated substring search of the same needle | Precomputed automaton (KMP, Aho-Corasick for many needles) | O(n·m) → O(n+m) | Only pays with a reused needle set or large inputs. |
| Repeated hashing of shifting windows | Rolling hash | O(n·k) → O(n) | Collisions require verification; unverified rolling-hash matching is a correctness bug. |

---

## Prefixes, paths, and hierarchies

**Signal:** autocomplete, longest-prefix match, routing tables, many keys sharing prefixes.

| From | To | Cost | Caveat |
|---|---|---|---|
| Scanning all keys for a prefix | Trie or radix tree | O(n·len) → O(len) | Memory-heavy and pointer-chasing; a sorted array plus binary search on the prefix range is often better and far simpler. |
| Repeated ancestor or connectivity queries | Union-find with path compression | near O(1) amortized | Union-find cannot delete or enumerate a set cheaply. |
| Dependency ordering computed repeatedly | Topological sort once, cache the order | O(V+E) per query → once | Must be invalidated when the graph changes. Detect cycles explicitly rather than looping forever. |

---

## Search over an answer space

**Signal:** trying candidate values in order until one satisfies a monotone predicate; "smallest capacity that works", "largest batch that fits".

| From | To | Cost | Caveat |
|---|---|---|---|
| Linear scan of candidates | Binary search on the answer | O(n) → O(log n) evaluations | **The predicate must be monotone.** If it is not, binary search silently returns a wrong answer. Verify monotonicity explicitly. |
| Unbounded search from zero | Exponential (galloping) search, then binary | O(n) → O(log answer) | Overflow at the doubling step on fixed-width integers. |

---

## Reuse: caching, memoization, and persisted derivations

**Signal:** the same expensive result computed more than once from inputs that did not change.

| From | To | Cost | Caveat |
|---|---|---|---|
| Recomputing a pure function of immutable inputs | Compute once, store beside the data | N computations → 1 | **The strongest move in the catalog when the inputs truly cannot change.** If they can, a stored derivation is a correctness bug, not an optimization. |
| Repeated computation within a request | Memoize for the request lifetime | Exponential → polynomial for overlapping subproblems | Unbounded memo tables are a leak. Bound the lifetime. |
| Expensive shared results across requests | LRU or TTL cache | Large | Every cache needs an invalidation story. Without one, refuse (refusal rules). |
| Per-call construction of a reusable object | Hoist it: build once, reuse | Setup × N → setup × 1 | Only if the object is genuinely stateless or safely shareable across concurrent callers. Sharing a stateful parser across threads is a data race, not a speedup. |

---

## Data access, pagination, and streaming

**Signal:** loading a whole collection to show or process part of it; `OFFSET` growing with page number; loading a file to read its header.

| From | To | Cost | Caveat |
|---|---|---|---|
| `LIMIT n OFFSET k` | Keyset (seek) pagination on an indexed, ordered column | O(k) → O(log n + page) | Needs a stable, unique sort key; ties break the cursor. Cannot jump to an arbitrary page number. |
| Fetching all rows to filter in the caller | Filter at the source | O(all) transfer → O(matching) | If the filter cannot be expressed at the source (an encrypted column, a computed predicate), say so and bound the result instead. |
| Loading a whole collection to aggregate | Aggregate at the source | Transfer of everything → one row | Moves cost to the source; make sure the source is not the bottleneck. |
| Reading a full file for a small part | Range read, or a sidecar index | O(size) → O(part) | Format must permit it. |
| Unbounded accumulation while streaming | Streaming aggregate, or bounded sketch (count-min, HyperLogLog, reservoir sample) | O(n) memory → O(1) | Sketches are approximate. Never use where an exact count is a contract. |
| Whole-collection sort exceeding memory | External merge sort, or push the sort to the storage engine | Fits | I/O bound; number of passes is what matters, not comparisons. |

---

## Storage-engine and query shapes

**Signal:** anything touching a database. **Every entry here is verified with a query plan, never by reading the schema.**

| From | To | Cost | Caveat |
|---|---|---|---|
| Query per row after a list query (N+1) | Join, `IN` batch, or prefetch | N+1 round trips → 1-2 | Batches have parameter limits; chunk them. |
| Scan because the index is unusable | Make the index usable | O(n) → O(log n) | Common causes: a **partial index whose predicate column is passed as a bound parameter**, so applicability cannot be proven at prepare time; a missing leading column for the equality; a function or cast wrapping the column. |
| Index that cannot serve the query's ordering | Reorder the composite columns | Removes a sort or temp b-tree | Column order is a trade between queries. Decide it by comparing plans, not by rule of thumb. |
| Anti-join against a large subquery (`NOT IN (SELECT ... LIMIT k)`) | Compute the boundary value, then a range predicate | O(n log n) materialization → O(log n) | Only when the set is genuinely "everything past a boundary" in some order. |
| Row-by-row writes in a loop | One transaction, or a bulk statement | N commits and syncs → 1 | Larger transactions hold locks longer; balance against contention. |
| Repeated aggregate over unchanged rows | Materialized view or a maintained counter | O(n) → O(1) | Introduces staleness and an invalidation path. |
| Concurrent writes to one row or document | Shard the counter, or use an atomic increment | Contention aborts → throughput | **This is the parallelisation trap.** More concurrency against one hot row reduces throughput. |

---

## Memory and layout

**Signal:** memory growth tracking input size when it need not; pauses; cache misses in a tight loop.

| From | To | Cost | Caveat |
|---|---|---|---|
| Array of records | Struct of arrays | Better locality on field-wise scans | Worse when whole records are accessed together. Measure; do not assume. |
| Growing a buffer by repeated append | Preallocate with known capacity | Amortized O(n) with copies → one allocation | Only when the size is genuinely known or well bounded. |
| Allocating a scratch buffer per iteration | Hoist and reuse it | N allocations → 1 | Reused buffers must be cleared or fully overwritten, or stale data leaks between iterations. |
| Materializing an intermediate collection | Iterator, generator, or lazy sequence | O(n) memory → O(1) | Laziness changes evaluation order and error timing, and can surprise around resource lifetimes. |
| Boxing small values in a hot collection | Primitive-specialized container | Large constant | Availability is language-specific. |
| Copying a large buffer to change its type view | Reinterpret or slice without copying | O(n) → O(1) | Alignment, endianness, and lifetime constraints. Unsafe in several languages. |

---

## Concurrency and parallelism

**Signal:** a batch loop that could overlap; a lock held across I/O; workers idle.

| From | To | Cost | Caveat |
|---|---|---|---|
| Sequential independent I/O | Bounded worker pool | Wall clock / concurrency | **Size the pool from the downstream constraint** (connection pool, rate limit, hot row), never from the client. Settle all outcomes so one failure does not cancel unrelated siblings. |
| Lock held across an I/O call | Compute inside the lock, do I/O outside | Throughput | Requires proving the state read under the lock is still valid afterwards. |
| Shared mutable counter | Per-worker counters, combined at the end | Removes contention | Readers see a stale total until combination. |
| Fine-grained locking everywhere | One coarse lock, or a single-writer design | Often faster | Contended fine-grained locks can be slower than one coarse lock; measure both. |

---

## Cross-cutting note

Many entries above change **when** work happens rather than how much: precompute, memoize, batch, defer, stream. That axis is usually a larger win than a better inner loop, and it is the one most often missed because it does not look like an algorithm.
