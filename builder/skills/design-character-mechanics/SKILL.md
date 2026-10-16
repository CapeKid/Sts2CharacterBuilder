---
name: design-character-mechanics
description: Design a standalone character's starting kit, combat resource and archetypes.
---

Ask for the general mechanic, strengths/weaknesses, complexity, HP, starting deck/relic, energy and intended difficulty. Offer AI choices for every omitted creative detail. Record explicit requests before implementation.
The shipped generator supports damage, Block, draw, Energy and a run-local Focus power granting end-of-turn Block; it does not translate arbitrary prose into effects. Adjust these if they fit the idea. For a different resource, implement project-owned src/Extensions code and integrate it deliberately; do not silently label Focus as the requested mechanic.
The current template uses the native energy baseline. Non-default energy requires an implemented owner-scoped hook and native tests. Keep model IDs stable and powers in native save state. Exclude cross-run progression entirely.
Output the mechanics decision and extension design. Verify resource reset, stacking, save/resume, owner/target isolation and upgraded cards. Skip outcome: disable mechanic, remove Focus effects, select the native starter-relic fallback, regenerate before release of saved IDs.
