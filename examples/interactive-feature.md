# Example: interactive offline photo annotation

## Scenario

A photo-review application has shipped a completed annotation feature on desktop and mobile. A reviewer opens a large image, draws regions, adds comments, works offline, and later sees edits on another device. The implementation includes local autosave, server synchronization, conflict resolution, keyboard shortcuts, touch gestures, and screen-reader labels.

## Invocation

Codex:

```text
$walkie-talkie Audit the completed photo annotation feature on desktop and mobile. Trace first use, autosave, offline editing, conflict resolution, app termination, keyboard-only use, touch input, and screen-reader behavior. Run safe relevant tests and separate observed evidence from gaps.
```

Claude Code:

```text
/walkie-talkie Audit the completed photo annotation feature on desktop and mobile. Trace first use, autosave, offline editing, conflict resolution, app termination, keyboard-only use, touch input, and screen-reader behavior. Run safe relevant tests and separate observed evidence from gaps.
```

## What a strong audit should expose

- Whether a region is durably saved before the UI reports success.
- What happens when two devices edit the same annotation from a stale base revision.
- Whether process death after local save but before upload loses, duplicates, or reorders work.
- Whether mouse, keyboard, touch, zoom, scaling, and screen-reader paths reach equivalent outcomes.
- Whether image content or comments enter logs, analytics, crash reports, or unintended caches.
- Whether users can understand pending synchronization and recover from a rejected conflict.

A useful result cites the actual view, state owner, persistence layer, sync protocol, tests, and observed behavior. It does not declare the feature ready from unit tests alone.
