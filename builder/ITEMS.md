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

Names, optional relic flavor and generated effect descriptions use BaseLib's current English-inline contract. Generated relics use Burning Blood's runtime icon; generated potions use Block Potion's runtime art. These are explicit native fallbacks: the package contains no game imagery. Custom item artwork, other target types, arbitrary effects and bespoke timing require project-owned extensions and their own evidence.

Run `validate`, `generate`, `build` and a fresh isolated native lab. The generator owns `src/Generated/Items.cs` only when items are present, and tracks `Relic_<id>` and `Potion_<id>` in the saved-ID baseline. First successful build freezes those identities. Deleting or renaming a built item requires an explicit migration. Adding or changing items invalidates build/native evidence. Generated code and embedded data ship in the project DLL; the toolkit and authoring files are not package inputs.

The native suite checks pools/eligibility, acquisition, fallback icons/text, exact effect deltas, repeated turns/combat reset, duplicate triggers/actions and serialization. Full run save/resume also preserves acquired relic IDs and potion slots. Headless fixtures do not establish co-op, visual quality, arbitrary extension behavior or balance.

Skip outcome: clear relics and potions, remove `starting_relic`, then disable `features.items`. The character uses Burning Blood and native relic/potion pools. Saved-ID protection still applies after a build; disabling an item library is not an automatic migration.
