---
name: verify-character
description: Verify generated character data, builds and native behavior with precise coverage gaps.
---

Run validate, generate --check, test and build as described in [the workflow](../../WORKFLOW.md). Record toolkit/project revision, source/input/DLL hashes, game branch/build and dependency versions. The structural report always distinguishes native gaps.
Exercise native selection, starter deck/relic, new card base/upgraded values, new power/resource, turn flow, targeting, card disposal, reward/shop/compendium and save/resume on each claimed branch. Test disabled features and malformed inputs. Custom effects require specific expected outcomes, not a loop that merely instantiates cards.
Use an isolated test game/profile with Steam Cloud disabled. Inspect the imported TestIsolation/lab tools for containment lessons; they contain reference-mod identities and are not generic launchers. Do not run tests against personal saves or claim a source/compile pass as native evidence.
Output project-relative evidence and record each completed stage. Physical Deck, online co-op, unavailable branches and unsupported effects remain named gaps. Do not mark release-ready while essential gaps remain.
