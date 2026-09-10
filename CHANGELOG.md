# Changelog

All notable changes to Tej Stack. Versions follow semantic versioning; the current version lives in `VERSION`.

## 0.5.0 (2026-09-10)

- New `tej` router skill: routes vague or voice-dictated invocations (tej stack, tay stack, tedge stack) to the right specialist skill.
- Built-in update check: every skill silently checks for a newer Tej Stack at most once per day and mentions available upgrades in one line, without blocking the task. Upgrade with `/plugin update tej-stack@tej-stack`.
- Added this changelog.

## 0.4.0 (2026-09-10)

- New `get-cited` skill: audit any website for AI answer-engine readiness (ChatGPT, Perplexity, Claude, Copilot, Google AI Overviews and AI Mode), with a proof per finding and hard, sourced refusals of AEO tactics that have no evidence (llms.txt, chunking, invisible schema, keyword stuffing). Grounded in Google's AI optimization guide, the GEO paper (KDD 2024), and 2025-2026 crawler and citation studies.

## 0.3.0

- New `big-o-police` skill: find and prove real algorithmic and data-structure wins, refuse the ones that do not pay.

## 0.2.0

- New `abstraction-police` skill: sweep for nearly-duplicated abstractions, drifted contracts, and premature abstractions.

## 0.1.0

- Initial release with `walkie-talkie` (feature audits through every affected actor) and `trace-failure` (causal failure explanations), dual Claude and Codex plugin manifests, direct installers, and CI validation on Linux and Windows.
