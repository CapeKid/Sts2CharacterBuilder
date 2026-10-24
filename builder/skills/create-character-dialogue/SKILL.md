---
name: create-character-dialogue
description: Create Ancient and character dialogue with localization and encounter integration.
---

Ask whether Ancient dialogue is wanted, collect supplied lines and offer AI completion. Record voice, first/repeat encounters, victory/ending text and languages separately. Preserve user-authored lines; fill gaps only when authorized by guided choices or expedited mode.

Read [the dialogue contract](../../DIALOGUE.md). Set `features.dialogue` and author optional `design/dialogue.json`: ordinary Ancient entry or `THE_ARCHITECT` ending, `first` or `repeat`, and 1–12 original speaker/text lines. Nonfinal `next` labels are optional; the final line leads to native reward buttons or ending Proceed. Optional translations use exact supported locale codes and matching-length line arrays; partial text/next overrides fall back to English and cannot change speakers or add a final next label. Each Ancient/visit pair is unique. Missing conversations retain native fallback. Native visit counts select ordinary first/repeat; Architect endings use native character wins (zero/positive), preserve existing attack metadata (or use no opening attack/both closing attacks for an empty native selection) and the native Proceed callback, and currently reject translations; add no custom saved state or cross-run progression.

Run `validate`, `generate`, and `generate --check` using the pinned toolkit CLI. Generated `src/Generated/Dialogue.cs` owns localized selection hooks for this character only. Do not copy the reference mod's conversations or edit generated code. Native Ancient cards and rewards are separate models and need card/pool verification.

Use a fresh `prepare-lab`/`test-native` lab for selector/fallback controls and every authored conversation's visible text, advancement, reward access and checkpoint replay. Translated rows also require every locale/fallback and checkpoint case, with rendered labels, live language switches and preserved progress/sound calls. Review formatting, wrapping, voice and English fallback in the actual game. Record human/device/language/co-op gaps separately; passing the synthetic suite does not complete them.

Architect endings require separate native ending/control records: rendered speech, native button advancement, preserved attack metadata, exact Proceed callback and map-checkpoint replay. Require an `ending-completion` record for each authored visit: actual closing attacks/WinRun, exactly-once isolated score/stat/history updates, completed-checkpoint removal, post-win result/character and native menu return. The test DLL isolates platform statistic/telemetry/achievement calls; normal packages exclude it. Forced-ending integration is not campaign reachability or human post-win layout review.

The generator supports eight ordinary Ancients with partial per-locale overrides plus English Architect endings. Custom Ancients, translated endings, other victory/defeat text and voiced lines require project-owned extensions plus explicit native evidence. Keep unsupported requested content as a gap.

Skip outcome: clear dialogue data, set dialogue false, regenerate and retain native encounter dialogue with no custom dialogue patches.
