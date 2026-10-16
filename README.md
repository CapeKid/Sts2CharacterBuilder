# Sts2CharacterBuilder

A separate development repository for an AI-guided Slay the Spire 2 character-builder toolkit.

**Status:** pre-implementation design review. The toolkit is not implemented yet. Existing runtime, assets and tools are the imported Spire Legacy reference implementation, not a finished generic builder.

- [Design and extraction plan](docs/character-builder-design.md)
- [Implementation issue](https://github.com/CapeKid/Sts2CharacterBuilder/issues/1)
- [Spire Legacy reference documentation](SPIRE_LEGACY_REFERENCE.md)
- [Original mod repository](https://github.com/CapeKid/SpireLegacy)

The scope is conventional standalone characters, guided and expedited authoring, modular skills and verification tools. Cross-run progression, heirs, inheritance, manor upgrades and crowns are permanently excluded.

This repository preserves the complete history of the character-builder branch through `60322dafc054f97d2c5c534dce3552f90fad4757`. It is an independent development fork because GitHub does not allow one account to own both a parent repository and its fork. Builder work belongs here; the Spire Legacy repository remains focused on the mod.

Inherited build and publishing scripts are reference material and still contain Spire Legacy-specific identifiers. Do not use them to publish this toolkit or another character to the existing mod's Workshop item. The extraction plan explains the required project configuration and identity separation.

Original code and content retain their existing [MIT license](LICENSE) and dependency notices.
