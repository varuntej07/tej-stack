# Infrastructure catalog

The infrastructure lens prices what the IaC and platform configs create, especially what bills while nobody is using it. It applies to Terraform and OpenTofu, CloudFormation, CDK (synthesize first), Pulumi, Serverless Framework (`serverless.yml`), SAM, `firebase.json`, `vercel.json`, `fly.toml`, `render.yaml`, and `docker-compose` files that run always-on services on a paid host.

## 1. Get a priced inventory

**Preferred: Infracost.** If the `infracost` CLI is installed, run it and cite it as the pricing source:

```bash
infracost breakdown --path <terraform-dir>
infracost breakdown --path <terraform-dir> --format json --out-file infracost.json
infracost diff --path <terraform-dir>        # cost change of the working tree versus the baseline
```

Infracost needs its own API key for price lookups. If it is not configured, do not configure it for the user; say it is available and fall back below. Infracost prices resources from their declared size; usage-based costs (requests, GB transferred) need a usage file or your own volume numbers.

**Fallback: price from the provider.** List resources from the IaC (the scanner prints Terraform resource types, CloudFormation types, and Serverless functions with file and line), then price each from the official source in [pricing-sources.md](pricing-sources.md): the AWS Price List API or pricing pages, the Azure Retail Prices API, the Google Cloud pricing pages or Cloud Billing Catalog API. Label every price with its source and date, and state the region and hours per month you assumed (730 is the usual month).

**Environments:** find how many copies exist. A module instantiated for `dev`, `staging`, `preview`, and `prod`, or per pull request, multiplies every idle cost below.

## 2. Idle and oversized costs, ranked by how often they show up

| # | Pattern | Where to look | Price it | Refute it |
|---|---|---|---|---|
| 1 | **NAT gateway per availability zone in non-prod** | `aws_nat_gateway` count or `for_each` over AZs; VPC modules with one NAT per AZ | hourly charge x 730 x count, plus per-GB processing x traffic | dev traffic needs HA egress, or the gateway is shared |
| 2 | **Oversized non-prod instances and databases** | `instance_type`, `instance_class`, machine types, DB tiers in dev or staging | hourly price difference x 730 x environments | load or CPU metrics in that environment justify the size |
| 3 | **Always-on non-prod** | no schedule or scale-to-zero on dev, staging, preview | hours idle per month x hourly price | the environment is used outside working hours (show logs) |
| 4 | **Provisioned IOPS or throughput nobody uses** | `io1`, `io2`, `iops`, `throughput`, provisioned capacity modes | provisioned units x unit price | volume metrics show sustained use near the provisioned level |
| 5 | **Older volume type where a cheaper current one fits** | `gp2` volumes on AWS | per-GB price difference on the EBS pricing page x GB | a dependency on the older type's behavior, confirmed in docs |
| 6 | **Storage with no lifecycle** | buckets with no lifecycle rule, logs and uploads kept forever, no transition to colder classes | GB x months x price, growing each month | data is read often enough that colder tiers cost more in retrieval |
| 7 | **Logs kept forever** | log groups with no `retention_in_days`, high-volume debug logging in prod | ingestion per GB + storage per GB-month | retention is required by policy (ask) |
| 8 | **Idle load balancers and gateways** | load balancers, API gateways, or VPC endpoints with no targets or in unused environments | hourly x 730 | they serve traffic (show metrics) |
| 9 | **Public IP addresses** | elastic or static IPs, especially unattached | check the provider's VPC or network pricing page for per-address hourly charges | none attached, none reserved |
| 10 | **Cross-zone and egress traffic** | services split across zones or regions that talk constantly, cross-region replication, NAT-routed traffic to the provider's own services that could use a gateway endpoint | GB per month x per-GB price | traffic volume is small (show flow logs or billing lines) |
| 11 | **Serverless memory and timeout set far above need** | `memory_size`, `timeout`, concurrency in function configs | GB-seconds at configured memory x invocations | duration and memory metrics show the size is used |
| 12 | **Paid platform features enabled by default** | preview deployments for every branch, image optimization, analytics, edge middleware on every route, in `vercel.json` and similar | units from the platform's usage page x price | the plan includes them, per the pricing page |

## 3. Platform configs

- **Firebase:** read `firebase.json` and `firestore.indexes.json` for functions, regions, and hosting; read security rules alongside the code for unbounded reads; check whether functions set `maxInstances`. Function triggers and listeners belong to the runaway lens too.
- **Vercel, Netlify, Render, Fly:** read the config for regions, instance sizes, always-on machines, cron jobs, and preview behavior. Price from the platform's pricing page for the plan the user is on (ask which plan).
- **docker-compose and Kubernetes manifests:** count always-on services and their resource requests. Price only when you know the host; otherwise list them under "Not checked".

## 4. Report shape for this lens

Open the section with the pricing source used (Infracost version, or which provider APIs and pages, with the date). Then a table of resources with monthly cost per environment, the idle-cost findings with the same card format as the other lenses, and a line for everything that is usage-based and therefore unpriced without volume.
