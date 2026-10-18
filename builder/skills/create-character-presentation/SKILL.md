---
name: create-character-presentation
description: Integrate a character's icons, energy display, VFX and accessible controls.
---

Use the character's art direction for portrait, map icon, selection transition, energy counter and trails. The shipped CustomIcon is an original geometric SVG.
Read [room presentation](../../PRESENTATION.md). Author optional design/presentation.json for independent rest/shop atlases, idle/action frames, ground anchors, local position and scale. Declare exact SVG/PNG bytes/provenance, validate and generate; omitted rooms retain native art. Do not hand-edit generated Presentation.cs or implement its reserved InitializePresentation partial method. Run a fresh native lab for accepted/rejected rest and purchase responses, facing, ownership and reconstruction; keep human/device observations separate.
Implement selection/ending/energy/VFX and other unsupported overrides in project-owned code and explicitly integrate them. Inspect inherited presentation only for API lessons; do not copy its class identity/assets or progression.
Verify selection, combat, rest, shop, death/victory, tooltips and 1280x800 layouts. Check keyboard/controller navigation, close/back affordances and color-independent readability. Separate physical Deck evidence from desktop layout checks.
Skip outcome: disable custom presentation choices and retain disclosed visible runtime fallbacks. Do not mark physical controls tested without a device observation.
