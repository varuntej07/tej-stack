# Device frames

Social and loop ads show the app inside a drawn phone. Store previews never do.

## The body

The template draws the body from `CONFIG.device` and `CONFIG.screenAspect`:

| Part | Android | iPhone |
|---|---|---|
| Bezel | about 3% of screen width, uniform | about 4% of screen width, uniform |
| Screen corner radius | about 9.5% of screen width | about 12.5% of screen width |
| Camera | Punch hole, centered, near the top | Dynamic Island pill, centered, near the top |
| Side buttons | Power and volume on the right | Action button and volume on the left, side button on the right |

Set `screenAspect` from the real captures: width divided by height of the PNG that `capture.py android-shot` saved (it prints both). Never stretch a capture to fit a frame of another aspect.

## Screens at real size

- Use real captures at full resolution. A 1080x2400 capture shown in a 480 px wide device is sharp; a rebuilt screen at the wrong dp is not.
- When a screen must be rebuilt in HTML (for example, a state that is hard to reach on a device), rebuild it at the app's real dp with its own tokens, then compare it side by side with a real capture before using it.
- Real captures already include the status bar and navigation or gesture bar. Leave `drawSystemBars: false`. Turn it on only for rebuilt screens.
- Clean the status bar before capturing when you can: full battery and signal, no notifications. On Android, demo mode does this (`adb shell settings put global sysui_demo_allowed 1`, then the `com.android.systemui.demo` broadcasts).

## Keyboards and other system UI

When the product is a keyboard or an IME, copy its own layout constants and vector drawables from the codebase: toolbar order, key weights, radii, pressed color. Never draw a generic QWERTY. A screenshot from the real device beats any value read from code.

## Truth over polish

A real-device capture is the reference for every pixel. If code values and the capture disagree, the capture wins, and the disagreement goes in your notes to the user.
