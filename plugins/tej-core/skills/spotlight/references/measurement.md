# Measuring AI-answer visibility

Every finding in a get-cited report names a measurement that could refute it. These are the instruments. State the expected direction before taking any reading; a prediction that survives is worth more than a number collected afterwards.

## 1. Retrievability checks (immediate, free, decisive)

- **Raw HTML test:** `curl -sA "<bot user-agent>" https://site/page | grep "the money sentence"`. Run once with a normal browser UA and once per AI bot UA (see [engine-matrix.md](engine-matrix.md)); differing responses expose UA-based blocking. View-source in a browser is the manual equivalent. If the sentence is absent from raw HTML, the page is invisible to AI crawlers regardless of anything else.
- **robots.txt fetch:** read the actual file per subdomain. Check which of GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, PerplexityBot, Google-Extended are named, and reconcile against what the owner says they want.
- **CDN/WAF check:** status codes returned **to the bot UAs specifically**, not to you. Cloudflare blocks AI crawlers by default since July 2025; a 403 to GPTBot with an open robots.txt is the signature.
- **Index check:** `site:` queries and Search Console / Bing Webmaster coverage. AI answers ride on search indexes; a non-indexed page is a non-citable page.
- **Schema check:** validator.schema.org, the rich results test, and the manual mirror check against visible content.

## 2. Server logs

The ground truth for crawler behavior:

- Presence and rate of each AI bot UA, and the status codes they receive. A bot that fetched robots.txt and never returned is a bot that was told to leave.
- `ChatGPT-User`, `Claude-User`, and `Perplexity-User` hits mean pages are being read into live answers right now; a leading indicator that citations may follow.
- Verify suspicious UAs against published IP ranges before concluding anything (spoofing is common).

## 3. Referral traffic

- ChatGPT appends `utm_source=chatgpt.com` and sends a `chatgpt.com` referrer. Perplexity sends `perplexity.ai`. Gemini sends `gemini.google.com`.
- **AI Overview clicks are indistinguishable from normal Google organic** in analytics; do not promise AIO click attribution.
- GA4: build a custom channel group matching session source against `chatgpt\.com|perplexity\.ai|claude\.ai|gemini\.google\.com|copilot\.microsoft\.com`, ordered above Referral or it never matches. (GA4 shipped a native "AI Assistant" channel in May 2026; verify its coverage in the live property, it reportedly misses Perplexity.) Plausible and similar: filter sources on the same hostnames.
- A meaningful share of AI-referred visits arrive referrer-less (apps, webviews) and land in Direct. Referral counts undercount; treat them as a floor.

## 4. Search Console

- AI Overviews and AI Mode impressions and clicks are folded into the "Web" search type (https://developers.google.com/search/docs/appearance/ai-features); they cannot be isolated in the classic Performance report.
- Google began rolling out a dedicated generative-AI performance report in mid-2026 (impressions in AI experiences by page, country, device; no queries or clicks at launch). Check whether the property has it; report what it shows and what it cannot show.

## 5. Prompt probes (share of voice)

The only direct measurement of the actual outcome: does the engine cite this site?

Protocol:
1. Fix a question set: 10 to 30 questions real customers ask, phrased as users phrase them, spanning head and sub-questions. Freeze the wording.
2. Run the set against each target engine (ChatGPT, Perplexity, AI Mode, Copilot, Claude) on a schedule, logged out or in a consistent account state.
3. Record per question: cited or not, position among citations, who else was cited, and the answer's claim about the brand.
4. **Single runs are noise.** Answers are stochastic and vary by session, phrasing, and geography. The unit of analysis is the trend across repeated runs; report variance alongside share.

Commercial trackers (Profound, Peec, Otterly, Ahrefs Brand Radar) automate this at scale. They measure exactly this protocol from outside; none has internal engine access, whatever the marketing says. The manual protocol costs nothing and is enough for a before/after on one site.

## Before/after discipline

For any implemented fix: take the relevant reading first (raw-HTML grep, bot status codes, prompt-probe baseline), state the expected change, apply one change, re-measure. Content-side changes move slowly through recrawl and re-index; expect weeks, not hours, and say so rather than claiming instant effect. An intervention whose predicted needle never moved gets reported as such, not quietly forgotten.
