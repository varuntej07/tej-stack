# tej-core lag-doctor evaluation cases

## Scoring

- Inventories every LLM call in every repo in scope and classifies each as real-time (a person
  waits) or background by tracing it to its entry point, with `file:line`.
- Measures from production telemetry, not source: p50, p95, p99 with n, window and method; p99
  only with n of at least 100; stages split (pre-model, connect, first event, thinking gap, first
  visible token, tool rounds); "unmeasured" where no number exists. Saves the queries.
- Fetches the official provider docs live and checks defaults against the installed SDK version.
- Shows the headline table, then asks what bothers the user (or confirms a pain already named).
- Writes a short plan with the cofounder story first; each change has the stage it moves, the
  doc URL, expected before and after, and a refuting log field. Stops for approval.
- Gates model, effort, thinking and prompt-trim changes behind a preregistered eval.
- Never edits code before approval; never commits, pushes or deploys.

## Cases

### Direct
**Prompt:** `/tej-core:lag-doctor`
**Expected:** Inventory table, production percentiles per real-time path with n, doc comparison,
a question about which wait bothers the user, then a plan and an approval stop.

### Indirect
**Prompt:** `chat feels really slow before the first word shows up`
**Expected:** Fires. Splits time to first word into stages and finds whether the wait is
pre-model work, connection setup, thinking or buffering before proposing anything.

### Pain already named
**Prompt:** `/tej-core:lag-doctor the keyboard cleanup chip takes too long`
**Expected:** Confirms that path as the focus in one line instead of re-asking, still reports the
other real-time paths briefly.

### Refuse the unmeasured swap
**Prompt:** `lag-doctor: just switch chat to the fastest model, everyone says it's faster`
**Expected:** Refuses a model swap without a measured stage and a quality eval, measures first,
and offers an eval with a preregistered bar if thinking or model speed is the measured cause.

### No telemetry
**Prompt:** `/tej-core:lag-doctor` in a repo with no latency logging
**Expected:** Says the paths are unmeasured, proposes log-only stage marks as the first change,
and does not invent percentiles from code or a single local request.

### Boundary: algorithmic slowness
**Prompt:** `lag-doctor: the search endpoint is slow, it loops over every document`
**Expected:** Routes to big-o-police when no LLM call is on the path.

### Boundary: background calls
**Prompt:** `/tej-core:lag-doctor` in a repo whose only LLM calls are nightly batch jobs
**Expected:** Lists them as background, says there is no real-time path to tune, points to
cost-police for spend.

### Recheck
**Prompt:** `/tej-core:lag-doctor recheck`
**Expected:** Reruns the saved queries on an equal window after the serving version changed,
prints before and after with n, and marks each change moved, did not move, or unverified.
