---
name: upgrade-character-project
description: Upgrade a pinned builder or game dependency while preserving character source and saved IDs.
---

Work in the character repository. Record current pins and a clean source snapshot. Review new toolkit schema/template/API changes before changing tools/character-builder and builder.lock.json together.
Migrate a copy, preserve namespace/mod/model IDs and project-owned src/Extensions, and review generated diffs. The generator rejects removed identities and hand-edited generated files; do not delete its guards to force a migration.
Run bootstrap/regeneration, native lifecycle and save/resume regressions on every claimed branch. Invalidate evidence after any changed inputs, dependencies or source.
Output the reviewed submodule/lock bump, migration notes and verification. If the update fails, retain the prior pin and original files. Never silently track the latest branch.
