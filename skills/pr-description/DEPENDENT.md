## :train: PR train

The `Notification` service moves from a synchronous DB-write-then-publish to an event-sourced outbox.
The table and dual-write land first, then this relay worker, then the synchronous path is removed — each
step must be live and verified before the next is safe.

Source: [NOTIF-408](https://jira.example.com/browse/NOTIF-408)

## TL;DR

The outbox table has no consumer yet, so this adds a relay worker that publishes unsent rows to the
message bus, running in parallel with the existing synchronous publish.

## Context

PR 1 added `notification_outbox` and dual-writes each event, but nothing drains the table. Until a relay
exists, the outbox rows accumulate unused and the synchronous publish in `NotificationService` remains the
only delivery path. This PR introduces the drain so PR 3 can remove the synchronous path.

## Changes

### Key changes

- Add `OutboxRelayWorker` (`services/notification/src/OutboxRelayWorker.java`) — polls the outbox on a
  fixed interval and drives the `OutboxRelay` abstraction to publish and mark rows sent.
- Extend `EventPublisher` with `publishBatch(List<NotificationEvent>)` and implement it in
  `KafkaEventPublisher` so the relay publishes a poll's worth of events in one round trip.
- Add `fetchUnpublished(int limit)` and `markPublished(List<Long> ids)` to
  `NotificationOutboxRepository`.

### Other changes

- Wire the worker and `notification.outbox.relay.*` config into `NotificationModule`.
- Add relay poll-interval and batch-size defaults to the service config.

## Reasoning

### Mark published only after the broker acks

`markPublished` runs after `publishBatch` returns, so a crash mid-publish leaves rows unsent and they
are retried on the next poll. This gives at-least-once delivery; downstream consumers already dedup by
event id.

## Rollout / risk

Gated behind `notification.outbox.relay.enabled`, default off. Enabling it starts a second live delivery
path alongside the synchronous publish, so consumers may briefly see duplicate events (deduped by id).
Roll out per region and watch outbox lag and publish error rate; disable the flag to stop the relay
without affecting the synchronous path.

## PR train

- https://github.com/Org/repo/pull/408001
- https://github.com/Org/repo/pull/408002 <-- here
- https://github.com/Org/repo/pull/408003
