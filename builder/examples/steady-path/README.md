# Steady Path: original numeric full-pool example

This original MIT-licensed sample shows a complete reward-count design within the builder's supported numeric vocabulary. It preserves all eight bootstrap card definitions and adds 80 individually named designs: **85 reward cards plus three basics**. It is an optional authoring reference, not the default for every character and not a balance-certified release.

The concept is a patient traveler who combines lasting defense, preparation and decisive attacks. These are ordinary run-local combat mechanics. The custom **Focus** here grants Block at turn end; it is not the native orb mechanic.

| Theme | Plan | Examples and tradeoffs |
| --- | --- | --- |
| Patient defense | Buy time with Block and accumulate Focus; choose when to spend Energy establishing defense instead of attacking. | Quiet Practice and Fortify exhaust. Settled Mind and Mountain Poise are Powers that leave combat after use. Defensive packages still need damage to finish encounters. |
| Traveling light | Draw toward useful attacks, then spend finite Energy bursts on a decisive turn. | Survey and Breathe cost Energy. Pack Light, Trail Rations and Expedition Plan exhaust. Repeatable draw cards do not refund their full Energy cost. |
| Clear the trail | Choose efficient single-target damage or broader coverage, with defensive/tempo bridges. | Long Stride commits two Energy to one foe; Trail Sweep spreads lower damage. Calm Through Chaos trades Exhaust and cost for damage, Block and Focus. |

Not every card belongs to a rigid archetype. Guarded Step, Even Pace and Read and Respond bridge offense, defense and cycling; upgrades change numbers or costs explicitly. Every card's rules are generated from its actual values. No unsupported effect exists only in prose. The 19 reward Powers all use Focus with distinct immediate resource/Block/draw packages; this is an intentional limitation of the current vocabulary, not evidence of 19 novel mechanics.

The rarity/type cells below match the **observed v0.111.0 Ironclad** comparator used for this example. Other branches/builds require their own current native comparison; these numbers are not global authoring defaults.

| Rarity | Attack | Skill | Power | Total |
| --- | ---: | ---: | ---: | ---: |
| Common | 13 | 7 | 0 | 20 |
| Uncommon | 15 | 14 | 9 | 38 |
| Rare | 8 | 9 | 10 | 27 |
| Total | 36 | 30 | 19 | 85 |

To try the example, initialize a **new** character project using the [normal workflow](../../WORKFLOW.md). Collect a small-pool native baseline and capture [planning targets](../../CARD-POOLS.md). Copy `cards.json` from this directory to the project's `design/cards.json`, keep the default starting deck/Focus feature, then run `generate`, `validate`, `balance`, a new native lab and `balance --comparator CHARACTER.IRONCLAD`. Do not replace another author's supplied card ideas with the sample. Existing saved model IDs must remain stable. Do not edit the submodule to customize a project.

The sample uses the shared original placeholder card art. It makes no human art, campaign, fun, physical-device or co-op claim. Balance warnings are intentionally retained for review: early Focus can trivialize weak enemy turns, large Block and Focus packages may be excessive, draw chains may compress decisions, and one-shot Energy bursts may dominate early drafting. Defensive stalling and Rare Power redundancy need human playtests, with predeclared decks/seeds/encounters and capped attempts. Do not automatically buff a sample because an automated run loses.

See [the sanitized full-pool native receipt](../../../docs/full-pool-native-fixture.json) for the tested revision/build, coverage and remaining gates. The owned game, private catalogs, logs, profiles and fixture project are not shipped with this example.
