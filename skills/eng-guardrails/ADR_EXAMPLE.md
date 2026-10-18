# Architecture Decision Records

An ADR records a structural invariant or an expensive-to-change design choice that the code does not show directly.
Do not violate an ADR without human confirmation. Each entry is 1–2 lines and names no code.
Observable behavior is in `functional-requirements.md`. Scope and sequencing are in the plan.

## ADR-1: TypeScript on Node
The server, client, and CLI are TypeScript on Node with strict typing, with commander for the CLI.

## ADR-2: HTTP over a Unix domain socket
Client and server talk HTTP over a advertised local socket. The system opens no network port, and the socket's presence advertises a running server.


## ADR-3: Command hooks, not HTTP hooks
Claude Code's HTTP hooks cannot reach a Unix socket. Command hooks also let the client start the server and report failures.

## ADR-4: The service interface is harness-agnostic
The service speaks one common HarnessEvent format and knows no harness-specific format, so other harnesses (Codex, OpenCode) can be added later. Each harness has its own client that adapts native events into a HarnessEvent.

## ADR-5: Delivered as one Claude Code plugin
The plugin bundles the hooks, client, and server, so a project depends on one thing and client and server versions always match.

## ADR-6: The socket defines health and single instance
A server is healthy only if it answers on the advertised socket. Two servers racing to start are resolved by which one binds to the advertised socket.

## ADR-7: One running server per home directory
Only one server runs for a home directory at a time, so creating a new server tears down the one already running there. The server outlives the hook that started it.

## ADR-8: No buffering or replay
Events are not buffered or replayed.

## ADR-9: Failures never block the agent
A hook failure must not stop the agent.

## ADR-10: The server answers success for every input
Malformed and unknown events are logged, not rejected. A bad payload or a Claude Code upgrade must not break a session.

## ADR-11: SQLite is the event store
Events go in one append-only log. State the harness needs later goes in separate tables.

## ADR-12: All runtime state lives under one overridable directory
Separate directories give fully isolated instances.

## ADR-13: Client and server are separate build targets
Each has its own source tree and build output. The server may depend on the client's shared types, never the reverse.

## ADR-14: One well-known socket name per home directory
Client and server share one socket name, derived from the service home directory. Services whose home directories differ use different names, including on the same machine.
