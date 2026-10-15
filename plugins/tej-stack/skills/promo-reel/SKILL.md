---
name: promo-reel
description: Turn a real app into a short promo video rendered from one HTML scene, using the app's own screens, colors, fonts, and copy, and nothing the app cannot actually do. Use when the user asks for a promo video, an app ad, a launch video, a TikTok, Reels, or Shorts ad, an App Store preview or app preview video, a Google Play or Play Store video, a Product Hunt video, a landing page hero loop, or mentions ad-kit. Also triggers on speech-to-text forms like promo reel, pro mo reel, or promo real. Captures real screens over adb, the iOS simulator, or Playwright, syncs every beat to the song, checks store rules before delivery, and refuses invented stats, reviews, rankings, and features. Not for editing camera footage, captioning talking-head videos, or general video editing.
---

# Promo Reel

> **Update check (run silently first):** run `bash "<this skill's directory>/../../bin/check-update.sh"` and read its single `TEJ_STACK:` status line. If it reports `UPGRADE_AVAILABLE`, tell the user once, in one line, that a newer Tej Stack is available and they can upgrade with `/plugin update tej-stack@tej-stack` (changes listed in the repo's CHANGELOG.md), then continue this task normally. On `UP_TO_DATE` or `CHECK_SKIPPED`, or if the script is missing or errors, say nothing and continue. The check must never block, delay, or fail the task.

Promo Reel makes a 15 to 30 second video of the user's app from a single HTML scene. Every frame is a pure function of time (closed-form springs in `assets/engine.js`), so renders are deterministic and any frame can be re-rendered alone.

**Evidence contract.** Every screen on camera is a real capture of the app or a rebuild checked against one. Every on-screen claim is in the claims ledger with its source: a file and line, or the user's own words. Never show a feature that does not exist. Never invent stats, reviews, ratings, rankings, download counts, prices, or awards. If the user asks for one without a source, refuse that line and offer a sourced alternative.

## Files in this skill

| Path | Use |
|---|---|
| `scripts/capture.py` | Real screens: `android-shot`, `android-record`, `ios-shot`, `ios-record`, `web-shot`, `to-webm`, `devices`. |
| `scripts/beatgrid.py` | Tempo, beat phase, and the drop downbeat of the song. |
| `scripts/render.py` | HTML to MP4 with motion blur, in chunks. `--stills` for review frames. |
| `scripts/audio.py` | Song window plus UI sounds aligned by their peaks. |
| `scripts/finish.py` | Join chunks, add the soundtrack, encode per destination (`social`, `appstore`, `play`, `loop`). |
| `scripts/check_specs.py` | Delivery gate: duration, resolution, fps, codec, size, audio, claims, store copy rules. |
| `scripts/seamcheck.py` | Loop seam check for `loop` mode. |
| `assets/scene.template.html` | The scene: device frames, screen layers, touch dot, headlines, end card, `?debug` safe zones. |
| `assets/engine.js` | Springs and tracks. Copy it next to the scene. Do not edit it per ad. |
| [references/store-rules.md](references/store-rules.md) | App Store and Google Play video rules with sources. |
| [references/beat-structure.md](references/beat-structure.md) | Hook, benefit beats, payoff, end card, and the beat table format. |
| [references/motion-rules.md](references/motion-rules.md) | What motion is allowed and what is banned. |
| [references/device-frames.md](references/device-frames.md) | Device bodies, real dp, keyboards, and when to draw system bars. |
| [references/claims-ledger.md](references/claims-ledger.md) | The `claims.json` format that `check_specs.py` reads. |

`SKILL_DIR` below is the folder that contains this file. Use `python3`, or `python` on Windows.

## Modes

| Mode | Output | Device frame | Rules |
|---|---|---|---|
| `social` | 1080x1920 first, then 1080x1080 and 1920x1080, re-laid out, never cropped | Drawn Android or iPhone | Hook in the first 1.5 s. Headlines of 5 words or fewer that work with the sound off. Text and key UI out of the top 14% and bottom 20%. End card held 2 s or more. |
| `store` | App Store preview (886x1920 for current iPhones) or a Google Play YouTube video | None | Footage captured from the app. No hands or device frames. App Store: 15 to 30 s, 30 fps max. Play: no ranking, price, or "Download now" copy. |
| `loop` | Seamless landing page or Product Hunt hero loop | Either | Every track returns to its start value. Check with `seamcheck.py`. |

When the user wants a store video, read [references/store-rules.md](references/store-rules.md) before the brief. A drawn device or HTML-rebuilt screen does not qualify as an App Store preview.

## Workflow

### 1. Preflight

Check the tools the chosen mode needs, and stop with install commands for anything missing:
- Python 3.9+, then `pip install -r SKILL_DIR/scripts/requirements.txt` and `python -m playwright install chromium`
- `ffmpeg` on `PATH` (`winget install Gyan.FFmpeg`, `brew install ffmpeg`, `apt install ffmpeg`). `ffprobe` is needed for `seamcheck.py` and gives `check_specs.py` the H.264 level.
- Android capture: `adb` with one authorized device (`python SKILL_DIR/scripts/capture.py devices`). iOS: macOS with Xcode for the simulator, or QuickTime for a physical iPhone.

### 2. Brief

Collect in one message, and only ask for what is missing: app name and codebase path, goal (downloads, signups, launch), audience, CTA or store link, length (15, 20, or 30 s), formats, mode, and the song. The user supplies the song and confirms its license allows ad use. Do not pick music for them.

### 3. Learn the app, read-only

Read at most about 40 files. Pull exact colors, font files, radii, icons, logo, and real UI copy into the scene's tokens. Pick the 3 or 4 moments that best sell the app. Start `claims.json` now and add every line that will appear on screen (see [references/claims-ledger.md](references/claims-ledger.md)). Do not edit the user's code.

### 4. Capture real screens

```bash
python SKILL_DIR/scripts/capture.py android-shot shots/01-home.png
python SKILL_DIR/scripts/capture.py android-record rec/focus.mp4 --seconds 15
python SKILL_DIR/scripts/capture.py to-webm rec/focus.mp4 rec/focus.webm --fps 30
python SKILL_DIR/scripts/capture.py web-shot http://localhost:3000 shots/01.png --w 390 --h 844 --scale 3 --mobile
```

Recordings must go through `to-webm` before the scene can show them: the Chromium that Playwright ships cannot decode H.264. For a website-only product, `web-shot` works, but say that a site tour may suit a web-first video tool better than a phone frame.

### 5. Beat grid, then stop for approval

Run `python SKILL_DIR/scripts/beatgrid.py song.mp3` and pick the start bar. Write the beat table described in [references/beat-structure.md](references/beat-structure.md): time, beat, screen, action, headline, and claim source. **Show the beat table and wait for the user's OK before building anything.**

### 6. Build the scene

Copy `assets/scene.template.html` to `scene.html` and `assets/engine.js` next to it. Edit only the CONFIG block and the CSS tokens: mode, device, `screenAspect` from the real captures, `seconds` (a whole number of bars), beats from the approved table, and the end card. Follow [references/motion-rules.md](references/motion-rules.md) and [references/device-frames.md](references/device-frames.md). Keep store badges out unless the user supplied the official artwork; use a plain text CTA instead.

### 7. Review stills

Render one still per beat, plus one just after every transition. Open `scene.html?debug` (or render the debug copy) to see the safe zones:

```bash
python SKILL_DIR/scripts/render.py scene.html --seconds 20 --w 1080 --h 1920 --stills 0.6,2.1,4.1,6.1 --out stills
```

Look at every still. Fix anything cramped, overlapping, unreadable, off-grid, or inside a safe zone. Show the stills to the user.

### 8. Render, mix, finish

```bash
python SKILL_DIR/scripts/render.py scene.html --seconds 20 --w 1080 --h 1920 --fps 60 --sub 4 --start 0 --end 320 --out out/chunk_00000.mp4
python SKILL_DIR/scripts/render.py scene.html --seconds 20 --w 1080 --h 1920 --fps 60 --sub 4 --start 320 --end 640 --out out/chunk_00320.mp4
```

Render in chunks of about 320 frames so each call survives shell timeouts, then continue to the last frame. Export sounds from the page (`JSON.stringify(window.SOUNDS)`) into `sounds.json` with the user's tap sound files, then:

```bash
python SKILL_DIR/scripts/audio.py --song song.mp3 --start 13.910 --seconds 20 --sounds sounds.json --out out/mix.wav --no_wrap --fade_out 1.5
python SKILL_DIR/scripts/finish.py --chunks "out/chunk_*.mp4" --audio out/mix.wav --profile social --out out/<app>-1080x1920.mp4
```

App Store previews: render at `--fps 30` and the accepted resolution, then `finish.py --profile appstore` (H.264 High 4.0, about 11 Mbps, AAC 256k, silent track if needed). Repeat for each format by re-rendering at the new size; the template re-lays out for square and landscape.

### 9. Check and deliver

```bash
python SKILL_DIR/scripts/check_specs.py out/<app>-1080x1920.mp4 --profile social-9x16 --claims claims.json
```

Fix every `FAIL`. Report each `WARN` and every `MANUAL` line to the user; those are rules a file check cannot see. Deliver to `out/<app>-<format>.mp4`.

### 10. Reply

Give the output paths, length, and formats, the `check_specs.py` result per file, any claims you refused and why, and anything the user must still confirm (song license, store disclosures, poster frame). Offer one next step, such as another format or a second cut with a different hook.
