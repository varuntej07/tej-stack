# Tej Stack

[![Validate](https://github.com/varuntej07/tej-stack/actions/workflows/validate.yml/badge.svg)](https://github.com/varuntej07/tej-stack/actions/workflows/validate.yml)
[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fvaruntej07%2Ftej-stack%2Fmain%2Fplugins%2Ftej-stack%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/varuntej07/tej-stack?style=social)](https://github.com/varuntej07/tej-stack/stargazers)

**Agent skills that show proof or say nothing.**

Your coding agent is confident about everything. Tej Stack skills are not. Every finding comes with the file and line, the measurement, or the doc that backs it, plus the check that would prove it wrong. If a claim can't be verified, the skill refuses to make it. Nothing in your code changes unless you ask.

Built for solo founders shipping with Claude Code and Codex. Plain Markdown skills, no account, no telemetry, no build step.

<!-- Hero: put an x-ray demo GIF or a link to a hosted x-ray page here. A real visual sells this repo faster than any sentence. -->

## Install in 30 seconds

**Claude Code.** Type these inside Claude Code:

```text
/plugin marketplace add varuntej07/tej-stack
/plugin install tej-stack@tej-stack
/reload-plugins
```

**Or from any terminal** (PowerShell, bash, or zsh), then restart Claude Code:

```text
claude plugin marketplace add varuntej07/tej-stack
claude plugin install tej-stack@tej-stack
```

**Or let Claude do it.** Paste this into Claude Code:

> Install Tej Stack for me: run `claude plugin marketplace add varuntej07/tej-stack` and then `claude plugin install tej-stack@tej-stack`. When both succeed, tell me to run `/reload-plugins`, then list the Tej Stack skills and one prompt to try for each.

<details>
<summary><b>Codex, or hosts that load skills directly</b></summary>

**Codex plugin:**

```text
codex plugin marketplace add varuntej07/tej-stack
codex plugin add tej-stack@tej-stack
```

Start a new conversation after installation.

**Direct skill install** (any host that reads `~/.claude/skills` or `~/.codex/skills`):

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

Use `--project` (Unix) or `-Scope project` (Windows) to install into the current repo instead. The installers refuse to overwrite skills they did not install.

</details>

## Quick start

1. Finished a feature? Run `/walkie-talkie` and name it.
2. Something broke? Run `/trace-failure` and paste the error.
3. New to a codebase? Run `/x-ray` and name a flow, like "login" or "POST /checkout".

Stop there. You'll know if this is for you.

## See it work

These are example sessions that show the shape of the output. Your results come from your own code.

<!-- Replace these with real runs against well-known open source repos. Real findings, with links, are what get shared. -->

**Auditing a finished feature**

```text
You:    /walkie-talkie the team invite flow is done. Is it ready?

Agent:  Actors: inviter, invitee (new account), invitee (existing account),
        workspace admin, email worker, expiry job.
        [traces each one through the code and runs the invite tests]

        BLOCKER  An existing user who opens the invite while logged out
                 lands on signup, creates a second account, and joins
                 with that one.
                 Evidence: routes/invite.ts:41 checks the token but not
                 the session. Refute it: open the link logged out with
                 an email that already has an account.
        HIGH     A revoked invite still works until the email worker's
                 cache expires (15 min).
                 Evidence: workers/invite-cache.ts:12, TTL = 900.
        NOT CHECKED  Email rendering in Outlook. No test or fixture exists.
```

**Hunting for performance wins, and refusing the fake ones**

```text
You:    /big-o-police the dashboard gets slow past 2k projects

Agent:  WIN      O(n·m) to O(n + m) in services/stats.ts:88. The nested
                 find() over members runs 2k × 40 times per load.
                 Proof: benchmark at n=2,000 went from 410 ms to 9 ms.
        REFUSED  Swapping the sort for a heap at utils/rank.ts:20.
                 n never exceeds 50 here, so the change adds code
                 without a measurable gain.
```

**Finding where the bill goes**

```text
You:    /cost-police our Anthropic bill doubled after launch

Agent:  Prices fetched today from platform.claude.com/docs/en/about-claude/pricing.
        LEAK     The 6k-token system prompt in api/chat.ts:31 is resent
                 uncached on every turn. 9k turns/day (from your usage
                 export) x 6k tokens = 54M tokens/day. Sonnet 5.5 input is
                 $2/MTok, cache reads $0.10/MTok: about $100/day saved,
                 roughly $3,000/month.
                 Refute it: if cache_read_input_tokens > 0 on /chat, I'm wrong.
        RUNAWAY  POST /summarize calls the model with no login and no
                 per-user limit. One script could spend your whole budget.
        REFUSED  "Switch to the cheapest model." There's no quality eval
                 for this task, and fewer output tokens can make a bigger
                 model cheaper. I can set up an A/B run instead.
```

**Mapping a flow you didn't write**

```text
You:    /x-ray how does a chat message get from the app to the model?

Agent:  Built x-ray-chat-flow.html: 14 blocks, 3 frames (client, API,
        model gateway). Click any block for its file and line, signature,
        inputs, outputs, config, and docs. 2 blocks are marked inferred:
        the retry policy lives in a dependency I could not read.
```

## The skills

| Skill | Your specialist | What it does |
| --- | --- | --- |
| `/walkie-talkie` | **Product QA lead** | Audits a finished feature through every affected user, actor, and recovery path, with code or runtime evidence for each finding. |
| `/trace-failure` | **Incident investigator** | Explains a failure as a causal chain, from the real person or system that started it to the impact users could see. |
| `/abstraction-police` | **Codebase janitor** | Finds near-duplicate abstractions, drifted copies, and premature abstractions, and ranks which merges are worth doing. |
| `/big-o-police` | **Performance engineer** | Finds where a different data structure or algorithm measurably cuts time or memory, proves each win, and refuses the ones that do not pay. |
| `/get-cited` | **AI search strategist** | Audits a website for ChatGPT, Perplexity, Claude, and Google AI answers, with a proof per finding, and refuses AEO myths. |
| `/x-ray` | **Staff engineer at a whiteboard** | Maps a file, repo flow, or concept into a clickable block diagram. Each block shows its file, signature, inputs, outputs, config, and docs. |
| `/cost-police` | **CFO who reads code** | Finds where LLM tokens, metered services, and cloud infrastructure waste money, and where one bug or abuser could run up the bill. Every dollar figure shows its math and a cited live price. |
| `/promo-reel` | **Motion designer** | Turns your real app into a short promo video: a social ad, an App Store or Play preview, or a landing-page loop. Uses real screens and real copy, and never shows a feature or stat the app doesn't have. |
| `/tej` | **Front desk** | Routes a vague or voice-dictated request ("run tay stack on this") to the right skill. |

In Codex, invoke a skill with `$` instead of `/`, for example `$walkie-talkie`.

### Which skill should I use?

| You want to know... | Use |
| --- | --- |
| Does this finished feature actually work for everyone who touches it? | `/walkie-talkie` |
| What happened, and why? | `/trace-failure` |
| Is this code repeating itself, or abstracted too early? | `/abstraction-police` |
| Why is this slow, and what fix actually pays off? | `/big-o-police` |
| Why doesn't AI search cite my site? | `/get-cited` |
| How does this code or idea work, step by step? | `/x-ray` |
| Where is my API or cloud bill going, and could it blow up? | `/cost-police` |
| Can I get a promo video of my app without hiring an editor? | `/promo-reel` |
| Not sure | `/tej` and describe it |

## The contract

Every Tej Stack skill follows the same four rules:

1. **Evidence first.** Each finding names its file and line, measurement, or source.
2. **Refutable.** Each finding names the check that would prove it wrong.
3. **Refuse what can't be verified.** "Not checked" is a valid answer. A guess dressed up as a finding is not.
4. **Read-only by default.** Skills report. They change code only when you ask.

### Works alongside gstack

Tej Stack is small on purpose. If you use [gstack](https://github.com/garrytan/gstack) for planning, review, and shipping, keep it. Tej Stack covers different ground: actor-by-actor feature audits, proven performance and cost wins, clickable code maps, AI search visibility, and promo videos built from your real app.

## Extra: speed-dial (optional, needs your own API key)

A separate Claude Code hook plugin. Save the commands you run all the time, then type a short prompt like "make the play store build" and the matching command starts in a new terminal window before the model runs. Matching is done by [Jev](https://typesafe.ai), TypeSafe's decision model, so it needs **your own `TYPESAFE_API_KEY`**. The Tej Stack skills do not need it.

<details>
<summary><b>Install and configure speed-dial</b></summary>

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

**Save commands** in `.claude/speed-dial.json` at a repo's root (commit it to share with your team), or in `~/.claude/speed-dial.json` for your own commands across every repo. If both files use the same id, the project entry wins. See [the example](plugins/speed-dial/examples/speed-dial.json).

| Field | Meaning |
| --- | --- |
| `id` | Lowercase letters, digits, `_` or `-`. Shown when it runs. |
| `description` | What Jev reads to decide. Say what the command does in words people would actually use. |
| `command` | A string, or `{ "windows", "macos", "linux" }`. It runs in PowerShell on Windows and bash elsewhere. |
| `cwd` | Folder to run in. Relative paths resolve from the current repo root. Default `.`. |
| `confirm` | `true` waits for Enter in the new window before running. Use it for deploys. |

**Trust.** A repo's `.claude/speed-dial.json` could label a destructive command as something harmless. So a project file stays off until you read it and type `speed-dial trust` in Claude Code. Any later edit switches it off again until you trust it again. Your own `~/.claude/speed-dial.json` is always on.

**What it will not do.**

- Prompts over 12 words, or starting with `/` or `!`, skip speed-dial and cost nothing.
- Unless both Jev answers reach 0.85 confidence, the prompt goes to Claude as usual.
- A missing key, a timeout, a network error, or a malformed file never blocks a prompt. It passes through.
- Jev sees only each entry's id and description, never the command, and can only pick from your list.
- Command output stays in its own window, out of Claude's context. If a command fails, paste the error into Claude.

</details>

## Updating

Each skill checks for a newer Tej Stack at most once a day: one 3-second request for this repo's `VERSION` file, cached in `~/.tej-stack/`. If there is an update, the skill says so in one line and keeps working. The check never blocks a task.

```text
/plugin update tej-stack@tej-stack
```

Direct installs update by re-running the installer with `--update` (Unix) or `-Update` (Windows). See [CHANGELOG.md](CHANGELOG.md) for what changed.

## Uninstall

```text
claude plugin uninstall tej-stack@tej-stack
claude plugin marketplace remove tej-stack
```

Direct installs: delete the skill folders the installer printed, under `~/.claude/skills/` or `~/.codex/skills/` (or `.claude/skills/` and `.agents/skills/` in a project).

## Contributing

Ideas for new founder workflows and focused fixes are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). A new skill needs one recognizable goal, a distinct trigger, a verifiable outcome, and evaluation cases under `evals/`.

If a skill saved you from a bad ship, a [star](https://github.com/varuntej07/tej-stack/stargazers) helps other founders find it.

## License

MIT. See [LICENSE](LICENSE).
