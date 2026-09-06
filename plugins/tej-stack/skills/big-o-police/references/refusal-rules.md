# Refusal rules

The value of this skill is as much in what it declines as in what it finds. An agent that reports every theoretically-better structure is noise, and worse, it is confidently wrong in a way that is expensive to check.

A finding passes only if **all four gates** hold. Otherwise it belongs in the deliberate non-findings list with the gate that stopped it.

---

## The four gates

### Gate 1 — the path is hot, with evidence

Name what makes it hot: per request, per row, per frame, per item, inside a loop bounded by user data, or on a startup path that blocks the first interaction.

Acceptable evidence: a profile, a call-count, a trace, a code path you can trace from an entry point, or a loop whose bound is user data.

Not acceptable: "this looks expensive", "this is called a lot", nesting depth, or the function being long.

If you cannot establish hotness, say so explicitly. **"I could not confirm this runs often enough to matter" is a valid and useful output.**

### Gate 2 — N is realistic and sourced

State the number and where it came from: a schema limit, a config cap, a product constraint, an observed distribution, or a pagination bound.

If N is small and structurally bounded, refuse regardless of how the code looks. A quadratic loop over a fixed 12-entry config table is not a finding.

If N is unbounded or user-controlled, say so — that raises severity, and it may be a denial-of-service concern rather than a performance one.

"Could grow" without a mechanism is not a source. Name what would make it grow.

### Gate 3 — a measurement exists that would refute you

Name the specific command or counter, and the expected result, before running it. See the proof playbook.

If nothing would distinguish your hypothesis from its opposite, you have an opinion. Report it as a question, not a finding.

### Gate 4 — you can state what gets worse

Every optimization trades something: memory, build or startup time, readability, invalidation surface, a new failure mode, a dependency, harder debugging, worse tail latency.

A finding that claims a pure win is under-analysed. Find the trade or drop the finding.

---

## Refuse outright

- **Cold paths.** Startup-once work, migrations, developer scripts, one-off tools, admin pages used monthly. Correctness and clarity dominate.
- **Small, bounded N.** Below the crossover point, the simple version is genuinely faster. See cost-models.
- **Serialization, wire, and on-disk formats that existing data depends on**, when the motive is speed. A format change is a migration with a compatibility story, not an optimization. This includes anything contributing to a checksum, signature, or associated-data string.
- **Caches with no invalidation story.** "Cache it" without naming what invalidates it and who calls that is a correctness bug waiting for a support ticket.
- **Exotic structures for unmeasurable gains.** If the win cannot be measured, the complexity cost is certain and the benefit is not.
- **Speculative generality.** "This would scale better if we had a million users" is a Gate 2 failure with extra steps.
- **Rewrites presented as optimizations.** If the change also restructures modules, renames concepts, or alters behaviour, it is not an optimization and must not be justified as one.
- **Anything in a security or cryptographic path** where the change affects timing, comparison, or key handling. Constant-time behaviour is a correctness property. Refuse and escalate.

---

## Named anti-patterns

| Anti-pattern | What it looks like | Why it fails |
|---|---|---|
| **Asymptotic tunnel vision** | Replacing a scan with a hash set for a 10-element list | Ignores the crossover point; often slower |
| **Trie for six strings** | Reaching for the impressive structure | Build cost and pointer chasing dominate |
| **Parallelise the bottleneck** | Adding workers against one shared row, counter, or lock | Contention makes throughput *fall* |
| **Cache without eviction** | A map that only grows | Converts a CPU cost into an unbounded memory leak |
| **Optimizing the measured proxy** | Improving the mean while the tail worsens | Users experience the tail |
| **Premature indexing** | An index per query shape | Every index is a write cost; unused ones are pure loss |
| **Micro-optimizing inside an I/O wait** | Tightening a loop that runs while a request is in flight | The cost is the wait, not the loop |
| **Benchmarketing** | A number produced after the change, with no prior prediction | Unfalsifiable; explains any result |
| **Recursion rewrites without a termination argument** | Converting to an iterative or memoized form and assuming equivalence | Changes termination and stack behaviour; requires an explicit argument, not an assumption |

---

## How to write a non-finding

Non-findings are evidence that the audit was a search rather than a pattern match. One line each:

> `src/report/aggregate.ts:88` — nested loop over categories × line items. **Refused, Gate 2:** categories are capped at 24 by the schema and line items at 500 per report, so the worst case is 12,000 comparisons on a background job. The simple version is clearer and fast enough.

> `src/index/build.rs:210` — full re-sort on every insert. **Refused, Gate 1:** called once per import, not per row. Would be an A finding if it moved to the per-row path.

Report the totals: how many regions were examined, how many findings survived each gate, and anything that could not be established — an N with no source, or a path whose hotness could not be confirmed. **What you could not determine is part of the result.**
