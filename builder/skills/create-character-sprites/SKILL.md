---
name: create-character-sprites
description: Integrate character combat atlases, animation states and anchors; route other room presentation to extensions.
---

Ask whether sprites are wanted, collect references/supplied frames and offer AI completion. Agree on style and proportions. Use image generation only with an available authorized tool; otherwise keep disclosed native placeholder presentation.
Read [the combat sprite contract](../../SPRITES.md). Integrate original/supplied assets for idle, attack, skill, hurt, death and victory through optional `design/sprites.json` and `features.sprites`. Record the exact SVG/PNG atlas, dimensions, frame rectangles, per-frame ground anchors, FPS, filter and scale. Preserve supplied art and provenance; do not copy the reference mod's assets or identity.

Run `validate`, `generate` and `generate --check` with the pinned CLI. Generated `src/Generated/Sprites.cs` owns the combat visual factory and animation integration. All six states are required; idle/victory loop, other actions finish within five seconds, and death holds until revive/new combat. Unsupported presentation needs project-owned extensions; do not duplicate the generated factory override.

Use a fresh native lab to verify atlas pixels, crops/anchors, native trigger/restart behavior, death/revive, real combat victory, scene reset and save/resume reconstruction. Review the actual art and combat layout at 1280x800 and record human observations separately from geometric/native checks. Files alone do not complete this stage.

Selection, rest/shop and defeat/victory screens, arms, trails, shaders and sounds retain native fallbacks until separately implemented and tested. Do not describe the combat generator as complete character presentation or claim device/co-op testing without observations.

Output sprite design/assets, provenance and native plus human evidence with explicit gaps. Skip outcome: clear sprite data, set sprites false and regenerate; native placeholder animation remains visible and disclosed, with no custom sprite hooks.
