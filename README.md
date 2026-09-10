# Tej Stack

[![Validate](https://github.com/varuntej07/tej-stack/actions/workflows/validate.yml/badge.svg)](https://github.com/varuntej07/tej-stack/actions/workflows/validate.yml)

Practical, evidence-first skills for solo founders building and shipping startups with AI coding agents.

Every skill follows the same contract: report with evidence first, name the check that could refute each finding, refuse work that cannot be verified, and change nothing unless explicitly asked. Tej Stack is intentionally small; it currently packages six focused skills and is ready to grow without changing its installation model.

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
| `tej` | Route a vague or voice-dictated request to the right Tej Stack skill. | `$tej` or `/tej` |

## Updating

Every skill quietly checks for a newer Tej Stack at most once per day (a single 3-second request to this repository's `VERSION` file, cached in `~/.tej-stack/`). When an update exists, the skill mentions it in one line and keeps working; nothing ever blocks on the check. To upgrade:

```text
/plugin update tej-stack@tej-stack
```

Direct installs update by re-running the installer with `--update` (Unix) or `-Update` (Windows). See [CHANGELOG.md](CHANGELOG.md) for what changed.

## Repository status

- Skills-only plugin; no MCP server, telemetry, background service, or account required.
- Native Codex and Claude plugin manifests are included.
- Direct installers support user and project scope.
- Skill and package validation runs in CI on Windows and Linux.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep each skill focused on one recognizable user goal and include evaluation cases for behavior changes.

## License

MIT. See [LICENSE](LICENSE).
