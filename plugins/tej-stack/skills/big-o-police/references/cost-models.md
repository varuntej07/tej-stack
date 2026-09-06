# Cost models beyond big-O

Asymptotic complexity answers one question: how does cost grow as N grows. It says nothing about the cost at the N you actually have, and it is silent about the four things that most often decide real performance: constant factors, memory hierarchy, allocation, and contention.

Check this file before recommending any transformation. Most incorrect optimizations are correct transformations applied outside their range.

## 1. Constant factors and the crossover point

Every "better" structure has a build cost, a memory cost, and a per-operation constant. Below some N, the naive version wins. That N is the **crossover point**, and it is often larger than people expect.

- A linear scan over a small contiguous array beats a hash lookup, because it is a few cache-resident comparisons against a hash, a modulo, and a pointer dereference. Crossover is commonly in the tens, not the single digits.
- Building a set to answer one membership question is strictly worse than scanning. It pays from roughly the second or third query.
- Balanced trees have both a worse constant and worse locality than arrays. For small collections an array with an O(n) insert routinely beats an O(log n) tree.
- Sorting has an excellent constant and decades of tuning behind it. "Avoid the sort" is often the wrong instinct.

**Rule:** if you cannot state the crossover point and show that the real N is past it, the finding fails refusal rule 2.

## 2. The memory hierarchy

A cache miss costs on the order of a hundred sequential operations. This is enough to invert an asymptotic comparison at practical sizes.

- Sequential access over contiguous memory is prefetchable. Pointer chasing is not. A linked structure with better complexity can lose badly to an array with worse complexity.
- Traversal order matters: iterating a 2D structure against its layout can cost an order of magnitude for identical work.
- "Fits in cache" is a real threshold. Crossing it is a step change, not a gradual slope, which is why a benchmark at small N can mislead completely about behaviour at large N.
- Splitting hot fields from cold ones can matter more than the algorithm, because it changes how much useful data each cache line carries.

## 3. Allocation, garbage, and pauses

Allocation is rarely free and its cost is often paid somewhere other than where it happens.

- Per-iteration temporaries in a hot loop cost allocation, initialization, and eventually collection. Hoisting a reusable buffer removes all three.
- In collected runtimes, throughput and *pause* are different problems. Reducing total allocation can cut tail latency even when mean throughput does not move.
- Growing a buffer by repeated append is amortized O(n) but performs several copies of the whole buffer. Preallocating when the size is known removes them.
- Large short-lived buffers are worse than their size suggests: they can bypass the nursery and cause premature promotion or direct old-generation pressure.

## 4. Amortized, worst case, and tail

Three different questions, routinely conflated.

- **Amortized** is the average over a sequence. A dynamic array append is amortized O(1) and occasionally O(n). Fine for throughput, sometimes unacceptable for a latency budget.
- **Worst case** is what an adversary or an unlucky input gets. Hash tables are O(1) average and O(n) worst case; with attacker-controlled keys that is a denial-of-service vector, not a footnote. Quickselect and naive quicksort have the same shape of exposure.
- **Tail latency** is what users actually feel. Optimizing the mean while making p99 worse is usually a net loss on an interactive path. A cache raises the mean and can worsen the tail on a miss.

State which of the three you are improving. "Faster" is not specific enough to be verified.

## 5. What actually dominates

Order-of-magnitude relationships worth carrying, when deciding what to look at first:

| Operation | Rough scale |
|---|---|
| In-memory operation, cache-resident | nanoseconds |
| Main memory access | ~100× a cache hit |
| Local SSD read | microseconds to tens of microseconds |
| Same-datacentre network round trip | hundreds of microseconds |
| Cross-region round trip | tens of milliseconds |
| Cold filesystem metadata call with a scanner or filter in the path | tens to hundreds of microseconds, highly variable |

The consequence: **an O(n²) in-memory loop over a thousand items is usually cheaper than one avoidable network round trip.** Establish which layer dominates before optimizing anything.

## 6. Contention: where more parallelism is less throughput

Concurrency is bounded by the most contended shared resource, not by the number of workers.

- Concurrent transactions against one row, document, or counter produce conflicts and retries. Past a small concurrency, throughput *falls* and error rates rise.
- A lock held across I/O serializes everything behind the slowest network call.
- False sharing puts unrelated data on one cache line and manufactures contention that is invisible in the source.
- Connection pools, rate limits, and per-partition write ceilings are all hard bounds. Exceeding them converts latency into errors.

**Size a pool from the downstream constraint.** If the shared resource is the ceiling, the fix is to remove the sharing (shard the counter, batch the writes, use an atomic increment), not to add workers.

## 7. Measurement hazards

- A microbenchmark on a warm loop with a constant input can be optimized away entirely. Consume the result and vary the input.
- Benchmarking at unrealistic N answers a question nobody asked. Use the sourced N from refusal rule 2.
- The first iteration includes warm-up, JIT, page faults, and cold caches. Report both cold and warm when both matter; say which you measured.
- Timing under a profiler or a debugger is not timing.
- Wall-clock on a shared or thermally throttled machine is noisy at the scale of most changes. Prefer counting operations (queries, syscalls, allocations, comparisons) over timing them: counts are deterministic, and a count that does not move is a falsified hypothesis.
