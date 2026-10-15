# Store video rules

Fetched 2026-10-15. Store rules change; when a value matters for a submission, re-check the source page. `scripts/check_specs.py` encodes the hard limits below (`FAIL`), the recommendations (`WARN`), and prints the rest as `MANUAL` lines.

## Apple App Store: app previews

Sources:
- App previews overview: https://developer.apple.com/app-store/app-previews/
- Specifications: https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications

### Content rules

| Rule | Apple's wording, condensed |
|---|---|
| Footage from the app | "Demonstrate the features, functionality, and user interface of your app using footage captured on device." |
| Stay within the app | "App previews must show only content within the app itself. Don't film people interacting with a device, such as an over-the-shoulder angle or fingers tapping the screen." |
| Touch graphics allowed | "You may add graphic elements, such as touch hotspots." Apple recommends capturing the native UI resolution rather than zooming in. |
| No implied features | Transitions between scenes must not imply functionality the app does not have. |
| Disclose purchases | If shown features need an in-app purchase, a subscription, or a login, disclose it in the footage or the end frame. |
| Authorized content only | Music, film, characters, brands, and other IP need licensing for marketing use in all territories. |
| Audio | A single score across the preview is suggested; UI sound effects are fine. |
| Poster frame | Shown when autoplay is off. Defaults to 5 seconds in. Changing it on an approved preview needs a new version. |

What this means for the template: `store` mode draws no device, ignores `zoom`, keeps headline plates small, and the screens must be real captures. A drawn phone with HTML-rebuilt screens is a `social` ad, not an App Store preview. Apple's capture guidance uses QuickTime with a connected device. Simulator recordings are common in practice, but Apple's wording says "captured on device", so prefer a real device for store previews.

### Technical specs

| Item | Value |
|---|---|
| Length | 15 s minimum, 30 s maximum |
| Count | Up to 3 per device size and language |
| File size | 500 MB maximum |
| Formats | `.mov`, `.m4v`, `.mp4` with H.264; `.mov` with ProRes 422 (HQ only) |
| H.264 | Progressive, up to High Profile Level 4.0, target 10 to 12 Mbps |
| Frame rate | 30 fps maximum |
| Audio | Stereo. H.264: AAC 256 kbps. ProRes: PCM (16, 24, or 32 bit) or AAC 256 kbps. 44.1 or 48 kHz. All tracks enabled. |
| Orientation | iOS: portrait or landscape. macOS and tvOS: landscape only. |
| Processing | Up to 24 hours after upload |

### Accepted resolutions

Use the accepted resolution, not the device's pixel resolution.

| Display class | Accepted portrait | Accepted landscape |
|---|---|---|
| iPhone with Dynamic Island or Face ID (large and medium), iPhone Air, iPhone Duo | 886 x 1920 | 1920 x 886 |
| iPhone with Home Button, large (8 Plus class) and 4" (SE 1st gen class) | 1080 x 1920 | 1920 x 1080 |
| iPhone with Home Button, medium (SE 2nd and 3rd gen, 8) | 750 x 1334 | 1334 x 750 |
| iPad 13", 11", 10.5" | 1200 x 1600 | 1600 x 1200 |
| iPad 12.9" (2nd generation) | 1200 x 1600 or 900 x 1200 | 1600 x 1200 or 1200 x 900 |
| iPad 9.7" | 900 x 1200 | 1200 x 900 |
| Mac, Apple TV | none | 1920 x 1080 |
| Apple Vision Pro | none | 3840 x 2160 |

iPhone with Home Button (3.5" display) does not support app previews. If you provide only the largest size, App Store Connect scales it down for smaller devices.

## Google Play: preview video

Source: https://support.google.com/googleplay/android-developer/answer/9866151

### Requirements

| Rule | Detail |
|---|---|
| How it is added | One YouTube URL in the "preview video" field. Not a playlist or channel URL, no extra parameters such as timecodes. |
| Ads | Ads must be off: turn off monetization, or use a video without monetization claims. Copyrighted music can attach claims that keep ads on even after you turn monetization off. |
| Privacy | Public or unlisted, not private. |
| Age | Not age restricted. |
| Embedding | Must be embeddable on Google Play. |

### Highly recommended (they affect promotion, not approval)

- Show the actual app experience, with core features in the first 10 seconds.
- At least 80% of the video should represent the real user experience. Limit title screens, logos, and pre-rendered content.
- Only the first 30 seconds autoplay (muted, depending on device and surface). Keep it short.
- Do not show people interacting with the device, unless core usage is off-device.
- Landscape or portrait are both supported. A portrait video must not have black bars at the sides.
- Copy that gives context when muted is fine, but no ranking, testimonial, award, price, or promotional language. Play's examples: "Best", "#1", "Top", "New", "Discount", "Sale", "Million Downloads". Play's own "Best Of" awards are allowed.
- No calls to action such as "Download now", "Install now", "Play now", or "Try now". Set the template's `end.cta` to `''` for Play.
- Text must be legible on a phone and on screen long enough to read.

"Free" is in Play's list for screenshots and the short description. `check_specs.py` flags it in the video too, because Play shows these assets side by side.

## Social platforms

TikTok, Instagram Reels, and YouTube Shorts overlay their own UI. The kit keeps text and key UI out of the top 14% and the bottom 20% of a 9:16 frame. That is a working margin from the ad-kit spec, not a published platform number; check the current platform guides if an ad will run as paid placement.
