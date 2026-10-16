---
name: verify-character
description: Verify generated character data, builds and native behavior with precise coverage gaps.
---

Run validate, generate --check, test and build as described in [the workflow](../../WORKFLOW.md). Record toolkit/project revision, source/input/DLL hashes, game branch/build and dependency versions. The structural report always distinguishes native gaps.
Exercise native selection, starter deck/relic, new card base/upgraded values, new power/resource, turn flow, targeting, card disposal, reward/shop/compendium and save/resume on each claimed branch. Test disabled features and malformed inputs. Custom effects require specific expected outcomes, not a loop that merely instantiates cards.
Use prepare-lab and test-native from [native testing](../../NATIVE-TESTING.md) for the generated numeric fixtures. These create independent copies, a dedicated profile, disabled Workshop mods and a replaced save backend; each lab runs only once. Read the emitted evidence and actual coverage. Native code is excluded from normal packages. Keep the imported reference-mod launchers out of this workflow.
Output project-relative evidence and record each completed stage. Physical Deck, online co-op, unavailable branches and unsupported effects remain named gaps. Do not mark release-ready while essential gaps remain.
