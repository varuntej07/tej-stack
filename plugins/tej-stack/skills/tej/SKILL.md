---
name: tej
description: Router for the Tej Stack skill suite. Use when the user invokes Tej Stack without naming a specific skill, or asks which Tej Stack skill fits a task. Triggers on tej, tej stack, tejstack, use tej, run tej stack on this, and speech-to-text aliases like tay stack, taj stack, tedge stack, tage stack, or tej stack. Routes feature audits to walkie-talkie, failure explanations to trace-failure, duplication sweeps to abstraction-police, performance hunts to big-o-police, and AI answer-engine visibility work to get-cited, then hands off to that skill rather than doing the work itself.
---

# Tej

> **Update check (run silently first):** run `bash "<this skill's directory>/../../bin/check-update.sh"` and read its single `TEJ_STACK:` status line. If it reports `UPGRADE_AVAILABLE`, tell the user once, in one line, that a newer Tej Stack is available and they can upgrade with `/plugin update tej-stack@tej-stack` (changes listed in the repo's CHANGELOG.md), then continue routing normally. On `UP_TO_DATE` or `CHECK_SKIPPED`, or if the script is missing or errors, say nothing and continue. The check must never block, delay, or fail the task.

Send the request to the right Tej Stack skill and hand off. Do not perform the underlying audit here; this skill exists so a vague or voice-dictated invocation still lands on the right specialist.

## Routing table

| The user's request is about | Route to |
|---|---|
| Whether a finished feature actually works for every user, actor, and recovery path | `walkie-talkie` |
| A failure, error, crash, broken behavior, or "what happened and why" | `trace-failure` |
| Duplicated code, drifted copies, repetitive-feeling modules, whether to merge or inline an abstraction | `abstraction-police` |
| Slowness, memory, scale degradation, data-structure or algorithm choices | `big-o-police` |
| Showing up in ChatGPT, Perplexity, Claude, Copilot, or Google AI answers; AEO, GEO, AI SEO, llms.txt, schema for AI | `get-cited` |

## How to route

1. Match the request against the table. If exactly one row fits, invoke that skill immediately with the user's original request; do not re-ask what they meant.
2. If two rows genuinely fit (a slow feature that also misbehaves), name both in one sentence, pick the one matching the user's primary verb (fix, explain, audit, speed up), and proceed. Offer the other as a follow-up at the end.
3. If no row fits, say so plainly and do the task without a Tej Stack skill; do not force the nearest skill onto a request it does not cover.
4. Voice-dictation input is often garbled; resolve the intent, not the transcription. "Run tay stack on why checkout is slow" routes to `big-o-police`.

When asked "what can Tej Stack do", answer with the table above in one short paragraph per skill, and note that every skill reports with evidence first and refuses work it cannot verify.
