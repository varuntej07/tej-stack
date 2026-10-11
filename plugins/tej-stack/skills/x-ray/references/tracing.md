# How to trace a target into an x-ray

Read the section for the input type. Then apply "Granularity" and "Web enrichment" to every map.

## A. Single code file

1. Read the whole file.
2. Find the entry: exported function, route decorator, `main`, `__main__` guard, class constructor, or the function the user named.
3. Walk the calls in execution order. Each meaningful call becomes a block. A meaningful call does I/O, changes state, branches the flow, or does real computation.
4. Imports from other files: add one block per imported thing you call, with `confidence: "inferred"` unless you open that file too. If the other file is available, open it.
5. Library calls (requests, SQLAlchemy, React Query, boto3, an LLM SDK): one `external` or `datastore` block each. Look up the docs (see Web enrichment).

## B. Repo or project

1. Run `python3 scripts/scan_repo.py <repo>`. It prints entry point candidates, the largest modules, and the most imported packages.
2. Pick the scope:
   - If the user named a flow ("login", "POST /chat", "checkout"), find it with `--find <symbol>` or grep for the route path.
   - If the user said "the whole repo", make an **architecture overview**: one block per module or service, grouped by layer. Then offer detail maps for the main flows.
3. Trace from the entry: open the handler, follow each call with `scan_repo.py <repo> --find <name>`, and read each definition. Stop at the repo boundary (library, network, database).
4. Read config sources that change behavior: `.env.example`, `settings.py`, `config/*.yaml`, `package.json` scripts, `docker-compose.yml`, `serverless.yml`, infra files. Put the values in `config`.
5. Note async boundaries: queues, background tasks, webhooks, cron, websockets. Use `kind: "async"` edges.
6. Check the tests for the flow. They show real inputs and expected outputs. Use them for `example` and `inputs[].example`.

Useful entry signals by stack:

| Stack | Where flows start |
|---|---|
| FastAPI / Flask / Django | `@app.get/post`, `@router.*`, `urls.py`, `views.py`, Celery `@task` |
| Express / Nest / Next.js | `app.get(...)`, `router.post(...)`, `@Controller`, `app/api/**/route.ts`, `pages/api/*` |
| React / React Native / Flutter | the screen component, event handler (`onPress`, `onSubmit`), state store actions, `main.dart` |
| Go | `http.HandleFunc`, `r.GET`, `func main()` |
| Java / Kotlin (Spring) | `@RestController`, `@GetMapping`, `@Scheduled`, `@KafkaListener` |
| Serverless | `handler` / `lambda_handler`, `serverless.yml`, `template.yaml` |
| ML / training | `train.py`, `main()`, dataloader, model `forward()`, optimizer step, eval loop, config YAML |
| CLI | `argparse`, `click`, `typer`, `commander`, `cobra` |

Optional static call-graph tools, if the user has them installed and the repo is large:
`code2flow` (Python, JS, Ruby, PHP), `pyan3` (Python), `madge` or `dependency-cruiser` (JS/TS module graphs). Their output is a hint. Always confirm against the code.

## C. Definition or concept (no code)

1. State the concept in one sentence. That is the map `summary`.
2. Break it into the stages a learner must understand, in the order data or causality flows. Usually 5 to 12 stages.
3. For each stage fill: `summary`, `details` (the mechanism), `inputs` and `outputs` (with shapes or units), `formula` when there is math, `example` with concrete numbers, `gotchas` (common misunderstandings), and `sources`.
4. Use `decision` blocks for real branches (for example "cache hit?"), and `data` blocks for the important intermediate objects (for example "KV cache tensor").
5. Group stages by phase (for example "Prefill" and "Decode", or "Client", "Auth server", "Resource server").
6. If the user has code that implements the concept, use `mode: "hybrid"` and add `location` to the stages that map to real code.

## Granularity

- 6 to 25 blocks per map. If the flow needs more, make an overview map plus one detail map per big area.
- One block = one responsibility. Merge trivial helpers into their caller and mention them in `notes`.
- Every arrow carries a `label` when something specific moves along it (arguments, a payload type, an event name, a condition).
- Mark the main path with `step` numbers. Leave side branches unnumbered.
- Error and retry paths get `error` blocks only when they matter to understanding the flow.

## Metadata quality rules

1. `location.file` and `location.line` must come from the file you read. Never guess line numbers.
2. `signature` and `code` are copied from the source, not rewritten.
3. `config` values come from the code or config files. If the value comes from the environment and is unknown, write `"env: OPENAI_API_KEY (unset here)"`.
4. `runtime` holds only observed values: logs, traces, test output, or a run you did. Set `runtime_source`. Otherwise leave it out.
5. Set `confidence: "inferred"` on any block you did not read directly.
6. Write `summary` and `details` in plain words. Say what happens and why. Do not restate the function name.
7. Add `gotchas` when you see a real risk: a hard-coded value, missing error handling, an N+1 query, a race, a secret in code.

## Web enrichment

Use web search and fetch when the tools are available. Skip this step quietly when they are not.

1. For each `external`, `service`, `datastore`, `model`, or library-heavy block, find the **official** docs page for the exact API used (for example the `messages.create` reference, not the vendor home page). Add it to that block's `sources` with `kind: "docs"`.
2. Check the library version in the lockfile or manifest (`requirements.txt`, `poetry.lock`, `package.json`, `go.mod`). Prefer docs for that version. Note deprecated calls in `gotchas`.
3. For concepts, prefer the original paper or spec plus one high-quality explainer. Add both to `sources`.
4. Put facts learned from the docs (defaults, limits, rate limits, timeouts) in `config` or `notes`, and cite the page.
5. Never paste long passages from a page. Summarize in your own words.
