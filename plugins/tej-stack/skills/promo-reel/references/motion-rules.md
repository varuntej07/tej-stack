# Motion rules

## How the engine works

`assets/engine.js` builds every animated value as a sum of closed-form damped-spring step responses. Each value is a pure function of time, so:

- any frame renders identically on its own, which is what makes chunked rendering and motion blur possible;
- there are no CSS transitions, timers, `requestAnimationFrame` loops, or stored state in a scene;
- `window.seek(t)` draws the frame at time `t`, and `render.py` calls it for every subframe.

Tracks (`Tr`) change target with `.to(time, value, spring)`. `V(start, [t, 1], [t, 0])` is a visibility track that enters with the `IN` spring and exits with the faster `OUT` spring, so content swaps never overlap. In `loop` mode every track must end on its start value (`tr.closes()`); the template adds closing steps and logs any track that still does not close.

Spring presets keep overshoot small (damping 0.75 or higher). Use them as they are:

| Preset | Use |
|---|---|
| `GEO` | Size, radius, position |
| `CAM` | Camera and zoom: slower, no overshoot |
| `IN` / `OUT` | Content enter and exit |
| `FAST` | Press |
| `CUR` | Touch dot or cursor travel |
| `COL` | Color |

## Allowed

- One clear motion per beat: a tap, a screen swap, a zoom into the area that matters, a value changing.
- Zoom inside the screen to make small UI readable (social and loop modes only).
- A touch dot with a press ring for taps. It is a graphic, not a hand.
- A short blur and scale on content swaps (`layer()` in the engine).
- UI sounds on taps, aligned to their peak by `audio.py`.

## Banned

- Bouncy or elastic easing, overshoot you can see.
- Particles, sparkles, confetti, light leaks, lens flares, glows.
- Gradients on UI chrome that the app does not have.
- Stock-template looks: spinning 3D phones, floating device stacks, generic "app mockup" scenes.
- Fake hands, fingers, or people holding the device.
- Store badges drawn by hand. Use the official artwork only when the user supplies it; otherwise a plain text CTA.
- Any screen, state, or transition that implies a feature the app does not have.
- Invented stats, reviews, star ratings, rankings, download counts, prices, or awards.

## Layout

- 9:16: headline between 14% and about 24% from the top, device below it, nothing important in the bottom 20%.
- 1:1 and 16:9: headline in a left column, device on the right. Re-lay out every format; never crop a 9:16 render.
- Render `scene.html?debug` stills to see the safe zones and the clock.
