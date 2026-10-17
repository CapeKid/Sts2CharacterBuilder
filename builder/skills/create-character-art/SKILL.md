---
name: create-character-art
description: Prepare supplied, generated or original placeholder card and UI art with provenance.
---

Ask whether custom art is wanted, collect supplied images, then ask whether to fill missing art. Match the character's approved style and preserve source files.
Use available generation tools only within budget/authorization. Without them, use clearly labeled original placeholders. Never extract or distribute game imagery.
Every shipped asset must be listed in assets/manifest.json with project-relative path, SHA-256, method, license and credit. Hash declarations are records, not proof of rights. Assign each supplied/generated SVG or PNG to its card's optional `portrait` property in design/cards.json with the exact declared project-relative path. Omit it to use assets/card.svg. See [portrait integration](../../ART.md) for the contract, runtime behavior and upgrade procedure. Adding an unused file does not complete integration.
Run validate, generate, build and the isolated native portrait checks after assigning art. Validate raster dimensions/crops and in-game appearance: headless pixel checks do not establish visual quality. Review card art at actual UI size and character icon readability. Keep any source metadata out of shipping files when inappropriate.
Skip outcome: retain the original visible geometric placeholders for required art; record the unfinished art in delivery notes.
