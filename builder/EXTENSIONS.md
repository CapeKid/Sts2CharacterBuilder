# Project-owned native extensions

The generator supports a small numeric effect vocabulary. Keep bespoke implementations in the character repository's `src/Extensions/`; the project compiles those files and regeneration preserves them. They are included in verification/build fingerprints. Do not write customizations into the toolkit submodule.

Per-card SVG/PNG portraits use the optional data-driven `portrait` field; see [card art](ART.md). No extension override is needed for that supported path. `ModEntry.Texture` loads only SVG/PNG assets declared in the manifest, using paths relative to `assets/` (for example `cards/strike.png`). Other presentation behaviors still require project-owned code.

Supported starting/drop relics and combat potions use optional `design/items.json`; see [items](ITEMS.md). Use extensions for effects, targets, art and timing outside that numeric contract.

The generated `Character`, `StarterRelic`, `FocusPower` and `ModEntry` are partial classes. Add presentation/lifecycle overrides in another part of the same class when the generator does not already define that member. For members already generated, use the hooks below or a separately implemented model. Do not duplicate an override in a partial class.

For example, in `src/Extensions/Configure.cs`, using the project's actual namespace:

```csharp
using MegaCrit.Sts2.Core.Models;

namespace MyCharacter;

public static partial class ModEntry
{
    static partial void Configure()
    {
        ExtensionHooks.StartingRelics = () => [ModelDb.Relic<MyStarterRelic>()];
        ExtensionHooks.AdditionalCards = () => [ModelDb.Card<MyBespokeCard>()];
    }
}
```

Implement those models against the pinned BaseLib/game API. `StartingDeck`, `StartingRelics`, `CardPool`, `RelicPool`, `PotionPool` and `Icon` hooks replace the corresponding fallback. `AdditionalCards` appends to the generated custom card pool; it does not modify a selected native pool. If custom cards are disabled, supply your own pool hook for additional cards. Pool/deck providers must be canonical model lookups, without stateful gameplay effects during enumeration.

`Configure` runs during mod initialization. Set delegates there; avoid eagerly accessing models before registration finishes. A custom card can return `ModelDb.CardPool<CharacterCardPool>()` from its Pool property and use its own OnPlay/upgrade/save fields. Project-owned extension model IDs must remain stable across releases; the generated model-ID baseline covers only generated models. Track extension IDs and migrations explicitly in project design notes.

For events/dialogue, register narrowly scoped hooks from Configure and test every enabled condition. For sprites/audio, add the selected branch's presentation overrides and record actual visual/audible observations. Asset files alone do not prove integration. Disable a generated Focus mechanic before replacing it with an unrelated resource, and make the choice before its IDs freeze where possible.
