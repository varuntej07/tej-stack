# Refusal rules

The value of this skill is as much in what it declines as in what it finds. A cost audit full of plausible dollar figures is worse than none, because founders act on numbers. Every figure here gets copied into a spreadsheet or a pitch deck.

A finding passes only if **all four gates** hold. Otherwise it goes in the deliberate non-findings list with the gate that stopped it, or it is reported in reduced form (per-call cost, `unpriced`) and labeled as such.

---

## The four gates

### Gate 1, the spend is real

Name the entry point that triggers the billed call: a route, a screen, a job, a schedule, a trigger. Code that is unreachable, behind a disabled flag, or only in tests is not spend.

Not acceptable: "this file imports the OpenAI SDK", "this looks expensive".

### Gate 2, the price is cited

A price from a live official page with URL and fetch date, from an Infracost run, or from the user's own invoice. Nothing else.

If you cannot fetch the price, the finding is `unpriced`. Keep the units (tokens, reads, GB-hours) so the user can price it themselves.

### Gate 3, the volume is sourced

Required for any figure per day, month, or year. Sources: billing export, provider usage export, logs, analytics, or the user's stated number, each labeled.

Without volume, report cost per call and cost per user action only, and name the number that would complete the math. "If you have 10k users" is not a source; it is a scenario, and must be labeled as one.

### Gate 4, there is a refute check

Name the usage field, log query, billing line item, metric, or plan output that would prove the finding wrong, and what value would do it.

If nothing could distinguish your hypothesis from its opposite, report it as a question, not a finding.

---

## Refuse outright

- **Savings with no volume.** "This could save you $2,000 a month" with no sourced volume is invented. Give the per-call saving and the formula.
- **Model downgrades without a quality eval.** Never recommend a cheaper model as a finding. Cost per completed task is what matters: a larger model can be cheaper if it writes fewer output tokens, needs fewer retries, or finishes agent tasks in fewer turns. Offer an A/B run with a fixed task set, a quality bar, and cost per successful task as the metric.
- **Semantic or response caches for personalized or multi-turn content.** The same words mean different things in different conversations and for different users. Caching across them returns wrong or leaked answers. Only deterministic, user-independent inputs qualify, with a cache key that includes the model id and prompt version.
- **Unmeasured token tricks.** Switching output to a new serialization format, compressing prompts, or stripping whitespace only counts with a before-and-after token count on real payloads and a check that quality held.
- **Self-hosting without the full bill.** A recommendation to run an open model yourself needs GPU or instance cost at the required throughput, idle time, ops time, and quality comparison. Without that, refuse.
- **Calling an alert a cap.** Budget alerts notify, often hours late, and do not stop spend. A spend cap covers only the services its provider lists. Name which services in this project are covered and which are not.
- **Cutting reliability to save money without saying so.** Removing a NAT per zone, a replica, or backups is a resilience trade. Present it as one, for non-prod only unless the user decides otherwise.
- **Changing prices or plans for the user.** Upgrading, downgrading, buying reserved capacity, or enabling a paid feature is the user's decision. Report the math; never act on billing.

---

## Named anti-patterns

| Anti-pattern | What it looks like | Why it fails |
|---|---|---|
| **Price from memory** | "GPT input is $X per million" with no URL | Prices change monthly; the number is probably stale |
| **The imaginary million users** | Savings computed at a volume nobody measured | Unfalsifiable; it inflates every finding equally |
| **Sticker price thinking** | Ranking models by per-token price | Ignores output length, retries, and turns per task |
| **Cache everything** | A response cache with no key design | Wrong answers, leaked answers, stale answers |
| **Alert as safety net** | "You have a budget alert, so you're covered" | Alerts lag and do not stop spend |
| **Prod-grade dev** | Copying prod sizing into every environment | Multiplies idle cost by environment count |
| **Tip list** | Generic advice not tied to a call site | Not evidence; skip it |

---

## How to write a non-finding

> `src/jobs/digest.ts:14`: nightly digest uses the standard tier, candidate for batch. **Refused, Gate 1:** the job is behind `ENABLE_DIGEST=false` in every environment config, so it does not run.

> `api/classify.py:40`: frontier model used for a three-label classifier. **Refused as a finding (model downgrade rule):** no eval exists. Proposed instead: an A/B on 200 logged inputs, cost per correct label as the metric.

Report the totals: call sites examined, findings by lens, findings reduced to per-call because volume was missing, and what could not be priced.
