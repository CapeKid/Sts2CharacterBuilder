# Sts2CharacterBuilder

A separate development repository for an AI-guided Slay the Spire 2 character-builder toolkit.

**Status:** portable prototype implementation. The builder now bootstraps pinned submodule projects, generates a small conventional character, validates designs, resumes evidence-backed work, compiles against owned game references, flags balance risks and stages closed private-test packages. Native gameplay, full optional-content generation and Workshop clean-room delivery gates remain open; this is not yet a finished generic builder.

Start an AI at [the create-character skill](builder/skills/create-character/SKILL.md). It routes guided or idea-only authoring through focused skills, including art, items, events, dialogue, sprites, audio, verification, balance and publishing. See [commands and ownership](builder/WORKFLOW.md), [publishing](builder/PUBLISHING.md) and [implementation status](docs/character-builder-status.md).

```powershell
python scripts/character-builder.py --project ../MyCharacter init --id MyCharacter --idea "Your character concept" --mode expedited
```

The initial eight-card design is a prototype, not an automatically completed native-sized card pool. Cards can select declared SVG/PNG portraits through an optional `portrait` field; see [card art](builder/ART.md). Optional [item data](builder/ITEMS.md) generates starting/drop/shop relics and combat potions with native pool integration and optional normal/outline/large SVG/PNG art. Optional [event data](builder/EVENTS.md) adds single-page solo encounters with bounded costs/rewards and native checkpoint behavior. Optional [dialogue data](builder/DIALOGUE.md) adds first/repeat conversations for ordinary Ancients with native reward access and English fallback. Optional [combat sprite data](builder/SPRITES.md) integrates SVG/PNG atlases with six native animation states, anchors, timing and reconstruction. Optional [room presentation data](builder/PRESENTATION.md) adds independent rest/shop atlases, native action responses and optional selection portraits/backgrounds. Optional [sound-effect data](builder/AUDIO.md) routes short PCM WAV selection/transition/attack/cast/death cues with native volume controls. The runtime implements a bounded effect vocabulary and a run-local Focus power. Agents author bespoke features in project-owned extensions. Disabled optional features use explicit native/original-placeholder fallbacks. Generated packages do not include the reference mod, game files or the toolkit.

`prepare-lab` and `test-native` provide opt-in isolated gameplay checks using an independent copy of an owned game and a dedicated save backend. The test-only probe is excluded from normal builds/packages. A local v0.111.0 fixture passed 107 native checks, including extra Energy/AoE cases, per-card portrait loading, authored relic/potion artwork and lifecycles, event/checkpoint cases, Ancient conversations, locale reloads, combat sprite states, Fairy in a Bottle recovery, short character sound routing/mute/cleanup, independent rest/shop action/reconstruction, Windows progress-reader lock controls and native selection portrait/unlock/background/navigation checks; see [native verification](builder/NATIVE-TESTING.md) for coverage and remaining limits. `balance --comparator CHARACTER.IRONCLAD` uses a passing current lab's native rarity/type counts rather than a hardcoded full-pool target.

- [Full card-pool planning](builder/CARD-POOLS.md)
- [Original 85-reward-card sample](builder/examples/steady-path/README.md)
- [Bounded native archetype observations](builder/PLAYTESTS.md)
- [Design and extraction plan](docs/character-builder-design.md)
- [Implementation issue](https://github.com/CapeKid/Sts2CharacterBuilder/issues/1)
- [Spire Legacy reference documentation](SPIRE_LEGACY_REFERENCE.md)
- [Original mod repository](https://github.com/CapeKid/SpireLegacy)

The scope is conventional standalone characters, guided and expedited authoring, modular skills and verification tools. Cross-run progression, heirs, inheritance, manor upgrades and crowns are permanently excluded.

Independent fresh-clone and custom-content-disabled characters also passed native numeric/save-resume and package checks; [their receipts](docs/independent-character-fixtures.json) separate executed records from skipped-feature sentinels. Human/device/live-delivery gates remain open.

The optional Steady Path sample preserves the bootstrap cards and adds 80 original designs around defense, draw/Energy preparation and attacks. Its 85 reward cards match the observed v0.111.0 Ironclad rarity/type cells. A fresh full-pool native lab passed 360 executed checks plus seven omitted-feature sentinels, including every card in both upgrade states and a 26-card deck saved/resumed with reward representatives; see [the receipt](docs/full-pool-native-fixture.json). Placeholder art, 25 heuristic balance warnings and unperformed human/campaign review remain explicit.

`prepare-publish` and `check-publish` prepare an offline private workspace using a hash-pinned Mega Crit uploader archive and exact staged payload. They preserve explicit update identity and never upload; see [publishing](builder/PUBLISHING.md). Live Workshop creation/update and authenticated download verification remain completion gates.

This repository preserves the complete history of the character-builder branch through `60322dafc054f97d2c5c534dce3552f90fad4757`. It is an independent development fork because GitHub does not allow one account to own both a parent repository and its fork. Builder work belongs here; the Spire Legacy repository remains focused on the mod.

Inherited build and publishing scripts are reference material and still contain Spire Legacy-specific identifiers. Do not use them to publish this toolkit or another character to the existing mod's Workshop item. The extraction plan explains the required project configuration and identity separation.

Original code and content retain their existing [MIT license](LICENSE) and dependency notices.
