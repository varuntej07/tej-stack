# Walkie-Talkie

> Audit a completed feature as users, background workers, external systems, and future devices actually experience it.

Coding agents are good at proving that code compiles and tests pass. They still miss the real product when a button has no useful waiting state, a retry duplicates a payment, a background job finishes on the wrong device, an old client cannot read migrated data, or a user cannot recover after an interruption. Walkie-Talkie closes that gap by tracing implementation evidence all the way to the observable experience.

It audits **one completed feature at a time**. The result is a decision-ready release recommendation grounded in code, tests, runtime behavior, data flow, side effects, and recovery paths.

## Quick Install

Clone once, then install for one or both agents.

### Unix, macOS, or Linux

```sh
git clone --depth 1 https://github.com/varuntej07/walkie-talkie.git
cd walkie-talkie
./scripts/install.sh both --user
```

### Windows PowerShell

```powershell
git clone --depth 1 https://github.com/varuntej07/walkie-talkie.git
Set-Location walkie-talkie
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 both -Scope user
```

Restart or open a new agent session after installation. Invoke the skill with `$walkie-talkie` in Codex or `/walkie-talkie` in Claude Code.

## What it audits

Walkie-Talkie supports interactive UI, create/edit/delete flows, search and recommendations, uploads and downloads, authentication, permissions, payments, scheduled work, notifications, APIs, webhooks, integrations, offline sync, cross-device behavior, real-time media, hardware, AI or agent actions, migrations, and staged rollouts.

For composite features it traces the handoffs: user action to API, queue to worker, provider callback to reconciliation, notification to another device, or old schema to new client.

## What the audit returns

Every audit leads with one recommendation: **ready**, **ready with accepted risks**, **needs fixes**, or **blocked by unanswered decisions**. It then provides:

- the feature contract, actors, boundaries, and relevant feature categories
- primary and alternate actor-observable journeys
- workflow states, ownership, commit points, and testable invariants
- prioritized findings with evidence, reproduction, impact, root cause, and smallest safe correction
- human-in-the-loop product decisions when the evidence does not define material behavior
- a verification matrix that separates executed evidence from gaps
- ordered next actions based on user risk and dependencies

## Installation options

The installers copy only `skills/walkie-talkie`. They create parent directories, reject collisions with a different skill, and require an explicit update flag before replacing an existing `walkie-talkie` installation. They do not require administrator privileges or execute downloaded dependencies.

| Agent | Personal installation | Current-project installation | Invocation |
| --- | --- | --- | --- |
| Codex | `~/.agents/skills/walkie-talkie` | `.agents/skills/walkie-talkie` | `$walkie-talkie` |
| Claude Code | `~/.claude/skills/walkie-talkie` | `.claude/skills/walkie-talkie` | `/walkie-talkie` |

Personal installation makes the skill available across projects for the current user. Project installation keeps the skill in the current repository so a team can use the same version.

### Unix, macOS, or Linux

```sh
# Personal Codex installation
./scripts/install.sh codex --user

# Current-project Claude Code installation
./scripts/install.sh claude --project

# Install for both agents, or explicitly update the same installed skill
./scripts/install.sh both --user
./scripts/install.sh both --user --update
```

### Windows PowerShell

```powershell
# Personal Codex installation
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 codex -Scope user

# Current-project Claude Code installation
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 claude -Scope project

# Install for both agents, or explicitly update the same installed skill
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 both -Scope user
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 both -Scope user -Update
```

## Using the skill

Give the agent a completed feature, its intended behavior, and access to the implementation and safe verification commands. The skill will inspect evidence before asking product questions.

### Codex

```text
$walkie-talkie Audit the completed offline photo annotation feature. Inspect the implementation and tests, exercise safe flows, and tell me whether it is ready to ship.
```

### Claude Code

```text
/walkie-talkie Audit the scheduled reminder feature across web, iOS, and Android, including timezone changes, duplicate delivery, and recovery after reconnect.
```

## Examples

1. [Interactive feature](examples/interactive-feature.md): audit a mobile and desktop offline photo annotation workflow, including focus, autosave, conflict handling, accessibility, and process death.
2. [Background notification](examples/background-notification.md): audit a scheduled cross-device medication reminder across timezones, quiet hours, offline devices, deduplication, and opt-out.
3. [Transactional workflow](examples/transactional-workflow.md): audit a Stripe-style purchase flow across checkout, webhooks, retries, fulfillment, refunds, and irreversible side effects.

## What it does not do

Walkie-Talkie is not a generic pre-build planning checklist, a substitute for product requirements, or proof that production works without current evidence. It does not invent consent, retention, fallback, destructive-action, destination, or cross-user data policies. It does not automatically modify production systems or approve a release; it produces an evidence-based recommendation and identifies the smallest safe next steps.

## Evaluations

[`evals/test-cases.md`](evals/test-cases.md) contains activation, evidence, HITL, concurrency, offline, accessibility, privacy, migration, rollback, and false-confidence cases for maintainers and agent-skill evaluators.

## Contributing

Issues and focused pull requests are welcome. Keep the core skill concise, preserve evidence-first behavior, add or update an evaluation when changing audit behavior, and test both installers when changing packaging.

## License

Released under the [MIT License](LICENSE).
