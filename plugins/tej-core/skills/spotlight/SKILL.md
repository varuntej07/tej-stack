---
name: spotlight
description: Make a website the page Google ranks and AI answers cite when someone asks about what the product does, then ship the fixes after the user approves a ranked plan. Covers classic SEO (titles, canonicals, per-page Open Graph, internal links, structured data), AI answer-engine readiness (AEO, GEO, crawler access, server-rendered copy, extractable answers), freshness and indexing (truthful sitemap lastmod, IndexNow, Search Console and Bing Webmaster), and honest alternatives and use-case pages. Use when the user says spotlight, optimize SEO, do SEO and AEO, get us indexed, get found on Google, show up in ChatGPT, Perplexity, Claude or AI Overviews, make AI recommend us as an alternative, keep the site fresh for search, or wants the same SEO pass rerun later ("spotlight recheck"). Works in any repo, with or without tej-core init. Stops for approval before any edit; never commits, pushes or deploys.
---

# Spotlight

Put the product in the spotlight when someone asks Google or an AI engine a question it
answers. The job is not to sprinkle SEO on a site. It is to prove, page by page, that search and
answer engines can fetch it, read it, index it, extract it, trust it and attribute it, that what
they read is true and current, and that a real page exists for each real question buyers ask.
Then fix the first broken link, in that order.

**The failure this skill exists to prevent is confident cargo-culting**: an llms.txt and fifty
FAQ schemas shipped onto a site whose homepage title still describes last year's product, whose
pages all share the homepage's `og:url`, and whose sitemap has never told Bing anything changed.
Every finding carries the check that could prove it wrong. Every tactic without evidence is
refused by name.

## 0. Setup

- Scope: if `.context/tej-core.json` exists, read `repos` and `never_touch`, and write the plan
  to `.context/4-scratchpad/`. Otherwise write it to the session scratchpad.
- Read the repo's CLAUDE.md, AGENTS.md and design docs first. Their copy, voice and page rules
  win over anything here.
- `spotlight recheck` skips to section 7.

## 1. Ground truth

Find what the product actually ships before judging any page: feature registries, settings
schemas, pricing catalogs, store listings, release feeds, sibling repos named in CLAUDE.md.
Write a claims ledger: each product claim, the file:line that proves it ships, and the platforms
it ships on. No page, title, description or JSON-LD may claim anything off the ledger. Find the
live URL (site config, env defaults, deploy config).

## 2. Probe the live site

Probe what engines get, not what the code suggests. `curl` is enough; never open a browser
unless the user asks.

- `robots.txt` on every host; `sitemap.xml` URLs and their `lastmod`.
- Per user-agent status and byte size on `/` and each money page: GPTBot, OAI-SearchBot,
  ChatGPT-User, ClaudeBot, Claude-SearchBot, Claude-User, PerplexityBot, Bingbot, Googlebot.
  A 403 or a tiny body for one bot is an A finding.
- For each indexable page, from raw HTML: `<title>`, meta description, canonical, `og:url`,
  `og:title`, JSON-LD `@type`s, and a grep for the page's money sentence. If it is not in the
  raw HTML it does not exist for AI crawlers.
- Inventory internal links: any indexable page no other page links to is an orphan.

## 3. Audit

Walk the citation chain in [references/engine-matrix.md](references/engine-matrix.md) order:
fetchable, readable, indexed, extractable, citable, attributable, agent-ready. A break at step N
outranks everything after it. Alongside it, check:

- [references/seo-foundations.md](references/seo-foundations.md): positioning drift between the
  homepage metadata and what the product is today, per-page metadata, internal links,
  structured data that mirrors visible content, Core Web Vitals.
- [references/freshness-indexing.md](references/freshness-indexing.md): truthful `lastmod`,
  visible updated dates, IndexNow, console verification.
- Content quality per [references/content-patterns.md](references/content-patterns.md) and
  schema rules per [references/schema-playbook.md](references/schema-playbook.md).

## 4. Opportunity map

List 15 to 30 questions real buyers ask: the jobs the product does ("dictate into any app on
Windows"), "<competitor> alternative", "<us> vs <them>", "best <category> for <audience>". For
each one record the page that answers it today, the page that should exist, or "not ours to
win" (needs third-party mentions). Propose new pages only for claims on the ledger, using
[references/alternatives-pages.md](references/alternatives-pages.md) for comparison pages.
Prefer one strong page per intent over many thin ones.

## 5. Plan, then stop

Write `SPOTLIGHT-<YYYY-MM-DD>.md`:

1. **The story first**, the way the user would say it to a cofounder: what is costing them
   visibility, how it works now, the one move that changes it, why it should work.
2. **Findings ranked** A (breaks the chain or tells every engine the wrong thing), B (found but
   under-served), C (polish). Each: page or asset, evidence observed, fix, cost, refuting check
   with the direction it should move.
3. **New pages** with the questions each answers and the ledger lines backing every claim.
4. **Deliberate non-findings**: tactics examined and refused, each with its receipt.
5. **Out of scope but decisive**: earned media (reviews, Reddit, launch sites, third-party
   lists, store reviews), stated honestly as work this repo cannot do.
6. **Prompt-probe set**: 20 frozen real questions to run per engine on a schedule, per
   [references/measurement.md](references/measurement.md).
7. **User-only steps**: console verification, sitemap submission, anything needing an account.

Reply with the story, the A findings and the plan path. **Stop for approval.** Do not edit.

## 6. Fix

Smallest verifiable change first, in chain order: unblock, then render, then metadata and
canonicals, then freshness, then structure, then new pages, then prose. Fix the class, not the
instance: when one page has wrong metadata, build or reuse the one helper every page goes
through. After each step re-run its check and the repo's lint, tests and build. In a tej-core
repo, run the evaluator agent until PASSED. Then:

- Ship the freshness loop from freshness-indexing.md (truthful lastmod, IndexNow key and ping
  script) and list the console steps only the user can do.
- Update the repo's SEO or AEO doc so the next run starts from receipts, and save the
  prompt-probe set there as the baseline.
- Write `.context/spotlight.json` as `{"last_run": "<YYYY-MM-DD>", "site": "<live URL>",
  "recheck_days": 30}`, one key per line. tej-core's session-start hook reads it in every
  session and reminds the user once the recheck is due. Keep `recheck_days` if the user set it.
- Report what changed, each check's before and after, and anything left unverified. Never
  commit, push or deploy without the user asking in the current message.

## 7. Recheck

The user is reminded automatically: once `last_run` in `.context/spotlight.json` is older
than `recheck_days`, the session-start hook tells the agent to offer a recheck.
`spotlight recheck` re-runs section 2 against the live site, diffs it against the last plan,
re-runs the prompt-probe set, and reports what moved, what did not, and new drift (pages added
without metadata, stale lastmod, claims that left the ledger). Citations and rankings move on
recrawl timescales: report weeks, never hours, and never claim a win from a single probe run.
Finish by updating `last_run` in `.context/spotlight.json` to today, which resets the reminder.

## Refusal rules, hard

Refuse by name with the receipt from [references/myths.md](references/myths.md), even when the
user asks directly:

- llms.txt as a visibility fix (legitimate only as a coding-agent convenience on docs sites).
- Chunking pages into fragments for RAG; rewriting prose for AI; keyword or question stuffing.
- Schema for content that is not visibly on the page.
- A page per query variant, or near-duplicate city, persona or competitor pages.
- Claims about a competitor without a dated source, or "they lack X" from a single visit.
- `/pricing.md` or similar "agent files" sold as a ranking lever: no published effect. Make the
  real pricing page server-rendered instead.
- Buying mentions, reviews, links or placements.
- Any tool or report claiming internal AI-engine ranking metrics.

When a new tactic appears, apply the three questions at the end of myths.md instead of guessing.
Where the online SEO skill packs disagree with this file, [references/sources.md](references/sources.md)
says which side the evidence is on.
