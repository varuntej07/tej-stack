# Tej Stack skills

Nine audit skills you call when you need one. They live in the same marketplace as Tej Core and install separately. Each one reports with the file and line, the measurement, or the doc that backs every finding, names the check that would prove it wrong, and says "not checked" when it could not verify something. None of them change your code unless you ask.

## Install

Claude Code, from any terminal, then restart Claude Code:

```text
claude plugin marketplace add varuntej07/tej-stack; claude plugin install tej-stack@tej-stack
```

Or inside Claude Code:

```text
/plugin marketplace add varuntej07/tej-stack
/plugin install tej-stack@tej-stack
/reload-plugins
```

Codex:

```text
codex plugin marketplace add varuntej07/tej-stack
codex plugin add tej-stack@tej-stack
```

In Codex, call a skill with `$` instead of `/`, for example `$walkie-talkie`.

Any host that reads `~/.claude/skills` or `~/.codex/skills`:

```sh
git clone --depth 1 https://github.com/varuntej07/tej-stack.git
cd tej-stack
./scripts/install.sh both --user
```

```powershell
git clone --depth 1 https://github.com/varuntej07/tej-stack.git
Set-Location tej-stack
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 both -Scope user
```

Use `--project` (Unix) or `-Scope project` (Windows) to install into the current repo instead. The installers refuse to overwrite skills they did not install.

## The skills

| Skill | Think of it as | What it does |
| --- | --- | --- |
| `/walkie-talkie` | Product QA lead | Audits a finished feature through every affected user, actor and recovery path, with code or runtime evidence for each finding. |
| `/trace-failure` | Incident investigator | Explains a failure as a causal chain, from the person or system that started it to the impact users could see. |
| `/abstraction-police` | Codebase janitor | Finds near-duplicate abstractions, drifted copies and premature abstractions, and ranks which merges are worth doing. |
| `/big-o-police` | Performance engineer | Finds where a different data structure or algorithm measurably cuts time or memory, proves each win, and refuses the ones that do not pay. |
| `/get-cited` | AI search strategist | Audits a website for ChatGPT, Perplexity, Claude and Google AI answers, with a proof per finding, and refuses AEO myths. |
| `/x-ray` | Staff engineer at a whiteboard | Maps a file, repo flow or concept into a clickable block diagram. Each block shows its file, signature, inputs, outputs, config and docs. |
| `/cost-police` | CFO who reads code | Finds where LLM tokens, metered services and cloud infrastructure waste money, and where one bug or abuser could run up the bill. Every dollar figure shows its math and a cited live price. |
| `/promo-reel` | Motion designer | Turns your real app into a short promo video: a social ad, an App Store or Play preview, or a landing-page loop. Real screens, real copy, nothing the app cannot do. |
| `/tej` | Front desk | Routes a vague or voice-dictated request ("run tay stack on this") to the right skill. |

## Which one

| You want to know | Use |
| --- | --- |
| Does this finished feature work for everyone who touches it? | `/walkie-talkie` |
| What happened, and why? | `/trace-failure` |
| Is this code repeating itself, or abstracted too early? | `/abstraction-police` |
| Why is this slow, and what fix pays off? | `/big-o-police` |
| Why doesn't AI search cite my site? | `/get-cited` |
| How does this code or idea work, step by step? | `/x-ray` |
| Where is my API or cloud bill going, and could it blow up? | `/cost-police` |
| Can I get a promo video of my app without hiring an editor? | `/promo-reel` |
| Not sure | `/tej` and describe it |

## The contract

1. Evidence first. Each finding names its file and line, measurement, or source.
2. Refutable. Each finding names the check that would prove it wrong.
3. Refuse what cannot be verified. "Not checked" is a valid answer. A guess dressed up as a finding is not.
4. Read-only by default. Skills report. They change code only when you ask.

## What the output looks like

These are illustrations of the shape, not real runs. Your findings come from your own code.

```text
You:    /walkie-talkie the team invite flow is done. Is it ready?

Agent:  Actors: inviter, invitee (new account), invitee (existing account),
        workspace admin, email worker, expiry job.

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

```text
You:    /cost-police our Anthropic bill doubled after launch

Agent:  Prices fetched today from platform.claude.com/docs/en/about-claude/pricing.
        LEAK     The 6k-token system prompt in api/chat.ts:31 is resent
                 uncached on every turn. 9k turns/day x 6k tokens =
                 54M tokens/day. At $2/MTok input and $0.10/MTok cache
                 reads that is about $100/day, roughly $3,000/month.
                 Refute it: if cache_read_input_tokens > 0 on /chat, I'm wrong.
        RUNAWAY  POST /summarize calls the model with no login and no
                 per-user limit. One script could spend your whole budget.
        REFUSED  "Switch to the cheapest model." There is no quality eval
                 for this task, and fewer output tokens can make a bigger
                 model cheaper. I can set up an A/B run instead.
```

## Updating

```text
claude plugin marketplace update tej-stack; claude plugin update tej-stack@tej-stack
```

Codex has no update command. Run `codex plugin marketplace upgrade tej-stack`, then `codex plugin add tej-stack@tej-stack` again.

Direct installs: re-run the installer with `--update` (Unix) or `-Update` (Windows).

## Uninstall

```text
claude plugin uninstall tej-stack@tej-stack
```

Direct installs: delete the skill folders the installer printed, under `~/.claude/skills/` or `~/.codex/skills/` (or `.claude/skills/` and `.agents/skills/` in a project).
