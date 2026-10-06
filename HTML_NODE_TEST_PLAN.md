# osu_megamix HTML Node Test

Experimental branch for testing osu_megamix.html as an
offline-first authoritative node with optional online capabilities.

## Authority

The HTML node owns authoritative local state.

Network connections are transport only.

Remote requests must never directly mutate authoritative state.

## Offline

Test:

- boot without Internet
- complete local runtime
- local input
- local state
- pause/resume
- Escape behavior
- menus
- collection
- megamix
- solo
- multi
- double-tap pause/escape
- local resource loading
- network-loss survival

## Online

Test where supported:

- connectivity detection
- resource requests
- WebSocket
- EventSource
- client/session communication
- state synchronization
- disconnect
- reconnect
- multiple clients

Online functionality must remain optional.

## Browser capabilities

Test:

- fetch
- WebSocket
- EventSource
- Worker
- SharedWorker
- ServiceWorker
- Cache API
- localStorage
- sessionStorage
- IndexedDB
- BroadcastChannel
- Web Crypto
- online/offline events
- visibility/lifecycle events

Unsupported APIs = SKIP.

## Test suite

Run:

1. HTML boot
2. runtime initialization
3. offline boot
4. online detection
5. offline transition
6. online transition
7. local state creation
8. local state mutation
9. local input
10. pause
11. resume
12. Escape
13. menu transitions
14. collection mode
15. megamix mode
16. solo mode
17. multi mode
18. double-tap pause/escape
19. invalid input rejection
20. remote-request validation
21. remote state cannot directly mutate authority
22. disconnect handling
23. reconnect handling
24. state survives network loss
25. persistence
26. storage availability
27. worker availability
28. WebSocket availability
29. Service Worker availability
30. resource loading
31. missing-resource handling
32. malformed-request handling
33. repeated-request handling
34. clean shutdown
35. clean restart

## Network safety

Run the runtime with network unavailable and available.

Authoritative state must remain locally controlled in both cases.

## Reporting

Every test must report:

PASS
FAIL
SKIP

with a short reason.

Do not conceal unsupported capabilities.

## Scope

Modify only experimental files on this branch.

Do not modify:

- osu_megamix.html
- production runtime files
- main branch
