# Cost model

Every dollar figure in the report is a product of four factors. Write each one down with its source. A figure with an unlabeled factor is a guess.

```text
cost per period = units per call x calls per action x actions per period x price per unit
```

## 1. Units per call

**LLM tokens.**
- Best: the provider's token counting endpoint on the real prompt (Anthropic documents a count tokens endpoint; other providers document tokenizers or count fields). Label it `counted`.
- Good: the `usage` object from real responses in logs. Label it `observed`.
- Fallback: characters divided by 4 for English prose and code. Label it `estimate (chars/4)`. It drifts for other languages, JSON, and code with many symbols.
- Split input into stable prefix (cacheable), variable input, retrieved context, tool definitions, and history. Each behaves differently under caching and trimming.
- Output: take the observed distribution when logs exist. Without logs, use `max_tokens` as the ceiling and say the typical value is unknown.
- Add hidden tokens the provider documents: tool-use system prompts, tool definitions, images, reasoning or thinking tokens billed as output.

**Other metered units:** document reads and writes, invocations and GB-seconds, GB stored and GB transferred, messages sent, requests. Count them per call from the code path you read.

## 2. Calls per action

Trace one user action or one job run end to end and count billed calls:
- fan-out (one call per item, per chunk, per tool),
- retries (configured attempts multiplied by the observed failure rate, when known),
- agent or tool loops (turns per task),
- history resent per turn (turn N re-sends turns 1 to N-1 unless cached).

## 3. Actions per period

Use the first source available and name it:

| Source | Label |
|---|---|
| Billing export or invoice line items | `billing` |
| Provider usage dashboard or usage CSV export | `provider usage` |
| Application logs or traces with counts per route | `logs` |
| Product analytics (sessions, DAU, events) | `analytics` |
| A number the user stated | `user-stated` |

No source means no monthly figure. Report cost per call and cost per action, and say exactly which number would complete the math (for example: "daily chat turns on /api/chat").

## 4. Price per unit

From the live official page, per [pricing-sources.md](pricing-sources.md): the exact model id or SKU, region, tier, and the multiplier that applies (cache write, cache read, batch, long context, data residency, fast mode). Record URL and fetch date.

## 5. Caching math

```text
cost of the stable prefix per period =
    writes x prefix tokens x write price
  + reads  x prefix tokens x read price
```

- Writes happen on the first call and on every call after the cache expires. Low-traffic routes refresh often and gain less. Use the provider's TTL from the docs and the real request spacing.
- Take the hit rate from usage fields (cache read tokens versus total input tokens) whenever logs exist. Never assume 100%.
- Confirm the prefix meets the provider's minimum cacheable length.

## 6. Ranges, not points

When any factor is uncertain, carry a low and a high value through the math and report the range. State which factor drives most of the spread. A range from $40 to $400 a month with "volume is the unknown" is more useful than a confident $220.

## 7. Worked example, with every label

```text
Site: api/chat.ts:31, POST /api/chat, one call per user turn
Stable prefix: 6,000 tokens (counted, count tokens endpoint)
Variable input: ~400 tokens per turn (observed, 7-day logs, median)
Volume: 9,000 turns per day (provider usage export, last 30 days)
Price: input $X/MTok, cache read $Y/MTok, cache write $Z/MTok
       (vendor pricing page URL, fetched YYYY-MM-DD)

Now:   9,000 x 6,000 = 54.0M prefix tokens/day at $X/MTok
After: hit rate 0.95 (assumed, verify with cache read tokens after rollout)
       reads  = 0.95 x 54.0M at $Y/MTok
       writes = 0.05 x 54.0M at $Z/MTok
Saving per day = now minus after; per month = x 30
Refute: if cache_read_input_tokens > 0 on /api/chat today, caching already works.
```

Substitute the real prices from this run's fetch. Do not copy example numbers into a report.
