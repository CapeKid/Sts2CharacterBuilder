# Sts2CharacterBuilder

A separate development repository for an AI-guided Slay the Spire 2 character-builder toolkit.

**Status:** portable prototype implementation. The builder now bootstraps pinned submodule projects, generates a small conventional character, validates designs, resumes evidence-backed work, compiles against owned game references, flags balance risks and stages closed private-test packages. Native gameplay, full optional-content generation and Workshop clean-room delivery gates remain open; this is not yet a finished generic builder.

Start an AI at [the create-character skill](builder/skills/create-character/SKILL.md). It routes guided or idea-only authoring through focused skills, including art, items, events, dialogue, sprites, audio, verification, balance and publishing. See [commands and ownership](builder/WORKFLOW.md), [publishing](builder/PUBLISHING.md) and [implementation status](docs/character-builder-status.md).

```powershell
python scripts/character-builder.py --project ../MyCharacter init --id MyCharacter --idea "Your character concept" --mode expedited
```

The initial six-card design is a prototype, not an automatically completed native-sized card pool. The runtime implements a bounded effect vocabulary and a run-local Focus power. Agents author bespoke features in project-owned extensions. Disabled optional features use explicit native/original-placeholder fallbacks. Generated packages do not include the reference mod, game files or the toolkit.

- [Design and extraction plan](docs/character-builder-design.md)
- [Implementation issue](https://github.com/CapeKid/Sts2CharacterBuilder/issues/1)
- [Spire Legacy reference documentation](SPIRE_LEGACY_REFERENCE.md)
- [Original mod repository](https://github.com/CapeKid/SpireLegacy)

The scope is conventional standalone characters, guided and expedited authoring, modular skills and verification tools. Cross-run progression, heirs, inheritance, manor upgrades and crowns are permanently excluded.

This repository preserves the complete history of the character-builder branch through `60322dafc054f97d2c5c534dce3552f90fad4757`. It is an independent development fork because GitHub does not allow one account to own both a parent repository and its fork. Builder work belongs here; the Spire Legacy repository remains focused on the mod.

Inherited build and publishing scripts are reference material and still contain Spire Legacy-specific identifiers. Do not use them to publish this toolkit or another character to the existing mod's Workshop item. The extraction plan explains the required project configuration and identity separation.

Original code and content retain their existing [MIT license](LICENSE) and dependency notices.
