# Changelog

All notable changes to Tej Stack. Versions follow semantic versioning; the current version lives in `VERSION`.

## 0.8.0 (2026-10-15)

- New `cost-police` skill: finds where LLM tokens, metered services (Firebase, serverless, storage, SMS), and infrastructure as code (Terraform, CloudFormation, Pulumi, serverless.yml) waste money, and where one bug or abuser could run up the bill. Prices are fetched live from official pages and cited on every dollar figure. It refuses savings claims without real volume and model downgrades without a quality eval. Ships a standard-library scanner for billed call sites.
- New `promo-reel` skill: turns a real app into a short promo video from one HTML scene, in three modes: social ad, App Store or Play preview, and seamless landing-page loop. It captures real screens over adb, simctl, or Playwright, keeps a claims ledger so nothing invented reaches the screen, stops for your OK on the beat table, and checks the render against store and platform specs before delivery. Based on the ad-kit springs engine and renderer.
- The `tej` router now sends cost questions to `cost-police` and promo video requests to `promo-reel`.
- README rewrite: one-paste install, quick start, example sessions, a "which skill" table, and uninstall steps.

## 0.7.0 (2026-10-10)

- New `speed-dial` Claude Code plugin, the first hook plugin in this marketplace. A short prompt like "make the play store build" is matched by Jev (TypeSafe) against the commands you save in `.claude/speed-dial.json`, and the match starts in a new terminal window without waiting on the model. Anything else passes through unchanged. Bring your own `TYPESAFE_API_KEY`. Project files stay off until you type `speed-dial trust`.
- `validate.py` now also checks hook plugins listed in the Claude marketplace.

## 0.6.0 (2026-10-10)

- New `x-ray` skill: map a code file, a repo flow, or a concept into a Figma-style block diagram page. Clicking a block opens its file and line, signature, inputs and outputs, config, code excerpt, gotchas, and official docs. Ships a stdlib-only repo scanner, a graph validator and builder, and a self-contained canvas template that runs as a local file or a claude.ai Artifact.
- The `tej` router now sends map and diagram requests to `x-ray`.

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
