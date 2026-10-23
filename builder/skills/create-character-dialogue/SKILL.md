---
name: create-character-dialogue
description: Create Ancient and character dialogue with localization and encounter integration.
---

Ask whether Ancient dialogue is wanted, collect supplied lines and offer AI completion. Record voice, first/repeat encounters, victory/ending text and languages separately. Preserve user-authored lines; fill gaps only when authorized by guided choices or expedited mode.

Read [the dialogue contract](../../DIALOGUE.md). Set `features.dialogue` and author optional `design/dialogue.json`: ordinary Ancient entry, `first` or `repeat`, and 1–12 original speaker/text lines. Nonfinal `next` labels are optional; the final line leads to native reward buttons. Optional translations use exact supported locale codes and matching-length line arrays; partial text/next overrides fall back to English and cannot change speakers or add a final next label. Each Ancient/visit pair is unique. Missing conversations retain native fallback. Native visit counts select first/repeat; add no custom saved state or cross-run progression.

Run `validate`, `generate`, and `generate --check` using the pinned toolkit CLI. Generated `src/Generated/Dialogue.cs` owns localized selection hooks for this character only. Do not copy the reference mod's conversations or edit generated code. Native Ancient cards and rewards are separate models and need card/pool verification.

Use a fresh `prepare-lab`/`test-native` lab for selector/fallback controls and every authored conversation's visible text, advancement, reward access and checkpoint replay. Translated rows also require every locale/fallback and checkpoint case, with rendered labels, live language switches and preserved progress/sound calls. Review formatting, wrapping, voice and English fallback in the actual game. Record human/device/language/co-op gaps separately; passing the synthetic suite does not complete them.

The generator supports eight ordinary Ancients with partial per-locale line/label overrides and English fallback. Custom Ancients, The Architect ending, victory/ending text, voiced lines require project-owned extensions plus explicit native evidence. Keep unsupported requested content as a gap.

Skip outcome: clear dialogue data, set dialogue false, regenerate and retain native encounter dialogue with no custom dialogue patches.
