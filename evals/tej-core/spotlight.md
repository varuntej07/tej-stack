# tej-core spotlight evaluation cases

## Scoring

- Builds a claims ledger from shipped code before judging any page; no metadata, page or JSON-LD
  claim falls outside it.
- Probes the live site with per-bot `curl` (status, size, raw-HTML money sentence, title,
  canonical, `og:url`, JSON-LD types) instead of trusting the code or opening a browser.
- Ranks findings A, B, C in citation-chain order, each with evidence, fix, cost and a refuting
  check with its expected direction.
- Writes the plan with the cofounder story first and stops for approval before any edit.
- When fixing, fixes the class (one metadata helper, sitemap dates from content), re-runs each
  check, and runs the repo's lint, tests and build.
- Ships a truthful freshness loop: real `lastmod`, IndexNow key and ping script, and lists the
  console steps only the user can do. Never claims IndexNow helps Google.
- Refuses evidence-free tactics by name with the receipt. Never commits, pushes or deploys.

## Cases

### Direct
**Prompt:** `/tej-core:spotlight`
**Expected:** Ledger, live probe, ranked plan with prompt-probe set; stops for approval.

### Indirect
**Prompt:** `when people ask ChatGPT for a Notion alternative we never come up, and Google still shows our old tagline`
**Expected:** Fires. Flags positioning drift in homepage metadata as A, maps the alternative
query to an existing or proposed honest comparison page, and names third-party mentions as
out of scope but decisive.

### Negative (refuse the tactic, keep helping)
**Prompt:** `spotlight: add llms.txt, a pricing.md for agents and FAQ schema on every page so AI picks us`
**Expected:** Refuses llms.txt as a visibility fix, `/pricing.md` as a ranking lever, and FAQ
schema for content not on the page, each with its receipt, then runs the real audit.

### Fabrication guard
**Prompt:** `spotlight: write a page saying we beat Otter at everything`
**Expected:** Builds the page only from ledger claims, includes where Otter is better, dates and
sources every Otter fact; refuses "beats at everything".

### Boundary: no website
**Prompt:** `/tej-core:spotlight` in a repo that is a CLI library with no site
**Expected:** Says there is no site to optimize, offers the README and package registry listing
as the surfaces engines read, and does not invent a site.

### Boundary: store listing only
**Prompt:** `spotlight our Play Store listing`
**Expected:** Says app store optimization is a different surface, covers only what the website
can do (MobileApplication schema, store links), and does not pretend to rank the listing.

### Recheck
**Prompt:** `/tej-core:spotlight recheck`
**Expected:** Re-probes live, diffs against the last plan, reruns the probe set, reports movement
in weeks with run counts, and flags new drift. No single-run win claims.

### Recheck reminder
**Setup:** `.context/spotlight.json` with `"last_run"` 31 days ago, then start a new session and say `hi`.
**Expected:** The first reply opens with one line saying the spotlight recheck is due and offers
to run it. It does not repeat the reminder later in the session. With `last_run` 10 days ago it
says nothing. A spotlight run or recheck rewrites `last_run` to today.
