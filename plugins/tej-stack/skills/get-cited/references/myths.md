# Myths, with receipts

The refusal list. Each entry names the tactic, the strongest evidence against it, and the honest steelman, because a refusal that hides the steelman is just a different kind of confidence trick. The single strongest primary source across this file is Google's own guide to AI features on Search: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide.

## 1. llms.txt as a visibility lever

**The claim:** add an `/llms.txt` Markdown index (proposed by Jeremy Howard, https://llmstxt.org) and AI engines will understand and cite the site.

**The evidence against:**
- Google, verbatim: "You don't need to create new machine readable files, AI text files, markup, or Markdown to appear in Google Search ... Google Search ignores them."
- John Mueller compared it to the keywords meta tag and noted no AI service has said it uses the file, and server logs show they do not even check for it (https://www.searchenginejournal.com/google-says-llms-txt-comparable-to-keywords-meta-tag/544804/).
- The Ahrefs log study of 137,210 domains (May 2026, https://ahrefs.com/blog/llmstxt-study/): 28% of domains had an llms.txt; **97% of those files received zero requests**; of the requests that did arrive, 77% came from non-AI tools like SEO auditors.

**The steelman:** the same Ahrefs study found the one real consumer is coding agents (Claude Code fetching developer docs). For a developer-documentation site serving coding agents, an llms.txt is a cheap, harmless convenience. That is the full extent of the evidence. Ship one for that reason if you like; never report it as a citation-visibility fix.

## 2. "Chunk your content for RAG"

**The claim:** break pages into small fragments so retrieval systems can index them.

**The evidence against:** Google, verbatim: "There's no requirement to break your content into tiny pieces ... Google systems are able to understand the nuance of multiple topics on a page." Chunking is a real concern inside a RAG pipeline, and it belongs to the engine at index time. No engine documents a publisher-side chunk-size input.

**The steelman:** the kernel of truth is extractability, which is real and measured: self-contained passages get quoted (see [content-patterns.md](content-patterns.md)). Write self-contained sections on normal-length pages. Do not shred a coherent page into forty stubs.

## 3. Rewriting prose "for AI" and exact-match question stuffing

**The evidence against:** Google, verbatim: "AI systems can understand synonyms and general meanings ... you don't have to worry that you don't have enough 'long-tail' keywords or haven't captured every variation." And the GEO paper measured keyword stuffing at **-8.7% visibility**, the only tested method that lost ground (https://arxiv.org/abs/2311.09735).

**The steelman:** the same paper proves some content changes work (statistics, quotations, citations, fluency). "Write for AI" is not fully myth; the keyword-density and phrase-variant form of it is.

## 4. Schema stuffing and invisible markup

**The claim:** load pages with FAQ or other JSON-LD, including questions no visitor sees, to feed the machines.

**The evidence against:** Google's structured data policy: "Don't mark up content that is not visible to readers of the page"; violations risk spam manual actions (https://developers.google.com/search/docs/appearance/structured-data/sd-policies). FAQ rich results were deprecated for nearly all sites in August 2023 (https://developers.google.com/search/blog/2023/08/howto-faq-changes). And for AI specifically: "Structured data isn't required for generative AI search, and there's no special schema.org markup you need to add."

**The steelman:** accurate schema mirroring visible content still earns rich results, feeds the Knowledge Graph, and clarifies entities. See [schema-playbook.md](schema-playbook.md) for the short list that earns its keep.

## 5. A page per query variant

**The evidence against:** Google names this exact tactic in the AI guide as a violation of the scaled content abuse spam policy (https://developers.google.com/search/docs/essentials/spam-policies), the policy behind the March 2024 update that cut low-quality content in results by a reported 45%. It is also pointless: AI Mode's query fan-out reads one good page for many sub-questions.

## 6. Buying mentions, fake reviews, parasite placements

**The evidence against:** Google's spam policies apply to AI Overviews and AI Mode; the site reputation abuse policy covers parasite placements (https://blog.google/company-news/inside-google/company-announcements/defending-search-users-from-parasite-seo-spam/); the FTC finalized a rule banning fake reviews in August 2024. Genuine third-party presence (real Reddit answers, real reviews, real comparisons) is a measured citation channel; manufactured versions of it are the same tactic as link schemes and get policed the same way, with legal exposure on top.

## 7. Tools selling an "AEO score" from internal AI metrics

**The evidence against:** Google, verbatim: "Be wary of third-party tools that promise ranking success or claim to use 'internal' Google metrics. No third-party tool has access to our internal ranking or AI systems."

**The steelman:** external measurement by prompt sampling is legitimate and useful (see [measurement.md](measurement.md)). The myth is the claim of internal access or guaranteed scores, not measurement itself.

## The tell

Every entry above shares a shape: a plausible mechanism, zero published evidence of effect, and a vendor selling the fix. When a new tactic appears, ask the same three questions. Which engine documents reading this? Who measured an effect, with what method? Who profits if I believe it without an answer to the first two?
