# Cost Police evaluation cases

Use raw prompts without telling the agent which problems exist, and without hinting that some prompts have no answer. Run against a small fixture repository when possible; the scanner's own test fixture (LLM calls in loops, a self-triggering Firestore function, an unbounded listener, an SMS send, a key in source, Terraform with NAT per AZ, gp2, and a log group without retention) is a good starting point.

## Scoring

- Inventories billed call sites from the code (scanner or equivalent search) before giving any advice, and reads the source of each candidate it reports.
- Traces each billed call to the entry point that triggers it and counts calls per user action, including fan-out, retries, and loop turns.
- Fetches prices live from official pages and cites the URL and fetch date for every price. Never prices from memory; marks findings `unpriced` when it cannot fetch.
- Shows the multiplication behind every dollar figure, with each factor labeled by source (counted, observed, estimate, billing, provider usage, logs, analytics, user-stated).
- Gives monthly or yearly figures only when volume is sourced; otherwise stops at per-call and per-action cost and names the missing number.
- Names a refute check for every finding: a usage field, log query, billing line, metric, or plan output, and the value that would prove it wrong.
- Covers all three lenses that apply (token waste, runaway risk, infrastructure) and says which lens was skipped and why.
- States that budget alerts are not caps, and names which services any spend cap actually covers.
- Refuses model downgrades without a quality eval, semantic caches for personalized or multi-turn content, unmeasured token tricks, and self-hosting without full cost math.
- Ends with "Not checked", deliberate non-findings with the rule that stopped each, and at most five next actions ranked by dollars per hour of work.
- Reports only; does not change code, prompts, models, limits, or infrastructure unless the user explicitly asks.

## Cases

### Direct trigger: LLM bill

**Prompt:** `Our Anthropic bill doubled last month. Find out why and what to cut.`

**Expected:** Activates. Runs the inventory, finds the call sites and model ids, fetches the current Anthropic pricing page and cites it, and checks caching, output ceilings, history growth, loops, and batchable work. Asks for or uses the usage export to get volume. Every dollar figure shows its math; the refute check for a caching finding names `cache_read_input_tokens`.

### Indirect trigger: unit economics

**Prompt:** `Can I afford a free tier for this app? What does one active user cost me?`

**Expected:** Activates. Traces the actions a typical user takes, counts billed calls per action, prices each from live sources, and reports cost per action and per user as a range. Asks for the actions-per-user number instead of inventing one, and labels any scenario as a scenario.

### Runaway trigger: launch fear

**Prompt:** `We launch on Product Hunt tomorrow. Could anything in here give us a surprise bill?`

**Expected:** Activates the runaway lens first. Checks unauthenticated billed routes, per-user limits, input size caps, self-triggering functions, unbounded listeners, SMS sends, public storage, agent loops, retries, and keys in source. Each risk gets a numeric 24-hour scenario labeled as a scenario. States that alerts lag and are not caps, and names which services a spend cap would cover in this project. Does not print any key value.

### IaC case

**Prompt:** `Here's our Terraform. Our AWS bill is $1,800 a month for an app with 200 users. Where is it going?`

**Expected:** Activates the infrastructure lens. Runs `infracost breakdown` if the CLI is installed and cites it; otherwise prices resources from AWS pricing pages or the Price List API with region and 730 hours stated. Finds environment multiplication (dev, staging, preview), NAT gateways per AZ in non-prod, oversized non-prod instances, provisioned IOPS, gp2 volumes, log groups without retention, idle load balancers, and public IPs. Presents removing redundancy as a resilience trade, recommended for non-prod only unless the user decides otherwise.

### Negative case: performance, not money

**Prompt:** `This endpoint takes 4 seconds. Find the O(n^2).`

**Expected:** Does not run a cost audit. Hands off to `big-o-police`, because the question is time complexity, not dollars.

### Refusal: savings with no volume

**Prompt:** `How much per month would I save by turning on prompt caching?` in a repo with no logs, no usage export, and no stated traffic.

**Expected:** Counts or estimates the stable prefix tokens, fetches cache write and read prices, and gives the saving per call and per thousand calls with the formula. Refuses a monthly figure and names the one number needed (calls per day on that route). Does not invent a traffic level.

### Refusal: cheapest model everywhere

**Prompt:** `Just switch everything to the cheapest model and tell me how much I save.`

**Expected:** Refuses to present a downgrade as a saving. Explains that cost per completed task decides it, that a larger model can cost less when it writes fewer output tokens or needs fewer retries or turns, and that quality can drop. Offers an A/B run on logged inputs with a quality bar and cost per successful task as the metric. Changes no code.

### Refusal: semantic cache on chat

**Prompt:** `Add a semantic cache in front of our support chatbot so repeat questions are free.`

**Expected:** Refuses for multi-turn, personalized conversations: the same words mean different things in different contexts and across users, so a cache returns wrong or leaked answers. Offers caching the stable prefix instead, and response caching only for deterministic, user-independent calls with a key that includes the model id and prompt version.

### Boundary: no web access

**Prompt:** `Audit our OpenAI costs.` in an environment where web fetches fail.

**Expected:** Says it cannot fetch live prices, asks the user for the prices they pay or their invoice, and keeps token and call math per finding marked `unpriced`. Never fills in a price from memory.

### Boundary: an alert called a safety net

**Prompt:** `We have a Firebase budget alert at $100, so we can't get a big bill, right?`

**Expected:** Corrects the premise: an alerts-only budget notifies, can lag behind real usage, and does not stop spend. Checks the current Firebase docs on spend caps and names which of the project's services they cover and which they do not (for example, Firestore reads when a cap covers only listed services). Points to the runaway risks in the code that matter more than the alert.

### Boundary: fix mode

**Prompt:** `Good report. Fix the top two.`

**Expected:** Switches to fix mode only on this explicit instruction. One change per step, smallest first. Before each change, states the usage field or billing line expected to move and in which direction; after it, shows how to confirm (usage fields on a real call, a token count, `infracost diff`, or plan output). Asks before changing a model, a rate limit, or any infrastructure.
