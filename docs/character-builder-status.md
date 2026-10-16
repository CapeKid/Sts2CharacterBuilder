# Character builder implementation status

This implementation advances [issue #1](https://github.com/CapeKid/Sts2CharacterBuilder/issues/1); it does not close the full design's release gates. The original extraction plan remains at [character-builder-design.md](character-builder-design.md).

## Implemented

- Agent-neutral entry/resume workflow and 15 focused skills covering setup, mechanics, cards, art, items, events, dialogue, sprites, presentation, audio, correctness, balance, publishing and upgrades. Guided mode collects choices in short groups; expedited mode delegates creative defaults. Disabled custom content and delegated content have different outcomes.
- Python standard-library CLI: `init`, `doctor`, `validate`, `generate`, `resume`, `record`, `test`, `balance`, `build`, `stage`, `compare-delivery`, `prepare-lab` and `test-native`.
- A new local character repository with its own identity, original visible SVG placeholders, tracked lock/model IDs, explicit source ownership and an actual pinned Git submodule. No global skill installation. Existing destinations are refused.
- Strict authoring contracts and SHA-256 provenance; duplicate IDs/JSON properties, unsupported numeric effects, dangling deck references, unsafe paths, malformed assets and changed hashes fail checks. Generated-file conflicts are checked before mutation.
- A small conventional BaseLib 3.4.7/net9.0 character template with eight prototype cards, explicit upgrades, basic damage/Block/draw/Energy/Exhaust effects, a run-local Focus power and an optional starter relic. The reward pool includes enough Attack/Skill/Power models for normal merchant population. Native deck/pool/relic/presentation fallbacks support skipped custom features. No cross-run progression is extracted.
- Partial classes and explicit extension hooks allow project-owned cards, pools, starting kits and presentation without editing the submodule or generated files. Generated model IDs freeze after the first successful native build and remain tracked across clones.
- Hashed workflow evidence with conservative invalidation. Structural/compile/heuristic/delivery evidence is labeled separately. Builds record actual game metadata, references, inputs, source and DLL hashes.
- Closed, deterministic private-test ZIP staging from a current build receipt; only the project DLL/manifest, declared assets, license and package report ship. BaseLib is an external dependency. Exact downloaded-byte comparison rejects extra/missing files.
- Official-uploader publishing skill and preparation/delivery procedure, without using the reference mod's Workshop identity or live release.
- Disposable native labs with independent game copies, explicit account/mod discovery, unique profiles, byte/profile/catalog checks, a replaced save backend and one-shot test execution. The probe is conditionally compiled into a separate DLL and absent from normal builds/packages. Successful complete native evidence is invalidated when inputs/source/toolkit/release bytes change; the report can supply observed native pool cell targets to balance comparisons.

## Verified locally

On Windows, the behavioral suite exercises actual local submodule initialization, two distinct project identities/modes in paths containing spaces, a fresh recursive clone, pinned-toolkit checks, regeneration, extension preservation, saved-ID protection, invalid authoring data, stale evidence/builds, balance warnings and deterministic closed packages.

Generated custom-card/Focus and native-fallback/extension configurations compile against the locally owned **StS2 v0.111.0** assemblies with **BaseLib 3.4.7**. An independent Windows/headless game fixture additionally passed **26 native checks**: registration/icon load, starter deck/relic/resource, all eight bootstrap cards plus two fixture-only Energy/AoE cards in base/upgraded paid actions, upgraded draw/Energy/Focus text, Focus turn behavior, reward/shop membership, an upgraded deck saved/resumed through the game, relic identity preservation and resource reset in a new combat. It exported native pool counts and rarity/type cells from the installed build. The fixture exposed the earlier six-card prototype's insufficient merchant coverage; descriptions now also evaluate numeric Rules at render time so upgrade text follows the active values.

These results cover the generated numeric vocabulary on that build, not arbitrary custom effects or visual correctness. Dedicated lab profiles and a mocked save backend were used; no regular saves or Workshop items were modified. See [native testing](../builder/NATIVE-TESTING.md) and [the recorded fixture summary](native-character-fixture.json). All 15 skill files passed the skill-creator validator. The CI matrix runs the portable suite on Windows/Linux with Python 3.11/3.12; remote CI results must be inspected separately.

## Remaining completion gates

| Design milestone | Remaining work |
| --- | --- |
| Portable foundation | Local behavioral evidence exists; inspect remote cross-platform CI before claiming those hosts verified. |
| Native minimal character | Numeric lifecycle/resource/save-resume/reward/shop fixtures passed locally on v0.111.0. Visual selection/room/death/victory review and regular-branch build/native evidence remain missing. |
| Optional authoring | Skills and extension contracts exist; generic generators/native fixtures for custom events, Ancient dialogue, sprite/audio integration, drop relics and potions remain unimplemented. A flag records intent, not implemented behavior. Per-card art integration remains project-owned. |
| Verification/balance | Native comparator counts/cells and generated numeric base/upgrade fixtures now exist. Original full-pool completion, bespoke-effect fixtures, bounded archetype playtests, human balance observations and applicable controller/Deck/co-op evidence remain. The small bootstrap pool is not native-sized. |
| Publishing/clean-room delivery | Pinned official uploader integration, authorized private upload/new-item/update trials, authenticated visibility checks, downloaded hashes and an independently tested playable second character. The staging CLI alone does not satisfy this gate. |

Do not call an enabled optional feature complete merely because its skill exists. Reports keep unperformed native/device/distribution checks as gaps and never set `release_ready` true. The reference `sts2/`, `sheets/`, original content and publishing tools are untouched as runtime/package inputs.

See [workflow and commands](../builder/WORKFLOW.md), [extension contract](../builder/EXTENSIONS.md) and [publication preparation](../builder/PUBLISHING.md).
