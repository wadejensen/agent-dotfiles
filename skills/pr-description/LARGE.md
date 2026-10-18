## TL;DR

Per-instance rate limiting let clients exceed the global quota by fanning out across pods, so this
moves the limiter to a shared Redis backend enforced across all instances.

## Context

The `PublicApiGateway` rate limiter keeps counters in local memory, so the effective limit scales
with instance count. During the March traffic spike a single client sent ~8x its quota by hitting
different pods. Analysis: [dashboard link].

## Changes

### Key changes

- Replace the in-memory `TokenBucket` with a Redis-backed `SharedTokenBucket`.
- Add a `RateLimitBackend` interface so the limiter no longer depends on a concrete store.
- Emit `rate_limit.reject` metrics tagged by client and route.

### Other changes

- Wire the Redis connection pool into the gateway module config.
- Update the load-test fixtures to point at the shared backend.

## Reasoning

### Fail open on Redis unavailability

If Redis is unreachable the limiter allows the request rather than blocking all traffic. Availability
of the API outweighs strict quota enforcement during a store outage.

### Lua script for atomic check-and-decrement

The check and decrement run in one round trip to avoid a race where concurrent requests each read the
same remaining count. This keeps enforcement correct under contention.

## Rollout / risk

Gated behind the `shared-rate-limiting` flag, default off. Enabling it changes live rejection behavior
for over-quota clients. Roll out per region and watch `rate_limit.reject` and Redis latency; disable
the flag to fall back to in-memory limits.
