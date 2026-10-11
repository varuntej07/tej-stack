# X-Ray graph schema

One JSON file describes one map. `scripts/build.py` validates it and injects it into the canvas page.
Every field except `title`, `nodes[].id` and `edges[].from/to` is optional. Leave a field out when you have no real value for it. The page hides empty sections.

## Top level

```json
{
  "title": "Chat request flow",
  "mode": "code",
  "layout": "lanes",
  "subject": "POST /api/chat in aura-backend",
  "summary": "Two or three plain sentences: what the flow does end to end, and where it starts and stops.",
  "root": "client",
  "groups": [{ "id": "api", "label": "API layer" }, { "id": "rag", "label": "Retrieval" }],
  "nodes": [ ... ],
  "edges": [ ... ],
  "context": { "Repo": "aura-backend", "Commit": "a1b2c3d", "Language": "Python 3.12" },
  "limits": ["Static read only. No runtime values were captured."],
  "sources": [{ "title": "FastAPI dependencies", "url": "https://fastapi.tiangolo.com/tutorial/dependencies/", "kind": "docs" }]
}
```

| Field | Meaning |
|---|---|
| `title` | Short name of the map, 2 to 5 words. Becomes the page title. |
| `mode` | `code` (traced from source), `concept` (a definition or idea), or `hybrid` (concept mapped onto real code). |
| `subject` | What was mapped, in one line: a path, symbol, endpoint, or term. |
| `summary` | Overview shown when no block is selected. Blank lines split paragraphs. |
| `layout` | `lanes` (default): one global left-to-right column per depth, so arrows always point right. `compact`: each lane restarts at the left edge. Use `compact` for phases that happen one after another (prefill then decode, client then server), so the map is not a wide staircase. |
| `root` | Node id where the flow starts. The "Start here" button opens it. |
| `groups` | Swim lanes, drawn as Figma-style frames. Order = top to bottom. Use layers or modules: client, API, domain, data, external. |
| `context` | Key-value facts about the whole map. |
| `limits` | What the map does not cover, and what is inferred. Be honest here. |
| `sources` | Links that apply to the whole map. |

## Nodes (blocks)

```json
{
  "id": "retriever",
  "title": "retrieve_context()",
  "subtitle": "Top-k semantic memory lookup",
  "kind": "function",
  "group": "rag",
  "step": 4,
  "metadata": {
    "summary": "Embeds the user message and returns the 5 closest memory chunks above a score threshold.",
    "details": "Longer explanation. How the step works inside, edge cases, why it exists.\n\nSecond paragraph.",
    "location": { "file": "app/rag/retriever.py", "line": 15, "end_line": 48, "symbol": "retrieve_context" },
    "signature": "async def retrieve_context(user_id: str, text: str, k: int = 5) -> list[Chunk]",
    "inputs":  [{ "name": "text", "type": "str", "desc": "Raw user message", "example": "what did I say about my trip?" }],
    "outputs": [{ "name": "chunks", "type": "list[Chunk]", "desc": "Sorted by cosine similarity" }],
    "calls": [{ "id": "embed", "name": "embed()" }, { "id": "vdb", "name": "pgvector query" }],
    "config": { "k": 5, "min_score": 0.72, "EMBED_MODEL": "text-embedding-3-small" },
    "runtime": { "latency": "140 ms", "chunks returned": 5 },
    "runtime_source": "logs/app.log 2026-10-10 14:02",
    "code": "async def retrieve_context(user_id, text, k=5):\n    vec = await embed(text)\n    ...",
    "lang": "python",
    "notes": ["Called once per request.", "Results are not cached."],
    "gotchas": ["min_score is hard-coded; tune it per embedding model."],
    "sources": [{ "title": "pgvector README", "url": "https://github.com/pgvector/pgvector", "kind": "docs" }],
    "fields": { "Owner": "rag module", "Async": "yes" },
    "confidence": "verified"
  }
}
```

| Field | Meaning |
|---|---|
| `id` | Unique, stable, kebab or snake case. |
| `title` | The real name: function name with `()`, class name, service name, or the concept stage. |
| `subtitle` | 3 to 8 words: what the block does. Shown on the card. |
| `kind` | Sets color and label. See the kind list below. |
| `group` | A `groups[].id`. Blocks with no group go to a lane at the bottom. |
| `step` | Order in the main path (1, 2, 3...). Drives the step-through buttons. Leave it off side branches. |
| `rank` | Optional column override (0 = leftmost). Normally computed from the edges. |
| `x`, `y` | Optional fixed position in pixels. Normally computed. |

### Metadata fields

| Field | Inspector section | Rule |
|---|---|---|
| `summary` | What it does | Required in practice. 1 to 2 sentences. |
| `details` | How it works | Optional depth. Blank lines split paragraphs. |
| `location` | Location | `file` relative to the repo root, `line` and `end_line` as integers. Copy button copies `file:line`. |
| `signature` | Signature | Exact text from the source. |
| `inputs`, `outputs` | Inputs / Outputs | Objects with `name`, `type`, `desc`, `example`, or plain strings. |
| `calls`, `uses` | Calls and uses | Strings or `{id, name}`. A matching node id becomes a clickable chip. |
| `config` | Config and parameters | Env vars, constants, flags, hyperparameters, with their values. |
| `runtime` | Runtime values | Only values you actually observed. Always set `runtime_source`. |
| `code` | Code | A short excerpt, 5 to 30 lines. Line numbers start at `location.line`. |
| `formula` | Formula | For concept mode. Plain text math, for example `softmax(QKᵀ/√d_k)·V`. |
| `example` | Example | A string or an object (shown as JSON). |
| `fields` | Details | Any extra key-value facts. |
| `notes` | Notes | Bullet list. |
| `gotchas` | Gotchas | Bullet list of risks, bugs, and traps. |
| `sources` | Sources and docs | `{title, url, kind}` where kind is `docs`, `code`, `paper`, `spec`, or `article`. |
| `confidence` | badge next to the title | `verified` (you read the code or the doc) or `inferred` (you deduced it). |

### Kinds

| Kind | Color | Use for |
|---|---|---|
| `entry`, `route` | blue | Where the flow starts: HTTP route, CLI command, event, cron, UI action |
| `function`, `method`, `class`, `module`, `component`, `hook` | violet | Your own code |
| `middleware`, `config`, `step` | slate | Cross-cutting layers, settings, generic stages |
| `service`, `external`, `model` | teal | Third-party APIs, other services, ML models |
| `datastore`, `cache`, `queue`, `data`, `file` | amber | Databases, caches, queues, data objects, files |
| `decision`, `error` | rose | Branch points and failure paths |
| `concept`, `formula` | violet | Concept-mode stages and math |
| `output`, `test` | green | Final results, responses, side effects, tests |

## Edges (arrows)

```json
{ "from": "router", "to": "retriever", "label": "text, user_id", "kind": "call" }
```

| Field | Meaning |
|---|---|
| `from`, `to` | Node ids. |
| `label` | What moves along the arrow: arguments, data type, event name, or condition. Keep it under 30 characters. |
| `kind` | `call` (solid, default), `data` (dashed), `async` (dotted: queue, event, background task), `return` (fine dots), `conditional` (solid, put the condition in `label`). |

Back edges (loops, retries) are allowed. They are drawn under the blocks.
