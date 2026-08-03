# Walkie-Talkie

> “The tests pass” is not the same as “the feature works for people.”

Coding agents are excellent at proving that code compiles, a handler returns 200, and a test suite is green. They still miss the product at the seams: the button that gives no useful waiting state, the retry that charges twice, the reminder that fires on two devices, the webhook that arrives after cancellation, the migration that strands an old client, or the failure that leaves a user with nowhere to go.

**Walkie-Talkie is the last-mile audit for completed features.** It reconstructs one feature as every affected person, device, worker, and external system experiences it, then follows the evidence from entry point to durable outcome and recovery.

It does not grade your checklist. It tells you whether the feature is ready.

**Who this is for:**

- **Builders using coding agents** who want more than “implementation complete”
- **Founders and product engineers** making ship decisions with limited QA bandwidth
- **Staff engineers and reviewers** auditing cross-service, asynchronous, or irreversible workflows
- **Teams shipping mobile, desktop, web, API, payment, notification, sync, or AI features**

## Quick start

1. Open Claude Code in the repository that contains your completed feature.
2. Paste the prompt below.
3. Let Claude install Walkie-Talkie, choose the strongest audit target, inspect the implementation, and run safe checks.
4. Read the verdict: **ready**, **ready with accepted risks**, **needs fixes**, or **blocked by unanswered decisions**.
5. Fix the highest-risk finding, then run <code>/walkie-talkie</code> again.

No path choices. No checklist assembly. No pretending that test presence is test evidence.

## Install — Claude does it

Open Claude Code in your project and paste this. Claude handles setup and starts the first audit.

> Install Walkie-Talkie from **https://github.com/varuntej07/walkie-talkie** for Claude Code at user scope, then use it now. Work autonomously: clone the repository into a new temporary directory; verify that <code>skills/walkie-talkie/SKILL.md</code> has frontmatter <code>name: walkie-talkie</code>; detect the operating system; on Unix/macOS/Linux run <code>./scripts/install.sh claude --user</code>, and on Windows run <code>powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 claude -Scope user</code>. If the same skill is already installed, use the installer’s explicit update option; if a different skill occupies the destination, leave it untouched and explain the collision. Verify the installed <code>SKILL.md</code>, <code>agents/openai.yaml</code>, and <code>assets/icon.svg</code>, then remove the temporary clone. Read the installed <code>SKILL.md</code> and audit one completed feature in the current repository. Infer the best target from the current diff and recent commits; ask only if multiple choices would materially change the result. Inspect code, tests, data flow, side effects, and recovery paths; run safe relevant checks; separate observed evidence from gaps; and finish with a release recommendation and ordered fixes. Do not stop after installation or planning.

Future Claude Code sessions expose the skill as:

~~~text
/walkie-talkie
~~~

Using Codex instead? Install once, then invoke:

~~~text
$walkie-talkie
~~~

## See it work

~~~text
You:    Install Walkie-Talkie from github.com/varuntej07/walkie-talkie
        and audit the feature I just finished. Do the setup and checks yourself.

Claude: Installed for Claude Code.
        Auditing the scheduled cross-device reminder from the current branch.

        Actors: scheduler, account owner, iOS device, Android device,
                push providers, local fallback, future offline device

        [traces schedule -> queue -> push -> local fallback -> dismissal sync]
        [runs contract and integration tests]
        [reproduces server push + local fallback arriving together]

        VERDICT: NEEDS FIXES

        P0 — Duplicate user-visible reminder
        Evidence: both delivery paths commit independently; no occurrence-level
                  deduplication key exists at the notification boundary.
        Impact: the user can receive two medication reminders for one occurrence.
        Smallest safe fix: persist and claim reminder_occurrence_id before display,
                           then add a concurrent-delivery integration test.

        Verified: timezone conversion, permission denial, single-device dismissal
        Not verified: old-client replay after 24+ hours offline
~~~

The valuable part is not the long report. It is the moment an apparently finished feature becomes a concrete ship decision.

## How the audit flows

Walkie-Talkie works from observable experience back into implementation evidence, then forward again through failure and recovery.

~~~text
[You: one completed feature]
             |
             v
[Claude/Codex + Walkie-Talkie]
             |
             +---- establish contract ----> intent, actors, authority, success, prohibited behavior
             |
             +---- inspect boundaries ----> UI/API -> jobs/queues -> stores -> providers -> other devices
             |
             +---- collect evidence ------> code + schemas + tests + runtime + logs + screenshots
             |
             v
[Journey and state model]
  discovery -> active -> waiting -> commit -> durable outcome -> retry/recovery
             |
             +---- challenge seams -------> duplicates, ordering, offline, cancellation,
             |                              accessibility, privacy, migration, rollback
             |
             v
[Decision-ready audit]
  verdict + experienced journeys + invariants + prioritized findings
  + HITL decisions + verification matrix + smallest safe next actions
~~~

The skill never assumes two implemented components are correctly connected. Every important claim must point to code, an executed test, observed runtime behavior, or an explicit evidence gap.

## What it audits

Walkie-Talkie selects only the categories that apply to the feature.

| Feature category | What it follows |
| --- | --- |
| Interactive UI | discovery, focus, feedback, navigation, cancellation, accessibility |
| Create/edit/delete | validation, drafts, conflicts, undo, persistence, destructive confirmation |
| Upload/download/import/export | limits, progress, interruption, partial failure, integrity, cleanup |
| Auth/permission/payment | denial, expiry, reauthentication, revocation, duplicate side effects |
| Background/scheduled work | trigger accuracy, delays, stale work, quiet periods, deduplication |
| Notifications/proactive actions | relevance, destination, timing, frequency, dismissal, opt-out |
| APIs/webhooks/integrations | contracts, idempotency, retries, rate limits, ordering, reconciliation |
| Offline/sync/cross-device | source of truth, clock skew, merge conflicts, replay, reconnect |
| Real-time/media/hardware | startup, latency, buffering, interruption, device changes, cleanup |
| AI/agent actions | grounding, uncertainty, permissions, confirmations, rollback, audit trail |
| Migration/rollout | old data, mixed versions, flags, partial rollout, rollback compatibility |

Composite features are the point. A checkout is not one endpoint; it is a buyer, browser, payment provider, webhook, order record, inventory claim, seller notification, fulfillment action, refund path, and support story.

## What you get

Every audit leads with one recommendation:

| Verdict | Meaning |
| --- | --- |
| **Ready** | Relevant journeys and invariants have current evidence; no release-blocking gap remains |
| **Ready with accepted risks** | Known, bounded risks are explicit and have an owner or monitoring path |
| **Needs fixes** | A confirmed defect, requirement mismatch, or unsafe gap can harm the experience |
| **Blocked by unanswered decisions** | Material product policy is undefined and must not be invented by the agent |

The report then gives you:

- the feature contract, actors, boundaries, and success definition
- primary and materially different alternate journeys
- state owners, legal transitions, commit points, and testable invariants
- prioritized findings with evidence, reproduction, user impact, root cause, and smallest correction
- human-in-the-loop decisions only where product intent materially changes the outcome
- a verification matrix that distinguishes executed evidence from untested paths
- next actions ordered by user risk and dependency

## Three very different examples

| Feature | Hidden seams the audit follows | Example |
| --- | --- | --- |
| Desktop/mobile photo annotation | autosave, process death, stale revisions, offline sync, keyboard/touch/screen reader | [Interactive feature](examples/interactive-feature.md) |
| Cross-device medication reminder | timezone travel, quiet hours, push/local duplication, dismissal sync, lock-screen privacy | [Background notification](examples/background-notification.md) |
| Stripe-style checkout and fulfillment | concurrent submits, webhook ordering, inventory claims, refunds, irreversible effects | [Transactional workflow](examples/transactional-workflow.md) |

## Safe installation and updates

The installers copy only the distributable <code>skills/walkie-talkie</code> folder. They do not require administrator privileges, download dependencies, run unrelated code, or silently replace an existing directory.

~~~text
[Requested destination]
          |
          +-- absent ----------------> stage copy -> validate -> rename into place -> installed
          |
          +-- same skill, no update -> stop nonzero -> print exact explicit-update command
          |
          +-- same skill + update ---> stage new copy -> move old copy to backup
          |                                  |
          |                                  +-- swap succeeds -> remove backup -> installed
          |                                  |
          |                                  +-- swap fails ----> restore backup -> fail nonzero
          |
          +-- different/invalid skill -> stop nonzero -> leave destination untouched
~~~

Collision checks read the YAML frontmatter, not a matching phrase somewhere in the file. Paths with spaces are supported.

### Personal or project installation

| Agent | Personal installation | Current-project installation | Invoke |
| --- | --- | --- | --- |
| Claude Code | <code>~/.claude/skills/walkie-talkie</code> | <code>.claude/skills/walkie-talkie</code> | <code>/walkie-talkie</code> |
| Codex | <code>~/.agents/skills/walkie-talkie</code> | <code>.agents/skills/walkie-talkie</code> | <code>$walkie-talkie</code> |

Personal installation follows you across projects. Project installation pins the skill inside one repository for teammates and automation.

### Manual install — Unix, macOS, or Linux

~~~sh
git clone --depth 1 https://github.com/varuntej07/walkie-talkie.git
cd walkie-talkie

# Choose claude, codex, or both. Choose --user or --project.
./scripts/install.sh both --user
~~~

### Manual install — Windows PowerShell

~~~powershell
git clone --depth 1 https://github.com/varuntej07/walkie-talkie.git
Set-Location walkie-talkie

# Choose claude, codex, or both. Choose user or project.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 both -Scope user
~~~

### Upgrade safely

Let Claude do it:

> Upgrade my installed Walkie-Talkie skill from **https://github.com/varuntej07/walkie-talkie**. Clone the latest <code>main</code> branch into a temporary directory, verify both source and destination have frontmatter <code>name: walkie-talkie</code>, run the correct installer for my operating system with its explicit update option, validate the installed files, remove the temporary clone, and report the installed commit. Never overwrite a different skill.

Or run the explicit update yourself:

~~~sh
./scripts/install.sh both --user --update
~~~

~~~powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 both -Scope user -Update
~~~

## Using Walkie-Talkie

The best prompt names the completed feature and any non-negotiable product boundary. The skill discovers the rest from the repository.

~~~text
/walkie-talkie Audit the scheduled reminder feature across web, iOS, and Android.
Include timezone changes, duplicate delivery, offline recovery, and lock-screen privacy.
~~~

~~~text
$walkie-talkie Audit the completed checkout-to-fulfillment workflow.
Treat at-most-one charge and at-most-one fulfillment as hard invariants.
~~~

Do not know which feature to pick? Say:

~~~text
/walkie-talkie Find the most recently completed user-facing feature in this repository
and audit it. Infer the target from the current branch, recent commits, and tests.
Ask only if multiple candidates would materially change the result.
~~~

## What it does not do

Walkie-Talkie is not:

- a pre-build product ideation framework
- a generic checklist detached from the implementation
- proof of production behavior without current runtime evidence
- permission to mutate production systems or perform irreversible actions
- permission to invent consent, retention, fallback, destructive-action, destination, or cross-user policy
- a replacement for accessibility, security, privacy, or domain experts when the feature requires them

It can recommend a fix. It does not silently make a materially different product decision for you.

## Privacy and permissions

- The skill adds no telemetry, analytics, background service, network client, or account.
- The installers only copy local files from this repository into the selected skill directory.
- Audits run through your coding agent and inherit that agent’s provider, workspace, sandbox, and approval policies.
- Safe read-only inspection is the default. Runtime checks and mutations still require the authority available in the active session.
- Findings should identify sensitive-data exposure without reproducing secrets or private user data.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| Claude does not show <code>/walkie-talkie</code> | Start a fresh Claude Code session; the installed skill is already in <code>~/.claude/skills/walkie-talkie</code> |
| Codex does not show <code>$walkie-talkie</code> | Start a fresh Codex session and confirm <code>~/.agents/skills/walkie-talkie/SKILL.md</code> exists |
| Installer says the skill already exists | Rerun only with <code>--update</code> or <code>-Update</code> after confirming it is the same skill |
| Installer reports a different installation | Leave it untouched; inspect that destination and choose which skill should own the name |
| Windows blocks PowerShell scripts | Use the documented per-process <code>-ExecutionPolicy Bypass</code> command; it does not change system policy |
| Audit says evidence is missing | Provide the closest runnable integration environment, logs, trace, or test seam; do not downgrade the gap to a guess |

## Evaluations

[<code>evals/test-cases.md</code>](evals/test-cases.md) covers correct and incorrect activation, missing evidence, HITL decisions, concurrency, duplicate side effects, offline and cross-device behavior, accessibility, privacy, migration, rollback, and false-confidence prevention.

## Contributing

Issues and focused pull requests are welcome. Preserve the evidence-first behavior, keep the core skill concise, add or update an evaluation when changing audit behavior, and test both installers when changing packaging.

## License

MIT. See [LICENSE](LICENSE).
