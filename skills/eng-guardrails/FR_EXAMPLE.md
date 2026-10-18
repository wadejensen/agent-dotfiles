# Functional requirements - lifecycle event log

This document gives the behavior that a user can observe when a harness runs with meta-harness. Meta-harness records lifecycle events. It does not change what the harness does.

## 1. Terms

1.1 A **harness** is a coding agent program.

1.2 A **session** is one run of a harness, from start to end. The harness gives each session an identifier.

1.3 A **lifecycle event** is a notification from a harness that something happened in a session.

1.4 The **service** is the long-running meta-harness program that receives lifecycle events and stores them.

1.5 A **harness plugin** is the integration point and mechanism between a harness and the system. Each harness has its own harness plugin. Section 10 lists the supported harnesses.

1.6 A **client** is the meta-harness program that a harness plugin runs for each lifecycle event. The client sends the event to the service. Each harness has its own client.

1.7 The **system** is the harness plugins, the clients and the service together.

1.8 The **state directory** is the directory where the service keeps everything it stores.

1.9 The **user** is the person who runs a harness.

1.10 The **system developer** is the person who builds and operates meta-harness.

1.11 The **terminal interface** is the text interface of a harness. The user sees text from the system in the terminal interface.

## 2. Setup

2.1 A project must need only the harness plugin to send events to meta-harness. The user must not have to edit other settings, install other programs, or start the service.

## 3. Recorded events

3.1 A harness plugin must send the lifecycle events that section 10 lists for its harness to the service. The service must store them.

3.1.1 A harness plugin must ignore all other lifecycle events.

3.1.2 Lifecycle events are similar but not identical across harnesses.

3.2 The system must record each event once. It must record the event when the harness reports it.

3.3 The system must not deny an action, redirect the agent, or add instructions to any session because of an event.

3.4 The service can perform blocking side effects when it processes an event. The harness waits until the service completes them and the client returns the response of the service. The system does not limit this wait.

## 4. Event records

4.1 The service must store each recorded event as an event record. An event record must contain these items:
- a number that is unique and increases with each new record
- the time the service received the event
- the harness
- the session identifier
- the name of the event
- the project directory of the session
- the complete original data of the event, unchanged

4.2 The system developer must be able to query the records of one session in the order the service received them.

4.3 The system developer must be able to query the records of one session by the harness and the session identifier.

4.4 The system developer must be able to query the records of one working directory.

4.5 The system must never change or delete an event record.

## 5. Service start

5.1 The user must not be required to start the service manually. The client must start the service if the service is not running.

5.2 The service must keep running after the client that started it ends.

5.3 The system must run at most one service for each state directory at any time.

5.4 The service must respond to a client connection within 500 milliseconds.

5.5 The start operation must not finish until the service is ready to receive requests. The client must wait for the start operation to finish.

5.5.1 The service must be ready within 15 seconds of the start operation beginning. If the service is not ready by then, the start has failed (requirement 7.1).

## 6. Service recovery

6.1 The client must treat a service as unhealthy if the service is running but does not respond to a client connection within 500 milliseconds (requirement 5.4).

6.2 When the service is unhealthy, the client must replace it with a new service and deliver the event to the new service. The client must not stop an unrelated process.

## 7. Failure

7.1 A failure is any case where the client cannot deliver an event to a working service. Examples: the service cannot start, or the service is not ready within 15 seconds of starting.

7.2 In a failure, the client must show the user one line of warning text in the terminal interface. The line must name meta-harness and give the reason.

7.3 The warning must not enter the context of the agent.

7.4 A failure must not stop the session. It must not stop the tool call or the turn that caused the event.

7.5 The system must not store a failed event later. The event is lost.

7.6 The client must show a warning for every failed event. It must not show a warning only once for each session.

## 8. Input handling

8.1 The service must accept every event it receives without an error to the client.

8.2 The service must store an event only if the event has a session identifier and an event name that section 10 lists.

8.3 The service must write each event it does not store to a diagnostic log that the system developer can read.

8.4 The service must not stop or become unhealthy because of unusual input.

## 9. State directory

9.1 The service must keep everything it stores, including the diagnostic log, in the state directory.

9.2 The default state directory is `.meta-harness` in the home directory of the user.

9.3 The user must be able to choose a different state directory with the setting `META_HARNESS_HOME`.

9.4 Two services that use different state directories must not affect each other.

## 10. Supported harnesses

### 10.1 Claude Code

10.1.1 The harness plugin for Claude Code is a Claude Code plugin. It runs the client as a Claude Code hook for each lifecycle event in requirement 10.1.2.

10.1.2 The lifecycle events are: SessionStart, SessionEnd, UserPromptSubmit, PreToolUse, PostToolUse, Stop, PreCompact, PostCompact, SubagentStart and SubagentStop.

10.1.3 The user must start Claude Code with the system enabled by running `meta-claude`. It must accept the same arguments as `claude`.
