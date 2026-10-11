---
name: x-ray
description: Map any code file, repo flow, architecture, or concept into an interactive Figma-style block diagram page where clicking a block opens everything used at that step (file and line, signature, inputs, outputs, config, code excerpt, gotchas, official docs). Use when the user says x-ray, xray, x-ray this, map this, diagram this flow, show the architecture, walk me through how this works visually, trace this request end to end, or explain a definition or concept as a flow. Also triggers on speech-to-text forms like x ray, ex ray, or extra this. Works on a single file, a whole repo, a pasted snippet, or a concept with no code. Never edits the user's code; it only writes the graph JSON and the HTML page.
---

# X-Ray

> **Update check (run silently first):** run `bash "<this skill's directory>/../../bin/check-update.sh"` and read its single `TEJ_STACK:` status line. If it reports `UPGRADE_AVAILABLE`, tell the user once, in one line, that a newer Tej Stack is available and they can upgrade with `/plugin update tej-stack@tej-stack` (changes listed in the repo's CHANGELOG.md), then continue this task normally. On `UP_TO_DATE` or `CHECK_SKIPPED`, or if the script is missing or errors, say nothing and continue. The check must never block, delay, or fail the task.

X-Ray turns a target into one self-contained HTML page:
- a dot-grid canvas of blocks grouped in Figma-style frames, with labeled arrows,
- a layers panel to search and jump to blocks,
- an inspector that shows everything known about the selected block,
- step-through buttons that walk the main path in order.

The page works offline as a local file and also publishes as a claude.ai Artifact.

**Evidence contract.** Every block is grounded in something you read: a file and line, a config value, a test, or an official doc. Anything you deduced is marked `confidence: "inferred"` and listed in the map's `limits`. Never invent line numbers, values, or runtime numbers. Do not edit the user's code.

## Files in this skill

| Path | Use |
|---|---|
| `scripts/scan_repo.py` | Fast structural scan: entry points, symbols, `--find` call sites. Standard library only. |
| `scripts/build.py` | Validates the graph JSON and renders the HTML page. Standard library only. |
| `assets/template.html` | The canvas renderer. Do not edit it per map. |
| `references/schema.md` | The graph JSON format. Read it before you write the graph. |
| `references/tracing.md` | How to trace code files, repos, and concepts, plus the metadata and web rules. |
| `examples/` | Two complete graphs: a code flow and a concept. Copy their shape. |

In the commands below, `SKILL_DIR` is the folder that contains this file. Use `python3`, or `python` on Windows. The scripts need only the Python 3.9+ standard library.

## Workflow

### 1. Decide the target and the mode

| User gives | Mode | Scope |
|---|---|---|
| One file, or a pasted snippet | `code` | The main flow through that file |
| A repo plus a flow name ("login", "POST /chat") | `code` | That flow, entry to exit |
| A repo with no flow named | `code` | Architecture overview, one block per module or service. Offer detail maps after. |
| A term or idea ("KV cache", "OAuth PKCE") | `concept` | The stages of the idea in causal order |
| A concept plus their code | `hybrid` | Concept stages, linked to real code locations |

If the scope is truly unclear and the repo is large, ask one question: which flow to map. Otherwise start.

### 2. Gather the facts

Read `references/tracing.md` and follow the section for the mode. For a repo, start with:

```bash
python3 SKILL_DIR/scripts/scan_repo.py <repo-or-file>
python3 SKILL_DIR/scripts/scan_repo.py <repo> --find <symbol>
```

Then read the actual source of every block you will draw. When web tools are available, look up the official docs for each external library, service, and model, and for concepts, the paper or spec (see "Web enrichment" in `references/tracing.md`).

### 3. Write the graph JSON

Read `references/schema.md`. Look at `examples/code-chat-flow.json` or `examples/concept-kv-cache.json`. Write the graph to a scratch file, for example `x-ray-<slug>.json`.

Rules:
1. 6 to 25 blocks. Split bigger flows into an overview plus detail maps.
2. Every block has `metadata.summary`. Code blocks have `location.file` and `location.line` from the real file.
3. Copy `signature` and `code` from the source. Never invent line numbers, values, or runtime data.
4. `runtime` only for observed values, with `runtime_source`.
5. Mark anything you did not read with `confidence: "inferred"`. List gaps in top-level `limits`.
6. Label arrows with what moves along them. Number the main path with `step`.

### 4. Build and validate

```bash
python3 SKILL_DIR/scripts/build.py x-ray-<slug>.json -o x-ray-<slug>.html                    # local browser file
python3 SKILL_DIR/scripts/build.py x-ray-<slug>.json -o x-ray-<slug>.html --target artifact  # for the Artifact tool
```

If the build prints `ERROR`, fix the JSON and run it again. Fix warnings about missing summaries or locations when you can.

If Python is not available: read `assets/template.html`, replace `__XRAY_TITLE__` with the title, and replace `/*__XRAY_DATA__*/` with the JSON (escape every `</` as `<\/`). For a local file, wrap the result in `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body> ... </body></html>`.

### 5. Deliver

Pick the first option the environment supports:
1. **Artifact tool available** (claude.ai, Claude app): build with `--target artifact`, publish the file with the Artifact tool, and give a one-line summary.
2. **Local machine** (Claude Code, other agents): build with `--target local`, write it next to the repo or in the folder the user named, and tell the user the path. Open it if the user asks (`open` on macOS, `xdg-open` on Linux, `start` on Windows).
3. **Otherwise**: send the HTML file.

Also keep the graph JSON. The user can re-render it or drop it onto an empty template page.

### 6. Reply

Give 2 to 4 sentences: what the map covers, where the flow starts, and anything important you found (a risk, a gap, an inferred area). Offer one next step, for example a detail map for the largest block. Do not repeat the metadata in chat.

## Updating a map

When the user asks to change a map ("add the error path", "split the retriever"), edit the graph JSON, rebuild, and republish to the same place. Keep node ids stable so the user's mental map stays valid.
