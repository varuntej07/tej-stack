# Measuring real-time LLM latency from production

The goal is one table per path that a second run can reproduce exactly: the same query, the
same window length, the same percentile method.

## Where the numbers live

Start with what the repo already writes. Look for a per-call log row from the model choke point
(latency, model, tokens, cached tokens, status), a per-turn summary row with stage marks, the
LLM tracer, and client timers in product analytics.

| Source | How to pull | Percentile in place |
|---|---|---|
| Google Cloud Logging | `gcloud logging read '<filter>' --project <id> --freshness 14d --format json`, then a throwaway script | no; compute locally or route logs to BigQuery |
| BigQuery (log sink, Crashlytics, analytics export) | `bq query --nouse_legacy_sql` | `APPROX_QUANTILES(x, 100)[OFFSET(95)]` |
| AWS CloudWatch Logs Insights | `aws logs start-query` | `pct(field, 95)` |
| Datadog, Grafana, Prometheus | API or `histogram_quantile(0.95, rate(<metric>_bucket[5m]))` | yes, bucketed (state the bucket edges) |
| Langfuse, LangSmith, Helicone and similar tracers | public API export of generations or traces | some dashboards; export raw rows anyway |
| PostHog | HogQL `quantile(0.95)(properties.<field>)` | yes |
| Provider consoles | usage and logs pages | rarely latency percentiles; use for cache and token checks |
| Voice frameworks (LiveKit Agents) | the framework's metrics events, logged per turn | no; log them and compute |

If the only evidence is code, say "unmeasured" and propose the smallest log-only stage mark.
Never conclude latency from source alone.

## Computing percentiles

- Use raw per-request rows. Compute with linear interpolation (numpy default) or nearest rank,
  and print which.
- Print n next to every percentile. p95 needs n of at least 20; p99 needs n of at least 100.
  Below that, print the max and "n too small" in the cell.
- Never average percentiles across segments, days or instances. Pool the raw rows and recompute.
- Keep cold starts, retries and fallbacks in the data. Segment them out as their own rows rather
  than deleting them; the tail is where they live.
- Write the throwaway script in the session scratchpad and keep it out of the repo. Paste the
  query into the report so a recheck reruns it unchanged.

## Stage decomposition

The number a person feels is the time to the first visible output (or the full applied result
when nothing streams). Break it down so each change can target one stage:

| Stage | Definition | Typical source |
|---|---|---|
| Client to server | client timer minus server total | client analytics vs server row |
| Pre-model | request in to the model call (auth, entitlement, reads, writes, retrieval, prompt build) | server stage marks |
| Connect | DNS, TCP and TLS to the provider (near zero on a reused connection) | client lifetime, SDK debug log, or the delta between first and later calls |
| Provider first event | model call to the first stream event of any kind | per-call row |
| Thinking gap | first event to first visible text or tool call | per-turn row with both timestamps |
| Generation | first visible token to last; roughly output tokens times time per output token | per-call row |
| Tool rounds | each tool execution plus the next model call | per-turn row |
| Voice turn | end-of-utterance delay + LLM time to first token + TTS time to first byte | voice framework metrics |

Segment every stage by model, effort or thinking level, surface (web, desktop, phone, keyboard),
tool versus no-tool turns, and cache hit versus miss. A path whose no-tool p50 is fine but whose
tool turns are slow has a different fix from one that is slow everywhere.

## Cache and token checks

Latency and caching are the same investigation on long prompts. Pull cached input tokens next to
latency: Anthropic `usage.cache_read_input_tokens` and `cache_creation_input_tokens`, OpenAI
`usage.input_tokens_details.cached_tokens` (or `prompt_tokens_details.cached_tokens`), Gemini
`usageMetadata.cachedContentTokenCount`. Zero cached tokens on a long, repeated prefix is a
finding; a high hit rate rules caching out as the fix.

## Before and after

- Same window length, same filters, same method. The "after" window starts once the serving
  version contains the change, not at the commit time.
- Report p50 and p95 deltas with both n values. A move smaller than the day-to-day spread of the
  "before" window is "no measurable change", not a win.
- A single request, a local run or a synthetic benchmark can explain a mechanism. It cannot be
  the before and after.
