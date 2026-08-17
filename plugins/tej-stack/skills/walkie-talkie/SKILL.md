---
name: walkie-talkie
description: Audit a completed product feature from the perspective of every affected user and actor, tracing the observable journey through actual code, runtime behavior, data, side effects, and recovery paths. Use after implementing a feature in any product layer, including UI, APIs, background jobs, notifications, authentication, permissions, payments, uploads, synchronization, real-time media, AI or agent actions, integrations, migrations, hardware, mobile, desktop, or web. Apply when validating UX completeness, production readiness, edge cases, lifecycle behavior, concurrency, failure recovery, accessibility, privacy, performance, compatibility, observability, or whether the built implementation matches the intended experience.
---

# Walkie-Talkie

Audit the feature as experienced, not merely as coded. Reconstruct how every actor enters, understands, uses, waits for, completes, abandons, retries, and recovers from it. Bind every conclusion to implementation or runtime evidence.

Default to post-build verification. Inspect and exercise the existing feature before proposing changes. Do not replace evidence with a generic checklist or assume that two implemented endpoints are correctly connected.

## 1. Establish the contract

Identify:

- primary user intent and definition of success
- affected actors, including end users, admins, recipients, external systems, background workers, and future sessions or devices
- entry points, triggers, prerequisites, permissions, entitlements, and supported environments
- user-visible and invisible outcomes, side effects, and prohibited behavior
- shared behavior versus platform-, role-, locale-, account-, or device-specific behavior

Read repository instructions, product requirements, implementation, tests, schemas, flags, telemetry, error handling, and relevant platform or provider contracts. When possible, run the product or its closest integration tests and observe actual behavior.

If intent and implementation conflict, report the conflict. Do not silently choose one.

## 2. Classify the feature

Select every applicable archetype and adapt the audit:

| Archetype | Emphasize |
| --- | --- |
| Interactive UI | discoverability, focus, feedback, navigation, accessibility, cancellation |
| Create/edit/delete | validation, drafts, conflicts, undo, persistence, destructive confirmation |
| Search/recommendation | loading, empty results, ranking, freshness, explanation, correction |
| Upload/download/import/export | size limits, progress, pause, partial failure, integrity, cleanup |
| Authentication/permission/payment | denial, expiry, reauthentication, duplicate charge/action, revocation |
| Background/scheduled work | trigger accuracy, delay, deduplication, quiet periods, stale work, visibility |
| Notification/proactive action | relevance, timing, destination, frequency, dismissal, opt-out |
| API/webhook/integration | contract compatibility, idempotency, retries, rate limits, ordering, reconciliation |
| Sync/offline/cross-device | source of truth, merge conflicts, clock skew, replay, reconnect, consistency |
| Real-time/media/hardware | startup, interruption, device changes, latency, buffering, resource release |
| AI/agent behavior | uncertainty, grounding, permissions, tool side effects, confirmation, rollback, audit trail |
| Migration/rollout | old data, mixed versions, flags, rollback, partial rollout, backward compatibility |

Do not force irrelevant checks. For a composite feature, trace the handoffs between archetypes.

## 3. Reconstruct journeys and workflow

Write the primary journey in actor-observable steps from discovery or trigger through durable outcome. Add alternate journeys for materially different roles, platforms, entry points, or asynchronous completion.

For every step record:

- actor action or triggering event
- preconditions and authority
- feedback before, during, and after work
- state before and after
- code path, event, boundary, and owner
- data read, created, mutated, cached, queued, persisted, synchronized, or deleted
- external or irreversible side effects
- latency target, deadline, timeout, cancellation, retry, and compensation behavior
- next available user action and anything that can block it
- evidence: file and symbol, test, log, trace, screenshot, reproduced behavior, or explicit gap

Represent non-linear features as a workflow graph rather than pretending they are one screen flow. Include multiple actors, delayed events, background completion, callbacks, notifications, restarts, and cross-device handoffs.

## 4. Define states and invariants

Derive explicit states and legal transitions from the implementation. Include only relevant states such as unavailable, initializing, ready, active, waiting, paused, partially complete, committing, synchronized, succeeded, canceled, expired, recoverable failure, terminal failure, and shutting down.

For each state verify:

- entry and exit conditions are unambiguous
- one component owns mutable state, or synchronization is explicit
- duplicate, missing, late, stale, and out-of-order events are safe
- repeated, simultaneous, and re-entrant actions cannot corrupt state or duplicate side effects
- cancellation and timeout work before, during, and after a commit boundary
- retries are bounded, idempotent where required, and use backoff appropriately
- queues, buffers, caches, histories, durations, and retries have bounds
- locks, I/O, network calls, rendering, model work, and callbacks do not block unrelated next actions
- resources, subscriptions, handles, temporary data, and UI state are cleaned up on every exit
- partial success can be detected, explained, reconciled, compensated, or safely resumed

State invariants must be testable. Prefer assertions such as “at most one charge per operation ID” over vague goals such as “avoid duplicate charges.”

## 5. Challenge the experience

Walk applicable variations without creating a meaningless Cartesian explosion:

- first use, returning use, and interrupted previous use
- empty, minimum, typical, maximum, malformed, stale, and adversarial input
- slow, unavailable, degraded, or inconsistent dependencies
- rapid repetition, overlap, navigation away, app backgrounding, sleep, restart, logout, and account switching
- offline, reconnect, multiple tabs/windows/devices, and old client versions
- permission denied, revoked, expired, or changed mid-operation
- low memory, low storage, battery constraints, device loss, and process termination where relevant
- screen reader, keyboard-only, scaling, reduced motion, localization, long text, and contrast where relevant
- sensitive data, secure contexts, wrong recipient/destination, retention, deletion, and auditability
- feature disabled, partially rolled out, rolled back, or receiving legacy data

At each variation ask: What does the actor see? What can they do next? What happened to their data? Can repeating the action make things worse? Can support or the owner determine what occurred?

## 6. Resolve product decisions with HITL

Inspect evidence before asking questions. Ask only when behavior is materially undefined and different answers change UX, privacy, safety, cost, data retention, compatibility, or architecture.

For each question provide:

1. the concrete scenario
2. the recommended default
3. viable alternatives
4. user and engineering consequences
5. whether other analysis can continue without the answer

Never invent fallback behavior, consent, retention, destructive action, destination selection, or cross-user data handling. Treat declared safety and privacy boundaries as hard requirements.

## 7. Verify the built feature

Derive verification from the workflow and invariants. Use the strongest available evidence:

1. deterministic unit or model-based state tests
2. component and contract tests
3. integration tests across real boundaries
4. end-to-end journeys on supported platforms
5. fault injection for timeouts, crashes, retries, ordering, and partial commits
6. performance, resource, load, and soak tests
7. accessibility, compatibility, security, privacy, and manual experience checks
8. production signals, including latency, failure reason, abandonment, retry, deduplication, and recovery

Run safe relevant checks when authorized. Do not claim a path works because a test exists, or claim verification without executing it or citing current runtime evidence. Label untestable paths and propose the smallest instrumentation or test seam needed.

## 8. Return a decision-ready audit

Lead with the release recommendation: ready, ready with accepted risks, needs fixes, or blocked by unanswered decisions.

Then provide:

1. **Feature contract:** actors, intent, success, boundaries, and archetypes.
2. **Experienced journeys:** primary and materially different alternate paths.
3. **Workflow and invariants:** states, handoffs, owners, commit points, and guarantees.
4. **Findings:** severity, classification, evidence, reproduction, user impact, root cause, and smallest safe correction.
5. **HITL decisions:** unresolved policy questions with recommended defaults.
6. **Verification matrix:** scenario, expected result, evidence or test level, coverage, and gap.
7. **Next actions:** ordered by user risk and dependency, with changes kept independently testable.

Separate confirmed defects, requirement mismatches, design risks, test gaps, observability gaps, and unanswered decisions. A long list is not rigor. Prioritize issues that can lose user work, perform the wrong side effect, expose data, trap the user, produce silent failure, or prevent recovery.
