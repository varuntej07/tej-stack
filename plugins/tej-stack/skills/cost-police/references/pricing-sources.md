# Pricing sources

Fetch prices from these official pages on every run and cite the URL and the fetch date next to each price. Every URL below loaded successfully when this file was written (2026-10-15). If one moves, find the replacement on the provider's own domain; never substitute a third-party price list, and never price from memory.

If the environment has no web access, ask the user for the prices they pay, or mark the finding `unpriced` and keep the unit math.

## LLM APIs

| Provider | Pricing | Mechanics worth reading |
|---|---|---|
| Anthropic | https://platform.claude.com/docs/en/about-claude/pricing | Prompt caching: https://platform.claude.com/docs/en/build-with-claude/prompt-caching. Batch: https://platform.claude.com/docs/en/build-with-claude/batch-processing. Token counting: https://platform.claude.com/docs/en/build-with-claude/token-counting |
| OpenAI | https://developers.openai.com/api/docs/pricing | The page lists standard, batch, flex, and fast tiers and cached input prices per model |
| Google Gemini API | https://ai.google.dev/gemini-api/docs/pricing | Context caching price, batch, flex, and priority tiers per model; some prices have dated changes, so read the effective dates |
| OpenRouter | https://openrouter.ai/models | Per-model prices; check whether the route adds a fee over the underlying provider |

Read the multipliers on the page itself. As an example of why: at the time of writing, Anthropic's cache read multiplier differed by model, data residency added a multiplier, and Gemini listed caching prices that change on a stated date.

## Cloud providers

| Provider | Source | Notes |
|---|---|---|
| AWS | https://aws.amazon.com/pricing/ | Service pages: EC2 https://aws.amazon.com/ec2/pricing/on-demand/, EBS https://aws.amazon.com/ebs/pricing/, VPC and NAT https://aws.amazon.com/vpc/pricing/, Lambda https://aws.amazon.com/lambda/pricing/, S3 https://aws.amazon.com/s3/pricing/, CloudWatch https://aws.amazon.com/cloudwatch/pricing/ |
| AWS Price List API | https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html | Programmatic prices; `GetProducts` reference: https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_pricing_GetProducts.html |
| AWS Budgets | https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html | Alerts and actions; read what an action does before calling it a limit |
| Google Cloud | https://cloud.google.com/pricing | Compute https://cloud.google.com/compute/all-pricing, Cloud Run and functions https://cloud.google.com/functions/pricing, Storage https://cloud.google.com/storage/pricing, Firestore https://cloud.google.com/firestore/pricing |
| Google Cloud Billing Catalog API | https://cloud.google.com/billing/docs/how-to/get-pricing-information-api | Programmatic SKU prices |
| Google Cloud budgets | https://cloud.google.com/billing/docs/how-to/budgets | States that alerts-only budgets do not cap usage; describes spend cap budgets where supported |
| Azure Retail Prices API | https://prices.azure.com/api/retail/prices | No key needed; filter with `$filter`, for example `serviceName eq 'Virtual Machines' and armRegionName eq 'eastus'`. Docs: https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices |
| Infracost | https://www.infracost.io/docs/ | CLI source: https://github.com/infracost/infracost. Cite Infracost as the source when its output is used |

## Platforms and metered services

| Provider | Pricing | Notes |
|---|---|---|
| Firebase | https://firebase.google.com/pricing | Firestore billing: https://firebase.google.com/docs/firestore/pricing. Surprise bills and spend caps: https://firebase.google.com/docs/projects/billing/avoid-surprise-bills and https://firebase.google.com/docs/projects/billing/spend-caps. At the time of writing, spend caps covered only a listed set of Firebase services, not every product |
| Vercel | https://vercel.com/pricing | Usage pricing detail: https://vercel.com/docs/pricing. Plans: https://vercel.com/docs/plans |
| Supabase | https://supabase.com/pricing | Check compute add-ons and spend cap settings per plan on the page |
| Twilio SMS | https://www.twilio.com/en-us/sms/pricing/us | Per-country pages exist; price the most expensive unblocked country for pumping scenarios |
| Twilio Verify | https://www.twilio.com/en-us/verify/pricing | Fraud controls: https://www.twilio.com/docs/verify/preventing-toll-fraud |
| Cloudflare Workers | https://developers.cloudflare.com/workers/platform/pricing/ | |
| Cloudflare R2 | https://developers.cloudflare.com/r2/pricing/ | |

## How to cite in the report

```text
Price: Claude <model> input $A/MTok, cache read $B/MTok
       source: https://platform.claude.com/docs/en/about-claude/pricing (fetched 2026-10-15)
```

One citation line per distinct price. If two findings use the same price, cite it once in a "Prices used" block at the top of the report and refer to it.
