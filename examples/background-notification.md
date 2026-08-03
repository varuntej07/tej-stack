# Example: scheduled cross-device notification

## Scenario

A medication application lets a person schedule a reminder for 8:00 PM. A cloud scheduler, iOS and Android push services, local fallback notifications, a wearable, and the web app can all participate. The person may cross timezones, change quiet hours, lose connectivity, dismiss on one device, or disable notifications after scheduling.

## Invocation

Codex:

```text
$walkie-talkie Audit the completed medication reminder feature across cloud scheduling, iOS, Android, web, and wearable delivery. Include timezone and daylight-saving changes, quiet hours, offline devices, duplicate events, cross-device dismissal, permission revocation, privacy, and old app versions.
```

Claude Code:

```text
/walkie-talkie Audit the completed medication reminder feature across cloud scheduling, iOS, Android, web, and wearable delivery. Include timezone and daylight-saving changes, quiet hours, offline devices, duplicate events, cross-device dismissal, permission revocation, privacy, and old app versions.
```

## What a strong audit should expose

- The source of truth for wall-clock time, timezone, recurrence, and delivery status.
- An invariant defining how many user-visible alerts may occur per reminder occurrence.
- Behavior when the server push and local fallback both fire, or arrive late and out of order.
- Whether dismissal, snooze, edit, delete, and opt-out reconcile across devices.
- What the user sees when delivery is impossible because permissions are denied or tokens expire.
- Whether notification previews reveal sensitive medication information on locked devices.

Undefined choices such as travel behavior or lock-screen content require a human decision with a recommended default; the audit must not invent them.
