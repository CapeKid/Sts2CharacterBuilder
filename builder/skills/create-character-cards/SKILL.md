---
name: create-character-cards
description: Author character cards and upgrades, optionally completing a native-comparable reward pool.
---

Ask whether to create custom cards, collect all supplied ideas, then ask whether to complete the remaining pool. Record a declined completion as an intentional small-pool prototype.
Write design/cards.json using [the card schema](../../cards.schema.json). IDs are stable C# identifier suffixes; starting_deck references those IDs. Basic cards do not count as reward cards. Tokens and bespoke effects require explicit extension code; do not classify them as reward cards accidentally.
For full-pool completion, inspect the selected game's actual native comparator and record reward count plus rarity/type cross-distribution, not historical Spire Legacy counts. Fill gaps around coherent archetypes and preserve user cards. If comparator evidence is unavailable, leave the full-pool gate pending.
The limited generator supports damage/Block/draw/Energy/Focus plus Exhaust and explicit base/upgraded values. Reject unsupported prose-only effects. Run generate, validate, balance and native base/upgraded targeting tests.
Skip outcome: empty cards.json and starting_deck; disable cards. The runtime uses native Ironclad deck/pool. This is a valid fallback, not an original full pool.
