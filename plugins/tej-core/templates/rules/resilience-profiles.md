# Resilience profiles

Every network or model call belongs to exactly one profile. Name it in every spec, plan and PR.
Real per-subsystem behavior is in each `.context/1-docs/ARCH-*.md` section 4.

## FastFail

For live turns a person is waiting on (voice, typing assist, interactive UI round trips).
Paths: <none yet; list globs, and mirror them as `fastfail_path_regex` in `.context/tej-core.json`
so the Stop hook enforces it>.

1. **Zero retries on the live path.** No retry loop, no backoff, no re-asking a provider already
   known to be slow while the user waits.
2. **Strict first-byte deadline, instant fallback** to another provider in the same turn.
3. **Fail open on capture.** Never drop the user's input because a provider is down.
4. **Degrade to the plain result.** The user always gets something correct, never a stall.

| Shape | Allowed? |
|---|---|
| Retry or backoff inside one live turn | No |
| A user-pressed "Retry" (a new turn the user asked for) | Yes |
| A durable background queue that survives restarts | Yes; mark the line `fastfail-exempt: durable queue` |
| Reopening a stalled device or socket | Yes; mark `fastfail-exempt: device recovery` |

## Resilient

For background, agent and request/response work. Paths: <list globs>.

1. **Bounded retries (1 to 2) with exponential backoff plus jitter** on transient failures only
   (429, 5xx, connection reset, read timeout). Honour `Retry-After`.
2. **Fail fast on deterministic errors:** 4xx, auth, validation, content policy, truncated output
   (a truncation hops to the next model, never retries the same one).
3. **Fallback chain**, and a fallback that changes price or capability logs the hop.
4. **Cancellation propagates.** A user stop cancels every in-flight call; never swallow it.
5. **Agent loops stop on progress, never on a clock.** Retries never count as progress.
6. **Every failure carries its cause** to the client.

## Both profiles

- Every `except` or `catch` names what it catches and keeps the cause. Silent catches are
  rejected by the Stop hook.
- Timeouts are explicit at every boundary; no call waits unbounded.
