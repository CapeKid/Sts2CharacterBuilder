# Project-owned native extensions

The generator supports a small numeric effect vocabulary. Keep bespoke implementations in the character repository's `src/Extensions/`; the project compiles those files and regeneration preserves them. They are included in verification/build fingerprints. Do not write customizations into the toolkit submodule.

Per-card SVG/PNG portraits use the optional data-driven `portrait` field; see [card art](ART.md). No extension override is needed for that supported path. `ModEntry.Texture` loads only SVG/PNG assets declared in the manifest, using paths relative to `assets/` (for example `cards/strike.png`). Other presentation behaviors still require project-owned code.

Supported starting/drop relics and combat potions, including declared normal/outline/large artwork, use optional `design/items.json`; see [items](ITEMS.md). Use extensions for effects, targets, visual behavior and timing outside that contract.

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

For bounded branching solo events, use [event data](EVENTS.md). For ordinary Ancient first/repeat conversations, use [dialogue data](DIALOGUE.md). For narrative content outside those contracts, register narrowly scoped hooks from Configure and test every enabled condition. The optional generated dialogue initializer is separate from Configure; do not implement its reserved partial method in extensions. For presentation/audio outside the generated contracts, add the selected branch's overrides and record actual visual/audible observations. Asset files alone do not prove integration. Disable a generated Focus mechanic before replacing it with an unrelated resource, and make the choice before its IDs freeze where possible.

The template restores this assembly's inline `ILocalizationProvider` text before native locale-change UI listeners run. Character/card/relic/potion/power/event categories use their normal tables; other extension categories must supply `LocTable`. This re-evaluates providers in the selected language, so extension providers may return translated text with an English fallback. Keep those getters free of gameplay mutations.

Combat atlases can use [sprite data](SPRITES.md) without a handwritten factory. When enabled, the generated Character partial owns `CreateCustomVisuals` and the reserved `ModEntry.InitializeSprites` partial method. Use an extension factory only when generated sprites are disabled/empty; register bespoke triggers and other presentation explicitly; [room data](PRESENTATION.md) can author rest/shop visuals independently.

Short character effects can use [audio data](AUDIO.md). Generated Audio.cs owns only configured select/transition/attack/cast/death getters, conditional hurt/victory event hooks and the reserved `ModEntry.InitializeAudio` partial method. Use extensions for other routes; do not replace a generated getter or add a second broad audio interceptor.

Generated room presentation owns rest/shop body replacement only where configured, plus the reserved `ModEntry.InitializePresentation` partial method. Do not install a second room-body replacer for the same scenes. Native inputs, thought bubbles, healing, merchant transactions and saves remain native; human layout/device and co-op campaign evidence are still required.

Selection portraits/backgrounds can use the [presentation contract](PRESENTATION.md). Generated Selection.cs owns only configured character art and the reserved `ModEntry.InitializeSelection` partial method. Do not install another portrait/background replacer for the same selector. Native locks, focus and Back behavior remain native. Run-start transitions and ending art require separate extensions and evidence.
## Item artwork ownership

Generated `Items.cs` owns optional `art.icon`, `art.outline` and `art.large` image-path overrides, its namespace-specific cached resource paths and the reserved `ModEntry.InitializeItems` partial method. Declared SVG/PNG textures register before native preloading and recover after disposal. The native asset-cache hook recognizes only exact registered paths; unassigned roles retain native paths. Keep bespoke item types in project-owned source and do not duplicate generated overrides. See [items](ITEMS.md).
