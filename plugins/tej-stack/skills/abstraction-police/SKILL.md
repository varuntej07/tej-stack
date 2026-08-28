---
name: abstraction-police
description: Sweep a codebase for nearly-duplicated abstractions that should be unified and for premature abstractions that should be inlined, then report ranked findings with file and line evidence. Use for requests to find duplication, audit code health, review copy-pasted logic, check whether the same concept is implemented twice, find drifted constants or hand-synced contracts, decide whether code needs an abstraction, or clean up before or after fast feature growth. Apply when the user says code feels repetitive, asks what to refactor, asks whether two similar functions or components should be merged, or wants a duplication audit of a module, layer, or the whole repository. Report only by default; change code only when the user explicitly asks for fixes.
---

# Abstraction Police

Find the same abstraction implemented more than once and the drift between the copies, because the drift is where the bugs live. In a fast-growing codebase the same concept quietly appears multiple times: a feature copies its neighbor's plumbing, then one copy gets hardened or fixed and the others silently do not. The mandate is to find these nearly duplicated abstractions and unify them.

Default to a report. Do not edit code unless the user explicitly asks for fixes; when they do, fix in small verified batches with the build and existing tests green after each one.

## 1. What to hunt for

1. **Near-duplicate abstractions**: two or more functions, hooks, components, structs, or modules implementing the same concept with slight drift - same shape under different names, copy-pasted then edited, or parallel implementations on either side of a process, API, or language boundary.
2. **Repeated inline patterns that deserve an abstraction**: the same multi-line sequence (setup/teardown, subscribe/unsubscribe, fetch-with-timeout, retry/backoff, atomic file write, error mapping) appearing in three or more call sites.
3. **Drifted constants and contracts**: the same magic number, event or route name, endpoint path, or serialized type defined independently in multiple places where one source of truth should exist. Hand-synced string contracts are the highest-value targets: both sides compile happily with a one-character drift and fail silently at runtime.
4. **The inverse, over-abstraction**: a generic layer with exactly one caller, an interface with one implementation, a config surface nothing configures, or indirection that is harder to trace than the duplication it replaced.

## 2. What NOT to flag

- Coincidental similarity: two things that look alike today but change for different reasons. Unifying them couples unrelated features.
- Deliberate duplication that a comment, README, or project instruction file explains. Read the explanation before flagging; a documented decision is a non-finding even when the code looks copy-pasted.
- Duplication across a hard boundary where a shared source of truth is impractical (for example two languages each needing a mirror of one wire type). Flag the missing anchor comment or generation step instead of the mirror itself.
- Style, naming, and formatting. Not this skill's beat.

## 3. Method

1. **Sweep by concept, not by file.** Enumerate the codebase's recurring concepts (caches, event plumbing, fetch layers, crypto or file IO, geometry or unit math, formatters, subscription lifecycles), then search for each concept's fingerprints across the whole tree. Read [references/hunting-patterns.md](references/hunting-patterns.md) for concrete fingerprints per category.
2. **Read every candidate before flagging.** A search hit is not a finding. Confirm the duplication is real, then describe the exact drift between copies: which copy was hardened, extended, or fixed after the split, and which silently was not.
3. **Check intent.** Look for comments, docs, and instruction files that explain the shape before convicting it. Record deliberate look-alikes you examined and did not flag, with the reason.
4. **Rank by cost:**
   - **A** - copies that have ALREADY drifted in behavior, or contracts already dead or broken (a listener with no emitter, a registered handler nothing calls).
   - **B** - hand-synced shared contracts in sync today but likely to drift.
   - **C** - mere verbosity; unify opportunistically when touching the file.

## 4. Report

For each finding, in rank order:

1. **Sites**: every location as `file:line`.
2. **Concept**: what is duplicated, in one sentence.
3. **Drift**: the concrete differences between copies, quoting both sides when they disagree.
4. **Why unifying (or inlining) pays**: the failure the next edit would cause.
5. **Suggested fix**: one paragraph naming where the unified version should live and which copy's behavior wins.

End with the deliberate non-findings list and totals (how many distinct sites examined, how many unprotected hand-synced contracts exist even where nothing has drifted yet).

## 5. If asked to fix

Sequence by dependency and risk: shared utility modules first, then contract constants, then mechanical call-site migrations, with the riskiest refactors last so early work stays revertable. Keep every phase compiling and existing tests passing before starting the next, preserve error-message strings and wire bytes exactly unless a change is called out as deliberate, and never let a unification silently change a frozen serialized format (stored data, AAD strings, binary headers) that existing artifacts depend on.
