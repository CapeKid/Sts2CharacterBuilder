# Character builder implementation status

This implementation advances [issue #1](https://github.com/CapeKid/Sts2CharacterBuilder/issues/1); it does not close the full design's release gates. The original extraction plan remains at [character-builder-design.md](character-builder-design.md).

## Implemented

- Agent-neutral entry/resume workflow and 15 focused skills covering setup, mechanics, cards, art, items, events, dialogue, sprites, presentation, audio, correctness, balance, publishing and upgrades. Guided mode collects choices in short groups; expedited mode delegates creative defaults. Disabled custom content and delegated content have different outcomes.
- Python standard-library CLI: `init`, `doctor`, `validate`, `generate`, `resume`, `record`, `test`, `balance`, `build`, `stage`, `compare-delivery`.
- A new local character repository with its own identity, original visible SVG placeholders, tracked lock/model IDs, explicit source ownership and an actual pinned Git submodule. No global skill installation. Existing destinations are refused.
- Strict authoring contracts and SHA-256 provenance; duplicate IDs/JSON properties, unsupported numeric effects, dangling deck references, unsafe paths, malformed assets and changed hashes fail checks. Generated-file conflicts are checked before mutation.
- A small conventional BaseLib 3.4.7/net9.0 character template with six prototype cards, explicit upgrades, basic damage/Block/draw/Energy/Exhaust effects, a run-local Focus power and an optional starter relic. Native deck/pool/relic/presentation fallbacks support skipped custom features. No cross-run progression is extracted.
- Partial classes and explicit extension hooks allow project-owned cards, pools, starting kits and presentation without editing the submodule or generated files. Generated model IDs freeze after the first successful native build and remain tracked across clones.
- Hashed workflow evidence with conservative invalidation. Structural/compile/heuristic/delivery evidence is labeled separately. Builds record actual game metadata, references, inputs, source and DLL hashes.
- Closed, deterministic private-test ZIP staging from a current build receipt; only the project DLL/manifest, declared assets, license and package report ship. BaseLib is an external dependency. Exact downloaded-byte comparison rejects extra/missing files.
- Official-uploader publishing skill and preparation/delivery procedure, without using the reference mod's Workshop identity or live release.

## Verified locally

On Windows, the behavioral suite exercises actual local submodule initialization, two distinct project identities/modes in paths containing spaces, a fresh recursive clone, pinned-toolkit checks, regeneration, extension preservation, saved-ID protection, invalid authoring data, stale evidence/builds, balance warnings and deterministic closed packages.

Generated custom-card/Focus and native-fallback/extension configurations compile against the locally owned **StS2 v0.111.0** assemblies with **BaseLib 3.4.7**. These are compilation checks, not in-game card lifecycle or save/resume tests. No personal saves or Workshop items were modified. All 15 skill files passed the skill-creator validator. The CI matrix runs the portable suite on Windows/Linux with Python 3.11/3.12; remote CI results must be inspected separately.

## Remaining completion gates

| Design milestone | Remaining work |
| --- | --- |
| Portable foundation | Local behavioral evidence exists; inspect remote cross-platform CI before claiming those hosts verified. |
| Native minimal character | Isolated native registration/selection, target/energy/effect/card disposal, turn flow, resource lifecycle, save/resume and room presentation. Regular-branch build/native evidence is still missing. |
| Optional authoring | Skills and extension contracts exist; generic generators/native fixtures for custom events, Ancient dialogue, sprite/audio integration, drop relics and potions remain unimplemented. A flag records intent, not implemented behavior. Per-card art integration remains project-owned. |
| Verification/balance | Actual native comparator counts and rarity/type cross-distribution, full effect/upgrade fixtures, bounded archetype playtests, human balance observations and applicable controller/Deck/co-op evidence. The small bootstrap pool is not native-sized. |
| Publishing/clean-room delivery | Pinned official uploader integration, authorized private upload/new-item/update trials, authenticated visibility checks, downloaded hashes and an independently tested playable second character. The staging CLI alone does not satisfy this gate. |

Do not call an enabled optional feature complete merely because its skill exists. Reports keep unperformed native/device/distribution checks as gaps and never set `release_ready` true. The reference `sts2/`, `sheets/`, original content and publishing tools are untouched as runtime/package inputs.

See [workflow and commands](../builder/WORKFLOW.md), [extension contract](../builder/EXTENSIONS.md) and [publication preparation](../builder/PUBLISHING.md).
