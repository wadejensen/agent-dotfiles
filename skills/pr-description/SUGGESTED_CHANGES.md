Suggested changes to [#284](https://github.com//Org/repo//pull/284). Code, not comments, for a few things that are clearer as a diff.

## What I changed and why

- **Moved the placeholder-asset lookup out of `UploadService` and behind `ThumbnailService`.**
  The controller shouldn't know how a placeholder is stored. That's a storage detail, and every other
  asset read already goes through `ThumbnailService`. See the diff for details.

- **Moved the `ThumbnailJob` enqueue into the upload transaction.** If the process stops between the
  commit and the enqueue, you get a committed asset with no job and nothing to retry it, which could silently drop a message and lose at-least-once delivery guarantee.

- **Made `ThumbnailWorker` idempotent on a deterministic render key.** A queue is at-least-once, so it
  processes some jobs twice. A key of (asset id, size) turns a duplicate into a harmless overwrite
  instead of a race.

## Potentially controversial

- The in-transaction enqueue couples the upload write to the queue client. The fully decoupled answer
  is an outbox row, but that's a bigger change than this PR. Tell me if you prefer that direction.
- I could take or leave the `ThumbnailService` move, but `ThumbnailJob` and `ThumbnailWorker` fixes are blocking.
