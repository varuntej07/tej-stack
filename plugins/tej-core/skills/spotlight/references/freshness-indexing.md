# Freshness and indexing

An engine can only cite what is in its index, and answer engines show a measured recency bias
(undated or stale pages lose to dated, recently updated ones). Freshness is a pipeline, not a
habit: the site must tell engines what changed, truthfully, every deploy.

## Truthful lastmod

- Google uses `<lastmod>` only when it is "consistently and verifiably accurate"; Bing uses it
  to prioritize recrawls. Ignored `changefreq` and `priority` are harmless but do nothing.
- Derive each URL's `lastmod` from a real content date: a post's `updated` or `date`, a
  comparison's `checkedOn`, a use case's `updated`, a legal page's effective date. Never
  `new Date()` at build time: that marks everything changed every deploy and teaches engines to
  ignore the field.
- Pages with no content date get no `lastmod` rather than a fabricated one. Add a content date
  constant next to the page's copy when the page matters.
- Show the same date visibly ("Updated <date>") on pages where recency matters (comparisons,
  pricing, guides). Dated statistics and "as of" competitor facts carry further.

## IndexNow (Bing, Copilot, Yandex, Seznam, Naver)

- Protocol: host a key file at `https://<host>/<key>.txt` whose body is the key, then POST
  `{ host, key, keyLocation, urlList }` to `https://api.indexnow.org/indexnow`. One submission
  is shared with every participating engine. HTTP 200 or 202 means received, not indexed.
- Microsoft states IndexNow keeps content fresh across Bing search and its AI experiences, which
  feed Copilot and much of ChatGPT Search.
- Google does not participate. Do not claim IndexNow helps Google.
- Ship it as a script run after each production deploy (or a post-deploy CI step) that submits
  the sitemap's URLs, or only those whose `lastmod` changed. Submit only URLs that return 200 on
  the live host. Do not submit on preview deploys.

## Google

- Google Search Console: verify the domain (DNS TXT is best; the HTML meta tag works), submit
  the sitemap, use URL Inspection and "Request indexing" for a few key pages after a big change.
  There is no Google ping endpoint; the old sitemap ping was retired in 2023.
- Search Console has no AI Overviews or AI Mode breakdown; clicks from them are folded into Web.

## Bing Webmaster Tools

- Verify (import from Search Console is fastest), submit the sitemap, enable IndexNow in the
  tool to see submitted URLs. Bing Webmaster now reports AI performance for Copilot citations.

## Verification tokens in code

- Read them from environment variables and emit the meta tag only when set. An empty
  `content=""` verification tag is a smell that someone meant to verify and never did.

## Timescales

Recrawl takes days, reindex and ranking movement takes weeks, citation share changes are
measured over weeks of repeated probes. Say so in every report.
