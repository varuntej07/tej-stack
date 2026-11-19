# speed-dial

A separate Claude Code hook plugin. Optional, and it needs your own API key. Save the commands you run all the time, then type a short prompt like "make the play store build" and the matching command starts in a new terminal window before the model runs. Matching is done by [Jev](https://typesafe.ai), TypeSafe's decision model, so it needs **your own `TYPESAFE_API_KEY`**. Tej Core and the Tej Stack skills do not need it.

## Install

```text
/plugin marketplace add varuntej07/tej-stack
/plugin install speed-dial@tej-stack
/reload-plugins
```

It needs Node 18 or newer on `PATH` and your TypeSafe key:

```powershell
setx TYPESAFE_API_KEY "your-key"        # Windows, then restart Claude Code
```

```sh
export TYPESAFE_API_KEY="your-key"      # macOS / Linux, in your shell profile
```

```text
you> make the play store build
speed-dial: android_release (0.93) is running in a new window
> flutter build appbundle --release
```

## Saving commands

Put them in `.claude/speed-dial.json` at a repo's root (commit it to share with your team), or in `~/.claude/speed-dial.json` for your own commands across every repo. If both files use the same id, the project entry wins. See [the example](../plugins/speed-dial/examples/speed-dial.json).

| Field | Meaning |
| --- | --- |
| `id` | Lowercase letters, digits, `_` or `-`. Shown when it runs. |
| `description` | What Jev reads to decide. Say what the command does in words people would actually use. |
| `command` | A string, or `{ "windows", "macos", "linux" }`. It runs in PowerShell on Windows and bash elsewhere. |
| `cwd` | Folder to run in. Relative paths resolve from the current repo root. Default `.`. |
| `confirm` | `true` waits for Enter in the new window before running. Use it for deploys. |

## Trust

A repo's `.claude/speed-dial.json` could label a destructive command as something harmless. So a project file stays off until you read it and type `speed-dial trust` in Claude Code. Any later edit switches it off again until you trust it again. Your own `~/.claude/speed-dial.json` is always on.

## What it will not do

- Prompts over 12 words, or starting with `/` or `!`, skip speed-dial and cost nothing.
- Unless both Jev answers reach 0.85 confidence, the prompt goes to Claude as usual.
- A missing key, a timeout, a network error or a malformed file never blocks a prompt. It passes through.
- Jev sees only each entry's id and description, never the command, and can only pick from your list.
- Command output stays in its own window, out of Claude's context. If a command fails, paste the error into Claude.

## Uninstall

```text
claude plugin uninstall speed-dial@tej-stack
```
