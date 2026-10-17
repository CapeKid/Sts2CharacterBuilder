# Character authoring workflow

Start at [create-character](skills/create-character/SKILL.md). Every substantial stage has a sibling skill with its inputs, outputs, checks and skip result. Agents without automatic skill discovery follow these Markdown files directly. No global skill installation is needed.

| Stage | Skill |
| --- | --- |
| Setup | [setup-character-project](skills/setup-character-project/SKILL.md) |
| Mechanics | [design-character-mechanics](skills/design-character-mechanics/SKILL.md) |
| Cards | [create-character-cards](skills/create-character-cards/SKILL.md) |
| Art | [create-character-art](skills/create-character-art/SKILL.md) |
| Items | [create-character-items](skills/create-character-items/SKILL.md) |
| Events | [create-character-events](skills/create-character-events/SKILL.md) |
| Ancient dialogue | [create-character-dialogue](skills/create-character-dialogue/SKILL.md) |
| Sprites | [create-character-sprites](skills/create-character-sprites/SKILL.md) |
| Presentation | [create-character-presentation](skills/create-character-presentation/SKILL.md) |
| Audio | [create-character-audio](skills/create-character-audio/SKILL.md) |
| Correctness | [verify-character](skills/verify-character/SKILL.md) |
| Balance | [assess-character-balance](skills/assess-character-balance/SKILL.md) |
| Publication | [publish-character](skills/publish-character/SKILL.md) |
| Later upgrades | [upgrade-character-project](skills/upgrade-character-project/SKILL.md) |

## Commands

Python 3.11+ and Git are required; native builds additionally require .NET 9+ and your owned game references. The CLI uses Python's standard library. Run from any directory with an explicit project root. Put options before the command, as shown.

```powershell
# From a committed toolkit checkout; the destination must not exist.
python scripts/character-builder.py --project ../FightingBaby init --id FightingBaby --name "The Fighting Baby" --idea "A fighting baby" --mode expedited --author "Your name"

# Thereafter invoke the project's pinned toolkit, not another checkout.
python tools/character-builder/scripts/character-builder.py --project . resume
python tools/character-builder/scripts/character-builder.py --project . doctor --game-data "C:/your/owned/game/data_sts2_windows_x86_64"
python tools/character-builder/scripts/character-builder.py --project . validate
python tools/character-builder/scripts/character-builder.py --project . generate
python tools/character-builder/scripts/character-builder.py --project . generate --check
python tools/character-builder/scripts/character-builder.py --project . test
python tools/character-builder/scripts/character-builder.py --project . balance
python tools/character-builder/scripts/character-builder.py --project . build --game-data "C:/your/owned/game/data_sts2_windows_x86_64"
python tools/character-builder/scripts/character-builder.py --project . stage
```

`init` creates a local repository and stages its initial files; it does not create a GitHub repository or an initial project commit. Make that commit after reviewing the generated files. Use `--toolkit-source /local/checkout --toolkit-commit <full-sha>` for an explicit offline source. A relative local source is resolved before cloning. The default source is this public repository, pinned to the invoking checkout's commit; unpushed commits require a local source. Subsequent recursive clones use `.gitmodules` and the gitlink. To publish a character initialized from a local source, review and change `.gitmodules` to a reachable remote containing the same pin.

## Ownership and data

`character.json` owns identity, features, starting deck, target branch and recorded choices. `design/cards.json` follows [cards.schema.json](cards.schema.json); base and upgraded numeric values are explicit. `assets/manifest.json` follows [assets.schema.json](assets.schema.json) and records exact shipped bytes and provenance. Unknown keys, duplicate JSON properties/IDs, dangling deck references, unsupported effects, invalid bounds and unsafe paths fail validation.

Optional `design/items.json` follows [the item contract](ITEMS.md): authored starters, drop/shop relics and combat potions use a bounded numeric effect vocabulary with native pool integration. Missing or empty data preserves the existing starter/potion fallbacks. Item changes participate in evidence fingerprints and generated model-ID protection. Native icons remain runtime fallbacks.

Optional `design/events.json` follows [the event contract](EVENTS.md): single-page solo events with act/character eligibility, bounded Gold/HP costs, Gold/healing rewards and an always-available Leave choice. Empty/missing data registers no events; enabled empty data remains a gap. Models and embedded English localization live in owned `src/Generated/Events.cs`, with frozen IDs and evidence fingerprints. Native imagery and ordinary event checkpoints remain explicit fallbacks.

The portable template implements a small conventional character: damage, Block, draw, Energy, Exhaust and a run-local Focus power. Focus grants Block at turn end; the optional starter relic grants one stack at combat start. The eight bootstrap cards are an intentional prototype: three basics and five reward cards, including the two Attacks, two Skills and one Power needed to populate normal merchant slots. Fill a requested original pool using native comparator evidence before calling it complete. Native energy, item/power icons and character animations currently use runtime fallbacks; authored item pools replace only their configured character pools. No game assets are included in the toolkit or ZIP.

Edit authoring data and run `generate`. The toolkit owns `src/Generated/Character.cs`, optional `src/Generated/Items.cs` and `src/Generated/Events.cs`, `Character.csproj`, the mod manifest and `design/model-ids.json`; `design/generated-files.json` tracks their ownership hashes across clones. Keep handwritten code in `src/Extensions`; it is compiled but never regenerated. The generator refuses changed/unowned outputs. Before the first successful native build, feature choices and model identities remain editable. That build freezes the tracked model-ID baseline; subsequent namespace/ID changes or model removals require an explicit migration. Fresh recursive clones can verify and regenerate outputs using the tracked manifest. A deliberate template change requires preserving/reviewing the old files and a migration; deleting the manifest is not a force-overwrite mechanism.

Ancient dialogue, custom sprites/audio and bespoke mechanics are skill-driven [project extensions](EXTENSIONS.md). Their feature flags record intent; this version has no generic generators or native fixtures for them. Enabling a flag is never proof of implementation. Structural reports name those gaps. Ordinary native content is the skip fallback. For per-card SVG/PNG art, assign an optional `portrait` path to a declared asset; see [portrait integration](ART.md). Cards without an assignment use the shared original placeholder. Character animation/presentation overrides remain project-owned.

Cross-run progression is excluded entirely. The imported `sts2/`, `sheets/`, art and historical scripts remain reference material and are never used as generated project/package inputs.

## Resume and evidence

`resume` computes a fingerprint of configuration, lock, cards, optional items/events, assets and extension source. `record` stores an outcome with evidence file hashes under ignored `.builder/state.json`:

```powershell
python tools/character-builder/scripts/character-builder.py --project . record mechanics --status complete --evidence design/mechanics.md --note "Starting kit and resource reviewed"
```

Statuses are pending, ready, running, complete, skipped and blocked. Disabled optional features report skipped. Changed inputs or changed/missing evidence reset completion to pending. The invalidation is deliberately conservative: an input change invalidates all recorded stages. A recorded human/agent claim is not independently verified native evidence. Keep detailed observations in project-owned files, with private game logs in ignored `private/`.

`test` performs structural verification and produces `private/verification.json` with explicit native/device/distribution gaps. It includes the status of any current, complete native evidence and rejects stale evidence as a pass. `build` verifies the pinned clean toolkit and current generated sources, compiles using owned references and records input/source/DLL/reference hashes plus local release metadata in `.builder/build.json`. It does not launch the game. Build failures retain `private/build.log`.

For opt-in gameplay checks, use [prepare-lab and test-native](NATIVE-TESTING.md). They use independently copied game files, a new uniquely named Godot profile and a replaced save backend. Native test code is compiled separately and stays out of ordinary packages. Each lab can run only once, including after a timeout. Evidence binds the exact request, game/dependency/test DLL hashes and project inputs; changed inputs require a fresh lab.

`balance` emits separate review warnings for repeatable draw/Energy loops, free scaling, high combined payoff and weak/no payoff, with reward rarity/type distributions and merchant coverage. It never tunes designs or certifies balance. After a passing native lab, `balance --comparator CHARACTER.IRONCLAD` reports exact rarity/type cell deficits/excess against that build's observed native pool. No historical class count is hardcoded.

`stage` requires a current matching build receipt. It creates a deterministic ZIP with only the configured mod DLL/manifest, declared assets/provenance, license and package report. BaseLib is an explicit external dependency. Native gameplay remains unverified until separately observed. See [publishing](PUBLISHING.md).

## Toolkit development checks

```powershell
python -m unittest discover -s builder/tests -v
```

The fixture suite uses temporary Git repositories and actual local submodules, not copied-template substitutes. It tests independently named projects, recursive clones, changed inputs/evidence, invalid designs, ownership preservation, IDs and closed packages. To additionally compile a temporary fixture, set `BUILDER_TEST_GAME_DATA` to the owned data directory. Optional native compilation is a separate test; no paid-game files are needed in CI.
