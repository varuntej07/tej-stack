# Claims ledger

Every line of text that appears on screen, including headlines, captions, and the end card, goes into `claims.json`. `scripts/check_specs.py --claims claims.json` reads it and fails the video when a claim that needs a source has none.

## Format

```json
{
  "claims": [
    { "text": "One tap to focus", "kind": "feature", "source": "lib/timer/timer_screen.dart:112" },
    { "text": "Plan the day. Protect your focus.", "kind": "copy", "source": "user-supplied: \"our tagline is Plan the day. Protect your focus.\"" },
    { "text": "Pro features need a subscription.", "kind": "disclosure", "source": "lib/paywall/plans.dart:14" },
    { "text": "4.8 stars on Google Play", "kind": "rating", "source": "https://play.google.com/store/apps/details?id=com.example.app" }
  ]
}
```

| Field | Meaning |
|---|---|
| `text` | Exactly what appears on screen. |
| `kind` | `feature`, `stat`, `review`, `rating`, `price`, `award`, `comparison`, `testimonial`, `disclosure`, `cta`, or `copy`. |
| `source` | `path/to/file.ext:line` where the feature or value lives, a URL, or `user-supplied: <the user's exact words>`. |

## Rules

- `feature`, `stat`, `review`, `rating`, `price`, `award`, `comparison`, and `testimonial` need a source. Without one, `check_specs.py` prints `FAIL`.
- A feature's source is the code that implements it, not a design doc or a TODO.
- A number ("2 hours saved", "10,000 users") needs a measured source the user can show. If the user has none, offer wording without the number.
- Ratings, reviews, and download counts must be current and come from the store page or the user. Never round up, never invent.
- `copy` and `cta` lines may have no source, but they must not carry an unsourced claim inside them.
- Google Play videos: keep ranking, price, and promotional words out of every line, and use no CTA. `check_specs.py --profile play` scans the ledger for them.

## Refusing a claim

When the user asks for a line the ledger cannot source, for example "#1 productivity app" or "1M downloads", say so plainly, leave it out, and offer a sourced alternative built from a real feature. Note the refusal in the final reply.
