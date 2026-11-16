# Official sources

Fetched 2026-11-15 while building this skill. Re-fetch on every run and cite the URL with the
fetch date; never cite a default or threshold from memory. Some URLs redirect (OpenAI moved to
`developers.openai.com`, Google AI docs to `aistudio.google.com`, Anthropic to
`platform.claude.com`); follow the redirect and cite the final URL.

| Topic | URL | What it backs |
|---|---|---|
| Anthropic, reducing latency | https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency | TTFT and baseline latency definitions; choose the model; shorter prompts and outputs; `max_tokens`; streaming |
| Anthropic, effort | https://platform.claude.com/docs/en/build-with-claude/effort | effort levels and per-model starting points; effort applies to thinking and tool calls; changing top-level effort can invalidate the cache |
| Anthropic, prompt caching | https://platform.claude.com/docs/en/build-with-claude/prompt-caching | automatic top-level `cache_control`; 4 breakpoints; minimum prefix per model; TTLs; invalidation order; usage fields; `max_tokens: 0` warm-up |
| Anthropic, streaming | https://platform.claude.com/docs/en/build-with-claude/streaming | event types, thinking deltas |
| Anthropic Python SDK | https://platform.claude.com/docs/en/api/sdks/python | default retries (2) and which errors; default 10 min timeout; timeouts are retried; client lifecycle and HTTP client options |
| OpenAI, latency optimization | https://developers.openai.com/api/docs/guides/latency-optimization | the seven principles; predicted outputs; WebSocket mode; measure p50 and p95 by model and task |
| OpenAI, prompt caching | https://developers.openai.com/api/docs/guides/prompt-caching | 1,024-token minimum prefix; static first; stable tools; `cached_tokens` |
| Gemini, optimization | https://aistudio.google.com/docs/optimization | priority, standard and flex tiers; implicit and explicit caching improve TTFT |
| Gemini, thinking | https://aistudio.google.com/docs/thinking | thinking levels and budgets per model |
| LiveKit Agents, metrics | https://docs.livekit.io/agents/ops/logging/ | `end_of_utterance_delay`, `transcription_delay`, LLM `ttft`, TTS `ttfb`, `e2e_latency`, the turn latency formula |
| LiveKit Agents, turns | https://docs.livekit.io/agents/build/turns/ | turn detector, endpointing `min_delay` and `max_delay`, VAD-only mode |
| Dean and Barroso, The Tail at Scale (CACM 2013) | https://www.barroso.org/publications/TheTailAtScale.pdf | why tails dominate at fan-out; hedged and tied requests |

## Secondary sources used for method only

- ClickHouse, "LLM inference latency: TTFT, tokens per second, and what to measure":
  percentiles over raw events, never means; end-to-end = TTFT + (output tokens - 1) x TPOT.
- arXiv 2508.10251, "Meta-metrics and best practices for system-level inference performance
  benchmarking": report percentiles across a realistic workload.

Neither is cited as the reason for a change; a plan line always points at a provider doc or the
user's own production numbers.
