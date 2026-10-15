# Beat structure

A promo is a short argument told on a beat grid. The headlines alone, with the sound off, must tell the story.

## The shape

| Part | Time | Job |
|---|---|---|
| Hook | 0 to 1.5 s | The most striking real UI moment plus a bold headline. No logo intro, no slow fade from black. |
| Benefit beats | 3 or 4 beats | One benefit each, shown working in the real app. Headline of 5 words or fewer. |
| Payoff | 1 beat | The outcome: the finished thing, the saved time, the result screen. |
| End card | last 2 s or more | Logo, app name, one-line promise, CTA. Held still long enough to read. |

Something happens on every beat: a tap, a screen change, a zoom, a headline swap, a value updating. A beat with nothing moving reads as a stall.

## Timing on the grid

1. Run `scripts/beatgrid.py song.mp3`. It prints BPM, beat length, phase, and low-end energy per bar.
2. Pick the start bar: the first bar after a big jump in "low" is usually the drop. Listen to confirm.
3. Make the video a whole number of bars: `T = bars * 4 * 60 / BPM`. At 120 BPM, 8 bars is 16 s and 10 bars is 20 s.
4. Put every cut and tap on a beat time `n * 60 / BPM` from the video's start. Pass the song start time to `audio.py --start`.
5. For a `loop`, start the first beat half a beat in, so no cut lands on the seam.

## Beat table

Show this table to the user and wait for their OK before building the scene. One row per beat change.

| Time (s) | Beat | Screen (capture file) | Action on screen | Headline (5 words max) | Claim source |
|---|---|---|---|---|---|
| 0.00 | 1 | `shots/01-home.png` | Device rises in, list visible | Your day, *sorted* | `lib/home/home_screen.dart:48` |
| 2.00 | 5 | `shots/02-timer.png` | Tap "Start session" | One tap to focus | `lib/timer/timer_screen.dart:112` |
| 4.00 | 9 | `rec/timer.webm` 3.0 s in | Countdown runs | Distractions stay out | `lib/timer/block_list.dart:20` |
| 6.00 | 13 | `shots/03-week.png` | Zoom on the weekly chart | See your *week* | `lib/stats/week_view.dart:31` |
| 8.00 | 17 | end card | Logo, name, promise, CTA | Plan the day. Protect your focus. | user-supplied: "Focusly helps you plan and focus" |

Also state, under the table: the song and its start time, the BPM, the total length, the formats, and the mode.

## Headline rules

- 5 words or fewer. Concrete verbs and nouns from the app's own vocabulary.
- One accent word at most, wrapped in `*stars*` in the template.
- No claim the claims ledger cannot source. "Saves 2 hours a day" needs a measured source; "Plan your day" needs only the feature.
- Store mode: captions are optional and small. Google Play: no "Best", "#1", "Top", "New", "Free", "Sale", or "Download now".
