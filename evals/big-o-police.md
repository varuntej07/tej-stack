# Big-O Police evaluation cases

Use raw prompts without telling the agent which problems exist, and without hinting that some prompts have no answer.

## Scoring

- Characterizes the access pattern (N and its source, operation mix, ordering need, key shape, lifetime, dominant cost) before naming any structure.
- Establishes what dominates - compute, memory, I/O, or waiting - before proposing anything.
- Looks for I/O in a loop, N+1 access, unusable indexes, per-call setup, wrong cadence, and over-materialization before reaching for an asymptotic rewrite of an in-memory loop.
- States a realistic N and cites where the number comes from. Never accepts "could be large" as a source.
- Names a specific measurement, with the expected result, that would refute the finding. Never treats a passing test suite as evidence about cost.
- Reads a query plan for anything touching a database rather than asserting an index is used.
- States what gets worse for every proposed change.
- Refuses findings that fail a gate, and lists them as deliberate non-findings with the gate that stopped them.
- Reports only; does not edit code unless the user explicitly asks for fixes.
- Never proposes changing a serialization or on-disk format that existing stored data depends on for speed reasons.
- Reports what it could not determine, rather than guessing.

## Cases

### Direct whole-repo audit

**Prompt:** `Audit this repository for algorithmic and data-structure problems.`

**Expected:** Ranked findings with `file:line`, complexity plus concrete cost at a sourced N, the transformation, what gets worse, and a verification command per finding. A deliberate non-findings section and totals. No code edits.

### Indirect trigger, symptom only

**Prompt:** `This page is fine on my account but it hangs for our biggest customer.`

**Expected:** Activates the skill. Treats "scales with data" as the signal, asks or derives what differs at that account, and looks for per-row work, N+1, and over-materialization rather than guessing at a micro-optimization.

### Negative case: must refuse

**Prompt:** `Make this faster.` pointing at a nested loop over a config table with a schema-enforced maximum of 12 entries, called once at startup.

**Expected:** Refuses. Cites Gate 1 (cold path, runs once at startup) and Gate 2 (N bounded at 12 by the schema), states that the simple version is clearer and likely faster than a hashed alternative at that size, and proposes no change. Does not invent a finding to look useful.

### Negative case: no measurement possible

**Prompt:** `I think our JSON parsing is slow, optimize it.` in a codebase with no profiler configured and no reproduction.

**Expected:** Does not propose a rewrite. Establishes whether parsing is on a hot path, asks for or constructs a realistic input, names how it would measure, and says clearly that without a measurement any change is unverifiable. May report the hypothesis as a question, explicitly not as a finding.

### Boundary: the index that is never used

**Prompt:** `Our queue query is slow even though there is an index on exactly those columns.` where the index is partial (`WHERE state = 1`) and the query binds the state as a parameter.

**Expected:** Asks for or produces a query plan rather than trusting the declaration. Identifies that partial-index applicability is resolved when the statement is prepared, so a bound predicate value cannot be proven to match, and that writing the literal fixes it. Verifies with a plan before and after. Full credit only if the plan is consulted rather than the schema.

### Boundary: parallelising into contention

**Prompt:** `We upload 100 records one at a time and it is slow. Parallelise it.` where each upload runs a transaction against one shared per-user counter document.

**Expected:** Does not fan out. Identifies the shared counter as the bounding resource, explains that concurrent transactions against one document produce conflicts and falling throughput, proposes a small bounded pool sized to that constraint, and offers removing the sharing (sharded counter, atomic increment, batching) as the real fix. Names contention metrics as the measurement.

### Boundary: frozen format

**Prompt:** `Our on-disk record format wastes space, switch it to something more compact.` where existing stored files use the current format.

**Expected:** Refuses to treat it as an optimization. Names it a migration with a compatibility and rollback story, warns about anything the format feeds (checksums, signatures, associated data), and asks whether old data must remain readable before discussing encodings.

### Boundary: correct-but-slower proposal

**Prompt:** `Replace this linear search with a hash map.` where the collection holds fewer than twenty elements and is rebuilt every call.

**Expected:** Explains the crossover point, notes that building the map costs a full pass plus allocation and would be paid on every call for a single lookup, and declines. Would accept the change only if the map were built once and queried repeatedly, and says so.

### Boundary: recursion

**Prompt:** `Rewrite this recursive tree walk iteratively so it is faster.`

**Expected:** Does not assume equivalence. Notes that the transformation changes termination and stack behaviour, asks what depth is realistic and whether stack overflow is the actual concern rather than speed, and requires an explicit termination argument. If the motive is depth rather than speed, says so plainly.

### Boundary: fix mode

**Prompt:** `Good findings. Now fix the top two.`

**Expected:** Switches to fix mode only on this explicit instruction. Smallest verifiable change first, one transformation per step, build and tests green after each, and the before-and-after measurement reported for each - including any that did not move.
