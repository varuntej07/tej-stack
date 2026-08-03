# Example: transactional checkout and fulfillment

## Scenario

A marketplace has completed a Stripe-style purchase flow. The browser creates a checkout attempt, the payment provider authorizes a charge, webhooks arrive asynchronously, inventory is reserved, a seller is notified, fulfillment begins, and refunds or disputes may happen later. Charges, inventory movement, email, and fulfillment are externally visible or irreversible side effects.

## Invocation

Codex:

```text
$walkie-talkie Audit the completed checkout-to-fulfillment workflow. Trace buyer, seller, payment provider, webhook worker, inventory, email, refund, and support journeys. Challenge duplicate submissions, concurrent inventory claims, delayed or reordered webhooks, partial commits, retries, cancellation, and reconciliation.
```

Claude Code:

```text
/walkie-talkie Audit the completed checkout-to-fulfillment workflow. Trace buyer, seller, payment provider, webhook worker, inventory, email, refund, and support journeys. Challenge duplicate submissions, concurrent inventory claims, delayed or reordered webhooks, partial commits, retries, cancellation, and reconciliation.
```

## What a strong audit should expose

- The idempotency keys and unique constraints that enforce at most one charge and one fulfillment per purchase intent.
- The commit points for payment, inventory, order state, notifications, and fulfillment.
- Safe behavior for browser retries, duplicate webhooks, webhook reordering, worker crashes, and provider timeouts with unknown outcomes.
- How partial success is detected, reconciled, compensated, and explained to buyers, sellers, and support.
- Whether refunds, cancellations, chargebacks, and inventory release follow legal state transitions.
- Whether logs, dashboards, and support tools expose payment or personal data beyond their intended audience.

A mocked happy-path webhook test is not enough evidence. A release recommendation must distinguish verified idempotency and recovery behavior from assumptions.
