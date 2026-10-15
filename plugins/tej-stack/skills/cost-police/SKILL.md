---
name: cost-police
description: Find where a codebase wastes money on LLM tokens, metered services, and cloud infrastructure, show the dollar math for every finding with live prices cited from official pages, flag where one bug or one abuser could run up the bill, and refuse savings claims that cannot be verified. Use for requests about a bill that is too high or doubled, API costs, token spend, a surprise or runaway bill, a Firebase, Firestore, AWS, GCP, Azure, Vercel, Supabase, Twilio, OpenAI, Anthropic, or Gemini bill, cost per user or per request, whether a free tier is affordable, whether this could bankrupt me at launch, denial of wallet, Terraform, CloudFormation, CDK, Pulumi, or serverless cost, infra cost, or cutting cloud spend. Also triggers on speech-to-text forms like cost police, coast police, cost-pleas, or cost please. Time and memory complexity questions go to big-o-police. Report only by default; change code or infrastructure only when the user explicitly asks for fixes.
---

# Cost Police

> **Update check (run silently before the audit):** run `bash "<this skill's directory>/../../bin/check-update.sh"` and read its single `TEJ_STACK:` status line. If it reports `UPGRADE_AVAILABLE`, tell the user once, in one line, that a newer Tej Stack is available and they can upgrade with `/plugin update tej-stack@tej-stack` (changes listed in the repo's CHANGELOG.md), then continue this task normally. On `UP_TO_DATE` or `CHECK_SKIPPED`, or if the script is missing or errors, say nothing and continue. The check must never block, delay, or fail the task.


Find where the money goes, where one mistake could make it go much faster, and what each fix is worth in dollars, with the arithmetic shown. The mandate is not to make the bill smaller at any price. It is to name the call site, price it from a live official source, show the math, and say plainly when a saving cannot be proven.

Default to a report. Do not edit code, prompts, or infrastructure unless the user explicitly asks for fixes.

**The failure this skill exists to prevent is not a high bill. It is a confident dollar figure nobody can check.** A made-up saving reads exactly like a real one. Every number must carry its prices, its volume, and a way to be proven wrong.

## 1. Three lenses

| Lens | The question | Catalog |
|---|---|---|
| **Token and API waste** | Where does steady spend leak on LLM and metered API calls? | [references/waste-catalog.md](references/waste-catalog.md) |
| **Runaway risk** | Where could one bug, one loop, or one abuser multiply the bill overnight? | [references/blast-radius.md](references/blast-radius.md) |
| **Infrastructure** | What do the IaC and platform configs cost while idle, and what is oversized? | [references/infra-catalog.md](references/infra-catalog.md) |

Run every lens that applies to the repo. A repo with no IaC skips the third lens and says so. Runaway risk is never skipped when the code calls anything billed per use.

## 2. Inventory before opinions

Start from what the code actually calls, not from a list of tips. In the commands below, `SKILL_DIR` is the folder that contains this file. Use `python3`, or `python` on Windows. The script needs only the Python 3.9+ standard library.

```bash
python3 SKILL_DIR/scripts/scan_costs.py <repo>
python3 SKILL_DIR/scripts/scan_costs.py <repo> --json
python3 SKILL_DIR/scripts/scan_costs.py <repo> --find <pattern>
```

The scanner lists LLM SDK call sites, model ids, whether `max_tokens`, caching, or batch usage appear nearby, calls inside loops, metered services (Firestore, function triggers, storage ACLs, SMS), and IaC resources. **Everything it prints is a candidate, not a finding.** Read the source of every candidate you keep. Then trace each billed call back to its entry point: which user action, job, or schedule triggers it, and how many times.

If the scanner is unavailable, search for the same things by hand: SDK imports, model id strings, `onSnapshot`, trigger decorators, `resource "`, `AWS::`, and SMS or verify calls.

## 3. Price it live, every run

Prices change often, differ by model, region, and tier, and have been wrong in every model's memory at least once. Fetch them.

1. Open the official pricing page for each provider the code uses, from [references/pricing-sources.md](references/pricing-sources.md). Record the URL and the fetch date next to every price you use.
2. For IaC, prefer `infracost breakdown --path <dir>` when the Infracost CLI is installed, and cite Infracost as the source. Otherwise use the provider's public price API or pricing page and say which.
3. Match the exact SKU: model id, region, tier (standard, batch, flex, fast), cache write versus cache read, and any long-context or data-residency multiplier.
4. **No web access:** ask the user for the prices, or mark the finding `unpriced` and keep the token or unit math. Never fill in a price from memory.

## 4. Build the cost model

For every call site that survives section 2, build the model in [references/cost-model.md](references/cost-model.md):

- **Units per call:** input and output tokens (from the provider's token counting endpoint when available, otherwise characters divided by 4, labeled as an estimate), or reads, writes, invocations, GB, messages.
- **Calls per action:** fan-out, retries, tool-loop turns, history resent each turn.
- **Actions per period:** from a billing export, a provider usage CSV, logs, analytics, or a number the user states. Label each source.
- **Cache hit rate**, when caching exists, from usage fields rather than hope.

Show the multiplication for every dollar figure. If volume is unknown, stop at cost per call and cost per user action, and say what number would turn it into a monthly figure.

## 5. Refusal rules, hard

A finding may only be reported if **all four gates** hold. Otherwise list it as a non-finding with the gate that stopped it. The full checklist is in [references/refusal-rules.md](references/refusal-rules.md).

1. **Gate 1, the spend is real.** The call site is reachable from a real entry point, with the trigger named.
2. **Gate 2, the price is cited.** A live official source with URL and date, or the user's own number. Otherwise the finding is `unpriced`.
3. **Gate 3, the volume is sourced** for any monthly or yearly figure. No volume means per-call and per-action cost only.
4. **Gate 4, there is a refute check.** Name the usage field, log query, billing line, or plan output that would prove the finding wrong.

Refuse outright, and say why:

- A monthly saving with no real volume behind it.
- A cheaper-model recommendation with no quality eval. A bigger model that writes fewer output tokens can cost less; propose an A/B run instead.
- A semantic or response cache for personalized or multi-turn chat.
- A token-format trick (a new serialization, prompt compression) with no measured before-and-after token count.
- Self-hosting a model with no infrastructure plus operations cost math.
- Calling any billing alert a cap. Alerts lag and do not stop spend. A spend cap only covers the services its provider lists; check that the service in question is one of them.

## 6. Report

Open with a headline: estimated spend for the period as a range when volume is known, otherwise "per-action costs only, volume not provided".

Then a ranked table, ordered by dollar impact multiplied by confidence:

| # | Lens | Site | Cost now | After fix | Confidence |
|---|---|---|---|---|---|

Runaway risks go in the same table. Their "cost now" is the worst case for a stated scenario (one abuser at the rate limit you found, one self-trigger loop for 24 hours), labeled as a scenario, not a forecast.

For each finding, a card:

1. **Site:** `file:line`, and the entry point that triggers it.
2. **Evidence:** what the code does, quoted or summarized from the source you read.
3. **Math:** units x calls x volume x price, with each price's URL and date and each assumption labeled.
4. **Fix:** the smallest change, and what it trades (latency, freshness, complexity, a new failure mode).
5. **Confidence:** high, medium, or low, and why.
6. **Refute it:** the exact check that would prove the finding wrong, for example "if usage shows `cache_read_input_tokens` above zero on this route, this finding is wrong."

Then, in order:

- **Infrastructure:** the IaC lens as its own section, with the pricing source (Infracost or the provider API) named once at the top.
- **Not checked:** everything you could not price, trace, or confirm, and what would unblock it. This section is not optional.
- **Deliberate non-findings:** what you examined and refused, one line each, with the gate or rule that stopped it.
- **Next actions:** at most five, ordered by dollars saved per hour of work.

## 7. If asked to fix

Smallest verifiable change first, one change per step. Before each change, state the usage field or billing line you expect to move and in which direction. After it, show how to confirm: the usage response fields, a token count of the new prompt, an `infracost diff`, or a plan output. Never apply an infrastructure change, change a model, or alter a rate limit without the user's explicit go-ahead for that specific change.
