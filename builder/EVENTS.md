# Character events

Optional `design/events.json` follows [events.schema.json](events.schema.json). New projects start with an empty array. Missing or empty data registers no events. Enable `features.events` before authoring nonempty data.

```json
[
  {
    "id": "QuietCamp",
    "name": "A Quiet Camp",
    "body": "A traveler offers a moment of rest.",
    "acts": [1, 2],
    "choices": [
      {
        "id": "Rest",
        "name": "Accept the offer",
        "result": "Rested, you continue your journey.",
        "cost": { "gold": 30, "hp": 0 },
        "reward": { "gold": 0, "heal": 12 }
      }
    ]
  }
]
```

Each event starts at its existing body/choices (`INITIAL`) and may add one to seven entries in `pages`. Every page has one to four authored choices and an automatically added Leave option. Single-page data remains valid. Each choice has an ID, title, explicit cost/reward values and exactly one destination: terminal `result` text or navigation `next` page ID. Bounds are 0–300 Gold and 0–30 HP for costs, and 0–300 Gold and 0–50 healing for rewards. A terminal choice must have at least one positive value. Navigation choices must have all four values zero and omit `result`; only terminal choices apply resource effects. These limits do not certify balance. Up-front affordability is checked even when a choice also grants Gold or healing.

Branch pages have `id`, `body` and `choices`; a navigation choice uses `"next": "Camp"` instead of `result`. Page references are exact and case-sensitive. The graph must be reachable from INITIAL and acyclic; converging paths are allowed. INITIAL, LEFT and IDs beginning with RESULT are reserved. Leave is reserved on every page. Choice IDs must be unique within their page, but may repeat on different pages. Page IDs are not native model IDs; editing a graph preserves its `Event_<id>` identity while invalidating prior build/evidence fingerprints. See the original [Crossroads example](examples/crossroads/events.json) for two paths converging on a shared page. Effects during navigation, loops and arbitrary conditional branching require extensions.

An HP payment must leave at least 1 HP. Unaffordable choices are locked; their descriptions still show the required Gold/HP. Callbacks check affordability again in case resources changed while the page was open. A stale choice refreshes its locked state without charging resources. Leave is always available and changes no resources. Page revisions reject old and sibling callbacks after navigation or an affordability refresh, including old Leave callbacks. Terminal choices claim resolution before awaited commands so they cannot apply a second outcome. Native commands handle Gold, unblockable/unpowered HP damage and healing; normal game modifiers and healing caps still apply.

`acts` selects one or more of the three act positions, including native variants of those acts. BaseLib registers the generated models in those act pools. Eligibility requires exactly one player using this project's character. Co-op and other characters use native events; this first contract does not implement shared-event voting or multiplayer outcomes. Forced debug entry bypasses random encounter eligibility and is used only by the isolated tests.

Titles, body, choice titles, generated cost/reward descriptions, result pages and Leave text use BaseLib's English inline localization. Standard native localization formatting applies; arbitrary dynamic variables are not supplied by this contract. Event imagery/background/VFX use Tablet of Truth's runtime paths as explicit placeholders. No native imagery is shipped. Custom art/layouts, combat encounters, card/item rewards, custom eligibility and arbitrary effects require project-owned extensions and separate evidence.

The events follow ordinary native event checkpoint behavior. Saving before a choice permits re-entering INITIAL with the checkpoint's resources. Branch navigation is transient: reloading while on a later page restarts the event at INITIAL. No branch position or custom journal is saved. Interrupting before leaving restores that checkpoint, including its pre-choice resources. Leaving the event and saving the next room preserves the outcome. There is no custom mid-choice transaction log, crash recovery journal or forced save of a finished event page. Do not force a save halfway through an awaited callback and describe that as supported recovery. The native fixture checks these checkpoint/rollback/replay/persistence controls for every page, using a deterministic path to a terminal outcome.

Run `validate`, `generate`, `build` and a fresh isolated native lab. Generated code/data live in owned `src/Generated/Events.cs`; the file is removed when event data becomes empty before IDs are frozen. `Event_<id>` model IDs freeze on the first successful build. Later removals or renames need an explicit migration, as with cards and items. Event data participates in build/evidence fingerprints; old native evidence cannot certify new event choices. The closed package contains the compiled models, without the toolkit or authoring files.

The native suite checks act registration, solo/foreign-character eligibility, visible option buttons and text, Gold/HP thresholds, stale affordability, exact unmodified effects, duplicate selection, Leave, and checkpoint behavior for every authored page/choice, plus visible destination text, old-page callback rejection and every page's Leave/checkpoint cases. Evidence identifies choices by event/page/choice; repeated choice IDs on different pages remain distinct. Headless checks do not establish visual layout quality, physical controls, co-op, arbitrary extensions or balance.

Skip outcome: clear the array and disable `features.events`; no custom event registration is emitted. An enabled flag with no data remains an explicit gap, not a completed module. Saved-ID protection still applies after a build.
