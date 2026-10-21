# Relics and potions

Author supported items in optional `design/items.json`, following [items.schema.json](items.schema.json). New projects start with an empty file. Existing projects without it keep their current starter and native potion fallback.

```json
{
  "schema_version": 1,
  "starting_relic": "TrainingToken",
  "relics": [
    {
      "id": "TrainingToken",
      "name": "Training Token",
      "rarity": "Starter",
      "trigger": "first-turn",
      "effects": { "block": 3, "draw": 0, "energy": 0, "focus": 1 },
      "flavor": "A reminder to practice."
    },
    {
      "id": "Notebook",
      "name": "Notebook",
      "rarity": "Uncommon",
      "trigger": "turn-start",
      "effects": { "block": 0, "draw": 1, "energy": 0, "focus": 0 }
    }
  ],
  "potions": [
    {
      "id": "SecondWind",
      "name": "Second Wind",
      "rarity": "Common",
      "effects": { "block": 6, "draw": 1, "energy": 0, "focus": 0 }
    }
  ]
}
```

Enable `features.items` for authored items. Every effect field is explicit: Block 0–30, draw 0–5, Energy 0–3 and Focus 0–10. At least one must be positive. Focus requires `features.mechanic`; other effects work without that feature or custom cards. These are authoring bounds, not balance certification. Effects use native commands, so normal draw/hand limits and modifiers apply.

Relics support `first-turn` (your first turn of each combat) and `turn-start` (each of your turns). Triggers are owner-scoped and claimed before awaited effects. The last triggered turn is saved with the relic and reset before a new combat, preventing duplicate application within one turn. Relic rarities are Starter, Common, Uncommon, Rare and Shop. Native rarity rules select reward/shop eligibility; Starter relics are excluded from the grab bag and shops. Authored relics belong to this character's pool and require this character in the run.

To replace the starting relic, provide exactly one Starter row and select its ID with `starting_relic`. Omit both to retain the default Focus starter, or Burning Blood when the Focus mechanic is disabled. The original generated StarterRelic model remains registered when enabled so adding an authored starter does not remove existing save IDs. Relic and potion IDs have separate namespaces, but each list must have unique IDs including case/underscore variants.

Potions support Common, Uncommon and Rare, combat-only use, and the owning player as target. Native actions handle procurement, belt capacity, target rejection, duplicate queued uses and consumption. Nonempty authored potion data selects a character-specific potion pool alongside the game's shared potions. With no authored potions the Ironclad potion pool remains the fallback. Native built-in character pools are not modified.

Names, optional relic flavor and generated effect descriptions use BaseLib's current English-inline contract. Each row may also assign independent artwork roles:

```json
"art": {
  "icon": "assets/items/token.svg",
  "outline": "assets/items/token-outline.png",
  "large": "assets/items/token-large.svg"
}
```

Enable `features.art`, declare each asset in `assets/manifest.json` with its exact case-sensitive path, SHA-256, method, license and credit, and preserve supplied sources. Only declared SVG/PNG files are supported; nested paths and spaces work. Empty `art`, unknown roles, unsafe/undeclared paths and unsupported formats fail validation. The builder does not generate, crop, resize or derive silhouettes. Export coherent normal/outline/large images and inspect their actual native crop, transparency and readability; structural checks do not assess artistic quality.

Omit any role to keep that role's existing native fallback: Burning Blood's packed icon for all relic roles, Block Potion's image for normal/large potion art and its outline for potion outlines. This may mix native and authored art; assign all three for a complete visual identity. Omit `art` entirely to keep existing behavior. No game imagery is copied into the package. Other target types, arbitrary effects and bespoke timing still require project-owned extensions and their own evidence.

Generated item artwork uses the existing virtual relic image paths and BaseLib custom potion image paths. Declared SVG/PNG bytes initially decode during initialization and register under exact project-owned `res://<namespace>/builder-item-art/...` paths in Godot's resource cache. Path lookups recover disposed textures and restore registration after native unloads. A narrow native asset-cache hook resolves only these exact registered paths, keeping large relics valid when the game memoizes their paths. Unassigned roles and foreign paths continue through native loading. These cache paths are separate from shipped asset paths; no Godot imports or PCK are needed. Failed decoding throws an error. Artwork adds no save fields and changes no model IDs. Do not redefine these generated image-path overrides in an extension.

Run `validate`, `generate`, `build` and a fresh isolated native lab. The generator owns `src/Generated/Items.cs` only when items are present, and tracks `Relic_<id>` and `Potion_<id>` in the saved-ID baseline. First successful build freezes those identities. Deleting or renaming a built item requires an explicit migration. Adding or changing items invalidates build/native evidence. Generated code and embedded data ship in the project DLL; the toolkit and authoring files are not package inputs.

The native suite checks pools/eligibility, acquisition, fallback icons/text, exact effect deltas, repeated turns/combat reset, duplicate triggers/actions and serialization. Configured artwork roles additionally require decoded pixels/dimensions/cache and native relic/potion UI refresh with foreign-model controls; large potion artwork is checked through its native getter. Omitted roles retain exact fallback texture identity. Mutable items, item serialization and full native run save/resume preserve artwork assignments, acquired relic IDs and potion slots. Headless fixtures do not establish co-op, visual quality, arbitrary extension behavior or balance.

Skip outcome: clear relics and potions, remove `starting_relic`, then disable `features.items`. The character uses Burning Blood and native relic/potion pools. Saved-ID protection still applies after a build; disabling an item library is not an automatic migration.
