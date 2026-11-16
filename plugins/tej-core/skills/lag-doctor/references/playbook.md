# Latency levers, in stage order

Each lever names the stage it moves, what the official source says, how to check the code, and
the field that proves it worked. Re-fetch the source before citing it: model names, defaults
and thresholds change between releases. Anything marked "gated" can change answer quality and
needs a preregistered eval before it ships.

## 1. Before the model

| Lever | What to check | Proof it worked |
|---|---|---|
| Run independent pre-model work concurrently (OpenAI latency guide: "Parallelize") | serial awaits on reads, retrieval, embedding, transcript writes | pre-model stage p50 |
| Move writes the answer does not need off the critical path | a transaction or analytics write before the model call | pre-model stage p50 |
| Don't default to an LLM (OpenAI: answer from code when the answer is known) | an LLM call for a lookup, a template or a classification a rule can make on structural facts | the call disappears from the path |
| Mark the stages | one timer around the whole prompt build hides which part is slow | stage marks appear in the log row |

## 2. Connection

| Lever | What to check | Proof it worked |
|---|---|---|
| One SDK client per process, reused (SDK clients pool connections; a client per request pays a fresh TCP and TLS handshake) | client constructed inside the request handler | provider first event p50 drops on warm instances |
| Keep-alive longer than the gap between calls | HTTP client idle expiry (some default to a few seconds) | same |
| Retries stacked once (Anthropic Python SDK retries connection errors, 408, 409, 429 and 5xx twice by default; a hand loop on top multiplies attempts) | SDK `max_retries` left at default under an own retry loop | worst-case attempts per request, tail p99 |
| Warm the connection on an intent signal (focus, mic start, screen open), unauthenticated, with a cooldown | the first request after idle pays the handshake | first-request-after-idle p50 |
| Server close to the provider region | cross-region hops on every call | connect stage |

## 3. Prefill (input)

| Lever | Source | What to check | Proof |
|---|---|---|---|
| Prompt caching, Anthropic | Prompt caching docs: top-level `cache_control` for automatic caching of the growing conversation; up to 4 breakpoints; minimum cacheable prefix per model; 5 min default TTL, 1 h at a higher write price; tools, system, messages invalidate in that order; changing effort or thinking settings invalidates | breakpoints only on short system blocks, a conversation that is never cached, a timestamp early in the prompt | `cache_read_input_tokens` > 0 and first event p50 |
| Prompt caching, OpenAI | Prompt caching guide: automatic on exact prefixes from 1,024 tokens; keep the static part first, append rather than rewrite; keep the `tools` list stable | dynamic content at the top, reordered tools | `cached_tokens` |
| Implicit caching, Gemini | Gemini optimization docs: implicit caching on 2.5 and newer when the prefix is identical; explicit caches for large shared context | a system instruction that changes per request | `cachedContentTokenCount` |
| Fewer input tokens (Anthropic reduce-latency guide, OpenAI "use fewer input tokens") | gated: trimming instructions or history can change behavior | input token count and first event p50 |
| Cache warm-up (Anthropic: a `max_tokens: 0` request writes the cache without output) | only where the first turn's miss is the measured pain | first-turn first event |

## 4. Thinking

| Lever | Source | Proof |
|---|---|---|
| Effort per route (Anthropic effort docs: lower effort means less and shorter thinking and fewer tool calls; Haiku 5.5's guidance names `low` for chat and short tool tasks; hold top-level effort constant inside a cached conversation) | gated | thinking gap p50 and p95 |
| Thinking off or deferred where supported (Anthropic: `thinking: {"type": "disabled"}` on Haiku 5.5 at `high` or below; `between_tools` on Sonnet 5.5) | gated | first visible token p50 |
| Reasoning effort, OpenAI (latency guide: lower `reasoning.effort` for routine tasks) | gated | same |
| Thinking level, Gemini (`minimal` or `low` for latency-sensitive extraction and classification) | gated | same |

Read the thinking gap, not just total latency: a fast first event followed by seconds of
thinking looks healthy on a provider dashboard and slow to the user.

## 5. Output

| Lever | Source | Proof |
|---|---|---|
| Fewer output tokens: ask for shorter answers, request only needed fields (structured outputs), cap `max_tokens` where the answer is short (Anthropic reduce-latency guide; OpenAI "generate fewer tokens") | gated when it changes the answer | output tokens and generation time |
| Predicted outputs for edits where most text is known (OpenAI) | provider-specific | generation time |
| Faster model or tier (Anthropic: choose the right model; OpenAI fast modes; Gemini priority tier) | gated, and costs more for priority tiers | first visible token and generation |

## 6. Round trips

| Lever | Source | Proof |
|---|---|---|
| Combine sequential calls when one request has everything it needs (OpenAI "make fewer requests") | gated | calls per user action |
| Parallel tool execution when the model emits several independent calls | none needed | tool round time |
| Persistent connection for multi-step tool loops (OpenAI WebSocket mode) | provider-specific | per-round overhead |

## 7. Perceived wait

| Lever | Source | Proof |
|---|---|---|
| Stream and render the first token at once (Anthropic and OpenAI both list streaming) | a server or client buffer that holds text until done, or a narration buffer larger than needed | client time to first visible token |
| Show progress during thinking or tool rounds | silent spinners | client-side abandonment, if tracked |

## 8. Tail (p95, p99)

| Lever | Source | Proof |
|---|---|---|
| Per-attempt timeout plus a fallback that fires before the first token, never one outer timeout around a whole chain | resilience profile of the path | p99 and fallback rate |
| Stop retrying a dead leg (circuit breaker or health check) | provider error rate by model | wasted attempts per request |
| Hedged requests after the p95 delay (Dean and Barroso, "The Tail at Scale", 2013: hedging at p95 cut a p99 from 1,800 ms to 74 ms for about 2% extra load) | only for cheap, idempotent, side-effect-free calls; an LLM call doubles spend on every hedge, so show the cost math | p99 and spend |
| Priority processing tiers (Gemini priority tier, OpenAI priority processing) | paid; state the price multiplier | p95 and p99 |

## 9. Voice

LiveKit Agents defines a turn as `end_of_utterance_delay + llm ttft + tts ttfb` and also reports
`e2e_latency` per message. Tune each term separately: turn detection mode and endpointing
`min_delay` and `max_delay`, the LLM's time to first token (every lever above), TTS time to
first byte (streaming TTS, warm connection). A voice change that adds latency anywhere is
usually a hard no; check the repo's rules.
