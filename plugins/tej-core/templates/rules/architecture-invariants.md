# Architecture invariants

Hard constraints for this codebase: correctness and product stances that plans and edits have
been rejected over. Treat them as constraints, not defaults to re-litigate. Each entry: the rule
in one bold line, then one line on why (ideally the incident that taught it).

## Defaults tej-core starts every repo with

- **No feature flags.** Shipping the code is turning it on. No `*_ENABLED` booleans or kill
  switches; if cost or risk needs bounding, say so and let the user decide.
- **No keyword matching on user intent.** Never decide what a user meant with a word list,
  substring or regex over their text. Gate on a structural fact or let a model judge it.
- **Secrets stay server-side.** No feature may need a provider key in a client or a user's own key.
- **One choke point per side** for outbound HTTP and for model calls, so tracing, timeouts and
  fallbacks live in one place.

## This repo

<Add rules as you learn them. /tej-core:compound appends here when a failure teaches one.>
