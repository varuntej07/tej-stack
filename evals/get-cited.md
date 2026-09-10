# Get Cited evaluation cases

Use raw prompts without telling the agent which problems exist, and without hinting that some prompts ask for tactics that must be refused.

## Scoring

- Audits the citation chain in order (fetchable, readable, indexed, extractable, citable, attributable) and stops content advice when an earlier link is broken.
- Tests fetchability against the real AI bot roster and the CDN/WAF as seen by those user-agents, not only robots.txt as seen by a browser.
- Tests readability against raw HTML (view-source or curl), never against the rendered DOM, and treats client-rendered money content as an A-rank finding that outranks all content advice.
- Distinguishes training bots from search-index bots from user-triggered fetchers, and states what each specific block costs (GPTBot vs OAI-SearchBot; Google-Extended not affecting AI Overviews).
- Grounds content recommendations in measured evidence (GEO paper effect sizes, citation-position studies) and marks unmeasured conventions as such.
- Refuses llms.txt, chunking, AI-prose rewriting, invisible schema, query-variant pages, bought mentions, and internal-metrics tools by name with a cited receipt, including when the user explicitly requests them, while stating the honest steelman.
- Names a refuting check for every finding (per-UA curl, robots.txt fetch, site: query, schema validator plus mirror check, frozen prompt-probe set) with the expected direction stated before measuring.
- Treats single prompt-probe runs as noise and requires trends over repeated runs.
- Reports earned-media gaps (third-party mentions, Reddit, reviews) honestly as out of repo scope instead of pretending on-page work covers them.
- Sets recrawl-timescale expectations (weeks, not hours) for content and index changes.
- Ends with deliberate non-findings and totals, including what could not be established.
- Reports only; does not edit code or content unless the user explicitly asks for fixes.

## Cases

### Direct whole-site audit

**Prompt:** `Audit this site so we show up in ChatGPT and Google AI answers.`

**Expected:** Walks the chain in order with evidence per link: robots.txt and CDN behavior per AI user-agent, raw-HTML readability of key pages, index status, then extractability and citability of the money pages. Ranked A/B/C findings each with the page, the broken link, the fix, the cost, and the verifying check. Deliberate non-findings and totals. No edits.

### Indirect trigger, symptom only

**Prompt:** `Competitors keep getting recommended by Perplexity and we never do.`

**Expected:** Activates the skill. Checks whether PerplexityBot can fetch and read the site at all before any content theory, then compares extractability and citability against what Perplexity actually cites in the category (including third-party surfaces like Reddit), and proposes a frozen prompt-probe set as the baseline measurement.

### Negative case: must refuse the asked-for tactic

**Prompt:** `Add an llms.txt and split our docs into small chunks so LLMs index us better.`

**Expected:** Refuses both with receipts: Google ignores llms.txt and the 137K-domain log study found 97% of the files get zero requests; chunking is the retriever's job with no publisher-side input. States the steelman (llms.txt is a harmless convenience for coding agents on developer docs) without overselling it, and redirects to the citation chain, starting with whether the docs are readable in raw HTML.

### Negative case: invisible schema

**Prompt:** `Generate FAQ schema with 50 common questions about our product and add it to the homepage. The questions don't need to be shown on the page.`

**Expected:** Refuses. Cites the visible-content structured data policy and spam-action risk, notes FAQ rich results are deprecated for nearly all sites, and offers the honest alternative: put the genuinely asked questions on the page as question-shaped headings with self-contained answers, marked up only if visible.

### Boundary: client-rendered SPA outranks everything

**Prompt:** `Review our marketing site for AI visibility.` where the site is a React SPA whose product and pricing content renders entirely client-side.

**Expected:** The JS-invisibility finding is rank A and explicitly stated to outrank all content advice: AI crawlers fetch raw HTML and do not execute JavaScript, so the money content does not exist for them. Proof is a curl or view-source grep showing the content absent. Recommends SSR, SSG, or prerendering for citable pages before any wording or schema work, and does not pad the report with content tips that are worthless until rendering is fixed.

### Boundary: the contradictory block

**Prompt:** `We want to be cited in ChatGPT. Why isn't it working?` where robots.txt disallows both GPTBot and OAI-SearchBot, or the site sits behind Cloudflare with default AI-bot blocking.

**Expected:** Finds the contradiction and separates the knobs: GPTBot governs training while OAI-SearchBot governs ChatGPT Search citations, and a CDN can 403 the bots regardless of robots.txt. Explains what unblocking each costs, verifies with per-UA requests and server logs rather than robots.txt alone, and leaves the allow/block decision to the owner instead of silently unblocking.

### Boundary: measurement honesty

**Prompt:** `We fixed our pages last week. Prove our AI visibility improved.`

**Expected:** Does not run one prompt per engine and declare victory. States that single runs are noise, sets up or asks for the frozen question set and repeated runs, checks server logs for AI user-agent activity and referral segments as supporting signals with the referrer-stripping caveat, and sets recrawl-timescale expectations rather than promising same-week movement.
