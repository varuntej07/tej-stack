# Token and API waste catalog

Use this catalog after the inventory, to recall what to check at a call site you have already read. It is not a list of tips to recommend everywhere. Each entry says how to detect it, how to price it, what the fix trades, and what would prove the finding wrong.

Provider mechanics below were checked against official docs, but numbers change. **Always confirm the current multiplier, minimum, and discount on the pricing page you fetched this run** before using it in math.

---

## Ranked by observed payoff

### 1. A stable prefix sent uncached on every call

**Looks like:** a long system prompt, tool list, document, or few-shot block that is identical across requests, with no caching configured. Or caching configured, but something variable (a timestamp, a request id, the user's name, a shuffled tool list) sits before the stable part and breaks the prefix.

**Provider mechanics to confirm on the live page:**
- Anthropic: caching is opt-in. A top-level `cache_control` turns on automatic caching; block-level `cache_control` places explicit breakpoints. Cache writes cost more than base input and cache reads cost a fraction of it; the read multiplier differs by model. There is a minimum cacheable length and a short default TTL with a longer paid option.
- OpenAI: cached input is billed at a discount on supported models; caching is applied to repeated prefixes automatically.
- Gemini: the pricing page lists a context caching price per model; some models support implicit caching only.

**Price it:** stable tokens x calls per period x (base input price minus cache read price), minus the cache write cost for each cache refresh. Include the refresh rate: traffic slower than the TTL means most calls pay the write price, not the read price.

**Trade:** prompt ordering constraints (variable content must come last), a write premium on cold traffic.

**Refute it:** the usage object on real responses. On Anthropic, `cache_read_input_tokens` above zero on this route means caching already works. On OpenAI, the cached token count in the usage details. If the cache hit rate is already high, the finding is wrong.

### 2. Output with no ceiling, or more output than the product uses

**Looks like:** no `max_tokens` (or the provider's equivalent), a prompt that invites long answers when the UI shows two lines, a JSON response with verbose keys and repeated wrappers, or reasoning or thinking budgets set far above what the task needs.

**Price it:** output tokens are usually several times the input price. Measure actual output length from logs or usage fields, not from the prompt.

**Trade:** truncated answers if the ceiling is too low. Tie the ceiling to what the UI or the next step actually consumes.

**Refute it:** the distribution of `output_tokens` in usage logs. If p95 is already near what the product uses, the finding is wrong.

### 3. Offline work on the real-time tier

**Looks like:** nightly summaries, backfills, evals, embeddings, classification of a queue, report generation, anything a user is not waiting on, sent through the standard synchronous endpoint.

**Provider mechanics:** Anthropic, OpenAI, and Gemini all list a Batch tier on their pricing pages, at a large discount in exchange for asynchronous completion. Some providers also list a flex tier. Confirm the discount and the completion window.

**Price it:** offline calls per period x cost per call x the batch discount.

**Trade:** latency (results arrive within the provider's batch window, not seconds), a new polling or webhook path, partial-failure handling.

**Refute it:** show that a user or a downstream deadline waits on the result. If one does, it is not offline work.

### 4. The whole history resent every turn

**Looks like:** a chat or agent loop that appends every message and every tool result forever, so turn N pays for turns 1 to N-1 again. Cost grows quadratically with conversation length.

**Price it:** sum of input tokens across turns for a realistic session length, from logs if available. Compare with caching the stable prefix (entry 1), trimming tool results, or summarizing old turns.

**Trade:** summarization loses detail; trimming tool results can drop facts the model later needs.

**Refute it:** session length distribution. If nearly all sessions are two or three turns, growth does not matter yet.

### 5. N+1 model calls

**Looks like:** one model call per item in a loop (per row, per file, per comment) where one call over the batch, or a cheaper deterministic step, would do. The scanner flags calls inside loops as candidates.

**Price it:** items per action x per-call overhead (the repeated system prompt and instructions are paid N times).

**Trade:** one large call fails as a unit, has a longer latency, and may hit context limits. Quality can change; check it.

**Refute it:** count model calls per user action in logs. If the count does not grow with items, the loop is not on the billed path.

### 6. Identical calls with no memoization

**Looks like:** the same deterministic input (a product description, a static doc, a fixed classification) sent to the model again on every request or every deploy. Embeddings recomputed for unchanged content.

**Price it:** duplicate calls per period x cost per call. Get the duplicate rate from logs (hash of the request body) before claiming it.

**Trade:** a cache needs an invalidation key (content hash plus model id plus prompt version). Without one, refuse.

**Refute it:** duplicate rate from logs. A low rate kills the finding. Never apply this to personalized or multi-turn content (see refusal rules).

### 7. Retrieval stuffing

**Looks like:** RAG that sends a fixed top-k of large chunks regardless of the question, whole documents where a section would do, or the same context sent to several chained calls.

**Price it:** retrieved tokens per call x calls. Measure, do not assume chunk sizes.

**Trade:** recall. Lowering k or chunk size can drop the answer. Requires an eval on real questions.

**Refute it:** an eval showing quality drops at the smaller context. If it does, the saving is not free and must be presented as a trade.

### 8. Agent and tool loops without a step limit

**Looks like:** `while` loops around tool use with no maximum turns, no budget check, and no stop on repeated identical tool calls. This is also a runaway risk; see [blast-radius.md](blast-radius.md).

**Price it:** median and worst observed turns per task x tokens per turn.

**Refute it:** a turn-count histogram. If the worst case is already small and bounded by something structural, the finding is low.

### 9. Model tier mismatch

**Looks like:** a frontier model used for a yes or no classification, routing, or extraction step.

**This is a hypothesis, never a finding on its own.** A bigger model can cost less per task when it writes fewer output tokens or needs fewer retries. Report it only as a proposed A/B run with a quality bar and a cost metric per completed task. See refusal rules.

### 10. Paid extras nobody looks at

**Looks like:** server-side tools billed per use (web search, code execution) enabled on routes that never need them; tool definitions sent on every call when the route uses no tools; data-residency or fast-mode pricing multipliers left on by default.

**Price it:** check each extra on the pricing page you fetched; some carry their own per-use fee, and every tool definition adds input tokens.

**Refute it:** the usage fields for server tool use, and whether the route's responses ever contain a tool call.

---

## Non-LLM metered APIs

The same shapes apply to anything billed per call: maps and geocoding, email and SMS, OCR, speech, translation, search APIs, vector databases billed per query. Look for per-item calls in loops, missing caching of deterministic results, and calls on page load that could run on demand.
