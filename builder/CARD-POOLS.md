# Completing an original card pool

The bootstrap is eight cards, including three basics. Full-pool completion is an authoring task: preserve supplied ideas, choose coherent build themes and add distinct supported cards. Repeating numeric cards until a counter is satisfied does not complete a character.

First generate a valid prototype and collect a passing [native baseline](NATIVE-TESTING.md) on the selected branch. Capture one observed built-in character's reward targets before editing:

```powershell
python tools/character-builder/scripts/character-builder.py --project . plan-cards --comparator CHARACTER.IRONCLAD
```

This writes `.builder/card-pool-baseline.json` with the native evidence path/hash, game build, target branch, toolkit pin, rarity/type cells and hashes of the original authored cards. The raw comparator catalog remains in private evidence. Capture requires complete current native coverage. A missing/unknown comparator or a stale lab fails without replacing an existing baseline.

Plans cover generated cards in `design/cards.json`. Extension-only models and bespoke behaviors need separate reconciliation and native fixtures.

While authoring, run:

```powershell
python tools/character-builder/scripts/character-builder.py --project . plan-cards
```

The report compares the current reward pool with those historical targets even after edits invalidate the old native pass. It lists missing/excess cells, basics separately, added cards, original cards changed/removed and reward cards with identical generated mechanics. Duplicate warnings ignore names, portraits and rarity, and compare type, target, Exhaust and all base/upgraded numeric values. They are review prompts; project-owned extension behavior may distinguish otherwise identical cards. Slightly different numbers can still be redundant, so these warnings do not certify originality or archetype coverage.

Review changed/removed supplied ideas and explain intentional revisions in the project design. Fill deficits around coherent themes and meaningful tradeoffs. Matching total count alone is insufficient; each rarity/type cell matters. Basics are excluded from reward counts. The comparator count comes from the tested build, with no universal hardcoded target. Unsupported effects require [project-owned implementation and fixtures](EXTENSIONS.md).

Keep the baseline and its referenced private evidence intact while planning. They are ignored local workflow files excluded from packages. A fresh clone must collect its own baseline. A toolkit or target-branch change requires a fresh baseline. To deliberately reset both targets and the original-card snapshot, collect a passing current native run and use `plan-cards --comparator <exact-id> --replace-baseline`. An ordinary planning call never replaces them.

After editing, run `generate`, `validate`, `balance`, and a **new** one-shot native lab covering every card in both upgrade states, rewards/shop and save/resume. Then run `balance --comparator <exact-id>` for current native parity. The planner never supplies native completion evidence or changes `release_ready`; old baseline evidence is accepted only for planning. A matching plan still needs current native verification, archetype/campaign playtests and human balance observations. A declined completion stays a labeled small-pool prototype; disabled custom cards use the native fallback rather than an original full pool.
