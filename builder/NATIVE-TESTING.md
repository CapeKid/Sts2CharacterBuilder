# Isolated native verification

The ordinary `test` command verifies authoring structure. Native checks additionally require a local owned game, the pinned BaseLib package, .NET, a known Workshop content directory and Steam account-directory discovery. The toolkit distributes none of those game files.

`character.json` selects the branch. Preparation checks the owned `release_info.json` against [compatibility.json](compatibility.json): the imported baseline is regular 0.107.1/public-beta 0.111.0. Selecting regular while pointing at beta is refused. A new build requires an explicit reviewed compatibility-pin update and fresh evidence; a successful compile alone does not enable a native branch claim.

Run the project's pinned CLI, using your actual paths:

```powershell
python tools/character-builder/scripts/character-builder.py --project . prepare-lab --game-root "C:/your/Steam/steamapps/common/Slay the Spire 2" --baselib-root "C:/your/.nuget/packages/alchyr.sts2.baselib/3.4.7" --workshop-root "C:/your/Steam/steamapps/workshop/content/2868840" --steam-userdata "C:/your/Steam/userdata" --lab-id first-check
python tools/character-builder/scripts/character-builder.py --project . test-native --lab-id first-check --timeout 240
python tools/character-builder/scripts/character-builder.py --project . test
python tools/character-builder/scripts/character-builder.py --project . balance --comparator CHARACTER.IRONCLAD
```

Preparation compiles the ordinary release DLL, then a separate test DLL with `BUILDER_NATIVE_TESTS` enabled. It independently copies the owned game to `private/labs/<id>/game/`, excluding installed local mods and overrides. It copies only the chosen character and pinned BaseLib into that lab. Source links/junctions and overlapping/existing destinations are refused. Allow several GB of private disk space per lab.

The lab creates a **new** `Sts2CharacterBuilderLab-<random-token>` profile under Godot's application-data location (Windows AppData or Linux XDG data), with settings for discovered accounts. Workshop manifests are catalogued and disabled in that profile; only the local character and BaseLib are enabled. The original game installation and regular profiles are not edited. The lab and profile are preserved for inspection; there is no recursive cleanup command. The launcher currently recognizes Windows/Linux game executables; native behavior has been exercised locally only on Windows/v0.111.0.

Before launch, hashes of the copied game, mod/dependency bytes, request and initial profile settings must agree. A changed Workshop catalog, extra game file, linked path or changed project input invalidates preparation. The probe checks its exact Godot profile, marker, request token and loaded game/BaseLib/test-DLL hashes before replacing the save backend with an isolated `GodotFileIo`. It then waits for the menu and runs the native suite once. Headless execution uses no interactive app window.

The native suite checks:

- Character/card registration and original icon loading; starter deck/relic identities and starter resource trigger.
- Every generated numeric card, base and upgraded, played through the native paid action path: targeting rejection, Energy, damage, Block, draw, resource gain, Exhaust/Power/discard disposal, completed action/table cleanup and card save round trips. Draw/Energy/Focus descriptions must match the active upgrade values. The recorded local fixture adds two test-only designs to exercise positive Energy gain and all-enemy damage combined with Block.
- Every generated card portrait in both upgrade states: decoded pixels/dimensions match the assigned SVG/PNG or shared fallback, cached textures are reused, and card save/load retains the selected texture. These checks require a fresh lab after a toolkit upgrade; old numeric-only evidence is incomplete. Human crop/style/legibility review remains separate.
- Focus's native Block hook, actual turn transition, persistent combat counter and reset at the next combat.
- Native reward and merchant creation, including owner/pool membership.
- A permanent deck upgrade, full native run save/read/reconstruction/resume, and deck/relic/character identity preservation.
- Actual native reward-card IDs, costs, dynamic values and rarity/type cells for each built-in character. These remain private evidence and can drive `balance --comparator`.

`test-native` emits progress and writes `evidence.json` under the lab. A success marker in `.builder/native-evidence.json` binds that file's hash. `test`, `balance --comparator` and package reports accept only complete current coverage with matching input/source/toolkit/release-DLL identity. Truncated, stale or failing evidence is not a native pass.

Each lab is one-shot. A timeout or interruption leaves its run marker; do not replay the mutation. Inspect `process.log`, `godot.log`, `progress.json`, `result.json` and `evidence.json`, fix the issue, then prepare a new lab ID. Preparation never reuses a dirty lab or resets existing profiles. The default timeout is 240 seconds, bounded to 30–600 seconds.

The test-only probe is absent from a normal build and ZIP. A native pass establishes the numeric fixtures on the **reported** branch/build, not visual correctness, campaign balance, physical Deck/controller support, co-op, arbitrary extension effects or Workshop delivery. Keep those gaps visible. Existing character projects made with the earlier six-card prototype may need additional reward types before a normal merchant can populate; review/add cards through authoring data rather than renaming saved models.
