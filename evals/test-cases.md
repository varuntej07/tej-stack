# Walkie-Talkie evaluation cases

Use these cases to evaluate triggering, audit depth, evidence discipline, and product judgment. Run them against a small fixture repository when possible; do not give the agent the expected findings.

## Scoring dimensions

- **Activation:** invokes the skill for a completed-feature experience audit and avoids unrelated work.
- **Evidence:** binds claims to code, tests, runtime observations, or explicit gaps.
- **Journey completeness:** covers every materially affected actor and asynchronous handoff.
- **State rigor:** derives legal transitions, ownership, commit points, and testable invariants.
- **Judgment:** prioritizes user risk, asks only material HITL questions, and avoids invented policy.
- **Confidence calibration:** never turns unexecuted tests, mocks, or absent evidence into a release claim.

## Cases

### 1. Correct activation: completed interactive feature

**Prompt:** “We finished drag-and-drop folder upload in the desktop app. Audit the actual experience, including progress, cancel, resume, process exit, duplicate files, keyboard access, and server cleanup. Is it ready?”

**Expected:** Trigger. Classify interactive UI plus upload/sync. Inspect implementation and run safe checks. Return the decision-ready audit structure with evidence.

### 2. Correct activation: composite transactional feature

**Prompt:** “The subscription upgrade flow is built. Walk every customer, billing, webhook, entitlement, email, and support path and look for duplicate side effects.”

**Expected:** Trigger. Model asynchronous actors and enforce invariants such as at most one charge and one entitlement transition per operation ID.

### 3. Should not trigger: pre-build ideation

**Prompt:** “Brainstorm ten social features for a gardening app.”

**Expected:** Do not trigger. No completed feature or request for evidence-based experience validation exists.

### 4. Should not trigger: isolated syntax fix

**Prompt:** “Fix the TypeScript type error in `parseDate` and run its unit test.”

**Expected:** Do not trigger unless the user separately asks for a completed-feature audit.

### 5. Missing implementation evidence

**Fixture:** A README claims offline sync works, but the repository contains only UI mocks and unit tests for serialization.

**Prompt:** “Audit the completed offline notes sync feature and approve it for release.”

**Expected:** Trigger. Refuse to infer server, reconnect, conflict, or durable persistence behavior. Recommend “needs fixes” or “blocked” as evidence warrants, and identify the smallest missing integration seams.

### 6. Undefined product decision requiring HITL

**Fixture:** A scheduled reminder stores local time and timezone, but no requirement defines whether it follows the traveler or stays tied to the original timezone.

**Prompt:** “Audit timezone behavior for the finished reminder feature.”

**Expected:** Inspect evidence first, then ask one decision-ready question with a recommended default, alternatives, consequences, and whether the rest of the audit can continue. Do not invent travel policy.

### 7. Concurrency and duplicate side effects

**Fixture:** Two checkout requests can create different provider idempotency keys, and webhook handling checks for an order before inserting without a database uniqueness constraint.

**Prompt:** “Audit checkout retries and webhook delivery under concurrency.”

**Expected:** Identify the race and possible duplicate charge or fulfillment. Cite the code and missing invariant, describe a reproducible interleaving, and propose the smallest safe transactional correction and tests.

### 8. Offline and cross-device behavior

**Fixture:** Device A dismisses a notification offline while Device B snoozes it online. Events use client timestamps and replay after reconnect.

**Prompt:** “Audit cross-device dismissal, snooze, and reconnect.”

**Expected:** Derive source-of-truth and ordering rules, address clock skew and replay, describe what each device shows, and expose any undefined conflict policy.

### 9. Accessibility and privacy

**Fixture:** A modal supports mouse clicks but lacks focus management; notification payloads contain a sensitive message body used on the lock screen and in analytics.

**Prompt:** “Audit the completed secure-message notification and settings experience.”

**Expected:** Cover keyboard and screen-reader recovery paths, lock-screen disclosure, telemetry boundaries, consent and opt-out, retention, and wrong-recipient behavior. Treat stated privacy boundaries as requirements.

### 10. Migration and rollback

**Fixture:** A new client writes schema v3, an old client reads only v2, and rollback code redeploys the old server without down-conversion.

**Prompt:** “Audit the shipped migration during partial rollout and rollback.”

**Expected:** Model mixed clients and servers, old data, irreversible writes, feature flags, rollback checkpoints, and recovery. Do not treat a successful forward migration test as rollback evidence.

### 11. False confidence prevention

**Fixture:** End-to-end tests exist but are skipped in CI; provider callbacks are mocked; no test or trace covers timeout after an external commit.

**Prompt:** “All tests are green. Confirm the payment feature is production-ready.”

**Expected:** Check whether tests actually ran and what they cover. Label mocks, skipped tests, and unobserved provider behavior. Do not return “ready” solely because test files exist or a summary says green.

### 12. Relevant checks without Cartesian explosion

**Fixture:** A local-only command palette has no network, background, payment, migration, or multi-device behavior.

**Prompt:** “Audit the completed command palette for release.”

**Expected:** Trigger, but focus on discoverability, focus, keyboard, screen reader, cancellation, state cleanup, latency, and error feedback. Do not pad the result with irrelevant webhook or payment checks.

## Failure signals

The evaluation fails if the agent returns a generic checklist, reports implementation assumptions as observations, ignores a material actor or commit boundary, invents policy, treats test presence as execution, recommends release despite an unbounded irreversible side effect, or buries high-risk findings beneath low-impact polish.
