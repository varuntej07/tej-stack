# Tej Core

[![Validate](https://github.com/varuntej07/tej-stack/actions/workflows/validate.yml/badge.svg)](https://github.com/varuntej07/tej-stack/actions/workflows/validate.yml)
[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fvaruntej07%2Ftej-stack%2Fmain%2Fplugins%2Ftej-core%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/varuntej07/tej-stack?style=social)](https://github.com/varuntej07/tej-stack/stargazers)

Tej Core is a harness for Claude Code and Codex that follows you into every repo you open. Install it once on your machine. From then on your agent explains a plan the way you would explain it to a cofounder before it writes a line, explains a bug before it touches the code, fixes the whole class of a bug instead of the one example you pasted, and only says "fixed" once it has watched the symptom disappear. A read-only evaluator gates every feature and bugfix, and a set of living architecture docs means the agent still knows how your system works next month.

I built this because I ship apps alone with Claude Code and Codex, and every new session started from zero. It forgot how I like plans explained, it jumped straight to code, it called a bug fixed because the build passed, and a week later it had no idea how the system fit together. I kept pasting the same rules into every project's CLAUDE.md. Tej Core is those rules, the loop that enforces them, and the docs that remember, as one plugin. All Markdown and bash, MIT, no account, no telemetry.

**Who this is for**

- Solo founders and small teams who build with Claude Code or Codex every day
- Anyone tired of the agent rushing into code before it understands the problem
- Anyone who has been told "fixed" and then found the bug still there

Two more things live in this marketplace: nine [evidence-first audit skills](docs/skills.md) (feature audits, failure traces, cost and performance hunts, code maps, promo videos) and [speed-dial](docs/speed-dial.md), a hook that runs your saved commands from a short prompt. Both install separately. The rest of this page is about Tej Core.

## See it work

A fresh clone of [expressjs/express](https://github.com/expressjs/express), no `CLAUDE.md`, no setup. This is the real output from 2026-11-19 at commit `43fca52`, trimmed for length. Nothing below was typed by hand.

```text
You:    /tej-core:init

Claude: What I found: this is a clone of Express 5.3.0, a single-package library
        with no services or workers. Everything in lib/ runs inside a live HTTP
        request, so the whole source tree is a FastFail path and there is no
        Resilient path at all. Routing, body parsing and file streaming live in
        upstream packages, and Express is the glue around them. I traced one real
        request through the hello-world example end to end, then split the code
        into four subsystems along its real seams: application (factory, settings,
        mounting, dispatch), request, response, and views. Each has an ARCH doc
        with file:line from the files I opened, budgets marked unmeasured because
        the repo has no benchmark, and a resilience table built from the actual
        throw and next(err) sites.

        Files written
        - CLAUDE.md (router: product paragraph, canonical paths, subsystem table, invariants)
        - AGENTS.md
        - .context/1-docs/ARCH-application.md, ARCH-request.md, ARCH-response.md, ARCH-views.md
        - .context/2-specs/_TEMPLATE-feature.md, _TEMPLATE-bugfix.md, IN-FLIGHT-AUDIT.md

        Five doc-versus-code drifts are recorded under Open in IN-FLIGHT-AUDIT.md,
        all stale upstream comments. The one worth knowing is the res.sendFile doc
        example that still shows the removed two-argument res.send(403, ...) form.

        Nothing is committed.
```

Part of the `CLAUDE.md` it wrote. Every claim carries the line it came from, so the next session can check instead of trust:

```text
## Invariants seen in the code

- Only LICENSE, Readme.md, index.js and lib/ are published (package.json:85-90).
  Nothing under test/ or examples/ may be required from lib/.
- A setting that needs a compiled form stores it under `<setting> fn` from inside
  app.set (lib/application.js:363-380). etag, query parser and trust proxy do this
  today. Readers such as req.query and req.ip only ever read the fn sibling.
- req and res prototypes are per-app objects (lib/express.js:45-52). app.handle
  swaps them in with Object.setPrototypeOf (lib/application.js:169-170) and a
  mounted app swaps the parent's back on exit (lib/application.js:230-237).
- Content-Length is never set when Transfer-Encoding is present (lib/response.js:180-184).
- Routing bugs belong in the router package. Express only proxies to it
  (lib/application.js:177, 190-258).
```

And one row from the audit it left behind, where the code and a comment disagree:

```text
| lib/response.js:367 (doc comment in res.sendFile) | Example uses res.send(403, 'Sorry! ...') |
| Express 5 removed the (status, body) form; res.send takes one argument
  (lib/response.js:126). The call would send the number 403 as the body with status 200. |
```

The four architecture docs, the router and the audit came to 688 lines. From then on, every session in that repo starts by reading the doc for the subsystem it is about to touch.

Then a question, in the same repo, the next session:

```text
You:    /tej-core:search when a handler calls res.send with a string, how does
        Express decide the ETag and whether to answer 304?

Claude: The ETag is a weak sha1 over the exact bytes about to be sent, and the
        304 is decided one line later by comparing that header with the
        request's If-None-Match.

        1. Pick the generator. res.send reads the app's compiled `etag fn` at
           line 162. The default setting is 'weak' (lib/application.js:95).
        2. Buffer the body. Because ETag is on, the string is copied into a
           Buffer at line 175 so the hash and Content-Length cover the same bytes.
        3. Check freshness. req.fresh (lib/request.js:469-486) returns true only
           when the method is GET, HEAD or QUERY, the status is 2xx or 304, and
           If-None-Match weakly matches the ETag just written.
        4. Flip to 304. Line 196 sets 304, lines 199 to 204 strip the entity
           headers and blank the body.

        Top three findings:
        - A 304 costs the same CPU as a 200. The full body is copied and hashed
          on the event loop before freshness is known, with no size cap. Only
          the socket write is saved.
        - The 304 decision ignores the etag setting. A hand-set ETag with ETag
          generation disabled still produces 304s. Pinned by
          test/res.send.js:504-517.
        - Doc drift. The ARCH doc init wrote says a short string costs one
          byteLength call, but under the default weak setting it always takes
          the Buffer.from copy. The doc also misses the 2xx gate.

        I did not open node_modules, so the etag and fresh internals are
        described from their published behaviour and this repo's tests.
```

It answered first, walked the path with line numbers, said what it did not read, and caught a mistake in the doc it had written an hour earlier. That last part is the point: the docs are checked against the code every time, not trusted.

## Install, about 30 seconds

**Requirements:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and `bash`. On Windows that is the Git for Windows bash Claude Code already uses. Nothing to build.

Paste this into any terminal (PowerShell, bash or zsh), then restart Claude Code:

```text
claude plugin marketplace add varuntej07/tej-stack; claude plugin marketplace update tej-stack; claude plugin install tej-core@tej-stack
```

It installs at user scope, so it is not tied to one project. If you already added the marketplace, the first command says so and the rest still run.

Then, in each repo you work on, run this once:

```text
/tej-core:init
```

It reads your code and writes a router `CLAUDE.md`, rules under `.claude/rules/`, one architecture doc per subsystem it can trace, and spec templates under `.context/`. If you already have a `CLAUDE.md`, it keeps every line, shows you the merge and waits for your OK. Nothing is committed.

**Codex.** Codex gets the skills and the rules, but not the hooks, because Codex does not run Claude Code hooks. `init` writes an `AGENTS.md` that carries the rules instead, and you call skills with `$` instead of `/`.

```text
codex plugin marketplace add varuntej07/tej-stack
codex plugin add tej-core@tej-stack
```

Start a new Codex conversation afterwards.

<details>
<summary>Other ways to install for Claude Code</summary>

Inside Claude Code, one at a time:

```text
/plugin marketplace add varuntej07/tej-stack
/plugin marketplace update tej-stack
/plugin install tej-core@tej-stack
/reload-plugins
```

Or paste this into Claude Code and let it do the work:

> Install Tej Core for me: run `claude plugin marketplace add varuntej07/tej-stack`, then `claude plugin marketplace update tej-stack`, then `claude plugin install tej-core@tej-stack`. When they succeed, tell me to restart Claude Code and run `/tej-core:init` in my repo.

</details>

## What changes

| What agents do today | What Tej Core makes them do instead |
| --- | --- |
| Jump straight into code | Open with the pain, how it works now, the idea, and why it should work, in plain first person. Then the diagrams, data flow, budgets and file:line. Then wait for your OK. |
| Fix the one example you pasted | Lay out every shape of the bug as a table, including the near misses where the fix must not fire, and fix the class. |
| Say "fixed" when it compiles | Say "fixed" only after the symptom is seen gone on the real surface. Otherwise say "unverified". |
| Try a third tweak of the same idea | After two failed fixes, attack the premise. |
| Swallow errors to make a test pass | Keep the cause. A silent `catch {}` or `except: pass` written this session blocks the turn. |
| Hide half-built work behind a flag | No feature flags. Shipping the code is turning it on. |
| Ship an edit nobody checked | Every source edit ends with a read-only evaluator PASS against a written spec. In a repo set up with `init`, the end-of-turn check blocks the turn until that happens. |
| Forget your system by next week | Read the architecture doc for a subsystem before editing it, and refresh the docs after every change. |

These apply in every repo from the first session, with no setup. The end-of-turn check and the architecture docs switch on in a repo once you run `init` there.

## The commands

| Command | What it does |
| --- | --- |
| `/tej-core:init` | Reads the repo and writes the router `CLAUDE.md`, rules, architecture docs, spec templates and config. Merges with an existing `CLAUDE.md` and shows you the diff first. |
| `/tej-core:feature` | Reads the docs and code, writes a spec (taxonomy with must-not-fire cases, ASCII diagram, data flow, latency budget, resilience matrix), **stops for your approval**, builds, then loops the evaluator until it passes. |
| `/tej-core:bugfix` | Evidence first, the full class of the bug, the explanation before any diff, a root-cause fix, the evaluator gate. |
| `/tej-core:search` | Read-only. The answer first, then the call graph, a latency and storage audit, resilience gaps, and where the docs have drifted from the code. |
| `/tej-core:pr` | Evaluator plus a duplication review, commit hygiene, and a PR description drafted to the scratchpad. Never pushes. |
| `/tej-core:release` | A pass or fail scorecard across every repo in scope. Asks before any build, tag, push or deploy. |
| `/tej-core:compound` | After a change: updates the architecture docs, turns new failure modes into rules, archives finished specs. |
| `/tej-core:spotlight` | SEO and AEO in one pass. Probes your live site the way Googlebot and GPTBot see it, ranks what keeps you out of Google and AI answers, plans the fixes, **stops for your approval**, then ships them with a freshness loop. `spotlight recheck` reruns it, and every session reminds you once when the monthly recheck is due. |
| `/tej-core:lag-doctor` | Finds every LLM call a person waits on, pulls p50, p95 and p99 from your production logs, splits the wait into stages, checks each against the provider's current docs, asks which wait bothers you, and writes a doc-backed plan that **stops for your approval**. `lag-doctor recheck` reruns the queries after the deploy. |
| `tej-core:evaluator` agent | A strict, read-only reviewer that returns PASSED or REJECTED with file:line reasons. The feature and bugfix loops call it until it passes. |

## How it works

```text
claude plugin install tej-core@tej-stack          once per machine, user scope
        │
        ▼
every session ──► SessionStart hook ──► the rules above
        │                          └──► your own rules, from ~/.claude/tej-core/rules.md
        │                          └──► repo set up? ──► repo map + active specs
        ▼
/tej-core:init ──► CLAUDE.md router · .claude/rules/ · .context/1-docs (ARCH docs)
                   .context/2-specs (templates) · .context/tej-core.json · AGENTS.md
        ▼
end of turn ──► Stop hook ──► only in set-up repos, only files this session edited
```

**Your own rules, everywhere.** Put anything you want every session to know in `~/.claude/tej-core/rules.md`: your shell, your commit style, words you never want used. The SessionStart hook loads it next to the Tej Core rules in every repo.

**Repo-specific steps** (test commands, evals, log locations, deploy targets) live in that repo's `.claude/rules/project-workflow.md`. `init` fills it from your manifests and CI, and the skills read it instead of guessing.

**The end-of-turn check** runs only in repos where you ran `init`, judges only files this session edited, never builds or runs tests, and never blocks twice in a row. It catches silent catches, new `*_ENABLED` flags, AI attribution trailers, retries on paths that should fail fast, specs marked done with unchecked boxes, and source edits that no evaluator PASS has covered since the last edit.

**Tej Core routes first.** Features go through `/tej-core:feature`, bugs through `/tej-core:bugfix`, questions through `/tej-core:search`, PRs and releases through their commands. Other skill packs still work; the rules use them for sub-steps inside a Tej Core flow (browser QA, diagnosis, design review) rather than instead of it.

If `bash` is missing, the hooks skip quietly. They never break a session.

## How it compares

**vs [gstack](https://github.com/garrytan/gstack).** gstack gives you a team of specialist reviewers you call on demand: CEO review, design review, QA in a real browser, a release engineer. Tej Core is the thing that is on all the time: how the agent explains, how it fixes, the spec gate, and the docs that persist. I run both. Tej Core's rules send feature, bug, search, PR and release work through its own loop and call gstack for sub-steps like browser QA. If you only want review and shipping, use gstack.

**vs [OpenSpec](https://github.com/Fission-AI/OpenSpec) and [Spec Kit](https://github.com/github/spec-kit).** Both are spec-driven workflows and both are good at the spec. Neither changes how the agent explains itself, neither has a read-only evaluator that rejects with file:line reasons, and neither carries a per-subsystem architecture doc that the agent has to read before editing. Tej Core's specs are plainer and its loop is stricter.

**vs nothing.** Pasting the same rules into every CLAUDE.md works until you forget one repo, or the rules drift, or the agent ignores them because nothing checks. Tej Core is one install, and the hook checks.

## When something goes wrong

**Claude cannot see `/tej-core:init`.** Restart Claude Code; plugins load at startup. Then run `claude plugin list` in a terminal and look for `tej-core@tej-stack` with status enabled. If it is missing, run the install line again.

**The rules did not show up at session start.** Type `/hooks` inside Claude Code and check that `tej-core` has a SessionStart hook. The hook runs `bash`, so on Windows make sure Git for Windows is installed, which Claude Code needs anyway.

**`plugin update` says you are current but a command is missing.** Run `claude plugin uninstall tej-core@tej-stack` and then `claude plugin install tej-core@tej-stack`. This happened once, in 0.10.0, and the validator now refuses a release without a version bump so it will not happen again.

**The end-of-turn check blocked a turn.** It prints exactly what it found and the file. Fix it, or tell the agent why the rule does not apply here and it will say so and finish. It never blocks the same turn twice.

**It says the evaluator has not passed.** Source files changed this session and no `tej-core:evaluator` PASS came after the last edit. The agent writes or names the spec under `.context/2-specs/`, runs the evaluator until PASSED, and records the spec path in `.context/4-scratchpad/.evaluator-passed`. The feature and bugfix commands do this on their own. Work that started in plain chat has to do it too.

**You want it off for one repo.** Delete that repo's `.context/tej-core.json`. The rules still load, but the check and the orientation stop.

**You want it off everywhere, without uninstalling.** `claude plugin disable tej-core@tej-stack`, and `enable` to turn it back on.

If none of that explains it, [open an issue](https://github.com/varuntej07/tej-stack/issues) with the output of `claude plugin list` and what the hook printed.

## Updating

From any terminal, then restart Claude Code:

```text
claude plugin marketplace update tej-stack; claude plugin update tej-core@tej-stack
```

Or inside Claude Code:

```text
/plugin marketplace update tej-stack
/plugin update tej-core@tej-stack
```

Codex has no update command. Refresh the marketplace, then add the plugin again and it reinstalls at the new version:

```text
codex plugin marketplace upgrade tej-stack
codex plugin add tej-core@tej-stack
```

What changed in each version is in [CHANGELOG.md](CHANGELOG.md).

## Uninstall

```text
claude plugin uninstall tej-core@tej-stack
claude plugin marketplace remove tej-stack
```

The files `init` wrote in your repos (`CLAUDE.md`, `.claude/rules/`, `.context/`) stay. They are plain Markdown and still useful on their own. Delete them by hand if you want them gone.

## Also here

- **[Tej Stack skills](docs/skills.md).** Nine audit skills for when you need a specialist: `/walkie-talkie` audits a finished feature through every user and actor, `/trace-failure` explains an error as a causal chain, `/big-o-police` and `/cost-police` find performance and billing wins and refuse the fake ones, `/x-ray` maps a flow into a clickable diagram, `/promo-reel` cuts an ad from your real app. Every finding comes with its evidence and the check that would prove it wrong.
- **[speed-dial](docs/speed-dial.md).** Type "make the play store build" and your saved command starts in a new window before the model runs. Needs your own TypeSafe key.

## Contributing

Focused fixes and new founder workflows are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). A new skill needs one recognizable goal, a distinct trigger, a verifiable outcome, and evaluation cases under `evals/`.

If Tej Core saved you from a bad ship, a [star](https://github.com/varuntej07/tej-stack/stargazers) helps other founders find it.

## License

MIT. See [LICENSE](LICENSE).
