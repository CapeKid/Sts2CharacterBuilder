---
name: create-character-presentation
description: Integrate a character's icons, energy display, VFX and accessible controls.
---

Use the character's art direction for portrait, map icon, selection transition, energy counter and trails. The shipped CustomIcon is an original geometric SVG; other presentation uses BaseLib/native runtime fallbacks.
Implement additional overrides in project-owned code and explicitly integrate them. Inspect inherited HeirPresentation only for API lessons; do not copy its class identity/assets.
Verify selection, combat, rest, shop, death/victory, tooltips and 1280x800 layouts. Check keyboard/controller navigation, close/back affordances and color-independent readability. Separate physical Deck evidence from desktop layout checks.
Skip outcome: disable custom presentation choices and retain disclosed visible runtime fallbacks. Do not mark physical controls tested without a device observation.
