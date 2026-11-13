# Schema playbook

Structured data is not an AI-visibility requirement. Google states it plainly: "Structured data isn't required for generative AI search, and there's no special schema.org markup you need to add" (https://developers.google.com/search/docs/fundamentals/ai-optimization-guide). Schema earns its place for rich results, entity clarity, and feeds. Recommend it for those reasons, at that priority, and never above a retrievability fix.

## The one hard rule

**Markup mirrors visible content.** Every fact in the JSON-LD appears on the rendered page a human can read. Google's policy: "Don't mark up content that is not visible to readers of the page"; violations risk a spam manual action (https://developers.google.com/search/docs/appearance/structured-data/sd-policies). Hidden-question FAQ blocks, ratings no reviewer gave, and prices not on the page are findings **against** a site, not optimizations.

## Types that earn their keep

- **Organization** (on the home or about page): legal name, alternate names, logo, `sameAs` links to the real social and directory profiles, contact points. This is entity disambiguation: it helps every engine resolve "who is this" and corroborate facts across the web. The highest-value markup for a brand that wants to be cited by name.
- **Product / Offer** with real price, availability, and honest review data, ideally backed by a Merchant Center feed for commerce. Google's AI guide explicitly points at Business Profile and Merchant Center feeds as the way product and local data reaches AI experiences.
- **Article / BlogPosting**: headline, author as a `Person` with a real profile URL, `datePublished` and `dateModified` that match the visible dates.
- **LocalBusiness** for physical businesses: NAP (name, address, phone) that exactly matches the Google Business Profile and other directories. Inconsistent NAP is an entity-legibility bug.
- **BreadcrumbList**, and **VideoObject** where video is real content.

**FAQPage:** rich results were deprecated for all but a narrow set of sites in August 2023 (https://developers.google.com/search/blog/2023/08/howto-faq-changes). Valid to keep if the questions are genuinely on the page; never a recommendation for AI visibility, and a finding if the questions are invisible.

## Minimal honest examples

Organization:

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Acme Analytics",
  "url": "https://acme.example",
  "logo": "https://acme.example/logo.png",
  "sameAs": [
    "https://github.com/acme",
    "https://www.linkedin.com/company/acme",
    "https://en.wikipedia.org/wiki/Acme_Analytics"
  ]
}
```

Article (author and dates must match what the page shows):

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "How we cut cold-start latency 60%",
  "author": { "@type": "Person", "name": "Varun Tej", "url": "https://acme.example/team/varun" },
  "datePublished": "2026-08-14",
  "dateModified": "2026-09-02"
}
```

## Validation

- https://validator.schema.org for syntactic validity of any type.
- https://search.google.com/test/rich-results for Google-eligibility of rich-result types.
- The mirror check is manual and mandatory: for each JSON-LD claim, point to where the rendered page shows it. And because AI crawlers read raw HTML only, JSON-LD injected by client-side JavaScript fails the same retrievability test as any other client-rendered content; it must be in the server response.
