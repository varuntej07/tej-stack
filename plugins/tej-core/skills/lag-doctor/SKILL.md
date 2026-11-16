---
name: lag-doctor
description: Make every real-time LLM call feel fast by measuring it first. Finds each model call a person waits on (chat, voice, keyboard, inline assist, agents with a live user), pulls p50, p95 and p99 from production logs and splits the wait into stages (pre-model work, connection, prefill, thinking, first visible token, tool rounds), checks each stage against the provider's current official docs, asks the user which wait bothers them, then writes a short, doc-referenced plan and stops for approval. Use when the user says lag doctor, lag-doctor, latency, chat feels slow, time to first token, TTFT, the model takes forever to answer, voice reply lag, speed up the LLM, p95 or p99 of a model call, or `lag-doctor recheck` after a deploy. Works in any repo, with or without tej-core init. Algorithm and data-structure slowness goes to big-o-police; token bills go to cost-police. Never edits code before approval; never commits, pushes or deploys.
---

# Lag Doctor

Make the wait a person feels shorter, and prove it with the same numbers before and after.

**The failure this skill exists to prevent is a confident speed-up nobody measured**: a model
swapped, effort lowered or a cache added because a blog said so, shipped onto a path whose real
wait was a 2.5 s think, a fresh TLS handshake per request, or a database write sitting in front
of the model. Every finding carries the production number that motivated it, the official doc
that backs the fix, and the log field that would prove it wrong.

## 0. Setup

- If `.context/tej-core.json` exists, read `repos` and `never_touch`, then
  `.claude/rules/project-workflow.md` for evidence sources, log commands, the resilience
  profiles and which reads need permission. The report goes to `.context/4-scratchpad/`, the
  plan to `.context/2-specs/`. Otherwise both go to the session scratchpad.
- Read the repo's `CLAUDE.md` and the ARCH doc for every path you touch. Their rules win (who
  picks models, latency gates, test policy, cost locks on high-frequency calls).
- Read-only until approval. Log and analytics reads are fine; anything paid, slow or that the
  repo says to ask about, ask first.
- `lag-doctor recheck` skips to section 7.

## 1. Inventory every real-time call

Find every LLM call in every repo in scope, then keep the ones a person waits on.

- Search for SDK clients and raw endpoints: `anthropic`, `openai`, `google.genai` /
  `generativeai`, `vertexai`, `bedrock`, `groq`, `mistral`, `cohere`, `livekit`, `/v1/messages`,
  `/chat/completions`, `/responses`, `generateContent`, `streamGenerateContent`, plus the repo's
  own choke point (a model provider, router or tracer). Include embeddings, STT and TTS calls
  that sit on the same wait.
- Trace each call to its entry point. **Real-time** means a person is looking at a spinner,
  a cursor or silence until it returns: chat, voice turns, keyboard or dictation cleanup, inline
  assist, an agent step the user watches. Background work (schedulers, queues, batch, async
  enrichment) is listed once as out of scope, never measured here.
- For each real-time call record, from the code: `file:line`, user action and surface, what the
  user waits on (first word, full answer, audio, an applied edit), provider and model, streaming
  or not, thinking and effort settings, cache configuration, client lifetime (one per process or
  one per request), timeout and retry layers (SDK default plus any hand loop), fallback chain,
  and the stage marks that already log around it.

## 2. Measure from production

Follow [references/measurement.md](references/measurement.md). In short:

- Find the telemetry that exists (structured log rows, the LLM tracer, product analytics,
  client timers). Pull 7 to 14 days, or since the last change to that path. Save every query in
  the report so `recheck` can rerun it unchanged.
- Report p50, p95, p99 with n, the window and the percentile method. p99 needs n of at least
  100; below that print the max and say so. Never average percentiles across segments.
- Split the wait into stages: pre-model work, connect, provider first event, thinking gap
  (first event to first visible token), first visible token, tool rounds, total, and the
  client-side delta when a client timer exists. Segment by model, effort, surface and cache hit.
- No number for a stage means "unmeasured", and a log-only stage mark becomes a finding.
- Compare server and client numbers when both exist: the gap is network, auth and connection
  setup, and it is often the cheapest win.

## 3. Check against the official docs

For each provider, SDK and voice framework in use, fetch its current docs live, starting from
[references/sources.md](references/sources.md), and record URL and fetch date. Then confirm
against the **installed** version (print the real class signature or default with a one-off
command; read the SDK source when a default is undocumented). Docs describe latest; the lockfile
says what runs.

Walk [references/playbook.md](references/playbook.md) in stage order (before the model,
connection, prefill, thinking, output, round trips, perceived wait, tail, voice). For every
lever, write one line: what the doc says, what the code does, and the measured stage it would
move. A doc gap with no measured stage behind it is a non-finding.

## 4. Ask what bothers the user

Show the headline table first (each real-time path, what the user waits on, p50, p95, p99, n),
then ask, with a structured question tool when the harness has one:

- Which path feels slow, and is it the first word, the full answer, or the bad tail?
- What is off limits: model choice, effort or thinking level, cost increase, a client release?
- Any quality bar a change must hold (an eval, a blind side-by-side, tool-choice agreement)?

If the user already named the pain in the request, confirm it in one line instead of asking
again. Their answer reorders the plan; it never removes a finding from the report.

## 5. Plan, then stop

Write `LATENCY-<YYYY-MM-DD>.md` (the measurement report, with the saved queries) and the plan.
In a tej-core repo the plan is `.context/2-specs/SPEC-latency-<slug>.md` from the repo's feature
template, `status: draft`. Keep it short:

1. **The story first**, the way the user would say it to a cofounder: the wait they hate, how
   the path works now, the one move that changes it, why it should work.
2. **Ranked changes**: user-visible ms saved at p50 and p95 times how often the path runs. Each
   change names the stage it moves, `file:line`, the official doc URL with the line that backs
   it, expected before and after, cost and quality risk, and the refuting check (the log field
   and the direction it must move).
3. **Taxonomy** with the near-miss rows where a change must NOT fire (other routes, other
   providers, the high-effort tier, signed-out or offline clients, consent gates).
4. **ASCII diagram** of the path with changed edges marked, a stage budget table before and
   after, and the resilience matrix per call (timeout, retries, fallback, cancellation).
5. **Gated changes**: anything that can change answer quality (model, effort, thinking, prompt
   trim) ships only behind a preregistered eval with a pass bar and a spend cap.
6. **Deliberate non-findings** with the reason, and the deploy order.

Reply with the story, the top three changes with their numbers, and the plan path.
**Stop for approval.** No code before it.

## 6. Build (after approval)

Run the build as `/tej-core:feature` Phase 3 when tej-core is set up; otherwise implement the
approved changes surgically, smallest verifiable change first, then the repo's lint, tests and
evals. Every change keeps its failure cause, adds no feature flag, and never stacks a new retry
layer on a fast-fail path. Never commit, push or deploy without the user asking in the current
message.

## 7. Recheck

`lag-doctor recheck` (or 3 to 5 days after the changes deploy): rerun the saved queries on a window
of the same length after the deploy, and print before and after side by side with n. A change is
done when its refuting field moved the predicted way; otherwise mark it "unverified" or "did not
move" and say why. Check the serving version first so the window really covers the new code.

## Refusal rules, hard

Refuse by name, with the reason, even when asked directly:

- A change justified by docs alone, with no measured stage it would shorten.
- A model swap, lower effort, less thinking or a prompt trim without a quality eval and a bar
  set before the run. Faster and worse is a regression.
- A speed claim from a single request or a synthetic benchmark presented as production.
- Hedged or duplicate requests on a billed or non-idempotent call without the cost math
  (hedging at p95 adds about 5% load only when the call is cheap and side-effect free).
- A semantic or response cache for personalized or multi-turn answers.
- Raising a timeout or adding a retry to make a number look better, or cutting a timeout below
  the healthy p99 of that call.
- Fake streaming: buffering the full answer then replaying it as tokens.
- A model id chosen by the agent where the repo says the user picks models.
