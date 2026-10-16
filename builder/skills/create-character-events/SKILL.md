---
name: create-character-events
description: Author optional character-specific events and test their registration and outcomes.
---

Ask whether events are wanted, collect all ideas, and offer AI completion separately. Write project-owned event design/localization and src/Extensions implementations against the selected branch's actual API.
Specify encounter eligibility, choices, costs, rewards, unavailable-choice text, re-entry and save behavior. Use explicit character predicates so unrelated characters are unaffected. Record co-op policy only if supported and tested.
The baseline generator does not implement events. An enabled flag is a request to author and integrate a module, not evidence of registration. Verify each choice, insufficient-resource boundary, interruption/save return and disabled-feature behavior in the game.
Output event sources, localization and native evidence. Skip outcome: no added event registration; set events false.
