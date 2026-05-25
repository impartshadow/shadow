# Event Routing Consolidation Guard

**Failure mode:** FM-004

**Purpose:** Prevent new reactive-event implementations from bypassing the canonical event bridge.

**Precondition:** Runtime code that emits or subscribes to events must use `core.trigger_registry`. `core.event_bus` is allowed only as a compatibility facade that forwards into `trigger_registry`.

**Trigger:** A code edit introduces a new ad hoc event bus/subscriber registry, or writes directly to `state/triggers/*.trigger`.

**Enforcement:** Block the edit before write.

**Recovery:** Import `emit`, `subscribe`, or `on` from `core.trigger_registry`. For cross-process events, call `emit(..., cross_process=True)` instead of writing trigger files directly.

