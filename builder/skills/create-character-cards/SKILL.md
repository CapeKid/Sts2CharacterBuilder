---
name: create-character-cards
description: Author character cards and upgrades, optionally completing a native-comparable reward pool.
---

Ask whether to create custom cards, collect all supplied ideas, then ask whether to complete the remaining pool. Record a declined completion as an intentional small-pool prototype.
Write design/cards.json using [the card schema](../../cards.schema.json). IDs are stable C# identifier suffixes; starting_deck references those IDs. Basic cards do not count as reward cards. Tokens and bespoke effects require explicit extension code; do not classify them as reward cards accidentally.
For full-pool completion, first collect a passing baseline with [native testing](../../NATIVE-TESTING.md), then run balance --comparator with the exact native character ID. Record that build's reward count and rarity/type cell targets. Use the baseline to plan completion, preserve user cards and fill gaps around coherent archetypes. Refresh native evidence after edits before claiming final parity. If comparator evidence is unavailable, leave the full-pool gate pending.
The limited generator supports damage/Block/draw/Energy/Focus plus Exhaust and explicit base/upgraded values. Reject unsupported prose-only effects. Run generate, validate, balance and native base/upgraded targeting tests.
Skip outcome: empty cards.json and starting_deck; disable cards. The runtime uses native Ironclad deck/pool. This is a valid fallback, not an original full pool.
