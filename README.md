# Tej Stack

[![Validate](https://github.com/varuntej07/tej-stack/actions/workflows/validate.yml/badge.svg)](https://github.com/varuntej07/tej-stack/actions/workflows/validate.yml)

Practical, evidence-first skills for solo founders building and shipping startups with AI coding agents.

Every skill follows the same contract: report with evidence first, name the check that could refute each finding, refuse work that cannot be verified, and change nothing unless explicitly asked. Tej Stack is intentionally small; it currently packages seven focused skills and is ready to grow without changing its installation model.

## Install

### Claude Code plugin

Run these inside Claude Code:

```text
/plugin marketplace add varuntej07/tej-stack
/plugin install tej-stack@tej-stack
/reload-plugins
```

### Codex plugin

Add the repository marketplace:

```powershell
codex plugin marketplace add varuntej07/tej-stack
codex plugin add tej-stack@tej-stack
```

Start a new conversation after installation.

### Direct skill install

Use this fallback for hosts that load skills directly:

```sh
git clone --depth 1 https://github.com/varuntej07/tej-stack.git
cd tej-stack
./scripts/install.sh both --user
```

Windows PowerShell:

```powershell
git clone --depth 1 https://github.com/varuntej07/tej-stack.git
Set-Location tej-stack
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 both -Scope user
```

Use `--update` on Unix or `-Update` on Windows to replace an existing Tej Stack skill. The installers refuse to overwrite unrelated skills.

## Skills

| Skill | Purpose | Invoke |
| --- | --- | --- |
| `walkie-talkie` | Audit a completed feature through every affected actor and recovery path. | `$walkie-talkie` or `/walkie-talkie` |
| `trace-failure` | Explain a failure from its real initiating actor through its technical and observable impact. | `$trace-failure` or `/trace-failure` |
| `abstraction-police` | Sweep the codebase for nearly-duplicated abstractions, drifted contracts, and premature abstractions, and report ranked findings. | `$abstraction-police` or `/abstraction-police` |
| `big-o-police` | Find where a different data structure or algorithm measurably reduces time or space cost, prove each win, and refuse the ones that do not pay. | `$big-o-police` or `/big-o-police` |
| `get-cited` | Audit a website for AI answer-engine readiness, rank what blocks retrieval or citation with a proof per finding, and refuse the AEO tactics with no evidence. | `$get-cited` or `/get-cited` |
| `x-ray` | Map a file, repo flow, or concept into a clickable block diagram where each block shows its file, signature, inputs, outputs, config, and docs. | `$x-ray` or `/x-ray` |
| `tej` | Route a vague or voice-dictated request to the right Tej Stack skill. | `$tej` or `/tej` |

## speed-dial (Claude Code plugin)

Asking an agent to "build the release" or "deploy the backend" costs about a minute of agent loop for a command you already know. speed-dial saves those commands in a small file. When a short prompt asks for one, it starts that command in a new terminal window before the model ever runs. Any other prompt goes to Claude unchanged.

```text
you> make the play store build
speed-dial: android_release (0.93) is running in a new window
> flutter build appbundle --release
```

The match is made by [Jev](https://typesafe.ai), TypeSafe's decision model, in roughly a quarter of a second. Jev only sees each entry's id and description, never the command itself, and it can only pick from your list.

### Install

```text
/plugin marketplace add varuntej07/tej-stack
/plugin install speed-dial@tej-stack
/reload-plugins
```

It needs Node 18 or newer on `PATH` and your own TypeSafe API key:

```powershell
setx TYPESAFE_API_KEY "your-key"        # Windows, then restart Claude Code
```

```sh
export TYPESAFE_API_KEY="your-key"      # macOS / Linux, in your shell profile
```

### Save commands

Put entries in `.claude/speed-dial.json` at a repo's root (commit it to share with your team), or in `~/.claude/speed-dial.json` for your own commands across every repo. If both files use the same id, the project entry wins. See [the example](plugins/speed-dial/examples/speed-dial.json).

| Field | Meaning |
| --- | --- |
| `id` | Lowercase letters, digits, `_` or `-`. Shown when it runs. |
| `description` | What Jev reads to decide. Say what the command does in words people would actually use. |
| `command` | A string, or `{ "windows", "macos", "linux" }`. It runs in PowerShell on Windows and bash elsewhere. |
| `cwd` | Folder to run in. Relative paths resolve from the current repo root. Default `.`. |
| `confirm` | `true` waits for Enter in the new window before running. Use it for deploys. |

### Trust

A repo's `.claude/speed-dial.json` could label a destructive command as something harmless. So a project file stays off until you read it and type `speed-dial trust` in Claude Code. Any later edit to the file switches it off again until you trust it again. Your own `~/.claude/speed-dial.json` is always on.

### What it will not do

- Prompts over 12 words, or starting with `/` or `!`, skip speed-dial and cost nothing.
- Unless both Jev answers reach 0.85 confidence, the prompt goes to Claude as usual.
- A missing key, a timeout, a network error or a malformed file never blocks a prompt. It just passes through.
- Command output stays in its own window, out of Claude's context. If a command fails, paste the error into Claude.

## Updating

Every skill quietly checks for a newer Tej Stack at most once per day (a single 3-second request to this repository's `VERSION` file, cached in `~/.tej-stack/`). When an update exists, the skill mentions it in one line and keeps working; nothing ever blocks on the check. To upgrade:

```text
/plugin update tej-stack@tej-stack
```

Direct installs update by re-running the installer with `--update` (Unix) or `-Update` (Windows). See [CHANGELOG.md](CHANGELOG.md) for what changed.

## Repository status

- `tej-stack` is skills-only: no MCP server, telemetry, background service, or account required.
- `speed-dial` is one dependency-free hook script. Its only network call goes to TypeSafe, with your own key.
- Native Codex and Claude plugin manifests are included.
- Direct installers support user and project scope.
- Skill and package validation runs in CI on Windows and Linux.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep each skill focused on one recognizable user goal and include evaluation cases for behavior changes.

## License

MIT. See [LICENSE](LICENSE).
