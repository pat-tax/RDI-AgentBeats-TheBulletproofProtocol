---
title: Green Agent Sprint 2 - A2A SDK Client Integration
version: 1.0
created: 2026-02-22
phase: Sprint 2 - Messenger Refactor
---

# Product Requirements Document: Green Agent Sprint 2

## Project Overview

Refactor the Green Agent's messenger module to use the a2a-sdk's native
`ClientFactory.connect()` pattern instead of raw httpx JSON-RPC calls.
This aligns with AgentBeats platform conventions (MAS-GraphJudge,
TestBehaveAlign reference implementations), providing implicit AgentCard
discovery, client caching per URL, TaskState lifecycle tracking, and SDK
error types.

**Scope**: `src/bulletproof_green/messenger.py` internals rewritten;
public API (`Messenger`, `MessengerError`, `create_message`, `send_message`)
preserved for backward compatibility. No changes to consumers
(`arena/executor.py`, `__init__.py`).

**Methodology**: Red-Green-Blue TDD — tests written first, then minimal
implementation, then refactor.

---

## Functional Requirements

#### Feature 1: SDK Client Connection and Caching

**Description**: Replace raw httpx with a2a-sdk ClientFactory.connect() for agent-to-agent connections, with per-URL client caching.

**Acceptance Criteria**:
- [ ] Messenger.send() calls ClientFactory.connect() instead of httpx directly
- [ ] Client instances are cached per URL (second call reuses first connection)
- [ ] ClientConfig uses streaming=False for non-streaming agents
- [ ] httpx.AsyncClient passed via ClientConfig for timeout control

**Technical Requirements**:
- a2a-sdk ClientFactory, ClientConfig, Client from a2a.client
- Client cache: dict[str, Client] keyed by URL
- httpx.AsyncClient cache: dict[str, httpx.AsyncClient] for lifecycle management

**Files**:
- `src/bulletproof_green/messenger.py`
- `tests/test_green_messaging_a2a.py`

---

#### Feature 2: SDK Message Construction

**Description**: Build proper a2a-sdk Message objects with TextPart and DataPart support for mixed-content messages.

**Acceptance Criteria**:
- [ ] send(text=...) creates Message with single TextPart
- [ ] send(data=...) creates Message with single DataPart
- [ ] send(text=..., data=...) creates Message with TextPart + DataPart
- [ ] Message uses Role.user enum (not raw string)
- [ ] Each message has unique UUID messageId

**Technical Requirements**:
- Message, Part, TextPart, DataPart, Role from a2a.types
- Replace create_text_message_object for mixed-part support

**Files**:
- `src/bulletproof_green/messenger.py`
- `tests/test_green_messaging_a2a.py`

---

#### Feature 3: SDK Response Extraction

**Description**: Extract response data from a2a-sdk Task artifacts instead of raw JSON-RPC dicts, returning dict[str, Any] for consumer compatibility.

**Acceptance Criteria**:
- [ ] Extracts DataPart.data dict from completed task artifacts
- [ ] Wraps TextPart.text as {"text": "..."} when no DataPart present
- [ ] Skips non-completed task states (working, submitted) in event stream
- [ ] Raises MessengerError when completed task has no artifacts
- [ ] Returns dict[str, Any] compatible with NarrativeResponse.model_validate()

**Technical Requirements**:
- TaskState from a2a.types for lifecycle checking
- AsyncIterator[ClientEvent | Message] from Client.send_message()
- ClientEvent = tuple[Task, UpdateEvent]

**Files**:
- `src/bulletproof_green/messenger.py`
- `tests/test_green_messaging_a2a.py`

---

#### Feature 4: SDK Error Mapping

**Description**: Map a2a-sdk exceptions and failed task states to MessengerError for backward-compatible error handling.

**Acceptance Criteria**:
- [ ] A2AClientTimeoutError maps to MessengerError with "timeout" in message
- [ ] A2AClientHTTPError maps to MessengerError with status code
- [ ] httpx.ConnectError during ClientFactory.connect maps to MessengerError
- [ ] TaskState.failed in event stream raises MessengerError

**Technical Requirements**:
- A2AClientError, A2AClientHTTPError, A2AClientTimeoutError from a2a.client
- MessengerError passthrough (no double-wrapping)

**Files**:
- `src/bulletproof_green/messenger.py`
- `tests/test_green_messaging_a2a.py`

---

#### Feature 5: Client Lifecycle Management

**Description**: Add close() method for proper cleanup of managed httpx clients and SDK client cache.

**Acceptance Criteria**:
- [ ] close() calls aclose() on all managed httpx.AsyncClient instances
- [ ] close() clears client cache so next send() creates fresh connection
- [ ] close() is idempotent (safe to call on unused Messenger)

**Technical Requirements**:
- httpx.AsyncClient.aclose() for cleanup
- Clear both _clients and _httpx_clients dicts

**Files**:
- `src/bulletproof_green/messenger.py`
- `tests/test_green_messaging_a2a.py`

---

#### Feature 6: Backward Compatibility

**Description**: Preserve public API surface for existing consumers (arena/executor.py, __init__.py exports).

**Acceptance Criteria**:
- [ ] create_message() still returns raw dict (unchanged pure function)
- [ ] send_message() free function still importable and callable (compat shim)
- [ ] Messenger importable from bulletproof_green package root
- [ ] MessengerError importable from bulletproof_green package root
- [ ] Messenger.send(text=..., data=...) returns dict compatible with NarrativeResponse.model_validate()
- [ ] Messenger(base_url=url) constructor stores base_url as public attribute
- [ ] Messenger timeout defaults to settings.timeout when not provided
- [ ] Initial client cache is empty (no connections until first send)

**Technical Requirements**:
- No changes to __init__.py exports
- No changes to arena/executor.py
- send_message free function wraps Messenger internally

**Files**:
- `src/bulletproof_green/messenger.py`
- `tests/test_green_messaging_a2a.py`

---

## Non-Functional Requirements

- All existing arena/executor tests must continue passing
- No new runtime dependencies (a2a-sdk already installed)
- Python 3.13, a2a-sdk>=0.3.20

## Out of Scope

- Changes to arena/executor.py or other consumers
- Purple agent messenger changes
- Retry/backoff logic (defer to future sprint)
- Async context manager (__aenter__/__aexit__) on Messenger

---

## Notes for Ralph Loop

Story Breakdown - Sprint 2 (6 stories total):
- **Feature 1 (SDK Client Connection)** → STORY-033: Implement SDK client connection with caching
- **Feature 2 (SDK Message Construction)** → STORY-034: Build SDK Message objects with mixed parts (depends: STORY-033)
- **Feature 3 (SDK Response Extraction)** → STORY-035: Extract response data from task artifacts (depends: STORY-033)
- **Feature 4 (SDK Error Mapping)** → STORY-036: Map SDK errors to MessengerError (depends: STORY-033)
- **Feature 5 (Client Lifecycle)** → STORY-037: Add close() for client cleanup (depends: STORY-033)
- **Feature 6 (Backward Compatibility)** → STORY-038: Preserve public API for consumers (depends: STORY-034, STORY-035, STORY-036, STORY-037)
