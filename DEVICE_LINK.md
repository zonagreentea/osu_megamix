# Device Link

`device_link.py` is osu!megamix's low-overhead, two-way device transport.
It uses one persistent UDP socket per device session and fixed-size binary
messages. A device sends `HELLO` once, receives `WELCOME`, then sends current
input; the game sends current state back through the same session.

## Packet format

Every packet starts with a 12-byte big-endian header:

| Bytes | Field |
| --- | --- |
| 0-1 | Magic: `OM` |
| 2 | Protocol version: `1` |
| 3 | Message type |
| 4-11 | Device ID: unsigned 64-bit integer |

Message types:

| Type | Payload | Direction |
| --- | --- | --- |
| `1` HELLO | none | device → game |
| `2` WELCOME | none | game → device |
| `3` INPUT | action `u8`, pressed `u8`, tick `u32` | device → game |
| `4` STATE | state `u8`, value `i32` | game → device |

Input and state packets are intentionally not retried. They represent current
state, so a later packet supersedes an earlier delayed one. Pairing uses the
source address from `HELLO`; messages from a different address cannot inject
input for that device ID.

## Game integration

```python
from device_link import DeviceLink

link = DeviceLink(on_input=game.receive_device_input)

# Once each game tick:
link.poll()

# When state changes:
link.publish_state(device_id, state=1, value=current_score)
```

For an internet-connected game host, expose UDP port `5051` (or pass another
port to `DeviceLink`). Local-network devices use the host's LAN address.
