---
name: get-cited
description: Audit any website for AI answer-engine readiness and make it the source AI answers cite, with a proof per finding and a hard refusal of tactics with no evidence. Use for requests to show up in ChatGPT, Perplexity, Claude, Copilot, or Google AI Overviews and AI Mode, get cited or recommended by AI, do AEO, GEO, LLM SEO, or AI search optimization, audit a site for AI visibility, decide about llms.txt or schema markup for AI, fix dropping AI referral traffic, check whether AI crawlers can read the site, or make a site agent-ready. Apply when the user says AI never mentions us, competitors get cited and we do not, ChatGPT gets our product wrong, our docs are invisible to AI, or asks whether an AEO tactic or tool is worth it. Works on any stack, framework, or CMS. Report only by default; change code or content only when the user explicitly asks for fixes.
---

# Get Cited

> **Update check (run silently before the audit):** run `bash "<this skill's directory>/../../bin/check-update.sh"` and read its single `TEJ_STACK:` status line. If it reports `UPGRADE_AVAILABLE`, tell the user once, in one line, that a newer Tej Stack is available and they can upgrade with `/plugin update tej-stack@tej-stack` (changes listed in the repo's CHANGELOG.md), then continue this task normally. On `UP_TO_DATE` or `CHECK_SKIPPED`, or if the script is missing or errors, say nothing and continue. The check must never block, delay, or fail the task.


Make the website the source AI answers cite. The mandate is not to sprinkle AI-magic on a site. It is to establish, in order, whether answer engines can fetch the content, read it, index it, extract it, trust it, and attribute it, and to fix the first broken link in that chain before touching anything downstream.

Default to a report. Do not edit code or content unless the user explicitly asks for fixes.

**The failure this skill exists to prevent is not invisibility to AI. It is confident cargo-culting**: shipping an llms.txt and fifty FAQ-schema entries while the product pages are client-rendered and invisible to every AI crawler, or while the CDN has been silently returning 403 to GPTBot since onboarding. A plausible AEO tactic with no evidence reads exactly like a real one. Every finding must carry a check that could prove it wrong, and every fashionable tactic that lacks evidence gets refused by name.

## 1. Walk the citation chain, in order

A citation requires every link below to hold. Audit them in this order, because a break at step N makes all later work worthless, and the expensive advice (content rewrites) sits at the end while the decisive failures (blocking, client-side rendering) sit at the start. Facts per engine, with sources, are in [references/engine-matrix.md](references/engine-matrix.md).

1. **Fetchable.** Read the real robots.txt per subdomain against the actual AI bot roster: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot, Claude-User, PerplexityBot, Google-Extended, Bingbot. Then check what the CDN or WAF returns **to those user-agents**, not to a browser: Cloudflare blocks AI crawlers by default since July 2025, so an open robots.txt proves nothing. Know what each block costs; blocking GPTBot opts out of training while blocking OAI-SearchBot opts out of ChatGPT Search citations, and Google-Extended does not touch AI Overviews at all.
2. **Readable.** AI crawlers fetch raw HTML and do not execute JavaScript (measured, Vercel/MERJ). The test is view-source or `curl`: if the money content is not in the server response, it does not exist for ChatGPT, Claude, or Perplexity. Client-rendered pages need SSR, SSG, or prerendering for every page that should be citable. This single finding outranks all content advice.
3. **Indexed.** Every answer engine rides on a search index: AI Overviews and AI Mode on Google's, Copilot and much of ChatGPT Search on Bing's, Perplexity on its own crawl. Not indexed means not citable. Standard indexability is the prerequisite, not a separate discipline.
4. **Extractable.** Engines cite self-contained passages: 44.2% of ChatGPT citations come from the first 30% of a page, and 78.4% of question-linked citations trace to headings. Direct answer in the first screenful; headings phrased as the real questions with a complete one-to-two sentence answer beneath; statistics on their own lines; tables for comparisons; one idea per paragraph. Patterns and their evidence in [references/content-patterns.md](references/content-patterns.md).
5. **Citable.** The measured content levers, from the GEO paper and successors: quotations from credible sources (+43% visibility), first-party statistics (+33%), cited sources (+28%), fluent prose. Keyword stuffing measured **negative**. Unique first-hand information beats restated commodity content; a page that only summarizes other pages gives an engine no reason to cite it over its sources.
6. **Attributable.** Entity legibility: Organization schema mirroring visible facts, consistent name and details across the site, profiles, and directories, visible authors and dates. Then the uncomfortable measured fact: brand mentions across the web out-predict backlinks roughly 3:1 for AI visibility, and a large share of citations go to third-party surfaces (Reddit, comparison posts, reviews). Report honestly which gaps are on-page and which are earned-media work this skill cannot fix from inside the repo. Schema specifics in [references/schema-playbook.md](references/schema-playbook.md).
7. **Agent-ready.** Where transactions matter: core flows that work without JavaScript where feasible, stable URLs, machine-readable feeds (Merchant Center, Business Profile) for product and local data.

## 2. Refusal rules, hard

Refuse these by name, with the receipt, even when the user asks for them directly. Full evidence and steelmen in [references/myths.md](references/myths.md).

- **llms.txt as a visibility fix.** Google Search ignores it, and a 137K-domain log study found 97% of llms.txt files receive zero requests. Legitimate only as a convenience for coding agents on developer-docs sites, and only described that way.
- **Chunking pages into fragments for RAG.** Retrieval systems chunk at index time; no engine documents a publisher-side input. Write self-contained sections instead.
- **Rewriting prose for AI or stuffing question variants.** Engines resolve synonyms; keyword stuffing measured -8.7% in the GEO paper.
- **Schema for content not visibly on the page.** Google spam policy violation, and FAQ rich results are deprecated for nearly everyone anyway.
- **A page per query variant.** Scaled content abuse. Query fan-out reads one good page for many sub-questions.
- **Buying mentions, reviews, or parasite placements.** Spam-policed and, for fake reviews, illegal under the 2024 FTC rule.
- **Any tool or tactic claiming internal AI-engine metrics.** No third party has them; Google says so verbatim.

The tell is always the same shape: plausible mechanism, no published effect, a vendor selling the fix. When a tactic not on this list appears, apply the three questions at the end of the myths file instead of guessing.

## 3. Prove it

Every finding names its refuting check, from [references/measurement.md](references/measurement.md):

- Fetchability: robots.txt fetch plus per-bot-UA `curl`, status codes as seen by the bot, server-log presence of each crawler.
- Readability: raw-HTML grep for the money sentence under each AI user-agent.
- Indexing: `site:` checks, Search Console and Bing Webmaster coverage.
- Schema: validator plus the manual mirror check against visible content.
- Outcome: a frozen prompt-probe set (10 to 30 real customer questions run on a schedule per engine, trend over repeated runs, never a single run) as the before/after for citation share; referral segmentation for traffic, stated as a floor because AI referrers strip.

State the expected direction of each measurement before taking it. Content and index changes move on recrawl timescales; say weeks, not hours.

## 4. Report

Rank by expected payoff:

- **A**: breaks the chain outright (blocked crawlers, client-rendered money content, not indexed). Fix now; nothing downstream matters until it is fixed.
- **B**: retrievable but weakly extractable or citable (buried answers, no statistics, no quotable units, entity confusion). Fix when touching the page.
- **C**: polish with plausible but unmeasured benefit. Note and move on.

For each finding: the page or asset, the broken chain link, the evidence observed, the fix, what it costs, and the exact check that verifies it. End with:

- **Deliberate non-findings**: tactics examined and refused, each with its receipt. This section is the evidence the audit was not pattern-matched from a marketing blog.
- **Out of scope but decisive**: the earned-media gaps (third-party mentions, review presence) reported honestly as such.
- **Totals**: pages examined, findings by rank, and anything that could not be established, named rather than guessed.

## 5. If asked to fix

Chain order, smallest verifiable change first: unblock before rendering, render before structure, structure before prose. One change per step, the named check re-run after each, both numbers reported including the ones that did not move. A fix whose predicted measurement never moved is reported as such, not defended.
