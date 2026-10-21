---
name: assess-character-balance
description: Assess card power, resource loops and archetype balance without automatic tuning.
---

Run balance for bounded heuristic warnings and merchant coverage. After a passing current [native lab](../../NATIVE-TESTING.md), use balance --comparator with an exact native character ID to compare the rarity/type cross-distribution. It reports cell deficits/excess, not balance quality. Inspect base and upgraded combined effects; the thresholds are triage, not native balance scores.
Use [plan-cards](../../CARD-POOLS.md) while editing a full pool: capture targets from a current lab first, then review deficits, altered/removed original cards and identical-mechanics groups after edits. Count parity and varied names/art do not establish coherent archetypes. Historical planning targets cannot replace fresh native evidence for the final comparison.
Compare each card against relevant native cards from the selected build, including targeting, costs, exhaust, draw, recursion, multi-hit and scaling. Record comparator IDs/build and why a combined effect justifies its price. Check both overpowered and underpowered cards.
Search repeatable zero-cost draw/Energy/resource loops, recursion and unbounded triggers. Sample coherent archetypes with predeclared decks, seeds, floors and test caps. Distinguish mechanical correctness from campaign strength and fun.
For generated-card combinations, optional [bounded native playtests](../../PLAYTESTS.md) run predeclared decks/seeds through real Nibbits combat under ordinary resources. Keep policy, starting upgrades and caps explicit; report victory/defeat/cap outcomes as scripted observations. `balance` exposes only current complete trials. The example's greedy policy and one encounter cannot certify campaign balance or justify automatic tuning.
Output findings with evidence and separate proposed tuning. Automated losses alone do not justify buffs. Never import the original mod's card overrides, progression economy or claimed win-rate targets.
Skip outcome: release balance remains unassessed; retain an explicit prototype label.
