# Sources surveyed

Spotlight was built in November 2026 after surveying the public SEO and AEO agent skills,
then keeping only what has evidence or a documented engine behavior behind it.

| Source | Taken | Refused or changed |
|---|---|---|
| tej-stack `get-cited` | The citation chain, engine matrix, content patterns, measurement, myths (shared byte-identical) | Report-only stance: spotlight fixes after approval |
| AgriciDaniel/claude-seo | Category coverage (technical, content, schema, sitemap, performance, AI readiness), INP not FID, quality gates against thin and mass pages | 0 to 100 health score: a weighted number with no outcome validation; findings are ranked A/B/C instead |
| coreyhaines31/marketingskills (ai-seo, competitors, schema, seo-audit) | Alternatives page structure and honesty rules, dated competitor facts, citations versus recommendations, freshness signals, repeated probes (mention rate over n runs) | `/pricing.md` and llms.txt as rewarded by ChatGPT and Claude: no published measurement; refused per myths.md |
| artificialguybr/seo-geo-aso-agent-skill | Finding, evidence, impact, fix rubric; AI crawler check first; honest note that blocking GPTBot does not remove ChatGPT Search | ASO keyword mining: out of scope for a website skill |
| yanivgoldenberg/seo-geo-skill, metawhisp/amazing-seo-skill | Live per-engine citation tracking as a measurement idea | Scorers that award points for llms.txt presence |
| RankSpotAI/awesome-seo-agent-skills | Used as the index of the field | |
| Bing Webmaster and IndexNow docs; Google Search Central sitemap docs | IndexNow protocol and scope, lastmod accuracy rule, no Google ping | |

## Where they disagree

- **llms.txt**: several packs score it as an AI visibility win. Log studies show almost no
  engine requests it, and Google ignores it. Evidence side: refuse as a visibility fix.
- **FAQ schema**: packs still recommend it for rich results. Google limited FAQ rich results in
  2023 and later reports say they are gone. Evidence side: mark up visible FAQs only, expect no
  SERP feature.
- **Comparison listicles**: older packs recommend "top N alternatives" pages. Mid 2026 citation
  data shows ChatGPT moving toward official, primary-source pages. Evidence side: one honest
  page per real competitor.
