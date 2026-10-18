Source: [MEDIA-284](https://jira.example.com/browse/ABC-123)

## TL;DR

Inline thumbnail generation times out large uploads, this PR moves generation to an async worker queue and serves a placeholder until ready.

## Context

`UploadService.handleUpload` renders every thumbnail size before returning, so a large image can hold the request open past the 30s gateway timeout. Uploads of >20MB images fail ~15% of the time.

## Changes

### Key changes

Enqueue a `ThumbnailJob` on upload and render sizes in a `ThumbnailWorker`, returning a placeholder asset immediately.

## Rollout / risk

Gated behind the `async-thumbnails` flag, default off. Enabling it delays thumbnail availability by
a few seconds and adds a worker deployment; disable the flag to fall back to inline generation.
