# Trace Failure evaluation cases

Use raw prompts without giving the agent the expected diagnosis.

## Scoring

- Starts with: `Who or what encounters this failure?`
- Classifies the real execution context before drawing a flow.
- Separates confirmed facts, inferences, and unknowns.
- Distinguishes the outer error from the meaningful broken contract.
- Does not invent a product-user journey.
- Does not propose a fix when the user asks only for an explanation.
- Never recommends a blind retry after a partial external side effect.

## Cases

### Product-facing console failure

**Prompt:** `I clicked Save and got Cannot read properties of undefined (reading 'id'). Explain it before fixing it.`

**Expected:** Begin with the product user, trace the handler crash and possible missing request, and stop before fix instructions.

### Developer-only type failure

**Prompt:** `TS2322: Type 'string | undefined' is not assignable to type 'string'. What is the right fix?`

**Expected:** Identify the developer and blocked build, trace the optional value, and compare validation, default, type, and upstream-contract corrections.

### Background uniqueness failure

**Prompt:** `A scheduled job logs duplicate key value violates unique constraint. Users report nothing. What does it mean?`

**Expected:** Do not invent an immediate user action; distinguish idempotency, conflict, concurrency, retry, and later data impact.

### Unknown backend trigger

**Prompt:** `Cloud logs show AttributeError: 'NoneType' object has no attribute 'email'. Why?`

**Expected:** Keep the initiator unknown until evidence distinguishes an API request, webhook, worker, scheduler, or startup task.

### Silent behavior

**Prompt:** `The button spins forever and there is no error.`

**Expected:** Activate without an error string and trace loading state, asynchronous work, swallowed or hanging completion, and missing cleanup.

### Partial payment success

**Prompt:** `Stripe charged the customer, but our API returned 500. What should I do?`

**Expected:** Treat the customer and operator as affected actors, prohibit blind retry, and require provider-state, idempotency, webhook, local-state, and reconciliation checks.
