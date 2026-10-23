# Resource-gated event choices

Original [event contract](../../EVENTS.md) example. Copy `events.json` to a character project, enable `features.events`, then validate/generate.

Ask requires 40 Gold without spending it. The Trade terminal choice additionally requires Gold and HP ranges, then applies its separate costs/rewards. Aid is available at zero Gold. CapControl is an explicit full-health healing-cap diagnostic, not a balanced reward design. Leave remains available on both pages.

The isolated suite uses controlled resources to test every condition, including 0.01-percent HP boundary failures, and ordinary native checkpoints. This does not establish campaign reachability, translation, layout or balance quality.

The example and a legacy event passed a fresh v0.111.0 fixture; see [native evidence](../../../docs/event-conditions-native-fixture.json). Each changed character project needs its own current native evidence.
