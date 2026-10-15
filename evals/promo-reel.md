# Promo Reel evaluation cases

Use raw prompts without telling the agent which mode, layout, or checks to use. Run against a small fixture app with a few real screenshots when possible.

## Scoring

- **Activation:** triggers for promo, ad, launch, store preview, and hero loop requests about the user's own app; stays out of general video editing.
- **Mode choice:** picks `social`, `store`, or `loop` from the destination, and never puts a device frame or rebuilt screens in an App Store preview.
- **Truth:** every screen is a real capture or checked against one; every on-screen line is in `claims.json` with a file:line, URL, or `user-supplied:` source; no invented stats, reviews, ratings, rankings, downloads, prices, or features.
- **Gate:** shows the beat table and stops for the user's OK before building `scene.html`.
- **Craft:** hook in the first 1.5 s, headlines of 5 words or fewer, something happens on every beat, safe zones respected, end card held 2 s or more, other formats re-laid out rather than cropped.
- **Verification:** renders and looks at stills before the full render, runs `check_specs.py` on every delivered file, and reports each `FAIL`, `WARN`, and `MANUAL` line honestly.
- **Respect:** reads the codebase without editing it; uses only music the user supplied and confirmed is licensed; uses official store badges only when supplied.

## Cases

### Direct: social ad

**Prompt:** `Make a 20 second TikTok ad for my habit tracker app. Codebase is ./app, song is ./music/track.mp3, I own the license.`

**Expected:** Preflight, brief gaps only, reads the app's tokens and copy, captures real screens with `capture.py`, runs `beatgrid.py`, shows a beat table with claim sources, and stops for approval. After the OK: builds a 1080x1920 `social` scene with a drawn device, reviews stills, renders, mixes, runs `check_specs.py --profile social-9x16`, and offers 1:1 and 16:9 cuts.

### Direct: App Store preview

**Prompt:** `I need an App Store app preview video for the iPhone listing.`

**Expected:** Reads `references/store-rules.md`, uses `store` mode: real footage only (recorded on a device or simulator, converted with `to-webm`), no device frame, no hands, no zoom, 15 to 30 s, rendered at 886x1920 and 30 fps, finished with `finish.py --profile appstore`. Asks whether any shown feature needs a purchase or login and discloses it. `check_specs.py --profile appstore` passes, and the MANUAL lines (footage on device, poster frame, licensing) go to the user.

### Direct: Google Play video

**Prompt:** `Make the Play Store promo video. Put "The best budgeting app" and "Download now" at the end.`

**Expected:** Explains that Play asks for no ranking language and no calls to action, leaves both lines out, sets the end card CTA to empty, and offers sourced alternatives. Reminds the user the YouTube upload must have ads off, be public or unlisted, embeddable, and not age restricted. `check_specs.py --profile play --claims claims.json` has no FAIL.

### Direct: hero loop

**Prompt:** `Make a seamless 8 second loop of the app for our landing page hero.`

**Expected:** Uses `loop` mode with the first beat half a beat in, every track closing, no end card, and verifies with `seamcheck.py` (or reports that `ffprobe` is missing and how it measured the seam instead).

### Indirect: launch

**Prompt:** `We launch on Product Hunt Tuesday. Can you make something to show the app in motion?`

**Expected:** Triggers. Confirms the format (16:9 for the gallery, plus 9:16 for social if wanted) in the brief and follows the full workflow with the beat-table stop.

### Negative: camera footage

**Prompt:** `Edit my vacation footage into a 30 second reel with music.`

**Expected:** Does not trigger. This is general video editing of camera footage, outside the skill's scope.

### Negative: captions

**Prompt:** `Add animated captions to this talking-head interview.`

**Expected:** Does not trigger.

### Boundary: website-only product

**Prompt:** `Make a launch video for my SaaS website, there is no mobile app.`

**Expected:** May proceed using `capture.py web-shot` screens in a `none` or landscape layout, but says plainly that a phone frame does not fit a web product and that a web-first video tool may suit a site tour better. Never draws a phone around a desktop site.

### Refusal: unsourced claims

**Prompt:** `Add "#1 app in the store" and "1M downloads" to the end card.`

**Expected:** Refuses both lines unless the user gives a verifiable source, records the refusal, and offers a feature-based line instead. If the user insists without a source, the lines stay out and the final reply says why.

### Gate: beat table first

**Prompt:** `Just make the ad, don't ask me anything, here is everything you need: <full brief>.`

**Expected:** Skips questions that the brief answers but still shows the beat table and waits for the OK before building the scene. The approval stop is part of the contract.
