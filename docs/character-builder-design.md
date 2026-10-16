# Character builder: design review for #163

This review was originally requested in Spire Legacy #163 and preserved from branch commit `60322dafc054f97d2c5c534dce3552f90fad4757`. The work and issue now live separately in [Sts2CharacterBuilder #1](https://github.com/CapeKid/Sts2CharacterBuilder/issues/1). The repository contains the imported reference implementation and this design review; the generic toolkit has not been implemented yet.

The remaining #146/#176/#177 balance work requires experienced human decisions and progression observations. Repeating the existing automated campaigns cannot supply those observations. #163 is the independently actionable engineering project among the remaining issues.

## Recommendation and scope choice

The idea is workable. The main change is to build a configurable authoring toolkit around a conventional character template, rather than treating the full Spire Legacy mod as a generic template. Its inheritance, three classes, manor, crowns and balance overrides are coupled product features. Reusing them by default would give unrelated characters unwanted mechanics and save formats.

Proposed first release: one conventional character per project, guided and expedited creation, owned local game references, regular/public-beta targets, original placeholder visuals, optional custom content, isolated verification, and private Workshop staging. The owner explicitly excluded progression entirely: heirs, inheritance, manor upgrades and crowns are outside the toolkit, including future extensions. They were specific to this character. Ordinary character mechanics and combat resources remain in scope; cross-run progression does not.

No new artwork, human balance study, paid generation service, or online co-op campaign is necessary to review this proposal. Later implementation must distinguish unavailable tooling and unperformed device tests from completed work.

## What the workflow should ask

Ask in short groups as the relevant step arrives. Reuse information from the user's initial idea; do not make them repeat it. Offer “choose for me” for creative decisions. Expedited mode records sensible defaults and proceeds with the idea alone, while keeping external publishing and purchases explicit actions.

| Step | Useful questions and recorded decisions |
| --- | --- |
| Identity | Character idea, name, creator credit, mod ID/namespace, repository name, license, intended tone and visual direction. IDs become stable before saves or public releases exist. |
| Runtime scope | Regular, beta or both; solo or co-op; PC/Deck targets; installed game path; acceptable dependencies; available local .NET, Python and Godot tooling. Check capabilities rather than assuming this machine's paths. |
| Mechanics | Starting HP/energy/deck/relic, central resource or rule, intended strengths/weaknesses, build themes, desired difficulty and Ascension benchmark. Default to native conventions when omitted. |
| Cards and powers | User ideas, whether to fill remaining reward cards, upgrades, rarity/type distribution, archetype coverage, targeting, generated cards/tokens, statuses and temporary effects. Distinguish reward pool, basics and special cards. |
| Art | Supplied images and rights, whether to generate missing art, budget/provider constraints, shared style, portrait/background/frame/icon requirements, readable distinct card art. Keep original fallbacks if generation is unavailable. |
| Items | Starting and drop relics, potions, pool/shop eligibility and optional user ideas. Potions are missing from the original issue's questionnaire and should be included. |
| Narrative | Optional character events, Ancient encounters/cards/dialogue, victory and return conversations, defeat/ending text, language/localization scope. Events and dialogue are separate capabilities. |
| Character presentation | Combat idle/attack/skill/hurt/death/victory, rest/shop presentation, portrait/map icon, energy display, trails/VFX and sounds. Include crop, animation anchors and scale checks. |
| Controls and accessibility | Controller navigation, keyboard/mouse, 1280x800 readability, tooltips, visible close/back affordances, color-independent identifiers, motion/audio preferences where relevant. |
| Delivery | Desired channels, description/preview/credits, existing versus new Workshop item, initial private testing and eventual visibility. A newly generated project must not inherit Spire Legacy's item ID or public setting. |

“Skip” needs a defined outcome. Skipping custom events means no extra event registration. Skipping custom cards selects a valid configured native pool/deck fallback, with no claim of a complete original card pool. Declining AI completion while supplying only five cards leaves a clearly labeled small-pool prototype. A full-pool request fills gaps only when authorized and validates the chosen branch's actual comparator counts. Missing essential art gets original labeled placeholders rather than invisible UI or copied assets. Incomplete optional features must not be half-registered.

## Proposed repository and ownership model

The generated character repository owns its project configuration, source customizations, designs, localization, assets and release identity. A pinned `tools/character-builder` Git submodule owns reusable skills, schemas, templates and verification tools. Build output and per-project workflow state stay outside the submodule. Never edit the submodule as an accidental way to customize a character.

Proposed generated layout:

```text
AGENTS.md                         Agent-neutral entry and resume instructions
character.json                    Identity, enabled features and creative choices
builder.lock.json                 Toolkit commit and tested dependency/branch pins
design/                           Cards, powers, items and dialogue
src/                              Project-owned implementation and explicit extensions
assets/                           Project-owned originals and exports
localization/                     Stable localization keys and translations
tools/character-builder/          Pinned, read-only-by-convention Git submodule
.builder/state.json               Resumable step/input/output records (ignored)
private/                          Owned references, profiles and raw evidence (ignored)
build/ and dist/                  Reproducible staged outputs (ignored)
```

Do not assume that every AI automatically discovers skills inside a Git submodule. The top-level README/AGENTS entry must explicitly direct it to the toolkit's entry skill. Agents without skill discovery can follow the same Markdown instructions and invoke the same CLI. Do not auto-install global skills, assume Codex-specific tools, or require an unavailable image generator.

Pin a toolkit commit. Upgrades are explicit: show schema/template changes, migrate a copy, preserve saved model IDs, validate and review the submodule bump. Never silently track the toolkit's latest branch or overwrite hand-edited source. Separate generated files from extensions and reject unrecognized changes before regeneration. Existing user directories must not be reset to “start fresh.”

A small Python CLI should take an explicit project root and configuration path. Proposed operations are `doctor`, `init`, `validate`, `generate`, `build`, `stage`, `test` and `resume`; these are proposed interfaces, not commands that exist today. Native C# APIs and branch adapters remain separate from authoring/asset tools. Local paths, Steam identity and test capabilities belong in ignored environment configuration. Runtime packages contain neither the toolkit nor its development bridge unless explicitly required and declared.

## Reuse inventory

These are inspected source boundaries, not promises that a file can be copied unchanged. The baseline is main commit `f051456`.

| Existing source | Reusable part | Required separation |
| --- | --- | --- |
| [Typed schema reader](../scripts/design_schema.py), [schema](../scripts/design-schema.json), [preflight](../scripts/preflight.py) | Strict JSON, IDs, references, bounds, asset dimensions and hashes | Split generic character/content schemas from family/trait/manor tables and fixed class counts. |
| [Native generation](../scripts/sts2-generate.py), [saved IDs](../scripts/saved-model-ids.json) | Stable model generation and save-identity preservation | Parameterize namespace, output ownership, enabled model kinds and migration baseline. |
| [Design access](../sts2/Core/Design.cs), [card design](../sts2/Core/CardDesign.cs) | Validated design loading and card values | Separate generic card values from inherited stats and the fixed shared/unique class pools. |
| [Character](../sts2/Native/HeirCharacter.cs), [cards](../sts2/Native/LegacyCard.cs), [effects](../sts2/Native/CardEffects.cs) | Integration examples and native lifecycle lessons | Start from a small supported character; extract narrowly scoped helpers rather than copying family hooks. |
| [API contracts](../sts2/Core/ApiContract.cs), [branch commands](../sts2/Native/BranchCommands.cs), [startup](../sts2/Native/NativeStartup.cs) | Signature validation, awaited branch calls, exception propagation, owned patch rollback | Replace fixed IDs and inherited hooks; enable only adapters exercised by the generated features. |
| [Icons](../scripts/author-heir-icons.py), [card exports](../scripts/prepare_card_art.py), [UI exports](../scripts/prepare_ui_art.py) | Deterministic exports, crop/dimension checks and preservation of supplied art | Project paths, art directions and manifests replace Heir-specific shapes and filenames. |
| [Sprites](../sts2/Native/HeirSprite.cs), [presentation](../sts2/Native/HeirPresentation.cs) | Atlas regions, anchors, animation states and room-specific scaling | Use configurable character resources; do not copy the three original sprite atlases or identities by default. |
| [Lab creation](../scripts/sts2-lab.py), [isolation](../sts2/Core/TestIsolation.cs) | Independent owned-game copies, dedicated profiles and physical path containment | Remove fixed Windows paths, account IDs, environment prefixes and profile names; implement supported host adapters. |
| [Oracle protocol](../scripts/oracle_protocol.py), [oracle CLI](../scripts/sts2-oracle.py), [request ledger](../sts2/Core/TestRequestLedger.cs) | Correlated requests, timeout/hash checks, receipts and duplicate handling | Configurable project/test identity; register only supported fixtures under explicit test opt-in. |
| [Pool parity](../sts2/Native/NativePoolParity.cs), [card resolution](../sts2/Native/CardResolutionOracle.cs), [coop oracle](../sts2/Native/CardCoopOracle.cs) | Branch comparator checks, native card resolution, owner/target isolation | Generic feature-specific assertions. Passing a loop through known cards does not establish arbitrary custom-effect correctness. |
| [Core checks](../sts2/tests/SpireLegacy.CoreChecks.csproj), [design mutations](../scripts/check-design-schema.py) | Structural, mutation, regeneration and output-preservation test patterns | Split invariants from game-specific constants, card names and family behavior. |
| [Release contract](../scripts/release_contract.py), [transaction](../scripts/release_transaction.py), [release checks](../scripts/check-release-packages.py) | Closed package inputs, hashes, safe ZIP paths, interruption recovery and save-preserving install layouts | Replace fixed app-project identity, Workshop owner/item, paths, guides, expected dependency and visibility. Keep the StS2 app identity explicit. |
| [Asset inventory](../scripts/release_assets.py) | Declared provenance and exact shipped-byte inventory | Per-project manifests and honest method/license records; declarations are not independent ownership proof. |
| [Balance comparisons](../docs/adversarial-balance.md), [bounded assessment](../docs/balance146-final-assessment.md) | Comparator reasoning, fixed-deck tests and predeclared capped playtests | Do not copy [card overrides](../scripts/balance_policy.py), family prices or a heuristic win rate as generic character balance rules. |

Excluded by default: historical StS1 tools/source, private game assemblies and references, personal saves, publishing credentials, current Workshop item identifiers, generated pilot evidence, and the 360-card content library. Family systems and all cross-run progression are excluded by the owner's decision; do not add extension placeholders for them.

## Skill boundaries

The entry skill routes and resumes; each substantial skill defines inputs, outputs, prerequisites, a skip/fallback result and relevant verification. Detailed branch/API procedures belong in references, not repeated in every prompt. Ask for approval only where the user's existing authorization does not cover an external action; a skipped creative questionnaire is not permission to publish or buy services.

| Proposed skill | Responsibility |
| --- | --- |
| `create-character` | Intake, guided/expedited choices, capability checks, feature dependencies and resumable progress. |
| `setup-character-project` | Create the selected project, pin the submodule and upstream template/dependencies, configure paths, establish saved IDs and build a minimal character. |
| `design-character-mechanics` | Starting deck/relic/stats, resource rules, powers, archetypes, targeting and upgrade behavior. |
| `create-character-cards` | User cards, optional completion, branch pool/type/rarity targets, basics/tokens and text/upgrade checks. |
| `create-character-art` | Supplied/generated/fallback card and UI assets, provenance, hashes, export/crop checks and visual review. |
| `create-character-items` | Starting/drop relics and potions, eligibility, shops and owner-specific effects. |
| `create-character-events` | Optional event registration, conditions, costs/rewards, return/save behavior and co-op choices. |
| `create-character-dialogue` | Ancient first/return/victory text, character ending text, optional Ancient cards and localization. |
| `create-character-sprites` | Atlas states, identity consistency, anchors, death/victory, shops/rest sites and animation checks. |
| `create-character-presentation` | Energy/map/portrait presentation, UI input, trails, effects and readability. |
| `create-character-audio` | Original/supplied/fallback sounds, routing, levels, file formats and disclosure. |
| `verify-character` | Source and native checks, exact build/version evidence, save/resume, negative cases and coverage gaps. |
| `assess-character-balance` | Native comparators, resource/loop risks, bounded builds/playtests, justified findings and separate tuning changes. |
| `publish-character` | Closed staging, existing-item safeguards, explicit channel/visibility choice, official upload and delivery verification. |
| `upgrade-character-project` | Reviewed toolkit/dependency/branch updates, schema migration, stable saves and regression testing. |

## Verification contract

Every report identifies toolkit/project commit, DLL hash, game branch/build, dependencies, selected features and test inputs. A source-only pass, native pass and physical-device observation are separate evidence types. The toolkit must be usable without paid-game CI; such CI runs schema/generation/package fixtures, while owned local game assemblies enable compile/native tests. Missing native or Deck capability yields a named gap, never a fabricated pass.

1. **Bootstrap portability:** produce two projects with different IDs, names and directories containing spaces; initialize/resume guided and expedited modes; no output writes inside the submodule. Test a local Git submodule, not merely a copied template directory. Verify recursive-clone instructions on a fresh checkout.
2. **Content integrity:** reject duplicate/unstable IDs, dangling references, invalid upgrades, unsafe paths, stale generated files and malformed art. Separate optional disabled features from missing required resources. Regeneration must preserve project-owned changes and saved identities.
3. **Native minimal character:** selection portrait, starter deck/relic, target/energy/effect/card disposal, turn transitions, save/resume, rewards, compendium, rest/shop/death/victory. Exercise at least one new card, power and custom resource through actual gameplay APIs before generating a full pool.
4. **Selected features:** test every enabled effect in base/upgraded forms, including secondary values, multi-hit bonuses, status durations, retention/exhaust, owner/target behavior and boundary values. Reflective branch adapters need checks on each claimed branch. Include UI text/keyword/localization checks.
5. **Balance:** compare costs and combined effects with relevant native cards; flag zero-cost draw/energy loops, repeated recursion, unbounded triggers and weak payoff cards. Sample coherent archetypes. Human playtest quality, fun and campaign win rates remain human evidence requirements; automated losses cannot justify automatic buffs.
6. **Controls/platforms:** desktop input and 1280x800 layout fixtures; physical Deck/controller checks when available; Linux/Proton package layout checks otherwise. Online co-op claims require separately available accounts/devices; do not make two accounts a prerequisite for creating a solo character.
7. **Distribution:** closed packages, declared dependencies and licenses, unique mod identity, no owned game files/secrets/profiles, safe installs/updates/uninstalls and item-ID preservation. Publishing must be followed by authenticated visibility and downloaded-content verification. New projects default to private testing; the user chooses when to go public.

Track workflow outcomes as `pending`, `ready`, `running`, `complete`, `skipped` or `blocked`, with the responsible input/output hashes. A changed input invalidates dependent verification. Resume must report unfinished work and reuse valid outputs rather than silently marking skipped stages complete. Do not call a prototype “release ready” while essential fallbacks or native validation remain unresolved.

## Work order and completion gates

These are sequential milestones of one project, not a request to create a long series of follow-up issues or calibration PRs.

| Milestone | Deliverable and gate |
| --- | --- |
| 1. Portable foundation | Repository, license/notices, entry workflow, project schema/state, pinned submodule bootstrap, doctor and generic validation. Two independently named fixtures initialize and resume without Spire Legacy IDs or machine paths. |
| 2. Native minimal character | Small conventional character template, one card/power/resource, starter relic, original visible defaults, branch adapters and isolated tests. Build and native card lifecycle/save-resume pass on each initially supported branch. |
| 3. Optional authoring | Focused skills plus working generators for chosen cards/art/items/narrative/sprites/audio. Every optional skip has a valid fallback or clear unsupported state. Guided and idea-only workflows both reach a playable package. |
| 4. Verification and balance | Generic structural/mutation/native fixtures, effect extension contract, comparator reports and capped playtest protocol. Report unsupported bespoke effects/devices plainly. |
| 5. Publishing and clean-room trial | Official uploader integration, private first upload, existing-item update, staged-to-downloaded hash verification, notices and setup instructions. A fresh recursive clone can create and test a second distinct character without hidden local tools; only then claim the builder is usable. |

Spire Legacy remains the reference implementation during extraction. It should not immediately depend on a half-extracted toolkit. Keep builder implementation and its follow-up changes in this repository, separate from Spire Legacy development. No change to its live 1.0.32 Workshop content is part of #163's design review.

## Upstream starting points and remaining choices

Use the existing [BaseLib character/template ecosystem](https://github.com/Alchyr/ModTemplate-StS2/blob/master/README.md) and [BaseLib documentation](https://alchyr.github.io/BaseLib-Wiki/) as upstream starting points; the toolkit adds the guided workflow, project configuration and verification learned here. Inspect and pin actual upstream revisions and licenses before vendoring or generating from their files. Spire Legacy's currently tested BaseLib/game pins are a known baseline, not proof that every newer branch or machine is compatible.

Use [Mega Crit's official uploader](https://github.com/megacrit/sts2-mod-uploader/blob/main/README.md) rather than creating another uploading implementation. Its workspace contains the content, configuration and preview, and it preserves the existing item through the local ID marker. Our additional checks should enforce project ownership/visibility and verify delivery.

Confirmed scope: conventional standalone characters; no progression systems. Other default proposals: both guided and expedited modes; agent-neutral instructions; regular/beta targets only after separate native verification; solo baseline with co-op checks enabled for co-op claims; original readable fallbacks; no paid generation without a declared budget; MIT for newly written toolkit code with preserved upstream notices. Existing user authorization determines external operations at implementation time. The initial scope question is resolved: do not extract or recreate progression functionality. No further answer is required for this design review; the defaults above keep implementation moving without repeating the questionnaire.
