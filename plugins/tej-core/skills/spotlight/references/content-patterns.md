# Content patterns with measured citation impact

What actually moves a page's chance of being cited, ranked by strength of evidence. Separate the measured from the folklore in every report; the folklore section at the bottom lists numbers that circulate without a traceable method.

## Experimentally tested: the GEO paper

"GEO: Generative Engine Optimization" (Aggarwal et al., KDD 2024, https://arxiv.org/abs/2311.09735) rewrote one source per query across 10,000 queries and measured visibility change in the generated answer. Results against baseline, on position-adjusted word count:

| Method | Visibility change |
|---|---|
| Quotation addition (quotes from credible sources) | **+42.6%** |
| Statistics addition (numbers replacing qualitative claims) | **+32.8%** |
| Fluency optimization | +28.7% |
| Cite sources (add citations to credible sources) | +27.7% |
| Technical terms | +18.5% |
| Easy-to-understand rewriting | +13.8% |
| Authoritative tone | +11.8% |
| **Keyword stuffing** | **-8.7%** |

Three findings matter beyond the table:

1. **Keyword stuffing lost visibility.** The one classic-SEO tactic tested made things worse.
2. **Effects vary by domain.** Authoritative tone won in debate and history; fluency in business and science; citations in law and factual queries; statistics in law, debate, and opinion. Do not apply one method uniformly.
3. **Lower-ranked pages gain the most.** Cite-sources moved rank-5 sources +115% while rank-1 sources lost ground. Content optimization is the underdog's lever.

Caveat to carry into reports: the paper used a simulated GPT-based engine, not production AI Overviews. A 2026 e-commerce follow-up (E-GEO, https://arxiv.org/abs/2511.20867) found optimized rewrites converge on a stable pattern and that gains reflect genuine content improvement rather than manipulation.

## Measured at scale: where citations land on a page

Sentence-level study of 3M ChatGPT responses with 18,012 verified citation matches (Kevin Indig, coverage at https://searchengineland.com/chatgpt-citations-content-study-469483):

- **44.2% of citations come from the first 30% of the page**; only 24.7% from the final third. Front-load the answer, the key statistic, and the framing. (A "55%" variant of this stat circulates for AI Overviews via derivative coverage; quote the verified 44.2% ChatGPT number.)
- **78.4% of question-associated citations traced to headings.** A heading phrased as the real question, with a self-contained one-to-two sentence answer directly beneath it, is the single most citable structure.
- Cited passages are entity-dense (~20.6% proper nouns vs a typical 5-8%), use definitional "X is" phrasing about twice as often, and sit near grade-16 readability: clear but not dumbed down.

A passage-level study of what AI answers quote verbatim (Advanced Web Ranking, https://www.advancedwebranking.com/blog/passages-quoted-vs-passages-absorbed-in-ai-answers, small n, treat as indicative) found engines quote **structured, self-contained single units** most: statistic lines, definitions, list items, table rows. Flowing narrative prose is quoted least. Name the entity in subject position in the first sentence under each heading.

## Measured at scale: what kinds of pages and sources get cited

- **Ranking is no longer sufficient or necessary.** Only 38% of AI Overview citations come from top-10 ranking pages (Ahrefs, 863K SERPs, https://ahrefs.com/blog/ai-overview-citations-top-10). Google's query fan-out cites pages that answer the sub-questions, not just the head query.
- **Brand mentions out-predict backlinks.** Across 75K brands, web mentions correlate 0.664 with AI Overview brand visibility; backlinks only 0.218 (https://ahrefs.com/blog/ai-overview-brand-correlation/). Correlational, but the gap is large and consistent.
- **Third-party surfaces carry huge citation share.** Perplexity's top sources are Reddit-dominated, ChatGPT's Wikipedia-dominated (Profound, 680M citations, https://www.tryprofound.com/blog/ai-platform-citation-patterns). A large share of winnable citations live on pages you do not own: Reddit threads, comparison listicles, review sites, YouTube. That is earned-media work, not on-page work, and an audit should say so rather than pretend on-page fixes cover it.
- **Format is domain-contingent.** Listicles took 61% of citations in B2B tech and roughly 0% in healthcare in the same study (DeltaV, 25K citations, https://www.deltavdigital.com/resources/reports/ai-citation-study/). Check what formats are being cited in the site's own category before prescribing one.
- **Freshness matters unevenly.** AI-cited URLs average ~26% younger than Google organic results; ChatGPT and Perplexity skew freshest, AI Overviews roughly match organic (Ahrefs, 17M cited URLs). Visible, honest dates on content whose answer changes over time; no fake date bumping.

## The practical writing checklist this evidence supports

1. Direct answer in the first screenful, before the wind-up.
2. Headings that are the reader's actual questions; a complete, self-contained answer in the next one or two sentences.
3. Replace qualitative claims with first-party numbers wherever the site has data. Original statistics are both a GEO win and the thing nobody else can copy.
4. Quote named, credible sources; cite them with links.
5. One idea per paragraph; each claim self-contained enough to survive extraction without its neighbors.
6. Tables for comparisons, lists for enumerations, a statistic on its own line.
7. Entity clarity: name the company, product, and subject explicitly instead of "we" and "it."
8. Visible author, visible date, and something first-hand that a summary of other pages cannot reproduce. Google's people-first guidance (https://developers.google.com/search/docs/fundamentals/creating-helpful-content) says commodity restatement is exactly what gets skipped.

## Folklore: do not quote these

Numbers that circulate in vendor blogs with no traceable methodology: "lists get 68% more citations," "tables have 96% AI-parsing accuracy," "Q&A structure adds 45% visibility," and any flat "FAQ schema boosts AI citations" claim. If a client repeats one, trace it; if it dead-ends in a marketing post, say so in the report.
