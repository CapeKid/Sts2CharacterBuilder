---
name: setup-character-project
description: Create a new character repository with a pinned Sts2CharacterBuilder submodule and independent identity.
---

Use the CLI init command in [the workflow](../../WORKFLOW.md). Choose a new project destination, mod ID, C# namespace, name, creator and license. Reuse the user's supplied identity; infer reversible defaults in expedited mode.
Check Python 3.11+, Git and .NET 9+ availability with doctor. Ask for the owned game's data directory when compilation is required and no path is known. Never copy game assemblies into Git or releases.
Create a local Git repository with the builder as tools/character-builder, pinned to a full committed SHA. Do not install global skills. Use the generated AGENTS.md as the neutral entry point. Create a remote repository only under the user's existing authorization and available account tools.
Run generate, validate and build with the pinned CLI. The template uses BaseLib 3.4.7 and native placeholder presentation; its conventional resource is run-local Focus, not progression. Record a compile receipt separately from native gameplay.
Output character.json, builder.lock.json, a real submodule gitlink, source/design/assets and setup evidence. Unsupported game versions remain gaps until separately verified.
