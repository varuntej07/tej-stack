# Flowmap evaluation cases

Use raw prompts without telling the agent how the map should look.

## Scoring

- Picks the right mode: `code` for files and repos, `concept` for a term with no code, `hybrid` when a concept is mapped onto the user's code.
- Every code block has `metadata.location.file` and an integer `line` taken from a file the agent actually read.
- `signature` and `code` are copied from source, not paraphrased.
- Blocks the agent did not read carry `confidence: "inferred"`, and the map's `limits` names the gaps.
- `runtime` values appear only with a `runtime_source`; no invented latency, token counts, or payloads.
- External libraries, services, and models link to official docs when web tools are available.
- Keeps each map between 6 and 25 blocks and offers detail maps instead of one oversized view.
- `scripts/build.py` exits 0 on the final graph, and the agent delivers an Artifact or a local HTML path.
- Never edits the user's source code.

## Cases

### Direct: one endpoint in a repo

**Prompt:** `flowmap the POST /api/chat flow in this repo`

**Expected:** Runs `scan_repo.py`, finds the route handler, traces middleware, retrieval, model call, streaming, and persistence, and builds a `code` map with stepped main path, labeled arrows, and file:line on every code block.

### Direct: single file

**Prompt:** `map app/rag/retriever.py`

**Expected:** Maps the functions in that file in execution order. Imported helpers from unread files are marked `inferred` unless the agent opens them.

### Indirect: wants to understand, not to fix

**Prompt:** `I just joined this project. How does a payment actually get processed here? Show me.`

**Expected:** Treats "show me" plus "how does it work" as a flowmap request, traces the payment flow, and does not propose code changes.

### Concept with no code

**Prompt:** `flowmap the concept: OAuth 2.0 authorization code with PKCE`

**Expected:** `concept` mode, stages grouped by party (client, authorization server, resource server), formulas or exact parameters where they exist (code_verifier, code_challenge S256), gotchas, and the RFC plus one quality explainer in sources. No `location` fields.

### Whole repo, no flow named

**Prompt:** `diagram the architecture of this repo`

**Expected:** Builds an overview with one block per module or service grouped by layer, then offers detail maps for the main flows instead of drawing every function.

### Boundary: runtime numbers requested without data

**Prompt:** `map the checkout flow and show how long each step takes`

**Expected:** Builds the static map, leaves `runtime` empty, and states in `limits` and in the reply that timings need logs, traces, or a profiling run. Does not invent milliseconds.

### Negative: debugging request

**Prompt:** `checkout returns 500 since this morning, why?`

**Expected:** Does not start a flowmap. The request is a failure explanation and belongs to `trace-failure`.

### Negative: feature audit

**Prompt:** `audit the new invite feature before I ship it`

**Expected:** Does not start a flowmap. The request belongs to `walkie-talkie`.
