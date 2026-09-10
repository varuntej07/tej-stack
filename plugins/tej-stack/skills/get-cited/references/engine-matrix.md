# Engine and crawler matrix

Per-engine facts that decide whether a page can be retrieved at all. Verified September 2026; bot rosters change, so when a finding hinges on one row, re-fetch the official doc listed for it before reporting.

## The bots

| Bot | Operator | Purpose | Respects robots.txt | Executes JS |
|---|---|---|---|---|
| `GPTBot` | OpenAI | Model training crawl | Yes | No |
| `OAI-SearchBot` | OpenAI | ChatGPT Search index | Yes | No |
| `ChatGPT-User` | OpenAI | Live fetch when a user asks | No (user-initiated) | No |
| `ClaudeBot` | Anthropic | Model training crawl | Yes | No |
| `Claude-SearchBot` | Anthropic | Claude search quality | Yes | No |
| `Claude-User` | Anthropic | Live fetch when a user asks | Yes | No |
| `PerplexityBot` | Perplexity | Perplexity's own index | Yes | No |
| `Perplexity-User` | Perplexity | Live fetch when a user asks | No ("generally ignores robots.txt", their words) | No |
| `Googlebot` | Google | Google index, which also feeds AI Overviews and AI Mode | Yes | Yes |
| `Google-Extended` | Google | robots.txt token only, no crawler of its own; opts out of Gemini training and grounding | It is a robots.txt token | n/a |
| `Bingbot` | Microsoft | Bing index, which grounds Copilot | Yes | Yes |
| `CCBot` | Common Crawl | Open corpus widely used for AI training | Yes | No |
| `meta-externalagent` | Meta | AI training and indexing | Yes | No |

Official bot docs: OpenAI (https://platform.openai.com/docs/bots), Anthropic (https://support.claude.com/en/articles/8896518), Perplexity (https://docs.perplexity.ai/guides/bots), Google (https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers), Common Crawl (https://commoncrawl.org/ccbot), Meta (https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/).

## No JavaScript execution

The Vercel/MERJ crawler study (December 2024, https://vercel.com/blog/the-rise-of-the-ai-crawler) measured it directly: GPTBot, ClaudeBot, PerplexityBot, Meta-ExternalAgent and Bytespider fetch raw HTML and never execute JavaScript. They download JS files (GPTBot in ~11.5% of requests, ClaudeBot in ~23.8%) and still never run them. Later third-party retests through 2026 confirm the finding holds. Only Googlebot (whose rendering also serves Gemini) and Bingbot render.

Consequence: anything rendered client-side is invisible to every AI-specific crawler. The test is view-source, not DevTools. If the money paragraph is not in the raw HTML response, it does not exist for ChatGPT, Claude, or Perplexity.

## Which index each answer engine rides on

- **Google AI Overviews / AI Mode**: the regular Google index via Googlebot, using query fan-out (https://developers.google.com/search/docs/appearance/ai-features). Not indexed in Google means not citable there.
- **ChatGPT Search**: Bing's index plus OpenAI's own OAI-SearchBot crawl and publisher deals. OAI-SearchBot volume grew sharply through 2025-2026 as OpenAI builds out its own index.
- **Perplexity**: its own index via PerplexityBot.
- **Copilot**: the Bing index. `noarchive` removes content from Copilot answers; `nocache` limits Copilot to URL, title, and snippet (Bing, September 2023 announcement).
- **Claude**: never officially named; Brave Search appears on Anthropic's subprocessor list and citation-overlap studies point the same way, with Claude-SearchBot suggesting a growing first-party index. Treat as inference, not fact.

## What blocking actually costs

These pairs are independent and owners routinely block the wrong one:

- Blocking `GPTBot` opts out of OpenAI **training**. Blocking `OAI-SearchBot` removes you from **ChatGPT Search citations**. A site that wants ChatGPT visibility but blocks both has opted out of the thing it is asking for.
- `Google-Extended` blocks Gemini training and grounding but does **not** affect Google Search or AI Overviews. The only controls over AI Overviews are the ones that also affect regular Search: `nosnippet`, `data-nosnippet`, `max-snippet`, `noindex`, and blocking Googlebot itself (https://developers.google.com/search/docs/appearance/ai-features). You cannot opt out of AI Overviews without also giving up Search presence.
- Blocking `ClaudeBot` opts out of Anthropic training; blocking `Claude-User` or `Claude-SearchBot` reduces visibility inside Claude conversations. Anthropic notes robots.txt is read per subdomain and that IP-blocking the bot can break the robots.txt opt-out itself.
- User-triggered fetchers (`ChatGPT-User`, `Perplexity-User`) reach pages regardless of robots.txt. Their appearance in server logs is a leading indicator that pages are being read into live answers.

## The silent blocker: CDN and WAF defaults

Since July 1, 2025, Cloudflare blocks AI crawlers **by default** for new domains and asks owners to opt in (https://blog.cloudflare.com/content-independence-day-no-ai-crawl-without-compensation/). A site behind Cloudflare (or a WAF with a similar "block AI bots" toggle) may be returning 403s to GPTBot, ClaudeBot, and PerplexityBot with a robots.txt that looks wide open. Check the CDN's bot settings and the server logs for AI user-agents receiving non-200 responses before diagnosing anything else.

## Verifying a bot is genuine

Each operator publishes IP ranges: OpenAI per-bot JSON files under openai.com (gptbot.json, searchbot.json, chatgpt-user.json), Anthropic at https://claude.com/crawling/bots.json, Perplexity at perplexitybot.json and perplexity-user.json under perplexity.com, Googlebot via reverse DNS or its published list, Common Crawl via `*.crawl.commoncrawl.org` reverse DNS. Validate user-agent plus IP together; user-agent strings alone are trivially spoofed.
