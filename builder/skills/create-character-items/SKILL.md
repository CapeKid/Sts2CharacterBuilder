---
name: create-character-items
description: Create character-specific starting/drop relics and potions with native eligibility tests.
---

Ask whether relics and potions are wanted, collect supplied ideas and independently ask whether AI should add more. Starting relics, reward relics, shops and potions have separate eligibility.
The template implements only the run-local Focus starter relic when items and mechanic are enabled. Its icon is a runtime native fallback. Drop relics/potions require project-owned src/Extensions implementations and explicit pool integration; do not claim the starter fulfills a requested item library.
Use the existing native model lifecycle as a reference, not the original mod's content or identity. Test owner-specific triggers, combat reset, stacking, acquisition, compendium, save/resume and shop/drop exclusions.
Skip outcome: disable items; the character uses native Burning Blood and native relic/potion pools. If the Focus mechanic is disabled, the same native starter fallback applies. Do not register disabled custom items.
