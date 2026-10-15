# Runaway risk catalog

Steady waste costs a percentage. Runaway risk costs the company. The public record is full of small projects billed thousands to tens of thousands of dollars in a day by a self-calling function, an unbounded query, or one abuser. The pattern is always the same: usage-billed service, no hard limit on the path, and an alert that arrived after the money was spent.

For each risk, state a **scenario** with numbers, not a forecast: "one script at the rate this endpoint allows, for 24 hours, costs $X at today's prices." Label it a scenario in the report.

---

## 1. Self-triggering functions

**Looks like:** a function triggered by writes to a collection, bucket, queue, or table that writes back to the same place. A Firestore `onDocumentWritten` that updates the document it fired on. A storage trigger that writes a thumbnail into the bucket it watches. A Lambda behind a CDN or API route that calls that same route. A webhook handler that triggers the webhook.

**Detect:** match each trigger's source path against the write targets inside its body. The scanner flags candidates where a trigger's watched collection name also appears in a write in the same file. Then read the code: is there a guard (a field check, a prefix filter, a "processed" flag) that stops the second run?

**Scenario:** invocations per second the loop can sustain x price per invocation, compute time, and every write and read it performs, for 24 hours.

**Fix:** a guard that makes the second run a no-op, write targets outside the watched path, and a concurrency limit on the function.

**Refute it:** show the guard, or the invocation metric staying flat after a single write in a test project.

## 2. Billed endpoints with no login or no per-user limit

**Looks like:** a route that calls an LLM, an SMS sender, a maps API, or any metered service, reachable without authentication, or authenticated but with no per-user quota, rate limit, or input-size cap. A client app that calls a provider directly with an embedded key.

**Detect:** for every billed call site, trace back to its entry point and check middleware for auth and rate limiting. Check input length caps: a 1M-token context accepts a very large paste.

**Scenario:** max requests per second the infrastructure accepts x max cost per request (largest accepted input plus the output ceiling), for 24 hours.

**Fix:** auth on the route, a per-user and per-IP quota, an input size cap, a server-side `max_tokens`, and keys only on the server.

**Refute it:** a request without credentials gets rejected, and the rate limiter's config shows a per-user limit.

## 3. SMS and OTP pumping

**Looks like:** a send-code endpoint (signup, login, phone verify) that sends an SMS for any number, with no rate limit per number, per IP, or per country, and no country allowlist. Attackers trigger codes to premium-rate numbers and the sender pays per message.

**Detect:** find Twilio, Vonage, SNS, Firebase phone auth, or Verify sends; trace to the route; check for limits, CAPTCHA, and geo restrictions. The provider's own fraud docs (see pricing sources) list the controls.

**Scenario:** sends per second allowed x the highest per-message price among countries not blocked.

**Fix:** per-number and per-IP limits, a country allowlist, the provider's fraud guard, and CAPTCHA before send.

**Refute it:** show the limiter and allowlist config, or the provider's fraud protection enabled.

## 4. Unbounded reads and listeners

**Looks like:** a Firestore or realtime listener on a whole collection with no `limit`; a `get()` per item inside a loop; a listener re-attached on every render; a list screen that reads every document to count them. Document databases bill per document read, so a missing `limit` turns one screen open into thousands of billed reads.

**Detect:** the scanner flags `onSnapshot` and reads inside loops. Read the query: is there a `limit`, a pagination cursor, and a detach on unmount?

**Scenario:** documents read per screen open x screen opens per user per day x users x price per read.

**Fix:** `limit` plus pagination, aggregate count queries instead of reading documents, one listener per screen with a detach.

**Refute it:** the provider's usage metrics for reads per day before and after a single screen open in a test project.

## 5. Public storage and egress

**Looks like:** a public bucket or object ACL (`public-read`, `allUsers`), large media served straight from the bucket with no CDN, or hotlinkable downloads. Egress is billed per GB, and anyone who finds the URL can loop a download.

**Scenario:** object size x downloads a single client can drive per hour x 24 x egress price per GB.

**Fix:** private buckets with signed URLs, a CDN in front, request-rate limits, and lifecycle rules.

**Refute it:** an unauthenticated request for the object is rejected, or a CDN is confirmed in front.

## 6. Agent loops, retries, and fan-out with no ceiling

**Looks like:** an agent loop with no maximum turns; a retry wrapper with no maximum attempts or no backoff; a queue consumer that requeues failures forever; a job that fans out one task per item with no cap.

**Scenario:** worst-case turns or attempts x cost per turn, per stuck task, multiplied by how many tasks can get stuck at once.

**Fix:** a step limit, a per-task budget check, capped retries with exponential backoff and jitter, and a dead-letter queue.

**Refute it:** show the limits in code or config.

## 7. Leaked keys

**Looks like:** provider keys in committed files, client bundles, mobile app binaries, or public CI logs. A leaked key is a billed endpoint with no login.

**Detect:** search for key patterns in tracked files and client code. Do not print a key in the report; give the file and line only.

**Fix:** rotate the key first, then move it server-side and scope it.

**Refute it:** the key is a public, restricted key by design (for example a client key restricted by app and API in the provider console), confirmed in the provider's docs.

---

## Alerts are not caps

State this in every report that has a runaway section:

- Budget alerts send a notification. They do not stop spend, and billing data can lag by hours, so a loop can run long past the threshold before anyone is told.
- Some providers offer real spend caps, but only for listed services. Firebase, for example, documents spend cap budgets for a short list of services and not for others. Read the provider's current docs and name which services in this project a cap covers and which it does not.
- Some API providers offer hard monthly spend limits per organization or project. Check the provider console docs and recommend setting one, but never describe one as configured unless the user confirms it.
