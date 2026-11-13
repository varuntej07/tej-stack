# SEO foundations

Google states its AI Overviews and AI Mode are rooted in its core ranking systems, and Bing
feeds Copilot and much of ChatGPT Search. Classic indexability is therefore the floor for
answer engines, not a separate discipline. Each item: the check, and what a failure looks like.

## Positioning drift (check first)

The homepage `<title>`, meta description, `og:title`, keywords and the root
`SoftwareApplication` or `Organization` JSON-LD are the sentences every engine repeats when
asked "what is <product>". They are written once at launch and rarely revisited.

- Check: compare those strings with the current hero copy and the claims ledger.
- Failure: the product pivoted (mobile to desktop, consumer to B2B, new flagship feature) and
  the metadata still describes the old one. Rank A: every engine is told the wrong thing.
- Fix: rewrite around today's ledger. Keep the title near 60 characters and the description
  near 155, primary job in the first half, no keyword lists.

## Per-page metadata

Every indexable page needs its own title, description, canonical, `og:url`, `og:title` and
`og:description`. Frameworks with layout inheritance (Next.js `metadata`, Nuxt `useHead`,
Astro layouts) silently hand child pages the root Open Graph, so shared links and some crawlers
see the homepage's URL and title.

- Check: `og:url` in raw HTML equals the page's canonical, on every indexable page.
- Fix the class: one helper (for example `pageMetadata({ title, description, path })`) that
  every page calls, so a new page cannot ship without it.

## Canonicals and duplicates

- One canonical per page, absolute, self-referencing unless deliberately consolidating.
- `www` and apex, trailing slash and no slash, `http` and `https`: one wins with a permanent
  redirect; the others never return 200.
- Noindexed utility pages (auth, checkout, easter eggs) stay out of the sitemap.

## Internal links and orphans

Engines discover and weight pages through links. A page reachable only through the sitemap is
an orphan: crawled late, weighted low.

- Check: for each sitemap URL, grep the rendered site for an `href` to it from another page.
- Fix: a nav or footer group for each content family (use cases, comparisons, blog), and
  contextual links from related pages.

## Structured data

- Mirror visible content only (Google spam policy). Build JSON-LD from the same data the page
  renders, never a second hand-written copy.
- Useful types for a software product: `Organization` (with `sameAs` to real profiles),
  `WebSite`, `SoftwareApplication` (or `MobileApplication`) with `operatingSystem`,
  `applicationCategory` and `offers` built from the live price catalog, `BlogPosting` with
  author and dates, `BreadcrumbList` on nested pages, `WebPage` with `dateModified`.
- FAQ rich results are limited to well-known government and health sites since 2023, and later
  reports say Google stopped showing them in 2026. FAQPage markup that mirrors a visible FAQ is
  harmless and still parseable; adding it for a SERP feature is not a reason.
- Do not hardcode prices or platform lists in JSON-LD; derive them from the same source the
  page uses so they cannot drift.
- Validate with the Schema.org validator and Google's Rich Results Test, then do the manual
  mirror check against the page.

## Core Web Vitals

Thresholds at the 75th percentile of real users: LCP at most 2.5 s, INP at most 200 ms, CLS at
most 0.1. INP replaced FID in March 2024; never report FID. Use field data (CrUX, Search
Console) over a single lab run. CWV is a tiebreaker, not a lever that rescues weak pages.

## Smaller items

- `robots` meta: `max-snippet:-1` and `max-image-preview:large` let engines quote and preview.
- Web app manifest and icons: polish, not ranking.
- `hreflang` only when real translated pages exist.
- Images: descriptive `alt`, explicit width and height, modern formats.
