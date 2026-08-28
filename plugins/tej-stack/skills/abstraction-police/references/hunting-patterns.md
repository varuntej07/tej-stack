# Hunting patterns

Concrete fingerprints for the concept sweep. Load only the sections that match the codebase's stack. Each pattern names the search that surfaces candidates and the drift that makes a candidate severity A.

## String contracts across a boundary

The highest-value category. Any place one side emits, publishes, or routes by a string literal and another side listens, subscribes, or matches on the same literal: IPC or WebView bridge events, message-bus topics, WebSocket message types, analytics event names, feature-flag keys, storage keys, route names.

- Search: every emit-like call for its literals, every listen-like call for its literals, then diff the two sets.
- Severity A signs: a name listened for but never emitted (dead listener), emitted but never handled (dead contract), or near-miss pairs one typo apart.
- Even with zero drift, count the unprotected surface: literals typed by hand on both sides with no shared constants module fail silently on the first rename.

## Copied security or durability code

Crypto wrappers, key management, atomic file writes (tmp-then-rename), transaction helpers, permission checks. A copied security implementation misses the hardening its original later receives: compare open flags, fsync calls, rename semantics, nonce and AAD handling line by line.

- Search: the platform primitives (encrypt, rename, fsync, chmod, begin/commit) and cluster call sites by shape.
- Severity A signs: one copy uses a safer variant (create-new versus truncate, write-through versus plain rename, versioned versus unversioned associated data) that the others never received.
- Frozen formats: never suggest changing a serialized grammar existing stored data decrypts or parses under; suggest freezing it in place with a named constant and pointing new code at the hardened variant.

## Subscription and lifecycle plumbing

Event listener effects, observer registration, interval and timer setup, connection open/close. The recurring bug: an async subscribe whose unsubscribe handle is assigned in a callback, so teardown that wins the race leaks the subscription forever.

- Search: the subscribe call, then classify each site's cleanup idiom; three coexisting idioms for one operation is the finding even before any leak.
- Fix shape: one hook or helper owning the disposed-guard and subscribe-before-load ordering; call sites become one-liners.

## Hand-synced type mirrors and constants

A struct or schema on one side and a hand-written interface on the other; a size, timeout, or geometry constant that must agree across languages or between code and stylesheets.

- Search: field-by-field comparison of every mirror pair; grep the literal numbers.
- Severity A signs: field sets that already disagree, or an enum variant added on one side that renders as undefined on the other.
- When generation is not worth adding yet, the zero-cost floor is bidirectional anchor comments: each side names its twin file so a future editor finds the pair.

## Fetch, retry, and timeout ceremony

AbortController-plus-timer wrappers, retry loops, backoff, response-to-JSON helpers, error mapping. Drift shows up as inconsistent abort semantics: one caller maps timeouts to a typed error, another leaks a raw exception, a third swallows it.

- Search: the controller or timer primitives around network calls.
- Do not flag controllers used for cancellation or teardown rather than deadlines; same primitive, different concept.

## Formatters and small display helpers

Relative-time, duration, currency, truncation helpers re-implemented per page. Drift is user-visible: two rows for the same timestamp disagreeing by a minute because one copy rounds and the other floors.

- Fix shape: one home module; keep genuinely distinct styles as separately named helpers in that home rather than forcing one style.

## Over-abstraction (the inverse sweep)

- A module with zero importers (verify with a repo-wide search for its name before flagging; then recommend annotate-or-delete as a user decision, since it may be a planned feature's stub).
- An interface or trait with one implementation plus test fakes only.
- Registered handlers, commands, or routes nothing invokes.
- Fast-growing codebases usually under-abstract rather than over-abstract; an empty inverse sweep is itself a useful reported result.

## Accidental utility gravity

Watch for one feature module becoming the de facto util crate: unrelated code importing a meeting module's clock, a vocabulary module doubling as the crypto provider. The fix is a named neutral home, not more feature-to-feature imports.
