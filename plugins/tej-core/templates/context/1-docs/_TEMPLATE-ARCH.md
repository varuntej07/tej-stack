# ARCH: <subsystem name>

Scope: <what this subsystem covers, in one or two sentences>. Resilience profile: **<FastFail |
Resilient>**. Sources: live code read on <YYYY-MM-DD>; paths below are relative to <root>.

## 1. ASCII Block Diagram
```
[client] --transport--> [handler] --> [service] --> [store / provider]
```

## 2. End-to-End User Data Flow
1. `<path:function>`: what happens, what it reads and writes.
2. ...

## 3. Latency & DB/Storage Read-Write Budget
| Stage | Budget ms | Measured or "unmeasured" | Reads | Writes | Cache |
|---|---|---|---|---|---|

## 4. Resilience Profile
| Call | Profile | Timeout | Retries | Fallback | Cancellation | Failure copy |
|---|---|---|---|---|---|---|

## 5. Non-Negotiable Invariants, Micro-Rules & Must-Not-Fire Edge Cases
- <rule>: <why, with file:line>.
