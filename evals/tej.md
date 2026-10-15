# Tej router evaluation cases

Use raw prompts without telling the agent which skill is correct.

## Scoring

- Routes to exactly one skill when one row of the routing table fits, and invokes it with the user's original request instead of re-asking.
- Resolves garbled speech-to-text invocations (tay stack, tedge stack, taj stack) to the intended skill by intent, not transcription.
- Runs the update check silently and mentions an available upgrade in at most one line, never blocking the task.
- When two skills fit, names both briefly, proceeds with the primary one, and offers the other as a follow-up.
- When no skill fits, says so and handles the task directly rather than forcing the nearest skill.
- Does not perform the specialist audit inside the router.

## Cases

### Direct ambiguous invocation

**Prompt:** `run tej stack on this repo`

**Expected:** Asks nothing about transcription; determines the dominant need from context (or asks one targeted question if the repo gives no signal), then invokes the matching skill. Does not run all eight.

### Voice-garbled routing

**Prompt:** `use tay stack, why is checkout so slow for big carts`

**Expected:** Routes to big-o-police with the slowness question intact. No comment about the misspelling.

### Two-skill overlap

**Prompt:** `tej: this new export feature is slow and sometimes silently fails`

**Expected:** Names both trace-failure (silent failure) and big-o-police (slow), picks one primary based on the phrasing, proceeds, and offers the other as a follow-up. Does not run both simultaneously without saying so.

### Map request

**Prompt:** `taj stack, map how the onboarding flow works in this app`

**Expected:** Routes to x-ray with the request intact. Does not route to walkie-talkie, because the user wants to see the flow, not audit it.

### Cost request

**Prompt:** `tej stack, our openai bill tripled this month, where is it going`

**Expected:** Routes to cost-police with the request intact. Does not route to big-o-police, because the user asked about money, not speed.

### Slow versus expensive

**Prompt:** `tay stack, the summarize endpoint is slow and costs us a fortune`

**Expected:** Names both big-o-police (slow) and cost-police (expensive), picks one primary from the phrasing, proceeds, and offers the other as a follow-up.

### Promo video request

**Prompt:** `tej, make a 20 second tiktok ad for my app`

**Expected:** Routes to promo-reel with the length and format intact. Does not start building the video inside the router.

### Negative case: no skill fits

**Prompt:** `tej stack, write a landing page headline for our launch`

**Expected:** States that no Tej Stack skill covers copywriting and does the task (or hands back) directly. Does not force get-cited onto a writing request that has no audit component.

### Capability question

**Prompt:** `what can tej stack do?`

**Expected:** One short paragraph per skill from the routing table, accurate to the eight specialist skills, noting the evidence-first, refusal-based house style. No invented skills.
